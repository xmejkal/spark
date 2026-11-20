"""
The room on the drawn breadboard (P953, #1359): a part's body as it lies (`BodyBox`), the free columns the planner keeps
between bodies (`BodySpacing`), the one row a tall module takes, and which hole of a row each of two jumpers takes.
`drawing`'s planner reads them, and `svg_diagram`'s canvas holds every BodyBox. Nothing here imports `drawing`.
"""

import collections


def rotate(pins, center, degrees):
    """{pin: (x, y)} turned clockwise about the center, as Wokwi turns a part. Not rounded: round once, at the end."""
    cx, cy = center
    turned = {}
    for pin, (x, y) in pins.items():
        for _ in range(degrees // 90 % 4):
            x, y = cx + cy - y, cy - cx + x
        turned[pin] = (x, y)
    return turned


class BodyBox(collections.namedtuple("BodyBox", "left top right bottom")):
    """Value: a part's body as it is turned and placed, its edges in px: its four corners turned about its center."""

    @classmethod
    def of(cls, part, part_px):
        """The box of a PlacedPart (or anything with `left top rotate`)."""
        return cls.at(part_px, part.rotate, part.left, part.top)

    @classmethod
    def at(cls, part_px, degrees, left, top):
        """The box of a part of `part_px` turned by `degrees` with its corner at (left, top)."""
        width, height = part_px["size"]
        corners = rotate({"0": (0, 0), "1": (width, 0), "2": (0, height), "3": (width, height)}, part_px["center"],
                         degrees).values()
        return cls(left + min(x for x, _ in corners), top + min(y for _, y in corners),
                   left + max(x for x, _ in corners), top + max(y for _, y in corners))

    def columns(self, surface):
        """The columns of `surface` whose x lies inside the box, edges included, in order."""
        return sorted({hole.column for hole in surface.terminal if self.left - 0.01 <= hole.x <= self.right + 0.01})


class BodySpacing:
    """
    Strategy: the space between part bodies, built for one plan. On a surface with `body_gap_columns` (spark's full board, the PO's
    "leave space in between elements"), a part's body is held right of `after`, that many free columns past the bodies
    placed before it; when it does not fit so, the old rule holds it right of `close`, SPACING_COLUMNS past the last
    pin, and the plan names it in `crowded`. A resistor whose leg joins a part's row keeps that part's bound
    (`limits`). Wokwi's half board has no gap, so its plan is the old rule alone, the one Wokwi was shown (P267).
    """

    #: The old rule: columns from one part's last pin to the next part's first, one empty column between them.
    SPACING_COLUMNS = 2

    def __init__(self, geometry):
        self.geometry = geometry
        self.gap = geometry.surface.body_gap_columns
        self.after = self.close = 1
        self.crowded, self.limits = [], {}

    def bounds(self, joins=None):
        """(after, close): the column a part's body is held right of, and the old rule's. A resistor that `joins` a
        part's row keeps that part's bound, and none by the old rule."""
        if joins:
            return (self.limits.get(joins, 0) if self.gap else 0), 0
        return self.after, self.close

    def placed(self, part, crowded, joins=None):
        """Note a part placed (`crowded` when by the old rule); a part placed in step order moves the bounds on."""
        after, close = self.bounds(joins)
        self.limits[part.id] = close if crowded else after
        self.crowded += [part.id] if crowded else []
        if joins is None:
            pins = max(hole.column for hole in part.holes.values())
            body = BodyBox.of(part, self.geometry.part(part.type)).columns(self.geometry.surface)
            self.close = pins + self.SPACING_COLUMNS
            self.after = max([pins] + body) + self.gap if self.gap else self.close
        return part

    def free_after(self, ledger):
        """The column a free row for a jumper lies right of: `after`, or `close` when no row right of it is free."""
        free = any(hole.column > self.after and ledger.group_is_free(hole.group) for hole in self.geometry.surface.terminal)
        return self.after if free else self.close


def tall_module_row(part_px, turned, degrees, surface):
    """The one row letter a tall module's pins may take at this turn, else None: for a part that covers holes, with its
    pins in one row, whose body reaches further from that row than the gap is wide, the outermost row on the side its
    body faces (row j when it hangs down, row a when it hangs up), so the body hangs past the board's outer edge. A
    board with two rows of pins straddles the gap by design, so it gets None."""
    if not part_px.get("covers_holes") or len({round(y, 3) for _, y in turned.values()}) != 1:
        return None
    pin_y = next(iter(turned.values()))[1]
    box = BodyBox.at(part_px, degrees, 0, 0)
    down, up = box.bottom - pin_y, pin_y - box.top
    top, bottom = surface.top_letters, [letter for letter in surface.letters_y if letter not in surface.top_letters]
    if max(down, up) <= surface.letters_y[bottom[0]] - surface.letters_y[top[-1]]:
        return None
    return bottom[-1] if down > up else top[0]


def ends_toward_their_runs(jumpers):
    """The jumpers with the holes of each row that two or more of them end in handed out again: the end whose other end
    lies higher takes the higher hole, so two legs in one column never run along each other (the walk's two jumpers to
    the e-paper's VCC, one from row a and one from row j). A rail's holes all lie at one height, so each rail jumper keeps
    the rail hole nearest its other end (P953)."""
    ends = collections.defaultdict(list)
    for index, jumper in enumerate(jumpers):
        for side, here, there in (("one", jumper.one, jumper.other), ("other", jumper.other, jumper.one)):
            if here.column:
                ends[here.group].append((index, side, there))
    changed = list(jumpers)
    for here in ends.values():
        holes = sorted((getattr(jumpers[index], side) for index, side, _ in here), key=lambda hole: hole.y)
        for (index, side, _), hole in zip(sorted(here, key=lambda end: (end[2].y, end[0])), holes):
            changed[index] = changed[index]._replace(**{side: hole})
    return changed
