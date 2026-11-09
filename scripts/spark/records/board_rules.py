"""
The rules a board record is held to (P724), as `part_rules` holds a part's: one named rule per function, each
`(board, validation) -> list` of problems, in the order of `RULES`, which `board_records.BOARD` runs, and the names only
they read (the forbidden keys, the fab keys, the shape of a label and a fact). The names `board_records` code and other
modules read too (`PIN_ROLES`, `POWER_FUNCTIONS`, `GPIO_MIN`, `GPIO_MAX`, `is_gpio`, `is_pin_map_constant`) live here,
and `board_records` imports them, so `board_records.PIN_ROLES` still works. It imports the records area below it, never
`board_records`.
"""

import math
import re

from spark.records import board_pads
from spark.records import provenance
from spark.records import record_kind
from spark.records import store

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

#: Ranges a GPIO number must fall in to be a number at all. Deliberately generous — this catches
#: a typo or a silkscreen label parsed as a pin, not a chip-specific mistake.
GPIO_MIN, GPIO_MAX = 0, 63

# --- MVP ---
#: What a board's `power` block offers a need, by fact (P389). A power fact has no pins, no constant and no scenario, so
#: it is no OnboardRole. `battery_input` says `input` and not `connector`, because a board may have pads.
POWER_FUNCTIONS = {
    "charger": {"does": "power", "what": "onboard charger"},
    "regulator": {"does": "power", "what": "onboard voltage regulator"},
    "battery_input": {"does": "connect", "what": "onboard battery input"},
}
# --- end MVP ---


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


def is_pin_map_constant(value):
    """True for a value that pins.py writes as a constant: a finite number or a word, never a bool and never a blank word."""
    if isinstance(value, str):
        return bool(value.strip())
    return isinstance(value, (int, float)) and not isinstance(value, bool) and (not isinstance(value, float) or math.isfinite(value))


def board_fact_problems(where, fact):
    """`provenance.fact_problems` of one fact of a board record, and one more problem for a value that is none of a finite number, a word or null."""
    problems = provenance.fact_problems(where, fact)
    value = fact.get("value") if isinstance(fact, dict) else None
    if value is not None and not is_pin_map_constant(value):  # one rule with pins.py, so no fact is dropped in silence
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


def power_problems(board, validation):
    """Every way the facts of POWER_FUNCTIONS in the board's `power` break the contract. A `power` that is no object is one problem."""
    power = board.get("power")
    if power is None:
        return []
    if not isinstance(power, dict):
        return ["power is %r; it must be an object of name -> {value, verified, source}" % (power,)]
    return [problem for fact in POWER_FUNCTIONS if fact in power for problem in board_fact_problems("power[%r]" % fact, power[fact])]
# --- end MVP ---


def pad_problems(board, validation):
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
        aliases = board_pads.BoardPads.from_record(board).aliases
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


def id_problems(board, validation):
    """The id names the file."""
    if board.get("id") != validation.path.stem:
        return [f"id is {board.get('id')!r} but the file is named {validation.path.stem!r}; "
                f"the two must match, because active.json selects by filename"]
    return []


def wokwi_power_pin_problems(board, validation):
    """Each power pad with no name in the simulator, when the record names its Wokwi power pins."""
    # A pad this board can WIRE must have a name in the simulator, or the first design that feeds
    # it is unsimulable. P29 made the FireBeetle's VCC wirable when something drives its rail, and
    # the irrigation controller then stopped at `"VCC" is not a pin of board-esp32-s3-devkitc-1` —
    # the stand-in devkit calls that pin `5V`. Nothing compared the two lists; a person running
    # the chain on one project was the check.
    wokwi_pins = board.get("wokwi_power_pins")
    if not (isinstance(wokwi_pins, dict) and board.get("wokwi_part_type")):
        return []
    return [f"power pad {pad!r} has no entry in wokwi_power_pins, so a board "
            f"that wires it cannot be simulated: the Wokwi part needs the "
            f"name IT gives that pin" for pad in sorted(board.get("power_pads") or {}) if pad not in wokwi_pins]


def pin_problems(board, validation):
    """`pins` that is no object or empty, and each label that maps to no GPIO number in range."""
    pins = board.get("pins")
    if not isinstance(pins, dict):
        return [] if pins is None else ["pins must be an object of silkscreen label -> GPIO number"]
    problems = [] if pins else ["pins is empty: a board with no pins cannot be wired to anything"]
    for label, gpio in pins.items():
        # Two labels sharing one GPIO is legal and common — on the FireBeetle 2 S3 both A4
        # and SS are GPIO10 — so duplicates are not an error. A non-integer is.
        if not isinstance(gpio, int) or isinstance(gpio, bool):
            problems.append(f"pin {label!r} maps to {gpio!r}, which is not a GPIO number")
        elif not GPIO_MIN <= gpio <= GPIO_MAX:
            problems.append(f"pin {label!r} maps to GPIO{gpio}, outside {GPIO_MIN}-{GPIO_MAX}")
    return problems


def gpio_list_problems(board, validation):
    """A `wake_capable_gpio` or `adc_gpio` that is there and is no list of GPIO numbers."""
    problems = []
    for key in ("wake_capable_gpio", "adc_gpio"):
        value = board.get(key)
        if value is not None and (not isinstance(value, list) or not all(
                isinstance(gpio, int) and not isinstance(gpio, bool) for gpio in value)):
            problems.append(f"{key} must be a list of GPIO numbers")
    return problems


