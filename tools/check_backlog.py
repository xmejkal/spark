#!/usr/bin/env python3
"""
W14 and the WIP limits on the spark project's open items (P102a; docs/2026-10-05-backlog-in-github-design.md §3 and
§8; raised on 2026-10-06 at the PO's word, P146, and again that evening to two per working stage and four in flight; P978, the PO, 2026-11-21: Build 3 and flight 5 for spark).
A card is asked for its Needed by and slice from Ready on — the commitment — not in Idea, Discovery or Design (P146).
A card that waits on someone is asked since when, in any open stage and a riding task too: a Waiting on with no Waiting
since is named (P146).
One card at a time may carry the label `expedite`, the PO's way past a limit: it lets its working stage, and its own
lane's flight, hold one over, and Ready none — it enters Build; two open cards labelled so are named (P146, decision 4 of
docs/2026-10-06-process-design.md).
The bin's board is read too, for three things: its cards in a working stage fly in the spark lane (a bench session,
labelled `bench`, sits outside it), the expedite is one card across both boards, and a card of its that waits on someone
is asked since when like any (the spec, §1: "The bin's desk cards count in the same three. A bench session is your hands,
so it sits outside them"). They fill none of spark's stages and are asked for no Needed by or slice (P146).
Ready, Build and the flight are judged per lane, by the card's slice: spark's cards and the sound slices' each have their
own places (LANES; P730, the PO, 2026-11-09, and P918, the PO, 2026-11-18: "A flight total per lane").
Run by tools/check_commit.py at every push. With no network or no gh it says it could not look, and passes: the gate
must work offline. So does a look that was only partial — not the bin's board (spark's cards are counted alone): a line
says so with the cause, and the push goes through (W1: said, never read as checked). A bin board that was read is said
too: the summary line carries its open count. The boards are read by board_read.py, the reader board.py shares (P811):
one GraphQL query per 100 items, 1 point a page, each task's parent story in the same answer. The whole board is read,
or nothing is judged (P168): a board whose pages held fewer items than it holds, or whose items held no issue, is
could-not-run with the numbers — spark's as the gate's one line, the bin's as its unread line. A draft or a pull
request on a board is no card. What the read cost is said in one line (COST_LINE) when it cost more than COST_FLOOR or
the look was not whole, so a normal push stays quiet. Where a card stands is one
rule for both readers, stage_of() (P167): a Status among KNOWN is its stage, a card with no Status is in Idea and said in
one line, a Status the gate does not know is could-not-run naming the card and the stage, and a board with no Status on
any card is could-not-run naming the shape — spark's; the bin's in that shape is set aside like one read in part.
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import board_read  # noqa: E402

OWNER, TITLE = "xmejkal", "spark"
#: The bin's project. Its cards in a working stage fly in the spark lane, and the expedite is one card across both
#: boards (the spec §1: "The bin's desk cards count in the same three"); they fill none of spark's stages.
BIN_TITLE = "the bin"
#: What problems() marks a card of the bin's board with, so a sentence names it apart from spark's: `bin #12`, not `#12`.
BIN_BOARD = "bin"
#: What main() and the status say when the bin's board could not be read: spark's cards were counted alone, and the bin's
#: expedite and waits were not checked either. A could-not-look, not a failure — said with its cause, and the push goes
#: through (W1).
BIN_UNREAD = "the bin's board could not be read (%s) — its cards were not counted or checked"
# --- MVP ---
@dataclass(frozen=True)
class Lane:
    """
    A part of the board with its own limits, told by the card's slice: its name as a sentence prints it, the slices that
    are its (none: every other card), its (stage, limit) pairs, the most of its cards in flight (IN_FLIGHT), and the most
    of its cards that wait on the PO in a working stage (waits_apart).
    """
    name: str
    slices: tuple
    limits: tuple
    flight: int
    waiting: int


#: The two lanes. Spark's is first and takes every card that is not another lane's: one on any other slice, one with no
#: slice, and every card of the bin (lane_of). Ready and Build since P730 (the PO, 2026-11-09): spark 4 and 2, sound, the
#: slices "pixel-games" and "graphics library", 1 and 1. The flight since P918 (the PO, 2026-11-18): spark 4, the number
#: that was the whole board's since 2026-10-06 evening (P146), and sound 2. The cards that wait on the PO since P928's
#: first slice (2026-11-19, the plan council's number, the PO's to change): 2 in each lane. P978, the PO, 2026-11-21: Build 3
#: and flight 5 for spark.
LANES = (Lane("spark", (), (("Ready", 4), ("Build", 3)), 5, 2),
         Lane("sound", ("pixel-games", "graphics library"), (("Ready", 1), ("Build", 1)), 2, 2))
#: The stages held across the whole board (§3); Idea and Done carry no limit. Every working stage takes 2, the PO's call of
#: 2026-10-06 evening (P146). Ready and Build are not here: LANES holds them (P730).
LIMITS = {"Discovery": 2, "Design": 2, "Review": 2}
#: Every stage the gate knows (P167), in the board's order.
STAGES = ("Idea", "Discovery", "Design", "Ready", "Build", "Review", "Done")
IN_FLIGHT = ("Discovery", "Design", "Build", "Review")
#: From the commitment on (Ready, Build, Review) a card carries its Needed by and slice; in Idea, Discovery and Design
#: it decides whether to build, and the PO's order into Ready is what commits. P146, docs/2026-10-06-process-design.md:
#: the skeptic pass's item 6 ("the gate checks a slice from Ready on, not from Discovery on") and §1 ("Your order into
#: Ready commits"). A card with no Status is not asked either, like Idea (stage_of).
JUDGED = ("Ready", "Build", "Review")
#: The stages the gate knows (P167), STAGES. A card whose Status is any other
#: word stands in a stage somebody renamed or added on the board, and the gate judges nothing until that is a decision.
#: `--help` lists these, so the two cannot drift.
KNOWN = STAGES
#: Where a card with no Status stands: GitHub's "No status" column holds a new item, which is the board's own state —
#: not counted, not judged, and said (no_stage()).
NO_STAGE_IS = "Idea"
#: What no_stage() says of the spark board when no card of it has a Status: not new items but the field's keys changed,
#: or every card is new — either way the gate knows no stage, and judges nothing (could-not-run, P167).
NO_STATUS = "no card of the %d on the spark board has a Status — the field's keys may have changed, or every card is new"
#: The bin's why in BIN_UNREAD for the same shape: the bin's board is set aside with its cause and spark's cards are
#: counted alone, as when it was read in part — one convention for the bin's failing, in fetch() and board.gather().
BIN_NO_STATUS = "no card of its %d has a Status"
#: The one sentence shape of a broken limit: what holds (a stage, or IN_FLIGHT_HOLDS), its lane's mark or none, how many,
#: which cards, the limit, and what to do.
HOLDS = "%s%s holds %d (%s) — its limit is %d: %s"
#: What HOLDS names a lane's flight: the cards of its four working stages together (IN_FLIGHT).
IN_FLIGHT_HOLDS = "In flight"
#: The board's Waiting on option for the PO, the one wait that is counted apart (waits_apart); board.py reads it too.
THE_PO = "the PO"
#: What HOLDS names a lane's cards that wait on the PO in a working stage, and what such a lane is told to do: no card
#: in work can be finished to free a place, so the newest goes back, and its wait and a comment keep what it was.
WAITING_HOLDS = "Waiting on %s" % THE_PO
WAITING_DOES = ("the newest (%%s) goes back to Idea with its wait kept and a comment that names its stage, until %s answers "
                "one" % THE_PO)
#: The one way past a limit, on the PO's word only (decision 4): a card labelled so may take its working stage, and its
#: lane's flight, one over its limit. One card at a time — the gate fails on two (P146).
EXPEDITE = "expedite"
#: The bin's label for a bench session — the PO's own hands at the bench, which sits outside the limits (the spec, §1: "A
#: bench session is your hands, so it sits outside them"). A bin card labelled so flies in no lane (P146).
BENCH = "bench"
#: Where a wait with no Waiting since sorts among dated ones: after every date, so it reads as the newest.
UNDATED = "9999-12-31"
#: Under this many GraphQL points a whole look stays quiet about its cost (P811): a normal push reads about 9 (a page per
#: 100 items, the project list); more than this says the cost, as does a look that was not whole.
COST_FLOOR = 50
#: The cost line: GitHub's own rateLimit.cost summed over the calls that answered, and the lowest remaining they gave.
COST_LINE = "  backlog: the board read cost %d GraphQL points in %d calls; %s of %s left this hour"

def _section(body, name):
    body = (body or "").replace("\r\n", "\n")  # GitHub keeps a body's line endings as they were typed
    match = re.search(r"^### %s[ \t]*\n(.*?)(?=^### |\Z)" % re.escape(name), body, re.S | re.M)
    text = match.group(1).strip() if match else ""
    return "" if text == "_No response_" else text


def _ref(entry):
    """A card as a sentence names it: `#12`, or `bin #12` for one of the bin's (problems() marks those, BIN_BOARD)."""
    return "%s#%s" % (BIN_BOARD + " " if entry.get("board") == BIN_BOARD else "", entry["content"].get("number"))


