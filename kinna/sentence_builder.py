"""Sentence Builder — generates sentences by solving geometric equations.

Implements Section 2.3 and the Phase 4 Construction Engine of KL v1.4.
Sentences are modeled as kinematic linkages:

    - Nouns   → masses
    - Verbs   → vectors (directional force)
    - Articles → flow regulators (A = generic frame, THE = specific bridge)
    - Prepositions → vector-field constraints

The builder selects words from a vocabulary whose vectors best match
a target geometric intent.
"""

from __future__ import annotations

import math
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .assembler import WordVector, assemble_word
from .di_calculator import distortion_index
from .tense_modifier import Tense, apply_tense


# ---------------------------------------------------------------------------
# Geometric intent templates
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class GeometricIntent:
    """A target geometry that describes what the sentence should express."""

    description: str
    verb_target: Tuple[float, float, float]   # desired verb vector
    noun_target: Tuple[float, float, float]   # desired noun vector
    tense: Tense = Tense.BASE


# Predefined intent templates
INTENT_TEMPLATES: Dict[str, GeometricIntent] = {
    "MOVE_UP": GeometricIntent(
        description="Upward motion with force",
        verb_target=(0.40, 0.70, 0.50),
        noun_target=(0.70, 0.50, 0.20),
    ),
    "MOVE_DOWN": GeometricIntent(
        description="Downward / heavy motion",
        verb_target=(0.50, 0.65, 0.30),
        noun_target=(0.75, 0.60, 0.10),
    ),
    "FLOW_THROUGH": GeometricIntent(
        description="Fluid passage or transfer",
        verb_target=(0.30, 0.20, 0.80),
        noun_target=(0.40, 0.15, 0.70),
    ),
    "IMPACT_STOP": GeometricIntent(
        description="Forceful stop or collision",
        verb_target=(0.60, 0.80, 0.10),
        noun_target=(0.80, 0.55, 0.10),
    ),
    "STABLE_REST": GeometricIntent(
        description="Static equilibrium / rest",
        verb_target=(0.75, 0.20, 0.15),
        noun_target=(0.85, 0.25, 0.10),
        tense=Tense.PAST,
    ),
    "ACTIVE_TRANSFER": GeometricIntent(
        description="Active transfer or exchange",
        verb_target=(0.45, 0.45, 0.65),
        noun_target=(0.55, 0.30, 0.55),
        tense=Tense.ACTIVE,
    ),
}


# ---------------------------------------------------------------------------
# Built-in small vocabulary (used when no DB is available)
# ---------------------------------------------------------------------------

BUILTIN_VERBS = [
    "RISE", "FALL", "PUSH", "PULL", "FLOW", "STOP", "BREAK", "BUILD",
    "MOVE", "TURN", "LIFT", "DROP", "HOLD", "SEND", "TAKE", "GIVE",
    "RUN", "WALK", "FLY", "SWIM", "JUMP", "CLIMB", "SLIDE", "SPIN",
    "CRASH", "BLAST", "DRIFT", "SHIFT", "TRUST", "GUARD", "BLOCK",
    "PRESS", "SPARK", "GRIP", "FLING", "THROW", "CATCH", "REST",
    "STAND", "SIT", "STRETCH", "SHRINK", "GROW", "SPLIT", "MERGE",
    "ASCEND", "DESCEND", "SURGE", "DRAIN", "POUR", "STREAM",
]

BUILTIN_NOUNS = [
    "ROCK", "WATER", "FIRE", "WIND", "BEAM", "WALL", "BRIDGE",
    "TOWER", "MASS", "FORCE", "WAVE", "STONE", "STEEL", "GLASS",
    "LIGHT", "HEAT", "FROST", "STORM", "BOLT", "CHAIN", "ROPE",
    "WHEEL", "GATE", "VALVE", "PIPE", "FRAME", "BLOCK", "SPRING",
    "ROCKET", "SHIP", "CRAFT", "DISK", "GLOBE", "ARCH", "DOME",
    "SHAFT", "BLADE", "PRISM", "FLUX", "PULSE", "SPARK",
]


