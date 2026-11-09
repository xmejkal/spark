"""
The part records, read and checked (W6-S3a, P720), as `board_records` does for a board: where a record's definition is
(`definition_path`), loading one (`load`) and finding one in any folder (`any_record`), the part kind `PART` with its
named rules, one per function (P724), and `validate = PART.validate` with the schema and the names it holds a record
to, what a record does (`function_of`, `function_problems`, `aliases`), and a broken record said as one line
(`broken_problems`). A part that cannot be used is a `PartError` with its `sourcing_codes` code. Moved whole from
`parts.py`. It imports `record_kind`, `part_rules` and the records area below it, never `parts.py`.
"""

import functools
import json
import re
from pathlib import Path

from spark.core.errors import CodedMessageError
from spark.records import board_records
from spark.records import provenance
from spark.records import record_kind
from spark.records import store
from spark.records.record_kind import (
    _absent, available, DEFINITION_SUFFIX, document_problems, owes, _parse, PIN_LISTS, record_home, RecordKind,
    REQUIRED_KEYS, RETIRED, SELECTOR_SAFE, _shape_problems, type_problems, VERBS)
from spark.sourcing import sourcing_codes
from spark.sourcing.part_rules import (
    bus_line_of, BUSES, CAPABILITIES, footprint_pad_count, host_part_problems, i2c_pullup_problems,
    pin_order_problems, simulation_problems)

SUPPORTED_SCHEMA = 1


#: A kind that says by itself what a part does (§5.6). A `sensor` or a `connector` does not: theirs is written
#: once, through `--function-set`, with a dry run.
KIND_FUNCTION = {"rtc": ("keep-time", "rtc"), "regulator": ("power", "regulator"), "button": ("input", "button"),
                 "indicator": ("indicate", "light"), "mosfet-driver": ("drive", "load-switch"),
                 "motor-driver": ("drive", "motor-dc"), "audio-amplifier": ("sound", "amplifier"),
                 "audio": ("sound", "audio-player"), "rangefinder": ("sense", "distance"), "servo": ("move", "servo"),
                 "board": ("compute", "microcontroller")}


def function_of(record, board=False):
    """
    What a record does (§5.6): its own `function`, else what its kind says, else nothing. A board also does what its own
    parts do (`board_records.onboard_functions`), each one added once and never to the record's own list. One the record
    also says (the same `does` and `what`) is the board's own dict, which carries the `role` (P397).
    """
    if record.get("function") and not function_problems(record):
        said = record["function"]
    else:
        kind = "board" if board else record.get("kind")
        kind_function = KIND_FUNCTION.get(kind) if isinstance(kind, str) else None
        said = [{"does": kind_function[0], "what": kind_function[1]}] if kind_function else []
    if not board:
        return said
    onboard = board_records.onboard_functions(record)
    own = {(function["does"], function["what"]): function for function in onboard}
    named = {(function["does"], function["what"]) for function in said}
    return [own.get((function["does"], function["what"]), function) for function in said] + [
        function for function in onboard if (function["does"], function["what"]) not in named]


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


def broken_problems(record, path):
    """What is wrong with a part record beyond what it owes (§5.4): `validate`'s problems, with the checks of each owed key skipped."""
    return _shape_problems(functools.partial(validate, owed=owes(record)), record, path, "part record")


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


class PartError(CodedMessageError):
    """A part definition that cannot be used, with the reason and its `sourcing_codes` code."""


def definition_path(part_id: str, project: Path = None) -> Path:
    found = store.records("parts", record_kind.LIBRARY, project).get(part_id)
    if found:
        return found[1]
    raise PartError("no part called %r.\n  available: %s", part_id, ", ".join(available(project)) or "(none)",
                    code=sourcing_codes.NO_SUCH_PART)