def _name(entry):
    return "%s %s" % (_ref(entry), entry["content"].get("title", ""))


class UnknownStage(Exception):
    """
    A board whose shape the gate cannot read (P167): a card in a stage it does not know, or no card with a Status at all
    (the field's keys changed). Both readers say could-not-run with its sentence and judge nothing (W1).
    """


def stage_of(entry):
    """
    The stage a card stands in — the one rule both readers follow (P167). Its Status when the gate knows it (KNOWN);
    NO_STAGE_IS for a card with none, GitHub's "No status" column, where a new item lands; UnknownStage for a Status the
    gate does not know — a renamed or added stage must be a decision, not a silent skip, so nothing is judged.
    """
    status = entry.get("status")
    if not status:
        return NO_STAGE_IS
    if status not in KNOWN:
        raise UnknownStage('%s is in a stage the gate does not know: "%s"' % (_name(entry), status))
    return status


def _marked(bin_items):
    """Copies of the bin's cards marked as its (BIN_BOARD), so a sentence names them `bin #12`; the caller's stay unmarked."""
    return [dict(entry, board=BIN_BOARD) for entry in (bin_items or ())]


def no_status_on(cards):
    """
    Whether `cards` are a board with cards and no Status on any of them (P167): not new items in the "No status" column
    but a changed field, or every card new — a shape the gate cannot place. The one rule for both readers, which set the
    bin's board aside over it (fetch(), board.gather()) and say could-not-run over spark's (no_stage()).
    """
    return bool(cards) and not any(entry.get("status") for entry in cards)


