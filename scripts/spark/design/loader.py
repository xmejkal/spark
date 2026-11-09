#!/usr/bin/env python3
"""
A design, loaded once: the requirements file, the project it belongs to, the board, the parts as
instances, and the rules.

Three scripts loaded a design on their own — `emit_board.main`, `check_all`'s placeholder list
and `check_spine` — and the copies disagreed in the ways copies do. That `main` (`board_emitter.read_inputs` now) resolved
the project on one line and passed the unresolved `--project` flag to the rules lookup seventy
lines later, so the documented invocation (inside the project, no flag) emitted every power
trace unsized, exit 0, and blamed the reader for it. `check_spine` resolved the project from the
current directory and the toolchain from the requirements file, so from anywhere else it could
not find the project's own parts. `check_all` copied the load-and-tag loop under
`except Exception: return ()`. And all three read the requirements JSON outside any `try`: a
malformed file was a traceback and exit 1, which in a three-valued tool reads as "problems
found". Sprint audit 2026-09-29, claims A2, A4, A8, A10.

So: one place. A design is loaded FROM ITS FILE. The project is the flag if given, else the
nearest project up from the file's own directory — not from wherever the command was typed.
Everything that can be wrong with the input is a `DesignError`, which callers turn into
`could-not-run`; nothing here raises anything else on bad input.

This module resolves and reads. It names a SIGNAL for its instance (`signal_name`), because that
name is decided when the instance is, and so it is the one that says which instance names are ONE
name (`one_name`): `signal_name` is what makes them one. It does not name COMPONENTS for the
netlist — that is `board_emitter`'s, because the name is decided by what the emitted file needs —
and it does not assign pins, because only the generator needs that. It refuses a file that gives
two parts one name before any stage runs on it (`read`), and a design whose signals land on one
name where the signals are derived (`signals_of`, which is the first to hold the part records).
"""

import json
import math
import re
from collections import namedtuple
from pathlib import Path

from spark.records import board_records
from spark.design import design_codes
from spark.design import fab
import parts as parts_library
from spark.records import record_kind
from spark.sourcing import part_records
from spark.records import provenance
from spark.core.errors import CodedMessageError

#: What `load` returns. `parts` are the requested instances: each a copy of its record, with
#: `_instance` set when the requirements named it.
Design = namedtuple("Design", "path project requirements board parts signals rules")

#: Where a project keeps the rules its checks and its generator both read.
RULES_PATH = Path(".spark") / "rules.json"

#: Where a built design's netlist lands, as `tsci build` lays it out: `dist/<name>/circuit.json`,
#: the single-board convention first. Named once — `check_all` discovers by it and `init_project`
#: seeds rules from it, and each had its own copy that the other could drift from (audit A6).
CIRCUIT_PATHS = ("dist/board/circuit.json", "dist/*/circuit.json")


def one_board_message(circuits, flags=""):
    """The sentence that two built designs in one project get from every tool (P223, P318): spark handles one board
    per project today. `circuits` are absolute paths, the first one the example; `flags` are what the tool also needs
    with it (init: --force, over the rules it already wrote). Many boards come with v0.13 (#94)."""
    return ("spark handles one board per project today: use one with --circuit %s%s, or give each board its own folder "
            "with its own parts/ and run init_project.py in it" % (circuits[0], " " + flags if flags else ""))


class DesignError(CodedMessageError):
    """Error: the input cannot be loaded, and this is why. Always a sentence, never a traceback. `code` (design_codes) says
    which refusal it is, and an agent decides on it, never on the sentence (P700). A CodedMessageError (P716 row 11)."""


#: Why two parts cannot share a name — said by this reader and by `needs` for the picks it writes, in the same words,
#: because it is one rule (P163). The rider about capitals is for two spellings; a name written twice gets the rule alone.
SAME_NAME_RULE = "the build refuses two components of one name"
ONE_NAME_RULE = "%s, and capitals do not make two names" % SAME_NAME_RULE


