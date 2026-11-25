"""
The move of a held part from one project to another as an Operation on the core (P1124, #1654): the first project lets go
of its hold, keeps each need that picked the part with no pick, and the second project picks the part for one of its
needs. Without `--apply` it plans fully and writes nothing: it names what each project loses and what goes out of date,
and its next step is the same move with `--apply`, which asks the person first. `release_picks` is the release alone, a
plain function that P1158's close calls too. parts.py is its CLI, through the Operation catalogue.
"""

from collections import namedtuple
from pathlib import Path

from spark.core import outcomes
from spark.core.cli import run_operation
from spark.core.errors import SparkError
from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, WRITES, Argument, Operation
from spark.core.result import Finding, Headline, NextStep, OperationResult
from spark.design import needs
from spark.design.need_requirements import REQUIREMENTS
from spark.design.pick_parts import NO_PASSED_OVER, PickParts
from spark.flow import flow_codes
from spark.idea import idea_codes
from spark.records import store
from spark.sourcing import drawer, record_home

# --- MVP ---
#: The help of `--move-hold`, the one sentence `--describe` prints.
MOVE_HELP = ("with --apply only, move a part that one project holds to another: FROM keeps each need that picked it, with no "
             "pick, and TO picks it for NEED. Without --apply it writes nothing, and says what each project loses and what goes "
             "out of date")
#: The help of `--apply`.
APPLY_HELP = "with --move-hold: write the move, after the person's yes to the plan it printed"
#: What `--help` says after the arguments.
MOVE_DETAILS = ("The drawer is written first, then TO's pick (the drawer, the history, the listing and TO's needs.json, as "
                "--pick writes them), and FROM's needs.json last, so the same move again finishes a move that stopped. "
                "A move of part of a count is refused. After a move that wrote, TO's page.html is written again on disk.")
#: The first line: the part, the two projects, and whether it was written.
HEAD_LINE = "move %s from %s to %s: %s"
#: The end of the first line, without and with `--apply`.
NOT_WRITTEN, WRITTEN = "nothing written yet", "done"
#: A project's heading among the lines.
PROJECT_LINE = "  %s:"
#: A need of FROM whose only pick moves, and one that keeps other picks.
WITHOUT_PICK_LINE = "    %s keeps its need, with no pick (was %s)"
KEEPS_OTHERS_LINE = "    %s keeps its need and %s, without %s"
#: A hold FROM lets go, and one TO lets go.
RELEASE_FROM_LINE = "    %s %d of %d: %s — its pick is taken off, the need stays"
RELEASE_TO_LINE = "    %s %d of %d: %s — no pick of this project explains it"
#: The words of a release and of a listing, without and with `--apply`.
WOULD_RELEASE, RELEASED = "would release", "released"
WOULD_LIST, LISTED = "would list", "listed"
#: TO's pick.
PICK_LINE = "    %s: %s"
#: TO put on the person's list.
LIST_LINE = "    %s %s on your projects"
#: What goes out of date in a project that has requirements.json, and who runs what.
STALE_LINE = "    out of date: %s. Run parts.py --requirements %s, then build."
#: The why of the next step without `--apply`.
NEXT_WHY = "the person says yes to this plan first: the move writes the drawer, the history and both projects' needs.json"
#: The text view's status line: a plan, a move done, a refusal, and a move that stopped (P1032).
PLAN_HEADLINE = "a plan, nothing written: the person says yes, then the same move runs with --apply"
MOVED_HEADLINE = "the hold moved, and the first project kept its need with no pick"
REFUSED_HEADLINE = "the move is refused, and nothing was written"
STOPPED_HEADLINE = "the move stopped before the first project's needs.json was written: the same move again finishes it"
#: The refusals.
SAME_FOLDER_SENTENCE = "%s and %s are one folder: a move takes a part from one project to another"
SAME_NAME_SENTENCE = ("%s and %s are two folders whose holds would go under one name, %s: put one on your projects with "
                      "/spark:init first, so it keeps its own name")
NOT_PICKED_SENTENCE = "no need of %s picks %s, so %s holds no %s to move"
ALREADY_PICKED_SENTENCE = "%s already picks %s for %s, and %s holds it too"
PART_OF_COUNT_SENTENCE = "%s would let go %d of %s and %s would take %d: a move of part of a count is not there yet"
PAIR_SENTENCE = "--move-hold takes FROM, TO and NEED=ID, the need of TO and the part: button=tactile-6mm"
STOPPED_SENTENCE = "%s's pick did not finish, so %s still picks %s: run the same move again once its problem is fixed"
#: The phases a move makes out of date in a project with requirements.json: the requirements its picks wrote, then what
#: was made from them (`flow_codes.MAKES_STALE`).
STALE_PHASES = flow_codes.MAKES_STALE[flow_codes.PICK] + flow_codes.MAKES_STALE[flow_codes.WRITE_REQUIREMENTS]

