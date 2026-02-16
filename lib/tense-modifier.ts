/**
 * Tense Modifier — applies morphological suffixes as geometric state changes.
 *
 * TypeScript port of kinna/tense_modifier.py (KL v1.4, Section 2.3.4)
 */

import { type Vec3, assembleWord } from "./assembler";

export type Tense = "base" | "past" | "active" | "future";

export interface TensedVector {
  word: string;
  tense: Tense;
  structure: number;
  force: number;
  flow: number;
  baseWord: string;
}

const ED_BLEND: Vec3 = [0.15, 0.10, -0.10];
const ING_BLEND: Vec3 = [-0.08, 0.05, 0.15];

function applyBlend(base: Vec3, blend: Vec3): Vec3 {
  return [
    Math.max(0, Math.min(1, base[0] + blend[0])),
    Math.max(0, Math.min(1, base[1] + blend[1])),
    Math.max(0, Math.min(1, base[2] + blend[2])),
  ];
}

export function applyTense(word: string, tense: Tense): TensedVector {
  let upper = word.toUpperCase();
  let baseWord = upper;

  if (upper.endsWith("ING") && upper.length > 3) {
    baseWord = upper.slice(0, -3);
  } else if (upper.endsWith("ED") && upper.length > 2) {
    baseWord = upper.slice(0, -2);
  }

  const wv = assembleWord(baseWord);
  const baseVec: Vec3 = [wv.structure, wv.force, wv.flow];

  let vec: Vec3;
  let display: string;

  if (tense === "past") {
    vec = applyBlend(baseVec, ED_BLEND);
    display = baseWord + "ED";
  } else if (tense === "active") {
    vec = applyBlend(baseVec, ING_BLEND);
    display = baseWord + "ING";
  } else {
    vec = baseVec;
    display = baseWord;
  }

  return {
    word: display,
    tense,
    structure: vec[0],
    force: vec[1],
    flow: vec[2],
    baseWord,
  };
}
