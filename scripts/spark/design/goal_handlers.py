"""
The handlers of a project's goal (W6-S3b, P721): what exists for a need (`_op_need`), a project's needs matched against
the store (`_op_needs`, `_op_match`, `_op_offer`), the picks as its requirements (`_op_requirements`), the cost line
(`_op_tally`). One `_op_<flag>` per operation of `parts.py`, each taking the parsed arguments and the project and
answering an `Answer`. Moved whole from `parts.py`, whose `main` dispatches to them; `--needs-set` and `--pick` read a
JSON payload, so they stay in the CLI (P721 row 6). `audit` went to `audit_records` as an Operation on `run_cli` (P707);
the other handlers follow with P726. It imports the records and sourcing areas and `needs` and `footprint_emitter`
beside it, never `parts.py`.
"""

import json
from pathlib import Path

from spark.core.text_guards import printable
from spark.records import store
from spark.records.record_kind import Answer, _cannot, _problem
from spark.sourcing import datasheets, drawer, matching, run_cost
from spark.sourcing.datasheets import NEED_MATCHER
from spark.sourcing.part_facts import _row, shelve
from spark.sourcing.part_handlers import sellers, vendor_order, _write_lines
from spark.design import board_components
from spark.design import footprint_emitter, needs
from spark.design import need_requirements


#: `--need`'s closing lines (P743): the fits the cutoff dropped, and nothing found.
NEED_MORE = "  and %d more with fewer of the words: add a word, or --matcher name-contains for the names alone"
NEED_NOTHING = ("  nothing in the drawer, the boards or the part records matches %r.\n"
                "  Research it: /spark:research \"%s\"  — vendors in order: %s; sellers: %s")


def _op_need(args, project):
    try:
        chosen = matching.matcher(args.matcher or NEED_MATCHER, "need")
    except matching.UnknownMatcherError as wrong:
        return Answer(unchecked=[_cannot(str(wrong))])
    rows, drafts, more = datasheets.need(args.need, project, chosen)
    found = [row for row in rows if row["in"] != "catalog"]
    known = [row for row in rows if row["in"] == "catalog"]
    data = {"need": args.need, "vendor_order": list(vendor_order(project)), "found": found, "drafts": drafts, "catalog": known,
            "more": more, "matcher": chosen.name}
    lines = [_need_line(row) for row in found]
    lines += [_row(part_id, "(draft)", "does not yet meet the contract — being filled in") for part_id in drafts]
    lines += [_need_line(row) + "  [catalog: researched before; `--promote %s --project .` builds with it]" % row["id"] for row in known]
    lines += [NEED_MORE % more] if more else []
    if not lines:
        lines = [NEED_NOTHING % (" ".join(args.need), " ".join(args.need), ", ".join(vendor_order(project)),
                                 ", ".join(sellers(project)) or "none named in the brief")]
    return Answer(data, lines)



def _need_line(row):
    """One text row of `--need` (P743): `owned N` first when the drawer holds it, the id or the entry key, the kind (`drawer entry`
    for an entry, `board` for a board with no kind), the name, the layer when it is not the library, the first reason."""
    owned = "owned %s" % row["owned"] if row["owned"] != 0 else ""
    kind = "drawer entry" if row["is"] == "entry" else row["kind"] or row["is"]
    where = "" if row["in"] == "library" else "in %s" % row["in"]
    why = "[%s]" % row["why"][0] if row["why"] else ""
    return "  %-9s %-28s %-14s %s" % (owned, row["id"] or row["entry"], kind, "  ".join(filter(None, [row["name"] or "", where, why])))


def _op_needs(args, project):
    listed = needs.read(args.needs)
    return Answer({"needs": listed}, ["  %-10s %s / %s%s%s" % (n["id"], n.get("does"), n.get("what"),
                                                               "  (%s)" % n["condition"] if n.get("condition") else "",
                                                               "  [%s]" % n["mark"] if n.get("mark") else "") for n in listed]
                  or ["  no needs yet — /spark:idea writes them"])


