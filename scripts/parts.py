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
import contextlib
import datetime
import hashlib
import json
import re
import shlex
import struct
import sys
import urllib.parse
from collections import namedtuple
from pathlib import Path

#: Parts ship with the plugin, and a project may keep its own in `parts/`. A project's own wins,
#: for the same reason a board definition does: what you verified yourself must not be replaced.
LIBRARY = Path(__file__).resolve().parent.parent / "parts"
DEFINITION_SUFFIX = ".json"

SUPPORTED_SCHEMA = 1

REQUIRED_KEYS = ("schema", "id", "name", "kind", "needs")

#: Each entry in `facts` must answer all three, or it is an opinion with a number attached.
REQUIRED_FACT_KEYS = ("value", "verified", "source")
#: Fields a record no longer holds, each with where that fact lives now (P95, W16). Owning one is the person's
#: fact, not the part's: it is a drawer entry, and a photo of the one they own goes on that entry.
RETIRED = {"owned": "what you own is a drawer entry — /spark:drawer, `parts.py --drawer-set`",
           "photo": "a photo of the one you own goes on its drawer entry's `photos`, kept with `parts.py --keep`"}

#: What a part does (§5.6): the PO's 13 verbs. `drive` is the driver (an L9110S), `move` the thing driven (a motor).
VERBS = ("sense", "input", "indicate", "sound", "move", "drive", "power", "keep-time", "store", "compute",
         "communicate", "connect", "mount")

#: A kind that says by itself what a part does (§5.6). A `sensor` or a `connector` does not: theirs is written
#: once, through `--function-set`, with a dry run.
KIND_FUNCTION = {"rtc": ("keep-time", "rtc"), "regulator": ("power", "regulator"), "button": ("input", "button"),
                 "indicator": ("indicate", "light"), "mosfet-driver": ("drive", "load-switch"),
                 "motor-driver": ("drive", "motor-dc"), "audio-amplifier": ("sound", "amplifier"),
                 "audio": ("sound", "audio-player"), "rangefinder": ("sense", "distance"), "servo": ("move", "servo"),
                 "board": ("compute", "microcontroller")}


def function_of(record, board=False):
    """What a record does (§5.6): its own `function`, else what its kind says, else nothing."""
    if record.get("function") and not function_problems(record):
        return record["function"]
    kind = "board" if board else record.get("kind")
    said = KIND_FUNCTION.get(kind) if isinstance(kind, str) else None
    return [{"does": said[0], "what": said[1]}] if said else []


def function_problems(record):
    """A `function` that is not [{"does": one of the 13 verbs, "what": words}] — absent is fine: the kind may say it."""
    function = record.get("function")
    if function is None or (isinstance(function, list) and function and all(
            isinstance(f, dict) and set(f) <= {"does", "what"} and f.get("does") in VERBS
            and isinstance(f.get("what"), str) and f["what"].strip() for f in function)):
        return []
    return ['function is [{"does": one of %s, "what": words}]' % ", ".join(VERBS)]


def aliases(record):
    """A record's other names (`also_known_as`) — only those that are words; a value that is no list names nothing (§5.5)."""
    said = record.get("also_known_as")
    return [alias for alias in said if isinstance(alias, str)] if isinstance(said, list) else []


#: The facts the chain reads from a part record (§5.4): absent, the record owes them, and no build can place it.
CHAIN_FACTS = ("footprint", "pin_order", "pin_order_proof", "body_mm", "simulation")


def _absent(key, value):
    if key == "body_mm":
        return not (isinstance(value, dict) and all(isinstance(value.get(side), (int, float)) for side in ("width", "height")))
    return value is None or value == [] or value == {} or value == ""


def owes(record):
    """What a part record owes (§5.4): each required key missing, and each fact the chain reads that is absent."""
    return ([key for key in REQUIRED_KEYS if key not in record] +
            [key for key in CHAIN_FACTS if _absent(key, record.get(key))])


def _about(problem, key):
    """Whether a validate problem is about this key — it starts with it, or says "no <key>" — rather than merely naming it."""
    return (problem.startswith((key + " ", key + ".", key + "[")) or problem == "missing required key %r" % key
            or re.search(r"\bno %s\b" % re.escape(key), problem) is not None)


def _shape_problems(check, record, path, what):
    """A check's problems — or, when the record is too malformed for the check to read, one saying so (§5.4: never a traceback)."""
    try:
        return check(record, path)
    except (AttributeError, TypeError, KeyError, ValueError) as wrong:
        return ["does not meet the %s's shape (%s)" % (what, wrong)]


def broken_problems(record, path):
    """What is wrong with a part record beyond what it owes (§5.4): `validate`'s problems that name no owed key."""
    owed = owes(record)
    return [problem for problem in _shape_problems(validate, record, path, "part record")
            if not any(_about(problem, key) for key in owed)]


def audit(project=None):
    """
    Every record in every layer — the catalog included — every drawer link, and each record a link reaches in the person's
    other projects, walked once (§5.4, P89): per layer how many are current, owe facts, or are broken; which say nothing
    of what they do (spark's layers and this project only); which entries point at nothing; which boards stop the chain at
    the footprint stage, their files holding no header geometry (C-7, P121).
    """
    import boards
    import drawer
    import emit_footprint
    walked = [("part", found, layer, path) for found, (layer, path) in store.records("parts", LIBRARY, project, drafts=True).items()]
    walked += [("board", found, layer, path) for found, (layer, path) in boards.records(project).items()]
    known, mine, seen = drawer.linkable(project), store.projects(), {row[3].resolve() for row in walked}
    dangling, linked = [], []
    for entry, said in drawer.entries().items():
        if not (isinstance(said.get("is"), dict) and said["is"]):
            continue
        where, path = drawer.resolve(said["is"], known)
        if where is None:
            dangling.append(entry)
        elif where in mine and path.resolve() not in seen:
            seen.add(path.resolve())
            linked.append((next(iter(said["is"])), path.stem, where, path))
    counts, owed, broken, silent, stops = {}, [], [], [], []
    for kind, found, layer, path in walked + linked:
        row = counts.setdefault(layer, {"current": 0, "owed": 0, "broken": 0})
        record = _parse(path)
        wrong = (["does not parse as a JSON object"] if not isinstance(record, dict) else
                 _shape_problems(boards.validate, record, path, "board definition") if kind == "board" else broken_problems(record, path))
        owing = [] if wrong or kind == "board" else owes(record)
        row["broken" if wrong else "owed" if owing else "current"] += 1
        if wrong:
            broken.append({"id": found, "layer": layer, "problems": wrong})
        elif owing:
            owed.append({"id": found, "layer": layer, "owes": owing})
        elif kind == "board" and emit_footprint.footprint_gaps(record):  # C-7: a board owes nothing, and may still stop the chain
            stops.append({"id": found, "layer": layer})
        if isinstance(record, dict) and not function_of(record, board=kind == "board") and (kind, found, layer, path) not in linked:
            silent.append(found)
    return counts, owed, broken, silent, dangling, stops


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

#: What a footprint may be (C-1, the council on PR #98): a footprinter's name — lower-case letters, digits, `_` and `.`, so
#: `pinrow5`, `jst_ph_3`, `0603`, `dip12_w15.24mm` — or a JLCPCB part, `jlcpcb:C2040`. The board is written with it as an
#: attribute's text, unescaped (P87, #19): a quote, a brace or a space in it would be code in `board.tsx`.
FOOTPRINT_NAME = re.compile(r"[a-z0-9][a-z0-9_.]*|jlcpcb:C[0-9]+")
#: What a silkscreen may not hold (C-1): the board keeps it in a `{/* … */}` comment, which `*/` ends, and `"` ends a string.
ENDS_THE_COMMENT = ("*/", '"')

