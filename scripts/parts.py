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
import datetime
import hashlib
import json
import re
import struct
import sys
import urllib.parse
import urllib.request
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

from outcomes import EXIT_OK, EXIT_PROBLEMS as EXIT_INVALID, EXIT_COULD_NOT_RUN  # noqa: E402


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

#: The buses a part may put a signal on, and the lines each has, by the board's label for the
#: line with the names vendors print for it. THE definition: `assign_pins` imports it to find the
#: board's pin for a line, and `validate` refuses a record naming a bus or a line not here — where
#: the record is written, not four scripts later (the shape of `CAPABILITIES`, G12). `i2s` was
#: missing from the assigner's own copy for one evening and the shipped MAX98357A could not be
#: placed by the chain while `--validate` called it fine (sprint-4 close audit, C6). A signal
#: named `<BUS>_<LINE>` — `I2S_BCLK` — names its line.
BUSES = {
    "i2c": {"SDA": ("SDA",), "SCL": ("SCL",)},
    "spi": {"SCK": ("SCK", "CLK", "SCLK"), "MOSI": ("MOSI", "DIN", "SDI", "SI"),
            "MISO": ("MISO", "DOUT", "SDO", "SO"), "SS": ("SS", "CS", "NSS")},
    "i2s": {"BCLK": ("BCLK", "SCK"), "LRC": ("LRC", "LRCLK", "WS"), "DIN": ("DIN", "SD", "DOUT")},
}


def bus_line_of(bus, name):
    """Which line of `bus` a signal called `name` is, by the board's label — or None."""
    lines = BUSES.get(bus) or {}
    printed = str(name).upper()
    if printed.startswith(bus.upper() + "_"):
        printed = printed[len(bus) + 1:]
    for line, names in lines.items():
        if printed in names:
            return line
    return None


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


#: How a part is simulated (backlog P31, ordered by the PO 2026-09-29): a Wokwi built-in part
#: standing in for it, a custom chip written for it and kept beside its record, or a reason it is
#: absent. `pins` maps the record's wired pads to the stand-in's pin names; null says the
#: stand-in has no such pin. The converter reads this instead of a hand table in another repo.
CHIP_SOURCE_SUFFIXES = (".chip.c", ".chip.json")


def chip_folder(part: dict, path: Path) -> Path:
    """Where a record's custom chip lives: `<record's folder>/<id>/chip/`, travelling with it."""
    return path.parent / part["id"] / "chip"


#: What a record may demand of its host as a COMPONENT (backlog P6): a resistor from a signal
#: pad to ground or to the part's rail, or a divider that brings a signal down before the host's
#: pin. The generator places and wires these; every other requirement stays prose, and is said.
HOST_PART_KINDS = ("pulldown", "pullup", "divider", "series")


def pin_order_problems(part: dict) -> list:
    """
    A pin order says how it was read (P81): it is the field where a mistake reverses a supply, and
    it was the one fact whose source lived only in a prose note nothing checked.
    """
    if not any(pad for pad in part.get("pin_order") or []):
        return []
    proof = part.get("pin_order_proof")
    if not isinstance(proof, dict):
        return ["pin_order states no pin_order_proof {verified, source}: where the order was read, "
                "because a pin order read wrong reverses a supply"]
    problems = []
    if not isinstance(proof.get("verified"), bool):
        problems.append("pin_order_proof.verified must be true or false")
    if not isinstance(proof.get("source"), str) or not proof["source"].strip():
        problems.append("pin_order_proof names no source: say where the pin order was read")
    return problems


def document_problems(part: dict) -> list:
    """
    A record points at its kept sources from `documents`, which replaced `attachments` (P62a,
    W16: one format, no reader for both). Each entry names a URL, the file, and a checksum that
    is one — the store finds a file by it, so a wrong one is a pointer to nothing.
    """
    problems = []
    if "attachments" in part:
        problems.append("`attachments` was replaced by `documents` (P62a): the file goes to the "
                        "store, the record keeps the pointer — run parts.py --fetch to redo it")
    for key, entry in (part.get("documents") or {}).items():
        if not isinstance(entry, dict) or not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256"))):
            problems.append("documents.%s has no sha256 that is one, so the store cannot find it" % key)
        elif not entry.get("file"):
            problems.append("documents.%s names no file" % key)
    problems += ["%s cites %r, which documents does not hold — a pointer to nothing" % (where, cited)
                 for where, cited in _citations(part) if cited not in (part.get("documents") or {})]
    return problems


def _citations(value, where=""):
    """(field, document key) for every `cites` in a record, at any depth."""
    found = []
    for name, inner in (value.items() if isinstance(value, dict) else []):
        here = "%s.%s" % (where, name) if where else name
        if name == "cites" and isinstance(inner, dict):
            found.append((where, inner.get("document")))
        elif isinstance(inner, dict):
            found += _citations(inner, here)
    return found