def no_stage(items, bin_items=()):
    """
    The line naming the cards with no Status — `3 card(s) have no stage: #2, #5, bin #20` — or None when every card has
    one. The spark board with no Status on any card (no_status_on) is UnknownStage naming the shape, NO_STATUS;
    problems() reads this first, so it cannot judge such a board. The bin's board in that shape never reaches here: fetch()
    and board.gather() set it aside first, as the bin's unread line.
    """
    if no_status_on(items):
        raise UnknownStage(NO_STATUS % len(items))
    unstaged = [_ref(entry) for entry in [*items, *_marked(bin_items)] if not entry.get("status")]
    return "%d card(s) have no stage: %s" % (len(unstaged), ", ".join(unstaged)) if unstaged else None


def rides(entry):
    """
    Whether a card is a task riding on its open story: it is counted nowhere
    itself, asked for no Needed by or slice, and not the expedite's holder — but its wait is asked, like every open card's.
    """
    return "task" in (entry.get("labels") or []) and entry.get("parent") is not None


def counts(entry):
    """
    Whether an open card counts against the limits: a task rides on its story, so it does not count — unless it has no
    parent story at all or only a closed one (board_read.open_parent), when it is a card of its own (P146); an epic counts in no stage, and its stories carry the limit (R9, the PO, 2026-10-18: WIP experiment A, broad form, to 2026-11-02).
    board.py reads the same rule.
    """
    labels = entry.get("labels") or []
    if "task" in labels:
        return entry.get("parent") is None
    return "epic" not in labels


