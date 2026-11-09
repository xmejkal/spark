"""
The rules that judge what a part asks of a board (W6-S2 P717, W6-S3a P720): the pull-up band, which a module's own I2C
pull-up (`facts.i2c_pullup_ohms`, `i2c_pullup_problems`) and a design's pull-ups (`rules_check`) are judged by, the
capabilities and buses a pin may be asked for (`CAPABILITIES`, `BUSES`, `bus_line_of`), the pad count a footprint name
says, a chip's folder, and the pin-order, host-part, simulation, control and pull-up conflict rules. Moved whole from
`parts.py`. It imports `record_kind` alone of spark, so checks reads it along its arrow down to sourcing.
"""

import re
from pathlib import Path

from spark.records.record_kind import _parse, PIN_LISTS, SELECTOR_SAFE

# --- MVP ---
#: A pull-up weaker than this cannot hold a bus high against its own capacitance; stronger than
#: this and the driving pin cannot pull it down. Wide on purpose — this is a sanity band, not a
#: design calculation, and saying which is which matters.
PULLUP_MIN_OHM = 1000
PULLUP_MAX_OHM = 10000
# --- end MVP ---

#: What a `needs` entry may ask a pin for. THE ONE DEFINITION — `assign_pins` imports it from here rather than keeping
#: its own, because it had its own and the two disagreed: a servo part declaring `needs: ["pwm"]` validated as a good
#: record and then made the pin assigner refuse the whole design. The only way out was to delete a true fact about the
#: part, which is a contract punishing honesty.
#:
#: It lives in the lower module on purpose. A capability is a claim a PART makes, so the file
#: that validates parts owns the vocabulary and the file that consumes it follows.
CAPABILITIES = ("wake", "adc", "pwm")


#: Footprinter families whose trailing number IS the pad count. Deliberately a whitelist, because the obvious shortcut —
#: take the first integer — is wrong in the most damaging direction: `sot23` is a three-pad package named after its
#: body, `0603` is a size in hundredths of an inch, and `sod123` is neither. A rule that read those as 23, 603 and 123
#: pads would contradict every honest part file it met, which is how a useful check gets switched off.
PAD_COUNT_FAMILIES = ("pinrow", "headermodule", "jst_ph_", "jst_sh_", "jst_xh_", "dip", "bh_")


#: The buses a part may put a signal on, and the lines each has, by the board's label for the line with the names
#: vendors print for it. THE definition: `assign_pins` imports it to find the board's pin for a line, and `validate`
#: refuses a record naming a bus or a line not here — where the record is written, not four scripts later (the shape of
#: `CAPABILITIES`, G12). `i2s` was missing from the assigner's own copy for one evening and the shipped MAX98357A could
#: not be placed by the chain while `--validate` called it fine (sprint-4 close audit, C6). A signal named
#: `<BUS>_<LINE>` — `I2S_BCLK` — names its line.
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
    order = part.get("pin_order")
    if not isinstance(order, list) or not any(order):  # a pin_order that is no list is validate's own problem
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


def i2c_pullup_problems(part: dict) -> list:
    """
    A record on an I2C bus says where its pull-ups come from (P55).

    I2C only ever pulls down, and a board may have none of its own — the FireBeetle V1.2+ has none
    anywhere. So the module carries them (`facts.module_has_i2c_pullups`), or the host adds them
    (`host_parts` pull-ups on every bus line); saying neither is how a bus floats. A module
    pull-up must also be one that can hold a bus: the same band `compare_design` judges by.
    """
    lines = [need.get("pin") for need in part.get("needs") or [] if need.get("bus") == "i2c" and need.get("pin")]
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
        if "internal_will_do" in host_part and (host_part["internal_will_do"] is not True or kind != "pullup"):
            problems.append("%s: internal_will_do is true on a pull-up, or absent (P204)" % where)
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
    return problems + chip_problems(part, path, chip, pins)


