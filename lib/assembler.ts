/**
 * Word Assembly — computes the composite mechanical vector for any word.
 *
 * TypeScript port of kinna/assembler.py (KL v1.4, Section 2.2)
 */

import { GLYPH_TABLE, type Glyph, getGlyph } from "./glyph-db";

export type Vec3 = [number, number, number];

const INITIAL_WEIGHT = 1.2;
const MEDIAL_WEIGHT = 1.0;
const TERMINAL_WEIGHT = 0.9;

export interface WordVector {
  word: string;
  structure: number;
  force: number;
  flow: number;
  glyphs: Glyph[];
  density: number;
}

function positionalWeight(index: number, length: number): number {
  if (length <= 1) return INITIAL_WEIGHT;
  const third = length / 3.0;
  if (index < third) return INITIAL_WEIGHT;
  if (index < 2 * third) return MEDIAL_WEIGHT;
  return TERMINAL_WEIGHT;
}

export function assembleWord(word: string): WordVector {
  const letters = word
    .split("")
    .filter((ch) => /[a-zA-Z]/.test(ch))
    .map((ch) => ch.toUpperCase());

  if (letters.length === 0) {
    return { word, structure: 0, force: 0, flow: 0, glyphs: [], density: 0 };
  }

  const glyphs = letters.map((ch) => getGlyph(ch));
  const n = glyphs.length;

  let sSum = 0, fSum = 0, flSum = 0, wSum = 0;
  for (let i = 0; i < n; i++) {
    const w = positionalWeight(i, n);
    sSum += glyphs[i].structure * w;
    fSum += glyphs[i].force * w;
    flSum += glyphs[i].flow * w;
    wSum += w;
  }

  const structure = sSum / wSum;
  const force = fSum / wSum;
  const flow = flSum / wSum;
  const density = Math.sqrt(structure ** 2 + force ** 2 + flow ** 2);

  return {
    word: word.toUpperCase(),
    structure,
    force,
    flow,
    glyphs,
    density,
  };
}

export function assembleMany(words: string[]): WordVector[] {
  return words.map(assembleWord);
}
