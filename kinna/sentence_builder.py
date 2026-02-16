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
from .cluster_tagger import tag_regimes
import sqlite3
from pathlib import Path
from typing import Set


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

# Curated vocab per intent to force sensible selections when provided.
CURATED_VOCAB: Dict[str, Dict[str, list[str]]] = {
    "MOVE_UP": {
        "nouns": ["ROPE", "BEAM", "BRIDGE", "TOWER", "WHEEL"],
        "verbs": ["LIFT", "RAISE", "HOIST", "ASCEND", "PULL"],
    },
    "MOVE_DOWN": {
        "nouns": ["ROPE", "BEAM", "STONE", "BLOCK", "WEIGHT"],
        "verbs": ["DROP", "LOWER", "DESCEND", "DROP", "FALL"],
    },
    "FLOW_THROUGH": {
        "nouns": ["PIPE", "VALVE", "WATER", "GLASS", "FRAME"],
        "verbs": ["FLOW", "DRAIN", "POUR", "STREAM", "PASS"],
    },
    "IMPACT_STOP": {
        "nouns": ["ROPE", "BEAM", "WALL", "BRIDGE", "BLOCK"],
        "verbs": ["STOP", "CRASH", "BREAK", "HALT", "SLAM"],
    },
    "STABLE_REST": {
        "nouns": ["BEAM", "BRIDGE", "STONE", "BLOCK", "MASS"],
        "verbs": ["REST", "STAND", "SETTLE", "HOLD", "REMAIN"],
    },
    "ACTIVE_TRANSFER": {
        "nouns": ["WHEEL", "PIPE", "ROPE", "GATE", "VALVE"],
        "verbs": ["SEND", "TRANSFER", "MOVE", "PASS", "SHIFT"],
    },
}

