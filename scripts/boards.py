#!/usr/bin/env python3
"""
Which board this project is built around — resolved in one place, and checked against a contract.

    python3 scripts/boards.py --path        the active board's definition file
    python3 scripts/boards.py --id          the active board's id
    python3 scripts/boards.py --list        every board available to switch to
    python3 scripts/boards.py --paths       their file paths, for tools that take a list
    python3 scripts/boards.py --get chip    one field, by dotted path
    python3 scripts/boards.py --validate    check every board file against the contract
    python3 scripts/boards.py --validate --for-fab
                                            also require what the PCB needs, not just the firmware

Boards are drop-in: add `boards/<id>.json` and put that id in `boards/active.json`. Nothing else
names a board. This file is both the library the Python tools import and the command `/spark:init`,
`/spark:build` and the review skill call, because a second copy of "where is the board file" would
be the exact duplication that boards/ exists to remove.

The contract is enforced rather than documented. A board definition that a person merely
*described* correctly is how the C6 pin map nearly shipped with D3 read as GPIO3; a definition
that a program refuses to load cannot fail that way. Structural validity and fab-readiness are
separate on purpose — the firmware can be built and simulated against a board whose footprint
nobody has verified, and it is better to say so than to either block that work or let an
unverified footprint reach a gerber.
"""

import hashlib
import json
import math
import re
import sys
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import provenance
import store

#: Board definitions ship with this plugin as a LIBRARY, so a project can adopt a verified one
#: without copying a file it would then have to maintain. A project may still keep its own in
#: `boards/`, and its own wins — a definition you have verified yourself always beats a shared
#: one, and a project must never be surprised by a library update.
LIBRARY = Path(__file__).resolve().parent.parent / "boards"

#: Where a project keeps what is its own: which board it uses, and any definitions of its own.
PROJECT_BOARDS_DIR = "boards"
SELECTION_NAME = "active.json"
DEFINITION_SUFFIX = ".json"

#: The resolved, validated board is written here so that every consumer — Make, a Python
#: generator, a TypeScript tool — reads ONE file at a known path instead of each re-implementing
#: the search and the schema check. That duplication was real: a TypeScript copy of this resolver
#: re-checked the schema version, the selection file and the id, and would have had to learn to
#: search a second directory the moment the library existed.
RESOLVED_NAME = "board.json"
SPARK_DIR = ".spark"

#: Files in boards/ that are not board definitions.
NOT_A_BOARD = frozenset({SELECTION_NAME})

#: The only schema version this code understands. A board file claiming a different one is
#: refused rather than read optimistically: the failure mode of guessing is a wrong pin map,
#: which is silent until the hardware is built.
SUPPORTED_SCHEMA = 1

#: What every board definition must carry for the firmware and the simulator to be generated.
REQUIRED_KEYS = ("schema", "id", "name", "chip", "wokwi_part_type",
                 "pins", "wake_capable_gpio", "adc_gpio", "physical")

#: What a board must additionally carry before it can be laid out and fabricated. Kept apart
#: from REQUIRED_KEYS because these are the fields that, if wrong, cost money.
REQUIRED_FOR_FAB = ("footprint_module", "footprint_export")

#: Keys a board file may NOT contain, because they are decisions rather than facts about the
#: hardware. boards/README.md states the rule; this enforces it. `wake_on_high` is the named
#: example and is exactly what went wrong: it was removed from one board file when the rule was
#: written and left in the other, and --validate said "ok" for a day.
#:
#: A fact is true of the board whatever you build with it. A decision is a choice you made, and
#: a board file that accumulates choices stops being swappable, which is the point of boards/.
FORBIDDEN_KEYS = {
    "wake_on_high": ("follows from how the buttons are wired; belongs in the firmware's own settings "
                     "(the smart bin's is config.WAKE_ON_HIGH)"),
    "i2c_freq": "a firmware setting, not a property of the board",
    "i2c_freq_hz": "a firmware setting, not a property of the board",
    "pin_assignments": ("which function sits on which pin is the design "
                        "(assign_pins.py works it out; the smart bin keeps it in mcu-pins.ts)"),
    "signals": ("which function sits on which pin is the design "
                "(assign_pins.py works it out; the smart bin keeps it in mcu-pins.ts)"),
}

#: The role names a board file may use, and what each one means to the scripts that read them.
#:
#: Closed, because an open vocabulary silently disabled a headline check. Two shipped boards
#: described the same hazard — the serial console — under two names, `boot_log_tx` and
#: `console_uart`. `check_design.py` (since cut, 066c4af) knew only the first and `assign_pins.py` only
#: the second, so a serial-parsing part sitting on the console UART was caught on one board and passed without a
#: word on the other. Nothing noticed, because a role nobody consumes looks exactly like a role
#: that is fine. A name outside this set is now an error rather than a silent no-op.
PIN_ROLES = {
    "console_uart": "carries the boot log and the serial console; it moves at every reset",
    "onboard_button": "something is already wired here and can press it",
    "onboard_led": "something is already wired here and will blink whatever you put on it",
    "onboard_display": "a display is already wired here and shows whatever its bus carries",
    "onboard_battery_sense": "a divider from the battery is wired here, so the pin reads the battery voltage",
    "strapping": "sampled at reset; the level here decides how the chip boots",
    "adc2_unusable_with_wifi": "on ADC2, which cannot be read while the radio is on",
    "not_wake_capable": "cannot bring the chip out of deep sleep",
    # Bus roles, read by `assign_pins`: a plain signal takes these last, so a later bus part is
    # not left with nowhere to go. Added 2026-09-29 (backlog P3) after the assigner spent SCK,
    # MI and MO on two LEDs and a button because nothing said they were a bus.
    "spi": "the hardware SPI bus; spent last by signals that could use any pin",
    "i2c": "the hardware I2C bus; spent last by signals that could use any pin",
    # Read by `restricted_pins` (P254, D14): code for a live try that writes one of these numbers is refused.
    "usb": "the chip's own USB D- and D+: driving one drops the USB port the session talks through",
    "flash": "wired to the flash that holds the firmware: driving one can stop the chip",
}

