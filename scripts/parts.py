#!/usr/bin/env python3
"""
What a part asks of the board it plugs into, and what is actually known about it.

    parts.py --list
    parts.py --show l9110s-module
    parts.py --validate
    parts.py --unverified <part> [part ...]   what nobody has checked yet about those parts

A part library is easy to get wrong in a way that is worse than not having one. The temptation is a schema covering
everything a part might have — and since a motor driver's facts (input thresholds, current) have nothing in common with
a rangefinder's (an I2C address, a calibration), that schema degenerates into `{"name": ..., "notes": ...}`: a directory
of documentation pretending to be configuration.

So this splits them.

**`needs` is a real schema**, because it IS uniform: every part asks its host for some pins, and each pin either needs a
capability or does not. That is exactly what `assign_pins.py` consumes, and it is the reason this file exists rather
than a folder of markdown.

**`facts` is deliberately open**, and every entry carries three things: a value, where it came from, and whether anyone
has actually checked. A fact with `verified: false` is not a defect — most parts arrive with several — but it must be
VISIBLE, because the unverified ones are what decide whether a design works. On the project this came from, the single
most consequential number in the whole build was an audio module's idle current, which nobody had measured and every
document quietly assumed.

This file is the CLI (W6-S3b, P721): the parser, the printers, `--describe`, `--needs-drop` on the core and the
handlers that read a JSON payload. The rest lives in `spark/sourcing/` (`part_facts`, `datasheets`, `part_handlers`,
`drawer`) and in `spark/design/goal_handlers.py`.
"""

import argparse
import contextlib
import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.core.outcomes import AnsweringParser, BadArgument, EXIT_OK as EXIT_OK, EXIT_PROBLEMS as EXIT_INVALID, EXIT_COULD_NOT_RUN as EXIT_COULD_NOT_RUN, EXIT_FOR, envelope  # noqa: E402, F401
from spark.core import outcomes  # noqa: E402
from spark.core.cli import run_operation  # noqa: E402
from spark.core.errors import CodedMessageError  # noqa: E402
from spark.core.events import Reporter  # noqa: E402
from spark.core.outside import build_outside_world  # noqa: E402
from spark.core.text_guards import guard_lines  # noqa: E402
from spark.records import missing_facts, provenance, store  # noqa: E402
from spark.records.record_kind import _absent, Answer, _cannot, CHAIN_FACTS, _note, _problem  # noqa: E402
from spark.sourcing import drawer, sourcing_codes  # noqa: E402
from spark.sourcing.part_handlers import _drawer_answer, _set_in_home, _write_lines  # noqa: E402
from spark.sourcing.part_records import broken_problems, function_problems, PartError  # noqa: E402
from spark.design import needs  # noqa: E402
from spark.design.goal_handlers import _what_a_pick_wrote  # noqa: E402
from spark.idea.drop_need import DropNeed  # noqa: E402
#: `main` runs each operation's handler by its name (`_op_` and the flag), so the handlers are imported by name.
from spark.sourcing.part_handlers import (  # noqa: E402, F401
    _op_catalog, _op_drawer, _op_fetch, _op_keep, _op_kept, _op_list, _op_promote, _op_read, _op_show, _op_signals,
    _op_skeleton, _op_sources, _op_step, _op_unverified, _op_validate)
from spark.design.goal_handlers import (  # noqa: E402, F401
    _op_audit, _op_match, _op_need, _op_needs, _op_offer, _op_requirements, _op_tally)


