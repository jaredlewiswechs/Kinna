"""Tests for Phases 2-5: Engine, Controller, and Safety."""

from kinna.assembler import assemble_word
from kinna.audit_suite import run_benchmark
from kinna.cluster_tagger import tag_regimes
from kinna.context_switch import assemble_word_in_regime, get_contextual_glyph
from kinna.regime_locker import Regime, detect_regime, detect_polymorphic_conflict
from kinna.safety_interlock import (
    GeometricConflictError,
    audit_output,
    check_word,
)
from kinna.sentence_builder import build_sentence, find_best_word, INTENT_TEMPLATES
from kinna.tense_modifier import Tense, apply_tense, detect_tense


# ── Cluster Tagger ───────────────────────────────────────────────────

class TestClusterTagger:
    def test_st_anchor(self):
        wv = assemble_word("TRUST")
        tags = tag_regimes(wv)
        assert "ST_ANCHOR" in tags

    def test_fl_vector(self):
        wv = assemble_word("FLOW")
        tags = tag_regimes(wv)
        assert "FL_VECTOR" in tags

    def test_gl_vector(self):
        wv = assemble_word("GLASS")
        tags = tag_regimes(wv)
        assert "GL_VECTOR" in tags


# ── Regime Locker ────────────────────────────────────────────────────

class TestRegimeLocker:
    def test_fluid_detection(self):
        lock = detect_regime("water flows through the pipe")
        assert lock.regime == Regime.FLUID_DYNAMICS

    def test_structural_detection(self):
        lock = detect_regime("the steel beam supports the bridge load")
        assert lock.regime == Regime.STRUCTURAL_ENGINEERING

    def test_aviation_detection(self):
        lock = detect_regime("the aircraft trim system adjusts pitch")
        assert lock.regime == Regime.AVIATION

    def test_medicine_detection(self):
        lock = detect_regime("the patient received treatment at the hospital")
        assert lock.regime == Regime.MEDICINE

    def test_general_fallback(self):
        lock = detect_regime("hello world")
        assert lock.regime == Regime.GENERAL

    def test_draft_polymorphism(self):
        conflicts = detect_polymorphic_conflict("draft", "")
        assert conflicts is not None
        regimes = {r for r in conflicts}
        assert Regime.FLUID_DYNAMICS in regimes
        assert Regime.COMPOSITION in regimes


# ── Context Switch ───────────────────────────────────────────────────

class TestContextSwitch:
    def test_d_remapped_in_fluid(self):
        cg = get_contextual_glyph("D", Regime.FLUID_DYNAMICS)
        assert cg.is_remapped
        assert cg.flow > 0.5  # D = Density in fluid → higher flow

    def test_d_remapped_in_structural(self):
        cg = get_contextual_glyph("D", Regime.STRUCTURAL_ENGINEERING)
        assert cg.is_remapped
        assert cg.structure > 0.7  # D = Dead Load → high structure

    def test_no_remap_for_general(self):
        cg = get_contextual_glyph("A", Regime.GENERAL)
        assert not cg.is_remapped

    def test_word_in_regime_changes_vector(self):
        v_fluid = assemble_word_in_regime("DRAFT", Regime.FLUID_DYNAMICS)
        v_comp = assemble_word_in_regime("DRAFT", Regime.COMPOSITION)
        assert v_fluid != v_comp


# ── Tense Modifier ───────────────────────────────────────────────────

class TestTenseModifier:
    def test_past_tense(self):
        tv = apply_tense("JUMP", Tense.PAST)
        assert tv.word == "JUMPED"
        assert tv.tense == Tense.PAST

    def test_active_tense(self):
        tv = apply_tense("JUMP", Tense.ACTIVE)
        assert tv.word == "JUMPING"
        assert tv.tense == Tense.ACTIVE

    def test_past_adds_structure(self):
        base = apply_tense("JUMP", Tense.BASE)
        past = apply_tense("JUMP", Tense.PAST)
        assert past.structure >= base.structure  # ED adds weight

    def test_active_adds_flow(self):
        base = apply_tense("JUMP", Tense.BASE)
        active = apply_tense("JUMP", Tense.ACTIVE)
        assert active.flow >= base.flow  # ING adds flow

    def test_detect_tense_ed(self):
        assert detect_tense("JUMPED") == Tense.PAST

    def test_detect_tense_ing(self):
        assert detect_tense("JUMPING") == Tense.ACTIVE

    def test_detect_tense_base(self):
        assert detect_tense("JUMP") == Tense.BASE


# ── Sentence Builder ────────────────────────────────────────────────

class TestSentenceBuilder:
    def test_build_move_up(self):
        plan = build_sentence("MOVE_UP")
        assert plan.render().endswith(".")
        assert len(plan.render().split()) >= 3

    def test_all_intents_buildable(self):
        for intent in INTENT_TEMPLATES:
            plan = build_sentence(intent)
            assert plan.render()

    def test_find_best_word(self):
        results = find_best_word(["RISE", "FALL", "REST"], (0.4, 0.7, 0.5), top_n=1)
        assert len(results) == 1
        assert results[0][1] >= 0.0  # DI is non-negative


# ── Safety Interlock ─────────────────────────────────────────────────

class TestSafetyInterlock:
    def test_check_word_returns_result(self):
        result = check_word("BEAM", Regime.STRUCTURAL_ENGINEERING, (0.8, 0.3, 0.15))
        assert result.word == "BEAM"
        assert result.di >= 0.0

    def test_audit_output(self):
        passed, results = audit_output(
            "The beam supports the bridge",
            Regime.STRUCTURAL_ENGINEERING,
            (0.80, 0.30, 0.15),
        )
        assert isinstance(passed, bool)
        assert len(results) > 0


# ── Audit Suite ──────────────────────────────────────────────────────

class TestAuditSuite:
    def test_benchmark_runs(self):
        report = run_benchmark()
        assert report.total == 20
        assert report.determinism_failures == 0

    def test_regime_accuracy_above_threshold(self):
        report = run_benchmark()
        assert report.regime_accuracy >= 0.50  # at least half correct

    def test_deterministic(self):
        r1 = run_benchmark()
        r2 = run_benchmark()
        for a, b in zip(r1.results, r2.results):
            assert a.word_results == b.word_results
