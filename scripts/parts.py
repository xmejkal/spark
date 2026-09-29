#!/usr/bin/env python3
"""
What a part asks of the board it plugs into, and what is actually known about it.

    parts.py --list
    parts.py --show l9110s-module
    parts.py --validate
    parts.py --unverified <part> [part ...]   what nobody has checked yet about those parts

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

#: What a pin's WIRING name may contain. Measured, not assumed: a probe board with six pin
#: labels showed `IN+`, `OUT-` and `A.B` unresolvable as tscircuit selectors while `V_IN`,
#: `GND2` and `3V3` resolved. An MP1584 buck's pads are silkscreened IN+ IN- OUT+ OUT-, and a
#: record using those names produced four "could not find port" errors and a regulator joined
#: to nothing. The fix at the time renamed the pins and LOST the silkscreen — which is exactly
#: the failure `physical.pad_aliases` prevents on the board side. Parts had no equivalent.
#:
#: So an entry has a `pin` (what selectors use, restricted to this) and optionally `printed`
#: (what is silkscreened, unrestricted). The generated file shows both where they differ.
SELECTOR_SAFE = "^[A-Za-z0-9_]+$"

#: What a `needs` entry may ask a pin for. THE ONE DEFINITION — `assign_pins` imports it from
#: here rather than keeping its own, because it had its own and the two disagreed: a servo part
#: declaring `needs: ["pwm"]` validated as a good record and then made the pin assigner refuse
#: the whole design. The only way out was to delete a true fact about the part, which is a
#: contract punishing honesty.
#:
#: It lives in the lower module on purpose. A capability is a claim a PART makes, so the file
#: that validates parts owns the vocabulary and the file that consumes it follows.
CAPABILITIES = ("wake", "adc", "pwm")

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


#: Footprinter families whose trailing number IS the pad count. Deliberately a whitelist, because
#: the obvious shortcut — take the first integer — is wrong in the most damaging direction:
#: `sot23` is a three-pad package named after its body, `0603` is a size in hundredths of an inch,
#: and `sod123` is neither. A rule that read those as 23, 603 and 123 pads would contradict every
#: honest part file it met, which is how a useful check gets switched off.
PAD_COUNT_FAMILIES = ("pinrow", "headermodule", "jst_ph_", "jst_sh_", "jst_xh_", "dip", "bh_")

#: The three lists in a record that hold pins. Written out three times before 2026-09-29, and
#: the missing-pin rule was applied to one of them for a week while the other two were read
#: with `entry["pin"]` — G15. A fourth list added to the schema now has to be added here, and
#: nowhere else.
PIN_LISTS = ("needs", "power", "unused_pins")


def printed_names(part):
    """`{wiring name: silkscreen text}` for every pin whose silkscreen differs from its name."""
    out = {}
    for group in PIN_LISTS:
        for entry in part.get(group) or []:
            pin, printed = entry.get("pin"), entry.get("printed")
            if pin and printed and printed != pin:
                out[pin] = printed
    return out


def has_placeholder_footprint(part):
    """Whether this part's footprint is a stand-in for one nobody has drawn yet."""
    return bool(part.get("footprint_placeholder"))