#: Named, so the one role a check singles out is spelled in exactly one place.
CONSOLE_UART = "console_uart"
#: The board's own LED, button, display and battery-level pin, which pins.py names and the build compares with the Wokwi definition (P396).
ONBOARD_LED = "onboard_led"
ONBOARD_BUTTON = "onboard_button"
ONBOARD_DISPLAY = "onboard_display"
ONBOARD_BATTERY_SENSE = "onboard_battery_sense"

#: Ranges a GPIO number must fall in to be a number at all. Deliberately generous — this catches
#: a typo or a silkscreen label parsed as a pin, not a chip-specific mistake.
GPIO_MIN, GPIO_MAX = 0, 63

from spark.core import outcomes, text_guards  # noqa: E402
from spark.core.outcomes import EXIT_OK, EXIT_PROBLEMS as EXIT_INVALID  # noqa: E402


class BoardError(text_guards.ValueMessageError):
    """Error: a board definition that cannot be used, with the reason a person needs to fix it."""


def walk_up(start: Path):
    """
    `start` and every directory above it, nearest first — the one upward walk (audit B17).

    Walks the path as given: a caller that wants it resolved resolves it first (`project_root`
    does). Resolving here turned `/var/…` into `/private/var/…` under `find_toolchain`, whose
    callers compare the path it returns.
    """
    start = Path(start)
    return [start, *start.parents]


def project_root(start: Path = None) -> Path:
    """
    The project this is being run for: the nearest directory up the tree holding
    `boards/active.json` or `.spark/`. Explicit beats clever, so `--project` overrides it. Raises `BoardError`
    when no directory up the tree holds either.
    """
    here = (start or Path.cwd()).resolve()
    for directory in walk_up(here):
        if (directory / PROJECT_BOARDS_DIR / SELECTION_NAME).is_file() \
                or (directory / SPARK_DIR).is_dir():
            return directory
    raise BoardError(
        "no project here: nothing up from %s holds %s/%s or %s/",
        here, PROJECT_BOARDS_DIR, SELECTION_NAME, SPARK_DIR)


#: The plugin's own root: what a design in no project is built from — its shipped boards and
#: parts, and no rules. Every command that reads may fall back to it; `--resolve`, which writes,
#: never does, because writing a stranger's resolved board into the plugin is not a fallback.
PLUGIN_ROOT = Path(__file__).resolve().parent.parent


def project_or_library(start: Path = None) -> Path:
    """
    The nearest project up from `start`, or the plugin's own root when there is none.

    Every script raised "no project here" from a fresh directory while `check_spine` alone fell
    back to the library, so the documented steps could not be followed from nowhere (sprint-4
    audit B5). Callers say so when they land on the library — see `design.is_library`.
    """
    try:
        return project_root(start)
    except BoardError:
        return PLUGIN_ROOT


def _read_json(path: Path, what: str) -> dict:
    if not path.is_file():
        raise BoardError("no %s at %s", what, path)
    try:
        return json.loads(path.read_text())
    except ValueError as broken:
        raise BoardError("%s is not valid JSON: %s", path, broken) from broken


def selection_file(project: Path) -> Path:
    return project / PROJECT_BOARDS_DIR / SELECTION_NAME


def active_id(project: Path) -> str:
    """
    The id of the board this project is currently built around.

    ONE id, and the type is checked rather than assumed. `if not board_id` was the only guard, and
    a non-empty list is truthy — so a project with two boards, which is the first thing anyone with
    two boards tries, got a Python list repr where a board id belongs:

        $ boards.py --id
        ['firebeetle2-esp32s3', 'xiao-esp32-c6']      # exit 0

    `boards/README.md` offers `--id` to Make and every other consumer to interpolate, so that
    string goes straight into a path. `--validate` said `ok` twice, and `--list` dropped the `*`
    marking the active board — an absent character as the only signal that the file is nonsense.
    """
    selection = _read_json(selection_file(project), "board selection")
    board_id = selection.get("board")
    if not board_id:
        raise BoardError('%s names no board (expected a "board" key holding a board id)', selection_file(project))
    if not isinstance(board_id, str):
        raise BoardError(
            "%s holds %r where a board id belongs. "
            "A project is built around ONE board: `.spark/board.json` is one file per project "
            "and every consumer reads it. Two boards means two projects — a car and its remote "
            "are separate designs that happen to talk to each other.", selection_file(project), board_id)
    return board_id


def records(project=None):
    """{id: (layer, path)} for every board definition — the project's own winning over spark's library."""
    return store.records("boards", LIBRARY, project, skip=NOT_A_BOARD)


def definition_path(project: Path, board_id: str = None) -> Path:
    """Where a board's definition lives. Defaults to the active board."""
    board_id = board_id or active_id(project)
    found = records(project).get(board_id) if isinstance(board_id, str) else None
    if found:
        return found[1]
    raise BoardError("no board definition for %r.\n  available: %s", board_id, ", ".join(available(project)) or "(none)")


def available(project: Path) -> list:
    """Every board that could be switched to — the project's own, plus the shipped library."""
    return sorted(records(project))


