"use client";

import type { Glyph } from "@/lib/glyph-db";

interface GlyphGridProps {
  glyphs: Glyph[];
  highlightIndex?: number;
}

export function GlyphGrid({ glyphs, highlightIndex }: GlyphGridProps) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {glyphs.map((g, i) => {
        const isHighlight = highlightIndex === i;
        return (
          <div
            key={i}
            className={`glyph-cell flex flex-col items-center p-2 rounded-xl min-w-[44px] ${
              isHighlight
                ? "bg-accent/10 ring-1 ring-accent/30"
                : "bg-surface-secondary"
            }`}
          >
            <span className="text-[17px] font-semibold">{g.letter}</span>
            <div className="flex gap-1 mt-1">
              <div
                className="w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: "#007AFF", opacity: g.structure }}
                title={`S: ${g.structure}`}
              />
              <div
                className="w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: "#FF9500", opacity: g.force }}
                title={`F: ${g.force}`}
              />
              <div
                className="w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: "#34C759", opacity: g.flow }}
                title={`Fl: ${g.flow}`}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

interface GlyphDetailProps {
  glyph: Glyph;
}

export function GlyphDetail({ glyph }: GlyphDetailProps) {
  return (
    <div className="card-inset p-4">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 bg-surface-primary rounded-xl flex items-center justify-center shadow-sm">
          <span className="text-2xl font-bold">{glyph.letter}</span>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-[13px] text-label-secondary">{glyph.topology}</p>
          <p className="text-[13px] text-label-tertiary mt-0.5">
            {glyph.physicalProperty}
          </p>
          <div className="flex items-center gap-3 mt-2 text-[12px] font-mono">
            <span className="text-[#007AFF]">S {glyph.structure.toFixed(2)}</span>
            <span className="text-[#FF9500]">F {glyph.force.toFixed(2)}</span>
            <span className="text-[#34C759]">Fl {glyph.flow.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