# Manual noun -> compatible verbs map as a fallback compatibility filter.
COMPATIBILITY_MAP: Dict[str, Set[str]] = {
    "ROPE": {"LIFT", "TUG", "PULL", "RAISE", "HOIST", "TIE", "DROP"},
    "BEAM": {"SUPPORT", "CARRY", "BEND", "BREAK", "LOAD", "HOLD"},
    "BRIDGE": {"SPAN", "SUPPORT", "CARRY", "CROSS", "HOLD"},
    "WATER": {"FLOW", "POUR", "DRAIN", "STREAM", "PASS"},
    "PIPE": {"FLOW", "DRAIN", "POUR", "PASS", "LEAK"},
    "GLASS": {"BREAK", "SHATTER", "POUR", "REFLECT", "SWIM"},
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

        def _conjugate_3sg(v: str) -> str:
            u = v.lower()
            if u.endswith(('s', 'sh', 'ch', 'x', 'z')):
                return u + 'es'
            if len(u) > 1 and u.endswith('y') and u[-2] not in 'aeiou':
                return u[:-1] + 'ies'
            return u + 's'

        # Simple grammar: for BASE tense, render third-person singular form
        if self.tense == Tense.BASE:
            verb_render = _conjugate_3sg(verb_form)
        elif self.tense == Tense.FUTURE:
            verb_render = 'will ' + verb_form.lower()
        else:
            verb_render = verb_form.lower()

        parts = []
        if self.article:
            parts.append(self.article)
        parts.append(self.noun.lower())
        parts.append(verb_render)

        # Capitalize first word, period at end
        sentence = " ".join(parts)
        # Capitalize first character, leave proper casing for verbs/articles as set
        return sentence[0].upper() + sentence[1:] + "."

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

    # Try to choose noun/verb pairs that share regime tags for semantic coherence.
    # Collect top candidates and prefer pairs with overlapping tags.
    top_k = 8
    verb_candidates = find_best_word(verb_pool, intent.verb_target, top_n=top_k)
    noun_candidates = find_best_word(noun_pool, intent.noun_target, top_n=top_k)

    best_pair = None
    best_score = float('inf')
    for v_word, v_di in verb_candidates:
        v_tags = set(tag_regimes(assemble_word(v_word)))
        for n_word, n_di in noun_candidates:
            n_tags = set(tag_regimes(assemble_word(n_word)))
            if v_tags & n_tags:
                score = v_di + n_di
                if score < best_score:
                    best_score = score
                    best_pair = (v_word, v_di, n_word, n_di)

    if best_pair:
        best_verb = (best_pair[0], best_pair[1])
        best_noun = (best_pair[2], best_pair[3])
    else:
        # If no shared-tag pair found, try targeted tag filtering based on intent
        req_noun_tag = None
        req_verb_tag = None
        if intent.noun_target[0] > 0.65:
            req_noun_tag = "HIGH_STRUCTURE"
        if intent.noun_target[2] > 0.65:
            req_noun_tag = "HIGH_FLOW"
        if intent.verb_target[1] > 0.60:
            req_verb_tag = "HIGH_FORCE"

        filtered_pairs = []
        for v_word, v_di in verb_candidates:
            v_tags = set(tag_regimes(assemble_word(v_word)))
            if req_verb_tag and req_verb_tag not in v_tags:
                continue
            for n_word, n_di in noun_candidates:
                n_tags = set(tag_regimes(assemble_word(n_word)))
                if req_noun_tag and req_noun_tag not in n_tags:
                    continue
                filtered_pairs.append((v_word, v_di, n_word, n_di))

        if filtered_pairs:
            # pick best by summed DI
            best = min(filtered_pairs, key=lambda p: p[1] + p[3])
            best_verb = (best[0], best[1])
            best_noun = (best[2], best[3])
        else:
            best_verb = find_best_word(verb_pool, intent.verb_target, top_n=1)[0]
            best_noun = find_best_word(noun_pool, intent.noun_target, top_n=1)[0]

    # Use WordNet DB to prefer verbs that co-occur with the chosen noun
    def _compatible_verbs_from_db(chosen_noun: str, verbs_list: List[str]) -> List[str]:
        db_path = Path(__file__).resolve().parent.parent / "kinematic.db"
        if not db_path.exists():
            return []
        try:
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute(
                "SELECT definition, examples FROM words WHERE word = ? AND synset_id LIKE '%.n.%'",
                (chosen_noun.upper(),),
            )
            rows = cur.fetchall()
            defs = " ".join(((r[0] or "") + " " + (r[1] or "")) for r in rows).lower()
            conn.close()
        except Exception:
            return []

        if not defs:
            return []

        # match verbs appearing in definitions/examples OR lemma match in DB examples
        compatible = []
        for v in verbs_list:
            lv = v.lower()
            if lv in defs:
                compatible.append(v)
                continue
            # also check if verb lemma appears as a standalone word in examples
            if any(f" {lv} " in (r[1] or "").lower() for r in rows):
                compatible.append(v)
        # dedupe
        compatible = list(dict.fromkeys(compatible))
        return compatible

    # If the noun is from DB, try to find compatible verbs and prefer them
    try:
        noun_word = best_noun[0]
        compat = _compatible_verbs_from_db(noun_word, verb_pool)
        if compat:
            # choose the compatible verb with lowest DI
            scored = [(w, distortion_index(assemble_word(w).as_tuple(), intent.verb_target)) for w in compat]
            scored.sort(key=lambda x: x[1])
            chosen_v = scored[0][0]
            # update best_verb if different
            if chosen_v != best_verb[0]:
                best_verb = (chosen_v, scored[0][1])
    except Exception:
        pass

    # CURATED VOCAB: if the intent has a curated vocabulary, prefer it
    curated = CURATED_VOCAB.get(intent_name)
    if curated:
        try:
            noun_pool_cur = [n.upper() for n in curated.get("nouns", [])]
            verb_pool_cur = [v.upper() for v in curated.get("verbs", [])]
            best_verb = find_best_word(verb_pool_cur, intent.verb_target, top_n=1)[0]
            best_noun = find_best_word(noun_pool_cur, intent.noun_target, top_n=1)[0]
        except Exception:
            pass

    # Manual compatibility fallback: prefer verbs from COMPATIBILITY_MAP for the chosen noun
    try:
        noun_word = best_noun[0].upper()
        compat_manual = COMPATIBILITY_MAP.get(noun_word, set())
        if compat_manual:
            candidates = [v for v in verb_pool if v.upper() in compat_manual]
            if candidates:
                # choose best DI among those
                scored = [(w, distortion_index(assemble_word(w).as_tuple(), intent.verb_target)) for w in candidates]
                scored.sort(key=lambda x: x[1])
                best_verb = (scored[0][0], scored[0][1])
    except Exception:
        pass

    article = "The" if use_article else ""

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