def footprint_stop(board_id: str, project: Path = None) -> str:
    """
    `emit_footprint.footprint_stop_line` of a board that stops the chain at the footprint stage — its file lacks what the
    footprint is drawn from (`emit_footprint.footprint_gaps`; C-7, P121) — and "" for one that builds on. Said wherever a
    board is offered or picked (F12: the XIAO was listed and picked without a word), never refused: such a board is still a
    choice for pin-map work. A file that cannot be read is not said to stop here; `--validate` names it.
    """
    import emit_footprint  # here, not at the top: it imports this module
    found = records(project).get(board_id)
    try:
        board = _read_json(found[1], "board definition") if found else None
    except BoardError:
        return ""
    return (emit_footprint.footprint_stop_line(board) or "") if isinstance(board, dict) else ""


def load(project: Path, board_id: str = None) -> dict:
    """A board definition, validated. Defaults to the active board."""
    path = definition_path(project, board_id)
    board = _read_json(path, "board definition")
    problems = validate(board, path)
    if problems:
        raise BoardError.of_lines([f"{path} does not meet the board contract:"] + [f"  - {problem}" for problem in problems])
    return board


def _words(value):
    """True for a string with words in it: an empty place would print half a hint."""
    return isinstance(value, str) and bool(value.strip())


class ButtonPlaces:
    """Value: the words that name the BOOT and RESET buttons in a hint, from a record's `physical.buttons`. A record with no
    buttons, or a part of them missing or of the wrong type, gives EMPTY: the plain words, never half a hint."""

    def __init__(self, seen_from=None, boot=None, reset=None):
        self.seen_from, self._boot, self._reset = seen_from, boot, reset

    @staticmethod
    def _button(buttons, key):
        one = buttons.get(key)
        if isinstance(one, dict) and _words(one.get("silkscreen")) and _words(one.get("place")):
            return "%s, %s" % (one["silkscreen"], one["place"])
        return None

    @classmethod
    def from_record(cls, record):
        """The places in a board record, or EMPTY."""
        physical = record.get("physical") if isinstance(record, dict) else None
        buttons = physical.get("buttons") if isinstance(physical, dict) else None
        if not isinstance(buttons, dict) or not _words(buttons.get("seen_from")):
            return cls.EMPTY
        boot, reset = cls._button(buttons, "boot"), cls._button(buttons, "reset")
        return cls(buttons["seen_from"], boot, reset) if boot and reset else cls.EMPTY

    @classmethod
    def of_project(cls, project):
        """The places in the record requirements.json names, or EMPTY when that record cannot be read."""
        try:
            name = json.loads((Path(project) / "requirements.json").read_text()).get("board")
            return cls.from_record(load(project, name)) if name else cls.EMPTY
        except (OSError, ValueError, AttributeError, BoardError):
            return cls.EMPTY

    @property
    def boot(self):
        return "BOOT button (%s)" % self._boot if self._boot else "BOOT button"

    @property
    def reset(self):
        return "RESET (%s)" % self._reset if self._reset else "RESET"

    @property
    def orientation(self):
        """The words after a hint that say which way left and right are seen, or nothing."""
        return ". Left and right as seen with %s" % self.seen_from if self.seen_from else ""


ButtonPlaces.EMPTY = ButtonPlaces()


# --- MVP ---
@dataclass(frozen=True)
class OnboardRole:
    """
    Value: what spark knows of one part that a board carries itself. `constant` is the name pins.py gives it.
    `scenario_verb` is what a scenario does to it (`read`, `press`), or None when no scenario reaches it. `does` and
    `what` are the function the board offers a need, in the words of `parts.VERBS`. `not_in_diagram` is what a passed
    run does not test of a part that no scenario reaches. A row has a verb or a sentence, never both and never neither.
    """

    constant: str
    scenario_verb: Optional[str]
    does: str
    what: str
    not_in_diagram: Optional[str] = None

    def __post_init__(self):
        if bool(self.scenario_verb) == bool(self.not_in_diagram):
            raise ValueError("%s needs a scenario verb or a sentence for what the diagram leaves out, and not both" % self.constant)


#: The board's own parts, one row each, read by pins.py (P236, P353), the build (P396) and the pick (P397). Here, beside
#: the record, because none of them imports the pin map. Each key is a role in PIN_ROLES.
ONBOARD_ROLES = {
    ONBOARD_LED: OnboardRole("ONBOARD_LED", "read", "indicate", "onboard LED light"),
    ONBOARD_BUTTON: OnboardRole("ONBOARD_BUTTON", "press", "input", "onboard button"),
    ONBOARD_DISPLAY: OnboardRole(
        "ONBOARD_DISPLAY", None, "indicate", "onboard display screen",
        "spark adds no part to the diagram for the board's own display, so a passed run does not test what it shows. "
        "Test it on the board."),
    ONBOARD_BATTERY_SENSE: OnboardRole(
        "ONBOARD_BATTERY_SENSE", None, "sense", "onboard battery level",
        "spark adds no battery to the diagram, so a passed run does not test what the board reads on this pin. "
        "Test it on the board."),
}

#: What a board's `power` block offers a need, by fact (P389). A power fact has no pins, no constant and no scenario, so
#: it is no OnboardRole. `battery_input` says `input` and not `connector`, because a board may have pads.
POWER_FUNCTIONS = {
    "charger": {"does": "power", "what": "onboard charger"},
    "regulator": {"does": "power", "what": "onboard voltage regulator"},
    "battery_input": {"does": "connect", "what": "onboard battery input"},
}


def onboard_entries(board):
    """
    (role, OnboardRole, entry) for each role in ONBOARD_ROLES that the board's `pin_roles` names with an object, in table
    order (P389). A `pin_roles` that is no object, or an entry that is none, names nothing. Every reader of the table
    goes through here, so each guards a malformed record the same way.
    """
    pin_roles = board.get("pin_roles")
    if not isinstance(pin_roles, dict):
        return []
    return [(role, spec, pin_roles[role]) for role, spec in ONBOARD_ROLES.items() if isinstance(pin_roles.get(role), dict)]