def load(part_id: str, project: Path = None) -> dict:
    path = definition_path(part_id, project)
    part = json.loads(path.read_text())
    problems = validate(part, path)
    if problems:
        raise PartError.of_lines(["%s does not meet the part contract:" % path]
                                 + ["  - " + problem for problem in problems], code=sourcing_codes.PART_CONTRACT_BROKEN)
    return part


# The part contract (P724): one named rule per function, each `(part, validation) -> list`, run by `PART.validate` in the
# order of `RULES`. A rule whose key the record owes (`owes`) returns [] itself.

def id_problems(part, validation):
    """The id names the file, and is a plain key."""
    # an owed id is a missing one, so the plain-key check below never reads it
    if "id" not in validation.owed and part.get("id") != validation.path.stem:
        return ["id is %r but the file is named %r; they must match" % (part.get("id"), validation.path.stem)]
    if isinstance(part.get("id"), str) and not store.PLAIN.fullmatch(part["id"]):
        # P87's attribute half: `board_emitter.component_name` capitalises the id's words and strips nothing, so the id is
        # what keeps `<chip name="…">` a name — a plain key, as every key of the store is
        return [NOT_A_PLAIN_ID % part["id"]]
    return []


def field_type_problems(part, validation):
    """Each field of the wrong type, the owed ones left out. In `PART.stop_after`: the rules after it read these fields."""
    return type_problems({key: value for key, value in part.items() if key not in validation.owed})


def retired_key_problems(part, validation):
    """Each retired key the record still holds (W16)."""
    problems = ["%r is retired: %s — delete the key (W16)" % (key, now) for key, now in RETIRED.items() if key in part]
    if any(isinstance(listing, dict) and listing.get("seller") == "owned" for listing in part.get("sourcing") or []):
        problems.append('a `sourcing` entry {"seller": "owned"} is retired: %s — delete it (W16)' % RETIRED["owned"])
    return problems


def need_problems(part, validation):
    """Each `needs` entry with no signal, a direction or a bus this does not know, or a capability no pin has."""
    problems = []
    for index, need in enumerate(part.get("needs") or []):
        where = "needs[%d]" % index
        if not need.get("signal"):
            problems.append("%s has no signal" % where)
        if need.get("direction") not in ("in", "out", "bidirectional", None):
            problems.append("%s direction is %r; expected in, out or bidirectional" % (where, need.get("direction")))
        bus = need.get("bus")
        if bus and bus not in BUSES:
            problems.append("%s is on bus %r, which is not a bus this knows: %s" % (where, bus, ", ".join(BUSES)))
        elif bus and need.get("signal") and bus_line_of(bus, need["signal"]) is None:
            problems.append("%s is on the %s bus but %r is not one of its lines: %s"
                            % (where, bus.upper(), need["signal"],
                               ", ".join("%s (%s)" % (line, "/".join(names))
                                         for line, names in BUSES[bus].items())))
        unknown = sorted(set(need.get("needs") or []) - set(CAPABILITIES))
        if unknown:
            # Caught HERE, not four scripts later. `assign_pins` refuses the entire design over an unknown capability —
            # rightly, since a silently dropped requirement produces a board wrong in exactly the way the requirement
            # existed to prevent — but it did so long after this file had pronounced the record good.
            problems.append("%s asks a pin for %s, which is not something a pin can be asked "
                            "for. Known: %s" % (where, ", ".join(unknown), ", ".join(CAPABILITIES)))
    return problems


def missing_pin_problems(part, validation):
    """Each entry of a list of pins (`PIN_LISTS`) that names no pin."""
    # Every list of pins, in one place. Only `needs` entries were checked for a pin, and then
    # `power` and `unused_pins` were read with `entry["pin"]` in four places — so an entry missing
    # one crashed the validator instead of being reported by it. Same defect twice in one file,
    # which is what happens when a rule is written at the use site rather than the contract.
    return ["%s[%d] has no pin, so nothing can say where it connects" % (group, index)
            for group in PIN_LISTS for index, entry in enumerate(part.get(group) or []) if not entry.get("pin")]


