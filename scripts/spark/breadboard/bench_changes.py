"""
What a rebuild asks a person to change on the bench (P300, #366). The last sheet for another design told the person to
wire some steps. This library keeps what that sheet said, with its time, as the base of `wiring-record.json` (P875),
compares it with the new steps, and says each difference as one bench action. It names jumpers by their ends and colors, never by holes: the person picks their own
free rows. `sheet` calls it; nothing here knows a circuit.

    describe(seated, colors)                       [RecordedStep], one per step of a sheet
    WiringLog.from_build(seated, colors, earlier, drawn, at)   the log of a sheet; kept connections keep their color
    WiringLog.read(path)                           the log on disk, None when there is none
    WiringLogStore(folder).stage(log) / .commit(staged)   the log put in place whole, after the sheet is written
    changes_between(record, seated, colors)        [WiringChange], in the order a person acts
    ChangeList().line(change) / .render(changes)   the words

A step is the same step when its subject has the same key: a part placed, a supply, or an end (a resistor end by its
job and end number, never its tag, which renumbers). It has moved when its anchor key differs, and a resistor has
been swapped when its value differs. A line names a resistor end by its job too, since its tag renumbers.
"""

import collections
import datetime
import json
import re
from pathlib import Path

from spark.breadboard import wiring_steps
from spark.build.build_record import STAGE_SUFFIX, StagedFile
from spark.core import zone_time
from spark.core.clock import SystemClock

#: The codes of WiringChange. A code decides; ChangeList writes the words.
ADDED, REMOVED, REROUTED, SWAPPED = "added", "removed", "rerouted", "swapped"
CODES = (ADDED, REMOVED, REROUTED, SWAPPED)
#: What a person does for a step: put a part in, put a resistor leg in, run a jumper, connect a supply. A swap and a
#: removed resistor say the resistor. A rail leg is a resistor leg bound for a rail: it goes in a free row, and a jumper
#: joins that row to the rail (P960).
PLACE, LEG, JUMPER, SUPPLY, RESISTOR = wiring_steps.PLACE, "leg", "jumper", wiring_steps.SUPPLY, "resistor"
RAIL_LEG = "rail leg"
#: Where a setup step puts an end: nothing holds it yet.
FREE_ROW = "a free row"

#: One step of a sheet as the record keeps it: its key and its anchor's key (tuples of strings), what a person does
#: (a kind above), the words for its subject and where it goes (a rail is "the GND rail", never the mark), a
#: resistor's tag, value and job, the color of its jumper on the bench (None when no drawing showed one), and the mark
#: ("GND") when it is the first end to reach a rail, else "", with that rail's sign ("+", "-", P953), "" for an
#: unsigned rail and in a record from before signs.
RecordedStep = collections.namedtuple("RecordedStep", "key anchor kind source to tag value job color marks sign",
                                      defaults=("",))
#: One difference: a code, what a person does (a kind), the subject's words, the jumper's color (None when the earlier
#: or new sheet showed none), the destination before and after, and the rail mark the first end to reach a rail puts on
#: it (else "") with its sign ("+", "-" or ""). A swapped resistor has its tag as `name` and its values as `before` and
#: `after`; a removed one has its tag, value (`before`) and job (`after`).
WiringChange = collections.namedtuple("WiringChange", "code kind name color before after marks sign", defaults=("",))


def _end_key(end):
    if end.kind == wiring_steps.RESISTOR:
        return (end.kind, end.job or end.component, end.pin)
    # a board end by its name, never its words: a joined pad's note (P1009) must not move a jumper that stayed
    return (end.kind, end.name if end.kind == wiring_steps.BOARD else end.words)


def _anchor_key(anchor):
    seat = anchor.seat()
    return (seat.kind,) + _end_key(seat.end) if seat.kind == wiring_steps.ROW else (seat.kind, seat.mark)


def _name(end):
    """An end as a change line names it: a resistor end also by its job, since its tag renumbers."""
    if end.kind == wiring_steps.RESISTOR and end.job:
        return "%s (%s)" % (end.name, end.job)
    return end.name


def _destination(anchor):
    """Where the ends of an anchor meet, in words that survive a renumbering: a rail is named by its mark."""
    seat = anchor.seat()
    if seat.kind == wiring_steps.RAIL:
        return "the %s rail" % seat.mark
    if seat.end.kind == wiring_steps.BOARD:
        return "the row of the jumper from %s" % seat.end.name
    return "the row of " + _name(seat.end)


