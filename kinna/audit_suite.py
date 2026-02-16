"""Audit Suite — KL-100 Benchmark for semantic reliability testing.

Implements Section 7 of KL v1.4. Runs labeled test queries and scores:
    - Regime Lock Accuracy
    - Conflict Precision / Recall
    - Determinism (same input → same output)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .assembler import assemble_word
from .context_switch import assemble_word_in_regime
from .di_calculator import (
    DIVerdict,
    classify_di,
    distortion_index,
)
from .regime_locker import Regime, detect_regime


@dataclass
class BenchmarkRow:
    """A single KL-100 benchmark entry."""

    query: str
    shape_label: str
    regime_lock_expected: Regime
    key_words: List[str]
    expected_di_range: Tuple[float, float]  # (min, max)
    pass_condition: str  # "allow", "clarify", or "reject"


@dataclass
class BenchmarkResult:
    """Result of running a single benchmark row."""

    row: BenchmarkRow
    regime_detected: Regime
    regime_correct: bool
    word_results: Dict[str, float]  # word → DI
    conflict_flagged: bool
    passed: bool
    notes: str = ""


@dataclass
class AuditReport:
    """Aggregate report for the full benchmark suite."""

    total: int = 0
    regime_correct: int = 0
    conflict_true_positive: int = 0
    conflict_false_positive: int = 0
    conflict_false_negative: int = 0
    determinism_failures: int = 0
    results: List[BenchmarkResult] = field(default_factory=list)

    @property
    def regime_accuracy(self) -> float:
        return self.regime_correct / self.total if self.total else 0.0

    @property
    def conflict_precision(self) -> float:
        tp = self.conflict_true_positive
        fp = self.conflict_false_positive
        return tp / (tp + fp) if (tp + fp) else 1.0

    @property
    def conflict_recall(self) -> float:
        tp = self.conflict_true_positive
        fn = self.conflict_false_negative
        return tp / (tp + fn) if (tp + fn) else 1.0

    @property
    def pass_rate(self) -> float:
        passed = sum(1 for r in self.results if r.passed)
        return passed / self.total if self.total else 0.0

    def summary(self) -> str:
        return (
            f"KL-100 Audit Report\n"
            f"{'=' * 40}\n"
            f"Total tests:          {self.total}\n"
            f"Regime accuracy:      {self.regime_accuracy:.1%}\n"
            f"Conflict precision:   {self.conflict_precision:.1%}\n"
            f"Conflict recall:      {self.conflict_recall:.1%}\n"
            f"Pass rate:            {self.pass_rate:.1%}\n"
            f"Determinism failures: {self.determinism_failures}\n"
        )


# ---------------------------------------------------------------------------
# Built-in KL-100 benchmark dataset (representative subset)
# ---------------------------------------------------------------------------

# Target vectors for common shape labels
SHAPE_TARGETS: Dict[str, Tuple[float, float, float]] = {
    "STRUCTURAL_STABILITY": (0.80, 0.30, 0.15),
    "STRUCTURAL_FAILURE": (0.30, 0.70, 0.20),
    "FLUID_FLOW_QUERY": (0.30, 0.20, 0.80),
    "THERMAL_TRANSFER": (0.40, 0.55, 0.55),
    "MED_OUTCOME_POSITIVE": (0.65, 0.40, 0.35),
    "MED_OUTCOME_NEGATIVE": (0.35, 0.60, 0.25),
    "AVIATION_CONTROL": (0.60, 0.50, 0.35),
    "AVIATION_FAILURE": (0.40, 0.70, 0.30),
    "UPWARD_MOTION": (0.40, 0.70, 0.50),
    "DOWNWARD_MOTION": (0.55, 0.65, 0.25),
    "IMPACT_STOP": (0.65, 0.70, 0.10),
    "PASSIVE_REST": (0.75, 0.20, 0.20),
}

KL_100_DATASET: List[BenchmarkRow] = [
    # --- Aviation (MCAS case study, Section 5.1) ---
    BenchmarkRow(
        query="The MCAS trim system adjusts the aircraft pitch",
        shape_label="AVIATION_CONTROL",
        regime_lock_expected=Regime.AVIATION,
        key_words=["TRIM", "PITCH"],
        expected_di_range=(0.0, 0.35),
        pass_condition="allow",
    ),
    BenchmarkRow(
        query="The MCAS system caused the aircraft to dive",
        shape_label="AVIATION_FAILURE",
        regime_lock_expected=Regime.AVIATION,
        key_words=["DIVE"],
        expected_di_range=(0.0, 0.50),
        pass_condition="allow",
    ),
    BenchmarkRow(
        query="TRIM describes a DIVE pattern in the MCAS documentation",
        shape_label="AVIATION_FAILURE",
        regime_lock_expected=Regime.AVIATION,
        key_words=["TRIM", "DIVE"],
        expected_di_range=(0.50, 1.0),
        pass_condition="reject",
    ),
    # --- Structural ---
    BenchmarkRow(
        query="The steel beam supports the load on the bridge",
        shape_label="STRUCTURAL_STABILITY",
        regime_lock_expected=Regime.STRUCTURAL_ENGINEERING,
        key_words=["BEAM", "SUPPORT", "BRIDGE"],
        expected_di_range=(0.0, 0.35),
        pass_condition="allow",
    ),
    BenchmarkRow(
        query="The bridge collapsed under the heavy load",
        shape_label="STRUCTURAL_FAILURE",
        regime_lock_expected=Regime.STRUCTURAL_ENGINEERING,
        key_words=["COLLAPSED", "BRIDGE"],
        expected_di_range=(0.0, 0.50),
        pass_condition="allow",
    ),
    BenchmarkRow(
        query="The foundation flowed into the building frame",
        shape_label="STRUCTURAL_STABILITY",
        regime_lock_expected=Regime.STRUCTURAL_ENGINEERING,
        key_words=["FLOWED", "FOUNDATION"],
        expected_di_range=(0.35, 1.0),
        pass_condition="clarify",
    ),
    # --- Fluid Dynamics ---
    BenchmarkRow(
        query="Water flows through the pipe at high pressure",
        shape_label="FLUID_FLOW_QUERY",
        regime_lock_expected=Regime.FLUID_DYNAMICS,
        key_words=["FLOW", "PIPE", "PRESSURE"],
        expected_di_range=(0.0, 0.35),
        pass_condition="allow",
    ),
    BenchmarkRow(
        query="The turbulent current pushed through the valve",
        shape_label="FLUID_FLOW_QUERY",
        regime_lock_expected=Regime.FLUID_DYNAMICS,
        key_words=["CURRENT", "VALVE"],
        expected_di_range=(0.0, 0.50),
        pass_condition="allow",
    ),
    # --- Medicine ---
    BenchmarkRow(
        query="The treatment stabilized the patient condition",
        shape_label="MED_OUTCOME_POSITIVE",
        regime_lock_expected=Regime.MEDICINE,
        key_words=["TREATMENT", "STABILIZED"],
        expected_di_range=(0.0, 0.35),
        pass_condition="allow",
    ),
    BenchmarkRow(
        query="The treatment collapsed the patient recovery",
        shape_label="MED_OUTCOME_POSITIVE",
        regime_lock_expected=Regime.MEDICINE,
        key_words=["TREATMENT", "COLLAPSED"],
        expected_di_range=(0.50, 1.0),
        pass_condition="reject",
    ),
    # --- Polymorphism (DRAFT, Section 6.4) ---
    BenchmarkRow(
        query="Check the draft of air through the ventilation system",
        shape_label="FLUID_FLOW_QUERY",
        regime_lock_expected=Regime.FLUID_DYNAMICS,
        key_words=["DRAFT"],
        expected_di_range=(0.0, 0.50),
        pass_condition="allow",
    ),
    BenchmarkRow(
        query="Review the draft of the document before publishing",
        shape_label="STRUCTURAL_STABILITY",
        regime_lock_expected=Regime.COMPOSITION,
        key_words=["DRAFT"],
        expected_di_range=(0.0, 0.50),
        pass_condition="allow",
    ),
    # --- Geometric congruence validation (Section 3) ---
    BenchmarkRow(
        query="Verify TRUST assembly: anchored suspension bridge",
        shape_label="STRUCTURAL_STABILITY",
        regime_lock_expected=Regime.STRUCTURAL_ENGINEERING,
        key_words=["TRUST"],
        expected_di_range=(0.0, 0.35),
        pass_condition="allow",
    ),
    BenchmarkRow(
        query="Verify GUARD assembly: fortified enclosure",
        shape_label="STRUCTURAL_STABILITY",
        regime_lock_expected=Regime.STRUCTURAL_ENGINEERING,
        key_words=["GUARD"],
        expected_di_range=(0.0, 0.35),
        pass_condition="allow",
    ),
    # --- Cross-regime conflict ---
    BenchmarkRow(
        query="The beam melted in the fire at the hospital",
        shape_label="STRUCTURAL_FAILURE",
        regime_lock_expected=Regime.STRUCTURAL_ENGINEERING,
        key_words=["BEAM", "MELTED"],
        expected_di_range=(0.35, 1.0),
        pass_condition="clarify",
    ),
    # --- Additional stability tests ---
    BenchmarkRow(
        query="The rocket ascends with maximum thrust",
        shape_label="UPWARD_MOTION",
        regime_lock_expected=Regime.AVIATION,
        key_words=["ROCKET", "ASCENDS"],
        expected_di_range=(0.0, 0.50),
        pass_condition="allow",
    ),
    BenchmarkRow(
        query="The stone rests at the base of the wall",
        shape_label="PASSIVE_REST",
        regime_lock_expected=Regime.STRUCTURAL_ENGINEERING,
        key_words=["STONE", "RESTS"],
        expected_di_range=(0.0, 0.50),
        pass_condition="allow",
    ),
    BenchmarkRow(
        query="The wave crashed against the glass tower",
        shape_label="IMPACT_STOP",
        regime_lock_expected=Regime.STRUCTURAL_ENGINEERING,
        key_words=["WAVE", "CRASHED", "TOWER"],
        expected_di_range=(0.0, 0.50),
        pass_condition="allow",
    ),
    BenchmarkRow(
        query="The heat flowed through the steel conductor",
        shape_label="THERMAL_TRANSFER",
        regime_lock_expected=Regime.THERMAL,
        key_words=["HEAT", "FLOWED"],
        expected_di_range=(0.0, 0.50),
        pass_condition="allow",
    ),
    BenchmarkRow(
        query="The electric current surged through the wire",
        shape_label="FLUID_FLOW_QUERY",
        regime_lock_expected=Regime.ELECTRICAL,
        key_words=["CURRENT", "SURGED"],
        expected_di_range=(0.0, 0.50),
        pass_condition="allow",
    ),
]


def run_benchmark(
    dataset: Optional[List[BenchmarkRow]] = None,
    *,
    verbose: bool = False,
) -> AuditReport:
    """Run the KL-100 benchmark suite.

    Parameters
    ----------
    dataset : list of BenchmarkRows; defaults to KL_100_DATASET.
    verbose : print each test result.

    Returns
    -------
    AuditReport with aggregate scores.
    """
    rows = dataset or KL_100_DATASET
    report = AuditReport(total=len(rows))

    for row in rows:
        # Phase 0: Regime detection
        lock = detect_regime(row.query)
        regime_correct = lock.regime == row.regime_lock_expected

        if regime_correct:
            report.regime_correct += 1

        # Phase 1: Geometric verification of key words
        target = SHAPE_TARGETS.get(row.shape_label, (0.5, 0.5, 0.5))
        word_results: Dict[str, float] = {}
        any_conflict = False

        for kw in row.key_words:
            vec = assemble_word_in_regime(kw, row.regime_lock_expected)
            di = distortion_index(vec, target)
            word_results[kw] = di
            verdict = classify_di(di)
            if verdict == DIVerdict.CONFLICT:
                any_conflict = True

        # Evaluate pass condition
        expects_reject = row.pass_condition == "reject"
        expects_clarify = row.pass_condition == "clarify"

        if expects_reject:
            if any_conflict:
                report.conflict_true_positive += 1
                passed = True
            else:
                report.conflict_false_negative += 1
                passed = False
        elif expects_clarify:
            # Clarify: we accept either suspect or conflict
            avg_di = sum(word_results.values()) / len(word_results) if word_results else 0
            passed = avg_di >= 0.20  # some geometric tension expected
            if any_conflict:
                report.conflict_false_positive += 1
        else:
            # "allow" — should NOT be flagged as conflict
            if any_conflict:
                report.conflict_false_positive += 1
                passed = False
            else:
                passed = True

        # Determinism check: run again and verify same results
        lock2 = detect_regime(row.query)
        word_results2: Dict[str, float] = {}
        for kw in row.key_words:
            vec = assemble_word_in_regime(kw, row.regime_lock_expected)
            di = distortion_index(vec, target)
            word_results2[kw] = di

        if lock2.regime != lock.regime or word_results2 != word_results:
            report.determinism_failures += 1

        result = BenchmarkResult(
            row=row,
            regime_detected=lock.regime,
            regime_correct=regime_correct,
            word_results=word_results,
            conflict_flagged=any_conflict,
            passed=passed,
        )
        report.results.append(result)

        if verbose:
            status = "PASS" if passed else "FAIL"
            regime_mark = "OK" if regime_correct else "MISS"
            print(
                f"  [{status}] [{regime_mark}] {row.query[:60]:<60} "
                f"DIs={word_results}"
            )

    return report


def run_and_print(dataset: Optional[List[BenchmarkRow]] = None) -> AuditReport:
    """Run the benchmark and print a summary."""
    print("Running KL-100 Benchmark Suite...")
    print("-" * 80)
    report = run_benchmark(dataset, verbose=True)
    print("-" * 80)
    print(report.summary())
    return report