#: Value: what a release does to one project, written nowhere yet: its needs after, the drawer changes, and each hold let go
#: as {"entry", "was", "now"} (`needs.dropped_holds`).
Release = namedtuple("Release", "after changes released")
#: Value: one project in a move: its listed name, its folder, the ids of its needs the move leaves with no pick, the holds it
#: lets go, and the phases that go out of date (empty when it has no requirements.json).
MoveSide = namedtuple("MoveSide", "name folder needs_without_pick released out_of_date")
#: Value: a move worked out and written nowhere (P883: a plan before the yes). `source` and `target` are MoveSides, `pick`
#: the part as a pick ({kind: id}, or None), `release` FROM's Release, `picked` TO's needs after its pick, `changes` and
#: `events` what TO's pick writes, `listed` whether TO is on the person's list, `adopted` what its listing adopts
#: (`record_home.list_project`), `notes` the pick's notes, `losing` FROM's needs that lose the part (`losing`) and
#: `findings` each refusal: a plan with one writes nothing.
MovePlan = namedtuple("MovePlan", "source target need pick release picked changes events listed adopted notes losing findings",
                      defaults=(None, None, (), (), (), True, (), (), (), ()))


def release_picks(name, current, entries, goes):
    """
    The release of project `name`'s picks that `goes(pick)` says go (P1124): its needs `current` with each such pick taken
    off (a need whose list empties loses its `pick` key, and stays), and the holds that only those picks explained, as
    `needs.dropped_holds` works them out on the drawer `entries`. A hold above its picks stays. Returns a Release and
    writes nothing.
    """
    after = [_without(need, goes) for need in current]
    changes, released = needs.dropped_holds(name, current, after, entries)
    return Release(after, changes, released)


def _without(need, goes):
    """The need with the picks `goes` names taken off, or the need itself when it has none of them."""
    picks = need.get("pick") or []
    kept = [pick for pick in picks if not goes(pick)]
    if len(kept) == len(picks):
        return need
    return dict(need, pick=kept) if kept else {key: value for key, value in need.items() if key != "pick"}


def drawer_after(entries, changes):
    """The drawer `entries` with each change's `after` laid over its entry, as `drawer.apply` would write it."""
    return dict(entries, **{change["entry"]: change["after"] for change in changes})


def out_of_date(folder):
    """The phases a move makes out of date in the project at `folder`: `STALE_PHASES` when it has requirements.json, else none."""
    return list(STALE_PHASES) if (Path(folder) / REQUIREMENTS).is_file() else []


def unpicked(before, after):
    """The ids of the needs that had a pick in `before` and have none in `after`."""
    had = {need["id"] for need in before if need.get("pick")}
    return [need["id"] for need in after if need["id"] in had and not need.get("pick")]


def taken(changes, name, stock):
    """The pieces project `name` gains on the drawer entries of `stock` (increases only: a re-pick also lets go)."""
    return sum(max(change["now"]["used_in"].get(name, 0) - (change["was"].get("used_in") or {}).get(name, 0), 0)
               for change in changes if change["entry"] in stock)


