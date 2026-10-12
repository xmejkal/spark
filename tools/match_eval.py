#!/usr/bin/env python3
"""
How well each matcher finds the part a need asks for (P211): `rank` over an invented drawer, and per matcher the cases at
rank 1, the cases in the shown list, the misses, and the precision cases it loses.

    tools/match_eval.py --cases tests/matching/cases.json --drawer tests/matching/drawer
    tools/match_eval.py --cases FILE --drawer DIR --matcher same-words --matcher word-overlap --json

A case is {"does", "what", "expect": key}, the part the need must find, or a precision case {"does", "what",
"not_first": key}, a part that must not come first. The shown list is `--match`'s (`matching.shown`). `--match` sorts owned
first and nearest first before it cuts. The invented drawer is all owned and in one layer, so here the matcher's order is
that order. A developer's tool, not the product: it lives in tools/ and reaches the product's modules by path.
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import matching  # noqa: E402
from outcomes import EXIT_FOR, envelope  # noqa: E402


def drawer_offers(folder):
    """The offers of an invented drawer: each `<key>.json` in `folder` as a drawer entry with no record, in key order."""
    return [matching.Offer.from_entry(path.stem, json.loads(path.read_text(encoding="utf-8")))
            for path in sorted(Path(folder).glob("*.json"))]


def _said(case):
    return "%s %s -> %s" % (case["does"], case["what"], case.get("expect") or "not " + case["not_first"])


def evaluate(matcher, cases, offers):
    """One matcher over the cases: how many at rank 1 and shown, the misses, and the precision cases it loses."""
    result = {"matcher": matcher.name, "cases": 0, "rank_1": 0, "shown": 0, "misses": [], "precision": 0, "precision_lost": []}
    for case in cases:
        fits = matcher.rank(case, offers)
        first = fits[0].offer.key if fits else None
        if "not_first" in case:
            result["precision"] += 1
            result["precision_lost"] += [_said(case)] if first == case["not_first"] else []
            continue
        shown = [fit.offer.key for rank, fit in enumerate(fits) if matching.shown(rank, fit.exact, fit.score)]
        result["cases"] += 1
        result["rank_1"] += first == case["expect"]
        result["shown"] += case["expect"] in shown
        result["misses"] += [] if case["expect"] in shown else [_said(case)]
    return result


def _lines(results):
    lines = []
    for one in results:
        lines.append("%-14s rank 1: %d/%d   shown: %d/%d   precision lost: %d/%d" % (
            one["matcher"], one["rank_1"], one["cases"], one["shown"], one["cases"], len(one["precision_lost"]), one["precision"]))
        lines += ["  missed: " + said for said in one["misses"]] + ["  lost: " + said for said in one["precision_lost"]]
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--cases", required=True, help="a JSON list of cases")
    parser.add_argument("--drawer", required=True, help="a folder of drawer entries, one <key>.json each")
    parser.add_argument("--matcher", action="append", help="a matcher's name; again for more (default: every one that serves --match)")
    parser.add_argument("--json", action="store_true", help="answer in one JSON object, for an agent")
    args = parser.parse_args(argv)
    names = args.matcher or sorted(name for name, cls in matching.MATCHERS.items() if "match" in cls.serves)
    try:
        matchers = [matching.matcher(name, "match") for name in names]  # the core refuses a name, as --match does
        cases, offers = json.loads(Path(args.cases).read_text(encoding="utf-8")), drawer_offers(args.drawer)
    except (OSError, ValueError) as wrong:  # UnknownMatcher and a JSON error are ValueErrors
        said = envelope("match_eval", "evaluate", unchecked=[{"sentence": str(wrong), "fix": None}])
        print(json.dumps(said) if args.json else "could-not-run: %s" % wrong)
        return EXIT_FOR[said["status"]]
    results = [evaluate(one, cases, offers) for one in matchers]
    said = envelope("match_eval", "evaluate", data={"matchers": results})
    print(json.dumps(said) if args.json else "\n".join(_lines(results)))
    return EXIT_FOR[said["status"]]


if __name__ == "__main__":
    sys.exit(main())