def pin_labels(entry):
    """The entry's `labels` when it is an object, else {}."""
    return entry["labels"] if isinstance(entry.get("labels"), dict) else {}


def names_pins(entry):
    """
    True when pins.py gives the entry's pins names: `gpio` is a list, and the entry has `labels` or exactly one GPIO.
    A part with no name for its pins is not offered for a need either, so the offer and the pin map cannot drift.
    """
    return isinstance(entry.get("gpio"), list) and (bool(pin_labels(entry)) or len(entry["gpio"]) == 1)


def _power_functions(board):
    """The function of each fact in POWER_FUNCTIONS that the board's `power` holds with a value `is_fact_value` accepts, in table order. pins.py writes no line for it."""
    power = board.get("power")
    if not isinstance(power, dict):
        return []
    return [dict(function) for fact, function in POWER_FUNCTIONS.items()
            if isinstance(power.get(fact), dict) and is_fact_value(power[fact].get("value"))]


def onboard_functions(board):
    """
    What the board offers a need through its own parts: one {"does", "what", "role"} per entry of `onboard_entries` that
    names its pins (`role` is its key in PIN_ROLES, P397), then one {"does", "what"} per power fact, which has no role.
    """
    return ([{"does": spec.does, "what": spec.what, "role": role} for role, spec, entry in onboard_entries(board) if names_pins(entry)]
            + _power_functions(board))


#: The `documents` entry of a board record that holds its Wokwi definition: the JSON of the Wokwi part type.
WOKWI_DEFINITION = "wokwi-board"

_COMMENT = re.compile(r"/\*.*?\*/", re.S)
_GPIO = re.compile(r"GPIO([0-9]+)")
_SHA256 = re.compile(r"[0-9a-f]{64}")


#: The component of a limit about the board's own GPIOs as a whole, and the sentences for a definition spark could not
#: compare (the record names none, or the store lacks it: one sentence for three causes, P397) or a stand-in (P483).
ONBOARD_GPIOS = "onboard GPIOs"
NO_DEFINITION_NAMED = outcomes.NOT_CHECKED_MESSAGE % "the board record names no Wokwi definition"
STAND_IN = "the Wokwi part of %s is a stand-in, where GPIO%d is a bare header pin with no onboard LED or button"
WHY_NOT_KEPT = ("spark's store lacks the Wokwi definition that the board record names, its sha256 differs, or it does "
                "not parse")


@dataclass(frozen=True)
class SimulatedPart:
    """
    Value: what a simulator models of a part type: the GPIOs its pins target (P396). `state` is a word of `outcomes` (OC4):
    `gpios` holds the pins only when RECORDED, `why` says what stopped the reader only when NOT_CHECKED. `is_stand_in` is
    the record's `wokwi_is_stand_in`: its sentence holds while no part is wired to that GPIO (P484 words a wired one).
    """

    state: str
    board_id: str
    gpios: frozenset = frozenset()
    why: Optional[str] = None
    is_stand_in: bool = False

    def why_not_read(self):
        """The sentence for a definition spark could not compare with the GPIOs, or None when it was read (RECORDED)."""
        if self.state == outcomes.NOT_CHECKED:
            return outcomes.NOT_CHECKED_MESSAGE % self.why
        if self.state == outcomes.NONE_RECORDED:
            return NO_DEFINITION_NAMED
        return None

    def why_not_simulated(self, gpio):
        """Why a scenario cannot reach this GPIO, or None: not looked at, no pin of the definition, or a stand-in's header pin."""
        if gpio in self.gpios:
            return STAND_IN % (self.board_id, gpio) if self.is_stand_in else None
        return self.why_not_read() or "the Wokwi definition of %s has no pin on GPIO%d" % (self.board_id, gpio)


def _names_a_kept_file(entry):
    """
    True when a `documents` entry is a table whose `sha256` is 64 lowercase hex characters and whose `file` is a plain
    name (`store.file_name_problem`, and no backslash and no `..`): the only entries that name a place under the store's
    `sources`. Any other would be joined into a path that leaves it (an absolute `sha256`) or opens something else.
    """
    if not isinstance(entry, dict) or not isinstance(entry.get("sha256"), str) or not isinstance(entry.get("file"), str):
        return False
    name = entry["file"]
    return bool(_SHA256.fullmatch(entry["sha256"])) and not store.file_name_problem(name) and "\\" not in name and ".." not in name


def read_simulated_part(board):
    """
    The board's Wokwi definition, kept in the store under the sha256 its record names, as a SimulatedPart. Never None,
    never raises (the reader rule in outcomes.py). A record that is no table, no `documents` table, or no entry for the
    definition: NONE_RECORDED. An entry the store cannot back (the entry names no 64-hex `sha256` and plain `file`, the
    file is missing, its bytes changed, it does not parse as a definition with `pins`): NOT_CHECKED with WHY_NOT_KEPT,
    never a guess that it has no pin.
    Wokwi's own files hold `/* */` comments, so they are cut only when strict JSON fails: a string may hold a `/*`.
    """
    if not isinstance(board, dict):
        return SimulatedPart(outcomes.NONE_RECORDED, "")
    board_id = board.get("id") or ""
    documents = board.get("documents")
    if not isinstance(documents, dict) or WOKWI_DEFINITION not in documents:
        return SimulatedPart(outcomes.NONE_RECORDED, board_id)
    not_kept = SimulatedPart(outcomes.NOT_CHECKED, board_id, why=WHY_NOT_KEPT)
    entry = documents[WOKWI_DEFINITION]
    if not _names_a_kept_file(entry):
        return not_kept
    try:
        payload = (store.place("sources") / entry["sha256"] / entry["file"]).read_bytes()
        if hashlib.sha256(payload).hexdigest() != entry["sha256"]:
            return not_kept
        text = payload.decode("utf-8", "replace")
        try:
            definition = json.loads(text)
        except (ValueError, RecursionError):
            definition = json.loads(_COMMENT.sub("", text))
        pins = definition.get("pins") if isinstance(definition, dict) else None
        if not isinstance(pins, dict):
            return not_kept
        targets = [pin.get("target") for pin in pins.values() if isinstance(pin, dict)]
        gpios = frozenset(int(match.group(1)) for match in (_GPIO.fullmatch(target) for target in targets
                                                            if isinstance(target, str)) if match)
    except (KeyError, TypeError, ValueError, RecursionError, OSError):
        # no file, a digit run too long for int(), what else the JSON or the path holds that raises
        return not_kept
    return SimulatedPart(outcomes.RECORDED, board_id, gpios, is_stand_in=board.get("wokwi_is_stand_in") is True)


