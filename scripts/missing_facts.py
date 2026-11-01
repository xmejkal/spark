"""
The facts a stage needs and the record lacks (P464): the onboard LED's and button's active level. A stage that
meets one stops short of guessing it, and says so as a Finding with the code `missing_fact`, which every interface
renders through `spark.core.result.envelope_item`. A person tells the fact (`parts.py --fact-set`), research finds it,
or a bench measures it; `level_write_problems` is the rule for what that write may hold.
"""

import board_codes
import boards
import provenance
from spark.core import outcomes
from spark.core.result import Finding

# --- MVP ---
#: Each role whose active level a stage needs, and what the level means for it. One table feeds the Findings and the pin map.
ACTIVE_LEVEL_MEANING = {
    boards.ONBOARD_LED: "the level that lights it",
    boards.ONBOARD_BUTTON: "the level it reads when pressed",
}
LEVEL_FACT = "active_level"
SENTENCE = "%s has no %s in the board record (%s), so the firmware would guess it"
FIX = ("Tell it: write it with `parts.py --fact-set %s FILE` as {value, verified, source}. Find it: run /spark:research. "
       "Or measure it on the bench.")


def list_missing_facts(board):
    """
    One Finding per onboard part of the board whose level a stage needs and whose record names no level, in table order.
    A part with no names for its pins gets none (pins.py writes no line for it), and a null level is missing.
    """
    return [Finding(outcomes.COULD_NOT_RUN, "pin_roles.%s.%s" % (role, LEVEL_FACT), board_codes.MISSING_FACT,
                    SENTENCE % (spec.what, LEVEL_FACT.replace("_", " "), ACTIVE_LEVEL_MEANING[role]),
                    FIX % board.get("id", "<board>"))
            for role, spec, entry in boards.onboard_entries(board)
            if role in ACTIVE_LEVEL_MEANING and boards.names_pins(entry) and provenance.read_value(entry, LEVEL_FACT) is None]


def level_write_problems(values):
    """
    Every way `values` is no write of an active level to a board: only {"pin_roles": {role: {"active_level": fact}}},
    a role of the table, the fact a {value, verified, source} that passes `provenance.fact_problems`. Empty means it holds.
    """
    roles = values.get("pin_roles")
    if set(values) != {"pin_roles"} or not isinstance(roles, dict) or not roles:
        return ["a board takes only pin_roles: {role: {%s: {value, verified, source}}}" % LEVEL_FACT]
    problems = []
    for role, entry in roles.items():
        if role not in ACTIVE_LEVEL_MEANING:
            problems.append("%r is no role whose level a stage needs: %s" % (role, ", ".join(ACTIVE_LEVEL_MEANING)))
        elif not isinstance(entry, dict) or set(entry) != {LEVEL_FACT}:
            problems.append("pin_roles[%r] takes only %s" % (role, LEVEL_FACT))
        elif isinstance(entry[LEVEL_FACT], dict) and entry[LEVEL_FACT].get("value") is None:
            problems.append("pin_roles[%r].%s is absent — a write fills a fact, it never empties one" % (role, LEVEL_FACT))
        else:
            problems += provenance.fact_problems("pin_roles[%r].%s" % (role, LEVEL_FACT), entry[LEVEL_FACT])
    return problems


def merged_roles(record, values):
    """(the record's `pin_roles` with `values["pin_roles"]` merged role by role, what each role held under the written names), so a role keeps its gpio and note."""
    held = record.get("pin_roles") if isinstance(record.get("pin_roles"), dict) else {}
    merged, was = dict(held), {}
    for role, entry in values["pin_roles"].items():
        before = held.get(role) if isinstance(held.get(role), dict) else {}
        merged[role], was[role] = (dict(before, **entry), {key: before.get(key) for key in entry}) if isinstance(entry, dict) else (entry, before)
    return merged, was


def board_write_problems(record, after, path, values, project):
    """
    What refuses a write of `values` to a board record: a board that is not in `project`'s own boards/ (another listed
    project's board is that project's to change), else `level_write_problems`, else each problem `boards.validate` finds in
    `after` that `record` did not have.
    """
    if project is None or path.parent.resolve() != (project / "boards").resolve():
        return ["%s is not a board of this project (%s): copy it into this project's boards/ first, or run from its own project" % (path.stem, project)]
    return level_write_problems(values) or sorted(set(boards.validate(after, path)) - set(boards.validate(record, path)))
# --- end MVP ---
