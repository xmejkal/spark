"""
The rails and the power nets of a design (P708): what each rail's net is called, who drives it, what loads it, and which
outputs meet or stand alone. It decides nothing about the file: `board_sections` writes it.
"""

from spark.design.board_components import component_name


# --- MVP ---
#: Rails with an ESTABLISHED net name. Deliberately not the whole vocabulary — see
#: `net_name_for_rail`. `MOTOR6V` carries a voltage belonging to one project's battery and is kept
#: only because designs already reference that net by name; a new design should say `motor` and
#: state the voltage in its rules file.
KNOWN_RAIL_NETS = {"logic": "V33", "ground": "GND", "motor": "MOTOR6V", "speaker": "SPEAKER"}


def net_name_for_rail(rail):
    """
    The net a rail's name means. ANY rail name is allowed — letters, digits and _, which `part_records.validate`,
    `board_records.validate` and `loader` hold a rail to: the board is written with it as code (P87's attribute half).

    This was a closed dictionary of four, and a rail outside it returned None — which the power
    loops turned into `continue`, so the connection was silently not emitted. An RC car with a 5 V
    servo rail and a 7.4 V traction pack came out with a servo that had a ground and no supply,
    and a regulator joined to the board by its two ground pins and nothing else. Exit 0, one
    unrelated note. That is the third instance of one defect — `244feb1` (signals with no part
    record) and `21156b4` (the processor on no ground) were the first two: the generator emitting
    less than it was asked for without saying so.

    The four above keep their names so existing designs are unchanged. Anything else becomes its
    own name upper-cased, and `rails_not_established` reports it — because an open vocabulary
    means a typo creates a net, and the answer is to show the reader what was created rather than
    to refuse every rail nobody thought of in advance.
    """
    if not rail:
        return None
    net = KNOWN_RAIL_NETS.get(rail, str(rail).upper())
    # tscircuit refuses a net name that starts with a digit ("12V"): the irrigation controller's
    # first build stopped inside the builder on its `12v` rail (irrigation diary I7).
    return "V" + net if net[0].isdigit() else net


def rails_not_established(part_list):
    """
    Rails this design invented, so a typo is visible rather than silently a new net.

    `GROUDN` is a perfectly good net name and a terrible ground. Reported, not refused: the
    alternative is the closed vocabulary that silently dropped three connections.
    """
    invented = {}
    for part, supply, _ in power_connections(part_list):
        rail = supply["rail"]
        if rail not in KNOWN_RAIL_NETS:
            invented.setdefault(net_name_for_rail(rail), []).append(
                "%s.%s" % (part["name"], supply["pin"]))
    return {net: sorted(pins) for net, pins in sorted(invented.items())}


def power_pins_with_no_rail(part_list):
    """Power pins whose record names no rail at all — a connection nobody can place."""
    return ["%s.%s" % (part["name"], supply["pin"])
            for part in part_list for supply in part.get("power") or []
            if not supply.get("rail")]
#: What a `polarity` becomes in a net name, so a differential pair reads as one.
POLARITY_SUFFIX = {"+": "_P", "-": "_N"}


#: Rails the microcontroller module itself supplies, so a design made only of consumers still
#: has a source for them.
RAILS_THE_MODULE_PROVIDES = ("V33", "GND")
#: Nets that are a ground. Named rather than guessed, because "the one called GND" stops being
#: true the moment a design has an analogue ground or an isolated return. `check_spine` reads
#: this too — one list, so the grounding rule and the supply rule cannot disagree.
GROUND_NETS = ("GND", "AGND", "DGND", "GROUND")


def power_connections(part_list):
    """
    Every module power pin that names a rail, as (part, supply, net): ONE walk of the lists.

    It was written four times — the source rule, the sink rule, the traces and the invented-rail
    report — each with its own `net_for` and `continue`, and G2 was fixed at some of them. An
    entry with no rail is not yielded; `power_pins_with_no_rail` is the one place that says so,
    and the generated file carries what it says.
    """
    for part in part_list:
        for supply in part.get("power") or []:
            net = net_for(supply)
            if net:
                yield part, supply, net


