"""Word Assembly — computes the composite mechanical vector for any word.

Implements the Word Assembly Mechanics from KL v1.4, Section 2.2:

    Word_Stability = f(Initial_Load, Medial_Bracing, Terminal_State)

The assembler sums glyph vectors with positional weighting:
  - Initial letters  (first 1/3)  → weight 1.2  (primary load path)
  - Medial letters   (middle 1/3) → weight 1.0  (bracing / flow)
  - Terminal letters  (last 1/3)  → weight 0.9  (output state)

The resulting 3D vector (Structure, Force, Flow) is called the *Word Vector*.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Sequence

from .glyph_db import GLYPH_TABLE, Glyph, get_glyph


# Positional weights ---------------------------------------------------

INITIAL_WEIGHT = 1.2
MEDIAL_WEIGHT = 1.0
TERMINAL_WEIGHT = 0.9


@dataclass(frozen=True, slots=True)
class WordVector:
    """The assembled mechanical vector for a word."""

    word: str
    structure: float
    force: float
    flow: float
    glyphs: tuple[Glyph, ...]
    density: float  # magnitude of the vector

    def as_tuple(self) -> tuple[float, float, float]:
        return (self.structure, self.force, self.flow)

    def magnitude(self) -> float:
        return self.density

    def __repr__(self) -> str:
        return (
            f"WordVector({self.word!r}, "
            f"S={self.structure:.3f}, F={self.force:.3f}, Fl={self.flow:.3f}, "
            f"dens={self.density:.3f})"
        )


def _positional_weight(index: int, length: int) -> float:
    """Return the positional weight for a glyph at *index* in a word of *length*."""
    if length <= 1:
        return INITIAL_WEIGHT
    third = length / 3.0
    if index < third:
        return INITIAL_WEIGHT
    elif index < 2 * third:
        return MEDIAL_WEIGHT
    else:
        return TERMINAL_WEIGHT


def assemble_word(word: str) -> WordVector:
    """Decompose *word* into glyphs and return its composite WordVector.

    Non-alphabetic characters are silently skipped.
    """
    letters = [ch.upper() for ch in word if ch.isalpha()]
    if not letters:
        return WordVector(
            word=word,
            structure=0.0,
            force=0.0,
            flow=0.0,
            glyphs=(),
            density=0.0,
        )

    glyphs: List[Glyph] = [get_glyph(ch) for ch in letters]
    n = len(glyphs)

    s_sum = 0.0
    f_sum = 0.0
    fl_sum = 0.0
    weight_sum = 0.0

    for i, g in enumerate(glyphs):
        w = _positional_weight(i, n)
        s_sum += g.structure * w
        f_sum += g.force * w
        fl_sum += g.flow * w
        weight_sum += w

    # Normalize by total weight so vectors stay in a comparable range.
    structure = s_sum / weight_sum
    force = f_sum / weight_sum
    flow = fl_sum / weight_sum

    density = math.sqrt(structure ** 2 + force ** 2 + flow ** 2)

    return WordVector(
        word=word.upper(),
        structure=structure,
        force=force,
        flow=flow,
        glyphs=tuple(glyphs),
        density=density,
    )


def assemble_many(words: Sequence[str]) -> list[WordVector]:
    """Assemble multiple words and return a list of WordVectors."""
    return [assemble_word(w) for w in words]
