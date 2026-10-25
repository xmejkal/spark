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
from pathlib import Path

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

from outcomes import EXIT_OK, EXIT_PROBLEMS as EXIT_INVALID  # noqa: E402


class BoardError(Exception):
    """A board definition that cannot be used, with the reason a person needs to fix it."""


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
        f"no project here: nothing up from {here} holds {PROJECT_BOARDS_DIR}/{SELECTION_NAME} "
        f"or {SPARK_DIR}/")


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
        raise BoardError(f"no {what} at {path}")
    try:
        return json.loads(path.read_text())
    except ValueError as broken:
        raise BoardError(f"{path} is not valid JSON: {broken}") from broken


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
        raise BoardError(f"{selection_file(project)} names no board "
                         f'(expected a "board" key holding a board id)')
    if not isinstance(board_id, str):
        raise BoardError(
            f'{selection_file(project)} holds {board_id!r} where a board id belongs. '
            f"A project is built around ONE board: `.spark/board.json` is one file per project "
            f"and every consumer reads it. Two boards means two projects — a car and its remote "
            f"are separate designs that happen to talk to each other.")
    return board_id


def records(project=None):
    """{id: (layer, path)} for every board definition — the project's own winning over spark's library."""
    return store.records("boards", LIBRARY, project, skip=NOT_A_BOARD)


def definition_path(project: Path, board_id: str = None) -> Path:
    """Where a board's definition lives. Defaults to the active board."""
    board_id = board_id or active_id(project)
    found = records(project).get(board_id)
    if found:
        return found[1]
    raise BoardError(f"no board definition for {board_id!r}.\n"
                     f"  available: {', '.join(available(project)) or '(none)'}")


def available(project: Path) -> list:
    """Every board that could be switched to — the project's own, plus the shipped library."""
    return sorted(records(project))


def footprint_stop(board_id: str, project: Path = None) -> str:
    """
    `parts.STOPS_AT_FOOTPRINT` for a board that stops the chain at the footprint stage — its file has no header geometry to
    draw the footprint from (`emit_footprint.footprint_gaps`; C-7, P121) — and "" for one that builds on. Said wherever a
    board is offered or picked (F12: the XIAO was listed and picked without a word), never refused: such a board is still a
    choice for pin-map work. A file that cannot be read is not said to stop here; `--validate` names it.
    """
    import emit_footprint  # here, not at the top: it imports this module
    import parts
    found = records(project).get(board_id)
    try:
        board = _read_json(found[1], "board definition") if found else None
    except BoardError:
        return ""
    return parts.STOPS_AT_FOOTPRINT if isinstance(board, dict) and emit_footprint.footprint_gaps(board) else ""


def load(project: Path, board_id: str = None) -> dict:
    """A board definition, validated. Defaults to the active board."""
    path = definition_path(project, board_id)
    board = _read_json(path, "board definition")
    problems = validate(board, path)
    if problems:
        raise BoardError(f"{path} does not meet the board contract:\n" +
                         "\n".join(f"  - {problem}" for problem in problems))
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
    scenario_verb: str | None
    does: str
    what: str
    not_in_diagram: str | None = None

    def __post_init__(self):
        if (self.scenario_verb is None) == (self.not_in_diagram is None):
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
    """The function of each fact in POWER_FUNCTIONS that the board's `power` holds with a value pins.py could write, in table order."""
    power = board.get("power")
    if not isinstance(power, dict):
        return []
    return [dict(function) for fact, function in POWER_FUNCTIONS.items()
            if isinstance(power.get(fact), dict) and is_fact_value(power[fact].get("value"))]


def onboard_functions(board):
    """What the board offers a need through its own parts: one {"does", "what"} per entry of `onboard_entries` that names its pins, then one per power fact."""
    return [{"does": spec.does, "what": spec.what} for _, spec, entry in onboard_entries(board) if names_pins(entry)] + _power_functions(board)


#: The `documents` entry of a board record that holds its Wokwi definition: the JSON of the Wokwi part type.
WOKWI_DEFINITION = "wokwi-board"

_COMMENT = re.compile(r"/\*.*?\*/", re.S)
_GPIO = re.compile(r"GPIO([0-9]+)")


@dataclass(frozen=True)
class SimulatedPart:
    """Value: what a simulator models of one part type, a board included: the GPIOs that its pins target (P396)."""

    board_id: str
    gpios: frozenset

    def why_not_simulated(self, gpio):
        """Why a scenario cannot reach this GPIO, or None when a pin of the definition targets it."""
        if gpio in self.gpios:
            return None
        return "the Wokwi definition of %s has no pin on GPIO%d" % (self.board_id, gpio)


def read_simulated_part(board):
    """
    The board's Wokwi definition, kept in the store under the sha256 its record names, as a SimulatedPart. None when the
    file is missing, its bytes changed, or it does not parse as a definition with `pins`: never a guess that it has no
    pin. The caller asks first whether the record names one.
    Wokwi's own files hold `/* */` comments, so they are cut only when strict JSON fails: a string may hold a `/*`.
    """
    documents = board.get("documents")
    entry = documents.get(WOKWI_DEFINITION) if isinstance(documents, dict) else None
    try:
        payload = (store.place("sources") / entry["sha256"] / entry["file"]).read_bytes()
    except (KeyError, TypeError, OSError):  # no entry, a field missing or of the wrong type, no file
        return None
    if hashlib.sha256(payload).hexdigest() != entry["sha256"]:
        return None
    text = payload.decode("utf-8", "replace")
    try:
        definition = json.loads(text)
    except (ValueError, RecursionError):
        try:
            definition = json.loads(_COMMENT.sub("", text))
        except (ValueError, RecursionError):
            return None
    pins = definition.get("pins") if isinstance(definition, dict) else None
    if not isinstance(pins, dict):
        return None
    targets = [pin.get("target") for pin in pins.values() if isinstance(pin, dict)]
    gpios = frozenset(int(match.group(1)) for match in (_GPIO.fullmatch(target) for target in targets
                                                        if isinstance(target, str)) if match)
    return SimulatedPart(board.get("id") or "", gpios)
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


def board_fact_problems(where, fact):
    """Every way one fact of a board record breaks the contract: `provenance.fact_problems`, and a value that is none of a finite number, a word or null."""
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
        problems += board_fact_problems("%s.facts[%r]" % (where, name), fact)
    return problems


def power_problems(board):
    """Every way the facts of POWER_FUNCTIONS in the board's `power` break the contract. A `power` that is no object is one problem."""
    power = board.get("power")
    if power is None:
        return []
    if not isinstance(power, dict):
        return ["power is %r; it must be an object of name -> {value, verified, source}" % (power,)]
    return [problem for fact in POWER_FUNCTIONS if fact in power for problem in board_fact_problems("power[%r]" % fact, power[fact])]
# --- end MVP ---


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

    # A pad every pin can be reached at. The geometry in `physical` is precise to 0.01 mm, and
    # which label sits on which pad is the one fact that cannot be derived from it — a cold
    # rebuild of the reference board was blocked exactly here. Worse, a name in `pins` that has
    # no pad produces a footprint whose pads the design's traces never reach, silently: the
    # silkscreen says MI where the design says MISO.
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
        if "active_level" in role and (type(role["active_level"]) is not int or role["active_level"] not in (0, 1)):
            # P353: the level that lights an LED or that a pressed button reads, which firmware writes as a number.
            problems.append(f"{where}.active_level is {role['active_level']!r}; it must be 0 or 1")

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
            raise BoardError(f"no {key_path!r} in this board definition "
                             f"(stopped at {step!r})")
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