#: The sentence that ends a limit about a part the build did not look at, or a part no scenario reaches (P396, P397).
BENCH = "Test it on the board."


def gpio_limits(part, checked, wired=None):
    """
    The GPIOs of the `checked` (spec, entry) pairs that `part`, a definition already read, gives no pin, as (component,
    sentence) limits; a GPIO in `wired`, {gpio: sentence}, has its own sentence (P484). A definition not read gives its
    one "not checked" line.
    """
    if part.state != outcomes.RECORDED:
        return [(ONBOARD_GPIOS, part.why_not_read())]
    said = []
    for spec, entry in checked:
        gpios = entry.get("gpio") if isinstance(entry.get("gpio"), list) else []
        for gpio in (gpio for gpio in gpios if isinstance(gpio, int) and not isinstance(gpio, bool)):
            why = part.why_not_simulated(gpio)
            if gpio in (wired or {}):
                said.append(("%s (GPIO%d)" % (spec.constant, gpio), wired[gpio]))
            elif why:
                said.append(("%s (GPIO%d)" % (spec.constant, gpio),
                             "%s, so spark knows no way for a scenario to %s it. %s" % (why, spec.scenario_verb, BENCH)))
    return said


def onboard_limits(board, wired=None):
    """
    What a passed run does not test of the board's own parts, as (component, sentence) pairs (P396, P389). An LED or
    button that its Wokwi definition gives no pin: spark knows no way for a scenario to reach it. One that spark wired in
    the diagram, a GPIO in `wired` ({gpio: sentence}, from `onboard_parts`, P484), gives that sentence. A record that cannot be
    compared says "not checked", in the list and never as a failure: it is what the build did not look at, as a
    stand-in's sentence is what the simulation cannot show (P37). A part no scenario reaches (the display, the
    battery-level pin) gives its `not_in_diagram` sentence whatever the definition holds, after the GPIO lines. A board with
    no such part gives [].
    """
    entries = onboard_entries(board)
    checked = [(spec, entry) for _, spec, entry in entries if spec.scenario_verb]
    said = gpio_limits(read_simulated_part(board), checked, wired) if checked else []
    return said + [(spec.constant, spec.not_in_diagram) for _, spec, _ in entries if spec.not_in_diagram]


def role_limits(board, roles, definitions=None, key=None):
    """
    {role: [(component, sentence)]} for each of `roles` that the board's `pin_roles` names, in table order (P397): the
    pairs `onboard_limits` gives for that role alone. The Wokwi definition is read only for a role with a scenario verb,
    and once per board when the caller passes the same `definitions`, a dict from `key` to the SimulatedPart already read.
    `key` names the board for that dict: the caller's own (an offer's key), else the record's `id`, which a record may lack.
    A verb role whose definition spark could not compare has the one ONBOARD_GPIOS pair, as in `onboard_limits`.
    """
    definitions = {} if definitions is None else definitions
    key = board.get("id") if key is None else key
    said = {}
    for role, spec, entry in onboard_entries(board):
        if role not in roles:
            continue
        if spec.scenario_verb:
            if key not in definitions:
                definitions[key] = read_simulated_part(board)
            said[role] = gpio_limits(definitions[key], [(spec, entry)])
        else:
            said[role] = [(spec.constant, spec.not_in_diagram)]
    return said
# --- end MVP ---


def resolve(project: Path) -> Path:
    """
    Write the active board, validated, to one known path.

    Every consumer then reads that instead of re-implementing the search and the schema check in
    its own language. The file is derived — regenerate it, never edit it.
    """
    board = load(project)
    destination = project / SPARK_DIR / RESOLVED_NAME
    destination.parent.mkdir(parents=True, exist_ok=True)
    # A distinct key, not "//": board definitions carry their own "//" comment, and merging on
    # that silently dropped the generated-file warning. The test noticed.
    destination.write_text(json.dumps(
        dict({"//generated": "GENERATED by spark's boards.py from boards/active.json. Do not "
                             "edit — run the resolver again. This exists so Make, Python and "
                             "TypeScript read one validated file instead of three copies of a "
                             "search."}, **board),
        indent=2) + "\n")
    return destination


# --- MVP ---
#: What a label of a role entry may be, and what a fact name may be: each becomes a part of a pins.py name, as
#: `ONBOARD_DISPLAY_MOSI` and `ONBOARD_DISPLAY_WIDTH`. `ON` is no label and `on` no fact, because `ONBOARD_BUTTON_ON`
#: holds the active level.
LABEL = re.compile(r"[A-Z0-9]+")
FACT_NAME = re.compile(r"[a-z_]+")
LEVEL_LABEL = "ON"
LEVEL_FACT = "on"


def is_gpio(value):
    return isinstance(value, int) and not isinstance(value, bool)


def is_fact_value(value):
    """True for a value that pins.py writes as a constant: a finite number or a word, never a bool and never a blank word."""
    if isinstance(value, str):
        return bool(value.strip())
    return isinstance(value, (int, float)) and not isinstance(value, bool) and (not isinstance(value, float) or math.isfinite(value))


