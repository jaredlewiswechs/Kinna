"use client";

import { useState } from "react";
import {
  detectRegime,
  REGIME_LABELS,
  type RegimeLock,
  type Regime,
} from "@/lib/regime-locker";

const REGIME_COLORS: Record<Regime, string> = {
  FLUID_DYNAMICS: "#007AFF",
  STRUCTURAL_ENGINEERING: "#FF9500",
  THERMAL: "#FF3B30",
  ELECTRICAL: "#FFCC00",
  MEDICINE: "#FF2D55",
  AVIATION: "#5856D6",
  COMPOSITION: "#AF52DE",
  GENERAL: "#8E8E93",
};

const REGIME_DESCRIPTIONS: Record<Regime, string> = {
  FLUID_DYNAMICS: "Fluid mechanics, flow patterns, hydraulic systems, and wave dynamics.",
  STRUCTURAL_ENGINEERING: "Load-bearing analysis, material stability, and structural integrity.",
  THERMAL: "Heat transfer, thermodynamics, combustion, and temperature dynamics.",
  ELECTRICAL: "Circuit analysis, electrical conductance, signal processing, and power systems.",
  MEDICINE: "Clinical pathology, treatment protocols, anatomical systems, and diagnostics.",
  AVIATION: "Aerodynamic forces, flight systems, avionics, and aircraft control.",
  COMPOSITION: "Written language construction, editing, revision, and document authoring.",
  GENERAL: "No specific physics regime detected. General-purpose analysis applies.",
};

export default function RegimePage() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<RegimeLock | null>(null);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setResult(detectRegime(query.trim()));
  }

  function tryExample(q: string) {
    setQuery(q);
    setResult(detectRegime(q));
  }

  return (
    <div className="page-enter">
      <div className="mb-8">
        <h1 className="text-[28px] font-bold tracking-tight">Regime</h1>
        <p className="text-[15px] text-label-secondary mt-1">
          Detect the physical domain and lock the semantic context.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2 mb-8">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe a scenario (e.g. &quot;the fluid flows through the pipe&quot;)"
          className="input-field flex-1"
          autoFocus
        />
        <button type="submit" className="btn-primary shrink-0">
          Detect
        </button>
      </form>

      {result && (
        <div className="flex flex-col gap-4">
          {/* Regime result */}
          <div className="card p-6 text-center">
            <div
              className="inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-3"
              style={{
                backgroundColor: `${REGIME_COLORS[result.regime]}15`,
              }}
            >
              <span
                className="text-2xl font-bold"
                style={{ color: REGIME_COLORS[result.regime] }}
              >
                {REGIME_LABELS[result.regime].charAt(0)}
              </span>
            </div>
            <h2
              className="text-[22px] font-bold"
              style={{ color: REGIME_COLORS[result.regime] }}
            >
              {REGIME_LABELS[result.regime]}
            </h2>
            <p className="text-[13px] text-label-tertiary mt-2 max-w-sm mx-auto">
              {REGIME_DESCRIPTIONS[result.regime]}
            </p>
          </div>

          {/* Confidence meter */}
          <div className="card p-5">
            <div className="flex items-center justify-between mb-2">
              <p className="section-header mb-0">Confidence</p>
              <span className="text-[15px] font-mono font-semibold">
                {(result.confidence * 100).toFixed(0)}%
              </span>
            </div>
            <div className="h-2.5 bg-surface-secondary rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${result.confidence * 100}%`,
                  backgroundColor: REGIME_COLORS[result.regime],
                }}
              />
            </div>
          </div>

          {/* Matched keywords */}
          {result.matchedKeywords.length > 0 && (
            <div className="card p-5">
              <p className="section-header">Matched Keywords</p>
              <div className="flex flex-wrap gap-1.5 mt-2">
                {result.matchedKeywords.map((kw) => (
                  <span
                    key={kw}
                    className="inline-flex items-center px-3 py-1.5 rounded-lg text-[13px] font-medium"
                    style={{
                      backgroundColor: `${REGIME_COLORS[result.regime]}12`,
                      color: REGIME_COLORS[result.regime],
                    }}
                  >
                    {kw}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Query echo */}
          <div className="card p-5">
            <p className="section-header">Input Query</p>
            <p className="text-[15px] text-label-secondary mt-1 italic">
              &ldquo;{result.query}&rdquo;
            </p>
          </div>
        </div>
      )}

      {!result && (
        <div className="card-inset p-8 text-center">
          <p className="text-label-quaternary text-[15px] mb-4">
            Enter a natural language query to detect its physical regime.
          </p>
          <div className="flex flex-col gap-2">
            {[
              "the fluid flows through the pipe under pressure",
              "the steel beam supports the bridge load",
              "the pilot adjusted the trim during flight",
              "the patient received treatment at the hospital",
            ].map((q) => (
              <button
                key={q}
                onClick={() => tryExample(q)}
                className="btn-secondary text-[13px] px-3 py-2 text-left"
              >
                &ldquo;{q}&rdquo;
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