def selector_pin_problems(part, validation):
    """Each pin that cannot be a selector, and each silkscreen (`printed`) that is no string or would end the board's comment."""
    # The wiring name reaches a tscircuit selector verbatim, so it is restricted to what a
    # selector can parse. The silkscreen goes in `printed`, where anything is allowed.
    problems = []
    for group in PIN_LISTS:
        for index, entry in enumerate(part.get(group) or []):
            pin = entry.get("pin")
            if pin and not re.fullmatch(SELECTOR_SAFE, str(pin)):  # whole: `$` alone lets a trailing newline through
                problems.append(
                    "%s[%d] pin %r cannot be a selector — letters, digits and _ only. If that is "
                    "what the silkscreen says, keep it in `printed` and give `pin` a wiring name"
                    % (group, index, pin))
            printed = entry.get("printed")
            if printed is not None and not isinstance(printed, str):
                problems.append("%s[%d] printed is %r; it is the silkscreen text, a string" % (group, index, printed))
            elif printed is not None and any(mark in printed for mark in ENDS_THE_COMMENT):
                problems.append("%s[%d] printed %r holds %s — the generated board keeps the silkscreen in a comment, "
                                "which that would end; write it without" % (group, index, printed, " and ".join(
                                    mark for mark in ENDS_THE_COMMENT if mark in printed)))
    return problems


def rail_and_signal_problems(part, validation):
    """Each rail and each signal that is not a name."""
    # A rail and a signal are names, as a pin is (P87's attribute half, after F11): a rail becomes the net the board is written
    # with — `to="net.<RAIL>"`, upper-cased — so a crafted one was code in board.tsx; a signal is what the pin map and the
    # firmware call a pin's job. Whole-string: `$` alone would let a trailing newline through.
    problems = []
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
    return problems


def body_problems(part, validation):
    """A `body_mm` with no numeric width and height, no provenance, or unverified with no why_it_matters."""
    # Dimensions are a real schema, not an open fact: a generator reads them to decide where things go, and a bare size let a guess
    # pass for a measurement (an outline that was missing silently became 16 x 12 mm).
    body = part.get("body_mm")
    if body is None or "body_mm" in validation.owed:
        return []
    if not isinstance(body, dict):
        return ["body_mm is not an object; it needs width, height and provenance"]
    problems = ["body_mm has no numeric %s" % key for key in ("width", "height") if not isinstance(body.get(key), (int, float))]
    problems += ["body_mm has no %r — a dimension with no provenance is a guess, and a generator cannot tell the "
                 "difference" % key for key in ("verified", "source") if key not in body]
    problems.extend(provenance.list_type_problems("body_mm", body))
    if body.get("verified") is False and not body.get("why_it_matters"):
        problems.append("body_mm is unverified with no why_it_matters; say what depends "
                        "on it — here, whether the modules physically fit the board")
    return problems


def placeholder_problems(part, validation):
    """A footprint placeholder that says nothing of the real footprint."""
    # A footprint standing in for the real one. `facts` and `body_mm` carry `verified`; the footprint carried no
    # provenance at all, so an XT30 inlet drawn as a JST PH — wrong pitch, wrong hole size, stated as a placeholder in a
    # comment nothing reads — looked identical to a footprint generated from a vendor drawing. `check_footprints` duly
    # measured the JST's annular rings and reported a defect about a part that is not on the board. The most expensive
    # field to get wrong was the one field with no way to say "not yet".
    if part.get("footprint_placeholder") and not part.get("footprint_note"):
        return ["footprint_placeholder is set with no footprint_note — say what the "
                "real footprint is and why this one stands in, or nobody can finish it"]
    return []


