"""
The drawn breadboard (P267, #300): the sheet's steps on a breadboard, each part's legs in holes and each
step's jumper in the color of what it carries, written as `breadboard.json`, a second Wokwi diagram, and as `breadboard.svg`.

A pure planner turns the steps into holes, and a renderer turns the holes into a diagram. The planner reads the steps
from `BreadboardSteps.anchored()`, so it never decides the wiring again. Where Wokwi draws each pin and hole comes from
`data/wokwi-geometry.json`, measured once in Wokwi. A leg over a hole connects in Wokwi with no connection entry, so
only the jumpers are connections.

    BreadboardPlanner(geometry, catalog).plan(steps)  ->  BreadboardLayout  ->  WokwiBreadboardDiagram().render(layout)
"""

import collections
import copy
import json
from pathlib import Path

from spark.breadboard import wiring_steps
from spark.breadboard.spacing import BodyBox, BodySpacing, ends_toward_their_runs, rotate, tall_module_row
from spark.core import codes

WOKWI_GEOMETRY_FILE = Path(__file__).resolve().parents[3] / "data" / "wokwi-geometry.json"
BREADBOARDS_FILE = Path(__file__).resolve().parents[3] / "data" / "breadboards.json"

#: Value: one hole, its Wokwi name (12t.a, tp.3), its center in px, its group (the holes joined with it inside the
#: board: a breadboard row such as 12t, or a rail such as tp), and its column (from 1; a rail hole has none, 0).
Hole = collections.namedtuple("Hole", "name x y group column")
#: What the planner draws for one component: its Wokwi type and attrs, {its pin as the steps name it: Wokwi pin}, and
#: its record (the board's or the part's, None for a part with none), which its picture is looked up by (P946).
DrawnPart = collections.namedtuple("DrawnPart", "type attrs pins record", defaults=(None,))
#: One component on the breadboard: its id, type, attrs, top-left corner in px, its turn, {Wokwi pin: Hole} and its
#: record, as its DrawnPart has it.
PlacedPart = collections.namedtuple("PlacedPart", "id type attrs left top rotate holes record", defaults=(None,))
#: One jumper between two holes, for the step it belongs to, with the bends of its route as Wokwi writes them (strings
#: such as "v-20"), empty when it runs straight, and what it carries (`wiring_steps.role_of`), which picks its color.
Jumper = collections.namedtuple("Jumper", "one other step route role", defaults=((), wiring_steps.SIGNAL))
#: Value: the whole drawing as holes, the `geometry` it was planned on, which any renderer reads, and `crowded`, the id of
#: each part placed closer to the part before it than its surface's `body_gap_columns`, since the board had no room.
BreadboardLayout = collections.namedtuple("BreadboardLayout", "breadboard parts jumpers geometry crowded", defaults=((),))


#: Why a board or a part cannot be drawn, as codes (P412): the code a build and an agent decide on, never the sentence.
NO_HEADER_FACT, HEADER_DISAGREES = "no_header_fact", "header_disagrees"
NO_DOUBTFUL_PAD_FACT, GROUND_NOT_ONE = "no_doubtful_pad_fact", "ground_not_one"
DUPLICATE_PAD_LABEL, NO_HOLE_LEFT, NO_WOKWI_PART = "duplicate_pad_label", "no_hole_left", "no_wokwi_part"
NO_PIN_POSITION, NO_WOKWI_PIN = "no_pin_position", "no_wokwi_pin"
#: The one code here that is a Code (P945): its fix, filled with the part record's id, says how to get the facts.
NO_DRAWING_FACT = codes.Code("no_drawing_fact", "nothing says how to draw a part (no Wokwi part and no physical block in its "
                             "record) or the board; the subject is it", "research.py --part %s --project . asks for the physical facts that draw it")