def i2c_pullup_problems(part: dict) -> list:
    """
    A record on an I2C bus says where its pull-ups come from (P55).

    I2C only ever pulls down, and a board may have none of its own — the FireBeetle V1.2+ has none
    anywhere. So the module carries them (`facts.module_has_i2c_pullups`), or the host adds them
    (`host_parts` pull-ups on every bus line); saying neither is how a bus floats. A module
    pull-up must also be one that can hold a bus: the same band `compare_design` judges by.
    """
    from compare_design import PULLUP_MIN_OHM, PULLUP_MAX_OHM
    lines = [need.get("pin") for need in part.get("needs") or [] if need.get("bus") == "i2c"]
    if not lines:
        return []
    facts = part.get("facts") or {}
    on_module = (facts.get("module_has_i2c_pullups") or {}).get("value") is True
    by_host = {extra.get("pin") for extra in part.get("host_parts") or [] if extra.get("kind") == "pullup"}
    problems = []
    if not on_module and not set(lines) <= by_host:
        problems.append("on an I2C bus that nothing pulls up: facts.module_has_i2c_pullups is not true "
                        "and host_parts adds no pullup on %s — I2C only pulls down, and a board may "
                        "have none of its own" % ", ".join(lines))
    ohms = (facts.get("i2c_pullup_ohms") or {}).get("value")
    if isinstance(ohms, (int, float)) and not PULLUP_MIN_OHM <= ohms <= PULLUP_MAX_OHM:
        problems.append("facts.i2c_pullup_ohms is %g ohm, outside the %d-%d ohm that can hold a bus"
                        % (ohms, PULLUP_MIN_OHM, PULLUP_MAX_OHM))
    return problems


def host_part_problems(part: dict) -> list:
    """What is wrong with a record's `host_parts`: a kind nothing can place, a pad, a value, a why."""
    problems = []
    signal_pads = {entry.get("pin") for entry in part.get("needs") or []} - {None}
    for index, host_part in enumerate(part.get("host_parts") or []):
        where = "host_parts[%d]" % index
        if not isinstance(host_part, dict):
            problems.append("%s must be an object {kind, pin, ohms, why}" % where)
            continue
        kind = host_part.get("kind")
        if kind not in HOST_PART_KINDS:
            problems.append("%s kind %r is not one the generator can place: %s" % (where, kind, ", ".join(HOST_PART_KINDS)))
            continue
        if host_part.get("pin") not in signal_pads:
            problems.append("%s names pin %r, which is not a signal pad of this part" % (where, host_part.get("pin")))
        def positive(key):
            value = host_part.get(key)
            return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0
        if kind == "series":
            # P78: a series resistor states its value, or the current it is for and the generator
            # computes the value from the part's forward voltage and the board's I/O voltage.
            if not positive("ohms") and not positive("for_current_ma"):
                problems.append("%s needs a positive ohms, or a for_current_ma to compute it from" % where)
        else:
            for key in (("top_ohms", "bottom_ohms") if kind == "divider" else ("ohms",)):
                if not positive(key):
                    problems.append("%s needs a positive %s" % (where, key))
        if not host_part.get("why"):
            problems.append("%s says no why — a passive nobody can explain is the first one removed" % where)
    return problems


def simulation_problems(part: dict, path: Path) -> list:
    """What is wrong with a record's `simulation`, if it has one; nothing is allowed to be absent."""
    sim = part.get("simulation")
    if sim is None:
        return []
    if not isinstance(sim, dict):
        return ["simulation must be an object: {\"wokwi\": {...}} or {\"skip\": \"why\"}"]
    if "skip" in sim:
        problems = [] if isinstance(sim["skip"], str) and sim["skip"] else [
            "simulation.skip must say why the part is absent from the simulation"]
        if "wokwi" in sim:
            problems.append("simulation has both skip and wokwi; a part is simulated or it is not")
        return problems
    wokwi = sim.get("wokwi")
    if not isinstance(wokwi, dict):
        return ["simulation needs wokwi {part or chip, pins, stand_in} or skip with a reason"]
    problems = []
    part_type, chip = wokwi.get("part"), wokwi.get("chip")
    if bool(part_type) == bool(chip):
        problems.append("simulation.wokwi names exactly one of part (a Wokwi built-in) or chip "
                        "(a custom chip beside the record)")
    if part_type and not wokwi.get("stand_in"):
        problems.append("a built-in part stands in for the real one: simulation.wokwi.stand_in must say "
                        "what differs, so a pass here is not mistaken for the bench")
    pins = wokwi.get("pins")
    if not isinstance(pins, dict):
        problems.append("simulation.wokwi.pins must map each wired pad to the stand-in's pin name, "
                        "or to null when the stand-in has no such pin")
    else:
        wired = {entry.get("pin") for group in ("needs", "power") for entry in part.get(group) or []} - {None}
        mentioned = {entry.get("pin") for group in PIN_LISTS for entry in part.get(group) or []} - {None}
        for pad in sorted(set(pins) - mentioned):
            problems.append("simulation.wokwi.pins names %r, a pad this part never mentions" % pad)
        for pad in sorted(wired - set(pins)):
            problems.append("simulation.wokwi.pins does not say where the wired pad %r goes on the "
                            "stand-in; name its pin, or null when it has none" % pad)
    if chip:
        folder = chip_folder(part, path)
        for suffix in CHIP_SOURCE_SUFFIXES:
            if not (folder / (chip + suffix)).is_file():
                problems.append("simulation.wokwi.chip %r needs %s beside the record" % (chip, folder / (chip + suffix)))
        problems.extend(control_problems(chip, folder / (chip + ".chip.json")))
        definition = _parse(folder / (chip + ".chip.json")) if (folder / (chip + ".chip.json")).is_file() else None
        chip_pins = set((definition or {}).get("pins") or []) - {""}
        if chip_pins and isinstance(pins, dict):
            # `AIA: "NOPE"` validated clean and was refused only by the converter (audit D18).
            for pad, target in sorted(pins.items()):
                if target is not None and target not in chip_pins:
                    problems.append("simulation.wokwi.pins maps %r to %r, which chip %s does not have: %s"
                                    % (pad, target, chip, ", ".join(sorted(chip_pins))))
    return problems


#: What wokwi-cli itself enforces on a control's id (its own message, 2026-09-29): a scenario's
#: `set-control` names it, so `flow_lpm` would be a slider nothing can set.
CONTROL_ID = re.compile(r"[a-zA-Z][a-zA-Z0-9]*")


