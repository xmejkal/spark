"""
What must be true before power is applied to one build (P191, P826): each supply from off the board, whose voltage the
sheet does not set, and what each part's record says: its CONFLICTs, the pins the firmware must pull up (P204), the pins
that must not float and its host requirements, in the record's own words. `BeforePower` holds them as facts, which a
page reads; `BeforePowerList` gives the sheet's "Before you power it" lines from them and decides nothing again.
"""

import collections

from spark.design import board_components
from spark.sourcing import part_rules

#: What one item is: a supply from off the board, a CONFLICT, a pin the firmware must pull up, a pin that must not float,
#: or one of a record's host requirements.
OFF_BOARD_SUPPLY, CONFLICT, FIRMWARE_PULL, UNUSED_PIN, HOST_REQUIREMENT = (
    "off-board-supply", "conflict", "firmware-pull", "unused-pin", "host-requirement")
#: One item: its kind; its subject, the name its line opens with (a supply's net, the component of a CONFLICT, a firmware
#: pull or an unused pin, the record's name for a host requirement); its pin (None for a supply and a host requirement);
#: its record id (None for a supply, which the circuit gives); the record's own words (the CONFLICT's line, the pin's note
#: or "" with none, the requirement; None for a supply and a firmware pull); and a supply's users, the components on it,
#: sorted (() for every other kind).
BeforePowerItem = collections.namedtuple("BeforePowerItem", "kind subject pin record said users")


class BeforePower:
    """Value: the items, in the sheet's order, and the design's record ids, sorted: each record `parts.py --show` shows
    whole."""

    def __init__(self, items, records):
        self.items = list(items)
        self.records = list(records)

    @classmethod
    def of(cls, design_parts, supplies):
        """From the design's parts and `supplies` ({net: the components on it}): the supplies first, then for each part
        its CONFLICTs, its firmware pulls and its unused pins, and its record's host requirements once per record."""
        items = [BeforePowerItem(OFF_BOARD_SUPPLY, net, None, None, None, tuple(sorted(users)))
                 for net, users in supplies.items()]
        seen = set()
        for part in design_parts:
            name = board_components.component_name(part)
            items += [BeforePowerItem(CONFLICT, name, conflict["pin"], part["id"], conflict["line"], ())
                      for conflict in part_rules.conflicts_of(part)]
            items += [BeforePowerItem(FIRMWARE_PULL, name, pin, part["id"], None, ())
                      for pin in part.get("_firmware_pulls", [])]
            items += [BeforePowerItem(UNUSED_PIN, name, pin["pin"], part["id"], pin.get("note", ""), ())
                      for pin in part.get("unused_pins") or []]
            if part["id"] not in seen:
                seen.add(part["id"])
                items += [BeforePowerItem(HOST_REQUIREMENT, part.get("name"), None, part["id"], requirement, ())
                          for requirement in part.get("host_requirements") or []]
        return cls(items, sorted({part["id"] for part in design_parts}))


class BeforePowerList:
    """Renderer: the items as Markdown lines, one template per kind, then the line that names each record whole."""

    #: The line of each kind, filled from an item's fields; a supply's users are joined by commas.
    TEMPLATES = {
        OFF_BOARD_SUPPLY: "- {subject} comes from off the board, and this sheet does not say its voltage: check it "
                          "against the supply range of {users} (`parts.py --show`) before you connect it",
        CONFLICT: "- **CONFLICT** on {subject}: {said}",
        FIRMWARE_PULL: "- {subject} {pin} has no resistor: the firmware must pull it up with Pin.PULL_UP, as `pins.py` "
                       "says (P204)",
        UNUSED_PIN: "- {subject} {pin}: {said}",
        HOST_REQUIREMENT: "- {subject}: {said}",
    }

    def render(self, before_power):
        lines = [self.TEMPLATES[item.kind].format(**item._replace(users=", ".join(item.users))._asdict())
                 for item in before_power.items]
        shows = ", ".join("`parts.py --show %s`" % record for record in before_power.records)
        return lines + ["", "Each record whole, with what it asks of the board: %s." % shows]
