"""Regime Locker — Phase 0 Intent Lock (Semantic Resolver).

Implements Section 6.1 of KL v1.4: detects query shape and establishes
the physical regime before geometric verification begins.

The regime locker uses keyword matching to determine which physics
apply to a given input context.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, FrozenSet, List, Optional, Set


class Regime(Enum):
    """Physical regimes supported by the kinematic compiler."""

    FLUID_DYNAMICS = "FLUID_DYNAMICS"
    STRUCTURAL_ENGINEERING = "STRUCTURAL_ENGINEERING"
    THERMAL = "THERMAL"
    ELECTRICAL = "ELECTRICAL"
    MEDICINE = "MEDICINE"
    AVIATION = "AVIATION"
    COMPOSITION = "COMPOSITION"
    GENERAL = "GENERAL"


@dataclass(frozen=True, slots=True)
class RegimeLock:
    """Result of regime detection."""

    regime: Regime
    confidence: float  # 0.0 to 1.0
    matched_keywords: tuple[str, ...]
    query: str


# Keyword → regime mapping (Section 6.1, 6.3)
REGIME_KEYWORDS: Dict[Regime, FrozenSet[str]] = {
    Regime.FLUID_DYNAMICS: frozenset({
        "water", "flow", "pipe", "fluid", "liquid", "stream", "current",
        "wave", "tide", "ocean", "river", "drain", "pump", "valve",
        "pressure", "turbulence", "laminar", "viscous", "hydraulic",
        "wind", "air", "draft", "ventilation",
    }),
    Regime.STRUCTURAL_ENGINEERING: frozenset({
        "beam", "load", "build", "structure", "bridge", "column",
        "foundation", "steel", "concrete", "frame", "truss", "support",
        "wall", "roof", "floor", "capital", "city", "tower", "arch",
        "stress", "strain", "shear", "tension", "compression",
    }),
    Regime.THERMAL: frozenset({
        "heat", "temperature", "thermal", "cold", "hot", "warm",
        "freeze", "melt", "boil", "burn", "fire", "flame", "cool",
        "insulate", "conduction", "convection", "radiation",
    }),
    Regime.ELECTRICAL: frozenset({
        "electric", "voltage", "current", "circuit", "wire", "charge",
        "battery", "power", "resistance", "capacitor", "inductor",
        "signal", "frequency", "amp", "watt", "ohm",
    }),
    Regime.MEDICINE: frozenset({
        "patient", "treatment", "diagnosis", "symptom", "disease",
        "drug", "medicine", "therapy", "surgery", "doctor", "hospital",
        "clinical", "dose", "prescription", "health", "medical",
        "organ", "tissue", "blood", "heart",
    }),
    Regime.AVIATION: frozenset({
        "aircraft", "flight", "pilot", "wing", "trim", "altitude",
        "runway", "cockpit", "throttle", "rudder", "aileron",
        "takeoff", "landing", "avionics", "mcas", "boeing", "airbus",
        "pitch", "yaw", "roll", "stall",
    }),
    Regime.COMPOSITION: frozenset({
        "write", "writing", "draft", "document", "text", "essay",
        "paragraph", "sentence", "word", "edit", "revise", "author",
        "publish", "manuscript", "chapter", "novel", "story", "poem",
    }),
}


def detect_regime(query: str) -> RegimeLock:
    """Detect the physical regime for a query string.

    Scans the query for regime keywords and returns the best match.
    If no specific regime is detected, returns GENERAL.
    """
    query_lower = query.lower()
    query_words = set(query_lower.split())

    best_regime = Regime.GENERAL
    best_score = 0.0
    best_matches: List[str] = []

    for regime, keywords in REGIME_KEYWORDS.items():
        matches = set(keywords & query_words)
        # Also check for substring matches for compound words
        for kw in keywords:
            if len(kw) > 3 and kw in query_lower and kw not in matches:
                matches.add(kw)

        if len(matches) > len(best_matches):
            best_matches = sorted(matches)
            best_regime = regime
            best_score = min(len(matches) / 3.0, 1.0)

    return RegimeLock(
        regime=best_regime,
        confidence=best_score,
        matched_keywords=tuple(best_matches),
        query=query,
    )


def detect_polymorphic_conflict(
    word: str,
    query: str,
) -> Optional[List[Regime]]:
    """Check if *word* appears in multiple regime keyword sets.

    Returns a list of conflicting regimes if ambiguity is detected,
    or None if the word is unambiguous.  (Section 6.4)
    """
    word_lower = word.lower()
    found_in: List[Regime] = []

    for regime, keywords in REGIME_KEYWORDS.items():
        if word_lower in keywords:
            found_in.append(regime)

    if len(found_in) > 1:
        return found_in
    return None


# Negation / geometric-flipper utilities ---------------------------------

NEGATION_PREFIXES: FrozenSet[str] = frozenset({"un", "non"})
"""Prefixes treated as potential geometric inverters in safety regimes.

These are intentionally conservative — only common negation prefixes are
included by default. The detection logic uses an anchor-based match so
that related morphological forms (e.g. ``STABLE`` / ``STABILITY``)
are still caught when appropriate.
"""

SAFETY_CRITICAL_REGIMES: FrozenSet[Regime] = frozenset({
    Regime.STRUCTURAL_ENGINEERING,
    Regime.AVIATION,
    Regime.MEDICINE,
})


def _shares_anchor(a: str, b: str, min_anchor: int = 4) -> bool:
    """Return True when `a` and `b` share a short anchor substring.

    This is a cheap, conservative heuristic to associate morphological
    siblings ("stable" / "stability").
    """
    if not a or not b:
        return False
    a_low = a.lower()
    b_low = b.lower()
    # direct containment is the strongest signal
    if a_low in b_low or b_low in a_low:
        return True
    # sliding-window anchor check
    anchor_len = min_anchor
    if len(a_low) < anchor_len or len(b_low) < anchor_len:
        return False
    for i in range(len(a_low) - anchor_len + 1):
        if a_low[i : i + anchor_len] in b_low:
            return True
    return False


def strip_negation_prefix(word: str, prefixes: Optional[Set[str]] = None) -> Optional[str]:
    """If *word* starts with a known negation prefix, return the stem.

    Returns None when no known prefix is present.
    """
    if not word:
        return None
    wl = word.lower()
    prefs = prefixes or set(NEGATION_PREFIXES)
    for p in prefs:
        if wl.startswith(p) and len(wl) > len(p) + 2:
            return wl[len(p) :]
    return None


def is_negation_pair(a: str, b: str, prefixes: Optional[Set[str]] = None) -> bool:
    """Return True if *a* and *b* are negation counterparts.

    The function is tolerant of simple morphological differences by using
    an anchor match after removing a negation prefix from either side.
    """
    if not a or not b:
        return False

    a_low = a.lower()
    b_low = b.lower()

    a_root = strip_negation_prefix(a_low, prefixes=prefixes)
    if a_root:
        if a_root == b_low or _shares_anchor(a_root, b_low):
            return True

    b_root = strip_negation_prefix(b_low, prefixes=prefixes)
    if b_root:
        if b_root == a_low or _shares_anchor(b_root, a_low):
            return True

    return False


def is_safety_critical(regime: Regime) -> bool:
    """Return True for regimes where negation should act as a flipper."""
    return regime in SAFETY_CRITICAL_REGIMES
