#!/usr/bin/env python3
"""
What a part asks of the board it plugs into, and what is actually known about it.

    parts.py --list
    parts.py --show l9110s-module
    parts.py --validate
    parts.py --unverified            what nobody has checked yet, across every part in use

A part library is easy to get wrong in a way that is worse than not having one. The temptation is
a schema covering everything a part might have — and since a motor driver's facts (input
thresholds, current) have nothing in common with a rangefinder's (an I2C address, a calibration),
that schema degenerates into `{"name": ..., "notes": ...}`: a directory of documentation
pretending to be configuration.

So this splits them.

**`needs` is a real schema**, because it IS uniform: every part asks its host for some pins, and
each pin either needs a capability or does not. That is exactly what `assign_pins.py` consumes,
and it is the reason this file exists rather than a folder of markdown.

**`facts` is deliberately open**, and every entry carries three things: a value, where it came
from, and whether anyone has actually checked. A fact with `verified: false` is not a defect —
most parts arrive with several — but it must be VISIBLE, because the unverified ones are what
decide whether a design works. On the project this came from, the single most consequential
number in the whole build was an audio module's idle current, which nobody had measured and
every document quietly assumed.
"""

import argparse
import json
import sys
from pathlib import Path

#: Parts ship with the plugin, and a project may keep its own in `parts/`. A project's own wins,
#: for the same reason a board definition does: what you verified yourself must not be replaced.
LIBRARY = Path(__file__).resolve().parent.parent / "parts"
PROJECT_PARTS_DIR = "parts"
DEFINITION_SUFFIX = ".json"

SUPPORTED_SCHEMA = 1

REQUIRED_KEYS = ("schema", "id", "name", "kind", "needs")

#: Each entry in `facts` must answer all three, or it is an opinion with a number attached.
REQUIRED_FACT_KEYS = ("value", "verified", "source")

EXIT_OK, EXIT_INVALID = 0, 1


class PartError(Exception):
    """A part definition that cannot be used, with the reason."""


def search_path(project: Path = None) -> list:
    return [project / PROJECT_PARTS_DIR for project in ([project] if project else [])] + [LIBRARY]


def available(project: Path = None) -> list:
    found = {}
    for directory in reversed(search_path(project)):
        if not directory.is_dir():
            continue
        for path in directory.glob("*" + DEFINITION_SUFFIX):
            found[path.stem] = path
    return sorted(found)


def definition_path(part_id: str, project: Path = None) -> Path:
    for directory in search_path(project):
        path = directory / (part_id + DEFINITION_SUFFIX)
        if path.is_file():
            return path
    raise PartError("no part called %r.\n  available: %s"
                    % (part_id, ", ".join(available(project)) or "(none)"))


def load(part_id: str, project: Path = None) -> dict:
    path = definition_path(part_id, project)
    part = json.loads(path.read_text())
    problems = validate(part, path)
    if problems:
        raise PartError("%s does not meet the part contract:\n%s"
                        % (path, "\n".join("  - " + problem for problem in problems)))
    return part


def validate(part: dict, path: Path) -> list:
    """Every way this definition breaks the contract. Empty means it holds."""
    problems = []

    if part.get("schema") != SUPPORTED_SCHEMA:
        problems.append("schema is %r, but this code understands only %d"
                        % (part.get("schema"), SUPPORTED_SCHEMA))
    for key in REQUIRED_KEYS:
        if key not in part:
            problems.append("missing required key %r" % key)
    if part.get("id") != path.stem:
        problems.append("id is %r but the file is named %r; they must match"
                        % (part.get("id"), path.stem))

    for index, need in enumerate(part.get("needs") or []):
        where = "needs[%d]" % index
        for key in ("signal", "pin"):
            if not need.get(key):
                problems.append("%s has no %s" % (where, key))
        if need.get("direction") not in ("in", "out", "bidirectional", None):
            problems.append("%s direction is %r; expected in, out or bidirectional"
                            % (where, need.get("direction")))

    for name, fact in (part.get("facts") or {}).items():
        if not isinstance(fact, dict):
            problems.append("facts.%s is not an object; every fact needs a value, a source and "
                            "whether it is verified" % name)
            continue
        for key in REQUIRED_FACT_KEYS:
            if key not in fact:
                problems.append("facts.%s has no %r — a number with no provenance is an opinion"
                                % (name, key))
        if fact.get("verified") and fact.get("value") is None:
            problems.append("facts.%s is marked verified but has no value" % name)
        if fact.get("verified") is False and fact.get("value") is not None \
                and not fact.get("why_it_matters"):
            # An unverified guess that nobody explains is how an assumption becomes a fact.
            problems.append("facts.%s is an unverified value with no why_it_matters; say what "
                            "depends on it or do not carry the number" % name)

    return problems


