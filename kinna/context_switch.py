"""Context Switch — regime-specific glyph remapping.

Implements Section 6.3 and 6.4 of KL v1.4: modifies glyph weights
based on the locked regime to handle polymorphic words.

When a regime is locked, certain glyphs are remapped to reflect the
physics of that domain (e.g., in FLUID regime, D = Density rather
than Dead Load).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .glyph_db import Glyph, GLYPH_TABLE
from .regime_locker import Regime


# Type alias for a 3-tuple override: (structure, force, flow)
VecOverride = Tuple[float, float, float]


# Regime-specific glyph remaps (Section 6.3)
# Each entry: letter → (new_structure, new_force, new_flow)
REGIME_REMAPS: Dict[Regime, Dict[str, VecOverride]] = {
    Regime.FLUID_DYNAMICS: {
        "D": (0.30, 0.40, 0.70),   # Density (fluid mass per volume)
        "L": (0.20, 0.10, 0.90),   # Laminar flow
        "S": (0.15, 0.25, 0.90),   # Turbulence / swirl
        "P": (0.40, 0.80, 0.40),   # Pressure (hydraulic)
        "V": (0.30, 0.50, 0.70),   # Velocity
    },
    Regime.STRUCTURAL_ENGINEERING: {
        "D": (0.80, 0.70, 0.05),   # Dead load
        "L": (0.60, 0.40, 0.20),   # Beam / lintel
        "S": (0.30, 0.75, 0.15),   # Shear force
        "F": (0.60, 0.80, 0.10),   # Fixed support
        "M": (0.80, 0.50, 0.15),   # Moment
    },
    Regime.THERMAL: {
        "H": (0.40, 0.60, 0.55),   # Heat transfer
        "C": (0.50, 0.20, 0.50),   # Conduction
        "R": (0.30, 0.50, 0.60),   # Radiation
        "F": (0.30, 0.80, 0.50),   # Flame / combustion
    },
    Regime.ELECTRICAL: {
        "C": (0.60, 0.30, 0.50),   # Capacitance
        "R": (0.50, 0.70, 0.20),   # Resistance (ohmic)
        "V": (0.40, 0.80, 0.40),   # Voltage
        "I": (0.30, 0.40, 0.70),   # Current (amperes)
        "W": (0.45, 0.60, 0.50),   # Watt / power
    },
    Regime.MEDICINE: {
        "D": (0.60, 0.50, 0.30),   # Dose / dosage
        "T": (0.55, 0.40, 0.35),   # Treatment
        "S": (0.30, 0.20, 0.60),   # Symptom flow
        "P": (0.50, 0.60, 0.35),   # Prognosis / patient state
    },
    Regime.AVIATION: {
        "T": (0.60, 0.50, 0.30),   # Trim (controlled adjustment)
        "D": (0.50, 0.70, 0.40),   # Drag
        "L": (0.40, 0.60, 0.50),   # Lift
        "S": (0.20, 0.30, 0.70),   # Stall (loss of flow)
    },
    Regime.COMPOSITION: {
        "D": (0.50, 0.30, 0.45),   # Draft state (provisional)
        "R": (0.55, 0.40, 0.45),   # Revision
        "E": (0.50, 0.30, 0.50),   # Editing layers
    },
}


@dataclass(frozen=True, slots=True)
class ContextualGlyph:
    """A glyph with regime-adjusted vectors."""

    letter: str
    regime: Regime
    structure: float
    force: float
    flow: float
    is_remapped: bool

    def as_tuple(self) -> Tuple[float, float, float]:
        return (self.structure, self.force, self.flow)


def get_contextual_glyph(letter: str, regime: Regime) -> ContextualGlyph:
    """Return a glyph with regime-specific vector adjustments.

    If the letter has a remap for the given regime, the override is used.
    Otherwise the default glyph values are returned.
    """
    letter = letter.upper()
    base = GLYPH_TABLE[letter]

    remaps = REGIME_REMAPS.get(regime, {})
    override = remaps.get(letter)

    if override is not None:
        return ContextualGlyph(
            letter=letter,
            regime=regime,
            structure=override[0],
            force=override[1],
            flow=override[2],
            is_remapped=True,
        )

    return ContextualGlyph(
        letter=letter,
        regime=regime,
        structure=base.structure,
        force=base.force,
        flow=base.flow,
        is_remapped=False,
    )


def assemble_word_in_regime(
    word: str,
    regime: Regime,
) -> Tuple[float, float, float]:
    """Assemble a word using regime-specific glyph mappings.

    Returns the (structure, force, flow) vector.
    """
    import math

    letters = [ch.upper() for ch in word if ch.isalpha()]
    if not letters:
        return (0.0, 0.0, 0.0)

    n = len(letters)
    s_sum = f_sum = fl_sum = w_sum = 0.0

    for i, ch in enumerate(letters):
        cg = get_contextual_glyph(ch, regime)
        # Positional weighting (same as assembler.py)
        third = n / 3.0
        if n <= 1:
            w = 1.2
        elif i < third:
            w = 1.2
        elif i < 2 * third:
            w = 1.0
        else:
            w = 0.9

        s_sum += cg.structure * w
        f_sum += cg.force * w
        fl_sum += cg.flow * w
        w_sum += w

    return (s_sum / w_sum, f_sum / w_sum, fl_sum / w_sum)
