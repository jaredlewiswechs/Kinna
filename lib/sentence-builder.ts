/**
 * Sentence Builder — generates sentences by solving geometric equations.
 *
 * TypeScript port of kinna/sentence_builder.py (KL v1.4, Section 2.3)
 */

import { type Vec3, assembleWord } from "./assembler";
import { distortionIndex } from "./di-calculator";
import { type Tense, applyTense } from "./tense-modifier";

export interface GeometricIntent {
  description: string;
  verbTarget: Vec3;
  nounTarget: Vec3;
  tense: Tense;
}

export const INTENT_TEMPLATES: Record<string, GeometricIntent> = {
  MOVE_UP: {
    description: "Upward motion with force",
    verbTarget: [0.40, 0.70, 0.50],
    nounTarget: [0.70, 0.50, 0.20],
    tense: "base",
  },
  MOVE_DOWN: {
    description: "Downward / heavy motion",
    verbTarget: [0.50, 0.65, 0.30],
    nounTarget: [0.75, 0.60, 0.10],
    tense: "base",
  },
  FLOW_THROUGH: {
    description: "Fluid passage or transfer",
    verbTarget: [0.30, 0.20, 0.80],
    nounTarget: [0.40, 0.15, 0.70],
    tense: "base",
  },
  IMPACT_STOP: {
    description: "Forceful stop or collision",
    verbTarget: [0.60, 0.80, 0.10],
    nounTarget: [0.80, 0.55, 0.10],
    tense: "base",
  },
  STABLE_REST: {
    description: "Static equilibrium / rest",
    verbTarget: [0.75, 0.20, 0.15],
    nounTarget: [0.85, 0.25, 0.10],
    tense: "past",
  },
  ACTIVE_TRANSFER: {
    description: "Active transfer or exchange",
    verbTarget: [0.45, 0.45, 0.65],
    nounTarget: [0.55, 0.30, 0.55],
    tense: "active",
  },
};

export const BUILTIN_VERBS = [
  "RISE", "FALL", "PUSH", "PULL", "FLOW", "STOP", "BREAK", "BUILD",
  "MOVE", "TURN", "LIFT", "DROP", "HOLD", "SEND", "TAKE", "GIVE",
  "RUN", "WALK", "FLY", "SWIM", "JUMP", "CLIMB", "SLIDE", "SPIN",
  "CRASH", "BLAST", "DRIFT", "SHIFT", "TRUST", "GUARD", "BLOCK",
  "PRESS", "SPARK", "GRIP", "FLING", "THROW", "CATCH", "REST",
  "STAND", "SIT", "STRETCH", "SHRINK", "GROW", "SPLIT", "MERGE",
  "ASCEND", "DESCEND", "SURGE", "DRAIN", "POUR", "STREAM",
];

export const BUILTIN_NOUNS = [
  "ROCK", "WATER", "FIRE", "WIND", "BEAM", "WALL", "BRIDGE",
  "TOWER", "MASS", "FORCE", "WAVE", "STONE", "STEEL", "GLASS",
  "LIGHT", "HEAT", "FROST", "STORM", "BOLT", "CHAIN", "ROPE",
  "WHEEL", "GATE", "VALVE", "PIPE", "FRAME", "BLOCK", "SPRING",
  "ROCKET", "SHIP", "CRAFT", "DISK", "GLOBE", "ARCH", "DOME",
  "SHAFT", "BLADE", "PRISM", "FLUX", "PULSE", "SPARK",
];

export interface SentencePlan {
  intent: string;
  article: string;
  noun: string;
  verb: string;
  tense: Tense;
  nounDI: number;
  verbDI: number;
  sentence: string;
}

function findBestWord(
  candidates: string[],
  target: Vec3,
): { word: string; di: number } {
  let bestWord = candidates[0];
  let bestDI = Infinity;

  for (const w of candidates) {
    const wv = assembleWord(w);
    const di = distortionIndex([wv.structure, wv.force, wv.flow], target);
    if (di < bestDI) {
      bestDI = di;
      bestWord = w;
    }
  }

  return { word: bestWord, di: bestDI };
}

export function buildSentence(intentName: string): SentencePlan {
  const intent = INTENT_TEMPLATES[intentName];
  if (!intent) throw new Error(`Unknown intent: ${intentName}`);

  const bestVerb = findBestWord(BUILTIN_VERBS, intent.verbTarget);
  const bestNoun = findBestWord(BUILTIN_NOUNS, intent.nounTarget);

  const tv = applyTense(bestVerb.word, intent.tense);
  const verbForm = tv.word;

  const parts = ["THE", bestNoun.word, verbForm];
  const raw = parts.join(" ");
  const sentence = raw[0] + raw.slice(1).toLowerCase() + ".";

  return {
    intent: intentName,
    article: "THE",
    noun: bestNoun.word,
    verb: bestVerb.word,
    tense: intent.tense,
    nounDI: bestNoun.di,
    verbDI: bestVerb.di,
    sentence,
  };
}