#: Why a record's id must be a plain key (`store.PLAIN`; P87): `validate` refuses a record named otherwise, and `--skeleton`
#: refuses to write one, so nobody is handed a file every reader refuses.
NOT_A_PLAIN_ID = ("id is %r, but an id is a plain key — lower-case letters, digits and - (led-red-5mm): files are named by it, "
                  "and the board names the part after it in code")

#: What ends a line comment in a generated file: a line break — `\n` and `\r` end Python's `#`, and JavaScript's `//` ends
#: at U+2028 and U+2029 too — and U+0085, which editors read as one.
LINE_BREAKS = re.compile(r"[\r\n\u0085\u2028\u2029]")


def one_line(text):
    """
    Words a generated file keeps in a `#` or `//` line comment, on that one line (concern 1, P87's line-comment half): every
    line break a space. The pin map the firmware imports and the footprint the board imports carry a board's name, a role's
    note, a pad's alias, a board's id; a line break in one ended the comment, and what followed was code.
    """
    return LINE_BREAKS.sub(" ", str(text))


#: What a `needs` entry may ask a pin for. THE ONE DEFINITION — `assign_pins` imports it from
#: here rather than keeping its own, because it had its own and the two disagreed: a servo part
#: declaring `needs: ["pwm"]` validated as a good record and then made the pin assigner refuse
#: the whole design. The only way out was to delete a true fact about the part, which is a
#: contract punishing honesty.
#:
#: It lives in the lower module on purpose. A capability is a claim a PART makes, so the file
#: that validates parts owns the vocabulary and the file that consumes it follows.
CAPABILITIES = ("wake", "adc", "pwm")

from outcomes import EXIT_OK, EXIT_PROBLEMS as EXIT_INVALID, EXIT_COULD_NOT_RUN, EXIT_FOR, envelope, page  # noqa: E402
import store  # noqa: E402


class PartError(Exception):
    """A part definition that cannot be used, with the reason."""


#: What one operation found (§6.4.1): its `data`, the lines a person reads without --json, and the rest of the
#: envelope. A handler returns one; `main` prints it either way and exits by its status.
Answer = namedtuple("Answer", "data lines problems unchecked next truncated", defaults=(None, (), (), (), (), None))


class BadArgument(Exception):
    """An argument parts.py cannot run with: could-not-run, and with --json an envelope like any other answer."""


def _problem(subject, sentence, fix=None):
    return {"subject": subject, "sentence": sentence, "fix": fix}


def _cannot(sentence, fix=None):
    return {"sentence": sentence, "fix": fix}


def _with_project(project):
    return ["--project", str(project)] if project else []


def available(project: Path = None) -> list:
    return sorted(store.records("parts", LIBRARY, project))


def definition_path(part_id: str, project: Path = None) -> Path:
    found = store.records("parts", LIBRARY, project).get(part_id)
    if found:
        return found[1]
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
    if chip and not (isinstance(chip, str) and re.fullmatch(SELECTOR_SAFE, chip)):
        # the re-check's probes: a chip's name names its files (`../escape` reached outside the chip folder, and
        # stage_chips copied from there) and is written into wokwi.toml (`x"⏎[[chip]]` was a table of its own)
        return problems + ["simulation.wokwi.chip is %r, but a chip's name is a name — letters, digits and _ (vl6180x, "
                           "l9110s): its files beside the record are named by it, and wokwi.toml is written with it" % (chip,)]
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
    elif isinstance(part.get("id"), str) and not store.PLAIN.fullmatch(part["id"]):
        # P87's attribute half: `emit_board.component_name` capitalises the id's words and strips nothing, so the id is
        # what keeps `<chip name="…">` a name — a plain key, as every key of the store is
        problems.append(NOT_A_PLAIN_ID % part["id"])
    for key, now in RETIRED.items():
        if key in part:
            problems.append("%r is retired: %s — delete the key (W16)" % (key, now))
    if any(isinstance(listing, dict) and listing.get("seller") == "owned" for listing in part.get("sourcing") or []):
        problems.append('a `sourcing` entry {"seller": "owned"} is retired: %s — delete it (W16)' % RETIRED["owned"])

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
            elif printed is not None and any(mark in printed for mark in ENDS_THE_COMMENT):
                problems.append("%s[%d] printed %r holds %s — the generated board keeps the silkscreen in a comment, "
                                "which that would end; write it without" % (group, index, printed, " and ".join(
                                    mark for mark in ENDS_THE_COMMENT if mark in printed)))

    # A rail and a signal are names, as a pin is (P87's attribute half, after F11): a rail becomes the net the board is written
    # with — `to="net.<RAIL>"`, upper-cased — so a crafted one was code in board.tsx; a signal is what the pin map and the
    # firmware call a pin's job. Whole-string: `$` alone would let a trailing newline through.
    for index, supply in enumerate(part.get("power") or []):
        rail = supply.get("rail") if isinstance(supply, dict) else None
        if rail and not (isinstance(rail, str) and re.fullmatch(SELECTOR_SAFE, rail)):
            problems.append("power[%d] rail is %r, but a rail is a name — letters, digits and _ (ground, logic, motor, 5v): "
                            "the board is written with it as code" % (index, rail))
    for index, need in enumerate(part.get("needs") or []):
        signal = need.get("signal") if isinstance(need, dict) else None
        if signal and not (isinstance(signal, str) and re.fullmatch(SELECTOR_SAFE, signal)):
            problems.append("needs[%d] signal is %r, but a signal is a name — letters, digits and _ (MOTOR_IA, STATUS_LED): "
                            "the pin map and the board name it, and firmware is written against it" % (index, signal))

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

    # A footprint is the NAME of one: the board is written with it as the text of an attribute, so a number or
    # `true` would reach tscircuit as the footprint "5" or "True" — and a string with a quote in it would be code
    # (C-1). An absent one (`_absent`: null, no key, empty) is owed, not wrong, so only a value that is there is
    # checked; whether a name names a real footprint is a build's to say.
    footprint = part.get("footprint")
    if not (_absent("footprint", footprint) or (isinstance(footprint, str) and FOOTPRINT_NAME.fullmatch(footprint))):
        problems.append("footprint is %r, but a footprint is the name of one — a footprinter's, in lower-case letters, "
                        "digits, _ and . (pinrow5, jst_ph_3, dip12_w15.24mm), or a JLCPCB part, jlcpcb:C<number>: the "
                        "board is written with it as code" % (footprint,))

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
    problems.extend(function_problems(part))
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


CATALOG_KEYS = ("schema", "id", "name", "kind")
#: What `--fetch` keeps: the sources worth having when the link rots.
KEEPABLE = (".pdf", ".jpg", ".jpeg", ".png", ".webp", ".svg")

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
    """Every catalog record that parses, says what it is and keeps no seller listings, by id; the rest are named as broken."""
    records, broken = {}, []
    for path in sorted(store.place("catalog").glob("*" + DEFINITION_SUFFIX)):
        record = _parse(path)
        if not (isinstance(record, dict) and all(record.get(key) for key in CATALOG_KEYS)):
            broken.append(path.name)
        elif record.get("sourcing"):
            broken.append("%s — keeps seller listings (`sourcing`): prices and stock go stale before anyone "
                          "reads them; a catalog record keeps the part, not where to buy it (P83)" % path.name)
        else:
            records[path.stem] = record
    return records, broken


def catalog_matches(words):
    """The catalog records matching every word, the way `need` matches — researched before, unbuilt."""
    return [dict(record, id=part_id) for part_id, record in catalog_records()[0].items()
            if _matches(words, part_id, record)]


#: What a record leaves behind when it goes onto the shelf (§5.5): who owns one, their photos, where to buy it,
#: the options one project weighed. The shelf keeps the part, not one project's story of it.
SHELF_DROPS = ("owned", "photo", "photos", "sourcing", "alternatives")

