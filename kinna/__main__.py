"""CLI entry point for the Kinna kinematic linguistics engine.

Usage:
    python -m kinna assemble WORD [WORD ...]
    python -m kinna compare WORD_A WORD_B
    python -m kinna regime "query text"
    python -m kinna build INTENT_NAME
    python -m kinna audit
    python -m kinna crawl [--limit N]
"""

from __future__ import annotations

import argparse
import sys


def cmd_assemble(args: argparse.Namespace) -> None:
    from .assembler import assemble_word

    for word in args.words:
        wv = assemble_word(word)
        print(wv)


def cmd_compare(args: argparse.Namespace) -> None:
    from .di_calculator import compare_words

    result = compare_words(args.word_a, args.word_b)
    print(result)


def cmd_regime(args: argparse.Namespace) -> None:
    from .regime_locker import detect_regime, detect_polymorphic_conflict

    lock = detect_regime(args.query)
    print(f"Regime:     {lock.regime.value}")
    print(f"Confidence: {lock.confidence:.2f}")
    print(f"Keywords:   {', '.join(lock.matched_keywords) or '(none)'}")

    # Check for polymorphic words
    for word in args.query.split():
        conflicts = detect_polymorphic_conflict(word, args.query)
        if conflicts:
            regimes = ", ".join(r.value for r in conflicts)
            print(f"  Polymorphic: '{word}' → [{regimes}]")


def cmd_build(args: argparse.Namespace) -> None:
    from .sentence_builder import INTENT_TEMPLATES, build_sentence

    if args.intent == "list":
        for name, intent in INTENT_TEMPLATES.items():
            print(f"  {name:<20} {intent.description}")
        return

    plan = build_sentence(args.intent)
    print(f"Intent:   {plan.intent}")
    print(f"Sentence: {plan.render()}")
    print(f"Noun DI:  {plan.noun_di:.4f}")
    print(f"Verb DI:  {plan.verb_di:.4f}")


def cmd_audit(args: argparse.Namespace) -> None:
    from .audit_suite import run_and_print

    run_and_print()


def cmd_crawl(args: argparse.Namespace) -> None:
    from .kinematic_crawler import crawl_wordnet

    limit = args.limit if args.limit > 0 else None
    inserted = crawl_wordnet(limit=limit, verbose=True)
    print(f"Crawl complete: {inserted} rows inserted.")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="kinna",
        description="Kinematic Linguistics Engine (KL v1.4)",
    )
    sub = parser.add_subparsers(dest="command")

    # assemble
    p_asm = sub.add_parser("assemble", help="Assemble word vectors")
    p_asm.add_argument("words", nargs="+", help="Words to assemble")

    # compare
    p_cmp = sub.add_parser("compare", help="Compare two words (DI)")
    p_cmp.add_argument("word_a", help="First word")
    p_cmp.add_argument("word_b", help="Second word")

    # regime
    p_reg = sub.add_parser("regime", help="Detect regime for a query")
    p_reg.add_argument("query", help="Query text")

    # build
    p_bld = sub.add_parser("build", help="Build a sentence from intent")
    p_bld.add_argument("intent", help="Intent name (or 'list')")

    # audit
    sub.add_parser("audit", help="Run KL-100 benchmark")

    # crawl
    p_crw = sub.add_parser("crawl", help="Crawl WordNet into kinematic.db")
    p_crw.add_argument("--limit", type=int, default=0, help="Limit synsets")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "assemble": cmd_assemble,
        "compare": cmd_compare,
        "regime": cmd_regime,
        "build": cmd_build,
        "audit": cmd_audit,
        "crawl": cmd_crawl,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
