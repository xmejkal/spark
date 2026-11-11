"""
The pick's helpers (W6-S3b, P721; P726): what a pick writes beyond the drawer (`_what_a_pick_wrote`) and the line a project
file gets when it starts naming drawer entries (`_names_your_entries`, shared with `write_requirements`). `--pick` reads a
JSON payload, so it stays in `parts.py` until its own PR (P721 row 6). The six goal handlers that lived here are design
Operations on `run_cli` since P726: `find_offers`, `list_needs`, `match_needs`, `show_offer`, `write_requirements`,
`tally_cost`; `audit` went to `audit_records` with P707.
"""

from spark.records import store


def _what_a_pick_wrote(name, listed, history, events, new_keys, dry_run):
    """
    What a pick writes beyond the drawer, said in its answer (C-17; the PO, 2026-10-08): the project put on the person's list,
    the `reused` lines its history gains, each reason noted — or already noted, and not changed, since the history keeps a
    need's first reason for a part — and a drawer entry's key that the project's own needs.json names from now on, said once.
    """
    seen, new = list(history), []
    for event in events:
        if not store.recorded(event, seen):
            new.append(event)
            seen.append(event)
    reused = sum(1 for event in new if event["event"] == "reused")
    lines = [] if listed else ["  %s %s on your projects" % ("would list" if dry_run else "listed", name)]
    lines += ["  %s to your history: %d reused" % ("would write" if dry_run else "wrote", reused)] if reused else []
    for event in (event for event in events if event["event"] == "passed_over"):
        passed = "%s (%s)" % (next(event[kind] for kind in ("part", "board", "entry") if kind in event), event["need"])
        lines.append("  %s why you passed over %s" % ("would note" if dry_run else "noted", passed) if event in new else
                     "  already noted, not changed: why you passed over %s — your history keeps the first reason" % passed)
    return lines + _names_your_entries("needs.json", new_keys, dry_run)


def _names_your_entries(file_name, new_keys, dry_run):
    """
    What a write says once when a project file starts naming drawer entries by their keys — each a key made from the person's
    label (C-17; F16): needs.json for --pick, requirements.json for --requirements, worded alike. Nothing when no key is new.
    """
    return ["  %s %s your drawer entr%s %s — a key made from your label, in the project's own file" % (file_name, "would name" if dry_run else
        "names", "y" if len(new_keys) == 1 else "ies", ", ".join(sorted(new_keys)))] if new_keys else []