def control_problems(chip, definition):
    """Controls in a chip's definition that a scenario could not name."""
    parsed = _parse(definition) if definition.is_file() else None
    if not isinstance(parsed, dict):
        return []
    return ["chip %s control %r: Wokwi requires an id of letters and digits only, starting with a letter"
            % (chip, control.get("id"))
            for control in parsed.get("controls") or [] if not CONTROL_ID.fullmatch(str(control.get("id")))]


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
        bus = need.get("bus")
        if bus and bus not in BUSES:
            problems.append("%s is on bus %r, which is not a bus this knows: %s"
                            % (where, bus, ", ".join(BUSES)))
        elif bus and need.get("signal") and bus_line_of(bus, need["signal"]) is None:
            problems.append("%s is on the %s bus but %r is not one of its lines: %s"
                            % (where, bus.upper(), need["signal"],
                               ", ".join("%s (%s)" % (line, "/".join(names))
                                         for line, names in BUSES[bus].items())))
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

    problems.extend(host_part_problems(part))
    problems.extend(i2c_pullup_problems(part))
    problems.extend(document_problems(part))
    problems.extend(pin_order_problems(part))
    problems.extend(simulation_problems(part, path))
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
                # A bus signal means dedicated hardware: the board's pin for that line of that
                # bus, found by `assign_pins.bus_line`. `line` is the part's own name for the
                # line — SDA, or a vendor's DIN — and it has to survive the instance rename that
                # `design.signals_of` gives `name`, or the assigner cannot find the pin (P21).
                entry["bus"] = need["bus"]
                entry["line"] = need["signal"]
            entry["from"] = part_id
            signals.append(entry)
    return signals


def open_questions_of(part, part_id=None):
    """Every fact in one record nobody has checked — its pin order among them (P81)."""
    part_id = part_id or part.get("id")
    questions = [{"part": part_id, "fact": name, "assumed": fact.get("value"),
                  "why_it_matters": fact.get("why_it_matters") or "", "source": fact.get("source", "")}
                 for name, fact in (part.get("facts") or {}).items() if not fact.get("verified")]
    proof = part.get("pin_order_proof")
    if isinstance(proof, dict) and not proof.get("verified"):
        questions.append({"part": part_id, "fact": "pin_order", "assumed": part.get("pin_order"),
                          "why_it_matters": "a pin order read wrong reverses a supply or swaps a signal",
                          "source": proof.get("source", "")})
    return questions


def unverified(part_ids, project: Path = None) -> list:
    """Every fact nobody has checked, across these parts — the design's real open questions."""
    return [question for part_id in part_ids for question in open_questions_of(any_record(part_id, project), part_id)]


#: Vendors to research in, in order, when a project's brief does not say. DFRobot first because
#: its wiki carries a pinout table and a dimension drawing for every module; Seeed next for the
#: same reason. A project overrides this in `.spark/project.json` → `prefer`.
DEFAULT_VENDOR_ORDER = ("dfrobot", "seeed")


def vendor_order(project=None):
    """The vendors to research in, from the project's brief, else the default."""
    if project:
        brief = Path(project) / ".spark" / "project.json"
        if brief.is_file():
            try:
                prefer = json.loads(brief.read_text()).get("prefer")
            except ValueError:
                prefer = None
            if isinstance(prefer, list) and prefer and all(isinstance(v, str) for v in prefer):
                return tuple(v.lower() for v in prefer)
    return DEFAULT_VENDOR_ORDER


#: Everything research has ever read, chosen or not, datasheet and photo saved beside it (PO,
#: 2026-09-29: "even if we end up not using that part, keep it — we want a good database in
#: time"). A `parts/` record must pass the contract; a catalog record only has to say what it is.
CATALOG = Path(__file__).resolve().parent.parent / "catalog"
CATALOG_KEYS = ("schema", "id", "name", "kind")
#: What `--fetch` keeps: the sources worth having when the link rots.
KEEPABLE = (".pdf", ".jpg", ".jpeg", ".png", ".webp", ".svg")

#: Where a person's kept sources live (P61, P62a): ONE store outside the plugin — a published plugin
#: cannot carry vendor documents — shared by every project, each file under its own checksum so a
#: record finds it without searching. The PO chose the place on 2026-10-02; its backup is the
#: machine's. A record holds the pointer (`documents`), never the file.
STORE = Path.home() / ".local" / "share" / "spark" / "sources"

#: An http(s) URL inside prose: "Table 3 of https://x/ds.pdf (rev 7)" cites https://x/ds.pdf. A
#: parenthesis belongs to the URL when it is balanced — DFRobot names files "DFR (1).pdf" — and
#: to the prose when it closes one the URL never opened.
URL = re.compile(r"https?://[^\s,;\]>'\"]+")


def _url_in_prose(url):
    url = url.rstrip(".:")
    while url.endswith(")") and url.count(")") > url.count("("):
        url = url[:-1].rstrip(".:")
    return url


def catalog_records():
    """Every catalog record that parses and says what it is, by id; the rest are named as broken."""
    records, broken = {}, []
    for path in sorted(CATALOG.glob("*" + DEFINITION_SUFFIX)):
        record = _parse(path)
        if isinstance(record, dict) and all(record.get(key) for key in CATALOG_KEYS):
            records[path.stem] = record
        else:
            broken.append(path.name)
    return records, broken


def catalog_matches(words):
    """The catalog records matching every word, the way `need` matches — researched before, unbuilt."""
    return [dict(record, id=part_id) for part_id, record in catalog_records()[0].items()
            if _matches(words, part_id, record)]


