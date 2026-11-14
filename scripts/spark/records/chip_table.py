"""
Facts about each chip that a board rule reads (P809): the rows of `data/chips.json`, read here and nowhere else.

One fact today, `adc2_used_by_wifi`, cited to ESP-IDF v5.5.1. `board_rules.adc2_role_problems` reads it: a board
whose chip shares ADC2 with Wi-Fi names the `adc2_unusable_with_wifi` role. The lookup follows the reader rule in
`outcomes`: a chip the table lacks or holds as null is NONE_RECORDED. It has no row in test_outcomes' READERS, because
it reads no file that may be absent: `load` reads the shipped table, a required thing, and raises.
"""

import functools
import json
import types
from dataclasses import dataclass
from pathlib import Path

from spark.core import outcomes

FILE = Path(__file__).resolve().parents[3] / "data" / "chips.json"


@dataclass(frozen=True)
class ChipFact:
    """Value: one fact of one chip. RECORDED holds `value` (True or False); NONE_RECORDED holds no value."""

    state: str
    value: bool = None
    why = None  # the reader rule's field: a lookup in a loaded table is never NOT_CHECKED


@dataclass(frozen=True)
class ChipTable:
    """Value: the table's facts by chip, read only. Built from the file's `chips` object, or from a dict in a test."""

    chips: types.MappingProxyType

    @classmethod
    def from_dict(cls, chips):
        """The table of a `chips` object: chip -> {fact name -> {value, cites}}."""
        return cls(types.MappingProxyType(dict(chips)))

    def adc2_used_by_wifi(self, chip):
        """Whether `chip` shares ADC2 with Wi-Fi, as a ChipFact; NONE_RECORDED for a chip the table lacks or holds as
        null, and for a chip that is no string."""
        fact = self.chips.get(chip, {}).get("adc2_used_by_wifi") if isinstance(chip, str) else None
        value = fact.get("value") if isinstance(fact, dict) else None
        return ChipFact(outcomes.RECORDED, value) if isinstance(value, bool) else ChipFact(outcomes.NONE_RECORDED)


@functools.lru_cache(maxsize=None)
def load(path=FILE):
    """The shipped table, read once per process: every board load asks it."""
    return ChipTable.from_dict(json.loads(Path(path).read_text())["chips"])