def signals_for(part_ids, project: Path = None) -> list:
    """
    Every signal these parts ask the host for, ready for `assign_pins.py`.

    Optional signals are included: a part that CAN wake the host usually should be able to, and
    a caller that does not want it can drop it. Silently omitting them would hide a requirement.
    """
    signals = []
    for part_id in part_ids:
        part = load(part_id, project)
        for need in part.get("needs") or []:
            entry = {"name": need["signal"], "needs": need.get("needs", [])}
            if need.get("pin_on_host"):
                entry["pin"] = need["pin_on_host"]
            if need.get("bus"):
                # A bus signal means dedicated hardware. The board almost certainly brings the
                # peripheral out on a pin of the same name, and using any other pin either does
                # not work or gives up the hardware peripheral for a bit-banged one.
                entry["bus"] = need["bus"]
            entry["from"] = part_id
            signals.append(entry)
    return signals


def unverified(part_ids, project: Path = None) -> list:
    """Every fact nobody has checked, across these parts — the design's real open questions."""
    open_questions = []
    for part_id in part_ids:
        part = load(part_id, project)
        for name, fact in (part.get("facts") or {}).items():
            if fact.get("verified"):
                continue
            open_questions.append({
                "part": part_id, "fact": name,
                "assumed": fact.get("value"),
                "why_it_matters": fact.get("why_it_matters") or "",
                "source": fact.get("source", "")})
    return open_questions


def _show(part):
    lines = ["%s — %s" % (part["name"], part["kind"]), ""]
    lines.append("  asks the host for:")
    for need in part.get("needs") or []:
        wants = (" [%s]" % ", ".join(need["needs"])) if need.get("needs") else ""
        optional = " (optional)" if need.get("optional") else ""
        lines.append("    %-12s -> module pin %s%s%s" % (need["signal"], need["pin"], wants, optional))

    facts = part.get("facts") or {}
    if facts:
        lines.append("\n  known:")
        for name, fact in facts.items():
            mark = "verified" if fact.get("verified") else "UNVERIFIED"
            lines.append("    %-28s %-10s %s" % (name, str(fact.get("value")), mark))
            if not fact.get("verified") and fact.get("why_it_matters"):
                lines.append("      %s" % fact["why_it_matters"])

    for requirement in part.get("host_requirements") or []:
        lines.append("\n  the board must: %s" % requirement)
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="parts.py", description="What a part needs, and what is known about it.")
    what = parser.add_mutually_exclusive_group(required=True)
    what.add_argument("--list", action="store_true")
    what.add_argument("--show", metavar="PART")
    what.add_argument("--validate", action="store_true")
    what.add_argument("--signals", nargs="+", metavar="PART",
                      help="the signals these parts ask for, as assign_pins.py input")
    what.add_argument("--unverified", nargs="+", metavar="PART",
                      help="what nobody has checked about these parts")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.list:
            for part_id in available():
                part = load(part_id)
                print("  %-22s %-16s %s" % (part_id, part["kind"], part["name"]))
        elif args.show:
            print(_show(load(args.show)))
        elif args.signals:
            print(json.dumps({"signals": signals_for(args.signals)}, indent=2))
        elif args.unverified:
            questions = unverified(args.unverified)
            if args.json:
                print(json.dumps(questions, indent=2))
            elif not questions:
                print("  everything these parts claim has been checked.")
            else:
                print("  %d thing(s) nobody has checked:\n" % len(questions))
                for question in questions:
                    print("  %s.%s = %s" % (question["part"], question["fact"],
                                            question["assumed"]))
                    if question["why_it_matters"]:
                        print("      %s" % question["why_it_matters"])
        else:
            failed = False
            for part_id in available():
                path = definition_path(part_id)
                problems = validate(json.loads(path.read_text()), path)
                print("  %-22s %s" % (part_id, "ok" if not problems
                                      else "%d problem(s)" % len(problems)))
                for problem in problems:
                    print("      - %s" % problem)
                failed = failed or bool(problems)
            return EXIT_INVALID if failed else EXIT_OK
    except PartError as broken:
        print("parts.py: %s" % broken, file=sys.stderr)
        return EXIT_INVALID
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
