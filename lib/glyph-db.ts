/**
 * Glyph Database — maps each Latin letter to a 3D mechanical vector.
 *
 * TypeScript port of kinna/glyph_db.py (KL v1.4, Table 2.1)
 */

export interface Glyph {
  letter: string;
  topology: string;
  physicalProperty: string;
  vectorType: string;
  structure: number;
  force: number;
  flow: number;
}

export const GLYPH_TABLE: Record<string, Glyph> = {
  A: { letter: "A", topology: "Triangular frame, crossbar", physicalProperty: "Stability, load distribution", vectorType: "Static equilibrium", structure: 0.90, force: 0.30, flow: 0.10 },
  B: { letter: "B", topology: "Vertical spine, dual lobes", physicalProperty: "Containment, redundancy", vectorType: "Volume storage", structure: 0.80, force: 0.20, flow: 0.15 },
  C: { letter: "C", topology: "Open arc", physicalProperty: "Reception, incomplete enclosure", vectorType: "Directional aperture", structure: 0.40, force: 0.15, flow: 0.60 },
  D: { letter: "D", topology: "Vertical spine, single lobe", physicalProperty: "Weight, mass concentration", vectorType: "Gravitational load", structure: 0.70, force: 0.65, flow: 0.10 },
  E: { letter: "E", topology: "Vertical with horizontal tiers", physicalProperty: "Layering, stratification", vectorType: "Hierarchical distribution", structure: 0.60, force: 0.25, flow: 0.40 },
  F: { letter: "F", topology: "Vertical post, cantilever arms", physicalProperty: "Reach, leverage", vectorType: "Moment arm", structure: 0.55, force: 0.70, flow: 0.30 },
  G: { letter: "G", topology: "Arc with inward hook", physicalProperty: "Capture, gating", vectorType: "Flow control", structure: 0.50, force: 0.35, flow: 0.55 },
  H: { letter: "H", topology: "Two pillars, crossbeam", physicalProperty: "Bridging, connection", vectorType: "Tensile span", structure: 0.85, force: 0.30, flow: 0.35 },
  I: { letter: "I", topology: "Vertical line", physicalProperty: "Axis, alignment", vectorType: "Linear direction", structure: 0.45, force: 0.20, flow: 0.50 },
  J: { letter: "J", topology: "Vertical line with bottom hook", physicalProperty: "Hook, leverage", vectorType: "Pendular capture", structure: 0.40, force: 0.45, flow: 0.50 },
  K: { letter: "K", topology: "Vertical with acute diagonals", physicalProperty: "Shear, cutting action", vectorType: "Kinetic impact", structure: 0.50, force: 0.80, flow: 0.35 },
  L: { letter: "L", topology: "Vertical to horizontal bend", physicalProperty: "Flow redirection, pooling", vectorType: "Liquid dynamics", structure: 0.35, force: 0.15, flow: 0.80 },
  M: { letter: "M", topology: "Double peak, stable base", physicalProperty: "Oscillation, wave stability", vectorType: "Harmonic frequency", structure: 0.75, force: 0.40, flow: 0.45 },
  N: { letter: "N", topology: "Two verticals, diagonal bridge", physicalProperty: "Transfer, passage", vectorType: "State transition", structure: 0.60, force: 0.30, flow: 0.55 },
  O: { letter: "O", topology: "Closed loop", physicalProperty: "Complete containment", vectorType: "Volume enclosure", structure: 0.85, force: 0.20, flow: 0.20 },
  P: { letter: "P", topology: "Vertical spine, top bulb", physicalProperty: "Pressure, potential", vectorType: "Stored energy", structure: 0.55, force: 0.75, flow: 0.25 },
  Q: { letter: "Q", topology: "Closed loop with tail", physicalProperty: "Containment with release", vectorType: "Controlled discharge", structure: 0.80, force: 0.30, flow: 0.35 },
  R: { letter: "R", topology: "Vertical, bulb, diagonal leg", physicalProperty: "Resistance, bracing", vectorType: "Force opposition", structure: 0.65, force: 0.60, flow: 0.30 },
  S: { letter: "S", topology: "Sinuous curve", physicalProperty: "Slip, flexibility", vectorType: "Low friction coefficient", structure: 0.20, force: 0.15, flow: 0.85 },
  T: { letter: "T", topology: "Vertical post, horizontal cap", physicalProperty: "Hard stop, limit", vectorType: "Impact boundary", structure: 0.70, force: 0.60, flow: 0.05 },
  U: { letter: "U", topology: "Open vessel", physicalProperty: "Reception, holding", vectorType: "Capacity volume", structure: 0.50, force: 0.10, flow: 0.55 },
  V: { letter: "V", topology: "Converging lines", physicalProperty: "Focus, concentration", vectorType: "Vector convergence", structure: 0.45, force: 0.70, flow: 0.40 },
  W: { letter: "W", topology: "Double valley", physicalProperty: "Wave, instability", vectorType: "Oscillatory motion", structure: 0.35, force: 0.40, flow: 0.75 },
  X: { letter: "X", topology: "Intersecting diagonals", physicalProperty: "Cross-bracing, locking", vectorType: "Torsional rigidity", structure: 0.80, force: 0.55, flow: 0.10 },
  Y: { letter: "Y", topology: "Branching fork", physicalProperty: "Distribution, splitting", vectorType: "Flow bifurcation", structure: 0.40, force: 0.30, flow: 0.70 },
  Z: { letter: "Z", topology: "Angular zigzag", physicalProperty: "Rapid direction change", vectorType: "Energy dissipation", structure: 0.30, force: 0.65, flow: 0.60 },
};

export function getGlyph(letter: string): Glyph {
  const g = GLYPH_TABLE[letter.toUpperCase()];
  if (!g) throw new Error(`Unknown glyph: ${letter}`);
  return g;
}