def fact_value_problems(where, fact):
    """`provenance.fact_problems` of one fact of a board record, and one more problem for a value that is none of a finite number, a word or null."""
    problems = provenance.fact_problems(where, fact)
    value = fact.get("value") if isinstance(fact, dict) else None
    if value is not None and not is_fact_value(value):  # one rule with pins.py, so no fact is dropped in silence
        problems.append("%s.value is %r; it must be a finite number, a word or null" % (where, value))
    return problems


def role_entry_problems(where, role):
    """
    Every way the `gpio`, `labels` and `facts` of one `pin_roles` entry break the contract (P389, P396 row 11), named
    from `where`, which the caller quotes. The entry is a dict that holds `gpio`. A name is quoted with `%r`, because
    `load` prints these with no screen guard. A `gpio` that is no list of GPIO numbers in range is one problem, and
    `labels` and `facts` are then checked against what is there.
    """
    problems = []
    gpio = role["gpio"]
    listed = isinstance(gpio, list) and all(is_gpio(each) for each in gpio)
    if not listed:
        problems.append("%s.gpio is %r; it must be a list of GPIO numbers" % (where, gpio))
        gpio = []
    problems += ["%s.gpio has GPIO%d, outside %d-%d" % (where, each, GPIO_MIN, GPIO_MAX)
                 for each in gpio if not GPIO_MIN <= each <= GPIO_MAX]
    problems += ["%s.gpio has GPIO%d twice" % (where, each) for each in sorted(set(gpio)) if gpio.count(each) > 1]
    labels = role.get("labels", {})
    if not isinstance(labels, dict):
        problems.append("%s.labels is %r; it must be an object of label -> GPIO number" % (where, labels))
        labels = {}
    for label, number in labels.items():
        if not isinstance(label, str) or not LABEL.fullmatch(label) or label == LEVEL_LABEL:
            problems.append("%s.labels has the label %r; a label is capital letters and digits, and not ON" % (where, label))
        if not is_gpio(number) or (listed and number not in gpio):
            problems.append("%s.labels[%r] is %r, which is not a GPIO in %s.gpio" % (where, label, number, where))
    facts = role.get("facts", {})
    if not isinstance(facts, dict):
        problems.append("%s.facts is %r; it must be an object of name -> {value, verified, source}" % (where, facts))
        facts = {}
    for name, fact in facts.items():
        if not isinstance(name, str) or not FACT_NAME.fullmatch(name) or name == LEVEL_FACT:
            problems.append("%s.facts has the name %r; a name is lower-case letters and underscores, and not on" % (where, name))
        elif name.upper() in labels:
            problems.append("%s.facts[%r] has the name of the label %r, so pins.py would write one constant twice"
                            % (where, name, name.upper()))
        problems += fact_value_problems("%s.facts[%r]" % (where, name), fact)
    return problems


def power_problems(board):
    """Every way the facts of POWER_FUNCTIONS in the board's `power` break the contract. A `power` that is no object is one problem."""
    power = board.get("power")
    if power is None:
        return []
    if not isinstance(power, dict):
        return ["power is %r; it must be an object of name -> {value, verified, source}" % (power,)]
    return [problem for fact in POWER_FUNCTIONS if fact in power for problem in fact_value_problems("power[%r]" % fact, power[fact])]
# --- end MVP ---


def _pad_problems(board):
    """Every way the pads of `physical` break the contract: a pin with no pad, an alias to no pad, a doubtful pad that is no pad."""
    # A pad every pin can be reached at. The geometry in `physical` is precise to 0.01 mm, and
    # which label sits on which pad is the one fact that cannot be derived from it — a cold
    # rebuild of the reference board was blocked exactly here. Worse, a name in `pins` that has
    # no pad produces a footprint whose pads the design's traces never reach, silently: the
    # silkscreen says MI where the design says MISO.
    problems = []
    physical = board.get("physical") or {}
    order = physical.get("header_order") or {}
    if order:
        pads = set()
        for key, labels in order.items():
            if key.startswith("//"):
                continue
            pads |= set(labels)
        aliases = physical.get("pad_aliases") or {}
        for name in sorted(board.get("pins") or {}):
            if name not in pads and aliases.get(name) not in pads:
                problems.append(
                    "pins.%s sits on no pad in physical.header_order, and physical.pad_aliases "
                    "does not say which pad it is. A footprint built from this would have no pad "
                    "for it, and every trace to it would silently reach nothing" % name)
        for name, pad in sorted(aliases.items()):
            if pad not in pads:
                problems.append(
                    "physical.pad_aliases maps %s to %r, which is not a pad in header_order"
                    % (name, pad))
        header = physical.get("header")
        doubtful = header.get("doubtful_pads") if isinstance(header, dict) else None
        if doubtful is not None and not isinstance(doubtful, list):
            problems.append("physical.header.doubtful_pads is %r; it must be a list of pad labels" % (doubtful,))
        for name in doubtful if isinstance(doubtful, list) else []:
            if not isinstance(name, str):
                problems.append("physical.header.doubtful_pads holds %r, but each entry is a pad label" % (name,))
            elif name not in pads:
                problems.append("physical.header.doubtful_pads names %r, which is not a pad in header_order" % (name,))
    return problems


