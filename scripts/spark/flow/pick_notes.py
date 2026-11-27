"""
A pick's notes (P1180): the plain sentences a person needs by a pick before they choose it, each from one fact of its
row of `needs.match` or from the parts list's board-file refusal. The library of the parts reader (`phase_readers`), which
puts them on the pick's Offer; the page, `flow.py show` and `--json` give them as they are, and none decides again.
"""

from spark.design import need_requirements
from spark.flow import flow_codes

# --- MVP ---
#: The verb of the need a board serves (`needs`' board need): a board is a plausible pick for it whatever its words.
COMPUTE = "compute"


def pick_id_of(candidate):
    """The id a pick of `candidate` names: its record's, or its drawer entry's key."""
    return candidate["id"] or candidate["entry"]


def candidate_label(candidate):
    """The part's own name, or its id when its record names none."""
    return candidate.get("label") or candidate["id"] or candidate["entry"]


def board_file_refusal(project, plan, need, candidate):
    """The sentence with which the parts list would refuse a pick of `candidate` for a compute `need` (P991), or None: only for a
    drawer entry that is no record spark knows, and only when the refusal names it — with a board picked by another need,
    the parts list places that board and refuses nothing; with two, it asks for one board. None for any other pick."""
    pick = plan.resolve(pick_id_of(candidate)) if need["does"] == COMPUTE else None
    if not pick or "entry" not in pick:
        return None
    problems = need_requirements.board_problems(plan.after(need["need"], pick), plan.known, plan.entries, project)
    return next((problem["sentence"] for problem in problems if problem["subject"] == pick["entry"]), None)


def pick_notes(project, plan, need, candidate):
    """The notes of a pick of `candidate` (a row of `needs.match`) for the matched `need`, a tuple of sentences in this order:
    spark cannot build from it (`board_file_refusal`), its record owes a fact the parts list needs
    (`need_requirements.blocking_facts`), it is broken, spark cannot simulate it (only when the parts list takes it,
    `need_requirements.refuses`), and the person was not sure they have it. () for none."""
    owed, broken = candidate["owes"], candidate["broken"]
    unsimulated = set(owed) & set(need_requirements.SIMULATION_FACTS) and not need_requirements.refuses(owed, broken)
    facts = ((flow_codes.NO_BOARD_FILE_MESSAGE, board_file_refusal(project, plan, need, candidate)),
             (flow_codes.OWED_NOTE, need_requirements.blocking_facts(owed)),
             (flow_codes.BROKEN_NOTE, broken),
             (flow_codes.NO_STANCE_NOTE % flow_codes.THIS_PART, unsimulated),
             (flow_codes.UNSURE_NOTE, candidate["unsure"]))
    return tuple(note for note, fact in facts if fact)
# --- end MVP ---