def net_for(supply):
    """
    The net a power pin belongs on.

    An INPUT joins the shared rail — several parts on V33, several pins on GND, which is the
    point of a rail. An OUTPUT gets its own net, because two outputs on one net is a short. That
    distinction did not exist here: both halves of a bridged class-D amplifier declared
    `"rail": "speaker"`, both were mapped to `net.SPEAKER`, and the generated board wired them
    together — printing the part file's own warning, "never ground either side", on the trace
    that did it.

    An input that names a side of a pair (`polarity`) takes that side's net, which the pair's
    output drives: the speaker terminal's SPK+ is on net.SPEAKER_P, its SPK- on net.SPEAKER_N
    (C-3). Without it the amplifier's two outputs each ended on a net with one member.
    """
    net = net_name_for_rail(supply.get("rail"))
    if net and (supply.get("direction") == "out" or supply.get("polarity") in POLARITY_SUFFIX):
        return net + POLARITY_SUFFIX.get(supply.get("polarity"), "")
    return net


def loads_across_a_pair(part_list):
    """
    The components that sit across a driven pair and have no ground of their own, by the name the
    emitted file gives them (C-3): a part that asks for no signal and whose every power pin is an
    input on one side of a pair — the terminal a speaker's two wires go to. Its return is the
    pair's other side, and a ground would short the amplifier, so `check_spine` asks of it what it
    asks of a two-terminal passive: that neither end dangles.
    """
    return sorted(component_name(part) for part in part_list
                  if not part.get("needs") and part.get("power")
                  and all(supply.get("direction", "in") == "in" and supply.get("polarity") in POLARITY_SUFFIX
                          for supply in part["power"]))


def rails_without_a_source(part_list):
    """
    Rails that something consumes and nothing provides.

    A list of modules is a list of CONSUMERS. Nobody lists the battery connector among their
    parts, so a generated board wires a motor driver's VCC to a motor rail that has no other
    member — and a net with one member cannot be routed, so the board does not build.

    That is worth saying plainly rather than emitting a file that fails: the design genuinely
    needs a source for that rail and the module list did not contain one.
    """
    consumed, provided = set(), set()
    for _, power, net in power_connections(part_list):
        # An OUTPUT is not a rail anything has to source — the part IS the source. This branch
        # collected nothing until 2026-09-25, so the function returned every consumed rail
        # whether or not something fed it, and adding the connector that supplies a rail did
        # not stop it being reported as unsupplied. The name and the docstring were right about
        # the intent; the code only did the first half.
        if power.get("direction") == "out":
            provided.add(net)
        elif net not in RAILS_THE_MODULE_PROVIDES:
            consumed.add(net)
    return sorted(consumed - provided)


def pair_sides_without_a_driver(part_list):
    """
    The rails `rails_without_a_source` names that are one side of a driven pair (F15): every pin on one is an input naming
    a `polarity` — a speaker terminal's SPK+ on SPEAKER_P. What feeds such a net is an amplifier's output, never a supply:
    told to pick a power inlet, a person would plug a supply into what the terminal's own record calls destructive. Decided
    by the pins, not by a `_P`/`_N` suffix, so a pair the design moves onto rails of its own is still one.
    """
    on = {}
    for _, supply, net in power_connections(part_list):
        if supply.get("direction") != "out":
            on.setdefault(net, []).append(supply)
    return [net for net in rails_without_a_source(part_list)
            if all(supply.get("polarity") in POLARITY_SUFFIX for supply in on[net])]


def outputs_in_contention(part_list):
    """
    Nets driven by more than one supply, or by a supply onto a rail the module itself provides.

    `part_records.validate` keeps two outputs of ONE part off one net; nothing did across parts, or
    against the board: a regulator's VOUT declared on `logic` was traced to net.V33 beside the
    microcontroller's own 3V3, exit 0, no note (sprint-4 audit B9). Two supplies on one rail
    short into each other unless one is designed to back-feed — which a part record cannot say,
    so the design has to.
    """
    drivers = {}
    for part, supply, net in power_connections(part_list):
        # A ground is not a supply: a connector declares its GND as `out` — the point where the
        # pack's return meets board ground — and many returns on one ground is what a ground is.
        if supply.get("direction") == "out" and net not in GROUND_NETS:
            drivers.setdefault(net, []).append("%s.%s" % (part["name"], supply["pin"]))
    contended = []
    for net in sorted(drivers):
        who = drivers[net]
        if net in RAILS_THE_MODULE_PROVIDES:
            contended.append((net, who + ["the microcontroller module's own %s" % net]))
        elif len(who) > 1:
            contended.append((net, who))
    return contended