def _op_match(args, project):
    try:
        chosen = matching.matcher(args.matcher or needs.MATCHER, "match")
    except matching.UnknownMatcherError as wrong:
        return Answer(unchecked=[_cannot(str(wrong))])
    matched, problems = needs.match(args.match, chosen)
    if not matched and not problems:
        return Answer(unchecked=[_cannot("%s has no needs yet — /spark:idea writes them" % args.match)])
    for need in matched:
        kept = [c for rank, c in enumerate(need["candidates"]) if matching.shown(rank, c["what_matches"], c["score"])]
        need["more"], need["candidates"] = len(need["candidates"]) - len(kept), kept
    lines = []
    for need in matched:
        lines.append("  %s — %s / %s%s%s" % (need["need"], need["does"], need["what"], "  (%s)" % need["condition"] if need["condition"] else "",
                                            "  [%s]" % need["mark"] if need["mark"] else ""))
        for c in need["candidates"]:
            lines.append("      %-10s %-46s %s" % ("owned %s" % c["owned"] if c["owned"] else "", "%s (%s)" % (c["id"] or c["entry"], c["in"]),
                                                  "  ".join(filter(None, [", ".join(c["what"]) + ("" if c["what_matches"] else " [other words]"),
                                                                          ("free %s%s" % (c["free"], ", held by " + ", ".join(map(printable, c["held_by"])) if c["held_by"] else "")) if c["owned"] else "",
                                                                          "owes " + ", ".join(c["owes"]) if c["owes"] else "",
                                                                          c.get("stop_line") or ""])))
                         + ("  maybe owned — check the drawer" if c["unsure"] else "") + ("  BROKEN" if c["broken"] else ""))
            lines += ["          " + c["about"]] if c["about"] else []
            lines += ["          " + sentence for sentence in c["limits"]]  # P397: the JSON keeps them as data
            del c["about"]  # the text shows it; the JSON gains only `score` and `why`
            c.pop("stop_line", None)  # likewise: the JSON has `stops_why`, the list
        hidden = "none with the need's words" if chosen.name == needs.MATCHER else "each scoring under %s" % matching.MIN_SHOWN
        lines += ["      … %d more, %s" % (need["more"], hidden)] if need["more"] else []
        lines += ["      nothing in the store does this — a gap"] if not need["candidates"] else []
    lines += ["  %s: %s" % (p["subject"], p["sentence"]) for p in problems]
    shown, truncated = store.page_with_store(matched, args.start, "match", ["--match", args.match] + (["--matcher", args.matcher] if args.matcher else []))
    return Answer({"needs": shown}, lines, problems=problems, truncated=truncated)


def _op_offer(args, project):
    """`--offer KEY`: the whole text of one offer, for a chooser to read (P211) — or a problem when nothing live has that key."""
    found = needs.offer(args.offer, project)
    if found is None:
        return Answer(problems=[_problem(args.offer, "no record and no live drawer entry called %r — `--need` and "
                                                     "`--drawer` list what exists" % args.offer)])
    return Answer({"offer": found.as_dict()}, found.describe().splitlines())  # the text once: in the lines, not again in data


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


def _gap_lines(problems, no_supply, no_receiver, no_driver):
    """What `--requirements` says of a rail with no supply, a net with no receiver or no driver: none on a refusal."""
    said = []
    said += ["  rail %s has no supply — pick a power inlet or a supply (%s draw%s from it)"
             % (gap["rail"], ", ".join(gap["drawn_by"]), "s" if len(gap["drawn_by"]) == 1 else "") for gap in ([] if problems else no_supply)]
    said += ["  net %s is driven by %s and nothing listed receives it — pick what it drives (a speaker terminal, a motor, a connector)"
             % (gap["net"], gap["driven_by"]) for gap in ([] if problems else no_receiver)]
    said += ["  net %s is one side of a driven pair and nothing listed drives it — pick what drives the pair (the amplifier this "
             "terminal hangs off), never a supply (%s %s on it)" % (gap["net"], ", ".join(gap["received_by"]),
                                                                    "is" if len(gap["received_by"]) == 1 else "are")
             for gap in ([] if problems else no_driver)]
    return said


