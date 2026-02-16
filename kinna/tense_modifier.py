"""Tense Modifier — applies morphological suffixes as geometric state changes.

Implements Section 2.3.4 of KL v1.4:

    -ED  : E (Layers) + D (Weight)  → past / static / settled
    -ING : I (Axis) + N (Transfer) + G (Gate) → active / in-progress

Suffixes modify the word vector to reflect temporal/dynamic state.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from .assembler import WordVector, assemble_word
from .glyph_db import get_glyph


class Tense(Enum):
    """Temporal / dynamic state of a word."""

    BASE = "base"
    PAST = "past"          # -ED suffix
    ACTIVE = "active"      # -ING suffix
    FUTURE = "future"      # WILL + base (periphrastic)


@dataclass(frozen=True, slots=True)
class TensedVector:
    """A word vector with tense modification applied."""

    word: str
    tense: Tense
    structure: float
    force: float
    flow: float
    base_word: str

    def as_tuple(self) -> Tuple[float, float, float]:
        return (self.structure, self.force, self.flow)


# Suffix glyph contributions (normalized blending weights)

# -ED: adds layering (E) + weight/mass (D) → increases structure, increases force, decreases flow
ED_BLEND = (0.15, 0.10, -0.10)

# -ING: adds axis (I) + transfer (N) + gating (G) → decreases structure, increases flow
ING_BLEND = (-0.08, 0.05, 0.15)


def _apply_blend(
    base: Tuple[float, float, float],
    blend: Tuple[float, float, float],
) -> Tuple[float, float, float]:
    """Apply a blend offset to a base vector, clamping to [0, 1]."""
    return tuple(  # type: ignore[return-value]
        max(0.0, min(1.0, b + d))
        for b, d in zip(base, blend)
    )


def apply_tense(word: str, tense: Tense) -> TensedVector:
    """Apply a tense modification to a word.

    For PAST (-ED) and ACTIVE (-ING), the suffix glyphs blend into
    the base word vector.  For BASE and FUTURE, no modification is made.
    """
    # Strip existing suffixes to find the root
    upper = word.upper()
    base_word = upper

    if upper.endswith("ING") and len(upper) > 3:
        base_word = upper[:-3]
    elif upper.endswith("ED") and len(upper) > 2:
        base_word = upper[:-2]

    wv = assemble_word(base_word)
    base_vec = wv.as_tuple()

    if tense == Tense.PAST:
        vec = _apply_blend(base_vec, ED_BLEND)
        display = base_word + "ED"
    elif tense == Tense.ACTIVE:
        vec = _apply_blend(base_vec, ING_BLEND)
        display = base_word + "ING"
    else:
        vec = base_vec
        display = base_word

    return TensedVector(
        word=display,
        tense=tense,
        structure=vec[0],
        force=vec[1],
        flow=vec[2],
        base_word=base_word,
    )


def detect_tense(word: str) -> Tense:
    """Heuristically detect the tense of a word from its suffix."""
    upper = word.upper()
    if upper.endswith("ING") and len(upper) > 3:
        return Tense.ACTIVE
    elif upper.endswith("ED") and len(upper) > 2:
        return Tense.PAST
    return Tense.BASE