def record_home(part_id, project=None):
    """Where a record lives — a parts/ on the search path, or the catalog — or None."""
    for directory in search_path(project) + [CATALOG]:
        if (directory / (part_id + DEFINITION_SUFFIX)).is_file():
            return directory
    return None


def any_record(part_id, project=None):
    """The record wherever it lives: validated from a parts/, raw from the catalog (a draft is allowed)."""
    home = record_home(part_id, project)
    if home == CATALOG:
        return _parse(home / (part_id + DEFINITION_SUFFIX)) or {}
    return load(part_id, project)


#: EXIF's pointer to the GPS block, and the size in bytes of each EXIF value type (TIFF 6.0).
GPS_BLOCK_TAG = 0x8825
EXIF_TYPE_BYTES = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8}


def without_location(payload):
    """
    A JPEG with its GPS block emptied, and whether it had one (P75). A phone writes where a photo
    was taken into it — all five of irrigation's did — and a person photographing a module at home
    for /spark:identify must not publish their address by committing the file. Emptied in place:
    every GPS value zeroed and the block's entry count set to 0, so nothing else in the file moves.
    """
    start = payload.find(b"Exif\x00\x00")
    if not payload.startswith(b"\xff\xd8") or start < 0:
        return payload, False
    data, tiff = bytearray(payload), start + 6
    order = "<" if data[tiff:tiff + 2] == b"II" else ">"

    def read(fmt, at):
        return struct.unpack_from(order + fmt, data, tiff + at)

    def zero(at, size):
        if tiff + at + size > len(data):
            raise struct.error("a value past the end of the file")
        data[tiff + at:tiff + at + size] = bytes(size)

    try:
        first = read("I", 4)[0]
        pointers = [read("I", first + 10 + 12 * i)[0] for i in range(read("H", first)[0])
                    if read("H", first + 2 + 12 * i)[0] == GPS_BLOCK_TAG]
        if not pointers:
            return payload, False
        block, entries = pointers[0], read("H", pointers[0])[0]
        for i in range(entries):
            _, kind, count, offset = read("HHII", block + 2 + 12 * i)
            if EXIF_TYPE_BYTES.get(kind, 1) * count > 4:
                zero(offset, EXIF_TYPE_BYTES.get(kind, 1) * count)
        zero(block, 2 + 12 * entries + 4)
    except struct.error:
        return payload, False
    return bytes(data), True


def keep_in_store(payload, name):
    """Put a file in the store under its checksum and return the checksum (P62a) — a photo without its location (P75)."""
    if name.lower().endswith((".jpg", ".jpeg")):
        payload = without_location(payload)[0]
    digest = hashlib.sha256(payload).hexdigest()
    (STORE / digest).mkdir(parents=True, exist_ok=True)
    (STORE / digest / name).write_bytes(payload)
    return digest


#: The unit a fact's name ends in, as a datasheet prints it.
UNIT_PRINTED = {"_v": r"(?<![A-Za-z])V(?![A-Za-z])", "_mv": r"mV", "_a": r"(?<![A-Za-z])A(?![A-Za-z])",
                "_ma": r"mA", "_ua": r"(µA|uA)", "_nm": r"nm", "_deg": r"(°|deg)", "_mm": r"mm",
                "_ohms": r"(Ω|ohm|k)", "_hz": r"[kM]?Hz", "_c": r"°C", "_mw": r"mW"}
#: What a datasheet calls a fact spark names its own way; the name's own words are always tried too.
DATASHEET_SAYS = {"max_continuous_current": ["dc forward current", "continuous current"],
                  "forward_voltage": ["forward voltage"], "forward_voltage_max": ["forward voltage"],
                  "peak_wavelength": ["peak wavelength", "wavelength at peak", "λpeak"], "viewing_angle": ["viewing angle"],
                  "deep_sleep_current": ["deep-sleep", "deep sleep"], "supply_voltage": ["supply voltage"]}
TABLE_ROW = re.compile(r"\S\s{3,}\S.*\S\s{3,}\S")
STANDALONE_NUMBER = re.compile(r"(?<![\w.=])\d+(\.\d+)?(?![\w.])")
SECTION = re.compile(r"^\s*(Table\s+\d+.*|[A-Z]{2,}[A-Z0-9 /&,\-]{4,}.*|\d+(\.\d+)+\s+[A-Z].{3,60})$")


def scan_datasheet(pages, wanted, labels=None):
    """
    Each wanted fact's lines in a datasheet, read page by page and STOPPED on the page where every
    fact is FOUND (P80): a run that printed a whole datasheet paid for it on every later turn, while
    the facts sat on one page. FOUND is a table row with the label, a standalone number, and the
    unit on the row or in a column header above; a prose bullet never is — the S3 overview's "7 uA"
    taken for the table is the P63 misreading. LABEL ONLY shows the next two lines; NOT FOUND names
    the words tried. `pages` yields (number, text); `labels` adds words per fact.
    """
    plan = {}
    for fact in wanted:
        suffix = next((end for end in sorted(UNIT_PRINTED, key=len, reverse=True) if fact.endswith(end)), "")
        stem = fact[:-len(suffix)] if suffix else fact
        words = list(dict.fromkeys(DATASHEET_SAYS.get(stem, []) + [stem.replace("_", " ")] + list((labels or {}).get(fact, []))))
        plan[fact] = (words, re.compile(UNIT_PRINTED[suffix]) if suffix else None)
    found = {fact: {"status": "NOT FOUND", "hits": [], "tried": words} for fact, (words, _) in plan.items()}
    for number, text in pages:
        lines, section = text.splitlines(), None
        for index, line in enumerate(lines, 1):
            # A heading names a table or a section; a table row that happens to start in capitals does not.
            section = line.strip() if SECTION.match(line) and not TABLE_ROW.search(line) else section
            for fact, (words, unit) in plan.items():
                if not any(word in line.lower() for word in words):
                    continue
                above = "\n".join(lines[max(0, index - 21):index - 1])
                has_unit = unit is None or unit.search(line) or re.search(r"\(\s*" + unit.pattern + r"\s*\)", above)
                if TABLE_ROW.search(line) and STANDALONE_NUMBER.search(line) and has_unit:
                    entry = found[fact]
                    if entry["status"] != "FOUND":
                        entry["status"], entry["hits"] = "FOUND", []
                    entry["hits"].append((number, index, section, re.sub(r"\s{3,}", " | ", line.strip())))
                elif found[fact]["status"] == "NOT FOUND":
                    # A wrapped cell puts a row's label between its values: show the line above too.
                    above_line = [previous.strip() for previous in lines[max(0, index - 3):index - 1] if previous.strip()][-1:]
                    below = [following.strip() for following in lines[index:index + 6] if following.strip()][:2]
                    found[fact] = dict(found[fact], status="LABEL ONLY",
                                       hits=[(number, index, section, " // ".join(above_line + [line.strip()] + below))])
        if all(entry["status"] == "FOUND" for entry in found.values()):
            break
    return found