def one_name(name):
    """
    A name as the build tells names apart: `signal_name` puts an instance's name in capitals before its signals, so
    OpenLid and Openlid both give OPENLID_BUTTON — one signal, which `assign_pins` placed twice and the generator
    traced to one pad from two GPIOs, exit 0 (P163, #100). The ONE definition; `needs._one_name` points here.
    """
    return name.upper()


def names_that_are_one(wanted):
    """
    The first pair of `parts` entries whose names are one name, as (index, name, index, name), or None.

    On the names the file GIVES: an entry's shape is `requested_parts`' to refuse, and what an unnamed entry is called
    is the generator's (`board_emitter.component_name`), whose own compare stays as the independent net.
    """
    seen = {}
    for index, entry in enumerate(wanted.get("parts") or []):
        name = entry.get("name") if isinstance(entry, dict) else None
        if not isinstance(name, str) or not name:
            continue
        if one_name(name) in seen:
            return seen[one_name(name)] + (index, name)
        seen[one_name(name)] = (index, name)
    return None


JSON_WORDS = {str: "text", dict: "an object", list: "a list", int: "a number", float: "a number", bool: "true or false",
              type(None): "null"}  # --- MVP --- (P438): the kind of a value in the words of the file's own format


def json_word(value):
    """What a person who writes JSON calls this value's kind; an exact type lookup, so a bool is not a number."""
    return JSON_WORDS.get(type(value), type(value).__name__)


def read(path):
    """The requirements file as a dict, or a DesignError saying what is wrong with it."""
    path = Path(path)
    if not path.is_file():
        raise DesignError("no requirements at %s", path, code=design_codes.NO_REQUIREMENTS)
    try:
        wanted = json.loads(path.read_text())
    except ValueError as broken:
        raise DesignError("%s is not JSON: %s", path, broken, code=design_codes.REQUIREMENTS_UNREADABLE) from broken
    except OSError as broken:
        raise DesignError("%s could not be read: %s", path, broken, code=design_codes.REQUIREMENTS_UNREADABLE) from broken
    if not isinstance(wanted, dict):
        raise DesignError("%s holds a %s; a requirements file is an object with `parts`",
                          path, type(wanted).__name__, code=design_codes.REQUIREMENTS_FIELD_WRONG)
    signals = wanted.get("signals")  # --- MVP --- (P438): a null stays the default; any other kind but a list is refused
    if signals is not None and not isinstance(signals, list):
        raise DesignError('%s: signals is %s; write a list of signals, each {"name", "needs", "pin" or "bus"}',
                          path, json_word(signals), code=design_codes.REQUIREMENTS_FIELD_WRONG)
    parts = wanted.get("parts")  # --- MVP --- (P438): the same for `parts`, before any entry is walked
    if parts is not None and not isinstance(parts, list):
        raise DesignError('%s: parts is %s; write a list of part ids or {"part", "name"}', path, json_word(parts),
                          code=design_codes.REQUIREMENTS_FIELD_WRONG)
    refuse_bad_signals(path, signals or [])
    clash = names_that_are_one(wanted)
    if clash:
        # P163: OpenLid and Openlid are one signal to the build, so the generator traced two GPIOs to one pad with exit 0.
        # Refused HERE, so the chain's first stage says so and nothing is emitted; both spellings, as the person wrote them.
        first, first_name, second, second_name = clash
        part = (wanted["parts"][second].get("part") if isinstance(wanted["parts"][second], dict) else None) or "…"
        rule = ONE_NAME_RULE if first_name != second_name else SAME_NAME_RULE  # BtnLeft twice is not about capitals
        raise DesignError('%s: parts[%d] is called %s and parts[%d] %s — %s; give one of them a name of its own, '
                          '{"part": "%s", "name": …}', path, first, first_name, second, second_name, rule, part,
                          code=design_codes.NAME_USED_TWICE)
    return wanted