def waits_apart(entry):
    """
    Whether a card is counted apart from the cards in work (P928's first slice): it stands in a working stage and waits
    on the PO. Such a card fills neither its stage nor its lane's flight; it counts in its lane's waiting total. A wait
    on anyone else, and a wait in Idea or Ready, changes nothing. board.py marks the same cards (one rule).
    """
    return entry.get("status") in IN_FLIGHT and entry.get("waiting on") == THE_PO


# --- MVP ---
def lane_of(entry):
    """
    The lane a card's places come from (P730): the one whose slices hold the card's, else the first, spark's — a card
    with no slice too, and every card of the bin whatever its slice (P918; problems() marks those, BIN_BOARD).
    """
    if entry.get("board") != BIN_BOARD:
        for lane in LANES:
            if entry.get("slice") in lane.slices:
                return lane
    return LANES[0]


def problems(items, bin_items=()):
    """
    Every sentence the gate fails on: a card with no Needed by or no slice — asked from Ready on, the commitment
    (JUDGED), not in Idea, Discovery or Design — a card that waits on someone (any name) with no Waiting since, in any
    open stage and a riding task included (the status lists every open wait, so the gate asks for every open date), two
    open cards labelled expedite (whatever their stage or board), and a broken WIP limit. A working stage, or a lane's
    flight, may hold one over its limit while exactly one of the cards it holds is the expedite; Ready, a queue the
    expedite never enters, may not. An epic counts nowhere; a task (a plan's step, a sub-issue of
    its story) rides on its open story and is judged only on its wait — unless it has no open parent story, when it is a card
    like any other (counts()). A Done card is not judged at all. Where a card stands is stage_of()'s word: a card in a
    stage the gate does not know, or a board with no Status on any card, is UnknownStage, and nothing is judged (P167).
    `bin_items` is the bin's board, or None when it could not be read (main() says so; nothing is said here). Its cards
    in a working stage that count (counts()) fly in the spark lane (lane_of) — all but a `bench` session, which sits
    outside the limits — and its expedite is the same one card; a card of its that waits on someone is asked since when,
    like any. They fill none of spark's stages and are asked for no Needed by or slice. A sentence names them `bin #12`.
    A flight's sentence lists its cards as the boards hold them, spark's first. A card in a working stage that waits on
    the PO (waits_apart) is in neither its stage's count nor its lane's flight: it is in its lane's waiting total, which
    takes no extra place from the expedite, and whose sentence lists the cards oldest wait first.
    """
    no_stage(items, bin_items)  # a board with no stage on any card is not judged (UnknownStage); its line is main()'s to say
    said, by_stage = [], {}
    flying, waiting = ({lane.name: [] for lane in LANES} for _ in range(2))
    bin_cards = _marked(bin_items)
    for entry in [*items, *bin_cards]:
        status = stage_of(entry)  # UnknownStage for a stage the gate does not know: nothing is judged (P167)
        if status == "Done":
            continue
        # The bin's cards fill none of spark's stages and are asked for no Needed by or slice; the wait is asked of both.
        from_spark = entry.get("board") != BIN_BOARD
        # The wait is asked of every open card, a riding task included: the status lists them all (board._waits).
        if entry.get("waiting on") and not entry.get("waiting since"):
            said.append("%s: waits on %s since nobody knows — set Waiting since" % (_name(entry), entry["waiting on"]))
        if rides(entry):
            continue  # a riding task is its story's; a parentless one is judged like any card
        apart = waits_apart(entry)  # a card that waits on the PO is in no stage's count and in no flight (P928)
        if from_spark and counts(entry) and not apart:
            by_stage.setdefault(status, []).append(entry)
        # A bench session is the PO's hands and sits outside the limits (the spec, §1): a bin card labelled so does not fly.
        if status in IN_FLIGHT and counts(entry) and (from_spark or BENCH not in (entry.get("labels") or [])):
            (waiting if apart else flying)[lane_of(entry).name].append(entry)
        if from_spark and status in JUDGED:
            if not _section(entry["content"].get("body"), "Needed by"):
                said.append("%s: no `Needed by` — W14: an item names the design that needs it" % _name(entry))
            if not entry.get("slice"):
                said.append("%s: on no slice of the story map" % _name(entry))
    # A story and the task riding on it, both labelled, are one rush: the task is counted nowhere itself.
    rushed = [e for e in [*items, *bin_cards]
              if e.get("status") != "Done" and not rides(e) and EXPEDITE in (e.get("labels") or [])]
    if len(rushed) > 1:
        said.append("%d cards labelled expedite (%s) — one at a time, on the PO's word"
                    % (len(rushed), ", ".join(_ref(e) for e in rushed)))

    def over(held, limit):
        """Whether `held` breaks `limit`: one over is allowed while exactly one of its cards is the expedite."""
        allowance = 1 if sum(1 for e in held if EXPEDITE in (e.get("labels") or [])) == 1 else 0
        return len(held) > limit + allowance

    for stage in STAGES:
        # Ready and Build are held per lane (P730); the other stages are held across the whole board.
        lanes = [(lane, " (%s)" % lane.name, dict(lane.limits)[stage]) for lane in LANES
                 if stage in dict(lane.limits)] or ([(None, "", LIMITS[stage])] if stage in LIMITS else [])
        for lane, mark, lane_limit in lanes:
            held = [e for e in by_stage.get(stage, []) if lane in (None, lane_of(e))]
            # The expedite enters Build, so it lends a working stage a place; Ready is a queue it never enters: none.
            if (over(held, lane_limit) if stage in IN_FLIGHT else len(held) > lane_limit):
                said.append(HOLDS % (stage, mark, len(held), ", ".join(_ref(e) for e in held), lane_limit,
                                     "the PO moves one back to Idea" if stage == "Ready" else "finish one before starting another"))
    for lane in LANES:
        # Each lane flies on its own (P918): one lane's cards never fill the other's flight, and the expedite lends its own.
        if over(flying[lane.name], lane.flight):
            said.append(HOLDS % (IN_FLIGHT_HOLDS, " (%s)" % lane.name, len(flying[lane.name]),
                                 ", ".join(_ref(e) for e in flying[lane.name]), lane.flight,
                                 "the %s lane finishes one before starting another" % lane.name))
        # The waiting total is a plain count: the expedite lends it no place. Oldest wait first, an undated one last.
        held = sorted(waiting[lane.name], key=lambda e: e.get("waiting since") or UNDATED)
        if len(held) > lane.waiting:
            said.append(HOLDS % (WAITING_HOLDS, " (%s)" % lane.name, len(held), ", ".join(_ref(e) for e in held),
                                 lane.waiting, WAITING_DOES % _ref(held[-1])))
    return said