def datasheet_pages(path, command):
    """(number, text) per page of a PDF, as the pdf-text tool lays it out — one page at a time, on demand."""
    import subprocess
    number = 1
    while True:
        done = subprocess.run(list(command) + ["-layout", "-f", str(number), "-l", str(number), str(path), "-"],
                              capture_output=True, text=True)
        if done.returncode != 0:
            return
        yield number, done.stdout
        number += 1


def read_datasheet(path, wanted, labels=None, project=None):
    """Print what `scan_datasheet` found, with the pages read; EXIT_OK only when every fact was FOUND."""
    import tools
    try:
        reader = tools.find("pdf-text", project)
    except tools.ToolProblem as missing:
        print("parts.py: --read: %s" % missing, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    read = []
    def counted():
        for page in datasheet_pages(path, reader.command):
            read.append(page[0])
            yield page
    found = scan_datasheet(counted(), wanted, labels)
    for fact, entry in found.items():
        if entry["status"] == "NOT FOUND":
            print("%-28s NOT FOUND — tried: %s" % (fact, ", ".join(entry["tried"])))
        for page, line, section, text in entry["hits"][:3]:
            print("%-28s %-10s p%d:%d  [%s]  %s" % (fact, entry["status"], page, line, section or "no heading", text[:220]))
    missing = [fact for fact, entry in found.items() if entry["status"] != "FOUND"]
    print("read %d of the document's pages, %s" % (len(read), "stopping where the last fact was found" if not missing
                                                    else "%d fact(s) not on a table row: read those pages as images" % len(missing)))
    return EXIT_OK if not missing else EXIT_INVALID


def keep_local(path, url=None):
    """
    Put a file you already have into the store and return the `documents` entry that points at it
    (P62b). The WROOM-1 v1.1 datasheet exists only as a kept file — its URL now serves v1.8 — so
    fetching can never bring it in; an import can. `url` is where it came from, if anyone knows.
    """
    path = Path(path)
    return {"url": url, "sha256": keep_in_store(path.read_bytes(), path.name), "file": path.name,
            "retrieved": datetime.date.today().isoformat(), "title": None, "version": None}


def records_with_documents(project=None):
    """(owner id, record) for every record that can point at a document: parts, catalog, boards."""
    import boards
    board_dirs = ([Path(project) / "boards"] if project else []) + [boards.LIBRARY]
    paths = [directory / (part_id + DEFINITION_SUFFIX) for directory in search_path(project) + [CATALOG]
             if directory.is_dir() for part_id in sorted(p.stem for p in directory.glob("*" + DEFINITION_SUFFIX))]
    paths += [path for directory in board_dirs if directory.is_dir()
              for path in sorted(directory.glob("*" + DEFINITION_SUFFIX)) if path.name not in boards.NOT_A_BOARD]
    for path in paths:
        record = _parse(path)
        if isinstance(record, dict) and record.get("documents"):
            yield path.stem, record


def citing(record, keys, url, where=""):
    """
    (field, locator) for every object in the record that rests on this document: by one of `keys` —
    the names THIS record gives the same file — or by its URL. A record that does not hold the file
    has no key for it, and an object with no `cites` names no document, so neither can match.
    """
    found = []
    for name, value in (record.items() if isinstance(record, dict) else []):
        here = "%s.%s" % (where, name) if where else name
        if not isinstance(value, dict):
            continue
        cited = (value.get("cites") or {}).get("document")
        if cited is not None and cited in keys:
            found.append((here, value["cites"].get("at") or "no page given"))
        elif url and isinstance(value.get("source"), str) and url in value["source"]:
            found.append((here, "cites its URL"))
        else:
            found += citing(value, keys, url, here)
    return found


def find_kept(words, project=None):
    """
    Every kept document matching every word — where it is in the store, present or MISSING, and
    each fact that rests on it — read from the records alone: no network (P62b). A researcher runs
    this BEFORE fetching: one fetch in five repeated one already made (P61).
    """
    wanted = [word.lower() for word in words]
    lines = []
    for owner, record in records_with_documents(project):
        for key, entry in record["documents"].items():
            said = " ".join(str(part) for part in (owner, key, entry.get("file"), entry.get("title"),
                                                   entry.get("url"), entry.get("version"))).lower()
            if not all(word in said for word in wanted):
                continue
            path = STORE / str(entry.get("sha256")) / str(entry.get("file"))
            lines.append("%s %s: %s %s" % (owner, key, entry.get("title") or entry.get("file"),
                                           entry.get("version") or "(version not read)"))
            lines.append("    %s  %s" % (path, "present" if path.is_file() else "MISSING"))
            for other, other_record in records_with_documents(project):
                same_file = {name for name, held in other_record["documents"].items()
                             if isinstance(held, dict) and held.get("sha256") == entry.get("sha256")}
                for field, locator in citing(other_record, same_file, entry.get("url")):
                    lines.append("    cited by %s %s — %s" % (other, field, locator))
    # The store itself: a file another project kept, or an interrupted run left, is still kept (P80).
    cited = {str(entry.get("sha256")) for _, record in records_with_documents(project)
             for entry in record["documents"].values() if isinstance(entry, dict)}
    for path in sorted(STORE.glob("*/*")) if STORE.is_dir() else []:
        if path.parent.name not in cited and all(word in path.name.lower() for word in wanted):
            lines.append("%s: kept; no record here cites it" % path.name)
            lines.append("    %s  present" % path)
    return lines


def document_key(name, taken):
    """A short, unique name for a document in a record: its file name's stem, made plain."""
    stem = re.sub(r"[^a-z0-9]+", "-", name.rsplit(".", 1)[0].lower()).strip("-") or "document"
    key, number = stem, 2
    while key in taken:
        key, number = "%s-%d" % (stem, number), number + 1
    return key


def fetch_documents(part_id, project=None, fetch=None):
    """
    Download every cited datasheet or image into the store and point at each from the record's
    `documents`: its URL, checksum, file name and the date it was fetched — `title` and `version`
    stay null until someone reads them, because a version is what the document PRINTS, not a
    guess (P61). `fetch(url) -> bytes or None` is a parameter for the tests.
    """
    home = record_home(part_id, project)
    if home is None:
        raise PartError("no record called %r to fetch for" % part_id)
    path = home / (part_id + DEFINITION_SUFFIX)
    record = json.loads(path.read_text())
    documents = dict(record.get("documents") or {})
    known = {entry.get("url") for entry in documents.values()}
    for url in cited_urls(record):
        bare = url.split("?")[0]
        if not bare.lower().endswith(KEEPABLE) or url in known:
            continue
        payload = (fetch or _download)(url)
        if payload is not None:
            name = urllib.parse.unquote(bare.rsplit("/", 1)[-1]) or "document"
            documents[document_key(name, documents)] = {
                "url": url, "sha256": keep_in_store(payload, name), "file": name,
                "retrieved": datetime.date.today().isoformat(), "title": None, "version": None}
    record["documents"] = documents
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    return documents


def _parse(path):
    try:
        return json.loads(path.read_text())
    except ValueError:
        return None


def _download(url):
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "spark"}), timeout=30).read()
    except Exception:  # noqa: BLE001 — a source that does not answer is simply not kept
        return None