ROW_FULL, NOT_DRAWN_YET, PLANNER_FAULT = "row_full", "not_drawn_yet", "planner_fault"
#: Each code with the one sentence that says what it means. Every refusal has one (P691).
CODES = {
    NO_HEADER_FACT: "the board's or the module's record lacks a field its pads or its outline need; the subject is the first field",
    HEADER_DISAGREES: ("the board's or the module's record disagrees with itself, a value of the wrong kind or a pad order "
                       "that does not fit the pin counts"),
    NO_DOUBTFUL_PAD_FACT: "the board's record does not say which pads are doubtful (physical.header.doubtful_pads), so no ground is picked",
    GROUND_NOT_ONE: ("no ground pad is left once the doubtful ones are out, or a ground pad is no pad of the header; "
                     "the subject names the ground pads left"),
    DUPLICATE_PAD_LABEL: "two pads of the board's record have one label; the subject is the label",
    NO_HOLE_LEFT: ("the breadboard has no place where a part fits with a free hole beside each of its pins, or no "
                   "free row for a jumper; the subject is the part or the end"),
    NO_WOKWI_PART: ("Wokwi has no part for a drawn part (the board or a module), so no Wokwi diagram is written, by design; "
                    "the why names each such part"),
    NO_PIN_POSITION: "data/wokwi-geometry.json lacks a Wokwi type's pins or one of them; the subject is the type",
    NO_DRAWING_FACT: NO_DRAWING_FACT.meaning,
    NO_WOKWI_PIN: "the end in the subject has no Wokwi pin: its part's record does not map it, or it is a doubtful pad",
    ROW_FULL: "a pin's row has no free hole for one more jumper, as too many steps join it; the subject is the row",
    NOT_DRAWN_YET: "the subject is not drawn yet: a rail, an off-board supply, or a resistor with both legs joined",
    PLANNER_FAULT: "a fault in spark's planner: a hole claimed twice or an unplaced part joined; the subject names it",
}


#: Value: a drawing a build did not write: where it would be, its renderer, why as a code from CODES with its subject
#: (None when it has none), the sentence a person reads, and the id of the part record that lacks the fact (None when
#: no record is known).
NotWritten = collections.namedtuple("NotWritten", "path renderer code subject why record", defaults=(None,))
#: The codes of a refusal a retry gives again: by design, or a drawing spark does not make yet. No failure the person can
#: fix; for NOT_DRAWN_YET, the sheet's steps say how to wire it by hand.
BY_DESIGN = (NO_WOKWI_PART, NOT_DRAWN_YET)


class NotDrawnError(Exception):
    """The steps cannot be drawn: a fact the drawing needs is missing, or the breadboard has no room. `code` (one of
    CODES, required) and `subject` say which, so a caller never reads the message. `record` is the id of the part record
    that lacks the fact, None when no record is known."""

    def __init__(self, message, code, subject=None, record=None):
        super().__init__(message)
        self.code = code
        self.subject = subject
        self.record = record


class Catalog(dict):
    """Value: what the planner draws each component as, {component: DrawnPart}, and `undrawn`, {component: the id of its
    part record} for each part that nothing says how to draw, so the refusal names the record to research."""

    def __init__(self, drawn=(), undrawn=None):
        super().__init__(drawn)
        self.undrawn = dict(undrawn or {})