class MoveHold(Operation):
    """
    Operation: move a part that one project (FROM) holds to another (TO), in one step. It plans under the store's lock:
    FROM's release (`release_picks`), then TO's pick on the drawer after it (`needs.plan_pick`), and refuses one folder
    or one name twice, a part FROM does not pick, TO's own problem and a move of part of a count, each a problems Finding
    with nothing written. With `apply` it writes the drawer first, then TO's pick through `PickParts` whole, then FROM's
    needs.json last, so the same move again finishes one that stopped. `needs_file`, `drawer_store` and `picker` are the
    collaborators a test swaps (None: the real ones).
    """

    name = "move-hold"
    details = MOVE_DETAILS
    data_keys = ("from_project", "to_project", "need", "pick", "released", "written", "projects")
    arguments = (Argument(("--move-hold",), "move", str, MOVE_HELP, nargs=3, metavar=("FROM", "TO", "NEED=ID")),
                 Argument(("--apply",), "apply", bool, APPLY_HELP),
                 COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, WRITES)

    def __init__(self, needs_file=None, drawer_store=None, picker=None):
        self.needs, self.drawer, self.picker = needs_file or needs, drawer_store or drawer, picker or PickParts()

    def effects_of(self, values):
        return self.effects if values["apply"] else (READS,)

    def written_project(self, values):
        return Path(values["move"][1])

    def run(self, move, apply, *, outside):
        source, target, given = Path(move[0]).resolve(), Path(move[1]).resolve(), move[2]
        need, _, pick_id = given.partition("=")
        if not (need and pick_id):
            raise SparkError("%s", PAIR_SENTENCE, code=idea_codes.BAD_ARGUMENT_MOVE)
        try:
            with store.locked():
                plan = self.plan(source, target, need, pick_id)
                stopped = self._write(plan, given, outside) if apply and not plan.findings else None
        except (OSError, store.StoreError) as failed:
            raise SparkError("the move of %s was not finished: %s", pick_id, failed, code=idea_codes.MOVE_UNWRITTEN)
        return stopped or self._result(plan, pick_id, move, apply and not plan.findings)

    def plan(self, source, target, need, pick_id):
        """
        The MovePlan of moving `pick_id` from the project at `source` to the need `need` of the project at `target`, both
        resolved folders. It reads FROM's needs and the drawer once (`needs.PickPlan`) and TO through `needs.plan_pick` on
        the drawer after FROM's release. Nothing is written here.
        """
        names = store.plan_listed_name(source), store.plan_listed_name(target)
        if source == target or names[0] == names[1]:
            sentence = SAME_FOLDER_SENTENCE % (source.name, target.name) if source == target else SAME_NAME_SENTENCE % (source, target, names[0])
            return MovePlan(MoveSide(names[0], source, [], [], []), MoveSide(names[1], target, [], [], []), need,
                            findings=[Finding.of(outcomes.PROBLEMS, pick_id, idea_codes.MOVE_SAME_PROJECT, sentence)])
        held = self.needs.PickPlan(source)
        wanted = held.resolve(pick_id)
        release = release_picks(held.name, held.current, held.entries,
                                lambda pick: wanted is not None and needs.as_record(pick, held.known, held.entries) == wanted)
        before = self.needs.read(target)
        picked, changes, events, notes, problems = self.needs.plan_pick(target, [(need, pick_id)], entries=drawer_after(held.entries, release.changes))
        sides = (MoveSide(names[0], source, unpicked(held.current, release.after), release.released, out_of_date(source)),
                 MoveSide(names[1], target, unpicked(before, picked), needs.released_holds(changes, names[1]), out_of_date(target)))
        listed = store.find_listed_name(target) is not None
        adopted = [] if problems else record_home.list_project(target, True)[1]
        already = any(needs.as_record(pick, held.known, held.entries) == wanted for one in before if one["id"] == need
                      for pick in one.get("pick") or [])
        found = self._refusals(held, pick_id, release, sides, (changes, problems, need if already else None))
        gone = next(iter(wanted.values())) if wanted else pick_id
        return MovePlan(sides[0], sides[1], need, wanted, release, picked, changes, events, listed, adopted, notes,
                        losing(held.current, release.after, gone), found)

    def _refusals(self, held, pick_id, release, sides, planned):
        """The Findings that refuse a move: a part FROM does not pick, TO's pick's own problems, a part TO's need already
        picks while FROM still holds it, then a part of a count. `held` is FROM's PickPlan, `planned` TO's pick as (drawer
        changes, problems, the need when TO's need already picks the part, else None). A retry whose FROM holds nothing
        any more lets go nothing, so it is never refused as already picked."""
        (changes, problems, already), wanted = planned, held.resolve(pick_id)
        if release.after == held.current:
            return [Finding.of(outcomes.PROBLEMS, pick_id, idea_codes.MOVE_NOT_PICKED,
                               NOT_PICKED_SENTENCE % (sides[0].name, pick_id, sides[0].name, pick_id))]
        if problems:
            return [Finding(outcomes.PROBLEMS, item["subject"], item.get("code"), item["sentence"], item.get("fix")) for item in problems]
        stock = {key for key in held.entries if needs.as_record({"entry": key}, held.known, held.entries) == wanted}
        let_go = sum(hold["was"] - hold["now"] for hold in release.released if hold["entry"] in stock)
        takes = taken(changes, sides[1].name, stock)
        if already and let_go > 0:
            return [Finding.of(outcomes.PROBLEMS, pick_id, idea_codes.MOVE_ALREADY_PICKED,
                               ALREADY_PICKED_SENTENCE % (sides[1].name, pick_id, already, sides[0].name))]
        if let_go > takes:
            return [Finding.of(outcomes.PROBLEMS, pick_id, idea_codes.MOVE_PART_OF_COUNT,
                               PART_OF_COUNT_SENTENCE % (sides[0].name, let_go, pick_id, sides[1].name, takes))]
        return []

    def _write(self, plan, given, outside):
        """The three writes of a planned move, in their order; the result that stops the move when TO's pick did not finish."""
        self.drawer.apply(plan.release.changes)
        values = {"project_and_picks": [str(plan.target.folder), given], "passed_over": NO_PASSED_OVER, "dry_run": False}
        result = run_operation(self.picker, values, outside=outside, build_outside=lambda effects: outside)
        if result.status() != outcomes.OK:
            stopped = Finding.of(outcomes.COULD_NOT_RUN, None, idea_codes.MOVE_UNWRITTEN,
                                 STOPPED_SENTENCE % (plan.target.name, plan.source.name, given.partition("=")[2]))
            return OperationResult(self._data(plan, False), list(result.findings) + [stopped], lines=list(result.lines),
                                   headline=Headline(STOPPED_HEADLINE, Headline.of_status(outcomes.COULD_NOT_RUN)))
        self.needs.write(plan.source.folder, plan.release.after)
        return None

    def _data(self, plan, written):
        """The `data` of a move: the two projects, the need, the pick, FROM's released holds, whether it wrote, and each side."""
        sides = [{"project": side.name, "needs_without_pick": list(side.needs_without_pick), "released": list(side.released),
                  "out_of_date": list(side.out_of_date)} for side in (plan.source, plan.target)]
        return {"from_project": plan.source.name, "to_project": plan.target.name, "need": plan.need, "pick": plan.pick,
                "released": list(plan.source.released), "written": written, "projects": sides}

    def _result(self, plan, pick_id, move, written):
        """The OperationResult of a move: its lines, and without `--apply` the same move with it as the next step."""
        if plan.findings:
            return OperationResult(self._data(plan, False), list(plan.findings),
                                   headline=Headline(REFUSED_HEADLINE, Headline.of_status(outcomes.PROBLEMS)))
        steps = [] if written else [NextStep(self.name, ["--move-hold"] + list(move) + ["--apply"], NEXT_WHY, [WRITES],
                                             needs_person=True, env=store.read_given_env())]
        return OperationResult(self._data(plan, written), lines=move_lines(plan, pick_id, written), next=steps,
                               notes=[{"subject": None, "sentence": note} for note in plan.notes] or None,
                               headline=Headline(MOVED_HEADLINE if written else PLAN_HEADLINE, Headline.of_status(outcomes.OK)))