def _gh(*args):
    return json.loads(subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60, check=True).stdout)


class PartialRead(Exception):
    """
    A board read in part (P168): its pages held fewer items than it holds, or its items held no issue (board_read.unread
    says which). The gate never judges part of a board — W1: a look that was only partial says so, and is not read as
    "the limits hold".
    """


def _cards(number, subject, spent):
    """The cards of the project numbered `number`, read whole (board_read), or PartialRead naming `subject`."""
    project = board_read.read_board(number, _gh, spent)
    short = board_read.unread(subject, project)
    if short:
        raise PartialRead(short)
    return board_read.to_items(project)


def fetch(spent=None):
    """
    (the spark project's cards, the bin project's cards, the bin's why). The projects are found by title in one call,
    and each board read whole by board_read, its tasks' parent stories in the same answer (open_parent); each answer's
    cost is added to `spent` when given. Raised for main(): board_read.Unreadable when gh or the network could not be
    reached or answered no board; LookupError for a spark project gh cannot find — the check must never quietly stop
    looking; PartialRead for a spark board read in part, of which nothing is judged (P168). The bin's board is read for
    the spark lane's flight, the expedite and its waits alone, so its failing — no project titled BIN_TITLE, a read that errors,
    one read in part, or one with no Status on any card (no_status_on) — costs nothing else: its cards are None and the
    bin's why says what went wrong, for main() to say. board.gather() sets it aside the same way, so the two readers
    cannot disagree over the bin.
    """
    numbers = board_read.projects(_gh, spent)
    if TITLE not in numbers:
        raise LookupError("no project titled %r under %s — the board cannot be checked" % (TITLE, OWNER))
    items = _cards(numbers[TITLE], "the spark board", spent)
    if BIN_TITLE not in numbers:
        return items, None, "no project titled %r under %s" % (BIN_TITLE, OWNER)
    try:
        bin_items = _cards(numbers[BIN_TITLE], "it", spent)
    except (PartialRead, board_read.Unreadable) as unread:
        return items, None, str(unread)
    if no_status_on(bin_items):  # read whole, but a shape the gate cannot place: set aside like one read in part
        return items, None, BIN_NO_STATUS % len(bin_items)
    return items, bin_items, None


