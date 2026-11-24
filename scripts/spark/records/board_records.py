"""
The board records: which board this project is built around — resolved in one place, and checked against a contract.

Boards are drop-in: add `boards/<id>.json` and name its id in the project's requirements.json (`board`, D35). The
selection in `boards/active.json` names the board only when the requirements name none (P988). This module is the
library the Python tools import, and the CLI `scripts/boards.py` is the command `/spark:init`, `/spark:build` and the
review skill call (P718), because a second copy of "where is the board file" would be the exact duplication that
boards/ exists to remove. The contract is `BOARD`, a `record_kind.RecordKind` whose rules live in `board_rules` (P724).
`RecordFinder` (`areas/records.md`) comes with P342.

The contract is enforced rather than documented. A board definition that a person merely
*described* correctly is how the C6 pin map nearly shipped with D3 read as GPIO3; a definition
that a program refuses to load cannot fail that way. Structural validity and fab-readiness are
separate on purpose — the firmware can be built and simulated against a board whose footprint
nobody has verified, and it is better to say so than to either block that work or let an
unverified footprint reach a gerber.
"""

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from spark.records import board_rules
from spark.records import chip_table
from spark.records import record_kind
from spark.records import records_codes
from spark.records import store
# Read here and, as board_records' own names, by pin_assigner, restricted_pins, onboard_parts and the tests (P724).
from spark.records.board_rules import (ADC2_UNUSABLE_WITH_WIFI, adc2_unread_gpio, GPIO_MAX, GPIO_MIN,  # noqa: F401
                                       BAND_WORDS, is_gpio, is_pin_map_constant, PIN_ROLES, POWER_FUNCTIONS,
                                       RADIO_FUNCTIONS)

#: Board definitions ship with this plugin as a LIBRARY, so a project can adopt a verified one
#: without copying a file it would then have to maintain. A project may still keep its own in
#: `boards/`, and its own wins — a definition you have verified yourself always beats a shared
#: one, and a project must never be surprised by a library update.
LIBRARY = Path(__file__).resolve().parents[3] / "boards"

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

#: Named, so the one role a check singles out is spelled in exactly one place.
CONSOLE_UART = "console_uart"
#: The board's own LED, button, display and battery-level pin, which pins.py names and the build compares with the Wokwi definition (P396).
ONBOARD_LED = "onboard_led"
ONBOARD_BUTTON = "onboard_button"
ONBOARD_DISPLAY = "onboard_display"
ONBOARD_BATTERY_SENSE = "onboard_battery_sense"

from spark.core import errors, outcomes  # noqa: E402


class BoardError(errors.CodedMessageError):
    """Error: a board definition that cannot be used, with the reason a person needs to fix it, and its `code` (records_codes)."""


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
    raise BoardError("no project here: nothing up from %s holds %s/%s or %s/",
        here, PROJECT_BOARDS_DIR, SELECTION_NAME, SPARK_DIR, code=records_codes.NO_PROJECT_HERE)


#: The plugin's own root: what a design in no project is built from — its shipped boards and
#: parts, and no rules. Every command that reads may fall back to it; `--resolve`, which writes,
#: never does, because writing a stranger's resolved board into the plugin is not a fallback.
PLUGIN_ROOT = Path(__file__).resolve().parents[3]


def project_or_library(start: Path = None) -> Path:
    """
    The nearest project up from `start`, or the plugin's own root when there is none.

    Every script raised "no project here" from a fresh directory while `check_spine` alone fell
    back to the library, so the documented steps could not be followed from nowhere (sprint-4
    audit B5). Callers say so when they land on the library — see `loader.is_library`.
    """
    try:
        return project_root(start)
    except BoardError:
        return PLUGIN_ROOT


def _read_json(path: Path, what: str) -> dict:
    if not path.is_file():
        raise BoardError("no %s at %s", what, path, code=records_codes.BOARD_FILE_MISSING)
    try:
        return json.loads(path.read_text())
    except ValueError as broken:
        raise BoardError("%s is not valid JSON: %s", path, broken, code=records_codes.RECORD_FILE_BROKEN) from broken


def selection_file(project: Path) -> Path:
    return project / PROJECT_BOARDS_DIR / SELECTION_NAME