def promote(part_id, project, to=None):
    """
    Move a record one step along its life: catalog -> the project's parts/ (to build with; it must
    then pass the contract), or the project's parts/ -> the plugin's library (for every later
    project). Its folder (a simulation chip) and its photo travel with it; its documents are
    pointers into the store and need nothing moved. Nothing is ever overwritten. Returns the path.
    """
    import shutil
    home = record_home(part_id, project)
    if home is None:
        raise PartError("no record called %r to promote" % part_id)
    to = Path(to) if to else (Path(project) / "parts" if home == CATALOG else LIBRARY)
    target = to / (part_id + DEFINITION_SUFFIX)
    if target.exists():
        raise PartError("%s exists; a promotion never overwrites" % target)
    to.mkdir(parents=True, exist_ok=True)
    shutil.copy2(home / (part_id + DEFINITION_SUFFIX), target)
    if (home / part_id).is_dir():
        shutil.copytree(home / part_id, to / part_id, dirs_exist_ok=True)
    photo = json.loads(target.read_text()).get("photo")
    if isinstance(photo, str) and project and (Path(project) / photo).is_file() and not (to / photo).exists():
        (to / photo).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path(project) / photo, to / photo)
    return target


def sellers(project=None):
    """
    Where the person buys, local first, from the project's brief — or nothing, which the
    researcher reports as "no sellers named" rather than choosing a shop for them.
    """
    if project:
        brief = Path(project) / ".spark" / "project.json"
        if brief.is_file():
            try:
                named = json.loads(brief.read_text()).get("sellers")
            except ValueError:
                named = None
            if isinstance(named, list) and named and all(isinstance(v, str) for v in named):
                return tuple(v.lower() for v in named)
    return ()


def _matches(words, part_id, record):
    haystack = " ".join([part_id, record.get("name") or "", record.get("kind") or "",
                         " ".join(record.get("also_known_as") or [])]).lower()
    return all(word.lower() in haystack for word in words)


def need(words, project=None):
    """
    The records matching every word — in id, name, kind or an alias — so what exists is known
    before anything is researched. Backlog R11: the RC car wrote three records by hand because
    nothing looked, and "nothing looked" was the first gap its diary named (G1).
    """
    found, drafts = [], []
    for part_id in available(project):
        try:
            record = load(part_id, project)
        except PartError:
            # A record still being filled in — research writes a skeleton first — must not stop
            # the search for everyone: `--need` died on a researcher's draft while five ran (I3).
            # Named as a draft, matched by its id alone, never returned as usable.
            if _matches(words, part_id, {}):
                drafts.append(part_id)
            continue
        if _matches(words, part_id, record):
            found.append(dict(record, id=part_id))
    return found, drafts