#: Every operation parts.py offers — the ONE table the argument parser and `--describe` are built from, so what an
#: agent reads about an operation cannot drift from what runs (§6.4.3). A row: the flag, its argparse keywords,
#: what it answers, its effects (`writes`, `network`, `deletes`), the keys of its `data`. An operation with an
#: effect takes --dry-run (§6.4.5).
OPERATIONS = (
    ("list", {"action": "store_true"}, "every record a project can build with, and where it comes from", (), ("parts",)),
    ("show", {"metavar": "PART"}, "one record, wherever it lives, and its CONFLICT lines: on verified facts a problem "
     "(exit 1), on unverified ones an assumption", (), ("record",)),
    ("validate", {"action": "store_true"}, "every record a project can build with, against the contract", (), ("checked",)),
    ("signals", {"nargs": "+", "metavar": "PART"}, "the signals these parts ask for, as assign_pins.py input", (), ("signals",)),
    ("unverified", {"nargs": "+", "metavar": "PART"}, "what nobody has checked about these parts, one assumption a fact",
     (), ("parts",)),
    ("need", {"nargs": "+", "metavar": "WORD"}, "what exists for a need, before researching: words matched in id, name, kind, alias; "
     "--matcher picks the matcher", (), ("need", "vendor_order", "found", "drafts", "catalog")),
    ("skeleton", {"metavar": "PART"}, "write a record to fill in, to the project's parts/", ("writes",), ("path", "record", "written")),
    ("sources", {"metavar": "PART"}, "ask every URL a record cites whether it answers", ("network",), ("part", "sources")),
    ("fetch", {"metavar": "PART"}, "download the datasheets and images a record cites, into your store", ("network", "writes"),
     ("documents", "would_fetch")),
    ("keep", {"metavar": "FILE"}, "put a file you already have into your store; answers its documents entry", ("writes",),
     ("document", "location_removed", "written")),
    ("read", {"metavar": "PDF"}, "read a datasheet page by page and stop where every --want fact is on a table row", (),
     ("facts", "pages_read")),
    ("kept", {"nargs": "+", "metavar": "WORD"}, "find a kept document by every word, with no network, and every fact resting on it",
     (), ("found",)),
    ("promote", {"metavar": "PART"}, "catalog → the project's parts/, or the project's parts/ → the plugin's library", ("writes",),
     ("path", "written")),
    ("catalog", {"action": "store_true"}, "every record research has kept, chosen or not", (), ("records", "broken")),
    ("drawer", {"action": "store_true"}, "what you own: label, count, the record it is, unsure, skip — 20 at a time", (),
     ("entries",)),
    ("drawer-set", {"metavar": "FILE"}, "set drawer entries from a JSON list in FILE (- for stdin): every write sets, never adds; with --project, an `is` may "
     "name a record in that project, such as one /spark:research just wrote; an entry may also say its about, description and tags",
     ("writes",), ("changes", "questions", "shelved")),
    ("drawer-import", {"nargs": 2, "metavar": ("SOURCE", "FILE")},
     "apply an importer's payload (FILE, or - for stdin) to the drawer: new entries, and counts by the re-import rule",
     ("writes",), ("changes", "questions", "shelved", "smaller")),
    ("function-set", {"nargs": 2, "metavar": ("PART", "FILE")},
     "set what a part does — a JSON [{does, what}] in FILE (- for stdin) — in the record's own home (--project picks the project's copy); never spark's library",
     ("writes",), ("part", "path", "was", "now", "written", "shelf_copy")),
    ("fact-set", {"nargs": 2, "metavar": ("PART", "FILE")},
     "fill what a record owes — a JSON object of the facts the chain reads, or `facts` entries {value, verified, source} by name (a bench result is verified true and its source says who, when and how; a text in it has its control characters turned into a space and is cut at 1000 characters, and a key with a control character is refused), or its about, description and tags, or a board's onboard LED or button level, `pin_roles` {onboard_led|onboard_button: {active_level: {value, verified, source}}} (a board of the project's own, merged role by role), in FILE (- for stdin) — in the record's own home (--project picks the project's copy); never spark's library",
     ("writes",), ("part", "path", "was", "now", "written", "shelf_copy")),
    ("audit", {"action": "store_true"}, "every record in every layer and every drawer link: what owes facts, what is broken",
     (), ("layers", "owed", "broken", "no_function", "dangling", "stops_at_footprint")),
    ("needs", {"metavar": "PROJECT"}, "a project's needs: what each does, its condition, its mark", (), ("needs",)),
    ("needs-set", {"nargs": 2, "metavar": ("PROJECT", "FILE")},
     "set a project's needs from a JSON list in FILE (- for stdin): every write sets, never adds", ("writes",),
     ("changes", "written")),
    ("match", {"metavar": "PROJECT"}, "each of a project's needs with the store's candidates: owned first, what each owes, "
     "each with its score and why; --matcher picks the matcher that ranks them; a board that serves a need through its own "
     "LED, button or display has `limits`, the sentences for what a passed run does not test of it", (), ("needs",)),
    ("offer", {"metavar": "KEY"}, "what one offer says of itself, for the chooser to read: a record's id or a drawer entry's "
     "key — about, description, tags, what it does, its names, power and size. --project reads the project's own records", (),
     ("offer",)),
    ("pick", {"nargs": "+", "metavar": ("PROJECT", "NEED=ID")},
     "set what each need picks (NEED=ID: a record, or a drawer entry) and reserve what you own of it — never past what another project holds; "
     "what it notes is under `notes`: a board given a need that its own part serves says what a run does not test of the part, "
     "and the other choice",
     ("writes",), ("project", "picks", "reserved", "released", "written")),
    ("needs-drop", {"nargs": 2, "metavar": ("PROJECT", "NEED")},
     "drop a need and its pick from .spark/needs.json and release only the holds of the dropped pick (every other hold stays); --dry-run "
     "says what it would do; history stays, and requirements.json is not changed: a note says when it still lists the part",
     ("writes",), ("project", "need", "dropped", "released", "written")),
    ("requirements", {"metavar": "PROJECT"},
     "the picks as the project's requirements.json: the board, and every part pick with a record — one that owes only its outline is written with a warning, one that owes more is refused; a catalog one goes onto the shelf; what the file already holds stays; board_only when the board itself serves every need",
     ("writes",), ("path", "requirements", "shelved", "unplaced", "kept", "board_was", "placeholder_outline", "unserved", "no_supply",
                   "no_driver", "no_receiver", "written")),
    ("step", {"nargs": 2, "metavar": ("PROJECT", "STEP")},
     "a spine step of a project starts now, in this Claude Code session — the cost line counts its transcript from here",
     ("writes",), ("step", "written")),
    ("tally", {"metavar": "PROJECT"},
     "the cost line: the picks, how many came from the store (known to spark before the project: its library, your store, your projects) and how many you own, and what the project's steps cost",
     (), ("picks", "from_store", "owned", "cost", "built", "line", "needs", "needs_picked")),
    ("describe", {"action": "store_true"}, "every operation, its arguments, effects and output — this list", (),
     ("operations", "options", "exits")),
)

