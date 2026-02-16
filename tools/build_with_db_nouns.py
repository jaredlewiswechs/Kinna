from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import sqlite3
from kinna.sentence_builder import build_sentence

con = sqlite3.connect('kinematic.db')
rows = [r[0] for r in con.execute("SELECT DISTINCT word FROM words WHERE (regime_tags LIKE '%STRUCTURAL_REGIME%' OR regime_tags LIKE '%HIGH_STRUCTURE%') AND synset_id LIKE '%.n.%' LIMIT 500").fetchall()]
con.close()
print('candidates', len(rows))
if rows:
    s = build_sentence('MOVE_UP', nouns=rows)
    print(s.render(), s.noun_di, s.verb_di)
else:
    print('no rows')