def skeleton(part_id, kind, vendor=None):
    """
    A record with every field present and nothing guessed: what research fills in.

    Nulls are facts nobody has recorded, and `validate` refuses the file until they are — the
    same rule `init` applies to the rules file. A fact is `verified: true` only when its value
    is the vendor's own text at the cited URL; read off an image, scaled, inferred or computed,
    it is `verified: false` with `why_it_matters` (the rule `commands/research.md` states).
    """
    return {
        "schema": 1, "id": part_id, "name": None, "kind": kind,
        "//": ("Written by /spark:research. A null is a fact nobody has recorded. verified: true = the "
               "vendor's own text at the cited URL; read off an image, inferred or computed = false."),
        "vendor": vendor, "sku": None, "sources": [],
        "needs": [], "power": [], "unused_pins": [], "pin_order": [], "footprint": None,
        "body_mm": {"width": None, "height": None, "verified": False, "source": None,
                    "why_it_matters": "every placement is arranged around it"},
        "facts": {}, "host_requirements": [],
        "sourcing": [],
        "//sourcing": ("Where it can be bought, one entry per listing actually fetched: "
                       "{seller, url, price_czk, checked}. Local sellers first, from the brief."),
    }


def cited_urls(record):
    """
    Every http(s) URL the record cites: in its `sources` — a list, or a dict of them, as four
    library records keep it — and in each fact's own source, wherever in the sentence it sits.
    Read only as a list of strings that START with http, this saw no URL at all in any of the
    eight library and board records (both P62 lenses, 2026-10-02).
    """
    sources = record.get("sources") or []
    texts = list(sources.values()) if isinstance(sources, dict) else list(sources)
    texts += [fact.get("source") for fact in (record.get("facts") or {}).values() if isinstance(fact, dict)]
    urls = [url for text in texts if isinstance(text, str) for url in URL.findall(text)]
    return list(dict.fromkeys(_url_in_prose(url) for url in urls))


def reachable(url):
    """Whether a URL answers at all. A hallucinated source is the one lie research tells easily."""
    import urllib.request
    try:
        request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "spark"})
        with urllib.request.urlopen(request, timeout=10) as answer:
            return 200 <= answer.status < 400
    except Exception:  # noqa: BLE001 — any failure to reach it is the same answer here
        return False


def sources_resolve(record, fetch=reachable):
    """(url, reachable) for every cited URL. `fetch` is a parameter so a test needs no network."""
    return [(url, fetch(url)) for url in cited_urls(record)]


def pull_conflicts(part):
    """
    A pull-down the board adds against the module's own pull-up, said with its arithmetic (P81, B11).
    The L9110S states 10 k pull-ups to VCC on its inputs and asked the board for 10 k pull-downs "so
    both are held low": a divider at half the supply, above its 2.5 V input threshold on a 6 V pack.
    The record's note said so; no output did. Quiet when the pin stays under the input-high threshold
    across the module's whole supply range.
    """
    facts = part.get("facts") or {}
    value = lambda name: (facts.get(name) or {}).get("value")
    pull_up, high, supply = value("onboard_input_pullups_ohms"), value("input_high_threshold_v"), value("supply_range_v")
    if not isinstance(pull_up, (int, float)):
        return []
    said = []
    for host_part in part.get("host_parts") or []:
        if host_part.get("kind") != "pulldown" or not isinstance(host_part.get("ohms"), (int, float)):
            continue
        ratio = host_part["ohms"] / (pull_up + host_part["ohms"])
        line = ("%s: the board's %g ohm pull-down against the module's own %g ohm pull-up to its supply "
                "holds the pin at %.2g of the supply" % (host_part["pin"], host_part["ohms"], pull_up, ratio))
        if isinstance(high, (int, float)):
            crossover = high / ratio
            if isinstance(supply, list) and len(supply) == 2 and supply[1] < crossover:
                continue
            if isinstance(supply, list) and len(supply) == 2:
                line += " (%g V to %g V over its %g-%g V range)" % (supply[0] * ratio, supply[1] * ratio, *supply)
            line += (", so it idles HIGH, not low, on any supply above %g V (input-high threshold %g V)"
                     % (crossover, high))
        if value("input_low_threshold_v") is None:
            line += "; the module's input-low threshold is not recorded, so below that the level is undefined"
        said.append(line)
    return said


def describe(part):
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
    for conflict in pull_conflicts(part):
        lines.append("\n  CONFLICT: %s" % conflict)
    return "\n".join(lines)