def validate(board: dict, path: Path, for_fab: bool = False) -> list:
    """
    Every way this board definition breaks the contract. Empty means it holds.

    Returns a list rather than raising on the first fault so that a person fixing a new board
    file sees all of it at once.
    """
    problems = []

    schema = board.get("schema")
    if schema != SUPPORTED_SCHEMA:
        problems.append(f"schema is {schema!r}, but this code understands only {SUPPORTED_SCHEMA}")

    for key in REQUIRED_KEYS:
        if key not in board:
            problems.append(f"missing required key {key!r}")

    if board.get("id") != path.stem:
        problems.append(f"id is {board.get('id')!r} but the file is named {path.stem!r}; "
                        f"the two must match, because active.json selects by filename")

    # A pad this board can WIRE must have a name in the simulator, or the first design that feeds
    # it is unsimulable. P29 made the FireBeetle's VCC wirable when something drives its rail, and
    # the irrigation controller then stopped at `"VCC" is not a pin of board-esp32-s3-devkitc-1` —
    # the stand-in devkit calls that pin `5V`. Nothing compared the two lists; a person running
    # the chain on one project was the check.
    wokwi_pins = board.get("wokwi_power_pins")
    if isinstance(wokwi_pins, dict) and board.get("wokwi_part_type"):
        for pad in sorted(board.get("power_pads") or {}):
            if pad not in wokwi_pins:
                problems.append(f"power pad {pad!r} has no entry in wokwi_power_pins, so a board "
                                f"that wires it cannot be simulated: the Wokwi part needs the "
                                f"name IT gives that pin")

    pins = board.get("pins")
    if isinstance(pins, dict):
        if not pins:
            problems.append("pins is empty: a board with no pins cannot be wired to anything")
        for label, gpio in pins.items():
            # Two labels sharing one GPIO is legal and common — on the FireBeetle 2 S3 both A4
            # and SS are GPIO10 — so duplicates are not an error. A non-integer is.
            if not isinstance(gpio, int) or isinstance(gpio, bool):
                problems.append(f"pin {label!r} maps to {gpio!r}, which is not a GPIO number")
            elif not GPIO_MIN <= gpio <= GPIO_MAX:
                problems.append(f"pin {label!r} maps to GPIO{gpio}, outside {GPIO_MIN}-{GPIO_MAX}")
    elif pins is not None:
        problems.append("pins must be an object of silkscreen label -> GPIO number")

    for key in ("wake_capable_gpio", "adc_gpio"):
        value = board.get(key)
        if value is None:
            continue
        if not isinstance(value, list) or not all(
                isinstance(gpio, int) and not isinstance(gpio, bool) for gpio in value):
            problems.append(f"{key} must be a list of GPIO numbers")

    problems += _pad_problems(board)

    pin_roles = board.get("pin_roles")
    if pin_roles is not None and not isinstance(pin_roles, dict):
        problems.append("pin_roles is %r; it must be an object of role -> {gpio, note}" % (pin_roles,))
        pin_roles = {}
    for role_name, role in (pin_roles or {}).items():
        where = "pin_roles[%r]" % role_name  # quoted: these problems reach the screen with no guard
        if role_name not in PIN_ROLES:
            problems.append(
                f"{where} is not a role any script reads, so it would be carried "
                f"and ignored. Known: {', '.join(sorted(PIN_ROLES))}")
        if not isinstance(role, dict) or "gpio" not in role or "note" not in role:
            problems.append(f"{where} needs both a 'gpio' list and a 'note'")
            continue
        if not isinstance(role["note"], str) or not role["note"].strip():
            # The note is the whole value of a role: "GPIO0 is special" helps nobody, whereas
            # "held low at reset it enters the bootloader" decides whether a button can go there.
            problems.append(f"{where} has an empty note; say what the caveat is")
        problems.extend(role_entry_problems(where, role))
        level = provenance.read_value(role, "active_level")  # P353, P464: the level an LED lights at or a button reads pressed, bare or a fact
        problems += provenance.fact_problems(f"{where}.active_level", role["active_level"]) if isinstance(role.get("active_level"), dict) else []
        problems += [f"{where}.active_level is {level!r}; it must be 0 or 1"] if level is not None and (type(level) is not int or level not in (0, 1)) else []

    problems += power_problems(board)

    # Decisions must not leak into a facts file, at any depth.
    def forbidden(node, path=""):
        if not isinstance(node, dict):
            return
        for key, value in node.items():
            if key in FORBIDDEN_KEYS:
                where = "%s.%s" % (path, key) if path else key
                problems.append(
                    "%s is a DECISION, not a fact about this board: %s. See boards/README.md"
                    % (where, FORBIDDEN_KEYS[key]))
            forbidden(value, "%s.%s" % (path, key) if path else key)

    forbidden(board)

    physical = board.get("physical")
    if for_fab:
        if not isinstance(physical, dict):
            problems.append("physical is missing, so the board cannot be laid out")
        else:
            for key in REQUIRED_FOR_FAB:
                if not physical.get(key):
                    problems.append(
                        f"physical.{key} is not set: no verified footprint for this board, "
                        f"so it is not ready to be laid out or fabricated")

    # A power pad with no rail would be wired to nothing, and the generator's pad loop skipped
    # such a pad with `continue` — the silent drop G2 removed for module pins, kept for the
    # processor's own. Refused here, where the board file is read, so it never reaches a
    # generator at all (sprint audit A6, item 8).
    import parts  # a board points at its datasheets the way a part does (P62b), and names a rail as a part does
    for pad, supply in sorted((board.get("power_pads") or {}).items()):
        if not isinstance(supply, dict) or not supply.get("rail"):
            problems.append(f"power_pads.{pad} names no rail, so the microcontroller pad would be "
                            f"wired to nothing")
        # P87's attribute half: the pad's trace is written to `net.<RAIL>`, so a rail is a name, never text
        elif not (isinstance(supply["rail"], str) and re.fullmatch(parts.SELECTOR_SAFE, supply["rail"])):
            problems.append(f"power_pads.{pad} rail is {supply['rail']!r}, but a rail is a name — letters, digits and _ "
                            f"(ground, logic, motor): the board is written with it as code")

    # P87's attribute half: board.tsx is written with `.Mcu > .<label>` for each pin and each power pad, `import { <export> }`
    # and `<export name="Mcu">`, so each is a name — the pin's own rule, whole — refused here even when the file carries it
    # consistently; and the id, which names files and is written into the footprint generated from it, is a plain key.
    for label in pins if isinstance(pins, dict) else {}:
        if not re.fullmatch(parts.SELECTOR_SAFE, label):
            problems.append(f"pins key {label!r} is not a name — letters, digits and _ (D3, SDA, A0): the board is written "
                            f"with it as code")
    for pad in board.get("power_pads") if isinstance(board.get("power_pads"), dict) else {}:
        if not re.fullmatch(parts.SELECTOR_SAFE, pad):
            problems.append(f"power_pads key {pad!r} is not a name — letters, digits and _ (3V3, GND1, VCC): the board is "
                            f"written with it as code")
    # concern 1: the footprint's comment quotes the drawing's drill (`NOT the <drill_mm> mm`), so it is a number, never text
    header = physical.get("header") if isinstance(physical, dict) else None
    drill = header.get("drill_mm") if isinstance(header, dict) else None
    if drill is not None and (isinstance(drill, bool) or not isinstance(drill, (int, float))):
        problems.append(f"physical.header.drill_mm is {drill!r}, but it is a number of millimetres (0.9): the footprint "
                        f"generated from it is written with it")
    export = physical.get("footprint_export") if isinstance(physical, dict) else None
    if export and not (isinstance(export, str) and re.fullmatch(parts.SELECTOR_SAFE, export)):
        problems.append(f"physical.footprint_export is {export!r}, but it is a name — letters, digits and _ "
                        f"(FireBeetle2Esp32S3): the board is written with it as code")
    if isinstance(board.get("id"), str) and not store.PLAIN.fullmatch(board["id"]):
        problems.append(f"id is {board['id']!r}, but an id is a plain key — lower-case letters, digits and - "
                        f"(firebeetle2-esp32s3): files are named by it, and it is written into the footprint generated from it")

    problems += parts.document_problems(board)
    return problems


