"use client";

import { useState } from "react";
import { assembleWord, type WordVector } from "@/lib/assembler";
import { tagRegimes } from "@/lib/cluster-tagger";
import { VectorCard } from "@/components/vector-display";
import { GlyphGrid, GlyphDetail } from "@/components/glyph-grid";

export default function AssemblePage() {
  const [input, setInput] = useState("");
  const [results, setResults] = useState<
    { vector: WordVector; tags: string[] }[]
  >([]);
  const [dbResults, setDbResults] = useState<any[]>([]);
  const [dbLoading, setDbLoading] = useState(false);
  const [selectedGlyphIndex, setSelectedGlyphIndex] = useState<{
    wordIdx: number;
    glyphIdx: number;
  } | null>(null);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const words = input
      .trim()
      .split(/[\s,]+/)
      .filter(Boolean);
    if (words.length === 0) return;

    const newResults = words.map((w) => {
      const vector = assembleWord(w);
      const tags = tagRegimes(vector);
      return { vector, tags };
    });
    setResults(newResults);
    setSelectedGlyphIndex(null);
  }

  async function fetchDB() {
    const words = input
      .trim()
      .split(/[,\s]+/)
      .filter(Boolean);
    if (words.length === 0) return;
    const q = words[0];
    setDbLoading(true);
    try {
      const res = await fetch(`/api/words?q=${encodeURIComponent(q)}&limit=12`);
      if (res.ok) {
        const data = await res.json();
        setDbResults(data);
      } else {
        setDbResults([]);
      }
    } catch (err) {
      console.error(err);
      setDbResults([]);
    } finally {
      setDbLoading(false);
    }
  }

  const selectedGlyph =
    selectedGlyphIndex !== null
      ? results[selectedGlyphIndex.wordIdx]?.vector.glyphs[
          selectedGlyphIndex.glyphIdx
        ]
      : null;

  return (
    <div className="page-enter">
      <div className="mb-8">
        <h1 className="text-[28px] font-bold tracking-tight">Assemble</h1>
        <p className="text-[15px] text-label-secondary mt-1">
          Decompose words into their kinematic vector representation.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2 mb-8">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter words (e.g. WATER FIRE STONE)"
          className="input-field flex-1"
          autoFocus
        />
        <button
          type="button"
          className="btn"
          onClick={fetchDB}
          disabled={dbLoading}
        >
          {dbLoading ? 'Searching DB...' : 'Search DB'}
        </button>
        <button type="submit" className="btn-primary shrink-0">
          Assemble
        </button>
      </form>

      {results.length > 0 && (
        <div className="flex flex-col gap-5">
          {results.map((r, wi) => (
            <div key={wi} className="flex flex-col gap-3">
              <VectorCard
                word={r.vector.word}
                structure={r.vector.structure}
                force={r.vector.force}
                flow={r.vector.flow}
                density={r.vector.density}
              />

              {/* Glyph decomposition */}
              <div className="card p-4">
                <p className="section-header">Glyph Decomposition</p>
                <div
                  className="cursor-pointer"
                  onClick={(e) => {
                    const target = (e.target as HTMLElement).closest(
                      ".glyph-cell"
                    );
                    if (!target) return;
                    const idx = Array.from(
                      target.parentElement!.children
                    ).indexOf(target);
                    setSelectedGlyphIndex({ wordIdx: wi, glyphIdx: idx });
                  }}
                >
                  <GlyphGrid
                    glyphs={r.vector.glyphs}
                    highlightIndex={
                      selectedGlyphIndex?.wordIdx === wi
                        ? selectedGlyphIndex.glyphIdx
                        : undefined
                    }
                  />
                </div>

                {selectedGlyphIndex?.wordIdx === wi && selectedGlyph && (
                  <div className="mt-3">
                    <GlyphDetail glyph={selectedGlyph} />
                  </div>
                )}
              </div>

              {/* Regime tags */}
              {r.tags.length > 0 && (
                <div className="card p-4">
                  <p className="section-header">Regime Tags</p>
                  <div className="flex flex-wrap gap-1.5">
                    {r.tags.map((tag) => (
                      <span
                        key={tag}
                        className="inline-flex items-center px-2.5 py-1 rounded-lg bg-accent/8 text-accent text-[12px] font-medium"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {results.length === 0 && (
        <div className="card-inset p-8 text-center">
          <p className="text-label-quaternary text-[15px]">
            Enter one or more words to see their kinematic vectors.
          </p>
          <div className="flex flex-wrap justify-center gap-2 mt-4">
            {["WATER", "STONE", "FIRE", "BRIDGE", "FLOW"].map((w) => (
              <button
                key={w}
                onClick={() => {
                  setInput(w);
                  const vector = assembleWord(w);
                  const tags = tagRegimes(vector);
                  setResults([{ vector, tags }]);
                }}
                className="btn-secondary text-[13px] px-3 py-1.5"
              >
                {w}
              </button>
            ))}
          </div>
        </div>
      )}

      {dbResults.length > 0 && (
        <div className="card p-4 mt-6">
          <p className="section-header">Database Results</p>
          <div className="flex flex-col gap-3 mt-3">
            {dbResults.map((r, i) => (
              <div key={i} className="border rounded p-3">
                <div className="flex items-baseline justify-between">
                  <strong className="text-[14px]">{r.word}</strong>
                  <span className="text-[12px] text-label-quaternary">{r.synset_id}</span>
                </div>
                <div className="text-[13px] text-label-secondary mt-1">
                  {r.definition}
                </div>
                <div className="text-[12px] text-label-quaternary mt-2">
                  density: {r.density?.toFixed(3)} — tags: {r.regime_tags}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