def cost_line(spent):
    """
    COST_LINE over `spent`, the rateLimit of each answer: their costs summed, and the lowest remaining of them — GitHub's
    answers come back out of order, so the last one's may not be the latest; None for none.
    """
    if not spent:
        return None
    return COST_LINE % (sum(each["cost"] for each in spent), len(spent), "{:,}".format(min(each["remaining"] for each in spent)),
                        "{:,}".format(spent[-1]["limit"]))


#: What `--help` says the gate checks; the limits are filled in from LIMITS and LANES, and the stages from
#: KNOWN, so the help cannot drift from the numbers the gate holds a board to or the stages it knows.
CHECKS = """\
The pre-push gate over the two GitHub Projects boards, spark's and the bin's, read through the
PO's own gh login. tools/check_commit.py runs it at every push; it takes no arguments.

It fails on:
  - a stage over its WIP limit: %(limits)s, held across both lanes;
    Ready and Build are counted per lane, by the card's slice: %(lanes)s;
  - a lane with too many cards in flight, Discovery, Design, Build and Review together:
    %(flights)s. A lane is told by the card's slice: %(slices)s; every other
    card, one with no slice and every card of the bin's are the spark lane's;
  - a lane with too many cards that wait on the PO in a working stage: %(waits)s. Such a
    card counts here, and in neither its stage nor its lane's flight. A wait on anyone else, and
    a wait in Idea or Ready, changes nothing; the expedite lends this total no place;
  - two open cards labelled `expedite`. One card at a time may carry it, on the PO's word: its
    working stage, and its lane's flight, may then hold one over their limit. Ready never;
  - a card that waits on someone (Waiting on) with no Waiting since, in any open stage, on either
    board, a task riding on its story included;
  - a card of spark's in Ready, Build or Review with no `Needed by` section or on no slice: the
    commitment starts at Ready, so Idea, Discovery and Design are not asked.

The stages it knows: %(known)s. A card in any other stage
is could-not-run naming it, and nothing is judged; a card with no Status is in Idea, and said. The
bin's board read in part, or with no Status on any card, is set aside and said, and spark's cards
are counted alone. A draft or a pull request on a board is no card.

How cards count: an epic counts in no stage, and its stories carry the
limit (R9, standing since 2026-11-05). A task under an open story rides on it and counts nowhere;
a task with no parent story, or only a closed one, is a card of its own. The bin's cards in a
working stage fly in the spark lane (a bin card labelled `bench` sits outside it) and
fill none of spark's stages.
"""
#: The exit codes `--help` names (W1: a look that could not run says so, and is never read as checked).
EXIT_CODES = """\
exit codes:
  0  the limits hold — or could-not-run: gh or the network could not be reached, the spark board was
     read in part or its items held no issue, a card is in a stage the gate does not know, or no card
     has a Status — said with its cause, and the limits were not checked. A partial look (the bin's
     board unread, or read in part) is said with its cause too, and so are cards with no Status. What
     the read cost is said when it was more than %(floor)d GraphQL points or the look was not whole.
  1  a problem, each named on a line of its own — or no project titled "spark" under %(owner)s.
  2  an argument the gate does not take.
"""