#: Some of the facts a build reads from a part record (§5.7) — not its outline (`body_mm`) or its simulation stand-in: a
#: digest of these vouches for a record until one of them changes.
BUILD_FACTS = ("needs", "power", "unused_pins", "pin_order", "footprint", "host_parts")
#: Some of the facts a build reads from a board (§5.7) — not its pin roles or GPIO capabilities (`pin_roles`, `adc_gpio`,
#: `wake_capable_gpio`, which assign_pins reads).
BOARD_FACTS = ("pins", "power_pads", "physical")


def digest(record, facts=BUILD_FACTS):
    """The sha256 of the facts a build reads from a record — a part's by default, a board's with BOARD_FACTS (§5.7)."""
    shown = {key: record[key] for key in facts if key in record}
    return hashlib.sha256(json.dumps(shown, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def note_built(design):
    """
    A `built` line in the history when a listed project's board runs end to end (§5.7, §8 T): the board's and each part's
    digest, so a proof of an old pin order never vouches for a corrected one. A project not on the list keeps no history.
    """
    name = store.project_name(design.project)
    if name is None:
        return False
    with store.locked():
        return store.append_event({"event": "built", "project": name,
                                   "board": {"id": design.board["id"], "digest": digest(design.board, BOARD_FACTS)},
                                   "parts": [{"id": part["id"], "digest": digest(part)} for part in design.parts]})


def _shelf_copy(path, project_name=None, record=None):
    """
    What the shelf would hold of a record: filtered — and when it came from a project, which one and its digest (§5.5).
    `record` is the record as it would be written, when that is not yet what its file says (a dry run).
    """
    record = json.loads(Path(path).read_text()) if record is None else record
    copy = {key: value for key, value in record.items() if key not in SHELF_DROPS}
    if project_name:
        copy["based_on"] = {"project": project_name, "digest": digest(record)}
    return copy


def shelvable(path, project_name=None):
    """Whether a record may go onto the shelf: only one whose shelf copy meets the contract, or `--list` breaks in every project."""
    return not validate(_shelf_copy(path, project_name), Path(path))


def shelve(path, project_name=None):
    """
    Put a record onto the person's shelf, so every project finds it (§5.5): a filtered copy — that says which project
    it came from and that record's digest, when it came from one; a catalog record names none, since nothing reads it.
    Its folder (a simulation chip) travels with it. Returns whether the shelf changed — or None when the record does
    not meet the contract (a draft stays where it is).
    """
    path = Path(path)
    copy = _shelf_copy(path, project_name)
    if validate(copy, path):
        return None
    changed = store.write_json("shelf", path.stem, copy)
    if (path.parent / path.stem).is_dir():
        store.copy_folder("shelf", path.parent / path.stem, path.stem)
    return changed


def record_home(part_id, project=None):
    """The folder a record lives in — the nearest layer that has it, the catalog included — or None."""
    found = store.records("parts", LIBRARY, project, drafts=True).get(part_id)
    return found[1].parent if found else None


def any_record(part_id, project=None):
    """The record wherever it lives: validated from a parts/, raw from the catalog (a draft is allowed)."""
    home = record_home(part_id, project)
    if home == store.place("catalog"):
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


def keep_in_store(payload, name, dry_run=False):
    """
    Put a file in the store under its checksum, checked (§6.2), and return the checksum (P62a) — a photo without its
    location (P75). A dry run asks the name rule the real run enforces, so it refuses what the real run would refuse.
    """
    if name.lower().endswith((".jpg", ".jpeg")):
        payload = without_location(payload)[0]
    if not dry_run:
        return store.keep(payload, name)
    problem = store.file_name_problem(name)
    if problem:
        raise store.StoreProblem(problem)
    return hashlib.sha256(payload).hexdigest()


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
    """What `scan_datasheet` found, with the pages read, as an Answer: a fact not on a table row is a problem."""
    import tools
    try:
        reader = tools.find("pdf-text", project)
    except tools.ToolProblem as missing:
        return Answer(unchecked=[_cannot("--read: %s" % missing)])
    read = []
    def counted():
        for one in datasheet_pages(path, reader.command):
            read.append(one[0])
            yield one
    found = scan_datasheet(counted(), wanted, labels)
    lines = []
    for fact, entry in found.items():
        if entry["status"] == "NOT FOUND":
            lines.append("%-28s NOT FOUND — tried: %s" % (fact, ", ".join(entry["tried"])))
        for number, line, section, text in entry["hits"][:3]:
            lines.append("%-28s %-10s p%d:%d  [%s]  %s" % (fact, entry["status"], number, line, section or "no heading", text[:220]))
    missing = [fact for fact, entry in found.items() if entry["status"] != "FOUND"]
    lines.append("read %d of the document's pages, %s" % (len(read), "stopping where the last fact was found" if not missing
                 else "%d fact(s) not on a table row: read those pages as images" % len(missing)))
    return Answer({"facts": found, "pages_read": read}, lines,
                  problems=[_problem(fact, "not on a table row: read its pages as images") for fact in missing])


def keep_local(path, url=None, dry_run=False):
    """
    Put a file you already have into the store and return the `documents` entry that points at it
    (P62b). The WROOM-1 v1.1 datasheet exists only as a kept file — its URL now serves v1.8 — so
    fetching can never bring it in; an import can. `url` is where it came from, if anyone knows.
    """
    path = Path(path)
    return {"url": url, "sha256": keep_in_store(path.read_bytes(), path.name, dry_run), "file": path.name,
            "retrieved": datetime.date.today().isoformat(), "title": None, "version": None}


def records_with_documents(project=None):
    """(owner id, record) for every record that can point at a document: parts, catalog, boards."""
    import boards
    paths = [path for _, path in store.records("parts", LIBRARY, project, drafts=True).values()]
    paths += [path for _, path in boards.records(project).values()]
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
    kept = store.place("sources")
    wanted = [word.lower() for word in words]
    lines = []
    for owner, record in records_with_documents(project):
        for key, entry in record["documents"].items():
            said = " ".join(str(part) for part in (owner, key, entry.get("file"), entry.get("title"),
                                                   entry.get("url"), entry.get("version"))).lower()
            if not all(word in said for word in wanted):
                continue
            path = kept / str(entry.get("sha256")) / str(entry.get("file"))
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
    for path in sorted(kept.glob("*/*")) if kept.is_dir() else []:
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


def to_fetch(record):
    """The cited datasheet and image URLs a record does not keep yet — what `--fetch` would download."""
    known = {entry.get("url") for entry in (record.get("documents") or {}).values()}
    return [url for url in cited_urls(record) if url.split("?")[0].lower().endswith(KEEPABLE) and url not in known]


def document_name(url):
    """The file name a cited URL is kept under: the last segment of its path, decoded — never its query."""
    return urllib.parse.unquote(url.split("?")[0].rsplit("/", 1)[-1]) or "document"


def fetch_plan(record):
    """
    [(url, file name)] for every document `--fetch` would keep, or a StoreProblem naming the first one the store would
    refuse by name. All or nothing (§6.4): the names come from the URLs, so every one is known before any download, and a
    refusal stops the whole fetch — not halfway, with the documents before it kept and no record pointing at them.
    `store.keep` still refuses such a name itself, as the last line of defence.
    """
    plan = [(url, document_name(url)) for url in to_fetch(record)]
    for url, name in plan:
        problem = store.file_name_problem(name)
        if problem:
            raise store.StoreProblem("%s: %s — nothing was fetched" % (url, problem))
    return plan


def fetch_documents(part_id, project=None, fetch=None):
    """
    Download every cited datasheet or image into the store and point at each from the record's
    `documents`: its URL, checksum, file name and the date it was fetched — `title` and `version`
    stay null until someone reads them, because a version is what the document PRINTS, not a
    guess (P61). A document the store would refuse by name stops the whole fetch before any
    download (`fetch_plan`). `fetch(url) -> bytes or None` is a parameter for the tests.
    """
    home = record_home(part_id, project)
    if home is None:
        raise PartError("no record called %r to fetch for" % part_id)
    path = home / (part_id + DEFINITION_SUFFIX)
    record = json.loads(path.read_text())
    documents = dict(record.get("documents") or {})
    for url, name in fetch_plan(record):
        payload = (fetch or _download)(url)
        if payload is not None:
            documents[document_key(name, documents)] = {
                "url": url, "sha256": keep_in_store(payload, name), "file": name,
                "retrieved": datetime.date.today().isoformat(), "title": None, "version": None}
    record["documents"] = documents
    _write_record(path, record)
    return documents


def _parse(path):
    try:
        return json.loads(path.read_text())
    except ValueError:
        return None


def _download(url):
    """One cited document through spark's one door to the network (§6.5) — None when it does not answer, so it is not kept."""
    try:
        return store.fetch(url)
    except store.StoreProblem:
        return None


def promote(part_id, project, to=None, dry_run=False):
    """
    Move a record one step along its life: catalog -> the project's parts/ (to build with; it must
    then pass the contract), or the project's parts/ -> the plugin's library (for every later
    project). Its folder (a simulation chip) travels with it; its documents are
    pointers into the store and need nothing moved. Nothing is ever overwritten. Returns the path.
    """
    import shutil
    home = record_home(part_id, project)
    if home is None:
        raise PartError("no record called %r to promote" % part_id)
    to = Path(to) if to else (Path(project) / "parts" if home in (store.place("catalog"), store.place("shelf")) else LIBRARY)
    target = to / (part_id + DEFINITION_SUFFIX)
    if target.exists():
        raise PartError("%s exists; a promotion never overwrites" % target)
    if dry_run:
        return target
    to.mkdir(parents=True, exist_ok=True)
    shutil.copy2(home / (part_id + DEFINITION_SUFFIX), target)
    if (home / part_id).is_dir():
        shutil.copytree(home / part_id, to / part_id, dirs_exist_ok=True)
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
                         " ".join(aliases(record))]).lower()
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
    """Whether a URL answers at all, asked through spark's one door (§6.5). A hallucinated source is the one lie research tells easily."""
    try:
        store.fetch(url, method="HEAD")
    except store.StoreProblem:
        return False
    return True


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