def refuse_bad_signals(path, signals):
    """Each entry of `signals` as the file gives it: a DesignError for the first that is no signal with a name, needs that
    are words, and a pin that is a name. A signal with no name was a KeyError through both mains and "the chain is broken"
    through the spine (close audit C7), so it is checked where the file is read, like `parts`."""
    for index, signal in enumerate(signals):
        if not isinstance(signal, dict) or not isinstance(signal.get("name"), str) or not signal["name"]:
            raise DesignError("%s: signals[%d] needs a `name`; a signal is {name, needs, pin?, bus?}",
                              path, index, code=design_codes.REQUIREMENTS_FIELD_WRONG)
        needs = signal.get("needs", [])
        if not isinstance(needs, list) or not all(isinstance(need, str) for need in needs):
            raise DesignError("%s: signals[%d].needs must be a list of what the pin must do",
                              path, index, code=design_codes.REQUIREMENTS_FIELD_WRONG)
        pin = signal.get("pin")
        if pin is not None and not isinstance(pin, str):
            raise DesignError('%s: signals[%d].pin is %s; write a pin name from the board such as "D0"',
                              path, index, json_word(pin), code=design_codes.REQUIREMENTS_FIELD_WRONG)
        if pin == "":
            raise DesignError('%s: signals[%d].pin is an empty name; write a pin name from the board such as "D0"',
                              path, index, code=design_codes.REQUIREMENTS_FIELD_WRONG)
        if not re.fullmatch(record_kind.SELECTOR_SAFE, signal["name"]):  # P87's attribute half, as a part's signal
            raise DesignError("%s: signals[%d] is named %r, but a signal is a name — letters, digits and _ (LED_STATUS): the "
                              "pin map and the board name it, and firmware is written against it", path, index, signal["name"],
                              code=design_codes.REQUIREMENTS_FIELD_WRONG)


def project_for(path, project=None):
    """
    The project a requirements file belongs to.

    `--project` wins. Otherwise the nearest project UP FROM THE FILE — a design lives with its
    parts and its rules, and it does not stop belonging to them when the command is typed from
    `/tmp`. A file inside no project at all is built from the plugin's own library (no rules),
    the way `check_spine` always did; the callers say so (`LIBRARY_NOTE`).
    """
    if project:
        chosen = Path(project)
        if not chosen.is_dir():
            # Unchecked, a typo here resolved to a path nobody looked at: the board and the
            # parts came from the library, the project's rules were dropped, exit 0, stderr
            # empty — A2's defect one character away (close audit C5).
            raise DesignError("no directory at %s — `--project` names a project directory", chosen,
                              code=design_codes.NO_PROJECT_FOLDER)
        return chosen.resolve()
    return board_records.project_or_library(Path(path).resolve().parent)


def is_library(project):
    """Whether a design was resolved to the plugin's own root, for want of a project around it."""
    return Path(project).resolve() == board_records.PLUGIN_ROOT


#: What the two mains say when a design was built from nowhere. One sentence, one place.
LIBRARY_NOTE = ("note: no project up from the requirements file, so parts and boards come from "
                "the plugin's library and there are no rules — `/spark:init` in a directory "
                "makes it a project")


def requested_parts(wanted):
    """
    The parts list, normalised to (part_id, instance name or None).

    An entry is either a bare id — `"l9110s-module"` — or an object naming the instance:
    `{"part": "tactile-button", "name": "BtnForward"}`. Five buttons without names is not a design
    anyway: you cannot write firmware against "button three".
    """
    entries = []
    for index, entry in enumerate(wanted.get("parts") or []):
        if isinstance(entry, dict):
            if not entry.get("part"):
                raise DesignError("parts[%d] names no `part`: %s", index, json.dumps(entry),
                                  code=design_codes.REQUIREMENTS_FIELD_WRONG)
            name = entry.get("name")
            if name is not None and not (isinstance(name, str) and re.fullmatch(record_kind.SELECTOR_SAFE, name)):
                # P87's attribute half: the instance's name is the component the board is written with, `<chip name="…">`
                raise DesignError("parts[%d] calls its instance %r, but an instance's name is a name — letters, digits and _ "
                                  "(BtnOpen): the board is written with it as code", index, name,
                                  code=design_codes.REQUIREMENTS_FIELD_WRONG)
            entries.append((entry["part"], name))
        elif isinstance(entry, str):
            entries.append((entry, None))
        else:
            raise DesignError("parts[%d] is a %s; an entry is a part id or {part, name}",
                              index, type(entry).__name__, code=design_codes.REQUIREMENTS_FIELD_WRONG)
    return entries


