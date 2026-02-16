/**
 * Distortion Index Calculator — quantifies geometric mismatch.
 *
 * TypeScript port of kinna/di_calculator.py (KL v1.4, Section 5.2)
 */

import { type Vec3, assembleWord } from "./assembler";

export type DIVerdict = "congruent" | "suspect" | "conflict";

export const DI_CONGRUENT_MAX = 0.35;
export const DI_SUSPECT_MAX = 0.70;

export interface DIResult {
  word: string;
  di: number;
  verdict: DIVerdict;
  wordVector: Vec3;
  targetVector: Vec3;
}

function cosineSimilarity(a: Vec3, b: Vec3): number {
  const dot = a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const magA = Math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2);
  const magB = Math.sqrt(b[0] ** 2 + b[1] ** 2 + b[2] ** 2);
  if (magA === 0 || magB === 0) return 0;
  return dot / (magA * magB);
}

export function classifyDI(di: number): DIVerdict {
  if (di < DI_CONGRUENT_MAX) return "congruent";
  if (di < DI_SUSPECT_MAX) return "suspect";
  return "conflict";
}

export function distortionIndex(wordVec: Vec3, targetVec: Vec3): number {
  return 1.0 - cosineSimilarity(wordVec, targetVec);
}

export function compareWords(wordA: string, wordB: string): DIResult {
  const va = assembleWord(wordA);
  const vb = assembleWord(wordB);
  const vecA: Vec3 = [va.structure, va.force, va.flow];
  const vecB: Vec3 = [vb.structure, vb.force, vb.flow];
  const di = distortionIndex(vecA, vecB);
  return {
    word: `${wordA.toUpperCase()} vs ${wordB.toUpperCase()}`,
    di,
    verdict: classifyDI(di),
    wordVector: vecA,
    targetVector: vecB,
  };
}

export function compareWordToTarget(word: string, target: Vec3): DIResult {
  const wv = assembleWord(word);
  const vec: Vec3 = [wv.structure, wv.force, wv.flow];
  const di = distortionIndex(vec, target);
  return {
    word: word.toUpperCase(),
    di,
    verdict: classifyDI(di),
    wordVector: vec,
    targetVector: target,
  };
}
