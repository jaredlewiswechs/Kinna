"use client";

import { useState } from "react";
import { assembleWord } from "@/lib/assembler";
import { compareWords, type DIResult } from "@/lib/di-calculator";
import { VectorBar, VerdictBadge } from "@/components/vector-display";

export default function ComparePage() {
  const [wordA, setWordA] = useState("");
  const [wordB, setWordB] = useState("");
  const [result, setResult] = useState<DIResult | null>(null);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const a = wordA.trim();
    const b = wordB.trim();
    if (!a || !b) return;
    setResult(compareWords(a, b));
  }

  function tryExample(a: string, b: string) {
    setWordA(a);
    setWordB(b);
    setResult(compareWords(a, b));
  }

  return (
    <div className="page-enter">
      <div className="mb-8">
        <h1 className="text-[28px] font-bold tracking-tight">Compare</h1>
        <p className="text-[15px] text-label-secondary mt-1">
          Compute the Distortion Index between two words.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2 mb-8">
        <input
          type="text"
          value={wordA}
          onChange={(e) => setWordA(e.target.value)}
          placeholder="First word"
          className="input-field flex-1"
          autoFocus
        />
        <div className="flex items-center justify-center text-label-quaternary text-[13px] font-medium sm:px-2">
          vs
        </div>
        <input
          type="text"
          value={wordB}
          onChange={(e) => setWordB(e.target.value)}
          placeholder="Second word"
          className="input-field flex-1"
        />
        <button type="submit" className="btn-primary shrink-0">
          Compare
        </button>
      </form>

      {result && (
        <div className="flex flex-col gap-4">
          {/* Verdict */}
          <div className="card p-5 text-center">
            <VerdictBadge verdict={result.verdict} di={result.di} />
            <p className="text-[13px] text-label-tertiary mt-3">
              {result.verdict === "congruent" &&
                "These words share similar geometric properties."}
              {result.verdict === "suspect" &&
                "These words have moderate geometric divergence."}
              {result.verdict === "conflict" &&
                "These words have significant geometric mismatch."}
            </p>
          </div>

          {/* Side-by-side vectors */}
          <div className="grid sm:grid-cols-2 gap-3">
            <div className="card p-5">
              <h3 className="text-[15px] font-semibold mb-3">
                {wordA.toUpperCase()}
              </h3>
              <div className="flex flex-col gap-2">
                <VectorBar
                  label="Structure"
                  value={result.wordVector[0]}
                  color="#007AFF"
                />
                <VectorBar
                  label="Force"
                  value={result.wordVector[1]}
                  color="#FF9500"
                />
                <VectorBar
                  label="Flow"
                  value={result.wordVector[2]}
                  color="#34C759"
                />
              </div>
            </div>
            <div className="card p-5">
              <h3 className="text-[15px] font-semibold mb-3">
                {wordB.toUpperCase()}
              </h3>
              <div className="flex flex-col gap-2">
                <VectorBar
                  label="Structure"
                  value={result.targetVector[0]}
                  color="#007AFF"
                />
                <VectorBar
                  label="Force"
                  value={result.targetVector[1]}
                  color="#FF9500"
                />
                <VectorBar
                  label="Flow"
                  value={result.targetVector[2]}
                  color="#34C759"
                />
              </div>
            </div>
          </div>

          {/* DI scale */}
          <div className="card p-5">
            <p className="section-header">Distortion Index Scale</p>
            <div className="mt-3 relative h-3 rounded-full overflow-hidden bg-surface-secondary">
              <div
                className="absolute inset-y-0 left-0 bg-congruent/60"
                style={{ width: "35%" }}
              />
              <div
                className="absolute inset-y-0 bg-suspect/60"
                style={{ left: "35%", width: "35%" }}
              />
              <div
                className="absolute inset-y-0 right-0 bg-conflict/60"
                style={{ left: "70%" }}
              />
              {/* Marker */}
              <div
                className="absolute top-1/2 -translate-y-1/2 w-3.5 h-3.5 bg-white rounded-full border-2 border-label-primary shadow-sm transition-all duration-500"
                style={{ left: `${Math.min(result.di * 100, 100)}%`, marginLeft: "-7px" }}
              />
            </div>
            <div className="flex justify-between mt-2 text-[11px] text-label-quaternary">
              <span>0.00 Congruent</span>
              <span>0.35</span>
              <span>0.70</span>
              <span>Conflict 1.00</span>
            </div>
          </div>
        </div>
      )}

      {!result && (
        <div className="card-inset p-8 text-center">
          <p className="text-label-quaternary text-[15px] mb-4">
            Try comparing two words to see their geometric relationship.
          </p>
          <div className="flex flex-wrap justify-center gap-2">
            {[
              ["WATER", "STEAM"],
              ["ROCK", "STONE"],
              ["FIRE", "WATER"],
              ["DRAFT", "BREEZE"],
            ].map(([a, b]) => (
              <button
                key={`${a}-${b}`}
                onClick={() => tryExample(a, b)}
                className="btn-secondary text-[13px] px-3 py-1.5"
              >
                {a} vs {b}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