def rails_requested(wanted):
    """
    `{(part_id, instance): {pin: rail}}` for every entry that re-points a power pin's rail.

    Which rail a part sits on is a property of the DESIGN, not of the part: an L9110S runs on
    6 V, 7.4 V or 12 V and its record had to pick one. The RC car shadowed the whole shipped
    record to change the one string `motor` → `traction`, and that copy was then frozen against
    every update to the record (cold test G5, backlog R9). So the requirements file says it:
    `{"part": "l9110s-module", "rails": {"VCC": "traction"}}`.
    """
    overrides = {}
    for index, entry in enumerate(wanted.get("parts") or []):
        if isinstance(entry, dict) and entry.get("rails"):
            rails = entry["rails"]
            if not isinstance(rails, dict) or not all(
                    isinstance(pin, str) and isinstance(rail, str) and rail for pin, rail in rails.items()):
                raise DesignError("parts[%d].rails must map pin names to rail names: %s",
                                  index, json.dumps(rails), code=design_codes.REQUIREMENTS_FIELD_WRONG)
            for pin, rail in rails.items():
                # P87's attribute half: the rail is the net written
                if not re.fullmatch(record_kind.SELECTOR_SAFE, rail):
                    raise DesignError("parts[%d].rails puts %s on %r, but a rail is a name — letters, digits and _ (traction, "
                                      "motor): the board is written with it as code", index, pin, rail,
                                      code=design_codes.REQUIREMENTS_FIELD_WRONG)
            overrides[(entry.get("part"), entry.get("name"))] = rails
    return overrides


def on_rails(part, rails):
    """
    The part's record with the named power pins moved to the design's rails — a COPY, with its
    own `power` list; the argument is left exactly as loaded. (`parts.load` reads the file every
    time, so an in-place edit would reach nothing else today; the copy is the contract, not a
    fix, and the test holds the function to it rather than to a cache that does not exist.)
    """
    for pin in rails:
        if not any(supply.get("pin") == pin for supply in part.get("power") or []):
            powers = ", ".join(s.get("pin", "?") for s in part.get("power") or []) or "none"
            raise DesignError("%s has no power pin %r to put on rail %r; its power pins are %s",
                              part.get("id"), pin, rails[pin], powers, code=design_codes.REQUIREMENTS_FIELD_WRONG)
    return dict(part, power=[dict(supply, rail=rails[supply["pin"]])
                             if supply.get("pin") in rails else supply
                             for supply in part.get("power") or []])


def record(part_id, project):
    """
    The library's record for a part, or a DesignError saying what is wrong with it.

    `parts.load` reads the file outside any try, so a malformed project part was a
    `JSONDecodeError` traceback through `emit_board.py` and `[!!] schematic Traceback …` through the
    spine — the A8 class, one module below the loader (audit B10). Named by part id here, since
    the library resolves the path.
    """
    try:
        return part_records.load(part_id, project)
    except part_records.PartError as broken:
        raise DesignError.of_error(broken, code=design_codes.PART_UNUSABLE) from broken
    except ValueError as broken:
        raise DesignError("the record for %r is not JSON: %s", part_id, broken, code=design_codes.PART_UNUSABLE) from broken
    except OSError as broken:
        raise DesignError("the record for %r could not be read: %s", part_id, broken,
                          code=design_codes.PART_UNUSABLE) from broken


def parts_of(wanted, project, board=None):
    """
    Each requested part as an instance: its record, `_instance` when named, its rails as designed, and each pull-up
    the board's internal one does instead left to the firmware (`firmware_pulls`).
    """
    if board is None:
        try:
            board = board_records.load(project, wanted.get("board"))
        except board_records.BoardError:
            board = None  # no board, no internal pull-up: every resistor stays
    part_list = []
    rails = rails_requested(wanted)
    for part_id, instance in requested_parts(wanted):
        part = dict(record(part_id, project))
        if instance:
            part["_instance"] = instance
        if (part_id, instance) in rails:
            part = on_rails(part, rails[(part_id, instance)])
        part_list.append(firmware_pulls(part, board))
    return part_list


