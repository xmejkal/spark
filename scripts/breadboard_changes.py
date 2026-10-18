"""
What a rebuild asks a person to change on the bench (P300, #366). The earlier sheet told the person to wire some steps.
This library keeps what that sheet said in `wiring-record.json`, compares it with the new steps, and says each
difference as one bench action. It names jumpers by their ends and colors, never by holes: the person picks their own
free rows. `breadboard.py` calls it; nothing here knows a circuit.

    describe(seated, colors)                       [RecordedStep], one per step of a sheet
    WiringRecord.from_build(seated, colors, earlier, drawn)   the record of a sheet; kept connections keep their color
    WiringRecord.read(path)                        the record on disk, None when there is none
    changes_between(record, seated, colors)        [WiringChange], in the order a person acts
    ChangeList().line(change) / .render(changes)   the words

A step is the same step when its subject has the same key: a part placed, a supply, or an end (a resistor end by its
job and end number, never its tag, which renumbers). It has moved when its anchor key differs, and a resistor has
been swapped when its value differs. A line names a resistor end by its job too, since its tag renumbers.
"""

import collections
import json
import os
import re
from pathlib import Path

import breadboard_steps

#: The codes of WiringChange. A code decides; ChangeList writes the words.
ADDED, REMOVED, REROUTED, SWAPPED = "added", "removed", "rerouted", "swapped"
CODES = (ADDED, REMOVED, REROUTED, SWAPPED)
#: What a person does for a step: put a part in, put a resistor leg in, run a jumper, connect a supply. A swap and a
#: removed resistor say the resistor.
PLACE, LEG, JUMPER, SUPPLY, RESISTOR = breadboard_steps.PLACE, "leg", "jumper", breadboard_steps.SUPPLY, "resistor"
#: Where a setup step puts an end: nothing holds it yet.
FREE_ROW = "a free row"

#: One step of a sheet as the record keeps it: its key and its anchor's key (tuples of strings), what a person does
#: (a kind above), the words for its subject and where it goes (a rail is "the GND rail", never the mark), a
#: resistor's tag, value and job, the color of its jumper on the bench (None when no drawing showed one), and the mark
#: ("GND") when it is the first end to reach a rail, else "".
RecordedStep = collections.namedtuple("RecordedStep", "key anchor kind source to tag value job color marks")
#: One difference: a code, what a person does (a kind), the subject's words, the jumper's color (None when the earlier
#: or new sheet showed none), the destination before and after, and the rail mark the first end to reach a rail puts on
#: it (else ""). A swapped resistor has its tag as `name` and its values as `before` and `after`; a removed one has its
#: tag, value (`before`) and job (`after`).
WiringChange = collections.namedtuple("WiringChange", "code kind name color before after marks")


def _end_key(end):
    if end.kind == breadboard_steps.RESISTOR:
        return (end.kind, end.job or end.component, end.pin)
    return (end.kind, end.words)


def _anchor_key(anchor):
    seat = anchor.seat()
    return (seat.kind,) + _end_key(seat.end) if seat.kind == breadboard_steps.ROW else (seat.kind, seat.mark)


def _name(end):
    """An end as a change line names it: a resistor end also by its job, since its tag renumbers."""
    if end.kind == breadboard_steps.RESISTOR and end.job:
        return "%s (%s)" % (end.name, end.job)
    return end.name


def _destination(anchor):
    """Where the ends of an anchor meet, in words that survive a renumbering: a rail is named by its mark."""
    seat = anchor.seat()
    if seat.kind == breadboard_steps.RAIL:
        return "the %s rail" % seat.mark
    if seat.end.kind == breadboard_steps.BOARD:
        return "the row of the jumper from %s" % seat.end.name
    return "the row of " + _name(seat.end)


def describe(seated, colors=None):
    """[RecordedStep], one per Seated step in order. `colors` is {step number: the color of its jumper in the drawing}
    (none when there is no drawing)."""
    colors = colors or {}
    reached, found = set(), []
    for number, one in enumerate(seated, 1):
        if one.act == breadboard_steps.PLACE:
            name = "the board" if one.subject == breadboard_steps.THE_BOARD else one.subject
            found.append(RecordedStep((PLACE, one.subject), None, PLACE, name, "", "", "", "", None, ""))
            continue
        anchor = _anchor_key(one.anchor)
        if one.act == breadboard_steps.SUPPLY:
            found.append(RecordedStep((SUPPLY, one.subject), anchor, SUPPLY, "the %s supply" % one.subject,
                                      _destination(one.anchor), "", "", "", None, ""))
            continue
        end = one.subject
        seat = one.anchor.seat()
        marks = seat.mark if seat.kind == breadboard_steps.RAIL and anchor not in reached else ""
        reached.add(anchor)
        to = FREE_ROW if one.act == breadboard_steps.SETUP else _destination(one.anchor)
        resistor = end.kind == breadboard_steps.RESISTOR
        source = _name(end) if end.kind == breadboard_steps.BOARD or not one.jumper else "the row of " + _name(end)
        found.append(RecordedStep(_end_key(end), anchor, JUMPER if one.jumper else LEG, source, to,
                                  end.component if resistor else "", end.value if resistor else "",
                                  end.job if resistor else "", colors.get(number) if one.jumper else None, marks))
    return found


