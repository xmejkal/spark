"""
The footprint pad each pin label of a board sits on (P512, #708).

The one reader of a board record's `physical.pad_aliases`, so a trace, a pin line, a breadboard sheet and the record
validator in board_records.py all read the pad the silkscreen prints from here. `JoinedPads` is the one reader of its
`physical.header.joined_pads` (P962), the pads the board joins inside itself.
"""

from dataclasses import dataclass


# --- MVP --- (P512, #708) the one reader of physical.pad_aliases: every trace, pin line and sheet asks it
@dataclass(frozen=True)
class BoardPads:
    """
    Value: the footprint pad each pin label sits on. Most labels are their own pad; `physical.pad_aliases` names the
    others (the FireBeetle 2 prints MOSI as MO, the XIAO C6 prints SDA as D4). A trace to the label instead of its pad
    reaches nothing, and the build says only "not connected".
    """

    aliases: dict

    @classmethod
    def from_record(cls, record):
        """The pads of a board record; a record with no aliases maps every label to itself."""
        physical = record.get("physical") if isinstance(record, dict) else None
        return cls(dict((physical.get("pad_aliases") if isinstance(physical, dict) else None) or {}))

    def pad_of(self, label):
        """The pad printed for `label`: its alias, or the label itself."""
        return self.aliases.get(label, label)

    def alias_pads(self):
        """The printed names the aliases give, such as MO and MI."""
        return frozenset(self.aliases.values())


# --- MVP --- (P962, #1380) the one reader of physical.header.joined_pads
@dataclass(frozen=True)
class JoinedPads:
    """
    Value: the groups of pads that the maker's schematic joins inside the board, from `physical.header.joined_pads`
    (the FireBeetle 2 joins 3V3 and 3V3_2, and GND1 and GND2). A group is a tuple of two pads or more, the pads of the
    record's own header. The record says it; a Wokwi geometry says the same as `joined_pins`.
    """

    groups: tuple

    @classmethod
    def from_record(cls, record):
        """
        The groups of a board record. It never raises: a record with no field reads as no group, and so does a field
        with a shape fault (a value that is no list of lists of two pads or more, or a pad in two groups). Only the
        shape is checked here. The rules (a pad of `header_order`, one rail, a source) are `board_rules`' to refuse, so
        a caller reads a record that `validate` passed.
        """
        physical = record.get("physical") if isinstance(record, dict) else None
        header = physical.get("header") if isinstance(physical, dict) else None
        fact = header.get("joined_pads") if isinstance(header, dict) else None
        value = fact.get("value") if isinstance(fact, dict) else None
        if not isinstance(value, list) or not all(
                isinstance(group, list) and len(group) >= 2 and all(isinstance(pad, str) for pad in group) for group in value):
            return cls(())
        pads = [pad for group in value for pad in group]
        return cls(tuple(tuple(group) for group in value)) if len(set(pads)) == len(pads) else cls(())

    def group_of(self, pad):
        """The group that holds `pad`, or `(pad,)` for a pad that no group joins."""
        return next((group for group in self.groups if pad in group), (pad,))
# --- end MVP ---
