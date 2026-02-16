"""Kinematic Crawler — indexes WordNet vocabulary by physical properties.

Iterates through NLTK WordNet synsets, computes a Word Vector for each
lemma using the assembler, and stores results in a SQLite database.

Requires: nltk  (with wordnet corpus downloaded)
    python -m nltk.downloader wordnet
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from .assembler import assemble_word, WordVector
from .cluster_tagger import tag_regimes

# Default DB path (project root)
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "kinematic.db"

SCHEMA = """\
CREATE TABLE IF NOT EXISTS words (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    word        TEXT    NOT NULL,
    synset_id   TEXT    NOT NULL,
    definition  TEXT,
    examples    TEXT,
    vec_structure REAL NOT NULL,
    vec_force     REAL NOT NULL,
    vec_flow      REAL NOT NULL,
    density       REAL NOT NULL,
    regime_tags   TEXT,
    UNIQUE(word, synset_id)
);

CREATE INDEX IF NOT EXISTS idx_word ON words(word);
CREATE INDEX IF NOT EXISTS idx_synset ON words(synset_id);
CREATE INDEX IF NOT EXISTS idx_regime ON words(regime_tags);
"""


def init_db(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Create (or open) the kinematic database and ensure schema exists."""
    path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(str(path))
    conn.executescript(SCHEMA)
    # Ensure `examples` column exists for older DBs
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(words)")
    cols = [r[1] for r in cur.fetchall()]
    if "examples" not in cols:
        try:
            cur.execute("ALTER TABLE words ADD COLUMN examples TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            # ignore if cannot alter
            pass
    conn.commit()
    return conn


def crawl_wordnet(
    db_path: Optional[Path] = None,
    *,
    limit: Optional[int] = None,
    verbose: bool = False,
) -> int:
    """Crawl WordNet and populate the kinematic database.

    Parameters
    ----------
    db_path : optional path to the SQLite file.
    limit : if set, stop after this many synsets (useful for testing).
    verbose : print progress every 1000 synsets.

    Returns
    -------
    int : number of word-synset rows inserted.
    """
    try:
        from nltk.corpus import wordnet as wn
    except ImportError:
        raise ImportError(
            "nltk is required for crawling. Install with: pip install nltk\n"
            "Then download WordNet: python -m nltk.downloader wordnet"
        )

    conn = init_db(db_path)
    cursor = conn.cursor()
    inserted = 0

    synsets = list(wn.all_synsets())
    if limit:
        synsets = synsets[:limit]

    for i, synset in enumerate(synsets):
        definition = synset.definition()
        examples = "; ".join(synset.examples())
        synset_id = synset.name()

        for lemma in synset.lemmas():
            word = lemma.name().replace("_", " ")
            if not word.isascii():
                continue

            wv = assemble_word(word)
            tags = ",".join(tag_regimes(wv))

            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO words "
                    "(word, synset_id, definition, examples, vec_structure, vec_force, "
                    "vec_flow, density, regime_tags) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        word.upper(),
                        synset_id,
                        definition,
                        examples,
                        wv.structure,
                        wv.force,
                        wv.flow,
                        wv.density,
                        tags,
                    ),
                )
                if cursor.rowcount > 0:
                    inserted += 1
            except sqlite3.IntegrityError:
                pass

        if verbose and (i + 1) % 1000 == 0:
            print(f"  ... processed {i + 1}/{len(synsets)} synsets ({inserted} rows)")
            conn.commit()

    conn.commit()
    conn.close()
    if verbose:
        print(f"Done. Inserted {inserted} rows into {db_path or DEFAULT_DB_PATH}")
    return inserted


def query_word(word: str, db_path: Optional[Path] = None) -> list[dict]:
    """Look up a word in the kinematic database."""
    path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM words WHERE word = ? ORDER BY synset_id",
        (word.upper(),),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def query_by_vector_range(
    s_min: float = 0.0,
    s_max: float = 1.0,
    f_min: float = 0.0,
    f_max: float = 1.0,
    fl_min: float = 0.0,
    fl_max: float = 1.0,
    db_path: Optional[Path] = None,
    limit: int = 50,
) -> list[dict]:
    """Find words whose vectors fall within given ranges."""
    path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT DISTINCT word, vec_structure, vec_force, vec_flow, density, regime_tags "
        "FROM words "
        "WHERE vec_structure BETWEEN ? AND ? "
        "  AND vec_force     BETWEEN ? AND ? "
        "  AND vec_flow      BETWEEN ? AND ? "
        "ORDER BY density DESC LIMIT ?",
        (s_min, s_max, f_min, f_max, fl_min, fl_max, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
