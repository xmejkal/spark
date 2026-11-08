"""
The footprint pad each pin label of a board sits on (P512, #708).

The one reader of a board record's `physical.pad_aliases`, so a trace, a pin line, a breadboard sheet and the record
validator in boards.py all read the pad the silkscreen prints from here.
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