def _not_negative(text):
    """An argparse type: a whole number from 0 up — a listing cannot start before its first item."""
    if int(text) < 0:
        raise argparse.ArgumentTypeError("%s is below 0" % text)
    return int(text)


#: The options an operation reads, in the same columns but effects.
OPTIONS = (
    ("kind", {}, "with --skeleton: the part's kind (motor-driver, sensor, regulator, …)"),
    ("vendor", {}, "with --skeleton: who makes it"),
    ("url", {}, "with --keep: where the file came from, if anyone knows"),
    ("want", {"nargs": "+", "metavar": "FACT"}, "with --read: the facts to find, named as records name them (forward_voltage_v …)"),
    ("label", {"action": "append", "metavar": "FACT=WORD|WORD"}, "with --read: extra words a datasheet uses for a fact"),
    ("passed-over", {"metavar": "FILE"}, "with --pick: the parts passed over and why, a JSON list in FILE (- for stdin) of {need, id, why, by}"),
    ("matcher", {"metavar": "NAME"}, "with --match or --need: the matcher that ranks the offers; a name that does not fit "
     "is refused with the names that do"),
    ("project", {"type": Path}, "a project whose own parts/ beats the shipped library"),
    ("from", {"type": _not_negative, "default": 0, "dest": "start", "metavar": "N"}, "with a listing: start at item N (truncated.next says where)"),
    ("dry-run", {"action": "store_true"}, "with an operation that has an effect: say what it would do, and do nothing"),
    ("json", {"action": "store_true"}, "answer in one envelope: problems, unchecked, notes, assumptions, next "
     "(docs/guide/agents/json.md, \"parts.py's envelope\")"),
)