def footprint_name_problems(part, validation):
    """A footprint that is there and is not the name of one."""
    # A footprint is the NAME of one: the board is written with it as the text of an attribute, so a number or
    # `true` would reach tscircuit as the footprint "5" or "True" — and a string with a quote in it would be code
    # (C-1). An absent one (`_absent`: null, no key, empty) is owed, not wrong, so only a value that is there is
    # checked; whether a name names a real footprint is a build's to say.
    footprint = part.get("footprint")
    if _absent("footprint", footprint) or (isinstance(footprint, str) and FOOTPRINT_NAME.fullmatch(footprint)):
        return []
    return ["footprint is %r, but a footprint is the name of one — a footprinter's, in lower-case letters, "
            "digits, _ and . (pinrow5, jst_ph_3, dip12_w15.24mm), or a JLCPCB part, jlcpcb:C<number>: the "
            "board is written with it as code" % (footprint,)]


def _pin_order(part, validation):
    """The record's `pin_order` when a rule reads it, or None: absent, or owed."""
    return None if "pin_order" in validation.owed else part.get("pin_order")


def pin_order_pad_problems(part, validation):
    """A `pin_order` that is no list of pads, names a pad the part never mentions, repeats a signal or leaves a pin out."""
    # Which pad is pin 1. The generator numbered `pinLabels` from the order the pins happened to
    # appear in this file — so an L9110S whose header reads BIA BIB GND VCC AIA AIB was emitted
    # as pin1: "AIA", and every trace to the module landed on the wrong pad. Nothing here could
    # have been right, because the physical order was not written down anywhere.
    order = _pin_order(part, validation)
    if order is None:
        return []
    if not isinstance(order, list) or not order:
        return ["pin_order must be a list of pad names, pad 1 first"]
    # `.get`, not `[...]`. An entry with no `pin` is exactly what the checks above exist to report, and reading
    # it here crashed the validator on the malformation it was written to catch: `needs[0] has no pin` was
    # appended, then this line raised KeyError three lines later. Every real part has a pin_order, so any part
    # broken in that way took the whole run down instead of being reported.
    named = {entry.get("pin") for group in PIN_LISTS for entry in part.get(group) or []} - {None}
    problems = ["pin_order pad %d is %r, which this part never mentions — a pad name that matches nothing silently "
                "wires nothing" % (position, pad) for position, pad in enumerate(order, start=1)
                if pad is not None and pad not in named]
    # A pad may legitimately appear twice, but only if it is a SUPPLY. Real modules bring
    # VCC and GND out on both rows so either side can be fed; a repeated SIGNAL is a typo,
    # and two pads shorted together is what it would build.
    supplies = {supply.get("pin") for supply in part.get("power") or []}
    placed = [pad for pad in order if pad is not None]
    repeated = {pad for pad in placed if placed.count(pad) > 1}
    problems += ["pin_order names %r on more than one pad, and it is not a supply — a signal on two "
                 "pads is two pads shorted together" % pad for pad in sorted(repeated - supplies)]
    missing = sorted(named - set(placed))
    if missing:
        problems.append("pin_order does not say where %s sit(s), so the generator would have to "
                        "guess a pad for them" % ", ".join(missing))
    return problems


def pad_count_problems(part, validation):
    """A footprint whose pad count is not the number of pads `pin_order` names."""
    # The two fields describe the same physical thing and nothing compared them. The VL6180X breakout shipped
    # saying `pinrow5` while naming seven pads — five of its seven carry a signal and two are unwired, so
    # somebody counted the pins instead of the pads. The generator then labelled a pad that did not exist; that
    # port got no position, and tscircuit's autorouter died reading its x — which does not fail loudly, it just
    # leaves the whole board with zero traces.
    order = _pin_order(part, validation)
    if not isinstance(order, list) or not order:  # absent, owed or no list: `pin_order_pad_problems` says which
        return []
    pads = footprint_pad_count(part.get("footprint"))
    if pads is None or pads == len(order):
        return []
    return ["footprint %r has %d pads but pin_order names %d. They describe the same physical part, so one of them is "
            "wrong — and the generator will label a pad that does not exist, which leaves that port with no position "
            "at all" % (part["footprint"], pads, len(order))]


