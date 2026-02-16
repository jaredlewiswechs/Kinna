from kinna.sentence_builder import INTENT_TEMPLATES, find_best_word, BUILTIN_VERBS, BUILTIN_NOUNS
from kinna.cluster_tagger import tag_regimes
from kinna.assembler import assemble_word
intent = INTENT_TEMPLATES['MOVE_UP']
print('Top verbs:')
for w,di in find_best_word(BUILTIN_VERBS, intent.verb_target, top_n=8):
    print(w, di, tag_regimes(assemble_word(w)))
print('\nTop nouns:')
for w,di in find_best_word(BUILTIN_NOUNS, intent.noun_target, top_n=16):
    print(w, di, tag_regimes(assemble_word(w)))

# show candidates with HIGH_STRUCTURE tag
print('\nNouns with HIGH_STRUCTURE:')
for w in BUILTIN_NOUNS:
    tags = tag_regimes(assemble_word(w))
    if 'HIGH_STRUCTURE' in tags:
        print(w, tags)