def pin_role_problems(board, validation):
    """A `pin_roles` that is no object, and each role no script reads, with no gpio or note, or whose entry breaks the contract."""
    pin_roles = board.get("pin_roles")
    if pin_roles is not None and not isinstance(pin_roles, dict):
        return ["pin_roles is %r; it must be an object of role -> {gpio, note}" % (pin_roles,)]
    problems = []
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
    return problems


def forbidden_key_problems(node, validation, path=""):
    """Each key of FORBIDDEN_KEYS in the record or an object inside it, depth first, named by its `path` of keys."""
    # Decisions must not leak into a facts file, at any depth.
    if not isinstance(node, dict):
        return []
    problems = []
    for key, value in node.items():
        where = "%s.%s" % (path, key) if path else key
        if key in FORBIDDEN_KEYS:
            problems.append(
                "%s is a DECISION, not a fact about this board: %s. See boards/README.md"
                % (where, FORBIDDEN_KEYS[key]))
        problems += forbidden_key_problems(value, validation, where)
    return problems


def fab_key_problems(board, validation):
    """For the fab contract (`for_fab`) alone: no `physical`, or a key of REQUIRED_FOR_FAB it does not set."""
    physical = board.get("physical")
    if not validation.for_fab:
        return []
    if not isinstance(physical, dict):
        return ["physical is missing, so the board cannot be laid out"]
    return [f"physical.{key} is not set: no verified footprint for this board, "
            f"so it is not ready to be laid out or fabricated" for key in REQUIRED_FOR_FAB if not physical.get(key)]


def power_pad_rail_problems(board, validation):
    """Each power pad that names no rail, or a rail that is not a name."""
    # A power pad with no rail would be wired to nothing, and the generator's pad loop skipped
    # such a pad with `continue` — the silent drop G2 removed for module pins, kept for the
    # processor's own. Refused here, where the board file is read, so it never reaches a
    # generator at all (sprint audit A6, item 8).
    problems = []
    for pad, supply in sorted((board.get("power_pads") or {}).items()):
        if not isinstance(supply, dict) or not supply.get("rail"):
            problems.append(f"power_pads.{pad} names no rail, so the microcontroller pad would be "
                            f"wired to nothing")
        # P87's attribute half: the pad's trace is written to `net.<RAIL>`, so a rail is a name, never text
        elif not (isinstance(supply["rail"], str) and re.fullmatch(record_kind.SELECTOR_SAFE, supply["rail"])):
            problems.append(f"power_pads.{pad} rail is {supply['rail']!r}, but a rail is a name — letters, digits and _ "
                            f"(ground, logic, motor): the board is written with it as code")
    return problems


def selector_name_problems(board, validation):
    """Each `pins` key, alias pad and `power_pads` key that is not a name."""
    # P87's attribute half: board.tsx holds each pins key, alias pad, power_pads key, export (names) and id (a key).
    problems = []
    pins = board.get("pins")
    for kind, label in ([("pins key", key) for key in (pins if isinstance(pins, dict) else {})]  # --- MVP --- (P512)
                        + [("alias pad", pad) for pad in sorted(board_pads.BoardPads.from_record(board).alias_pads(), key=str)]):
        if not re.fullmatch(record_kind.SELECTOR_SAFE, str(label)):  # an alias pad too: `.Mcu > .<pad>` takes it
            problems.append(f"{kind} {label!r} is not a name — letters, digits and _ (D3, SDA, A0): the board is written "
                            f"with it as code")
    for pad in board.get("power_pads") if isinstance(board.get("power_pads"), dict) else {}:
        if not re.fullmatch(record_kind.SELECTOR_SAFE, pad):
            problems.append(f"power_pads key {pad!r} is not a name — letters, digits and _ (3V3, GND1, VCC): the board is "
                            f"written with it as code")
    return problems


def drill_problems(board, validation):
    """A `physical.header.drill_mm` that is there and is no number."""
    # concern 1: the footprint's comment quotes the drawing's drill (`NOT the <drill_mm> mm`), so it is a number, never text
    physical = board.get("physical")
    header = physical.get("header") if isinstance(physical, dict) else None
    drill = header.get("drill_mm") if isinstance(header, dict) else None
    if drill is not None and (isinstance(drill, bool) or not isinstance(drill, (int, float))):
        return [f"physical.header.drill_mm is {drill!r}, but it is a number of millimetres (0.9): the footprint "
                f"generated from it is written with it"]
    return []


def footprint_export_problems(board, validation):
    """A `physical.footprint_export` that is there and is not a name."""
    physical = board.get("physical")
    export = physical.get("footprint_export") if isinstance(physical, dict) else None
    if export and not (isinstance(export, str) and re.fullmatch(record_kind.SELECTOR_SAFE, export)):
        return [f"physical.footprint_export is {export!r}, but it is a name — letters, digits and _ "
                f"(FireBeetle2Esp32S3): the board is written with it as code"]
    return []


def plain_id_problems(board, validation):
    """An id that is a string and not a plain key."""
    if isinstance(board.get("id"), str) and not store.PLAIN.fullmatch(board["id"]):
        return [f"id is {board['id']!r}, but an id is a plain key — lower-case letters, digits and - "
                f"(firebeetle2-esp32s3): files are named by it, and it is written into the footprint generated from it"]
    return []


def board_document_problems(board, validation):
    """`record_kind.document_problems` of the record."""
    return record_kind.document_problems(board)


#: The board's rules, in the order `board_records.BOARD` runs them after the shared schema and required-key checks.
RULES = (id_problems, wokwi_power_pin_problems, pin_problems, gpio_list_problems, pad_problems, pin_role_problems,
         power_problems, forbidden_key_problems, fab_key_problems, power_pad_rail_problems, selector_name_problems,
         drill_problems, footprint_export_problems, plain_id_problems, board_document_problems)
