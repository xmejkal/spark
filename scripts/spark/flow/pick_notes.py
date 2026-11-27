"""
A pick's notes (P1180): the plain sentences a person needs by a pick before they choose it, each from one fact of its
row of `needs.match` or from the parts list's board-file refusal; the first says that a board the person picked has the
part (P1136). Also a pick's words: a board's own part that serves a need (`own_part_of`), and the part's name with it
(`part_words`), which a pick's label and its page row both read. The library of the parts reader (`phase_readers`),
which puts them on the pick's Offer; the page, `flow.py show` and `--json` give them as they are, and none decides again.
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


def is_plausible(need, candidate):
    """True when `candidate` holds the need's words or the matcher scores it above 0 (P976): owned junk takes no place. A
    board is plausible for a compute need whatever its words: the board is what a compute need picks."""
    if need["does"] == COMPUTE and candidate["kind"] == "board":
        return True
    return bool(candidate["what_matches"]) or candidate["score"] > 0


def own_part_of(need, candidate):
    """The board's own part that serves `need` (P1136), as its first `what` word for the need's verb ("onboard button"),
    for a board candidate (a row of `needs.match`) of a need that does not compute; else None."""
    if candidate["kind"] == "board" and need["does"] != COMPUTE and candidate["what"]:
        return candidate["what"][0]
    return None


def part_words(part, own_part):
    """A pick's part as a person reads it (P1136): its name, then the board's own part (OWN_PART) when it has one."""
    return part + flow_codes.OWN_PART % own_part if own_part else part


def is_on_picked_board(plan, need, candidate):
    """True when a compute need of the project picks the board `candidate` and its own part plausibly serves `need`
    (P1136): another need's pick of it, or a part that holds none of the need's words, says nothing."""
    computing = {each["id"] for each in plan.current if each.get("does") == COMPUTE}
    return bool(own_part_of(need, candidate) and is_plausible(need, candidate)
                and computing & set(candidate.get("picked_for", ())))


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
    the board the person picked has it (`is_on_picked_board`, P1136), spark cannot build from it (`board_file_refusal`), its record owes a fact the parts list needs
    (`need_requirements.blocking_facts`), it is broken, spark cannot simulate it (only when the parts list takes it,
    `need_requirements.refuses`), and the person was not sure they have it. () for none."""
    owed, broken = candidate["owes"], candidate["broken"]
    unsimulated = set(owed) & set(need_requirements.SIMULATION_FACTS) and not need_requirements.refuses(owed, broken)
    facts = ((flow_codes.ONBOARD_NOTE, is_on_picked_board(plan, need, candidate)),
             (flow_codes.NO_BOARD_FILE_MESSAGE, board_file_refusal(project, plan, need, candidate)),
             (flow_codes.OWED_NOTE, need_requirements.blocking_facts(owed)),
             (flow_codes.BROKEN_NOTE, broken),
             (flow_codes.NO_STANCE_NOTE % flow_codes.THIS_PART, unsimulated),
             (flow_codes.UNSURE_NOTE, candidate["unsure"]))
    return tuple(note for note, fact in facts if fact)
# --- end MVP ---
