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
import math
from pathlib import Path

from spark.core.text_guards import ValueMessageError

FILE = Path(__file__).resolve().parent.parent / "data" / "fabrication.json"

#: Keys beginning `//` are the prose beside each number — the repository's JSON comment
#: convention, used by every board and part file — and are not values.
DATA = {section: {name: value for name, value in body.items() if not name.startswith("//")}
        for section, body in json.loads(FILE.read_text()).items() if isinstance(body, dict)}


def process(name, rules=None):
    """A fabrication number, or the project's own if its rules file states one under `fabrication`."""
    stated = ((rules or {}).get("fabrication") or {}).get(name)
    return DATA["process"][name] if stated is None else stated


# --- MVP --- (P434, #576; P454, #615) one reader of a rules file, so a value of the wrong kind or below its lowest is refused where the file is read
#: What `fabrication_problem` says for a rules file whose top level is no object.
WHOLE_FILE = "(top level)"
#: The reasons `fabrication_problem` gives, as codes: the field is no object, no finite number, or below its lowest.
NOT_AN_OBJECT, NOT_A_NUMBER, TOO_LOW = "not-an-object", "not-a-number", "too-low"


class RulesError(ValueMessageError):
    """Error: a rules file cannot be read, or states a `fabrication` value that is no finite number or is below its lowest, and this is why."""


def is_finite_number(value):
    """True for an int or a float that is no bool, no NaN, no infinity and not too big for a float (a 400-digit int)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(float(value))
    except OverflowError:
        return False


def lowest_words(key):
    """The limit of a process key as words: `above 0` or `at least 0`, from the key of its entry in `DATA["lowest"]`."""
    (kind, number), = DATA["lowest"][key].items()
    return "%s %s" % (kind.replace("_", " "), number)


def is_below_lowest(key, value):
    """True when a finite number is refused by the limit of its process key: at or under an `above`, under an `at_least`."""
    limit = DATA["lowest"][key]
    if "above" in limit:
        return value <= limit["above"]
    return value < limit["at_least"]


def fabrication_problem(rules):
    """None for no problem, else `(field, reason)`: the field at fault (WHOLE_FILE, `fabrication`, or `fabrication.<key>` for the
    first key of the process stated wrongly) and why, NOT_AN_OBJECT, NOT_A_NUMBER or TOO_LOW. A null `fabrication` or key is the
    default; other keys are left alone."""
    if not isinstance(rules, dict):
        return WHOLE_FILE, NOT_AN_OBJECT
    stated = rules.get("fabrication")
    if stated is None:
        return None
    if not isinstance(stated, dict):
        return "fabrication", NOT_AN_OBJECT
    for key in DATA["process"]:
        if stated.get(key) is None:
            continue
        if not is_finite_number(stated[key]):
            return "fabrication." + key, NOT_A_NUMBER
        if is_below_lowest(key, stated[key]):
            return "fabrication." + key, TOO_LOW
    return None


def read_rules(path):
    """The rules in a project's rules file, or a RulesError that names the file (and the field)."""
    try:
        rules = json.loads(Path(path).read_text())
    except (OSError, ValueError) as broken:
        raise RulesError("%s could not be read: %s", path, broken) from broken
    problem = fabrication_problem(rules)
    if problem is None:
        return rules
    field, reason = problem
    if reason == NOT_AN_OBJECT:
        raise RulesError("%s: %s is not an object", path, field)
    if reason == NOT_A_NUMBER:
        raise RulesError("%s: %s is not a finite number; write a number, or remove the key to use the default", path, field)
    raise RulesError("%s: %s must be %s; write a larger number, or remove the key to use the default",
                     path, field, lowest_words(field.rpartition(".")[2]))


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