def describe(seated, colors=None):
    """[RecordedStep], one per Seated step in order. `colors` is {step number: the color of its jumper in the drawing}
    (none when there is no drawing)."""
    colors = colors or {}
    reached, found = set(), []
    for number, one in enumerate(seated, 1):
        if one.act == wiring_steps.PLACE:
            name = "the board" if one.subject == wiring_steps.THE_BOARD else one.subject
            found.append(RecordedStep((PLACE, one.subject), None, PLACE, name, "", "", "", "", None, ""))
            continue
        anchor = _anchor_key(one.anchor)
        if one.act == wiring_steps.SUPPLY:
            found.append(RecordedStep((SUPPLY, one.subject), anchor, SUPPLY, "the %s supply" % one.subject,
                                      _destination(one.anchor), "", "", "", None, ""))
            continue
        end = one.subject
        seat = one.anchor.seat()
        marks = seat.mark if seat.kind == wiring_steps.RAIL and anchor not in reached else ""
        reached.add(anchor)
        to = FREE_ROW if one.act == wiring_steps.SETUP else _destination(one.anchor)
        resistor = end.kind == wiring_steps.RESISTOR
        source = _name(end) if end.kind == wiring_steps.BOARD or not one.jumper or resistor else "the row of " + _name(end)
        kind = (RAIL_LEG if resistor else JUMPER) if one.jumper else LEG
        found.append(RecordedStep(_end_key(end), anchor, kind, source, to,
                                  end.component if resistor else "", end.value if resistor else "",
                                  end.job if resistor else "", colors.get(number) if one.jumper else None, marks,
                                  seat.sign if marks else ""))
    return found


#: The steps of the last sheet whose wiring differed from the one after it, and the time spark wrote that sheet (None when
#: an old record did not say): what a list of changes counts from.
SheetBase = collections.namedtuple("SheetBase", "steps at")


def _step(one):
    """One RecordedStep from its dict in the file. KeyError, TypeError or ValueError when it is none."""
    step = RecordedStep(tuple(one["key"]), tuple(one["anchor"]) if one["anchor"] else None, one["kind"], one["source"],
                        one["to"], one["tag"], one["value"], one["job"], one["color"], one["marks"], one.get("sign", ""))
    if not all(isinstance(part, str) for part in step.key + (step.anchor or ())):
        raise ValueError("a key that is not a list of strings")
    return step


def _said(at):
    """A time as `zone_time.stamp` writes it, as a heading says it: local, to the minute. ValueError, OverflowError or
    TypeError for a time that is none, or that the local zone cannot say."""
    return datetime.datetime.fromisoformat(at).astimezone().strftime("%Y-%m-%d %H:%M")


def _time(value):
    """`value` when it is a time that `_said` can say, or None; an error of `_said` for anything else."""
    if value is not None:
        _said(value)
    return value


class WiringLog:
    """
    Value: what the last sheet told the person to wire, `steps` as [RecordedStep], and `drawn_jumpers`, the pairs of
    holes (frozensets of two hole names) that spark drew itself in breadboard.json, not a jumper the person kept. `at` is
    the time of that sheet and `base` the SheetBase the list on it counts from, None for a first wiring built again
    (P875). `why_unread` says why the file cannot be used, else None.
    """

    FILE_NAME = "wiring-record.json"

    def __init__(self, steps, drawn_jumpers=(), why_unread=None, at=None, base=None):
        self.steps = list(steps)
        self.drawn_jumpers = {frozenset(pair) for pair in drawn_jumpers}
        self.why_unread, self.at, self.base = why_unread, at, base

    @classmethod
    def from_build(cls, seated, colors, earlier, drawn, at=None):
        """The record of a sheet built from `seated` at the time `at`. A connection the earlier record also had keeps the
        color the person wired, so a later line names a color the bench shows. The base is the earlier sheet when its
        wiring differs from this one, else the earlier sheet's own base: the list stays until another design is built."""
        usable = earlier if earlier and not earlier.why_unread else None
        before = {one.key: one for one in usable.steps} if usable else {}
        steps = []
        for one in describe(seated, colors):
            old = before.get(one.key)
            steps.append(one._replace(color=old.color) if old and old.color else one)
        base = usable.base if usable else None
        if usable and changes_between(usable, seated, colors):
            base = SheetBase(usable.steps, usable.at)
        return cls(steps, drawn, None, at, base)

    @classmethod
    def read(cls, path):
        """The record in the file, None when there is no file. A file that is not a record gives one with `why_unread`.
        A file with no `at` and no `base` is one from before them."""
        path = Path(path)
        if not path.is_file():
            return None
        try:
            data = json.loads(path.read_text())
            held = data.get("base")
            base = SheetBase([_step(one) for one in held["steps"]], _time(held["at"])) if held is not None else None
            return cls([_step(one) for one in data["steps"]], [pair for pair in data["drawn_jumpers"]], None,
                       _time(data.get("at")), base)
        except (OSError, UnicodeDecodeError, ValueError, OverflowError, KeyError, TypeError, AttributeError) as broken:
            return cls([], (), "cannot be read (%s: %s)" % (type(broken).__name__, broken))

    def to_dict(self):
        return {"steps": _step_dicts(self.steps), "drawn_jumpers": sorted(sorted(pair) for pair in self.drawn_jumpers),
                "at": self.at, "base": {"steps": _step_dicts(self.base.steps), "at": self.base.at} if self.base else None}


