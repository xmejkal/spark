#!/usr/bin/env python3
"""
What one run cost, read from its transcript (P97; docs/2026-10-04-store-design.md §6.7):

    cost.py <transcript.jsonl>      what one run cost — a research agent's, for instance

The library is `spark/sourcing/run_cost.py` (W6-S3a, P720): the steps of a project, their windows, and what each cost.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.core.outcomes import EXIT_OK, EXIT_COULD_NOT_RUN  # noqa: E402
from spark.sourcing.run_cost import _moment, _read, count  # noqa: E402


def main(argv=None):
    given = sys.argv[1:] if argv is None else list(argv)
    if len(given) != 1 or not Path(given[0]).is_file():
        print("usage: cost.py <transcript.jsonl> — what one run cost, from its transcript", file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    try:
        entries, unreadable = _read([Path(given[0])])
    except OSError as cannot:
        print("cost.py: %s" % cannot, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    stamps = sorted(moment for moment in map(_moment, entries) if moment)
    if not stamps:
        print("cost.py: %s holds no time cost.py can read, so what the run cost is not known" % Path(given[0]).name, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    counted = count(entries)
    counted["minutes"] = round((stamps[-1] - stamps[0]).total_seconds() / 60)
    for key in ("requests", "by_tool", "runs", "documents", "tokens", "minutes"):
        print("%-9s %s" % (key, counted[key]))
    if unreadable:
        print("%-9s %s" % ("unreadable_lines", unreadable))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