#: What a current fact's name says its unit is. A pointer to a fact named anything else is
#: refused rather than read as amps: `stall_current: 700` is a guess about a factor of a thousand.
CURRENT_UNITS = (("_ua", 1e-6), ("_ma", 1e-3), ("_a", 1.0))


def current_of(part, pointer):
    """
    A figure a power pin names: `stall_current_ma`, or one key of a fact whose value is a table,
    `active_supply_current_ua.active_max`. `amps` is None when the record does not state it, and
    `why` then says what is missing — the part's own words for the gap, not a zero.
    """
    if not pointer:
        return {"amps": None, "verified": False, "why": "names no fact for its current"}
    name, _, key = pointer.partition(".")
    fact = (part.get("facts") or {}).get(name)
    scale = next((scale for suffix, scale in CURRENT_UNITS if name.endswith(suffix)), None)
    if not isinstance(fact, dict) or scale is None:
        return {"amps": None, "verified": False,
                "why": "names %r, which is not a current this record states" % pointer}
    value = fact.get("value")
    if key:
        value = value.get(key) if isinstance(value, dict) else None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return {"amps": None, "verified": False, "why": "%s is not stated" % pointer}
    return {"amps": value * scale, "verified": bool(fact.get("verified")), "why": pointer}


def volts_of(part, pointer):
    """
    The voltage a supply pin holds its rail at, from the fact its `volts` names (P197): `io_volts`. `value` is None
    when the record does not state it, and `why` then says what is missing, as `current_of` does for a current.
    """
    if not pointer:
        return {"value": None, "verified": False, "why": "names no fact for its voltage"}
    fact = (part.get("facts") or {}).get(pointer)
    value = fact.get("value") if isinstance(fact, dict) and pointer.endswith("_volts") else None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return {"value": None, "verified": False, "why": "%s is not a voltage this record states" % pointer}
    return {"value": value, "verified": bool(fact.get("verified")), "why": pointer}


def module_as_part(board):
    """The board's power pads in the shape of a part's power entries, its `power` as its facts."""
    return {"id": "module", "_instance": "Mcu", "facts": board.get("power") or {},
            "power": [dict(entry, pin=pad) for pad, entry in (board.get("power_pads") or {}).items()]}


def rail_settler(rails, outputs):
    """`settle(net)`: the sum of one rail of `rail_loads`, each rail settled once, a converter's input through the
    output it feeds."""
    settled = {}

    def settle(net, through=()):
        if net in settled:
            return settled[net]
        amps, missing, unverified = 0.0, [], []
        for load in rails[net]["loads"]:
            if "feeds" in load:
                fed = outputs.get((id(load["part"]), load["feeds"]))
                inner = settle(fed, through + (net,)) if fed and fed not in through + (net,) else None
                load = {"who": load["who"],
                        "why": "carries what %s carries%s" % (
                            fed, "" if inner and inner["complete"] else ", which is not fully stated"),
                        "amps": inner["amps"] if inner and inner["complete"] else None,
                        "verified": bool(inner) and not inner["unverified"]}
            if load["amps"] is None:
                missing.append("%s: %s" % (load["who"], load["why"]))
                continue
            amps += load["amps"]
            if not load["verified"]:
                unverified.append("%s: %s" % (load["who"], load["why"]))
        supplies = rails[net]["supplies"]
        settled[net] = {"amps": amps, "complete": not missing, "missing": missing,
                        "unverified": unverified,
                        "supply": supplies[0] if len(supplies) == 1 else None}
        return settled[net]

    return settle


def rail_loads(part_list, board=None):
    """
    What each rail carries, summed from the facts its members' power pins name (P52).

    `{net: {amps, complete, missing, unverified, supply}}`. A pin names its figure — `draws` on an
    input, `can_supply` on an output, `own_draw` where a module takes from the rail it makes —
    because a servo has a stall AND an idle current and only the record can say which one its
    pin draws. `amps` is what IS stated, so an open rail still says what it carries at least;
    `missing` names every load the records leave open, where a total would be a guess.

    A converter's input `feeds` an output and draws at most what that output delivers: an upper
    bound for a step-down converter, and the only figure its record can honestly give. An output
    may also name the fact that states the voltage it holds its rail at, as `volts` (P197).
    """
    members = list(part_list) + ([module_as_part(board)] if board else [])
    rails, outputs = {}, {}
    for part, supply, net in power_connections(members):
        if net in GROUND_NETS:
            continue
        rail = rails.setdefault(net, {"loads": [], "supplies": []})
        who = "%s.%s" % (component_name(part), supply["pin"])
        if supply.get("direction") == "out":
            outputs[(id(part), supply["pin"])] = net
            rail["supplies"].append(dict(current_of(part, supply.get("can_supply")), who=who,
                                         volts=volts_of(part, supply.get("volts"))))
            if supply.get("own_draw"):
                rail["loads"].append(dict(current_of(part, supply["own_draw"]), who=who))
        elif supply.get("feeds"):
            rail["loads"].append({"who": who, "part": part, "feeds": supply["feeds"]})
        else:
            rail["loads"].append(dict(current_of(part, supply.get("draws")), who=who))

    settle = rail_settler(rails, outputs)
    return {net: settle(net) for net in rails}