class WiringRecord:
    """
    Value: what the last sheet told the person to wire, `steps` as [RecordedStep], and `drawn_jumpers`, the pairs of
    holes (frozensets of two hole names) that spark drew itself in breadboard.json, not a jumper the person kept.
    `why_unread` says why the file cannot be used, else None.
    """

    FILE_NAME = "wiring-record.json"

    def __init__(self, steps, drawn_jumpers=(), why_unread=None):
        self.steps = list(steps)
        self.drawn_jumpers = {frozenset(pair) for pair in drawn_jumpers}
        self.why_unread = why_unread

    @classmethod
    def from_build(cls, seated, colors, earlier, drawn):
        """The record of a sheet built from `seated`. A connection the earlier record also had keeps the color the
        person wired, so a later line names a color the bench shows."""
        before = {one.key: one for one in earlier.steps} if earlier and not earlier.why_unread else {}
        steps = []
        for one in describe(seated, colors):
            old = before.get(one.key)
            steps.append(one._replace(color=old.color) if old and old.color else one)
        return cls(steps, drawn)

    @classmethod
    def read(cls, path):
        """The record in the file, None when there is no file. A file that is not a record gives one with `why_unread`."""
        path = Path(path)
        if not path.is_file():
            return None
        try:
            data = json.loads(path.read_text())
            steps = [RecordedStep(tuple(one["key"]), tuple(one["anchor"]) if one["anchor"] else None, one["kind"],
                                  one["source"], one["to"], one["tag"], one["value"], one["job"], one["color"],
                                  one["marks"]) for one in data["steps"]]
            for one in steps:
                if not all(isinstance(part, str) for part in one.key + (one.anchor or ())):
                    raise ValueError("a key that is not a list of strings")
            return cls(steps, [pair for pair in data["drawn_jumpers"]])
        except (OSError, UnicodeDecodeError, ValueError, KeyError, TypeError) as broken:
            return cls([], (), "cannot be read (%s: %s)" % (type(broken).__name__, broken))

    def to_dict(self):
        return {"steps": [dict(one._asdict(), key=list(one.key), anchor=list(one.anchor) if one.anchor else None)
                          for one in self.steps],
                "drawn_jumpers": sorted(sorted(pair) for pair in self.drawn_jumpers)}

    def write(self, path):
        """Write the file whole or not at all: a temporary file beside it, then a replace."""
        path = Path(path)
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_text(json.dumps(self.to_dict(), indent=1) + "\n")
        os.replace(temporary, path)


def changes_between(record, seated, colors=None):
    """
    [WiringChange] from the earlier `record` to the steps now, in the order a person acts: what to take out (a whole
    resistor is one line), what to swap, then what to put in and which connections to move, a line that marks a rail
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
        if one.kind == LEG and one.tag:
            if one.key[:2] not in taken_out:
                taken_out.add(one.key[:2])
                removed.append(WiringChange(REMOVED, RESISTOR, one.tag, None, one.value, one.job, ""))
        else:
            removed.append(WiringChange(REMOVED, one.kind, one.source, one.color, one.to, "", ""))
    swapped, added, rerouted, jobs = [], [], [], set()
    for one in now:
        old = before.get(one.key)
        if old is None:
            added.append(WiringChange(ADDED, one.kind, one.source, one.color, "", one.to, one.marks))
            continue
        if old.value != one.value and one.key[:2] not in jobs:
            jobs.add(one.key[:2])
            swapped.append(WiringChange(SWAPPED, RESISTOR, one.tag, None, old.value, one.value, ""))
        if old.anchor != one.anchor:
            rerouted.append(WiringChange(REROUTED, one.kind, one.source, old.color, old.to, one.to, one.marks))
    bench = {change.color for change in removed + rerouted if change.color}
    added = [change._replace(color=None) if change.color in bench else change for change in added]
    further = sorted(added + rerouted, key=lambda change: not change.marks)
    return removed + swapped + further


def _article(word):
    """"a" or "an" for a color or a value, as it is said: an orange jumper, an 820Ω resistor, a 330Ω one."""
    digits = re.match(r"\d+", word)
    if digits:
        return "an" if digits.group().startswith("8") or digits.group() in ("11", "18") else "a"
    return "an" if word[:1].lower() in "aeiou" else "a"


class ChangeList:
    """Renderer: one bench action per change, the words a person reads."""

    def line(self, change):
        jumper = "%s jumper" % change.color if change.color else "jumper"
        after = "a free rail, which you mark %s" % change.marks if change.marks else change.after
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
            return "Move %s: it now goes to %s (it went to %s)." % (change.name, after, change.before)
        if change.kind == PLACE:
            return "Put %s in the breadboard." % change.name
        if change.kind == LEG:
            return "Put %s in %s." % (change.name, after)
        if change.kind == SUPPLY:
            return "Connect %s to %s." % (change.name, after)
        return "Run %s %s from %s to %s." % (_article(jumper), jumper, change.name, after)

    def render(self, changes):
        return [self.line(change) for change in changes]