def _step_dicts(steps):
    return [dict(one._asdict(), key=list(one.key), anchor=list(one.anchor) if one.anchor else None) for one in steps]


class WiringLogStore:
    """
    Store: the wiring record beside the sheet, `<folder>/wiring-record.json`, put in place in two steps (P875): `stage` makes
    `wiring-record.json.new` exclusively, `commit` replaces the record with it in one step. The record has two states, the
    old and the new one. `now` is the time of a sheet, from `clock` (SystemClock).
    """

    def __init__(self, folder, clock=None):
        self.path = Path(folder) / WiringLog.FILE_NAME
        self.clock = clock or SystemClock()

    def now(self):
        return zone_time.stamp(self.clock.now())

    def stage(self, log):
        """The StagedFile that holds `log`, made. OSError when the stage's name is taken (StageTakenError) or the write fails."""
        staged = StagedFile.from_bytes(self.path.with_name(self.path.name + STAGE_SUFFIX), (json.dumps(log.to_dict(), indent=1) + "\n").encode())
        try:
            staged.make()
        except OSError:
            staged.remove()
            raise
        return staged

    def commit(self, staged):
        """Replace the record with the stage. OSError leaves both as they were."""
        staged.commit(self.path)


def changes_between(record, seated, colors=None):
    """
    [WiringChange] from the earlier `record` (a WiringLog or a SheetBase: anything with `steps`) to the steps now, in the
    order a person acts: what to take out (a whole resistor is one line), what to swap,
    then what to put in and which connections to move, a line that marks a rail
    before the lines that use it, each in step order. A jumper in the record shows its bench color; one added shows
    its color in the new drawing, unless a jumper to take out or move had that color on the bench.
    """
    now = describe(seated, colors)
    before = {one.key: one for one in record.steps}
    kept = {one.key for one in now}
    removed, taken_out = [], set()
    for one in record.steps:
        if one.key in kept:
            continue
        if one.kind in (LEG, RAIL_LEG) and one.tag and one.key[:2] not in taken_out:
            taken_out.add(one.key[:2])
            removed.append(WiringChange(REMOVED, RESISTOR, one.tag, None, one.value, one.job, ""))
        if one.kind == RAIL_LEG:  # the leg goes with its resistor, and its jumper to the rail comes out too
            removed.append(WiringChange(REMOVED, JUMPER, "the row of " + one.source, one.color, one.to, "", ""))
        elif one.kind != LEG or not one.tag:
            removed.append(WiringChange(REMOVED, one.kind, one.source, one.color, one.to, "", ""))
    swapped, added, rerouted, jobs = [], [], [], set()
    for one in now:
        old = before.get(one.key)
        if old is None:
            added.append(WiringChange(ADDED, one.kind, one.source, one.color, "", one.to, one.marks, one.sign))
            continue
        if old.value != one.value and one.key[:2] not in jobs:
            jobs.add(one.key[:2])
            swapped.append(WiringChange(SWAPPED, RESISTOR, one.tag, None, old.value, one.value, ""))
        if old.anchor != one.anchor:
            for change in _moved(old, one):
                {REMOVED: removed, ADDED: added}.get(change.code, rerouted).append(change)
    bench = {change.color for change in removed + rerouted if change.color and change.kind != RAIL_LEG}  # a moved rail leg's jumper is new
    added = [change._replace(color=None) if change.color in bench else change for change in added]
    rerouted = [change._replace(color=None) if change.kind == RAIL_LEG and change.color in bench else change
                for change in rerouted]
    further = sorted(added + rerouted, key=lambda change: not change.marks)
    return removed + swapped + further