def _parser():
    """The argument parser, built from OPERATIONS and OPTIONS so that `--describe` cannot drift from it."""
    parser = AnsweringParser(prog="parts.py", description="What a part needs, and what is known about it.")
    what = parser.add_mutually_exclusive_group(required=True)
    for name, keywords, summary, _, _ in OPERATIONS:
        what.add_argument("--" + name, help=summary, **keywords)
    for name, keywords, summary in OPTIONS:
        parser.add_argument("--" + name, help=summary, **keywords)
    return parser


def _read_json_input(name):
    """A payload from a file, or from stdin for '-' — the way labels and names travel, never argv (§6.4.2). A refusal
    with the code `input_unreadable` when it is not readable JSON, which `main` answers as could-not-run."""
    try:
        return json.loads(sys.stdin.read() if name == "-" else Path(name).read_text())
    except (OSError, ValueError) as broken:
        raise CodedMessageError("%s is not readable JSON: %s", "stdin" if name == "-" else name, broken,
                                code=sourcing_codes.INPUT_UNREADABLE) from None


def _op_drawer_set(args, project):
    items = _read_json_input(args.drawer_set)
    return _drawer_answer(*drawer.plan_set(items, project), args.dry_run)


def _op_drawer_import(args, project):
    source, name = args.drawer_import
    payload = _read_json_input(name)
    changes, questions, problems, smaller = drawer.plan_import(source, payload)
    answer = _drawer_answer(changes, questions, problems, args.dry_run)
    if not problems and not args.dry_run:
        store.write_json("drawer-import", store.slug(source), drawer.kept_payload(payload))
    return answer._replace(data=dict(answer.data, smaller=smaller), lines=list(answer.lines) + ["  %s" % s for s in smaller])


def _op_function_set(args, project):
    part_id, name = args.function_set
    function = _read_json_input(name)
    answer = _set_in_home(part_id, project, {"function": function}, args.dry_run, lambda record, after, path:
                          function_problems(after) if function else ["a function is a non-empty list [{does, what}]"])
    return answer._replace(data=dict(answer.data, was=answer.data["was"]["function"], now=function)) if answer.data else answer


def _op_fact_set(args, project):
    """Fill a record's chain facts, write `facts` entries by name (a bench result and its source, P374), or set what it says of itself (about, description, tags)."""
    part_id, name = args.fact_set
    facts = _read_json_input(name)
    if not (isinstance(facts, dict) and facts and set(facts) <= set(CHAIN_FACTS + drawer.DESCRIBING + ("facts", "pin_roles"))):
        return Answer(problems=[_problem(part_id, "a fact write is a JSON object of facts the chain reads: %s, or `facts` entries by name; or of what a "
                                                  "record says of itself: %s" % (", ".join(CHAIN_FACTS), ", ".join(drawer.DESCRIBING)))])
    facts = {key: drawer.scrub(key, value) if key in drawer.DESCRIBING + drawer.PROVENANCE_KEYS else value for key, value in facts.items()}
    wrong = [drawer.CHECKS[key][1] for key in drawer.DESCRIBING if key in facts and not drawer.CHECKS[key][0](facts[key])] + drawer.list_provenance_key_problems(facts)
    if wrong:
        return Answer(problems=[_problem(part_id, sentence) for sentence in wrong])
    return _set_in_home(part_id, project, facts, args.dry_run, lambda record, after, path: missing_facts.board_write_problems(record, after, path, facts, project) if "pin_roles" in facts else (
        ["%s is absent — a write fills a fact, it never empties one" % key for key in facts if _absent(key, facts[key])]
        + sorted(set(provenance.list_entry_problems(facts.get("facts"), record.get("facts"))) | set(broken_problems(after, path)) - set(broken_problems(record, path)))))


def _op_needs_set(args, project):
    target, name = args.needs_set
    items = _read_json_input(name)
    after, changes, problems = needs.plan_set(target, items)
    written = not (problems or args.dry_run)
    if written and changes:
        needs.write(target, after)
    return Answer({"changes": changes, "written": written}, _write_lines(changes, problems, args.dry_run), problems=problems)


