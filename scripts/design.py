#!/usr/bin/env python3
"""
A design, loaded once: the requirements file, the project it belongs to, the board, the parts as
instances, and the rules.

Three scripts loaded a design on their own — `emit_board.main`, `check_all`'s placeholder list
and `check_spine` — and the copies disagreed in the ways copies do. `emit_board.main` resolved
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

This module resolves and reads. It does not name components or signals for the netlist — that is
`emit_board`'s, because the name is decided by what the emitted file needs — and it does not
assign pins, because only the generator needs that.
"""

import json
import re
import sys
from collections import namedtuple
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import boards  # noqa: E402
import parts as parts_library  # noqa: E402

#: What `load` returns. `parts` are the requested instances: each a copy of its record, with
#: `_instance` set when the requirements named it.
Design = namedtuple("Design", "path project requirements board parts signals rules")

#: Where a project keeps the rules its checks and its generator both read.
RULES_PATH = Path(".spark") / "rules.json"

#: Where a built design's netlist lands, as `tsci build` lays it out: `dist/<name>/circuit.json`,
#: the single-board convention first. Named once — `check_all` discovers by it and `init_project`
#: seeds rules from it, and each had its own copy that the other could drift from (audit A6).
CIRCUIT_PATHS = ("dist/board/circuit.json", "dist/*/circuit.json")


class DesignError(Exception):
    """The input cannot be loaded, and this is why. Always a sentence, never a traceback."""


def read(path):
    """The requirements file as a dict, or a DesignError saying what is wrong with it."""
    path = Path(path)
    if not path.is_file():
        raise DesignError("no requirements at %s" % path)
    try:
        wanted = json.loads(path.read_text())
    except ValueError as broken:
        raise DesignError("%s is not JSON: %s" % (path, broken)) from broken
    except OSError as broken:
        raise DesignError("%s could not be read: %s" % (path, broken)) from broken
    if not isinstance(wanted, dict):
        raise DesignError("%s holds a %s; a requirements file is an object with `parts`"
                          % (path, type(wanted).__name__))
    for index, signal in enumerate(wanted.get("signals") or []):
        # A signal with no name was a KeyError through both mains and "the chain is broken"
        # through the spine (close audit C7). Checked where the file is read, like `parts`.
        if not isinstance(signal, dict) or not isinstance(signal.get("name"), str) or not signal["name"]:
            raise DesignError("%s: signals[%d] needs a `name`; a signal is {name, needs, pin?, bus?}"
                              % (path, index))
        if not isinstance(signal.get("needs", []), list):
            raise DesignError("%s: signals[%d].needs must be a list of what the pin must do"
                              % (path, index))
    return wanted


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
            raise DesignError("no directory at %s — `--project` names a project directory" % chosen)
        return chosen.resolve()
    return boards.project_or_library(Path(path).resolve().parent)


def is_library(project):
    """Whether a design was resolved to the plugin's own root, for want of a project around it."""
    return Path(project).resolve() == boards.PLUGIN_ROOT


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
                raise DesignError("parts[%d] names no `part`: %s" % (index, json.dumps(entry)))
            name = entry.get("name")
            if name is not None and not (isinstance(name, str) and re.fullmatch(parts_library.SELECTOR_SAFE, name)):
                # P87's attribute half: the instance's name is the component the board is written with, `<chip name="…">`
                raise DesignError("parts[%d] calls its instance %r, but an instance's name is a name — letters, digits and _ "
                                  "(BtnOpen): the board is written with it as code" % (index, name))
            entries.append((entry["part"], name))
        elif isinstance(entry, str):
            entries.append((entry, None))
        else:
            raise DesignError("parts[%d] is a %s; an entry is a part id or {part, name}"
                              % (index, type(entry).__name__))
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
                raise DesignError("parts[%d].rails must map pin names to rail names: %s"
                                  % (index, json.dumps(rails)))
            for pin, rail in rails.items():
                if not re.fullmatch(parts_library.SELECTOR_SAFE, rail):  # P87's attribute half: the rail is the net written
                    raise DesignError("parts[%d].rails puts %s on %r, but a rail is a name — letters, digits and _ (traction, "
                                      "motor): the board is written with it as code" % (index, pin, rail))
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
            raise DesignError("%s has no power pin %r to put on rail %r; its power pins are %s"
                              % (part.get("id"), pin, rails[pin],
                                 ", ".join(s.get("pin", "?") for s in part.get("power") or [])
                                 or "none"))
    return dict(part, power=[dict(supply, rail=rails[supply["pin"]])
                             if supply.get("pin") in rails else supply
                             for supply in part.get("power") or []])