def _moved(old, new):
    """[WiringChange] of one step whose anchor moved (P960). A leg that sat in a free row before P953 stays there, and
    only the jumper from its row to the rail is new; a leg in another row moves to a free row, with that jumper. A rail
    leg bound for another rail keeps its row, and its jumper moves; one bound for a row first loses its jumper, so no
    row is left tied to the old rail."""
    jumper = "the row of " + new.source
    if new.kind == RAIL_LEG and old.kind == LEG and old.to == FREE_ROW:
        return [WiringChange(ADDED, JUMPER, jumper, new.color, "", new.to, new.marks, new.sign)]
    if old.kind == RAIL_LEG and new.kind == RAIL_LEG:
        return [WiringChange(REROUTED, JUMPER, jumper, old.color, old.to, new.to, new.marks, new.sign)]
    if old.kind == RAIL_LEG:
        return [WiringChange(REMOVED, JUMPER, jumper, old.color, old.to, "", ""),
                WiringChange(REROUTED, new.kind, new.source, None, FREE_ROW, new.to, new.marks, new.sign)]
    color = new.color if new.kind == RAIL_LEG else old.color  # a rail leg's jumper is new; another keeps its bench color
    return [WiringChange(REROUTED, new.kind, new.source, color, old.to, new.to, new.marks, new.sign)]


def _article(word):
    """"a" or "an" for a color or a value, as it is said: an orange jumper, an 820Ω resistor, a 330Ω one."""
    digits = re.match(r"\d+", word)
    if digits:
        return "an" if digits.group().startswith("8") or digits.group() in ("11", "18") else "a"
    return "an" if word[:1].lower() in "aeiou" else "a"


class ChangeList:
    """Renderer: one bench action per change, the words a person reads."""

    def heading(self, since):
        """The heading of the list: it names the time of the sheet it counts from, else says none is known."""
        if since is None:
            return "Changes since an earlier sheet spark wrote (spark did not note when)"
        return "Changes since the sheet spark wrote on " + _said(since)

    def note(self, since):
        """The line under the heading: spark cannot know that the person wired that sheet."""
        which = "that earlier sheet" if since is None else "the sheet from " + _said(since)
        return "Use this list only if you wired %s. If you did not, follow the steps below: they are the whole wiring." % which

    def line(self, change):
        jumper = "%s jumper" % change.color if change.color else "jumper"
        rail = "a free %s rail" % change.sign if change.sign else "a free rail"
        after = "%s, which you mark %s" % (rail, change.marks) if change.marks else change.after
        if change.code == SWAPPED:
            return "Swap %s, %s, for %s %s resistor in the same rows." % (
                change.name, change.before, _article(change.after), change.after)
        if change.code == REMOVED:
            if change.kind == RESISTOR:
                return "Take out %s." % ", ".join([change.name, " ".join(filter(None, (change.before, change.after)))])
            if change.kind == JUMPER:
                return "Take out the %s from %s to %s." % (jumper, change.name, change.before)
            return ("Disconnect %s." if change.kind == SUPPLY else "Take out %s.") % change.name
        if change.code == REROUTED:
            if change.kind == SUPPLY:
                return "Connect %s to %s instead of %s." % (change.name, after, change.before)
            if change.kind == JUMPER:
                return "Move the %s from %s: it now goes to %s (it went to %s)." % (
                    jumper, change.name, after, change.before)
            if change.kind == RAIL_LEG:
                return "Move %s: %s (it went to %s)." % (change.name, self._rail_leg(jumper, after), change.before)
            return "Move %s: it now goes to %s (it went to %s)." % (change.name, after, change.before)
        if change.kind == PLACE:
            return "Put %s in the breadboard." % change.name
        if change.kind == LEG:
            return "Put %s in %s." % (change.name, after)
        if change.kind == RAIL_LEG:
            return "Put %s %s." % (change.name, self._rail_leg(jumper, after)[len("put it "):])
        if change.kind == SUPPLY:
            return "Connect %s to %s." % (change.name, after)
        return "Run %s %s from %s to %s." % (_article(jumper), jumper, change.name, after)

    @staticmethod
    def _rail_leg(jumper, rail):
        """The words that bring a rail leg in (P960): a free row close to the row of its other end, and a jumper to the rail."""
        return "put it in a free row close to the row of its other end, and run %s %s from that row to %s" % (
            _article(jumper), jumper, rail)

    def render(self, changes):
        return [self.line(change) for change in changes]