def _op_needs_drop(args, project):
    """The drop of a need, run on the core (P514): DropNeed through `run_operation`, its result as parts.py's Answer."""
    target, need = args.needs_drop
    result = run_operation(DropNeed(), {"project": Path(target), "need": need, "dry_run": args.dry_run},
                           build_outside=lambda effects: build_outside_world(effects, Reporter()))
    return Answer(result.data, result.lines, notes=result.notes or (), diagnostics=result.diagnostics,
                  problems=[_problem(found.subject, found.sentence, found.fix) for found in result.findings if found.severity == outcomes.PROBLEMS],
                  unchecked=[_cannot(found.sentence, found.fix) for found in result.findings if found.severity == outcomes.COULD_NOT_RUN])


def _op_pick(args, project):
    target, given = args.pick[0], args.pick[1:]
    pairs = [tuple(one.split("=", 1)) for one in given if "=" in one]
    if not pairs or len(pairs) != len(given):
        return Answer(unchecked=[_cannot("--pick takes the project, then NEED=ID for each pick: light=led-red-5mm",
                                         "parts.py --match <project> lists each need's candidates and their ids")])
    reasons = _read_json_input(args.passed_over) if args.passed_over else []
    history = store.events()  # read whole before the first write: one that cannot be read refuses the pick, with nothing written
    listed, keys_before = store.find_listed_name(target) is not None, needs.entry_keys(needs.read(target))
    after, changes, events, notes, problems = needs.plan_pick(target, pairs, reasons)
    if not problems and not args.dry_run:
        store.add_project(target)
        drawer.apply(changes)
        for event in events:
            store.append_event(event)
        # the project's own file last: a store that refuses leaves it as it was, and the same pick, retried, finishes the rest
        needs.write(target, after)
    asked, name = dict(pairs), store.plan_listed_name(target)
    picks = [{"need": need["id"], "pick": need.get("pick") or []} for need in after if need["id"] in asked]
    said = [] if problems else ["  %s: %s" % (one["need"], ", ".join(next(iter(pick.values())) for pick in one["pick"])) for one in picks]
    released = needs.released_holds(changes, name)
    said += [] if problems else ["  %s%s: %s — no pick of this project explains it" % (
        "would release" if args.dry_run else "released", "" if hold["now"] == 0 else " %d of %d" % (hold["was"] - hold["now"], hold["was"]),
        hold["entry"]) for hold in released]
    wrote = [] if problems else _what_a_pick_wrote(name, listed, history, events, needs.entry_keys(after) - keys_before, args.dry_run)
    return Answer({"project": name, "picks": picks,
                   "reserved": [{"entry": change["entry"], "used_in": change["now"]["used_in"]} for change in changes],
                   "released": released, "written": not problems and not args.dry_run},
                  _write_lines(changes, problems, args.dry_run, said + ["  %s" % note for note in notes] + wrote), problems=problems,
                  notes=[_note(note) for note in notes])


def _op_describe(args, project):
    operations = [{"op": name, "flag": "--" + name, "summary": summary, "effects": list(effects), "dry_run": bool(effects),
                   "arguments": {key: (list(value) if isinstance(value, tuple) else value)
                                 for key, value in keywords.items() if key in ("nargs", "metavar")},
                   "data": list(keys)} for name, keywords, summary, effects, keys in OPERATIONS]
    options = [{"flag": "--" + name, "summary": summary} for name, _, summary in OPTIONS]
    exits = {str(code): status for status, code in EXIT_FOR.items()}
    lines = ["  %-18s %s%s" % (op["flag"], op["summary"], "  [%s]" % ", ".join(op["effects"]) if op["effects"] else "")
             for op in operations]
    return Answer({"operations": operations, "options": options, "exits": exits}, lines)


