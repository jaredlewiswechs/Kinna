"use client";

import { useState } from "react";
import {
  buildSentence,
  INTENT_TEMPLATES,
  type SentencePlan,
} from "@/lib/sentence-builder";
import { VectorBar } from "@/components/vector-display";

const intentKeys = Object.keys(INTENT_TEMPLATES);

export default function BuildPage() {
  const [selectedIntent, setSelectedIntent] = useState<string | null>(null);
  const [result, setResult] = useState<SentencePlan | null>(null);

  function handleBuild(intentName: string) {
    setSelectedIntent(intentName);
    setResult(buildSentence(intentName));
  }

  return (
    <div className="page-enter">
      <div className="mb-8">
        <h1 className="text-[28px] font-bold tracking-tight">Build</h1>
        <p className="text-[15px] text-label-secondary mt-1">
          Generate sentences from geometric intent templates using vector
          matching.
        </p>
      </div>

      {/* Intent template selector */}
      <div className="mb-8">
        <p className="section-header">Intent Templates</p>
        <div className="grid gap-2 mt-3">
          {intentKeys.map((key) => {
            const intent = INTENT_TEMPLATES[key];
            const active = selectedIntent === key;
            return (
              <button
                key={key}
                onClick={() => handleBuild(key)}
                className={`card p-4 text-left transition-shadow ${
                  active
                    ? "ring-2 ring-accent shadow-md"
                    : "hover:shadow-sm"
                }`}
              >
                <div className="flex items-baseline justify-between">
                  <h3 className="text-[15px] font-semibold">
                    {key.replace(/_/g, " ")}
                  </h3>
                  <span className="text-[11px] font-mono text-label-quaternary">
                    {intent.tense}
                  </span>
                </div>
                <p className="text-[13px] text-label-tertiary mt-0.5">
                  {intent.description}
                </p>
                <div className="flex gap-4 mt-2 text-[11px] font-mono text-label-quaternary">
                  <span>
                    verb [{intent.verbTarget.map((v) => v.toFixed(2)).join(", ")}]
                  </span>
                  <span>
                    noun [{intent.nounTarget.map((v) => v.toFixed(2)).join(", ")}]
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {result && (
        <div className="flex flex-col gap-4">
          {/* Generated sentence */}
          <div className="card p-6 text-center">
            <p className="text-[11px] text-label-quaternary uppercase tracking-wider mb-2">
              Generated Sentence
            </p>
            <p className="text-[22px] font-semibold tracking-tight">
              {result.sentence}
            </p>
          </div>

          {/* Breakdown */}
          <div className="grid sm:grid-cols-2 gap-3">
            <div className="card p-5">
              <h3 className="text-[15px] font-semibold mb-1">
                Verb: {result.verb}
              </h3>
              <p className="text-[11px] text-label-quaternary mb-3">
                Tense: {result.tense} &middot; DI ={" "}
                {result.verbDI.toFixed(4)}
              </p>
              <div className="flex flex-col gap-2">
                <VectorBar
                  label="Structure"
                  value={INTENT_TEMPLATES[result.intent].verbTarget[0]}
                  color="#007AFF"
                />
                <VectorBar
                  label="Force"
                  value={INTENT_TEMPLATES[result.intent].verbTarget[1]}
                  color="#FF9500"
                />
                <VectorBar
                  label="Flow"
                  value={INTENT_TEMPLATES[result.intent].verbTarget[2]}
                  color="#34C759"
                />
              </div>
            </div>
            <div className="card p-5">
              <h3 className="text-[15px] font-semibold mb-1">
                Noun: {result.noun}
              </h3>
              <p className="text-[11px] text-label-quaternary mb-3">
                DI = {result.nounDI.toFixed(4)}
              </p>
              <div className="flex flex-col gap-2">
                <VectorBar
                  label="Structure"
                  value={INTENT_TEMPLATES[result.intent].nounTarget[0]}
                  color="#007AFF"
                />
                <VectorBar
                  label="Force"
                  value={INTENT_TEMPLATES[result.intent].nounTarget[1]}
                  color="#FF9500"
                />
                <VectorBar
                  label="Flow"
                  value={INTENT_TEMPLATES[result.intent].nounTarget[2]}
                  color="#34C759"
                />
              </div>
            </div>
          </div>

          {/* DI fitness */}
          <div className="card p-5">
            <p className="section-header">Match Fitness</p>
            <div className="flex flex-col gap-3 mt-3">
              <div className="flex items-center justify-between">
                <span className="text-[13px] text-label-secondary">
                  Verb DI (lower is better)
                </span>
                <span className="text-[13px] font-mono font-semibold">
                  {result.verbDI.toFixed(4)}
                </span>
              </div>
              <div className="h-2 bg-surface-secondary rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-accent transition-all duration-500"
                  style={{
                    width: `${Math.max(0, (1 - result.verbDI) * 100)}%`,
                  }}
                />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[13px] text-label-secondary">
                  Noun DI (lower is better)
                </span>
                <span className="text-[13px] font-mono font-semibold">
                  {result.nounDI.toFixed(4)}
                </span>
              </div>
              <div className="h-2 bg-surface-secondary rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-accent transition-all duration-500"
                  style={{
                    width: `${Math.max(0, (1 - result.nounDI) * 100)}%`,
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {!result && (
        <div className="card-inset p-8 text-center">
          <p className="text-label-quaternary text-[15px]">
            Select an intent template above to generate a sentence from
            geometric targets.
          </p>
        </div>
      )}
    </div>
  );
}
