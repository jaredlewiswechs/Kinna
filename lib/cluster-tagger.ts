/**
 * Cluster Tagger — assigns phonosemantic regime tags to word vectors.
 *
 * TypeScript port of kinna/cluster_tagger.py (KL v1.4, Section 4)
 */

import type { WordVector } from "./assembler";

export function tagRegimes(wv: WordVector): string[] {
  const tags: string[] = [];
  const word = wv.word.toUpperCase();

  if (word.endsWith("ST")) tags.push("ST_ANCHOR");
  if (word.startsWith("FL")) tags.push("FL_VECTOR");
  if (word.startsWith("GL")) tags.push("GL_VECTOR");
  if (word.startsWith("CR")) tags.push("CR_FRACTURE");
  if (word.startsWith("SP")) tags.push("SP_SCATTER");
  if (word.startsWith("SW")) tags.push("SW_SWEEP");
  if (word.startsWith("TR")) tags.push("TR_TRAVERSE");
  if (word.startsWith("GR")) tags.push("GR_GRIP");

  if (wv.structure > 0.70) tags.push("HIGH_STRUCTURE");
  if (wv.force > 0.60) tags.push("HIGH_FORCE");
  if (wv.flow > 0.70) tags.push("HIGH_FLOW");

  if (wv.flow > 0.65 && wv.structure < 0.45) tags.push("FLUID_REGIME");
  if (wv.structure > 0.65 && wv.flow < 0.30) tags.push("STRUCTURAL_REGIME");
  if (wv.force > 0.55 && wv.structure > 0.55) tags.push("FORCE_REGIME");
  if (wv.flow > 0.50 && wv.force < 0.30) tags.push("PASSIVE_FLOW");

  return tags;
}