def _score_match(
    candidate_vec: Tuple[float, float, float],
    target_vec: Tuple[float, float, float],
) -> float:
    """Score how well a candidate matches a target (lower = better)."""
    return distortion_index(candidate_vec, target_vec)


def find_best_word(
    candidates: List[str],
    target: Tuple[float, float, float],
    top_n: int = 1,
) -> List[Tuple[str, float]]:
    """Find the best matching words from candidates for a target vector.

    Returns list of (word, DI_score) sorted by score ascending (best first).
    """
    scored = []
    for w in candidates:
        wv = assemble_word(w)
        di = _score_match(wv.as_tuple(), target)
        scored.append((w, di))
    scored.sort(key=lambda x: x[1])
    return scored[:top_n]


@dataclass
class SentencePlan:
    """A planned sentence with geometric justification."""

    intent: str
    article: str
    noun: str
    verb: str
    tense: Tense
    noun_di: float
    verb_di: float

    def render(self) -> str:
        """Render the sentence as a string."""
        tv = apply_tense(self.verb, self.tense)
        verb_form = tv.word

        parts = []
        if self.article:
            parts.append(self.article)
        parts.append(self.noun)
        parts.append(verb_form)

        # Capitalize first word, period at end
        sentence = " ".join(parts)
        return sentence[0].upper() + sentence[1:].lower() + "."

    def __repr__(self) -> str:
        return (
            f"SentencePlan(intent={self.intent!r}, "
            f"sentence={self.render()!r}, "
            f"noun_DI={self.noun_di:.3f}, verb_DI={self.verb_di:.3f})"
        )


def build_sentence(
    intent_name: str,
    *,
    verbs: Optional[List[str]] = None,
    nouns: Optional[List[str]] = None,
    use_article: bool = True,
) -> SentencePlan:
    """Build a sentence that matches a geometric intent.

    Parameters
    ----------
    intent_name : key into INTENT_TEMPLATES (e.g. "MOVE_UP").
    verbs : candidate verb list; defaults to BUILTIN_VERBS.
    nouns : candidate noun list; defaults to BUILTIN_NOUNS.
    use_article : whether to prepend an article ("The").

    Returns
    -------
    SentencePlan with the best-matching noun and verb.
    """
    intent = INTENT_TEMPLATES[intent_name]
    verb_pool = verbs or BUILTIN_VERBS
    noun_pool = nouns or BUILTIN_NOUNS

    best_verb = find_best_word(verb_pool, intent.verb_target, top_n=1)[0]
    best_noun = find_best_word(noun_pool, intent.noun_target, top_n=1)[0]

    article = "THE" if use_article else ""

    return SentencePlan(
        intent=intent_name,
        article=article,
        noun=best_noun[0],
        verb=best_verb[0],
        tense=intent.tense,
        noun_di=best_noun[1],
        verb_di=best_verb[1],
    )


def build_sentence_from_target(
    description: str,
    verb_target: Tuple[float, float, float],
    noun_target: Tuple[float, float, float],
    tense: Tense = Tense.BASE,
    *,
    verbs: Optional[List[str]] = None,
    nouns: Optional[List[str]] = None,
) -> SentencePlan:
    """Build a sentence from explicit target vectors."""
    verb_pool = verbs or BUILTIN_VERBS
    noun_pool = nouns or BUILTIN_NOUNS

    best_verb = find_best_word(verb_pool, verb_target, top_n=1)[0]
    best_noun = find_best_word(noun_pool, noun_target, top_n=1)[0]

    return SentencePlan(
        intent=description,
        article="THE",
        noun=best_noun[0],
        verb=best_verb[0],
        tense=tense,
        noun_di=best_noun[1],
        verb_di=best_verb[1],
    )
