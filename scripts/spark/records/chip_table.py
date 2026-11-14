"""
Facts about each chip that a board rule reads (P809): the rows of `data/chips.json`, read here and nowhere else.

One fact today, `adc2_used_by_wifi`, cited to ESP-IDF v5.5.1. `board_rules.adc2_role_problems` reads it: a board whose
chip shares ADC2 with Wi-Fi names the `adc2_unusable_with_wifi` role. A chip the table lacks, or holds as null, is a
reading that could not be made (`outcomes.NOT_CHECKED`), which `boards.py --validate` says aloud.
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
    """Value: one fact of one chip. RECORDED holds `value` (True or False); NOT_CHECKED holds `why` and no value."""

    state: str
    value: bool = None
    why: str = None


@dataclass(frozen=True)
class ChipTable:
    """Value: the table's facts by chip, read only. Built from the file's `chips` object, or from a dict in a test."""

    chips: types.MappingProxyType

    @classmethod
    def from_dict(cls, chips):
        """The table of a `chips` object: chip -> {fact name -> {value, cites}}."""
        return cls(types.MappingProxyType(dict(chips)))

    def adc2_used_by_wifi(self, chip):
        """Whether `chip` shares ADC2 with Wi-Fi, as a ChipFact; NOT_CHECKED for a chip the table lacks or holds as null."""
        fact = self.chips.get(chip, {}).get("adc2_used_by_wifi") if isinstance(chip, str) else None
        value = fact.get("value") if isinstance(fact, dict) else None
        if isinstance(value, bool):
            return ChipFact(outcomes.RECORDED, value)
        return ChipFact(outcomes.NOT_CHECKED, why="%s holds no ADC2 fact for chip %r" % (FILE.relative_to(FILE.parents[1]), chip))


@functools.lru_cache(maxsize=None)
def load(path=FILE):
    """The shipped table, read once per process: every board load asks it."""
    return ChipTable.from_dict(json.loads(Path(path).read_text())["chips"])