def move_lines(plan, pick_id, written):
    """The lines a person reads of a move: the head line, then FROM's and TO's (`side_lines`)."""
    head = [HEAD_LINE % (pick_id, plan.source.name, plan.target.name, WRITTEN if written else NOT_WRITTEN)]
    return head + side_lines(plan, written, True) + side_lines(plan, written, False)


def side_lines(plan, written, source):
    """The lines of one project of a move: FROM's needs that lose the part and its released holds, or TO's pick, its
    released holds, its listing and adoptions; then what goes out of date."""
    side = plan.source if source else plan.target
    release = RELEASED if written else WOULD_RELEASE
    lines = [PROJECT_LINE % side.name]
    if source:
        lines += [KEEPS_OTHERS_LINE % (need_id, ", ".join(kept), pick) if kept else WITHOUT_PICK_LINE % (need_id, pick)
                  for need_id, pick, kept in plan.losing]
        lines += [RELEASE_FROM_LINE % (release, hold["was"] - hold["now"], hold["was"], hold["entry"]) for hold in side.released]
    else:
        lines += [PICK_LINE % (need["id"], ", ".join(_ids(need))) for need in plan.picked if need["id"] == plan.need]
        lines += [RELEASE_TO_LINE % (release, hold["was"] - hold["now"], hold["was"], hold["entry"]) for hold in side.released]
        lines += [] if plan.listed else [LIST_LINE % (LISTED if written else WOULD_LIST, side.name)]
        adopted = [(one, record_home.REFRESHED) for one in record_home.adopted_ids(plan.adopted)] if written else plan.adopted
        lines += ["  " + line for line in record_home.adoption_lines(adopted)]
    return lines + ([STALE_LINE % (", ".join(side.out_of_date), side.folder)] if side.out_of_date else [])


def losing(before, after, gone):
    """(need id, the id of the part that goes, the ids of the picks it keeps) of each need in `before` whose picks change in
    `after`, the needs after a release; `gone` is the id of the part that goes."""
    later = {need["id"]: need for need in after}
    return [(need["id"], gone, _ids(later[need["id"]])) for need in before if _ids(need) != _ids(later[need["id"]])]


def _ids(need):
    """The ids a need's picks name, in order."""
    return [next(iter(pick.values())) for pick in need.get("pick") or []]
# --- end MVP ---