def firmware_pulls(part, board):
    """
    The part with each pull-up the board's internal one does left to the firmware (P204, the PO's rule of 2026-10-12:
    prefer what the board offers). It needs the board's `internal_pull_up_ohms` and a host pull-up marked
    `internal_will_do`. A pin that wakes the chip keeps its resistor, because the internal pull lets go in sleep.
    The pins left to the firmware are listed in `_firmware_pulls`. The board's pull counts only as a finite positive number
    (a fact's `value`, or a bare number where a fact belongs). Any other value reads as a missing fact (P431).
    """
    pull = provenance.read_value(board, "power", "internal_pull_up_ohms")
    # a comparison, not math.isfinite: a 400-digit int is valid JSON and cannot become a float
    if isinstance(pull, bool) or not isinstance(pull, (int, float)) or not 0 < pull < math.inf:
        return part
    wakes = {need.get("pin") for need in part.get("needs") or [] if "wake" in (need.get("needs") or [])}
    left = [host for host in part.get("host_parts") or []
            if host.get("kind") == "pullup" and host.get("internal_will_do") and host.get("pin") not in wakes]
    if not left:
        return part
    return dict(part, host_parts=[host for host in part["host_parts"] if host not in left],
                _firmware_pulls=[host["pin"] for host in left])


def signal_name(part, need):
    """
    The name the assigner knows this need by.

    ONE definition, because there were briefly two. An instance prefixes its signals so five
    buttons are five signals rather than one name five times — and the same mapping written out
    at each use site diverged immediately: the trace lookup was fixed and the unclaimed-signal
    reporter was not, so five correctly wired signals were reported as connected to nothing.
    It lives with the loader because the name is decided when the instance is.
    """
    if part.get("_instance"):
        return "%s_%s" % (part["_instance"].upper(), need["signal"])
    return need["signal"]


# --- MVP --- (P513, #709): a part's signal pinned from the requirements file, as a cable or a connector fixes it
def pin_part_signals(signals, sources, own):
    """
    The part signals with the pins the requirements give them, and the (index, entry) pairs of `own` not used for that.

    An entry with a `pin` whose name is a part signal's sets that signal's pin, once: it IS that signal, so it adds no
    second one. The part's record says the rest (needs, bus, from), so an entry that also gives another key is refused,
    never dropped. A bus line is refused: the assigner places the bus, and a pin split the bus from a
    second part on it (review of #727). So is a name that is a part signal's only when capitals are ignored. An entry
    with no `pin`, or a second pin for one signal, is left for P163's compare, which names both.
    """
    at = {signal["name"]: index for index, signal in enumerate(signals)}
    folded = {name.casefold(): index for name, index in at.items()}
    pinned, unused, signals = set(), [], list(signals)  # pinned: the names an entry already gave a pin
    for index, entry in enumerate(own):
        name = entry["name"]
        if entry.get("pin") and name not in at and name.casefold() in folded:
            raise DesignError("signals[%d] pins %s, and no part has a signal of that name; did you mean %s, %s? A "
                              "signal's name is exact", index, name, signals[folded[name.casefold()]]["name"],
                              sources[folded[name.casefold()]], code=design_codes.REQUIREMENTS_FIELD_WRONG)
        if not entry.get("pin") or name not in at or name in pinned:
            unused.append((index, entry))
            continue
        if signals[at[name]].get("bus"):
            raise DesignError("signals[%d] pins %s, an %s bus line: the assigner places the bus, so drop `pin`",
                              index, sources[at[name]], signals[at[name]]["bus"].upper(),
                              code=design_codes.REQUIREMENTS_FIELD_WRONG)
        extra = sorted(set(entry) - {"name", "pin"})
        if extra:
            raise DesignError("signals[%d] pins %s and also gives %s; an entry that pins a part's signal holds only "
                              "`name` and `pin`, and the part's record says the rest", index, sources[at[name]],
                              ", ".join(extra), code=design_codes.REQUIREMENTS_FIELD_WRONG)
        signals[at[name]] = dict(signals[at[name]], pin=entry["pin"])
        pinned.add(name)
    return signals, unused