def power_direction_problems(part, validation):
    """A power pin that is neither in nor out, and two outputs that would land on one net."""
    # A power pin's DIRECTION is what says whether sharing a net is normal or fatal. Several GND
    # pins on one net is how ground works; two amplifier outputs on one net is a short. Both
    # looked identical in this schema — a `rail` and nothing else — and the generator duly wired
    # both halves of a bridged class-D output together, under the part's own note saying never to.
    problems, outputs_by_rail = [], {}
    for index, supply in enumerate(part.get("power") or []):
        direction = supply.get("direction")
        if direction not in ("in", "out"):
            problems.append(
                "%s direction is %r; a power pin is 'in' (it consumes a rail, and sharing one is "
                "normal) or 'out' (it drives a load, and sharing a net is a short)" % ("power[%d]" % index, direction))
        elif direction == "out" and isinstance(supply.get("rail"), (str, type(None))):  # any other rail is said above
            # Keyed on the NET it would land on, which for an output is the load plus which side
            # of it this pin drives. Two outputs on one load are the normal case — that is what a
            # differential pair is — and they are only a short if nothing distinguishes them.
            outputs_by_rail.setdefault((supply.get("rail"), supply.get("polarity")), []).append(supply.get("pin"))
    return problems + [
        "power pins %s are outputs driving %r with the same polarity (%r), so they would "
        "land on one net and short into each other. Give each its own `polarity`, or they "
        "are not separate outputs" % (", ".join(map(str, pins)), rail, polarity)
        for (rail, polarity), pins in outputs_by_rail.items() if len(pins) > 1]


def part_fact_problems(part, validation):
    """`provenance.list_fact_problems` of the record's `facts`."""
    return provenance.list_fact_problems(part.get("facts"))


def part_host_part_problems(part, validation):
    """`part_rules.host_part_problems` of the record."""
    return host_part_problems(part)


def part_i2c_pullup_problems(part, validation):
    """`part_rules.i2c_pullup_problems` of the record."""
    return i2c_pullup_problems(part)


def part_document_problems(part, validation):
    """`record_kind.document_problems` of the record."""
    return document_problems(part)


def pin_order_proof_problems(part, validation):
    """`part_rules.pin_order_problems` of the record, unless it owes its `pin_order_proof`."""
    return [] if "pin_order_proof" in validation.owed else pin_order_problems(part)


def part_simulation_problems(part, validation):
    """`part_rules.simulation_problems` of the record, unless it owes its `simulation`."""
    return [] if "simulation" in validation.owed else simulation_problems(part, validation.path)


def part_function_problems(part, validation):
    """`function_problems` of the record."""
    return function_problems(part)


RULES = (id_problems, field_type_problems, retired_key_problems, need_problems, missing_pin_problems,
         selector_pin_problems, rail_and_signal_problems, body_problems, placeholder_problems, footprint_name_problems,
         pin_order_pad_problems, pad_count_problems, power_direction_problems, part_fact_problems,
         part_host_part_problems, part_i2c_pullup_problems, part_document_problems, pin_order_proof_problems,
         part_simulation_problems, part_function_problems)
#: The part kind (P724). `field_type_problems` stops the rules after it: they read the fields it checks, so they run
#: only on a record whose types are right.
PART = RecordKind("part", SUPPORTED_SCHEMA, REQUIRED_KEYS, RULES, stop_after=(field_type_problems,))
#: Every way a definition breaks the contract. Empty means it holds. The checks of an `owed` key (`owes`) do not run.
validate = PART.validate


def any_record(part_id, project=None):
    """The record wherever it lives: validated from a parts/, raw from the catalog (a draft is allowed)."""
    home = record_home(part_id, project)
    if home == store.place("catalog"):
        return _parse(home / (part_id + DEFINITION_SUFFIX)) or {}
    return load(part_id, project)
