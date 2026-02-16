"""Glyph Database — maps each Latin letter to a 3D mechanical vector.

Each glyph is defined by three components derived from the topology
described in the Kinematic Linguistics v1.4 specification (Table 2.1):

    Structure : rigidity, containment, framing  (how much the shape *holds*)
    Force     : energy, pressure, impact         (how much the shape *pushes*)
    Flow      : movement, transfer, flexibility  (how much the shape *moves*)

Values are normalized to [0, 1].
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True, slots=True)
class Glyph:
    """A single glyph's mechanical properties."""

    letter: str
    topology: str
    physical_property: str
    vector_type: str
    structure: float
    force: float
    flow: float

    def as_tuple(self) -> tuple[float, float, float]:
        return (self.structure, self.force, self.flow)


# ---------------------------------------------------------------------------
# Master Glyph Table  (KL v1.4, Table 2.1)
#
# The three-axis scores are derived from the topology descriptions:
#   - A triangular frame is high-structure, moderate force, low flow.
#   - S sinuous curve is low-structure, low force, high flow.
#   - etc.
# ---------------------------------------------------------------------------

GLYPH_TABLE: Dict[str, Glyph] = {
    "A": Glyph(
        letter="A",
        topology="Triangular frame, crossbar",
        physical_property="Stability, load distribution",
        vector_type="Static equilibrium",
        structure=0.90, force=0.30, flow=0.10,
    ),
    "B": Glyph(
        letter="B",
        topology="Vertical spine, dual lobes",
        physical_property="Containment, redundancy",
        vector_type="Volume storage",
        structure=0.80, force=0.20, flow=0.15,
    ),
    "C": Glyph(
        letter="C",
        topology="Open arc",
        physical_property="Reception, incomplete enclosure",
        vector_type="Directional aperture",
        structure=0.40, force=0.15, flow=0.60,
    ),
    "D": Glyph(
        letter="D",
        topology="Vertical spine, single lobe",
        physical_property="Weight, mass concentration",
        vector_type="Gravitational load",
        structure=0.70, force=0.65, flow=0.10,
    ),
    "E": Glyph(
        letter="E",
        topology="Vertical with horizontal tiers",
        physical_property="Layering, stratification",
        vector_type="Hierarchical distribution",
        structure=0.60, force=0.25, flow=0.40,
    ),
    "F": Glyph(
        letter="F",
        topology="Vertical post, cantilever arms",
        physical_property="Reach, leverage",
        vector_type="Moment arm",
        structure=0.55, force=0.70, flow=0.30,
    ),
    "G": Glyph(
        letter="G",
        topology="Arc with inward hook",
        physical_property="Capture, gating",
        vector_type="Flow control",
        structure=0.50, force=0.35, flow=0.55,
    ),
    "H": Glyph(
        letter="H",
        topology="Two pillars, crossbeam",
        physical_property="Bridging, connection",
        vector_type="Tensile span",
        structure=0.85, force=0.30, flow=0.35,
    ),
    "I": Glyph(
        letter="I",
        topology="Vertical line",
        physical_property="Axis, alignment",
        vector_type="Linear direction",
        structure=0.45, force=0.20, flow=0.50,
    ),
    "J": Glyph(
        letter="J",
        topology="Vertical line with bottom hook",
        physical_property="Hook, leverage",
        vector_type="Pendular capture",
        structure=0.40, force=0.45, flow=0.50,
    ),
    "K": Glyph(
        letter="K",
        topology="Vertical with acute diagonals",
        physical_property="Shear, cutting action",
        vector_type="Kinetic impact",
        structure=0.50, force=0.80, flow=0.35,
    ),
    "L": Glyph(
        letter="L",
        topology="Vertical to horizontal bend",
        physical_property="Flow redirection, pooling",
        vector_type="Liquid dynamics",
        structure=0.35, force=0.15, flow=0.80,
    ),
    "M": Glyph(
        letter="M",
        topology="Double peak, stable base",
        physical_property="Oscillation, wave stability",
        vector_type="Harmonic frequency",
        structure=0.75, force=0.40, flow=0.45,
    ),
    "N": Glyph(
        letter="N",
        topology="Two verticals, diagonal bridge",
        physical_property="Transfer, passage",
        vector_type="State transition",
        structure=0.60, force=0.30, flow=0.55,
    ),
    "O": Glyph(
        letter="O",
        topology="Closed loop",
        physical_property="Complete containment",
        vector_type="Volume enclosure",
        structure=0.85, force=0.20, flow=0.20,
    ),
    "P": Glyph(
        letter="P",
        topology="Vertical spine, top bulb",
        physical_property="Pressure, potential",
        vector_type="Stored energy",
        structure=0.55, force=0.75, flow=0.25,
    ),
    "Q": Glyph(
        letter="Q",
        topology="Closed loop with tail",
        physical_property="Containment with release",
        vector_type="Controlled discharge",
        structure=0.80, force=0.30, flow=0.35,
    ),
    "R": Glyph(
        letter="R",
        topology="Vertical, bulb, diagonal leg",
        physical_property="Resistance, bracing",
        vector_type="Force opposition",
        structure=0.65, force=0.60, flow=0.30,
    ),
    "S": Glyph(
        letter="S",
        topology="Sinuous curve",
        physical_property="Slip, flexibility",
        vector_type="Low friction coefficient",
        structure=0.20, force=0.15, flow=0.85,
    ),
    "T": Glyph(
        letter="T",
        topology="Vertical post, horizontal cap",
        physical_property="Hard stop, limit",
        vector_type="Impact boundary",
        structure=0.70, force=0.60, flow=0.05,
    ),
    "U": Glyph(
        letter="U",
        topology="Open vessel",
        physical_property="Reception, holding",
        vector_type="Capacity volume",
        structure=0.50, force=0.10, flow=0.55,
    ),
    "V": Glyph(
        letter="V",
        topology="Converging lines",
        physical_property="Focus, concentration",
        vector_type="Vector convergence",
        structure=0.45, force=0.70, flow=0.40,
    ),
    "W": Glyph(
        letter="W",
        topology="Double valley",
        physical_property="Wave, instability",
        vector_type="Oscillatory motion",
        structure=0.35, force=0.40, flow=0.75,
    ),
    "X": Glyph(
        letter="X",
        topology="Intersecting diagonals",
        physical_property="Cross-bracing, locking",
        vector_type="Torsional rigidity",
        structure=0.80, force=0.55, flow=0.10,
    ),
    "Y": Glyph(
        letter="Y",
        topology="Branching fork",
        physical_property="Distribution, splitting",
        vector_type="Flow bifurcation",
        structure=0.40, force=0.30, flow=0.70,
    ),
    "Z": Glyph(
        letter="Z",
        topology="Angular zigzag",
        physical_property="Rapid direction change",
        vector_type="Energy dissipation",
        structure=0.30, force=0.65, flow=0.60,
    ),
}


def get_glyph(letter: str) -> Glyph:
    """Return the Glyph for a single uppercase Latin letter.

    Raises ``KeyError`` for non-alphabetic characters.
    """
    return GLYPH_TABLE[letter.upper()]