def _parser():
    """The gate's command line: no arguments; `--help` says what it checks and what its exit codes mean, and asks gh nothing."""
    return argparse.ArgumentParser(
        prog="check_backlog.py", formatter_class=argparse.RawDescriptionHelpFormatter,
        description=CHECKS % {"limits": ", ".join("%s %d" % limit for limit in LIMITS.items()),
                              "lanes": "; ".join("%s: %s" % (lane.name, ", ".join("%s %d" % limit for limit in lane.limits))
                                                 for lane in LANES),
                              "flights": ", ".join("%s %d" % (lane.name, lane.flight) for lane in LANES),
                              "waits": ", ".join("%s %d" % (lane.name, lane.waiting) for lane in LANES),
                              "slices": "; ".join("%s is %s" % (lane.name, ", ".join(lane.slices))
                                                  for lane in LANES if lane.slices),
                              "known": ", ".join(KNOWN)},
        epilog=EXIT_CODES % {"owner": OWNER, "floor": COST_FLOOR})


def _gate():
    """
    (exit code, lines to print, whether the look was whole, what each answer cost) — the gate, unprinted. A look that
    was not whole is could-not-run, or spark's board judged without the bin's.
    """
    spent = []
    try:
        items, bin_items, bin_why = fetch(spent)
    except LookupError as gone:
        return 1, ["  backlog: %s" % gone], False, spent
    except PartialRead as short:
        return 0, ["  backlog: could-not-run — %s; the limits were not checked" % short], False, spent
    except board_read.Unreadable as unreachable:
        return 0, ["  backlog: could-not-run — gh or the network could not be reached (%s); the limits were not checked"
                   % unreachable], False, spent
    try:
        unstaged = no_stage(items, bin_items)
        said = problems(items, bin_items)
    except UnknownStage as unplaced:
        return 0, ["  backlog: could-not-run — %s; the limits were not checked" % unplaced], False, spent
    summary = "  backlog: %d open, %s" % (sum(1 for e in items if e.get("status") != "Done"),
                                         "the limits hold" if not said else "%d problem(s)" % len(said))
    if bin_items is not None:
        summary += "; the bin: %d open" % sum(1 for e in bin_items if e.get("status") != "Done")
    lines = [summary, *("    " + sentence for sentence in said)]
    if unstaged:
        lines.append("  backlog: " + unstaged)
    if bin_items is None:
        lines.append("  backlog: " + BIN_UNREAD % bin_why)
    return (1 if said else 0), lines, bin_items is not None, spent


def main(argv=()):
    """
    The gate, printed; its exit code. `argv` is the command line's arguments — none by default, so check_commit.py, which
    imports this and calls main() with a commit in its own sys.argv, is never read as asking the gate anything. The cost
    line comes last, when the read cost more than COST_FLOOR or the look was not whole (P811).
    """
    _parser().parse_args(list(argv))
    code, lines, whole, spent = _gate()
    if spent and (not whole or sum(each["cost"] for each in spent) > COST_FLOOR):
        lines.append(cost_line(spent))
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