def chip_problems(part, path, chip, pins):
    """What is wrong with a record's `simulation.wokwi.chip`: its name, its files beside the record, its pins."""
    problems = []
    if chip and not (isinstance(chip, str) and re.fullmatch(SELECTOR_SAFE, chip)):
        # the re-check's probes: a chip's name names its files (`../escape` reached outside the chip folder, and
        # stage_chips copied from there) and is written into wokwi.toml (`x"⏎[[chip]]` was a table of its own)
        return problems + ["simulation.wokwi.chip is %r, but a chip's name is a name — letters, digits and _ (vl6180x, "
                           "l9110s): its files beside the record are named by it, and wokwi.toml is written with it" % (chip,)]
    if chip and isinstance(part.get("id"), str):  # with no plain id the files have no folder, and the id is its own problem
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


def pull_conflicts(part):
    """Each CONFLICT line of `conflicts_of`, as text: what the generator writes into board.tsx."""
    return [conflict["line"] for conflict in conflicts_of(part)]


def conflicts_of(part):
    """
    A pull-down the board adds against the module's own pull-up, said with its arithmetic (P81, B11). The L9110S states
    10 k pull-ups to VCC on its inputs and asked the board for 10 k pull-downs "so both are held low": a divider at half
    the supply, above its 2.5 V input threshold on a 6 V pack. The record's note said so; no output did. Quiet when the
    pin stays under the input-high threshold across the module's whole supply range.

    Each is {pin, line, rests_on, fix, upgrade}. `rests_on` names, as `<part>.<fact>`, the facts it used that nobody has
    verified: none, and it is a problem whose `fix` is the arithmetic's answer; any, and it is an assumption, which
    `upgrade` says how to settle (the PO's rule, 2026-10-05 on #43).
    """
    facts = part.get("facts") or {}
    def value(name):
        return (facts.get(name) or {}).get("value")

    pull_up, high, supply = value("onboard_input_pullups_ohms"), value("input_high_threshold_v"), value("supply_range_v")
    if not isinstance(pull_up, (int, float)):
        return []
    rests_on, upgrade = _rests_on(part, facts, high, supply)
    fix = _holding_low(facts, pull_up, supply)
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
        said.append({"pin": host_part["pin"], "line": line, "rests_on": rests_on, "fix": fix, "upgrade": upgrade})
    return said


def _rests_on(part, facts, high, supply):
    """The facts a CONFLICT used that nobody has verified, as `<part>.<fact>`, and the `upgrade` that settles them."""
    recorded = {"onboard_input_pullups_ohms": True, "input_high_threshold_v": isinstance(high, (int, float)),
                "supply_range_v": isinstance(supply, list) and len(supply) == 2}
    rests_on = sorted("%s.%s" % (part.get("id"), name) for name, usable in recorded.items()  # missing is not verified
                      if not (usable and (facts.get(name) or {}).get("verified")))
    upgrade = "record or verify %s from the maker's own sources (parts.py --fact-set), then run --show again" % ", ".join(rests_on)
    return rests_on, upgrade


def _holding_low(facts, pull_up, supply):
    """
    A CONFLICT's fix: the largest pull-down that holds the pin under the module's input-low threshold across its supply
    range, so it reads low, and what it then draws at rest. Under the input-high threshold alone the level is undefined
    (the refuter on P124), so without an input-low threshold the fix is to record one.
    """
    low = facts.get("input_low_threshold_v") or {}
    if not (isinstance(low.get("value"), (int, float)) and isinstance(supply, list) and len(supply) == 2):
        return ("record the module's input_low_threshold_v, the level it reads as low, then run --show again: "
                "held only under the input-high threshold, the level is undefined")
    largest = int(pull_up * low["value"] / (supply[1] - low["value"]))
    return ("a pull-down under %d ohm holds it under its %g V input-low threshold%s up to %g V, so it reads low; it then "
            "draws up to %.2g mA from the supply at rest" % (largest, low["value"], "" if low.get("verified") else
                                                             " (not verified)", supply[1], 1000 * supply[1] / (pull_up + largest)))