def _op_requirements(args, project):
    content, shelving, unplaced, kept, board_was, problems, placeholder, unserved, no_supply, no_receiver, no_driver = need_requirements.requirements(
        args.requirements)
    path, changed = Path(args.requirements) / need_requirements.REQUIREMENTS, False
    # F16: the drawer keys the file names before this write — need_requirements.requirements has read it as JSON already
    held = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    named = need_requirements.unserved_keys(held)
    if not problems and not args.dry_run:
        for record, source in shelving:
            shelve(record, source)
        changed = store.write_file(path, json.dumps(content, indent=2, ensure_ascii=False) + "\n")
    said = [] if problems else ["  %s %s: board %s; parts %s" % (
        "would write" if args.dry_run else "wrote" if changed else "unchanged", path, content["board"],
        ", ".join(need_requirements.entry_label(entry) for entry in content["parts"]) or "none")]
    said += ["  board: %s → %s" % (json.dumps(board_was), json.dumps(content["board"]))] if board_was not in (None, content["board"]) and not problems else []
    # --- MVP --- P387: board_only is said both ways, never silently written or dropped
    said += ["  board only: nothing to build but the board; the build skips the parts, schematic and footprint"
             ] if content.get(need_requirements.BOARD_ONLY) is True and not problems else []
    said += ["  board_only removed: the file lists parts"] if isinstance(held, dict) and need_requirements.BOARD_ONLY in held and content["parts"] and not problems else []
    stop = "" if problems else footprint_emitter.footprint_stop(content["board"], Path(args.requirements))
    said += ["  board %s: %s" % (content["board"], stop)] if stop else []  # F12 (C-7): said, never refused
    said += ["  onto the shelf, so every project builds with it: %s" % ", ".join(Path(r).stem for r, _ in shelving)] if shelving and not problems else []
    said += ["  placeholder outline — %s owes body_mm, so the PCB step lays it out at a placeholder %g x %g mm: a dimension drawing "
             "(fetched after the person's yes) or a measurement fills it — %s" % ((part_id,) + board_components.DEFAULT_BODY_MM + (how,))
             for part_id, how in ([] if problems else placeholder)]
    said += ["  reserved, not placed — no record: %s" % ", ".join(unplaced)] if unplaced and not problems else []
    said += ["  kept, not from a pick: %s" % ", ".join(need_requirements.entry_label(entry) for entry in kept)] if kept and not problems else []
    said += _gap_lines(problems, no_supply, no_receiver, no_driver)
    said += ["  not on the board: %s — %s" % (item["need"], need_requirements.NOT_ON_THE_BOARD[item["why"]].format(picks=", ".join(item["picks"])))
             for item in ([] if problems else unserved)]
    said += [] if problems else _names_your_entries(need_requirements.REQUIREMENTS, need_requirements.unserved_keys(content) - named, args.dry_run)
    return Answer({"path": str(path), "requirements": content, "shelved": [Path(r).stem for r, _ in shelving],
                   "unplaced": unplaced, "kept": kept, "board_was": board_was, "placeholder_outline": [part_id for part_id, _ in placeholder],
                   "unserved": unserved, "no_supply": no_supply, "no_driver": no_driver,
                   "no_receiver": no_receiver, "written": not problems and not args.dry_run},
                  _write_lines([], problems, args.dry_run, said), problems=problems)


def _op_tally(args, project):
    name = store.find_listed_name(args.tally)
    if name is None:
        return Answer(unchecked=[_cannot("%s is not on your list of projects, so no step of it was marked" % args.tally,
                                         "mark a step with parts.py --step <project> <step> in a Claude Code session: that puts it on the list")])
    history, entries, listed = store.events(), drawer.entries(), needs.read(args.tally)
    picks = [(need["id"], pick) for need in listed for pick in need.get("pick") or []]
    unpicked = [need["id"] for need in listed if not need.get("pick")]  # C-2: the picks are counted against the needs they serve
    reused = [event for event in history if event.get("event") == "reused" and event.get("project") == name]
    from_store = sum(1 for need_id, pick in picks if dict({"event": "reused", "project": name, "need": need_id}, **pick) in reused)
    owned = sum(1 for _, pick in picks if needs.owned(pick, entries))
    try:
        counted, unchecked = run_cost.cost([event for event in history if event.get("event") == "step"], name), []
    except run_cost.NoTranscriptError as missing:
        counted, unchecked = None, [_cannot(str(missing), "mark each step with parts.py --step <project> <step> in a Claude Code session")]
    said, unreadable = run_cost.line(len(picks), from_store, owned, counted), run_cost.unreadable_note(counted)
    built = any(event.get("event") == "built" and event.get("project") == name for event in history)
    needs_said = "%d of %d needs picked%s" % (len(listed) - len(unpicked), len(listed),
                                              " — not picked: %s" % ", ".join(unpicked) if unpicked else "")
    return Answer({"picks": len(picks), "from_store": from_store, "owned": owned, "cost": counted, "built": built, "line": said,
                   "needs": len(listed), "needs_picked": len(listed) - len(unpicked)},
                  ["  " + said, "  " + needs_said] + ["  " + glossed for glossed in run_cost.gloss(counted)]
                  + ["  " + item["sentence"] for item in unchecked] + (["  " + unreadable] if unreadable else [])
                  + ([] if built else ["  not built yet — check_spine records it when the chain runs end to end, and a board-only build records none"]),
                  unchecked=unchecked)