def active_id(project: Path) -> str:
    """
    The id of the board the selection, `boards/active.json`, names. The project's board is `project_board_id` (P988).

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
        raise BoardError('%s names no board (expected a "board" key holding a board id)', selection_file(project), code=records_codes.NO_BOARD_SELECTED)
    if not isinstance(board_id, str):
        raise BoardError(
            "%s holds %r where a board id belongs. "
            "A project is built around ONE board: `.spark/board.json` is one file per project "
            "and every consumer reads it. Two boards means two projects — a car and its remote "
            "are separate designs that happen to talk to each other.", selection_file(project), board_id, code=records_codes.NO_BOARD_SELECTED)
    return board_id


#: The file whose `board` names the project's board (D35, P988), and the line said once when it cannot be read.
REQUIREMENTS_NAME, NOT_MARKED = "requirements.json", "no board is marked: %s"


def requirements_board(project: Path):
    """requirements.json's `board` (D35, P988), or None for no requirements.json, no key, `null` or `""`. A file that
    cannot be read, is no JSON object or holds any other value that is no string is a BoardError (RECORD_FILE_BROKEN)."""
    requirements = Path(project) / REQUIREMENTS_NAME
    if not requirements.is_file():
        return None
    wanted = _read_json(requirements, "requirements file")
    if not isinstance(wanted, dict):
        raise BoardError("%s is not a JSON object", requirements, code=records_codes.RECORD_FILE_BROKEN)
    named = wanted.get("board")
    if named is not None and not isinstance(named, str):
        raise BoardError("%s holds %r where one board id belongs", requirements, named, code=records_codes.RECORD_FILE_BROKEN)
    return named or None


def project_board_id(project: Path) -> str:
    """The id of the project's board (D35, P988): requirements.json's `board`, else the selection (`active_id`). A
    requirements.json that cannot be read is a BoardError, never a quiet fall back to the selection."""
    return requirements_board(project) or active_id(project)


def marked_board(project: Path):
    """(the project's board id, None) for `--list` and `--validate` (P988). A broken requirements.json gives (None, its
    sentence). No file that names a board (the library, a folder with no selection, P989) gives (None, None)."""
    try:
        named = requirements_board(project)
    except BoardError as broken:
        return None, str(broken)
    try:
        return named or active_id(project), None
    except BoardError:
        return None, None


def records(project=None):
    """{id: (layer, path)} for every board definition — the project's own winning over the store's shelf (P989), and the
    shelf over spark's library."""
    return store.records("boards", LIBRARY, project, skip=NOT_A_BOARD)


def definition_path(project: Path, board_id: str = None) -> Path:
    """Where a board's definition lives. Defaults to the project's board (`project_board_id`)."""
    board_id = board_id or project_board_id(project)
    found = records(project).get(board_id) if isinstance(board_id, str) else None
    if found:
        return found[1]
    raise BoardError("no board definition for %r.\n  available: %s", board_id, ", ".join(available(project)) or "(none)", code=records_codes.NO_BOARD_DEFINITION)


def available(project: Path) -> list:
    """Every board that could be switched to — the project's own, the store's shelf (P989) and the shipped library."""
    return sorted(records(project))


def load(project: Path, board_id: str = None) -> dict:
    """A board definition, validated. Defaults to the project's board (`project_board_id`)."""
    path = definition_path(project, board_id)
    board = _read_json(path, "board definition")
    problems = validate(board, path)
    if problems:
        raise BoardError.of_lines([f"{path} does not meet the board contract:"] + [f"  - {problem}" for problem in problems], code=records_codes.BOARD_CONTRACT_BROKEN)
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
        """The places in the record of the project's board (D35), or EMPTY when that record cannot be read."""
        try:
            return cls.from_record(load(project))
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
    `what` are the function the board offers a need, in `record_kind.VERBS`' words. `not_in_diagram` is what a passed
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
    """The function of each fact in POWER_FUNCTIONS that the board's `power` holds with a value `is_pin_map_constant` accepts, in table order. pins.py writes no line for it."""
    power = board.get("power")
    if not isinstance(power, dict):
        return []
    return [dict(function) for fact, function in POWER_FUNCTIONS.items()
            if isinstance(power.get(fact), dict) and is_pin_map_constant(power[fact].get("value"))]


