"""
`parts.py --pick`: what each need picks, and what you own of it reserved, as an Operation on the core (P726 PR 3). It was
`parts._op_pick`; `what_a_pick_wrote` was `goal_handlers`'. A pick never reserves past what another project holds; a board given
a need that its own part serves says what a run does not test of the part (`notes`). `--passed-over` is a JSON list the CLI
reads and hands in (`Argument.payload`).
"""

from spark.core import codes
from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, WRITES, Argument
from spark.records import store
from spark.records.answer_operation import ANSWER_ARGUMENTS, AnswerOperation
from spark.records.record_kind import Answer, _cannot, _note
from spark.sourcing import drawer
from spark.sourcing.write_answers import names_your_entries, write_lines
from spark.design import needs

# --- MVP ---
#: The help of `--passed-over`, worded as parts.py's OPTIONS row was.
PASSED_OVER_HELP = "with --pick: the parts passed over and why, a JSON list in FILE (- for stdin) of {need, id, why, by}"
#: The refusal of a pick with no NEED=ID pairs.
PAIRS_SENTENCE = "--pick takes the project, then NEED=ID for each pick: light=led-red-5mm"
PAIRS_FIX = "parts.py --match <project> lists each need's candidates and their ids"
#: The default of `--passed-over`: no file given. An object of its own, so a file that holds `null` is still a payload the
#: planner refuses (a `None` would read as the flag left out).
NO_PASSED_OVER = ()


def what_a_pick_wrote(name, listed, history, events, new_keys, dry_run):
    """
    What a pick writes beyond the drawer, said in its answer (C-17; the PO, 2026-10-08): the project put on the person's list,
    the `reused` lines its history gains, each reason noted — or already noted, and not changed, since the history keeps a
    need's first reason for a part — and a drawer entry's key that the project's own needs.json names from now on, said once.
    """
    seen, new = list(history), []
    for event in events:
        if not store.recorded(event, seen):
            new.append(event)
            seen.append(event)
    reused = sum(1 for event in new if event["event"] == "reused")
    lines = [] if listed else ["  %s %s on your projects" % ("would list" if dry_run else "listed", name)]
    lines += ["  %s to your history: %d reused" % ("would write" if dry_run else "wrote", reused)] if reused else []
    for event in (event for event in events if event["event"] == "passed_over"):
        passed = "%s (%s)" % (next(event[kind] for kind in ("part", "board", "entry") if kind in event), event["need"])
        lines.append("  %s why you passed over %s" % ("would note" if dry_run else "noted", passed) if event in new else
                     "  already noted, not changed: why you passed over %s — your history keeps the first reason" % passed)
    return lines + names_your_entries("needs.json", new_keys, dry_run)


class PickParts(AnswerOperation):
    """Operation: `pick` as parts.py answers it: each need's picks, what was reserved and released, what the pick wrote
    beyond the drawer, the notes; a refusal writes nothing."""

    name = "pick"
    data_keys = ('project', 'picks', 'reserved', 'released', 'written')
    arguments = (Argument(("--pick",), "project_and_picks", str,
                          "set what each need picks (NEED=ID: a record, or a drawer entry) and reserve what you own of it — never past what another project holds; "
                          "what it notes is under `notes`: a board given a need that its own part serves says what a run does not test of the part, "
                          "and the other choice", nargs="+", metavar=("PROJECT", "NEED=ID")),
                 Argument(("--passed-over",), "passed_over", str, PASSED_OVER_HELP, NO_PASSED_OVER, metavar="FILE", payload=0),
                 ANSWER_ARGUMENTS["dry_run"], COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, WRITES)

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def build_answer(self, project_and_picks, passed_over, dry_run):
        target, given = project_and_picks[0], project_and_picks[1:]
        pairs = [tuple(one.split("=", 1)) for one in given if "=" in one]
        if not pairs or len(pairs) != len(given):
            return Answer(unchecked=[_cannot(PAIRS_SENTENCE, PAIRS_FIX, code=codes.BAD_ARGUMENT)])
        reasons = [] if passed_over is NO_PASSED_OVER else passed_over
        history = store.events()  # read whole before the first write: one that cannot be read refuses the pick, with nothing written
        listed, keys_before = store.find_listed_name(target) is not None, needs.entry_keys(needs.read(target))
        after, changes, events, notes, problems = needs.plan_pick(target, pairs, reasons)
        if not problems and not dry_run:
            store.add_project(target)
            drawer.apply(changes)
            for event in events:
                store.append_event(event)
            # the project's own file last: a store that refuses leaves it as it was, and the same pick, retried, finishes the rest
            needs.write(target, after)
        asked, name = dict(pairs), store.plan_listed_name(target)
        picks = [{"need": need["id"], "pick": need.get("pick") or []} for need in after if need["id"] in asked]
        said = [] if problems else ["  %s: %s" % (one["need"], ", ".join(next(iter(pick.values())) for pick in one["pick"])) for one in picks]
        released = needs.released_holds(changes, name)
        said += [] if problems else ["  %s%s: %s — no pick of this project explains it" % (
            "would release" if dry_run else "released", "" if hold["now"] == 0 else " %d of %d" % (hold["was"] - hold["now"], hold["was"]),
            hold["entry"]) for hold in released]
        wrote = [] if problems else what_a_pick_wrote(name, listed, history, events, needs.entry_keys(after) - keys_before, dry_run)
        return Answer({"project": name, "picks": picks,
                       "reserved": [{"entry": change["entry"], "used_in": change["now"]["used_in"]} for change in changes],
                       "released": released, "written": not problems and not dry_run},
                      write_lines(changes, problems, dry_run, said + ["  %s" % note for note in notes] + wrote), problems=problems,
                      notes=[_note(note) for note in notes])
# --- end MVP ---
