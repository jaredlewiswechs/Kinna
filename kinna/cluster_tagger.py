"""Cluster Tagger — assigns phonosemantic regime tags to word vectors.

Implements Section 4 of the KL v1.4 specification. Tags words based on
their vector shape and letter-cluster patterns.

Regime clusters:
    ST_ANCHOR       : terminal -ST  → stopping / standing / impact
    FL_VECTOR       : initial FL-   → low-friction surface interaction
    GL_VECTOR       : initial GL-   → viscous / gated flow
    HIGH_STRUCTURE  : vec_structure > 0.70
    HIGH_FORCE      : vec_force     > 0.60
    HIGH_FLOW       : vec_flow      > 0.70
    FLUID_REGIME    : vec_flow > 0.65 and vec_structure < 0.45
    STRUCTURAL_REGIME: vec_structure > 0.65 and vec_flow < 0.30
"""

from __future__ import annotations

from typing import List

from .assembler import WordVector


def tag_regimes(wv: WordVector) -> List[str]:
    """Return a list of regime tags applicable to the given WordVector."""
    tags: List[str] = []
    word = wv.word.upper()

    # --- Phonosemantic cluster patterns (Section 4) ---

    if word.endswith("ST"):
        tags.append("ST_ANCHOR")

    if word.startswith("FL"):
        tags.append("FL_VECTOR")

    if word.startswith("GL"):
        tags.append("GL_VECTOR")

    if word.startswith("CR"):
        tags.append("CR_FRACTURE")

    if word.startswith("SP"):
        tags.append("SP_SCATTER")

    if word.startswith("SW"):
        tags.append("SW_SWEEP")

    if word.startswith("TR"):
        tags.append("TR_TRAVERSE")

    if word.startswith("GR"):
        tags.append("GR_GRIP")

    # --- Vector-shape regime tags ---

    if wv.structure > 0.70:
        tags.append("HIGH_STRUCTURE")

    if wv.force > 0.60:
        tags.append("HIGH_FORCE")

    if wv.flow > 0.70:
        tags.append("HIGH_FLOW")

    # Composite regime tags
    if wv.flow > 0.65 and wv.structure < 0.45:
        tags.append("FLUID_REGIME")

    if wv.structure > 0.65 and wv.flow < 0.30:
        tags.append("STRUCTURAL_REGIME")

    if wv.force > 0.55 and wv.structure > 0.55:
        tags.append("FORCE_REGIME")

    if wv.flow > 0.50 and wv.force < 0.30:
        tags.append("PASSIVE_FLOW")

    return tags
