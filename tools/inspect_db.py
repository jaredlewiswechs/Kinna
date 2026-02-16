#!/usr/bin/env python3
"""Quick DB inspector for `kinematic.db` (prints totals, top rows by density, and tag counts)."""
import sqlite3
import collections

DB = "kinematic.db"
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()

total = cur.execute("SELECT COUNT(*) FROM words").fetchone()[0]
distinct_words = cur.execute("SELECT COUNT(DISTINCT word) FROM words").fetchone()[0]

top = cur.execute(
    "SELECT word, synset_id, vec_structure, vec_force, vec_flow, density, regime_tags, definition "
    "FROM words ORDER BY density DESC LIMIT 12"
).fetchall()

cnt = collections.Counter()
for (rt,) in cur.execute("SELECT regime_tags FROM words"):
    tags = (rt or "").split(',')
    for t in tags:
        t = t.strip()
        if t:
            cnt[t] += 1

print(f"TOTAL_ROWS: {total}")
print(f"DISTINCT_WORDS: {distinct_words}\n")

print("TOP_ROWS_BY_DENSITY")
for r in top:
    defn = (r['definition'][:140] + '...') if r['definition'] and len(r['definition']) > 140 else (r['definition'] or '')
    print(f"{r['word']:<20} {r['synset_id']:<30} s={r['vec_structure']:.3f} f={r['vec_force']:.3f} fl={r['vec_flow']:.3f} dens={r['density']:.3f} tags={r['regime_tags']}")
    print(f"   {defn}")

print("\nTOP_REGIME_TAGS")
for tag, ct in cnt.most_common(12):
    print(f"{(tag or '(none)'):<30}{ct}")

con.close()