def _row(part_id, kind, rest):
    return "  %-28s %-14s %s" % (part_id, kind, rest)


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
    what.add_argument("--need", nargs="+", metavar="WORD",
                      help="what exists for a need, before researching: words matched in id, name, kind, alias")
    what.add_argument("--skeleton", metavar="PART", help="write a record to fill in, to the project's parts/")
    what.add_argument("--sources", metavar="PART", help="fetch every URL a record cites; a source that does not answer is named")
    what.add_argument("--fetch", metavar="PART", help="download the datasheets and images a record cites, into your store")
    what.add_argument("--keep", metavar="FILE", help="put a file you already have into your store; prints its documents entry")
    what.add_argument("--read", metavar="PDF", help="read a datasheet page by page and stop where every --want fact is on a table row")
    what.add_argument("--kept", nargs="+", metavar="WORD",
                      help="find a kept document by every word, with no network, and every fact resting on it")
    what.add_argument("--promote", metavar="PART", help="catalog → the project's parts/, or the project's parts/ → the plugin's library")
    what.add_argument("--catalog", action="store_true", help="every record research has kept, chosen or not")
    parser.add_argument("--kind", help="with --skeleton: the part's kind (motor-driver, sensor, regulator, …)")
    parser.add_argument("--vendor", help="with --skeleton: who makes it")
    parser.add_argument("--url", help="with --keep: where the file came from, if anyone knows")
    parser.add_argument("--want", nargs="+", metavar="FACT", help="with --read: the facts to find, named as records name them (forward_voltage_v …)")
    parser.add_argument("--label", action="append", metavar="FACT=WORD|WORD", help="with --read: extra words a datasheet uses for a fact")
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
                    where = "project" if definition_path(part["id"], project).parent != LIBRARY else "library"
                    print(_row(part["id"], part["kind"], "%-9s %s" % (where, part["name"])))
        elif args.show:
            part = any_record(args.show, project)
            print(json.dumps(part, indent=2) if args.json else describe(part))
        elif args.signals:
            print(json.dumps({"signals": signals_for(args.signals, project)}, indent=2))
        elif args.need:
            found, drafts = need(args.need, project)
            known = [p for p in catalog_matches(args.need) if p["id"] not in drafts and p["id"] not in {q["id"] for q in found}]
            order = ", ".join(vendor_order(project))
            shops = ", ".join(sellers(project)) or "none named in the brief"
            if args.json:
                print(json.dumps({"tool": "parts", "need": args.need, "vendor_order": list(vendor_order(project)),
                                  "found": [{"id": p["id"], "kind": p["kind"], "name": p["name"]} for p in found],
                                  "drafts": drafts,
                                  "catalog": [{"id": p["id"], "kind": p["kind"], "name": p["name"]} for p in known]}, indent=2))
            elif found or drafts or known:
                for part in found:
                    print(_row(part["id"], part["kind"], part["name"]))
                for part_id in drafts:
                    print(_row(part_id, "(draft)", "does not yet meet the contract — being filled in"))
                for part in known:
                    print(_row(part["id"], part["kind"], "%s  [catalog: researched before; `--promote %s --project .` builds with it]"
                               % (part["name"], part["id"])))
            else:
                print("  nothing in the library matches %r.\n  Research it: /spark:research \"%s\"  — vendors in order: %s; sellers: %s"
                      % (" ".join(args.need), " ".join(args.need), order, shops))
        elif args.skeleton:
            if not project or not args.kind:
                print("parts.py: --skeleton needs --project (the record belongs to a project's parts/) "
                      "and --kind", file=sys.stderr)
                return EXIT_INVALID
            target = project / "parts" / (args.skeleton + DEFINITION_SUFFIX)
            if target.exists():
                print("parts.py: %s exists; fill it in, do not overwrite it" % target, file=sys.stderr)
                return EXIT_INVALID
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(skeleton(args.skeleton, args.kind, args.vendor), indent=2, ensure_ascii=False) + "\n")
            print("  wrote %s — every null is a fact to record; `parts.py --validate --project .` says what is missing" % target)
        elif args.keep:
            if args.keep.lower().endswith((".jpg", ".jpeg")) and without_location(Path(args.keep).read_bytes())[1]:
                print("  removed the location (EXIF GPS) from %s before keeping it" % Path(args.keep).name, file=sys.stderr)
            print(json.dumps(keep_local(args.keep, args.url), indent=2, ensure_ascii=False))
        elif args.read:
            labels = {}
            for given in args.label or []:
                fact, _, words = given.partition("=")
                labels[fact] = [word.strip().lower() for word in words.split("|") if word.strip()]
            return read_datasheet(args.read, args.want or [], labels, project)
        elif args.kept:
            found = find_kept(args.kept, project)
            print("\n".join(found) if found else "nothing kept matches %s — fetch it, or --keep a file "
                                                  "you have" % " ".join(args.kept))
            return EXIT_OK if found else EXIT_INVALID
        elif args.fetch:
            kept = fetch_documents(args.fetch, project)
            for entry in kept.values():
                print("  %s/%s  <-  %s" % (entry["sha256"][:12], entry["file"], entry["url"]))
            if not kept:
                print("  %s cites no datasheet or image URL to keep" % args.fetch)
        elif args.promote:
            if not project:
                print("parts.py: --promote needs --project", file=sys.stderr)
                return EXIT_INVALID
            print("  promoted to %s" % promote(args.promote, project))
        elif args.catalog:
            records, broken = catalog_records()
            for part_id, record in records.items():
                print(_row(part_id, record["kind"], record["name"]))
            for name in broken:
                print(_row(name, "BROKEN", "does not parse, or names no schema/id/name/kind"))
            print("  %d record(s), %d broken" % (len(records), len(broken)))
        elif args.sources:
            record = any_record(args.sources, project)
            answers = sources_resolve(record)
            if args.json:
                print(json.dumps({"tool": "parts", "part": args.sources,
                                  "sources": [{"url": u, "reachable": ok} for u, ok in answers]}, indent=2))
            else:
                for url, ok in answers:
                    print("  %s  %s" % ("ok  " if ok else "NO  ", url))
                if not answers:
                    print("  %s cites no URL — every fact rests on prose sources a person has to find" % args.sources)
            return EXIT_INVALID if any(not ok for _, ok in answers) else EXIT_OK
        elif args.unverified:
            questions = unverified(args.unverified, project)
            if args.json:
                print(json.dumps(questions, indent=2))
            elif not questions:
                print("  everything these parts claim has been checked.")
            else:
                print("  %d thing(s) nobody has checked:\n" % len(questions))
                for question in questions:
                    print("  %s.%s = %s" % (question["part"], question["fact"], question["assumed"]))
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
                    print("  %-28s %s" % (one["part"], "ok" if not one["problems"] else "%d problem(s)" % len(one["problems"])))
                    for problem in one["problems"]:
                        print("      - %s" % problem)
            return EXIT_INVALID if any(c["problems"] for c in checked) else EXIT_OK
    except PartError as broken:
        print("parts.py: %s" % broken, file=sys.stderr)
        return EXIT_INVALID
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