def _radio_functions(board, table=None):
    """The function of each radio of the board's chip in `table`, a chip_table.ChipTable, by default `data/chips.json`
    (P990), in RADIOS order. The Wi-Fi function of a chip with a band also holds it as `band` (P1013), which only
    `shown_what` reads."""
    table, chip = chip_table.load() if table is None else table, board.get("chip")
    band, functions = table.wifi_band(chip), []
    for name in table.radios(chip):
        functions.append(dict(RADIO_FUNCTIONS[name], band=band) if name == "wifi" and band else dict(RADIO_FUNCTIONS[name]))
    return functions


def onboard_functions(board):
    """
    What the board offers a need through its own parts: one {"does", "what", "role"} per entry of `onboard_entries` that
    names its pins (`role` is its key in PIN_ROLES, P397), then one {"does", "what"} per power fact, then one per radio
    of the board's chip in `data/chips.json` (P990), the Wi-Fi one with the chip's `band` (P1013). A power fact and a
    radio have no role.
    """
    return ([{"does": spec.does, "what": spec.what, "role": role} for role, spec, entry in onboard_entries(board) if names_pins(entry)]
            + _power_functions(board) + _radio_functions(board))


def shown_what(function):
    """The words a `--match` line shows for `function` (P1013): its `what`, with its `band` inside the closing bracket, as
    "onboard Wi-Fi radio (WiFi; 2.4 GHz only)". A `band` that is no words, or a `what` with no closing bracket, gives
    `what` as it is. The matchers read `what` alone, so the band never moves a score."""
    what, band = function.get("what"), function.get("band")
    if isinstance(band, str) and band.strip() and isinstance(what, str) and what.endswith(")"):
        return what[:-1] + BAND_WORDS % band
    return what


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


def names_a_kept_file(entry):
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
    if not names_a_kept_file(entry):
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
    sentence) limits. A definition not read gives its one "not checked" line first. A GPIO in `wired`, {gpio: sentence},
    gives its own sentence whether the definition was read or not (P484).
    """
    said = [] if part.state == outcomes.RECORDED else [(ONBOARD_GPIOS, part.why_not_read())]
    for spec, entry in checked:
        gpios = entry.get("gpio") if isinstance(entry.get("gpio"), list) else []
        for gpio in (gpio for gpio in gpios if isinstance(gpio, int) and not isinstance(gpio, bool)):
            why = part.state == outcomes.RECORDED and part.why_not_simulated(gpio)
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


def role_limits(board, roles, definitions=None, key=None, wired=None):
    """
    {role: [(component, sentence)]} for each of `roles` that the board's `pin_roles` names, in table order (P397): the
    pairs `onboard_limits` gives for that role alone, with the same `wired` ({gpio: sentence}, P778). The Wokwi definition is read only for a role with a scenario verb,
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
            said[role] = gpio_limits(definitions[key], [(spec, entry)], wired)
        else:
            said[role] = [(spec.constant, spec.not_in_diagram)]
    return said
# --- end MVP ---


def resolve(project: Path) -> Path:
    """
    Write the project's board (`project_board_id`), validated, to one known path.

    Every consumer then reads that instead of re-implementing the search and the schema check in
    its own language. The file is derived — regenerate it, never edit it.
    """
    board = load(project)
    destination = project / SPARK_DIR / RESOLVED_NAME
    destination.parent.mkdir(parents=True, exist_ok=True)
    # A distinct key, not "//": board definitions carry their own "//" comment, and merging on
    # that silently dropped the generated-file warning. The test noticed.
    destination.write_text(json.dumps(
        dict({"//generated": "GENERATED by spark's boards.py from the project's board (requirements.json, else "
                             "boards/active.json). Do not edit — run the resolver again. This exists so Make, Python "
                             "and TypeScript read one validated file instead of three copies of a search."}, **board),
        indent=2) + "\n")
    return destination


#: The board kind (P724): its rules are `board_rules.RULES`. A list, not a raise at the first fault, so that a person
#: fixing a new board file sees all of it at once.
BOARD = record_kind.RecordKind("board", SUPPORTED_SCHEMA, REQUIRED_KEYS, board_rules.RULES)
#: Every way a board definition breaks the contract, and with `for_fab=True` the fab contract too. Empty means it holds.
validate = BOARD.validate


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
            raise BoardError("no %r in this board definition (stopped at %r)", key_path, step, code=records_codes.NO_SUCH_FIELD)
        value = value[step]
    return value
