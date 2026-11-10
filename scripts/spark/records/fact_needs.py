"""
Who reads which fact of a part record (P738, #1014): the rows of `data/fact-needs.json`, read here and nowhere else.

The file is the one place that says "this consumer reads this fact". `--unverified` names the readers of each open
fact from it, and a test imports every consumer and finds the fact in its source. It imports no consumer itself: the
arrows run from the consumers to the records, never back.
"""

import json
from dataclasses import dataclass
from pathlib import Path

FILE = Path(__file__).resolve().parents[3] / "data" / "fact-needs.json"

# --- MVP --- (P738, #1014) the fact need tree, facts only
#: A consumer's status toward a fact: it reads the fact today, or a card (`FactNeed.card`) will make it read.
READS, WILL_READ = "reads", "will read"


@dataclass(frozen=True)
class FactNeed:
    """Value: one consumer's need of one fact of a part record of one kind. `fact_path` is dotted inside a block."""

    kind: str
    fact_path: str
    consumer: str
    status: str
    card: str = None

    @property
    def reads(self):
        """Whether the consumer reads the fact today."""
        return self.status == READS

    @property
    def fact_name(self):
        """The last segment of `fact_path`: the literal a consumer's source names."""
        return self.fact_path.rpartition(".")[2]

    def to_dict(self):
        """The reader as an envelope entry: who, whether today, and the card that makes it read."""
        return {"consumer": self.consumer, "status": self.status, "card": self.card}


@dataclass(frozen=True)
class FactNeeds:
    """Value: every row of the file, asked by kind or by the fact an open row writes back to, and the question research
    asks for a fact path it finds absent (P737): `{text, unit, answer_form, example}` by fact path."""

    rows: tuple
    questions: dict = None

    @classmethod
    def from_file(cls, path=FILE):
        """The rows under `needs` and the `questions` by fact path; the file's `//` key is prose beside them."""
        held = json.loads(Path(path).read_text())
        return cls(tuple(FactNeed(**row) for row in held["needs"]), dict(held.get("questions") or {}))

    def question_of(self, fact_path):
        """The question research asks for this fact path, or None when the file has none."""
        return (self.questions or {}).get(fact_path)

    def of_kind(self, kind):
        """The needs of a part of this kind."""
        return [need for need in self.rows if need.kind == kind]

    def of_fact(self, write):
        """The needs of one fact, by the `write` key an unverified row carries (`body_mm`, `facts.<name>`): exact."""
        return [need for need in self.rows if need.fact_path == write]
# --- end MVP ---