#: Separates the levels of a key path given to --get, e.g. `physical.width_mm`.
KEY_PATH_SEPARATOR = "."


def get(project: Path, key_path: str, board_id: str = None):
    """
    One field out of a board definition, addressed by dotted path.

    A generic accessor rather than a flag per field, because a project's own Makefile or script, and any
    future consumer, should be able to reach a new board fact without this file growing a new option for it.
    """
    value = load(project, board_id)
    for step in key_path.split(KEY_PATH_SEPARATOR):
        if not isinstance(value, dict) or step not in value:
            raise BoardError("no %r in this board definition (stopped at %r)", key_path, step)
        value = value[step]
    return value


def _validate_all(project: Path, for_fab: bool) -> int:
    """Check every board file, not just the active one, and say what is wrong with each."""
    failed = False
    for board_id in available(project):
        path = definition_path(project, board_id)
        try:
            board = _read_json(path, "board definition")
        except BoardError as broken:
            print(f"  {board_id}: {broken}")
            failed = True
            continue
        problems = validate(board, path, for_fab=for_fab)
        marker = "active" if board_id == active_id(project) else "     "
        where = "library" if path.parent == LIBRARY else "project"
        if problems:
            print(f"  {marker}  {board_id} ({where}): {len(problems)} problem(s)")
            for problem in problems:
                print(f"           - {problem}")
            failed = True
        else:
            print(f"  {marker}  {board_id} ({where}): ok")
    return EXIT_INVALID if failed else EXIT_OK


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="boards.py", description="Resolve and check the project's board definitions.")
    what = parser.add_mutually_exclusive_group(required=True)
    what.add_argument("--path", action="store_true", help="the active board's definition file")
    what.add_argument("--id", action="store_true", help="the active board's id")
    what.add_argument("--list", action="store_true", help="every board available to switch to")
    what.add_argument("--paths", action="store_true",
                      help="every board definition file, for tools that take a list")
    what.add_argument("--validate", action="store_true", help="check every board file")
    what.add_argument("--get", metavar="KEY.PATH",
                      help="one field from the active board, e.g. chip or physical.width_mm")
    what.add_argument("--resolve", action="store_true",
                      help="write the validated active board to .spark/board.json")
    parser.add_argument("--for-fab", action="store_true",
                        help="with --validate, also require what the PCB needs")
    parser.add_argument("--project", help="the project to act on (default: found upwards)")
    args = parser.parse_args(argv)

    try:
        # Reading modes may fall back to the plugin's library; the one writing mode may not.
        project = (Path(args.project).resolve() if args.project
                   else project_root() if args.resolve else project_or_library())
        if args.path:
            print(definition_path(project))
        elif args.resolve:
            print(resolve(project))
        elif args.id:
            print(active_id(project))
        elif args.paths:
            # Deliberately not `boards/*.json`: that glob also matches active.json, which is a
            # selection rather than a board. Everything that needs the list should ask here.
            print(" ".join(str(definition_path(project, b)) for b in available(project)))
        elif args.get:
            print(get(project, args.get))
        elif args.list:
            try:
                current = active_id(project)
            except BoardError:
                current = None          # nothing chosen — the library, or a project before init
            for board_id in available(project):
                where = "library" if definition_path(project, board_id).parent == LIBRARY \
                    else "project"
                stop = footprint_stop(board_id, project)
                print(f"  {'*' if board_id == current else ' '} {board_id} ({where}){' ' + stop if stop else ''}")
        else:
            return _validate_all(project, for_fab=args.for_fab)
    except BoardError as broken:
        print(f"boards.py: {broken}", file=sys.stderr)
        return EXIT_INVALID
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
