"""
What a board house can make and what a part is: read from `data/fabrication.json`, not restated.

Every number here used to be a literal in one to three scripts. Three of them were genuinely two
copies — the chip package power table, the square header pin, the hole plating — so a change to
one was silently missing from the other. One pair was worse than a copy: `check_footprints`
demanded at least 0.25 mm of annular ring and `emit_footprint` drew 0.35, related only by a
sentence in a comment, so raising the checker's minimum would have left the generator emitting
footprints that fail its own check. That relationship is arithmetic now.

Two questions, and they are different:

* **`process`** is what THIS board house can make, and a project may disagree. `.spark/rules.json`
  states its own under `fabrication`, by the same names, and `process(name, rules)` prefers it.
  A fab with a finer process, or a design on 2 oz copper, changes numbers rather than code.
* **`part`** is what a physical component IS. An 0603 dissipates what an 0603 dissipates, so
  nothing overrides these; they live here because more than one script asks.

What is deliberately NOT here is in the file's own `//boundary` note: a law or a published
standard stays in code beside the arithmetic that uses it, with its source in a comment, because
moving it would trade prose that explains a formula for a lookup that does not.
"""

import json
from pathlib import Path

FILE = Path(__file__).resolve().parent.parent / "data" / "fabrication.json"

#: Keys beginning `//` are the prose beside each number — the repository's JSON comment
#: convention, used by every board and part file — and are not values.
DATA = {section: {name: value for name, value in body.items() if not name.startswith("//")}
        for section, body in json.loads(FILE.read_text()).items() if isinstance(body, dict)}


def process(name, rules=None):
    """A fabrication number, or the project's own if its rules file states one under `fabrication`."""
    stated = ((rules or {}).get("fabrication") or {}).get(name)
    return DATA["process"][name] if stated is None else stated


def part(name):
    """A fact about a physical part. Nobody overrides these: an 0603 is an 0603."""
    return DATA["parts"][name]


def header_pin_diagonal_mm():
    """The dimension that actually has to fit through a hole, computed rather than restated."""
    return part("header_pin_side_mm") * 2 ** 0.5


def annular_ring_to_draw_mm(rules=None):
    """
    What a generator puts around a hole: the board house's recommendation plus the margin — or a
    project's own minimum, where it is stricter than that (P57). Never a literal.
    """
    aim = max(process("recommended_annular_ring_mm", rules), process("min_annular_ring_mm", rules))
    return aim + process("annular_ring_margin_mm", rules)
