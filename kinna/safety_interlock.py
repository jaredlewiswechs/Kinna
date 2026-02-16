"""Safety Interlock — the final gate before output.

Implements Section 5.2 threshold enforcement:

    DI < 0.35  → Allow
    0.35-0.70  → Request clarification
    DI >= 0.70 → Reject (GeometricConflictError)

Every word in an output is verified against the locked regime's
expected geometry before being emitted.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from .assembler import assemble_word
from .context_switch import assemble_word_in_regime
from .di_calculator import (
    DIResult,
    DIVerdict,
    classify_di,
    distortion_index,
)
from .regime_locker import Regime, RegimeLock


class GeometricConflictError(Exception):
    """Raised when a word's geometry conflicts with the locked regime.

    This is the hard rejection gate (DI >= 0.70).
    """

    def __init__(self, word: str, di: float, regime: Regime, suggestion: str = ""):
        self.word = word
        self.di = di
        self.regime = regime
        self.suggestion = suggestion
        msg = (
            f"GeometricConflictError: '{word}' has DI={di:.4f} "
            f"in regime {regime.value}."
        )
        if suggestion:
            msg += f" Suggested alternative: '{suggestion}'."
        super().__init__(msg)


@dataclass(frozen=True, slots=True)
class InterlockResult:
    """Result of running a word through the safety interlock."""

    word: str
    regime: Regime
    di: float
    verdict: DIVerdict
    passed: bool
    suggestion: Optional[str] = None


def check_word(
    word: str,
    regime: Regime,
    target_vector: Tuple[float, float, float],
) -> InterlockResult:
    """Check a single word against the regime's expected geometry.

    Returns an InterlockResult. Does not raise on failure — use
    ``enforce_word`` for hard rejection.
    """
    regime_vec = assemble_word_in_regime(word, regime)
    di = distortion_index(regime_vec, target_vector)
    verdict = classify_di(di)

    return InterlockResult(
        word=word.upper(),
        regime=regime,
        di=di,
        verdict=verdict,
        passed=verdict != DIVerdict.CONFLICT,
    )


def enforce_word(
    word: str,
    regime: Regime,
    target_vector: Tuple[float, float, float],
    *,
    alternatives: Optional[List[str]] = None,
) -> InterlockResult:
    """Check a word and raise GeometricConflictError if DI >= 0.70.

    If alternatives are provided and the word fails, the best alternative
    is included in the error as a suggestion.
    """
    result = check_word(word, regime, target_vector)

    if result.verdict == DIVerdict.CONFLICT:
        suggestion = ""
        if alternatives:
            # Find the best alternative
            best_di = float("inf")
            for alt in alternatives:
                alt_vec = assemble_word_in_regime(alt, regime)
                alt_di = distortion_index(alt_vec, target_vector)
                if alt_di < best_di:
                    best_di = alt_di
                    suggestion = alt.upper()

        raise GeometricConflictError(
            word=word.upper(),
            di=result.di,
            regime=regime,
            suggestion=suggestion,
        )

    return result


def check_sentence(
    words: List[str],
    regime: Regime,
    target_vector: Tuple[float, float, float],
) -> List[InterlockResult]:
    """Check all content words in a sentence against the regime geometry.

    Skips common function words (articles, prepositions, pronouns).
    Returns a list of InterlockResults.
    """
    FUNCTION_WORDS = {
        "THE", "A", "AN", "TO", "AT", "IN", "ON", "OF", "BY", "FOR",
        "UP", "IT", "IS", "AS", "OR", "IF", "SO", "NO", "DO",
        "I", "WE", "HE", "SHE", "YOU", "THEY", "ME", "US", "HIM", "HER",
        "AND", "BUT", "NOT", "WITH", "FROM", "THAT", "THIS", "THAN",
        "BE", "AM", "ARE", "WAS", "WERE", "BEEN", "BEING",
        "HAS", "HAVE", "HAD", "WILL", "WOULD", "SHALL", "SHOULD",
        "CAN", "COULD", "MAY", "MIGHT", "MUST",
    }

    results = []
    for w in words:
        clean = "".join(ch for ch in w if ch.isalpha()).upper()
        if not clean or clean in FUNCTION_WORDS:
            continue
        results.append(check_word(clean, regime, target_vector))

    return results


def audit_output(
    text: str,
    regime: Regime,
    target_vector: Tuple[float, float, float],
    *,
    strict: bool = True,
) -> Tuple[bool, List[InterlockResult]]:
    """Run the full safety interlock on an output text.

    Parameters
    ----------
    text : the output text to audit.
    regime : the locked physical regime.
    target_vector : the expected geometry for this context.
    strict : if True, any CONFLICT verdict causes overall failure.

    Returns
    -------
    (passed, results) : overall pass/fail and per-word results.
    """
    words = text.split()
    results = check_sentence(words, regime, target_vector)

    if strict:
        passed = all(r.passed for r in results)
    else:
        # Lenient: only fail if majority are conflicts
        conflicts = sum(1 for r in results if not r.passed)
        passed = conflicts < len(results) / 2 if results else True

    return (passed, results)
