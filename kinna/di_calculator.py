"""Distortion Index Calculator — quantifies geometric mismatch.

Implements Section 5.2 of the KL v1.4 specification:

    DI = 1 - cosine_similarity(W, E)

Where:
    W = Word vector (from assembler)
    E = Expected/target vector

DI ranges:
    DI < 0.35         → Congruent   (Allow)
    0.35 <= DI < 0.70 → Suspect     (Clarify)
    DI >= 0.70        → Conflict    (Reject)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Union

from .assembler import WordVector, assemble_word


class DIVerdict(Enum):
    """Classification of a Distortion Index value."""

    CONGRUENT = "congruent"
    SUSPECT = "suspect"
    CONFLICT = "conflict"


# Threshold boundaries (Section 5.2, Table)
DI_CONGRUENT_MAX = 0.35
DI_SUSPECT_MAX = 0.70


@dataclass(frozen=True, slots=True)
class DIResult:
    """Result of a distortion index comparison."""

    word: str
    di: float
    verdict: DIVerdict
    word_vector: Tuple[float, float, float]
    target_vector: Tuple[float, float, float]

    def __repr__(self) -> str:
        return (
            f"DIResult({self.word!r}, DI={self.di:.4f}, "
            f"verdict={self.verdict.value})"
        )


def _cosine_similarity(
    a: Tuple[float, float, float],
    b: Tuple[float, float, float],
) -> float:
    """Compute cosine similarity between two 3D vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return dot / (mag_a * mag_b)


def classify_di(di: float) -> DIVerdict:
    """Return the verdict category for a given DI value."""
    if di < DI_CONGRUENT_MAX:
        return DIVerdict.CONGRUENT
    elif di < DI_SUSPECT_MAX:
        return DIVerdict.SUSPECT
    else:
        return DIVerdict.CONFLICT


def distortion_index(
    word_vec: Tuple[float, float, float],
    target_vec: Tuple[float, float, float],
) -> float:
    """Compute the Distortion Index between two 3D vectors.

    Returns a float in [0.0, 2.0] (though typically [0.0, 1.0]).
    """
    return 1.0 - _cosine_similarity(word_vec, target_vec)


def compare_word_to_target(
    word: str,
    target: Tuple[float, float, float],
) -> DIResult:
    """Assemble *word* and compute DI against a *target* vector."""
    wv = assemble_word(word)
    vec = wv.as_tuple()
    di = distortion_index(vec, target)
    return DIResult(
        word=word.upper(),
        di=di,
        verdict=classify_di(di),
        word_vector=vec,
        target_vector=target,
    )


def compare_words(word_a: str, word_b: str) -> DIResult:
    """Compare two words by their assembled vectors.

    Returns a DIResult where ``word`` is ``"word_a vs word_b"``.
    """
    va = assemble_word(word_a)
    vb = assemble_word(word_b)
    di = distortion_index(va.as_tuple(), vb.as_tuple())
    return DIResult(
        word=f"{word_a.upper()} vs {word_b.upper()}",
        di=di,
        verdict=classify_di(di),
        word_vector=va.as_tuple(),
        target_vector=vb.as_tuple(),
    )