def record(part_id, project):
    """
    The library's record for a part, or a DesignError saying what is wrong with it.

    `parts.load` reads the file outside any try, so a malformed project part was a
    `JSONDecodeError` traceback through `emit_board` and `[!!] schematic Traceback …` through the
    spine — the A8 class, one module below the loader (audit B10). Named by part id here, since
    the library resolves the path.
    """
    try:
        return parts_library.load(part_id, project)
    except parts_library.PartError as broken:
        raise DesignError(str(broken)) from broken
    except ValueError as broken:
        raise DesignError("the record for %r is not JSON: %s" % (part_id, broken)) from broken
    except OSError as broken:
        raise DesignError("the record for %r could not be read: %s" % (part_id, broken)) from broken


def parts_of(wanted, project):
    """Each requested part as an instance: its record, `_instance` when named, its rails as designed."""
    part_list = []
    rails = rails_requested(wanted)
    for part_id, instance in requested_parts(wanted):
        part = dict(record(part_id, project))
        if instance:
            part["_instance"] = instance
        if (part_id, instance) in rails:
            part = on_rails(part, rails[(part_id, instance)])
        part_list.append(part)
    return part_list


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


def signals_of(part_list, wanted, project):
    """
    Every signal this design asks the host for, ready for `assign_pins`: each instance's, named
    per instance, then the requirements' own.

    Derived HERE, once. `emit_board.main` derived them and `assign_pins.main` handed the raw
    `parts` entries to the library instead, so the first step every document names crashed on
    the `{part, name}` form every document shows (audit B1), and the two mains could have
    disagreed about which signals a design has.
    """
    signals = []
    for part in part_list:
        try:
            asked = parts_library.signals_for([part["id"]], project)
        except (parts_library.PartError, ValueError, OSError) as broken:
            raise DesignError(str(broken)) from broken
        for signal in asked:
            # Signals are per INSTANCE, not per part. Five buttons asking for `BUTTON` produced
            # five signals of one name, which `assign_pins` placed on five pins and every
            # downstream lookup keyed by name then collapsed to whichever came last.
            signals.append(dict(signal, name=signal_name(part, {"signal": signal["name"]})))
    return signals + list(wanted.get("signals") or [])


def rules_in(project):
    """
    The project's rules, or an empty dict when it has none. Absent is not an error — `init`
    writes it. Present and unreadable IS one: a rules file nobody can parse must not quietly
    become "no rules", because the generated board would then say every width is unjustified
    while the file that justifies them sits right there.
    """
    path = Path(project) / RULES_PATH
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text())
    except (ValueError, OSError) as broken:
        raise DesignError("%s could not be read: %s" % (path, broken)) from broken


def load(path, project=None, board_id=None):
    """A design from its requirements file. Every way the input is wrong is a DesignError."""
    wanted = read(path)
    root = project_for(path, project)
    try:
        board = boards.load(root, board_id or wanted.get("board"))
    except boards.BoardError as broken:
        raise DesignError(str(broken)) from broken
    part_list = parts_of(wanted, root)
    return Design(Path(path), root, wanted, board, part_list, signals_of(part_list, wanted, root),
                  rules_in(root))