#: Every operation parts.py offers — the ONE table the argument parser and `--describe` are built from, so what an
#: agent reads about an operation cannot drift from what runs (§6.4.3). A row: the flag, its argparse keywords,
#: what it answers, its effects (`writes`, `network`, `deletes`), the keys of its `data`. An operation with an
#: effect takes --dry-run (§6.4.5).
OPERATIONS = (
    ("list", {"action": "store_true"}, "every record a project can build with, and where it comes from", (), ("parts",)),
    ("show", {"metavar": "PART"}, "one record, wherever it lives", (), ("record",)),
    ("validate", {"action": "store_true"}, "every record a project can build with, against the contract", (), ("checked",)),
    ("signals", {"nargs": "+", "metavar": "PART"}, "the signals these parts ask for, as assign_pins.py input", (), ("signals",)),
    ("unverified", {"nargs": "+", "metavar": "PART"}, "what nobody has checked about these parts", (), ("questions",)),
    ("need", {"nargs": "+", "metavar": "WORD"}, "what exists for a need, before researching: words matched in id, name, kind, alias",
     (), ("need", "vendor_order", "found", "drafts", "catalog")),
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
    ("drawer-set", {"metavar": "FILE"}, "set drawer entries from a JSON list in FILE (- for stdin): every write sets, never adds",
     ("writes",), ("changes", "questions", "shelved")),
    ("drawer-import", {"nargs": 2, "metavar": ("SOURCE", "FILE")},
     "apply an importer's payload (FILE, or - for stdin) to the drawer: new entries, and counts by the re-import rule",
     ("writes",), ("changes", "questions", "shelved", "smaller")),
    ("function-set", {"nargs": 2, "metavar": ("PART", "FILE")},
     "set what a part does — a JSON [{does, what}] in FILE (- for stdin) — in the record's own home (--project picks the project's copy); never spark's library",
     ("writes",), ("part", "path", "was", "now", "written", "shelf_copy")),
    ("fact-set", {"nargs": 2, "metavar": ("PART", "FILE")},
     "fill what a record owes — a JSON object of the facts the chain reads, in FILE (- for stdin) — in the record's own home (--project picks the project's copy); never spark's library",
     ("writes",), ("part", "path", "was", "now", "written", "shelf_copy")),
    ("audit", {"action": "store_true"}, "every record in every layer and every drawer link: what owes facts, what is broken",
     (), ("layers", "owed", "broken", "no_function", "dangling", "stops_at_footprint")),
    ("needs", {"metavar": "PROJECT"}, "a project's needs: what each does, its condition, its mark", (), ("needs",)),
    ("needs-set", {"nargs": 2, "metavar": ("PROJECT", "FILE")},
     "set a project's needs from a JSON list in FILE (- for stdin): every write sets, never adds", ("writes",),
     ("changes", "written")),
    ("match", {"metavar": "PROJECT"}, "each of a project's needs with the store's candidates: owned first, what each owes",
     (), ("needs",)),
    ("pick", {"nargs": "+", "metavar": ("PROJECT", "NEED=ID")},
     "set what each need picks (NEED=ID: a record, or a drawer entry) and reserve what you own of it — never past what another project holds",
     ("writes",), ("project", "picks", "reserved", "released", "written")),
    ("requirements", {"metavar": "PROJECT"},
     "the picks as the project's requirements.json: the board, and every part pick with a record — one that owes only its outline is written with a warning, one that owes more is refused; a catalog one goes onto the shelf; what the file already holds stays",
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
    ("project", {"type": Path}, "a project whose own parts/ beats the shipped library"),
    ("from", {"type": _not_negative, "default": 0, "dest": "start", "metavar": "N"}, "with a listing: start at item N (truncated.next says where)"),
    ("dry-run", {"action": "store_true"}, "with an operation that has an effect: say what it would do, and do nothing"),
    ("json", {"action": "store_true"}, "answer in one envelope (docs/2026-10-04-store-design.md §6.4.1)"),
)


class _Parser(argparse.ArgumentParser):
    """argparse, except that a bad argument is an answer, not an exit — with --json it is an envelope too."""

    def error(self, message):
        raise BadArgument(message)


def _parser():
    """The argument parser, built from OPERATIONS and OPTIONS so that `--describe` cannot drift from it."""
    parser = _Parser(prog="parts.py", description="What a part needs, and what is known about it.")
    what = parser.add_mutually_exclusive_group(required=True)
    for name, keywords, summary, _, _ in OPERATIONS:
        what.add_argument("--" + name, help=summary, **keywords)
    for name, keywords, summary in OPTIONS:
        parser.add_argument("--" + name, help=summary, **keywords)
    return parser


def _op_list(args, project):
    listing = []
    for part_id, (layer, path) in store.records("parts", LIBRARY, project).items():
        record = load(part_id, project)
        listing.append({"id": part_id, "kind": record["kind"], "name": record["name"], "layer": layer, "from": str(path.parent)})
    shown, truncated = page(listing, args.start, "list", ["--list"] + _with_project(project))
    lines = [_row(p["id"], p["kind"], "%-9s %s" % (p["layer"], p["name"])) for p in listing]
    return Answer({"parts": shown}, lines, truncated=truncated)


def _op_show(args, project):
    part = any_record(args.show, project)
    return Answer({"record": part}, [describe(part)])


def _op_validate(args, project):
    checked = []
    for part_id in available(project):
        path = definition_path(part_id, project)
        try:
            record = json.loads(path.read_text())
        except json.JSONDecodeError as bad:
            return Answer(unchecked=[_cannot("--validate: %s is not JSON: %s" % (path, bad))])
        checked.append({"part": part_id, "path": str(path), "problems": validate(record, path)})
    shown, truncated = page(checked, args.start, "validate", ["--validate"] + _with_project(project))
    lines = []
    for one in checked:
        lines.append("  %-28s %s" % (one["part"], "ok" if not one["problems"] else "%d problem(s)" % len(one["problems"])))
        lines += ["      - %s" % problem for problem in one["problems"]]
    return Answer({"checked": shown}, lines, truncated=truncated,
                  problems=[_problem(one["part"], problem) for one in checked for problem in one["problems"]])


def _op_signals(args, project):
    found = {"signals": signals_for(args.signals, project)}
    return Answer(found, [json.dumps(found, indent=2)])


def _op_unverified(args, project):
    questions = unverified(args.unverified, project)
    lines = ["  everything these parts claim has been checked."] if not questions else \
        ["  %d thing(s) nobody has checked:\n" % len(questions)]
    for question in questions:
        lines.append("  %s.%s = %s" % (question["part"], question["fact"], question["assumed"]))
        if question["why_it_matters"]:
            lines.append("      %s" % question["why_it_matters"])
    return Answer({"questions": questions}, lines)


def _brief(part):
    return {"id": part["id"], "kind": part["kind"], "name": part["name"]}


def _op_need(args, project):
    found, drafts = need(args.need, project)
    known = [p for p in catalog_matches(args.need) if p["id"] not in drafts and p["id"] not in {q["id"] for q in found}]
    data = {"need": args.need, "vendor_order": list(vendor_order(project)), "found": [_brief(p) for p in found],
            "drafts": drafts, "catalog": [_brief(p) for p in known]}
    lines = [_row(p["id"], p["kind"], p["name"]) for p in found]
    lines += [_row(part_id, "(draft)", "does not yet meet the contract — being filled in") for part_id in drafts]
    lines += [_row(p["id"], p["kind"], "%s  [catalog: researched before; `--promote %s --project .` builds with it]"
                   % (p["name"], p["id"])) for p in known]
    if not lines:
        lines = ["  nothing in the library matches %r.\n  Research it: /spark:research \"%s\"  — vendors in order: %s; sellers: %s"
                 % (" ".join(args.need), " ".join(args.need), ", ".join(vendor_order(project)),
                    ", ".join(sellers(project)) or "none named in the brief")]
    return Answer(data, lines)


def _op_skeleton(args, project):
    if not project or not args.kind:
        return Answer(unchecked=[_cannot("--skeleton needs --project (the record belongs to a project's parts/) and --kind")])
    if not store.PLAIN.fullmatch(args.skeleton):  # P87: a file every reader would refuse is never written
        return Answer(problems=[_problem(args.skeleton, NOT_A_PLAIN_ID % args.skeleton)])
    target = project / "parts" / (args.skeleton + DEFINITION_SUFFIX)
    if target.exists():
        return Answer(problems=[_problem(args.skeleton, "%s exists; fill it in, do not overwrite it" % target)])
    record = skeleton(args.skeleton, args.kind, args.vendor)
    if not args.dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    return Answer({"path": str(target), "record": record, "written": not args.dry_run},
                  ["  %s %s — every null is a fact to record; `parts.py --validate --project .` says what is missing"
                   % ("would write" if args.dry_run else "wrote", target)])


def _op_sources(args, project):
    record = any_record(args.sources, project)
    if args.dry_run:
        urls = cited_urls(record)
        return Answer({"part": args.sources, "sources": [{"url": url, "reachable": None} for url in urls]},
                      ["  would ask %s" % url for url in urls])
    answers = sources_resolve(record)
    lines = ["  %s  %s" % ("ok  " if ok else "NO  ", url) for url, ok in answers] or \
        ["  %s cites no URL — every fact rests on prose sources a person has to find" % args.sources]
    return Answer({"part": args.sources, "sources": [{"url": url, "reachable": ok} for url, ok in answers]}, lines,
                  problems=[_problem(url, "does not answer") for url, ok in answers if not ok])


def _op_fetch(args, project):
    if args.dry_run:
        home = record_home(args.fetch, project)
        if home is None:
            raise PartError("no record called %r to fetch for" % args.fetch)
        wanted = [url for url, _ in fetch_plan(json.loads((home / (args.fetch + DEFINITION_SUFFIX)).read_text()))]
        return Answer({"documents": None, "would_fetch": wanted}, ["  would fetch %s" % url for url in wanted]
                      or ["  %s cites no datasheet or image URL to keep" % args.fetch])
    kept = fetch_documents(args.fetch, project)
    lines = ["  %s/%s  <-  %s" % (entry["sha256"][:12], entry["file"], entry["url"]) for entry in kept.values()]
    return Answer({"documents": kept, "would_fetch": []}, lines or ["  %s cites no datasheet or image URL to keep" % args.fetch])


def _op_keep(args, project):
    path = Path(args.keep)
    if not path.is_file():
        return Answer(unchecked=[_cannot("--keep: no file at %s" % path)])
    located = path.name.lower().endswith((".jpg", ".jpeg")) and without_location(path.read_bytes())[1]
    if located and not args.json:
        print("  removed the location (EXIF GPS) from %s before keeping it" % path.name, file=sys.stderr)
    entry = keep_local(path, args.url, dry_run=args.dry_run)
    return Answer({"document": entry, "location_removed": located, "written": not args.dry_run},
                  [json.dumps(entry, indent=2, ensure_ascii=False)])


def _op_read(args, project):
    labels = {}
    for given in args.label or []:
        fact, _, words = given.partition("=")
        labels[fact] = [word.strip().lower() for word in words.split("|") if word.strip()]
    return read_datasheet(args.read, args.want or [], labels, project)


def _op_kept(args, project):
    found = find_kept(args.kept, project)
    return Answer({"found": found}, found or ["nothing kept matches %s — fetch it, or --keep a file you have" % " ".join(args.kept)])


def _op_promote(args, project):
    if not project:
        return Answer(unchecked=[_cannot("--promote needs --project")])
    target = promote(args.promote, project, dry_run=args.dry_run)
    return Answer({"path": str(target), "written": not args.dry_run},
                  ["  %s %s" % ("would promote to" if args.dry_run else "promoted to", target)])


def _read_json_input(name):
    """A payload from a file, or from stdin for '-' — the way labels and names travel, never argv (§6.4.2): (data, None) or (None, why not)."""
    try:
        return json.loads(sys.stdin.read() if name == "-" else Path(name).read_text()), None
    except (OSError, ValueError) as broken:
        return None, "%s is not readable JSON: %s" % ("stdin" if name == "-" else name, broken)


def _change_line(change, dry_run):
    """
    One set-only write's change (§5.2), the drawer's and the needs file's alike: '  new soil-probe: soil probe × 8 — is
    part sen0193-soil-moisture' for a new drawer entry (× ? when its count was left out), else '  set soil: mark null →
    "have"', every value from what it was.
    """
    if change["new"] and "entry" in change:
        now, linked = change["now"], change["now"].get("is")
        return "  %s %s: %s × %s%s" % ("would add" if dry_run else "new", change["entry"], now.get("label"), now.get("count", "?"),
                                         " — is %s %s" % next(iter(linked.items())) if linked else "")
    return "  %s %s: %s" % ("would set" if dry_run else "set", change.get("entry") or change.get("need"), "; ".join(
        "%s %s → %s" % (key, json.dumps(change["was"].get(key), ensure_ascii=False), json.dumps(value, ensure_ascii=False))
        for key, value in change["now"].items()))


def _write_lines(changes, problems, dry_run, said=()):
    """
    What a set-only write did or would do (§5.2), said one way for the drawer and the needs file: each change — marked
    when anything was refused, because then nothing is written — what else the write has to say, then each refusal; or
    that nothing changes.
    """
    lines = [("  refused, not written: " + _change_line(change, dry_run).strip()) if problems else _change_line(change, dry_run)
             for change in changes] + list(said)
    lines += ["  refused, so nothing was written: %s — %s" % (p["subject"], p["sentence"]) for p in problems]
    return lines or ["  nothing to change"]


def _drawer_answer(changes, questions, problems, dry_run):
    """What a drawer write did or would do (§5.2): all of it, or — when anything is refused — none of it."""
    import drawer
    if not problems and not dry_run:
        drawer.apply(changes)
    made = [change for change in changes if change["now"]]
    wanted = [change["shelve"] for change in made if change["shelve"]]
    shelved = [Path(path).stem for path, project in wanted if shelvable(path, project)]
    left = [Path(path).stem for path, project in wanted if not shelvable(path, project)]
    said = ["  ? %s" % q["sentence"] for q in questions] + [
        "  not shelved: %s — it does not meet the part contract yet, so it stays in its project and the entry still links to it"
        % stem for stem in left]
    return Answer({"changes": [{key: change[key] for key in ("entry", "new", "was", "now")} for change in made],
                   "questions": questions, "shelved": shelved, "not_shelved": left, "written": not (problems or dry_run)},
                  _write_lines(made, problems, dry_run, said), problems=problems)


def _op_drawer(args, project):
    import drawer
    entries = drawer.listing()
    shown, truncated = page(entries, args.start, "drawer", ["--drawer"])
    lines = ["  %-44s %6s  %-38s %s" % (str(e["label"])[:44], "?" if e["count"] is None else e["count"],
                                         "%s %s" % next(iter(e["is"].items())) if e["is"] else "—",
                                         "maybe owned — check the drawer" if e["unsure"] else ("skip: %s" % e["skip"] if e["skip"] else ""))
             for e in entries]
    lines.append("  %d entr%s" % (len(entries), "y" if len(entries) == 1 else "ies"))
    return Answer({"entries": shown}, lines, truncated=truncated)


def _op_drawer_set(args, project):
    import drawer
    items, unreadable = _read_json_input(args.drawer_set)
    if unreadable:
        return Answer(unchecked=[_cannot(unreadable)])
    return _drawer_answer(*drawer.plan_set(items), args.dry_run)


def _op_drawer_import(args, project):
    import drawer
    source, name = args.drawer_import
    payload, unreadable = _read_json_input(name)
    if unreadable:
        return Answer(unchecked=[_cannot(unreadable)])
    changes, questions, problems, smaller = drawer.plan_import(source, payload)
    answer = _drawer_answer(changes, questions, problems, args.dry_run)
    if not problems and not args.dry_run:
        store.write_json("drawer-import", store.slug(source), drawer.kept_payload(payload))
    return answer._replace(data=dict(answer.data, smaller=smaller), lines=list(answer.lines) + ["  %s" % s for s in smaller])


def _shelved_from(path):
    """The project a shelf copy says it was shelved from (its `based_on`, §5.5) — None for a catalog's copy, or no copy."""
    record = _parse(path) if Path(path).is_file() else None
    based_on = record.get("based_on") if isinstance(record, dict) else None
    named = based_on.get("project") if isinstance(based_on, dict) else None
    return named if isinstance(named, str) else None


def _record_path(part_id, project):
    """
    A part record's own file, and the project whose shelf copy follows it (§5.4, §5.5): the nearest layer that has it, the
    catalog included, else a project on the person's list — except that a shelf copy of a listed project's record is not a
    home: that project's record is. A record found in the project given names that project too, when the shelf holds a copy
    of it shelved from there: the copy follows its record, however the record was reached.
    """
    import drawer
    path, where = next(((path, where) for kind, found, where, path in drawer.linkable(project) if (kind, found) == ("part", part_id)),
                       (None, None))
    if path is not None and path.parent == store.place("shelf"):
        named = _shelved_from(path)
        folder = store.projects().get(named) if named else None
        home = folder / "parts" / path.name if folder is not None else None
        return (home, named) if home is not None and home.is_file() else (path, None)
    named = store.project_name(project) if where == "project" else None
    return path, named if named and _shelved_from(store.place("shelf") / path.name) == named else None


def _refresh_shelf_copy(path, record, project_name, dry_run):
    """
    The shelf copy of a project's record made current again (§5.5) — after a write, and when an earlier write left it behind
    (the record filled in its project while the copy stayed, so every retry said "nothing to change") — said in words:
    current, refreshed, would refresh, or not refreshed and why: a copy that would not meet the contract is not written.
    """
    copy = _shelf_copy(path, project_name, record)
    if _parse(store.place("shelf") / path.name) == copy:
        return "current"
    wrong = validate(copy, path)
    if wrong:
        return "shelf copy not refreshed: %s" % "; ".join(wrong)
    if dry_run:
        return "would refresh the shelf copy"
    shelve(path, project_name)
    return "shelf copy refreshed"


def _write_record(path, record):
    """A record back to its own home, whole (§6.1): through the store when it lives there (contained, private), else to its file."""
    for name in ("shelf", "catalog"):
        if path.parent == store.place(name):
            return store.write_json(name, path.stem, record)
    return store.write_file(path, json.dumps(record, indent=2, ensure_ascii=False) + "\n")


def _set_in_home(part_id, project, values, dry_run, refuse):
    """
    Set fields of a part record in its own home (§5.4) — the catalog's, a project's, or a listed project's behind a shelf
    copy — never spark's library, which is changed in spark's repository. A shelf copy that follows the record is made
    current whether or not this write changed anything (`_refresh_shelf_copy`), and the answer says what became of it.
    `refuse(record, after, path)` says what is wrong with the result, and anything it says refuses the write.
    """
    path, source = _record_path(part_id, project)
    if path is None:
        raise PartError("no part record called %r — `parts.py --need` finds what exists" % part_id)
    if path.parent.resolve() == LIBRARY.resolve():
        return Answer(problems=[_problem(part_id, "%s is in spark's own library, which is changed in spark's repository, "
                                                  "not by parts.py" % part_id)])
    record = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        return Answer(problems=[_problem(part_id, "%s is not a JSON object (%s) — repair the file by hand first" % (part_id, path))])
    after = dict(record, **values)
    wrong = refuse(record, after, path)
    if wrong:
        return Answer(problems=[_problem(part_id, sentence) for sentence in wrong])
    was, changes = {key: record.get(key) for key in values}, after != record
    if changes and not dry_run:
        _write_record(path, after)
    shelf_copy = _refresh_shelf_copy(path, after, source, dry_run) if source else None
    said = ("  %s %s (%s): %s" % ("would set" if dry_run else "set", part_id, path, "; ".join(
                "%s %s → %s" % (key, json.dumps(was[key], ensure_ascii=False), json.dumps(value, ensure_ascii=False))
                for key, value in values.items()))
            if changes else "  nothing to change: %s (%s) already says this" % (part_id, path))
    return Answer({"part": part_id, "path": str(path), "was": was, "now": values, "written": not dry_run, "shelf_copy": shelf_copy},
                  [said] + (["  " + shelf_copy] if shelf_copy not in (None, "current") else []))


def _op_function_set(args, project):
    part_id, name = args.function_set
    function, unreadable = _read_json_input(name)
    if unreadable:
        return Answer(unchecked=[_cannot(unreadable)])
    answer = _set_in_home(part_id, project, {"function": function}, args.dry_run, lambda record, after, path:
                          function_problems(after) if function else ["a function is a non-empty list [{does, what}]"])
    return answer._replace(data=dict(answer.data, was=answer.data["was"]["function"], now=function)) if answer.data else answer


def _op_fact_set(args, project):
    part_id, name = args.fact_set
    facts, unreadable = _read_json_input(name)
    if unreadable:
        return Answer(unchecked=[_cannot(unreadable)])
    if not (isinstance(facts, dict) and facts and set(facts) <= set(CHAIN_FACTS)):
        return Answer(problems=[_problem(part_id, "a fact write is a JSON object of facts the chain reads: %s" % ", ".join(CHAIN_FACTS))])
    return _set_in_home(part_id, project, facts, args.dry_run, lambda record, after, path: (
        ["%s is absent — a write fills a fact, it never empties one" % key for key in facts if _absent(key, facts[key])]
        + sorted(set(broken_problems(after, path)) - set(broken_problems(record, path)))))


def _op_catalog(args, project):
    records, broken = catalog_records()
    listing = [{"id": part_id, "kind": record["kind"], "name": record["name"]} for part_id, record in records.items()]
    shown, truncated = page(listing, args.start, "catalog", ["--catalog"])
    lines = [_row(r["id"], r["kind"], r["name"]) for r in listing]
    lines += [_row(name, "BROKEN", "does not parse, or names no schema/id/name/kind") for name in broken]
    lines.append("  %d record(s), %d broken" % (len(records), len(broken)))
    return Answer({"records": shown, "broken": broken}, lines, truncated=truncated,
                  problems=[_problem(name.split(" — ")[0], "a broken catalog record: %s" % name) for name in broken])


#: What `--audit` says of a board whose file has no header geometry (C-7): the chain stops there, whatever else it passes.
STOPS_AT_FOOTPRINT = "stops at the footprint stage (P121) — no header geometry in its board file"


def _op_audit(args, project):
    counts, owed, broken, silent, dangling, stops = audit(project)
    shown, truncated = page(owed, args.start, "audit", ["--audit"] + _with_project(project))
    lines = ["  %-12s %3d current, %3d owe facts, %3d broken" % (layer, row["current"], row["owed"], row["broken"])
             for layer, row in counts.items()]
    lines += ["  BROKEN %s (%s): %s" % (b["id"], b["layer"], "; ".join(b["problems"][:3])) for b in broken]
    lines += ["  %s (%s) owes: %s" % (o["id"], o["layer"], ", ".join(o["owes"])) for o in owed]
    lines += ["  says nothing of what it does — set it once with --function-set <part> <file>%s: %s"
              % (" --project %s" % shlex.quote(str(project)) if project else "", ", ".join(silent))] if silent else []
    lines += ["  drawer entry %s points at a record nobody has" % entry for entry in dangling]
    lines += ["  %s (%s) %s" % (s["id"], s["layer"], STOPS_AT_FOOTPRINT) for s in stops]
    return Answer({"layers": counts, "owed": shown, "broken": broken, "no_function": silent, "dangling": dangling,
                   "stops_at_footprint": stops}, lines,
                  truncated=truncated, problems=[_problem(b["id"], "broken: " + "; ".join(b["problems"])) for b in broken]
                  + [_problem(entry, "points at a record nobody has") for entry in dangling])


def _op_needs(args, project):
    import needs
    listed = needs.read(args.needs)
    return Answer({"needs": listed}, ["  %-10s %s / %s%s%s" % (n["id"], n.get("does"), n.get("what"),
                                                               "  (%s)" % n["condition"] if n.get("condition") else "",
                                                               "  [%s]" % n["mark"] if n.get("mark") else "") for n in listed]
                  or ["  no needs yet — /spark:idea writes them"])


def _op_match(args, project):
    import needs
    matched, problems = needs.match(args.match)
    if not matched and not problems:
        return Answer(unchecked=[_cannot("%s has no needs yet — /spark:idea writes them" % args.match)])
    for need in matched:
        kept = [c for rank, c in enumerate(need["candidates"]) if rank < 8 or c["what_matches"]]
        need["more"], need["candidates"] = len(need["candidates"]) - len(kept), kept
    shown, truncated = page(matched, args.start, "match", ["--match", args.match])
    lines = []
    for need in matched:
        lines.append("  %s — %s / %s%s%s" % (need["need"], need["does"], need["what"], "  (%s)" % need["condition"] if need["condition"] else "",
                                            "  [%s]" % need["mark"] if need["mark"] else ""))
        lines += ["      %-10s %-46s %s" % ("owned %s" % c["owned"] if c["owned"] else "", "%s (%s)" % (c["id"] or c["entry"], c["in"]),
                                        "  ".join(filter(None, [", ".join(c["what"]) + ("" if c["what_matches"] else " [other words]"),
                                                                "free %s" % c["free"] if c["owned"] else "",
                                                                "owes " + ", ".join(c["owes"]) if c["owes"] else "",
                                                                "stops at the footprint stage (P121)" if c.get("stops_at") else ""])))
                  + ("  maybe owned — check the drawer" if c["unsure"] else "") + ("  BROKEN" if c["broken"] else "")
                  for c in need["candidates"]]
        lines += ["      … %d more, none with the need's words" % need["more"]] if need["more"] else []
        lines += ["      nothing in the store does this — a gap"] if not need["candidates"] else []
    lines += ["  %s: %s" % (p["subject"], p["sentence"]) for p in problems]
    return Answer({"needs": shown}, lines, problems=problems, truncated=truncated)


def _op_needs_set(args, project):
    import needs
    target, name = args.needs_set
    items, unreadable = _read_json_input(name)
    if unreadable:
        return Answer(unchecked=[_cannot(unreadable)])
    after, changes, problems = needs.plan_set(target, items)
    written = not (problems or args.dry_run)
    if written and changes:
        needs.write(target, after)
    return Answer({"changes": changes, "written": written}, _write_lines(changes, problems, args.dry_run), problems=problems)


def _op_pick(args, project):
    import drawer
    import needs
    target, given = args.pick[0], args.pick[1:]
    pairs = [tuple(one.split("=", 1)) for one in given if "=" in one]
    if not pairs or len(pairs) != len(given):
        return Answer(unchecked=[_cannot("--pick takes the project, then NEED=ID for each pick: light=led-red-5mm",
                                         "parts.py --match <project> lists each need's candidates and their ids")])
    reasons, unreadable = _read_json_input(args.passed_over) if args.passed_over else ([], None)
    if unreadable:
        return Answer(unchecked=[_cannot(unreadable)])
    history = store.events()  # read whole before the first write: one that cannot be read refuses the pick, with nothing written
    listed, keys_before = store.project_name(target) is not None, needs.entry_keys(needs.read(target))
    after, changes, events, notes, problems = needs.plan_pick(target, pairs, reasons)
    if not problems and not args.dry_run:
        store.add_project(target)
        drawer.apply(changes)
        for event in events:
            store.append_event(event)
        # the project's own file last: a store that refuses leaves it as it was, and the same pick, retried, finishes the rest
        needs.write(target, after)
    asked, name = dict(pairs), store.add_project(target, dry_run=True)
    picks = [{"need": need["id"], "pick": need.get("pick") or []} for need in after if need["id"] in asked]
    said = [] if problems else ["  %s: %s" % (one["need"], ", ".join(next(iter(pick.values())) for pick in one["pick"])) for one in picks]
    released = _released(changes, name)
    said += [] if problems else ["  %s%s: %s — no pick of this project explains it" % (
        "would release" if args.dry_run else "released", "" if hold["now"] == 0 else " %d of %d" % (hold["was"] - hold["now"], hold["was"]),
        hold["entry"]) for hold in released]
    wrote = [] if problems else _what_a_pick_wrote(name, listed, history, events, needs.entry_keys(after) - keys_before, args.dry_run)
    return Answer({"project": name, "picks": picks,
                   "reserved": [{"entry": change["entry"], "used_in": change["now"]["used_in"]} for change in changes],
                   "released": released, "written": not problems and not args.dry_run},
                  _write_lines(changes, problems, args.dry_run, said + ["  %s" % note for note in notes] + wrote), problems=problems)


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


def _released(changes, name):
    """
    The holds of project `name` a pick lets go (C-4): each drawer entry whose reservation for it goes down, because no pick of
    the project explains it any more — a re-pick, or a hold given by hand — as {"entry", "was", "now"}. A pick rebuilds the
    project's holds from its picks (§8 C), and what it drops is said, never left to a bare `used_in … → {}`.
    """
    return [{"entry": change["entry"], "was": was, "now": now} for change in changes
            for was, now in [((change["was"].get("used_in") or {}).get(name, 0), change["now"]["used_in"].get(name, 0))] if now < was]


#: What `--requirements` says of a need nothing on the board serves (C-2), by why: plainly, and what the person can do.
NOT_ON_THE_BOARD = {"no pick": "no pick; --match lists its candidates",
                    "a gap": "marked a gap: nothing like it is in the store yet; research it before it can be built",
                    "no record": "{picks} has no record: fine for what is wired off the board (a speaker, a battery); what sits on the "
                                 "board needs one — link its drawer entry to a record with `is`, or research one"}


def _op_requirements(args, project):
    import boards
    import needs
    content, shelving, unplaced, kept, board_was, problems, placeholder, unserved, no_supply, no_receiver, no_driver = needs.requirements(
        args.requirements)
    path, changed = Path(args.requirements) / needs.REQUIREMENTS, False
    # F16: the drawer keys the file names before this write — needs.requirements has read it as JSON already
    named = needs.unserved_keys(json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {})
    if not problems and not args.dry_run:
        for record, source in shelving:
            shelve(record, source)
        changed = store.write_file(path, json.dumps(content, indent=2, ensure_ascii=False) + "\n")
    said = [] if problems else ["  %s %s: board %s; parts %s" % (
        "would write" if args.dry_run else "wrote" if changed else "unchanged", path, content["board"],
        ", ".join(needs.entry_label(entry) for entry in content["parts"]) or "none")]
    said += ["  board: %s → %s" % (json.dumps(board_was), json.dumps(content["board"]))] if board_was not in (None, content["board"]) and not problems else []
    stop = "" if problems else boards.footprint_stop(content["board"], Path(args.requirements))  # F12 (C-7): said, never refused
    said += ["  board %s %s" % (content["board"], stop)] if stop else []
    said += ["  onto the shelf, so every project builds with it: %s" % ", ".join(Path(r).stem for r, _ in shelving)] if shelving and not problems else []
    said += ["  placeholder outline — %s owes body_mm, so the PCB step lays it out at a placeholder %g x %g mm: a dimension drawing "
             "(fetched after the person's yes) or a measurement fills it — %s" % ((part_id,) + needs.emit_board.DEFAULT_BODY_MM + (how,))
             for part_id, how in ([] if problems else placeholder)]
    said += ["  reserved, not placed — no record: %s" % ", ".join(unplaced)] if unplaced and not problems else []
    said += ["  kept, not from a pick: %s" % ", ".join(needs.entry_label(entry) for entry in kept)] if kept and not problems else []
    said += ["  rail %s has no supply — pick a power inlet or a supply (%s draw%s from it)"
             % (gap["rail"], ", ".join(gap["drawn_by"]), "s" if len(gap["drawn_by"]) == 1 else "") for gap in ([] if problems else no_supply)]
    said += ["  net %s is driven by %s and nothing listed receives it — pick what it drives (a speaker terminal, a motor, a connector)"
             % (gap["net"], gap["driven_by"]) for gap in ([] if problems else no_receiver)]
    said += ["  net %s is one side of a driven pair and nothing listed drives it — pick what drives the pair (the amplifier this "
             "terminal hangs off), never a supply (%s %s on it)" % (gap["net"], ", ".join(gap["received_by"]),
                                                                    "is" if len(gap["received_by"]) == 1 else "are")
             for gap in ([] if problems else no_driver)]
    said += ["  not on the board: %s — %s" % (item["need"], NOT_ON_THE_BOARD[item["why"]].format(picks=", ".join(item["picks"])))
             for item in ([] if problems else unserved)]
    said += [] if problems else _names_your_entries(needs.REQUIREMENTS, needs.unserved_keys(content) - named, args.dry_run)
    return Answer({"path": str(path), "requirements": content, "shelved": [Path(r).stem for r, _ in shelving],
                   "unplaced": unplaced, "kept": kept, "board_was": board_was, "placeholder_outline": [part_id for part_id, _ in placeholder],
                   "unserved": unserved, "no_supply": no_supply, "no_driver": no_driver,
                   "no_receiver": no_receiver, "written": not problems and not args.dry_run},
                  _write_lines([], problems, args.dry_run, said), problems=problems)


def _op_step(args, project):
    import cost
    target, step = args.step
    if step not in cost.STEPS:
        return Answer(unchecked=[_cannot("a step is one of %s (the spine, §2 of the store design)" % ", ".join(cost.STEPS))])
    listed = store.project_name(target) is not None
    event = cost.step_event(store.add_project(target, dry_run=args.dry_run), step)
    if not args.dry_run:
        store.append_event(event)
    # C-17: what a step writes is said — a line in the person's history, with the session's id, and the project on their list
    return Answer({"step": event, "written": not args.dry_run},
                  ["  %s step %s of %s — a line in your history%s" % (
                      "would start" if args.dry_run else "started", step, event["project"],
                      ", with this Claude Code session's id" if event["session"] else cost.session_note())]
                  + ([] if listed else ["  %s %s on your projects" % ("would list" if args.dry_run else "listed", event["project"])]))


def _op_tally(args, project):
    import cost
    import drawer
    import needs
    name = store.project_name(args.tally)
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
        counted, unchecked = cost.cost([event for event in history if event.get("event") == "step"], name), []
    except cost.NoTranscript as missing:
        counted, unchecked = None, [_cannot(str(missing), "mark each step with parts.py --step <project> <step> in a Claude Code session")]
    said, unreadable = cost.line(len(picks), from_store, owned, counted), cost.unreadable_note(counted)
    built = any(event.get("event") == "built" and event.get("project") == name for event in history)
    needs_said = "%d of %d needs picked%s" % (len(listed) - len(unpicked), len(listed),
                                              " — not picked: %s" % ", ".join(unpicked) if unpicked else "")
    return Answer({"picks": len(picks), "from_store": from_store, "owned": owned, "cost": counted, "built": built, "line": said,
                   "needs": len(listed), "needs_picked": len(listed) - len(unpicked)},
                  ["  " + said, "  " + needs_said] + ["  " + glossed for glossed in cost.gloss(counted)]
                  + ["  " + item["sentence"] for item in unchecked] + (["  " + unreadable] if unreadable else [])
                  + ([] if built else ["  not built yet — check_spine records it when the chain runs end to end"]),
                  unchecked=unchecked)


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


def _say(op, answer, as_json):
    """
    Print one answer and return its exit code (§6.4.1): with --json the envelope, compact, on stdout; without, the
    person's lines — and when an answer has no lines, its sentences are the answer, on stderr as before.
    """
    said = envelope("parts", op, answer.data, answer.problems, answer.unchecked, answer.next, answer.truncated)
    if as_json:
        print(json.dumps(said, ensure_ascii=False, separators=(",", ":")))
    else:
        for line in answer.lines:
            print(line)
        if not answer.lines:
            for item in list(answer.problems) + list(answer.unchecked):
                print("parts.py: %s%s" % (item["sentence"], " — " + item["fix"] if item.get("fix") else ""), file=sys.stderr)
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
    except store.StoreProblem as broken:
        answer = Answer(unchecked=[_cannot(str(broken))])
    return _say(op, answer, args.json)


if __name__ == "__main__":
    sys.exit(main())