def _text_of(answer):
    """
    The person's lines, then what the answer carries that they do not say yet: each problem and could-not-run item
    with its fix, each note and assumption, and the next steps (P124, #58). A line already said is not said again, so a
    handler that prints an item its own way keeps its wording; one that forgets an item no longer drops it.
    """
    lines = list(answer.lines)
    said = lambda words: bool(words) and any(words in line for line in answer.lines)  # noqa: E731 — the handler's own
    for heading, items in (("", answer.problems), ("could not check: ", answer.unchecked)):
        for item in items:
            if not (said(item["sentence"]) or said(item.get("subject"))):  # a handler may word an item its own way
                lines.append("  %s%s%s" % (heading, "%s: " % item["subject"] if item.get("subject") else "", item["sentence"]))
            if item.get("fix") and not said(item["fix"]):
                lines.append("  fix%s: %s" % (" for %s" % item["subject"] if item.get("subject") else "", item["fix"]))
    for note in answer.notes:
        shown = "%s: %s" % (note["subject"], note["sentence"]) if note.get("subject") else note["sentence"]
        if not said(shown):
            lines.append("  " + shown)
    for assumption in answer.assumptions:
        if not (said(assumption["fact"]) or said(assumption.get("sentence"))):
            lines.append("  ? %s%s%s" % (assumption["fact"], " = %s" % assumption["assumed"] if "assumed" in assumption else "",
                                         " — " + assumption["sentence"] if assumption.get("sentence") else ""))
        if assumption.get("upgrade") and not said(assumption["upgrade"]):
            lines.append("    to settle it: %s" % assumption["upgrade"])
    lines += ["  next: parts.py %s — %s" % (" ".join(step["argv"]), step["why"]) for step in answer.next]
    return lines


def _say(op, answer, as_json):
    """
    Print one answer and return its exit code (§6.4.1): with --json the envelope, compact, on stdout; without, the
    person's lines and whatever the answer carries that they leave out (`_text_of`). An answer with no lines says its
    problems and could-not-run items on stderr, as before.
    """
    said = envelope("parts", op, answer.data, answer.problems, answer.unchecked, answer.next, answer.truncated,
                    notes=answer.notes, assumptions=answer.assumptions)
    if answer.diagnostics:
        print(guard_lines("\n".join(answer.diagnostics)), file=sys.stderr)
    if as_json:
        print(json.dumps(said, ensure_ascii=False, separators=(",", ":")).encode("utf-8", "backslashreplace").decode("utf-8"))  # P445: a lone surrogate is written as a JSON escape
    else:
        if not answer.lines:
            for item in list(answer.problems) + list(answer.unchecked):
                said_here = "parts.py: %s%s" % (item["sentence"], " — " + item["fix"] if item.get("fix") else "")
                print(guard_lines(said_here), file=sys.stderr)
            answer = answer._replace(problems=(), unchecked=())
        for line in _text_of(answer):
            # P403, P423: every field, once, at the edge: a control or a right-to-left character shows as `?`. A line's own
            # newlines stay. A name that can hold a newline (a holder, a used_in key) is guarded where it is put in.
            print(guard_lines(line))  # --json stays raw, as data
    return EXIT_FOR[said["status"]]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    asked = next((name for name, *_ in OPERATIONS if "--" + name in argv), None)
    try:
        args = _parser().parse_args(argv)
    except BadArgument as bad:
        return _say(asked, Answer(unchecked=[_cannot(str(bad), "parts.py --describe --json lists every operation and its arguments")]),
                    "--json" in argv)
    op = next(name for name, *_ in OPERATIONS if getattr(args, name.replace("-", "_")) not in (None, False))
    project = args.project.resolve() if args.project else None
    writes = "writes" in next(effects for name, _, _, effects, _ in OPERATIONS if name == op)
    try:
        with store.locked() if writes else contextlib.nullcontext():
            answer = globals()["_op_" + op.replace("-", "_")](args, project)
    except (OSError, json.JSONDecodeError) as unreadable:
        answer = Answer(unchecked=[_cannot("--%s: %s" % (op, unreadable))])
    except PartError as broken:
        value = getattr(args, op.replace("-", "_"))
        answer = Answer(problems=[_problem(" ".join(value) if isinstance(value, list) else
                                           (value if isinstance(value, str) else None), str(broken))])
    except CodedMessageError as broken:  # a store's refusal, an unreadable input: could-not-run, never a traceback
        answer = Answer(unchecked=[_cannot(str(broken))])
    return _say(op, answer, args.json)


if __name__ == "__main__":
    sys.exit(main())
