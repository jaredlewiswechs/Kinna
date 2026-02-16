/**
 * Regime Locker — detects the physical regime for a query.
 *
 * TypeScript port of kinna/regime_locker.py (KL v1.4, Section 6.1)
 */

export type Regime =
  | "FLUID_DYNAMICS"
  | "STRUCTURAL_ENGINEERING"
  | "THERMAL"
  | "ELECTRICAL"
  | "MEDICINE"
  | "AVIATION"
  | "COMPOSITION"
  | "GENERAL";

export interface RegimeLock {
  regime: Regime;
  confidence: number;
  matchedKeywords: string[];
  query: string;
}

const REGIME_KEYWORDS: Record<Exclude<Regime, "GENERAL">, Set<string>> = {
  FLUID_DYNAMICS: new Set([
    "water", "flow", "pipe", "fluid", "liquid", "stream", "current",
    "wave", "tide", "ocean", "river", "drain", "pump", "valve",
    "pressure", "turbulence", "laminar", "viscous", "hydraulic",
    "wind", "air", "draft", "ventilation",
  ]),
  STRUCTURAL_ENGINEERING: new Set([
    "beam", "load", "build", "structure", "bridge", "column",
    "foundation", "steel", "concrete", "frame", "truss", "support",
    "wall", "roof", "floor", "capital", "city", "tower", "arch",
    "stress", "strain", "shear", "tension", "compression",
  ]),
  THERMAL: new Set([
    "heat", "temperature", "thermal", "cold", "hot", "warm",
    "freeze", "melt", "boil", "burn", "fire", "flame", "cool",
    "insulate", "conduction", "convection", "radiation",
  ]),
  ELECTRICAL: new Set([
    "electric", "voltage", "current", "circuit", "wire", "charge",
    "battery", "power", "resistance", "capacitor", "inductor",
    "signal", "frequency", "amp", "watt", "ohm",
  ]),
  MEDICINE: new Set([
    "patient", "treatment", "diagnosis", "symptom", "disease",
    "drug", "medicine", "therapy", "surgery", "doctor", "hospital",
    "clinical", "dose", "prescription", "health", "medical",
    "organ", "tissue", "blood", "heart",
  ]),
  AVIATION: new Set([
    "aircraft", "flight", "pilot", "wing", "trim", "altitude",
    "runway", "cockpit", "throttle", "rudder", "aileron",
    "takeoff", "landing", "avionics", "mcas", "boeing", "airbus",
    "pitch", "yaw", "roll", "stall",
  ]),
  COMPOSITION: new Set([
    "write", "writing", "draft", "document", "text", "essay",
    "paragraph", "sentence", "word", "edit", "revise", "author",
    "publish", "manuscript", "chapter", "novel", "story", "poem",
  ]),
};

export const REGIME_LABELS: Record<Regime, string> = {
  FLUID_DYNAMICS: "Fluid Dynamics",
  STRUCTURAL_ENGINEERING: "Structural Engineering",
  THERMAL: "Thermal",
  ELECTRICAL: "Electrical",
  MEDICINE: "Medicine",
  AVIATION: "Aviation",
  COMPOSITION: "Composition",
  GENERAL: "General",
};

export const REGIME_ICONS: Record<Regime, string> = {
  FLUID_DYNAMICS: "droplet",
  STRUCTURAL_ENGINEERING: "building",
  THERMAL: "flame",
  ELECTRICAL: "bolt",
  MEDICINE: "heart",
  AVIATION: "plane",
  COMPOSITION: "pencil",
  GENERAL: "globe",
};

export function detectRegime(query: string): RegimeLock {
  const queryLower = query.toLowerCase();
  const queryWords = new Set(queryLower.split(/\s+/));

  let bestRegime: Regime = "GENERAL";
  let bestScore = 0;
  let bestMatches: string[] = [];

  for (const [regime, keywords] of Object.entries(REGIME_KEYWORDS) as [
    Exclude<Regime, "GENERAL">,
    Set<string>,
  ][]) {
    const matches = new Set<string>();
    for (const kw of keywords) {
      if (queryWords.has(kw)) {
        matches.add(kw);
      } else if (kw.length > 3 && queryLower.includes(kw)) {
        matches.add(kw);
      }
    }

    if (matches.size > bestMatches.length) {
      bestMatches = Array.from(matches).sort();
      bestRegime = regime;
      bestScore = Math.min(matches.size / 3.0, 1.0);
    }
  }

  return {
    regime: bestRegime,
    confidence: bestScore,
    matchedKeywords: bestMatches,
    query,
  };
}
