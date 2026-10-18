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
changed when its value differs.
"""

import collections
import json
from pathlib import Path

import breadboard_steps

#: The codes of WiringChange. A code decides; ChangeList writes the words.
ADDED, REMOVED, REROUTED, CHANGED = "added", "removed", "rerouted", "changed"
CODES = (ADDED, REMOVED, REROUTED, CHANGED)
#: What a person does for a step: put a part in, put a resistor leg in, run a jumper, connect a supply. A change of
#: value says the resistor.
PLACE, LEG, JUMPER, SUPPLY, VALUE = breadboard_steps.PLACE, "leg", "jumper", breadboard_steps.SUPPLY, "value"
#: Where a setup step puts an end: nothing holds it yet.
FREE_ROW = "a free row"

#: One step of a sheet as the record keeps it: its key and its anchor's key (tuples of strings), what a person does
#: (a kind above), the words for its subject and where it goes, a resistor's tag and value, the color of its jumper
#: on the bench (None when no drawing showed one), and whether it marks a rail the later steps use.
RecordedStep = collections.namedtuple("RecordedStep", "key anchor kind source to tag value color marks")
#: One difference: a code, what a person does (a kind), the subject's words, the jumper's color (None when the earlier
#: or new sheet showed none), and the destination before and after. A `changed` resistor has its tag as `name` and its
#: values as `before` and `after`.
WiringChange = collections.namedtuple("WiringChange", "code kind name color before after")


def _end_key(end):
    if end.kind == breadboard_steps.RESISTOR:
        return (end.kind, end.job or end.component, end.pin)
    return (end.kind, end.words)


def _anchor_key(anchor):
    seat = anchor.seat()
    return (seat.kind,) + _end_key(seat.end) if seat.kind == breadboard_steps.ROW else (seat.kind, seat.mark)


def describe(seated, colors=None):
    """[RecordedStep], one per Seated step in order. `colors` is {step number: the color of its jumper in the drawing}
    (none when there is no drawing)."""
    colors = colors or {}
    reached, found = set(), []
    for number, one in enumerate(seated, 1):
        if one.act == breadboard_steps.PLACE:
            name = "the board" if one.subject == breadboard_steps.THE_BOARD else one.subject
            found.append(RecordedStep((PLACE, one.subject), None, PLACE, name, "", "", "", None, False))
            continue
        anchor = _anchor_key(one.anchor)
        if one.act == breadboard_steps.SUPPLY:
            found.append(RecordedStep((SUPPLY, one.subject), anchor, SUPPLY, "the %s supply" % one.subject,
                                      one.anchor.destination(False), "", "", None, False))
            continue
        end = one.subject
        marks = one.anchor.seat().kind == breadboard_steps.RAIL and anchor not in reached
        reached.add(anchor)
        to = FREE_ROW if one.act == breadboard_steps.SETUP else one.anchor.destination(marks)
        resistor = end.kind == breadboard_steps.RESISTOR
        source = end.name if end.kind == breadboard_steps.BOARD or not one.jumper else "the row of " + end.name
        found.append(RecordedStep(_end_key(end), anchor, JUMPER if one.jumper else LEG, source, to,
                                  end.component if resistor else "", end.value if resistor else "",
                                  colors.get(number) if one.jumper else None, marks))
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
                                  one["source"], one["to"], one["tag"], one["value"], one["color"], one["marks"])
                     for one in data["steps"]]
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


def changes_between(record, seated, colors=None):
    """
    [WiringChange] from the earlier `record` to the steps now, in the order a person acts: what to take out, what to
    swap, then what to put in and which jumpers to move, a line that marks a rail before the lines that use it, each
    in step order. A jumper in the record shows its bench color; one added shows its color in the new drawing.
    """
    now = describe(seated, colors)
    before = {one.key: one for one in record.steps}
    kept = {one.key for one in now}
    removed = [WiringChange(REMOVED, one.kind, one.source, one.color, one.to, "")
               for one in record.steps if one.key not in kept]
    swapped, added, rerouted, jobs = [], [], [], set()
    for one in now:
        old = before.get(one.key)
        if old is None:
            added.append((one.marks, WiringChange(ADDED, one.kind, one.source, one.color, "", one.to)))
            continue
        if old.value != one.value and one.key[:2] not in jobs:
            jobs.add(one.key[:2])
            swapped.append(WiringChange(CHANGED, VALUE, one.tag, None, old.value, one.value))
        if old.anchor != one.anchor:
            rerouted.append((one.marks, WiringChange(REROUTED, one.kind, one.source, old.color, old.to, one.to)))
    further = sorted(added + rerouted, key=lambda pair: not pair[0])
    return removed + swapped + [change for _, change in further]


class ChangeList:
    """Renderer: one bench action per change, the words a person reads."""

    def line(self, change):
        jumper = "%s jumper" % change.color if change.color else "jumper"
        if change.code == CHANGED:
            return "Swap %s, %s, for a %s resistor in the same rows." % (change.name, change.before, change.after)
        if change.code == REMOVED:
            return ("Take out the %s from %s to %s." % (jumper, change.name, change.before)
                    if change.kind == JUMPER else "Disconnect %s." % change.name if change.kind == SUPPLY
                    else "Take out %s." % change.name)
        if change.code == REROUTED:
            return "Move the %s from %s: it now goes to %s (it went to %s)." % (
                jumper, change.name, change.after, change.before)
        return {PLACE: "Put %s in the breadboard." % change.name,
                LEG: "Put %s in %s." % (change.name, change.after),
                JUMPER: "Run a %s from %s to %s." % (jumper, change.name, change.after),
                SUPPLY: "Connect %s to %s." % (change.name, change.after)}[change.kind]

    def render(self, changes):
        return [self.line(change) for change in changes]