class Surface:
    """
    Value: the holes of a board and which are joined inside it, from data/wokwi-geometry.json. A group is the holes
    joined inside the board: on a breadboard a row of five or a rail, on a perfboard later a single hole. (netlist.py
    says net only once something is wired.)
    """

    def __init__(self, board):
        self.type = board["type"]
        self.pitch = board["pitch"]
        self.holes = []
        for number in range(1, board["columns"] + 1):
            x = board["first_column_x"] + board["pitch"] * (number - 1)
            for letter, y in board["letters_y"].items():
                group = "%d%s" % (number, "t" if letter in board["top_letters"] else "b")
                self.holes.append(Hole("%s.%s" % (group, letter), x, y, group, number))
        for rail, y in board["rails_y"].items():
            for number in range(1, board["rail_holes"] + 1):
                x = board["first_rail_x"] + board["pitch"] * (number - 1 + (number - 1) // board["rail_block"])
                self.holes.append(Hole("%s.%d" % (rail, number), x, y, rail, 0))
        self.terminal = [hole for hole in self.holes if hole.column]
        self.rails = list(board["rails_y"])
        self.letters_y = dict(board["letters_y"])
        self.top_letters = board["top_letters"]
        #: The free columns the planner keeps between two part bodies on this board (P953); 0 keeps the old rule.
        self.body_gap_columns = board.get("body_gap_columns", 0)
        #: The terminal holes column by column, nearest the gap first and the side below the gap before the side above
        #: it at the same distance: ranked by letter, never by float distance, whose ties would move a part.
        top = board["top_letters"]
        bottom = [letter for letter in board["letters_y"] if letter not in top]
        rank = {letter: (index, 1) for index, letter in enumerate(reversed(top))}
        rank.update({letter: (index, 0) for index, letter in enumerate(bottom)})
        self.by_gap = sorted(self.terminal, key=lambda hole: (hole.column,) + rank[hole.name.rsplit(".", 1)[1]])

    @classmethod
    def load_full(cls, path=BREADBOARDS_FILE):
        """spark's own full-size surface, 63 columns and four rails (data/breadboards.json)."""
        return cls(json.loads(Path(path).read_text())["full"])

    def hole_at(self, x, y, tolerance):
        """The terminal hole whose center lies within the tolerance of (x, y), else None."""
        return next((hole for hole in self.terminal if abs(hole.x - x) <= tolerance and abs(hole.y - y) <= tolerance),
                    None)


class WokwiGeometry:
    """Value: where Wokwi draws each part's pins, and the surface of its breadboard
    (data/wokwi-geometry.json). A copy with another part or another surface (`with_part`, `with_surface`) leaves it as it was."""

    def __init__(self, data):
        self.data = data
        self.surface = Surface(data["breadboard"])
        self.tolerance = data["tolerance_px"]

    @classmethod
    def load(cls, path=WOKWI_GEOMETRY_FILE):
        return cls(json.loads(Path(path).read_text()))

    def with_part(self, wokwi_type, part_px):
        """A copy that also knows one part's px (a board drawn from its record); this geometry is not changed."""
        copied = copy.copy(self)
        copied.data = dict(self.data, parts=dict(self.data["parts"], **{wokwi_type: part_px}))
        return copied

    def with_surface(self, surface):
        """A copy whose holes are `surface`'s; this geometry is not changed."""
        copied = copy.copy(self)
        copied.surface = surface
        return copied

    def part(self, wokwi_type):
        """{center, covers_holes, pins} of one Wokwi type, or NotDrawnError naming it."""
        found = self.data["parts"].get(wokwi_type)
        if found is None:
            raise NotDrawnError("no Wokwi pin positions for %s in data/wokwi-geometry.json" % wokwi_type, NO_PIN_POSITION,
                           wokwi_type)
        return found

    def hole_at(self, x, y):
        """The terminal hole under a pin at (x, y), within the measured tolerance, else None."""
        return self.surface.hole_at(x, y, self.tolerance)


class HoleLedger:
    """The taken holes of one surface. A claim of a taken hole is refused and names it. (Its messages say row, the word
    a person reads on the sheet.)"""

    def __init__(self, surface, taken=None):
        self.surface = surface
        self.taken = dict(taken or {})

    def claim(self, hole, by):
        if hole.name in self.taken:
            raise NotDrawnError("hole %s is taken by %s, and %s needs it too" % (hole.name, self.taken[hole.name], by),
                           PLANNER_FAULT, hole.name)
        self.taken[hole.name] = by

    def is_free(self, hole):
        return hole.name not in self.taken

    def group_is_free(self, group):
        return all(self.is_free(hole) for hole in self.surface.holes if hole.group == group)

    def claim_free_hole(self, group, by):
        """Claim the first free hole of one group, or NotDrawnError: the group is full."""
        hole = next((hole for hole in self.surface.holes if hole.group == group and self.is_free(hole)), None)
        if hole is None:
            raise NotDrawnError("row %s has no free hole for %s" % (group, by), ROW_FULL, group)
        self.claim(hole, by)
        return hole

    def claim_free_group(self, after, by):
        """Claim a hole in the first group right of column `after` with nothing in it, or NotDrawnError: the board is
        full."""
        for hole in self.surface.terminal:
            if hole.column > after and self.group_is_free(hole.group):
                self.claim(hole, by)
                return hole
        raise NotDrawnError("the breadboard has no free row left for %s" % by, NO_HOLE_LEFT, by)


class PartPlacement:
    """Strategy: where one part goes, and how it is turned."""

    def reserve_first(self, ledger):
        """Called once, with the plan's ledger, before the first part is placed. A strategy that keeps parts where an
        earlier plan put them claims their holes here. The default claims nothing."""

    def place(self, part_id, drawn, ledger, after=0, pinned=None):
        raise NotImplementedError


class JumperPlacement:
    """Strategy: which holes the jumpers take, once the parts are placed and each jumper has its two rows."""

    def place_jumpers(self, layout, ledger):
        """The layout with its jumpers' holes chosen. `ledger` holds the holes the parts take and no jumper's. The
        default keeps the holes the planner took."""
        return layout


class FirstFitPartPlacement(PartPlacement):
    """
    The first turn and position, left to right, where every pin lies over a free hole, each pin in a group of its own
    that holds nothing else, and every hole the part covers is free. A part that covers holes also leaves each of its pins
    a free hole in its group, for a jumper (P412). A board that straddles the gap fits only when
    turned, because its pins in one line would share a group. `pinned` (pin, group) puts one pin in a group that already
    holds something: a resistor's leg in the group of the pin it joins. On a surface with `body_gap_columns` the whole
    body lies right of `after` too, and a tall module takes only the outermost row (`spacing.tall_module_row`, P953).
    """

    #: Flat first, so a resistor lies along a row of holes before it stands across the gap.
    TURNS_DEGREES = (0, 180, 90, 270)

    def __init__(self, geometry):
        self.geometry = geometry

    def place(self, part_id, drawn, ledger, after=0, pinned=None):
        part_px = self.geometry.part(drawn.type)
        wanted = [pin for pin in drawn.pins.values() if pin not in part_px["pins"]]
        if wanted:
            raise NotDrawnError("data/wokwi-geometry.json has no pin %s on %s" % (wanted[0], drawn.type), NO_PIN_POSITION,
                           drawn.type)
        surface = self.geometry.surface
        right_end = max(hole.x for hole in surface.terminal) + surface.pitch / 2  # a body may hang below, not past the end
        for degrees in self.TURNS_DEGREES:
            turned = rotate(part_px["pins"], part_px["center"], degrees)
            first = pinned[0] if pinned else next(iter(turned))
            row = None if pinned else tall_module_row(part_px, turned, degrees, surface)
            candidates = [hole for hole in surface.by_gap if (not pinned or hole.group == pinned[1])
                          and (row is None or hole.name.endswith("." + row))]
            for start in candidates:
                left, top = start.x - turned[first][0], start.y - turned[first][1]
                box = BodyBox.at(part_px, degrees, left, top)
                if surface.body_gap_columns and (min(box.columns(surface)) <= after or box.right > right_end):
                    continue
                holes = self._fit(turned, left, top, ledger, after, pinned)
                if holes is None:
                    continue
                covered = self._covered(part_px, degrees, left, top, holes) if part_px.get("covers_holes") else []
                if any(not ledger.is_free(hole) or (hole.column and hole.column <= after) for hole in covered):
                    continue
                if part_px.get("covers_holes") and not self._pins_keep_a_free_hole(holes, covered, ledger):
                    continue
                for pin, hole in holes.items():
                    ledger.claim(hole, "%s %s" % (part_id, pin))
                for hole in covered:
                    ledger.claim(hole, "%s, which covers it" % part_id)
                return PlacedPart(part_id, drawn.type, drawn.attrs, left, top, degrees, holes, drawn.record)
        raise NotDrawnError("%s does not fit on the breadboard" % part_id, NO_HOLE_LEFT, part_id)

    def _fit(self, turned, left, top, ledger, after, pinned):
        holes = {}
        for pin, (x, y) in turned.items():
            hole = self.geometry.hole_at(left + x, top + y)
            if hole is None or not ledger.is_free(hole) or (hole.column <= after and not pinned):
                return None
            if pinned and pin == pinned[0]:
                holes[pin] = hole
                continue
            if not ledger.group_is_free(hole.group) or hole.group in {one.group for one in holes.values()}:
                return None
            holes[pin] = hole
        return holes

    def _pins_keep_a_free_hole(self, holes, covered, ledger):
        """True when each pin's group keeps a hole that nothing takes and the body does not cover: a jumper needs it."""
        taken = {hole.name for hole in list(holes.values()) + covered}
        return all(any(hole.group == pin.group and ledger.is_free(hole) and hole.name not in taken
                       for hole in self.geometry.surface.terminal) for pin in holes.values())

    def _covered(self, part_px, degrees, left, top, holes):
        """The holes under the part's body, besides its own pins, rail holes too: its box, turned, about its center."""
        cx, cy = part_px["center"]
        half_w, half_h = (cy, cx) if degrees % 180 else (cx, cy)
        mine = {hole.name for hole in holes.values()}
        return [hole for hole in self.geometry.surface.holes if hole.name not in mine
                and abs(hole.x - (left + cx)) < half_w and abs(hole.y - (top + cy)) < half_h]


class BreadboardPlanner:
    """Pure: the steps, the geometry and what to draw for each component in, a BreadboardLayout out. The space between
    part bodies is `spacing.BodySpacing`'s (P953): the layout names in `crowded` each part placed closer than it keeps."""

    def __init__(self, geometry, catalog, placement=None, jumper_placement=None):
        self.geometry = geometry
        self.catalog = catalog
        self.placement = placement or FirstFitPartPlacement(geometry)
        self.jumper_placement = jumper_placement or JumperPlacement()

    def plan(self, steps):
        """Each part placed in step order, then each resistor with a leg in the row it joins, then each jumper."""
        ledger = HoleLedger(self.geometry.surface)
        self.placement.reserve_first(ledger)
        seated = list(steps.anchored())
        placed, spacing = {}, BodySpacing(self.geometry)
        for step in seated:
            if step.act == wiring_steps.PLACE:
                placed[step.subject] = self._place_apart(spacing, step.subject, ledger)
        self._refuse_what_is_not_drawn(seated)
        self._place_resistors(seated, placed, ledger, spacing)
        parts_only = HoleLedger(self.geometry.surface, ledger.taken)
        groups, jumpers = {}, []
        for number, step in enumerate(seated, 1):
            end = step.subject
            if not step.jumper:
                continue
            if step.act == wiring_steps.SETUP:
                jumper = Jumper(ledger.claim_free_hole(self._group_of(end, placed, groups), end.name),
                                ledger.claim_free_group(spacing.free_after(ledger), end.name), number, role=step.role)
                groups[end.name] = jumper.other.group
                jumpers.append(jumper)
            else:
                anchor = step.anchor.seat().end
                jumpers.append(Jumper(ledger.claim_free_hole(self._group_of(end, placed, groups), end.name),
                                      ledger.claim_free_hole(self._group_of(anchor, placed, groups), anchor.name), number,
                                      role=step.role))
        if spacing.gap:  # spark's own board; Wokwi's half board keeps the holes Wokwi was shown
            jumpers = ends_toward_their_runs(jumpers)
        return self.jumper_placement.place_jumpers(BreadboardLayout(
            self.geometry.surface.type, list(placed.values()), jumpers, self.geometry, tuple(spacing.crowded)), parts_only)

    @staticmethod
    def _refuse_what_is_not_drawn(seated):
        for step in seated:
            if step.act != wiring_steps.PLACE and step.anchor.seat().kind == wiring_steps.RAIL:
                mark = step.anchor.seat().mark
                raise NotDrawnError("%s goes on a rail, and rails are not drawn yet" % mark, NOT_DRAWN_YET, mark)
            if step.act == wiring_steps.SUPPLY:
                raise NotDrawnError("the %s supply comes from off the board, and a supply is not drawn yet" % step.subject,
                               NOT_DRAWN_YET, step.subject)

    def _place_apart(self, spacing, part_id, ledger, pinned=None, joins=None):
        """The part placed with its body right of `spacing`'s bound; when the board has no room for that, by the old
        rule, and named crowded. A resistor whose leg is `pinned` in the row of the part it `joins` keeps that part's."""
        drawn = self._drawn(part_id)
        after, close = spacing.bounds(joins)
        try:
            return spacing.placed(self.placement.place(part_id, drawn, ledger, after, pinned), False, joins)
        except NotDrawnError as refused:
            if refused.code != NO_HOLE_LEFT or after <= close:
                raise
        return spacing.placed(self.placement.place(part_id, drawn, ledger, close, pinned), True, joins)

    def _place_resistors(self, seated, placed, ledger, spacing):
        """A resistor has a fixed length, so it goes in with the leg that joins a row already in that row, its body in
        the space of the part it joins (BodySpacing); one that joins no row keeps the space after the last part."""
        resistors = collections.OrderedDict()
        for step in seated:
            if (step.act in (wiring_steps.SETUP, wiring_steps.JOIN)
                    and step.subject.kind == wiring_steps.RESISTOR):
                pinned = resistors.setdefault(step.subject.component, [])
                if step.act == wiring_steps.JOIN:
                    pinned.append((step.subject, step.anchor.seat().end))
        waiting = list(resistors.items())
        while waiting:
            # a resistor whose leg joins another resistor's row waits until that resistor is in
            ready = [(component, pinned) for component, pinned in waiting
                     if all(anchor.component in placed for _, anchor in pinned)]
            if not ready:
                raise NotDrawnError("%s joins a row that is never placed" % waiting[0][0], PLANNER_FAULT, waiting[0][0])
            for component, pinned in ready:
                if len(pinned) > 1:
                    raise NotDrawnError("both ends of %s join other rows, and a drawn resistor has a fixed length"
                                   % component, NOT_DRAWN_YET, component)
                joined = [(self._pin(end), self._group_of(anchor, placed, {})) for end, anchor in pinned]
                joins = pinned[0][1].component if joined else None
                placed[component] = self._place_apart(spacing, component, ledger, joined[0] if joined else None, joins)
            waiting = [one for one in waiting if one[0] not in placed]

    def _drawn(self, component):
        return drawn_part(component, self.catalog)

    def _group_of(self, end, placed, groups):
        return end_group(end, placed, self.catalog, groups)

    def _pin(self, end):
        return end_pin(end, self.catalog)


#: Why a part is not drawn, filled with its component: neither of the two ways to draw it is in its record.
NO_DRAWING_MESSAGE = "nothing says how to draw %s: its record has no Wokwi part and no physical block"


def drawn_part(component, catalog):
    """What the catalog draws for one component, or NotDrawnError naming it and the record the catalog knows it by."""
    drawn = catalog.get(component)
    if drawn is None:
        raise NotDrawnError(NO_DRAWING_MESSAGE % component, NO_DRAWING_FACT, component,
                            record=getattr(catalog, "undrawn", {}).get(component))
    return drawn


def end_pin(end, catalog):
    """The Wokwi pin of one end, or NotDrawnError naming it."""
    pin = drawn_part(end.component, catalog).pins.get(end.pin)
    if pin is None:
        raise NotDrawnError("which Wokwi pin is %s is not known" % end.name, NO_WOKWI_PIN, end.name)
    return pin


def end_group(end, placed, catalog, groups=None):
    """The group an end sits in: its pin's group, or the free group its board pad's jumper took (`groups`, which the
    planner fills as it draws). The planner and the drawing check (`drawing_match`) both ask it."""
    if groups and end.name in groups:
        return groups[end.name]
    if end.component not in placed:
        raise NotDrawnError("%s is joined before it is placed" % end.name, PLANNER_FAULT, end.name)
    return placed[end.component].holes[end_pin(end, catalog)].group


def hole_label(hole):
    """What a person reads on a breadboard for one terminal hole: its row letter, then its column (e41 for 41t.e). A rail
    hole keeps its Wokwi name."""
    group, _, letter = hole.name.partition(".")
    return "%s%d" % (letter, hole.column) if hole.column else hole.name


class StepHoles:
    """
    Value: the holes each numbered step uses in one planned layout (P945), {step number: words}, which the step list
    appends: a placing step names its part's holes, a jumper its two holes in the order the step runs it, and a
    resistor leg its own hole, at the step that puts it in. A step the layout does not draw has none. Built by `of`; it decides nothing again.
    """

    def __init__(self, words):
        self.words = dict(words)

    def get(self, number):
        """The words of one step's holes, or None."""
        return self.words.get(number)

    @staticmethod
    def _span(holes):
        """A part's holes by row letter, then column: each run of neighbouring columns as one range, "e38 to e45", and a
        hole with no neighbour alone, so "e12, e14" never reads as e13 too."""
        runs = []
        for hole in sorted(holes, key=lambda hole: (hole.name.partition(".")[2], hole.column)):
            last = runs[-1][-1] if runs else None
            if last and last.name.partition(".")[2] == hole.name.partition(".")[2] and hole.column == last.column + 1:
                runs[-1].append(hole)
            else:
                runs.append([hole])
        return ", ".join(hole_label(run[0]) if len(run) == 1 else "%s to %s" % (hole_label(run[0]), hole_label(run[-1]))
                         for run in runs)

    @classmethod
    def of(cls, layout, steps):
        """The holes of `steps` (a BreadboardSteps) as `layout` draws them, numbered as `steps.numbered()` numbers them."""
        placed = {part.id: part for part in layout.parts}
        jumpers = {jumper.step: jumper for jumper in layout.jumpers}
        words = {}
        for number, seated in enumerate(steps.anchored(), 1):
            if number in jumpers:
                words[number] = "from %s to %s" % (hole_label(jumpers[number].one), hole_label(jumpers[number].other))
            elif seated.act == wiring_steps.PLACE and seated.subject in placed:
                words[number] = cls._span(placed[seated.subject].holes.values())
            elif seated.act in (wiring_steps.SETUP, wiring_steps.JOIN) and seated.subject.kind == wiring_steps.RESISTOR \
                    and seated.subject.component in placed:
                hole = placed[seated.subject.component].holes.get(seated.subject.pin)
                words[number] = hole_label(hole) if hole else None
        return cls({number: said for number, said in words.items() if said})


class WokwiBreadboardDiagram:
    """Renderer: a BreadboardLayout as a Wokwi diagram, each jumper in the color of what it carries. Its constructor takes
    the colors, so the sheet and the diagram share one palette. Every drawing renderer has the four class attributes
    below, `text(layout)` and `why_not_written(layout)`, which `sheet.DRAWING_RENDERERS` and the build read."""

    #: The file it writes, beside the sheet.
    FILE_NAME = "breadboard.json"
    #: What the build calls the file in a line that says it was not written or was removed.
    NOUN = "drawn breadboard"
    #: What the build says beside the file's path when it wrote it.
    PURPOSE_MESSAGE = "an example layout of the steps on a breadboard: paste it into a new project on wokwi.com"
    #: What the sheet says about the file, under its steps.
    SHEET_MESSAGE = ("An example layout is in breadboard.json: paste it into the diagram.json of a new project on "
                     "wokwi.com.")
    #: What the sheet says once when no Wokwi diagram is written, filled with the why.
    SHEET_DECLINED_MESSAGE = "There is no Wokwi diagram: %s. Use the picture."
    #: Why no file is written, filled with each drawn part that Wokwi has no part for.
    DECLINED_MESSAGE = "Wokwi has no part for %s"

    def __init__(self, colors=None, breadboard_id="bb1"):
        self.colors = colors or wiring_steps.JumperColors()
        self.breadboard_id = breadboard_id

    def why_not_written(self, layout):
        """None when the layout can be a Wokwi diagram, else the NotWritten (its path is only the file's name): a part that
        says it is no Wokwi part would show the wrong part there. The why names each such part, in layout order, by the
        name the picture gives it (the board is "the board")."""
        missing = [part for part in layout.parts if not layout.geometry.part(part.type).get("wokwi_part", True)]
        if not missing:
            return None
        names = ["the board" if part.id == wiring_steps.THE_BOARD else layout.geometry.part(part.type).get("name") or part.id
                 for part in missing]
        said = names[0] if len(names) == 1 else "%s and %s" % (", ".join(names[:-1]), names[-1])
        return NotWritten(Path(self.FILE_NAME), self, NO_WOKWI_PART, None, self.DECLINED_MESSAGE % said)

    def render(self, layout):
        parts = [{"type": layout.breadboard, "id": self.breadboard_id, "top": 0, "left": 0, "attrs": {}}]
        for part in layout.parts:
            drawn = {"type": part.type, "id": part.id, "top": _round_px(part.top), "left": _round_px(part.left)}
            drawn.update({"rotate": part.rotate} if part.rotate else {})
            drawn["attrs"] = dict(part.attrs or {})
            parts.append(drawn)
        colors = self.colors.of({jumper.step: jumper.role for jumper in layout.jumpers})
        connections = [["%s:%s" % (self.breadboard_id, jumper.one.name), "%s:%s" % (self.breadboard_id,
                        jumper.other.name), colors[jumper.step], list(jumper.route)] for jumper in layout.jumpers]
        return {"version": 1, "author": "spark", "editor": "wokwi", "parts": parts, "connections": connections,
                "dependencies": {}}

    def text(self, layout):
        """The diagram as the file holds it: the same layout gives the same bytes."""
        return json.dumps(self.render(layout), indent=2, ensure_ascii=False) + "\n"


def _round_px(value):
    """A position as the file holds it: rounded once, here, and whole when it is whole."""
    value = round(value, 3)
    return int(value) if value == int(value) else value