def outputs_with_nothing_on_them(part_list):
    """
    Nets a part drives that nothing on this board receives.

    The mirror of `rails_without_a_source`, and it has to be said too: a speaker is not a module,
    so nobody lists one, and the amplifier's two outputs each end up a net with one member. That
    is a net that cannot route, in a file whose header says every connection is derived and
    checked — and the errors a build then reports should be the ones this file predicted rather
    than a surprise.
    """
    driven, received = [], set(RAILS_THE_MODULE_PROVIDES)
    for part, power, net in power_connections(part_list):
        if power.get("direction") == "out":
            driven.append((net, part["name"], power["pin"]))
        else:
            received.add(net)
    # Same omission this function's twin had: it listed every driven net without ever asking
    # whether something on the board receives it. Adding the power inlet that feeds the motor
    # driver then produced a warning that the motor rail goes nowhere, naming the part it goes
    # to. A warning that fires on a correct design is worse than none — it is the reason people
    # stop reading them.
    return sorted(entry for entry in driven if entry[0] not in received)


def supply_net_of(part):
    """The net the part's own supply pin sits on, for a pull-up: its first non-ground input rail."""
    for supply in part.get("power") or []:
        net = net_name_for_rail(supply.get("rail"))
        if supply.get("direction", "in") == "in" and net and net not in GROUND_NETS:
            return net
    return "V33"


def rails_driven_by(part_list):
    """The non-ground nets something on this board SOURCES. A ground is not a rail anybody drives."""
    return {net for _, supply, net in power_connections(part_list)
            if supply.get("direction") == "out" and net not in GROUND_NETS}


def mcu_power_nets(board, part_list):
    """
    The module's own power pads, as (pad, net, wired): which ones this board joins, and to what.

    A pad the module DRIVES — its grounds, its 3.3 V regulator output — is wired always; it is
    what the rest of the board hangs off. A pad the module RECEIVES on is wired only when
    something on this board drives that rail, and that condition is the whole of backlog P29.

    Both halves have cost a board. Wiring a receiving pad unconditionally puts a net with one
    member on every design that has no such supply — and on the FireBeetle it would carry the USB
    5 V out to whatever is on the rail, which is how 5 V reaches a 3.3 V part. Never wiring it is
    what shipped until 2026-09-30: the irrigation controller's buck record says "Feeds the
    FireBeetle's 5 V/VCC input and the sensors", and the generated board had no such trace. Its
    processor was fed by nothing, on a board that built, routed and reported no error.

    ONE home, because `check_spine` asks the same question of the built circuit and the two must
    not be able to disagree — this file's own history is three defects of exactly that shape.
    """
    driven = rails_driven_by(part_list)
    for pad, supply in sorted((board.get("power_pads") or {}).items()):
        net = net_name_for_rail(supply.get("rail"))
        receives = supply.get("direction", "in") == "in" and net not in GROUND_NETS
        yield pad, net, bool(net) and (not receives or net in driven)


def supply_inputs(board, part_list):
    """
    Every power connection this design STATES as an input, as (component, pin, net).

    The claim a built circuit has to honour. Outputs are left out on purpose: a driven net with
    nothing on it is a different complaint, and `outputs_with_nothing_on_them` already makes it.
    """
    claims = [(component_name(part), supply["pin"], net)
              for part, supply, net in power_connections(part_list)
              if supply.get("direction", "in") == "in" and net not in GROUND_NETS]
    claims += [("Mcu", pad, net) for pad, net, wired in mcu_power_nets(board, part_list)
               if wired and net not in GROUND_NETS]
    return sorted(claims)
# --- end MVP ---