def signals_of(part_list, wanted, project):
    """
    Every signal this design asks the host for, ready for `assign_pins`: each instance's, named
    per instance, then the requirements' own.

    Derived HERE, once. `emit_board.main` (`board_emitter.read_inputs` now) derived them and `assign_pins.main` handed the raw
    `parts` entries to the library instead, so the first step every document names crashed on
    the `{part, name}` form every document shows (audit B1), and the two mains could have
    disagreed about which signals a design has. A requirements entry that pins a part's signal is that signal's pin,
    not a second signal (P513, `pin_part_signals`).
    """
    signals, sources = [], []  # sources[i] says where signals[i] came from, for the refusal below
    for part in part_list:
        try:
            asked = parts_library.signals_for([part["id"]], project)
        except part_records.PartError as broken:
            raise DesignError.of_error(broken, code=design_codes.PART_UNUSABLE) from broken
        except (ValueError, OSError) as broken:
            raise DesignError("%s", broken, code=design_codes.PART_UNUSABLE) from broken
        for signal in asked:
            # Signals are per INSTANCE, not per part. Five buttons asking for `BUTTON` produced
            # five signals of one name, which `assign_pins` placed on five pins and every
            # downstream lookup keyed by name then collapsed to whichever came last.
            signals.append(dict(signal, name=signal_name(part, {"signal": signal["name"]})))
            sources.append("%s's %s" % (part.get("_instance") or part["id"], signal["name"]))
    signals, unused = pin_part_signals(signals, sources, list(wanted.get("signals") or []))  # --- MVP --- (P513)
    signals += [entry for _, entry in unused]
    sources += ["signals[%d]" % index for index, _ in unused]  # its index in the file, so a refusal names the right one
    refuse_one_signal_twice(sources, signals)
    return signals


def refuse_one_signal_twice(sources, signals):
    """
    A DesignError naming both sources when two of `signals` share a name (P163, #100), the route the names compare in
    `read` does not see: a `signals` entry written as OPENLID_BUTTON beside an instance called OpenLid — or two unnamed
    parts asking for BUTTON — is ONE signal to the assigner and the generator, which look a signal up by its exact name.
    The assigner placed it twice, the generator traced both pins to one pad, the build passed and the chain said "runs
    end to end". Refused where the signals are derived — `read` cannot, it has no part records; exact, because every
    lookup downstream is.
    """
    placed = {}
    for source, signal in zip(sources, signals):
        if signal["name"] in placed:
            raise DesignError("%s and %s are both %s — one signal, which the pin assigner would place twice and the "
                              "generator trace to one pad from two pins; give one of them a name of its own",
                              placed[signal["name"]], source, signal["name"], code=design_codes.NAME_USED_TWICE)
        placed[signal["name"]] = source


def rules_in(project):
    """
    The project's rules, or an empty dict when it has none. Absent is not an error — `init`
    writes it. Present and unreadable IS one: a rules file nobody can parse must not quietly
    become "no rules", because the generated board would then say every width is unjustified
    while the file that justifies them sits right there.
    """
    path = Path(project) / RULES_PATH
    if not path.exists():
        return {}
    try:
        return fab.read_rules(path)  # --- MVP --- (P434): also refuses a `fabrication` value that is no finite number
    except fab.RulesError as refused:
        raise DesignError("%s", refused, code=design_codes.RULES_REFUSED) from refused


def load(path, project=None, board_id=None):
    """A design from its requirements file. Every way the input is wrong is a DesignError."""
    wanted = read(path)
    root = project_for(path, project)
    try:
        board = board_records.load(root, board_id or wanted.get("board"))
    except board_records.BoardError as broken:
        raise DesignError.of_error(broken, code=design_codes.BOARD_UNUSABLE) from broken
    part_list = parts_of(wanted, root, board)
    return Design(Path(path), root, wanted, board, part_list, signals_of(part_list, wanted, root),
                  rules_in(root))
