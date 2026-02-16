"""Unit and integration tests for the Negation Filter added to
`regime_locker.py` and its effect on the Safety Interlock.
"""

from kinna.context_switch import assemble_word_in_regime
from kinna.di_calculator import DIVerdict
from kinna.regime_locker import (
    is_negation_pair,
    strip_negation_prefix,
    is_safety_critical,
    NEGATION_PREFIXES,
)
from kinna.regime_locker import Regime
from kinna.safety_interlock import check_sentence


def test_strip_negation_prefix_basic():
    assert strip_negation_prefix("UNSTABLE") == "stable"
    assert strip_negation_prefix("NONFLAMMABLE") == "flammable"
    assert strip_negation_prefix("STABLE") is None


def test_is_negation_pair_exact_and_anchor():
    # direct stem matches
    assert is_negation_pair("UNSTABLE", "STABLE")
    assert is_negation_pair("NONFLAMMABLE", "FLAMMABLE")

    # anchor-based morphological match (stable vs stability)
    assert is_negation_pair("UNSTABLE", "STABILITY")

    # negative case
    assert not is_negation_pair("UNRELATED", "RELATEDNESS")


def test_safety_regime_detection():
    assert is_safety_critical(Regime.AVIATION)
    assert is_safety_critical(Regime.STRUCTURAL_ENGINEERING)


def test_negation_forces_conflict_in_safety_regime():
    target = assemble_word_in_regime("STABLE", Regime.STRUCTURAL_ENGINEERING)
    results = check_sentence(
        ["Stability", "UNSTABLE"],
        Regime.STRUCTURAL_ENGINEERING,
        target,
    )

    assert len(results) == 2
    assert all(r.verdict == DIVerdict.CONFLICT for r in results)
    assert all(r.di == 1.0 for r in results)