def footprint_pad_count(footprint):
    """
    How many pads a footprinter string describes, or None when this cannot tell.

    None is a real answer and must stay available: most footprints do not encode a count, and a
    checker that guesses one would report every one of them as a disagreement.
    """
    if not isinstance(footprint, str):
        return None
    name = footprint.strip().lower()
    for family in PAD_COUNT_FAMILIES:
        if name.startswith(family):
            digits = ""
            for character in name[len(family):]:
                if not character.isdigit():
                    break
                digits += character
            if digits:
                return int(digits)
    return None


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
        if not need.get("signal"):
            problems.append("%s has no signal" % where)
        if need.get("direction") not in ("in", "out", "bidirectional", None):
            problems.append("%s direction is %r; expected in, out or bidirectional"
                            % (where, need.get("direction")))
        unknown = sorted(set(need.get("needs") or []) - set(CAPABILITIES))
        if unknown:
            # Caught HERE, not four scripts later. `assign_pins` refuses the entire design over
            # an unknown capability — rightly, since a silently dropped requirement produces a
            # board wrong in exactly the way the requirement existed to prevent — but it did so
            # long after this file had pronounced the record good.
            problems.append("%s asks a pin for %s, which is not something a pin can be asked "
                            "for. Known: %s"
                            % (where, ", ".join(unknown), ", ".join(CAPABILITIES)))

    # Every list of pins, in one place. Only `needs` entries were checked for a pin, and then
    # `power` and `unused_pins` were read with `entry["pin"]` in four places — so an entry missing
    # one crashed the validator instead of being reported by it. Same defect twice in one file,
    # which is what happens when a rule is written at the use site rather than the contract.
    for group in PIN_LISTS:
        for index, entry in enumerate(part.get(group) or []):
            if not entry.get("pin"):
                problems.append("%s[%d] has no pin, so nothing can say where it connects"
                                % (group, index))

    # The wiring name reaches a tscircuit selector verbatim, so it is restricted to what a
    # selector can parse. The silkscreen goes in `printed`, where anything is allowed.
    import re
    for group in PIN_LISTS:
        for index, entry in enumerate(part.get(group) or []):
            pin = entry.get("pin")
            if pin and not re.match(SELECTOR_SAFE, str(pin)):
                problems.append(
                    "%s[%d] pin %r cannot be a selector — letters, digits and _ only. If that is "
                    "what the silkscreen says, keep it in `printed` and give `pin` a wiring name"
                    % (group, index, pin))
            printed = entry.get("printed")
            if printed is not None and not isinstance(printed, str):
                problems.append("%s[%d] printed is %r; it is the silkscreen text, a string"
                                % (group, index, printed))

    # Dimensions are a real schema, not an open fact, because every part has an outline and a
    # generator reads them structurally to decide where things go. They sat OUTSIDE the
    # provenance contract as a bare `{"width": .., "height": ..}` — so one part carried a
    # measured size, one carried an unsourced guess wearing exactly the same clothes, and one
    # carried nothing at all and silently became 16 x 12 mm inside the generator. Placement was
    # then proven not to overlap, using numbers nobody had taken.
    body = part.get("body_mm")
    if body is not None:
        if not isinstance(body, dict):
            problems.append("body_mm is not an object; it needs width, height and provenance")
        else:
            for key in ("width", "height"):
                if not isinstance(body.get(key), (int, float)):
                    problems.append("body_mm has no numeric %s" % key)
            for key in ("verified", "source"):
                if key not in body:
                    problems.append("body_mm has no %r — a dimension with no provenance is a "
                                    "guess, and a generator cannot tell the difference" % key)
            if body.get("verified") is False and not body.get("why_it_matters"):
                problems.append("body_mm is unverified with no why_it_matters; say what depends "
                                "on it — here, whether the modules physically fit the board")

    # A footprint standing in for the real one. `facts` and `body_mm` carry `verified`; the
    # footprint carried no provenance at all, so an XT30 inlet drawn as a JST PH — wrong pitch,
    # wrong hole size, stated as a placeholder in a comment nothing reads — looked identical to a
    # footprint generated from a vendor drawing. `check_footprints` duly measured the JST's
    # annular rings and reported a defect about a part that is not on the board. The most
    # expensive field to get wrong was the one field with no way to say "not yet".
    if part.get("footprint_placeholder"):
        if not part.get("footprint_note"):
            problems.append("footprint_placeholder is set with no footprint_note — say what the "
                            "real footprint is and why this one stands in, or nobody can finish it")

    # Which pad is pin 1. The generator numbered `pinLabels` from the order the pins happened to
    # appear in this file — so an L9110S whose header reads BIA BIB GND VCC AIA AIB was emitted
    # as pin1: "AIA", and every trace to the module landed on the wrong pad. Nothing here could
    # have been right, because the physical order was not written down anywhere.
    order = part.get("pin_order")
    if order is not None:
        if not isinstance(order, list) or not order:
            problems.append("pin_order must be a list of pad names, pad 1 first")
        else:
            # `.get`, not `[...]`. An entry with no `pin` is exactly what the checks above
            # exist to report, and reading it here crashed the validator on the malformation it
            # was written to catch: `needs[0] has no pin` was appended, then this line raised
            # KeyError three lines later. Every real part has a pin_order, so any part broken in
            # that way took the whole run down instead of being reported.
            named = {entry.get("pin") for group in PIN_LISTS
                     for entry in part.get(group) or []} - {None}
            for position, pad in enumerate(order, start=1):
                if pad is not None and pad not in named:
                    problems.append(
                        "pin_order pad %d is %r, which this part never mentions — a pad name that "
                        "matches nothing silently wires nothing" % (position, pad))
            # A pad may legitimately appear twice, but only if it is a SUPPLY. Real modules bring
            # VCC and GND out on both rows so either side can be fed; a repeated SIGNAL is a typo,
            # and two pads shorted together is what it would build.
            supplies = {supply.get("pin") for supply in part.get("power") or []}
            placed = [pad for pad in order if pad is not None]
            repeated = {pad for pad in placed if placed.count(pad) > 1}
            for pad in sorted(repeated - supplies):
                problems.append(
                    "pin_order names %r on more than one pad, and it is not a supply — a signal "
                    "on two pads is two pads shorted together" % pad)
            missing = sorted(named - set(placed))
            if missing:
                problems.append(
                    "pin_order does not say where %s sit(s), so the generator would have to "
                    "guess a pad for them" % ", ".join(missing))

            # The two fields describe the same physical thing and nothing compared them. The
            # VL6180X breakout shipped saying `pinrow5` while naming seven pads — five of its
            # seven carry a signal and two are unwired, so somebody counted the pins instead of
            # the pads. The generator then labelled a pad that did not exist; that port got no
            # position, and tscircuit's autorouter died reading its x — which does not fail
            # loudly, it just leaves the whole board with zero traces.
            pads = footprint_pad_count(part.get("footprint"))
            if pads is not None and pads != len(order):
                problems.append(
                    "footprint %r has %d pads but pin_order names %d. They describe the same "
                    "physical part, so one of them is wrong — and the generator will label a pad "
                    "that does not exist, which leaves that port with no position at all"
                    % (part["footprint"], pads, len(order)))

    # A power pin's DIRECTION is what says whether sharing a net is normal or fatal. Several GND
    # pins on one net is how ground works; two amplifier outputs on one net is a short. Both
    # looked identical in this schema — a `rail` and nothing else — and the generator duly wired
    # both halves of a bridged class-D output together, under the part's own note saying never to.
    outputs_by_rail = {}
    for index, supply in enumerate(part.get("power") or []):
        where = "power[%d]" % index
        direction = supply.get("direction")
        if direction not in ("in", "out"):
            problems.append(
                "%s direction is %r; a power pin is 'in' (it consumes a rail, and sharing one is "
                "normal) or 'out' (it drives a load, and sharing a net is a short)"
                % (where, direction))
        elif direction == "out":
            # Keyed on the NET it would land on, which for an output is the load plus which side
            # of it this pin drives. Two outputs on one load are the normal case — that is what a
            # differential pair is — and they are only a short if nothing distinguishes them.
            outputs_by_rail.setdefault(
                (supply.get("rail"), supply.get("polarity")), []).append(supply.get("pin"))

    for (rail, polarity), pins in outputs_by_rail.items():
        if len(pins) > 1:
            problems.append(
                "power pins %s are outputs driving %r with the same polarity (%r), so they would "
                "land on one net and short into each other. Give each its own `polarity`, or they "
                "are not separate outputs" % (", ".join(pins), rail, polarity))

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
    # Every function in this file already took `project`, and nothing ever passed one — so the
    # docstring's promise that "a project's own wins" was unreachable from any entry point and
    # the library was closed at whatever ships with the plugin.
    parser.add_argument("--project", type=Path,
                        help="a project whose own parts/ beats the shipped library")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    project = args.project.resolve() if args.project else None

    try:
        if args.list:
            listing = [dict(load(part_id, project), id=part_id) for part_id in available(project)]
            if args.json:
                print(json.dumps({"tool": "parts", "parts": [
                    {"id": part["id"], "kind": part["kind"], "name": part["name"],
                     "from": str(definition_path(part["id"], project).parent)}
                    for part in listing]}, indent=2))
            else:
                for part in listing:
                    where = ("project" if project and definition_path(part["id"], project).parent
                             != LIBRARY else "library")
                    print("  %-22s %-16s %-9s %s"
                          % (part["id"], part["kind"], where, part["name"]))
        elif args.show:
            part = load(args.show, project)
            print(json.dumps(part, indent=2) if args.json else _show(part))
        elif args.signals:
            print(json.dumps({"signals": signals_for(args.signals, project)}, indent=2))
        elif args.unverified:
            questions = unverified(args.unverified, project)
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
            checked = []
            for part_id in available(project):
                path = definition_path(part_id, project)
                checked.append({"part": part_id, "path": str(path),
                                "problems": validate(json.loads(path.read_text()), path)})
            if args.json:
                print(json.dumps({"tool": "parts",
                                  "status": "problems" if any(c["problems"] for c in checked)
                                            else "ok",
                                  "checked": checked}, indent=2))
            else:
                for one in checked:
                    print("  %-22s %s" % (one["part"], "ok" if not one["problems"]
                                          else "%d problem(s)" % len(one["problems"])))
                    for problem in one["problems"]:
                        print("      - %s" % problem)
            return EXIT_INVALID if any(c["problems"] for c in checked) else EXIT_OK
    except PartError as broken:
        print("parts.py: %s" % broken, file=sys.stderr)
        return EXIT_INVALID
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
