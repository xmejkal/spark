"""
The breadboard sheet from a built design (P191): the parts, each resistor they ask for, the numbered wiring steps, the
drawings and the changes on the bench, written beside the requirements file. The CLI `breadboard.py` calls `write`.
Its refusals carry the codes of `breadboard_codes`.
"""

import collections
import json
import re
from pathlib import Path

from spark.design import pin_assigner
import board_pads
from spark.design import loader
import drawer
from spark.design import board_emitter
import part_shape
import parts
import store
from spark.breadboard import bench_changes
from spark.breadboard import breadboard_codes
from spark.breadboard import drawing
from spark.breadboard import drawing_catalog
from spark.breadboard import drawing_match
from spark.breadboard import kept_moves
from spark.breadboard import wiring_steps

#: Where the build keeps what it built, relative to the project (`check_spine.py … --keep .`).
CIRCUIT = Path("dist") / "board" / "circuit.json"
#: What a build that finished was built from, written beside its circuit by `check_spine --keep` (the refuter, P191).
BUILT_FROM = CIRCUIT.parent / "built-from.json"
SHEET = "breadboard.md"
#: The component every generated design calls its dev board (emit_board, the converter's BOARD mapping).
BOARD_COMPONENT = "Mcu"
#: What each kind of passive a part asks for does, said the way a person reads it.
PURPOSE = {"pullup": "pull-up on", "pulldown": "pull-down on", "series": "in series with", "divider": "divider on"}
LEGEND = ("*have*: yours = your drawer holds it for this project · in your drawer = you own it, not held here · "
          "to get = not in your drawer · blank = this project is not on your list (`/spark:init` puts it there)")

#: The views of the wiring steps the sheet shows, in order: (heading, one line that says how to read it, renderer).
WIRING_VIEWS = (
    ("Steps", "One connection per step. The board's pins take the rows beside them, so a board pin always gets a jumper.",
     wiring_steps.NumberedList()),
    ("Diagram", "Each line is one step, with its number.", wiring_steps.MermaidDiagram()),
)

#: The one palette of step colors, for the sheet's color line and the drawing's jumpers alike.
STEP_COLORS = wiring_steps.StepColors()
#: The drawings written beside the sheet, in order: each a renderer of one planned layout (P270). A new drawing is a
#: new entry here, and nothing else changes.
DRAWING_RENDERERS = (drawing.WokwiBreadboardDiagram(STEP_COLORS),
                     drawing.SvgBreadboardDiagram(STEP_COLORS))
#: What the sheet says of the bench: one line per change since the last build, in these words.
CHANGE_LIST = bench_changes.ChangeList()
#: The drawing a person edits in Wokwi, whose moves a rebuild keeps (P273).
EDITABLE_DRAWING = next(renderer for renderer in DRAWING_RENDERERS
                        if isinstance(renderer, drawing.WokwiBreadboardDiagram))


class NotBuilt(Exception):
    """Error: there is no built circuit to read, or it is not this design's. `code` (breadboard_codes) says which."""

    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


# --- MVP ---
#: Each error from outside that stops the sheet, with its code: the errors `main` catches, after a NotBuilt.
OUTSIDE_CODES = {loader.DesignError: breadboard_codes.REQUIREMENTS_UNUSABLE, store.StoreProblem: breadboard_codes.STORE_PROBLEM,
                 OSError: breadboard_codes.FILE_UNUSABLE}
REFUSALS = (NotBuilt, *OUTSIDE_CODES)


def refusal_code(stopped):
    """Value: the code (breadboard_codes) of one of REFUSALS: a NotBuilt's own, else its outside error's. It never reads
    the message."""
    if isinstance(stopped, NotBuilt):
        return stopped.code
    return next(code for kind, code in OUTSIDE_CODES.items() if isinstance(stopped, kind))
# --- end MVP ---


def _passives(design_parts):
    """{component name of a passive a part asks for: what it is for}, from the parts' records."""
    found = {}
    for part in design_parts:
        for host_part in part.get("host_parts") or []:
            phrase = PURPOSE.get(host_part["kind"], host_part["kind"] + " on")
            for name in board_emitter.host_part_names(part, host_part):
                found[name] = "%s %s %s" % (phrase, board_emitter.component_name(part), host_part["pin"])
    return found


def record_built_from(requirements_path, out):
    """Write what a build that finished was built from; `check_spine --keep` calls it, and the sheet compares it."""
    Path(out).write_text(json.dumps({"requirements": json.loads(Path(requirements_path).read_text())}, indent=1) + "\n")


def _check_fresh(circuit, design_parts, circuit_path, requirements_path):
    """Refuse a circuit that is not a finished build of this design: not a circuit, a failed build, a build of other
    requirements (the board swapped, a part added), or one that never recorded what it was built from."""
    again = "build again: `check_spine.py %s --keep .`" % requirements_path.name
    built_from = circuit_path.parent / BUILT_FROM.name
    if not built_from.is_file():
        raise NotBuilt("%s records no finished build (no %s beside it): %s" % (circuit_path, BUILT_FROM.name, again),
                       breadboard_codes.NOT_BUILT)
    try:
        recorded = json.loads(built_from.read_text()).get("requirements")
        current = json.loads(requirements_path.read_text())
    except (ValueError, AttributeError) as broken:
        raise NotBuilt("%s cannot be read (%s): %s" % (built_from, broken, again),
                       breadboard_codes.BUILD_UNREADABLE) from broken
    if recorded != current:
        raise NotBuilt("%s was built from other requirements than %s: %s" % (circuit_path, requirements_path.name, again),
                       breadboard_codes.BUILT_FROM_OTHER_REQUIREMENTS)
    if not isinstance(circuit, list) or not all(isinstance(element, dict) for element in circuit):
        raise NotBuilt("%s is not a built circuit: %s" % (circuit_path, again), breadboard_codes.BUILD_UNREADABLE)
    failed = sorted({e["type"] for e in circuit if re.fullmatch(r"source_\w+_error", e.get("type") or "")})
    if failed:
        raise NotBuilt("the last build failed (%s): %s" % (", ".join(failed), again), breadboard_codes.BUILD_FAILED)
    wanted = ({BOARD_COMPONENT} | {board_emitter.component_name(part) for part in design_parts}
              | set(_passives(design_parts)))
    built = {e["name"] for e in circuit if e.get("type") == "source_component"
             and e.get("ftype") in ("simple_chip", "simple_resistor")}
    if wanted != built:
        raise NotBuilt("%s was built from other requirements (in the build only: %s; in the file only: %s): %s"
                       % (circuit_path, ", ".join(sorted(built - wanted)) or "nothing",
                          ", ".join(sorted(wanted - built)) or "nothing", again),
                       breadboard_codes.BUILT_FROM_OTHER_REQUIREMENTS)


#: What the parts table's `have` column says of a part: the words the sheet prints, and the codes `_have` decides on.
HAVE_YOURS, HAVE_IN_DRAWER, HAVE_TO_GET = "yours", "in your drawer", "to get"


def _have(requirements_path, record_ids):
    """{record id: yours | in your drawer | to get}, from the drawer; None when the project is not on the list."""
    name = store.find_listed_name(requirements_path.resolve().parent)
    if not name:
        return None
    said = {record_id: HAVE_TO_GET for record_id in record_ids}
    for entry in drawer.entries().values():
        target = entry.get("is") if isinstance(entry.get("is"), dict) else {}
        if entry.get("skip"):
            continue
        for record_id in (value for value in target.values() if value in said):
            if (entry.get("used_in") or {}).get(name):
                said[record_id] = HAVE_YOURS
            elif said[record_id] == HAVE_TO_GET and entry.get("count", 1):
                said[record_id] = HAVE_IN_DRAWER
    return said


def _parts_table(board, design_parts, resistors, supplies, have):
    """The parts to buy or take from the drawer, as Markdown rows: equal parts and equal resistors totalled."""
    status = (lambda record_id: have.get(record_id, HAVE_TO_GET)) if have is not None else (lambda record_id: "")
    rows = ["| qty | part | for | have |", "| --- | --- | --- | --- |",
            "| 1 | %s | the board | %s |" % (board.get("name"), status(board.get("id")))]
    by_record = collections.OrderedDict()
    for part in design_parts:
        by_record.setdefault(part["id"], (part, []))[1].append(board_emitter.component_name(part))
    rows += ["| %d | %s | %s | %s |" % (len(names), part.get("name"), ", ".join(sorted(names)), status(record_id))
             for record_id, (part, names) in by_record.items()]
    by_value = collections.OrderedDict()
    for tag, value, purpose in resistors.values():
        by_value.setdefault(value, []).append("%s %s" % (tag, purpose))
    rows += ["| %d | %s resistor, through-hole | %s | %s |" % (len(uses), value, "; ".join(uses), status(None))
             for value, uses in by_value.items()]
    rows += ["| | what feeds %s: a supply from off the board, not part of this list | %s | |"
             % (net, ", ".join(sorted(users))) for net, users in supplies.items()]
    return rows + ["| | a breadboard and jumper wires | | %s |" % status(None), "", LEGEND]


def _supplies(circuit):
    """{net name: the parts on it} for each point that carries a named net and no board pin: a supply from off the board."""
    found = {}
    for point in wiring_steps.points(circuit):
        if point.nets and not any(component["name"] == BOARD_COMPONENT for component, _ in point.members):
            for net in point.nets:
                found.setdefault(net, set()).update(component["name"] for component, _ in point.members)
    return found


def _unwired(board, design):
    """A line for each signal the requirements add that no part takes: its pin is spent, and nothing is on it yet."""
    own = [signal for signal in design.signals if not signal.get("from")]
    if not own:
        return []
    assignments, _ = pin_assigner.assign(design.board, design.signals)
    pads = board_pads.BoardPads.from_record(board)  # --- MVP --- (P512)
    return ["- %s: board %s, nothing wired to it yet (the requirements add this signal)"
            % (a["signal"], pads.pad_of(a["pin"])) for a in assignments if a["signal"] in {s["name"] for s in own}]


def _before_power(design_parts, supplies):
    """What each part's record says must be true before power is applied: its CONFLICTs, its floating pins, its
    warnings, in the record's own words; and the supplies from off the board, whose voltage this sheet does not set."""
    lines, seen = [], set()
    lines += ["- %s comes from off the board, and this sheet does not say its voltage: check it against the supply "
              "range of %s (`parts.py --show`) before you connect it" % (net, ", ".join(sorted(users)))
              for net, users in supplies.items()]
    for part in design_parts:
        name = board_emitter.component_name(part)
        lines += ["- **CONFLICT** on %s: %s" % (name, conflict) for conflict in parts.pull_conflicts(part)]
        lines += ["- %s %s has no resistor: the firmware must pull it up with Pin.PULL_UP, as `pins.py` says (P204)"
                  % (name, pin) for pin in part.get("_firmware_pulls", [])]
        lines += ["- %s %s: %s" % (name, pin["pin"], pin.get("note", "")) for pin in part.get("unused_pins") or []]
        if part["id"] not in seen:
            seen.add(part["id"])
            lines += ["- %s: %s" % (part.get("name"), requirement) for requirement in part.get("host_requirements") or []]
    shows = ", ".join("`parts.py --show %s`" % record_id for record_id in sorted({part["id"] for part in design_parts}))
    return lines + ["", "Each record whole, with what it asks of the board: %s." % shows]


#: What one build gives the sheet and the drawing: the design, its circuit, its resistors and its steps.
Read = collections.namedtuple("Read", "built circuit resistors point_lines steps")


def _read_build(requirements_path, circuit_path=None):
    """The built design and its steps, for a requirements file whose project has been built with --keep."""
    requirements_path = Path(requirements_path)
    circuit_path = Path(circuit_path) if circuit_path else requirements_path.resolve().parent / CIRCUIT
    if not circuit_path.is_file():
        raise NotBuilt("nothing is built at %s yet: run `check_spine.py %s --keep .` first"
                       % (circuit_path, requirements_path.name), breadboard_codes.NOT_BUILT)
    built = loader.load(requirements_path)
    try:
        circuit = json.loads(circuit_path.read_text())
    except ValueError as broken:
        raise NotBuilt("%s is not JSON (%s): build again" % (circuit_path, broken), breadboard_codes.BUILD_UNREADABLE) from broken
    _check_fresh(circuit, built.parts, circuit_path, requirements_path)
    passives = _passives(built.parts)
    resistors = collections.OrderedDict(
        (c["name"], ("R%d" % number, c.get("display_resistance") or "", passives.get(c["name"], "")))
        for number, c in enumerate((c for c in circuit if c.get("type") == "source_component"
                                    and c.get("ftype") == "simple_resistor"), 1))
    point_lines, steps = wiring_steps.wiring(built.board, circuit, built.parts, resistors, BOARD_COMPONENT)
    return Read(built, circuit, resistors, point_lines, steps)


def _drawing_inputs(read):
    """(geometry, catalog) the layout is planned on. Wokwi's own geometry for a board it measured; for a board drawn
    from its own record, a copy that holds its part_px and spark's 63-column breadboard (P412)."""
    wokwi = drawing.WokwiGeometry.load()
    catalog = drawing_catalog.describe_parts(read, wokwi)
    board = read.built.board
    part_px, _ = part_shape.find_part_px(board, part_shape.sources_for(wokwi.data["parts"]))
    if not part_px.get("full_surface"):
        return wokwi, catalog
    geometry = wokwi.with_part(catalog[wiring_steps.THE_BOARD].type, part_px)
    return geometry.with_surface(drawing.Surface.load_full()), catalog


def _plan_layout(read):
    geometry, catalog = _drawing_inputs(read)
    return drawing.BreadboardPlanner(geometry, catalog).plan(read.steps)


def drawing_text(requirements_path, circuit_path=None, read=None):
    """The Wokwi diagram's text, or NotDrawn with what stopped it."""
    return EDITABLE_DRAWING.text(_plan_layout(read or _read_build(requirements_path, circuit_path)))


#: One plan of the layout for a sheet and its drawings: the layout, or what stopped it (a NotDrawn, with its code and
#: subject), and the earlier parts it could not keep as the person left them ([NotKeptResult]), the fresh layout, and
#: each end the layout joins differently from the points ([DrawingDiffersResult], P279).
PlannedLayout = collections.namedtuple("PlannedLayout", "layout stopped not_kept fresh differs", defaults=(None, ()))


def _plan_once(read, earlier_path=None, record=None):
    """The layout planned fresh; then, when `earlier_path` is a diagram the person may have edited, planned again
    keeping the parts they moved. The fresh plan's error stands. When the kept plan has no room, the fresh layout is
    used and the moved parts are named. `record` is the earlier wiring record (None when there is none or it cannot be
    read): it says which jumpers of the earlier file spark drew itself. The layout it returns is checked against the
    points (P279)."""
    try:
        fresh = _plan_layout(read)
    except drawing.NotDrawn as stopped:
        return PlannedLayout(None, stopped, [])
    geometry, catalog = _drawing_inputs(read)

    def checked(layout, not_kept):
        differs = drawing_match.DrawnNets(layout, layout.geometry).differences(read.steps.points, catalog)
        return PlannedLayout(layout, None, not_kept, fresh, differs)

    if earlier_path is None or EDITABLE_DRAWING.why_not_written(fresh):
        return checked(fresh, [])  # no Wokwi diagram is written, so no earlier one is kept
    earlier = kept_moves.EarlierDiagram.read(earlier_path, geometry.surface.type)
    if earlier is None:
        return checked(fresh, [])
    if earlier.why_unread:
        return checked(fresh, [kept_moves.NotKeptResult(
            Path(earlier_path).name, kept_moves.UNREADABLE,
            kept_moves.MESSAGES[kept_moves.UNREADABLE] % earlier.why_unread)])
    placement = kept_moves.KeepMovesFirstFitPartPlacement(geometry, earlier, catalog)
    jumpers = kept_moves.KeepMovesJumperPlacement(geometry, earlier)
    try:
        layout = drawing.BreadboardPlanner(geometry, catalog, placement, jumpers).plan(read.steps)
        default = None
    except drawing.NotDrawn:
        layout, default = fresh, kept_moves.NO_ROOM
    drawn = record.drawn_jumpers if record and not record.why_unread else None
    named = kept_moves.name_parts_not_kept(earlier, layout, fresh, placement.reasons, default)
    named += kept_moves.name_jumpers_not_kept(earlier, layout, fresh, jumpers.reasons, geometry, drawn, default)
    return checked(layout, named)


def holds_parts(path):
    """True when `path` is a breadboard.json of spark's kind with at least one part on it: a diagram that may hold a
    person's moves (P273), which a build that did not finish leaves alone."""
    earlier = kept_moves.EarlierDiagram.read(path, drawing.WokwiGeometry.load().surface.type)
    return bool(earlier and earlier.parts)


def _drawing_lines(planned):
    """The sheet's lines on the drawings beside it: the jumper colors, each drawing, the board it was drawn from and any
    point it joins differently; or why none is written."""
    if not planned.layout:
        return ["", "%s not written: %s." % (" and ".join(renderer.FILE_NAME for renderer in DRAWING_RENDERERS),
                                              planned.stopped)]
    colors = "Each jumper has its step's color: %s." % ", ".join(
        "%d %s" % (jumper.step, STEP_COLORS.color(jumper.step)) for jumper in planned.layout.jumpers)
    drawn = [renderer for renderer in DRAWING_RENDERERS if not renderer.why_not_written(planned.layout)]
    first, *others = drawn
    lines = ["", "%s %s" % (first.SHEET_MESSAGE, colors)]
    lines += [line for renderer in others for line in ("", renderer.SHEET_MESSAGE)]
    if len(drawn) < len(DRAWING_RENDERERS):
        lines += ["", drawing.WokwiBreadboardDiagram.SHEET_DECLINED_MESSAGE]
    lines += [line for one in drawing_catalog.board_lines(planned.layout) for line in ("", one)]
    if planned.differs:
        more = len(planned.differs) - 1
        lines += ["", "The drawing does not join the points the same way: %s%s. Wire from the steps above."
                  % (planned.differs[0].why, ", and %d more" % more if more else "")]
    return lines


def sheet(requirements_path, circuit_path=None, read=None, planned=None, change_lines=None):
    """The sheet, as Markdown, for a requirements file whose project has been built with --keep (or its circuit).
    `planned` is the layout `write()` already planned, so the sheet says what the drawings show. `change_lines` is the
    section "Changes since the last build" (P300), None on a first build."""
    requirements_path = Path(requirements_path)
    read = read or _read_build(requirements_path, circuit_path)
    planned = planned or _plan_once(read)
    built, circuit, resistors, steps = read.built, read.circuit, read.resistors, read.steps
    supplies = _supplies(circuit)
    have = _have(requirements_path, {part["id"] for part in built.parts} | {built.board.get("id")})
    lines = ["# Breadboard: %s, on a %s" % (requirements_path.resolve().parent.name, built.board.get("name")), "",
             "## Parts", ""]
    lines += _parts_table(built.board, built.parts, resistors, supplies, have)
    lines += ["", "## Wiring"]
    if change_lines is not None:
        lines += ["", "### Changes since the last build", ""] + change_lines
    for heading, intro, renderer in WIRING_VIEWS:
        lines += ["", "### " + heading, "", intro, ""] + renderer.render(steps)
    lines += _drawing_lines(planned)
    lines += ["", "### Points", "", "After the steps, each line is one point: its ends must be joined, and nothing else.",
              ""]
    lines += read.point_lines
    unwired = _unwired(built.board, built)
    lines += (["", "Not wired:", ""] + unwired) if unwired else []
    lines += ["", "## Before you power it", ""] + _before_power(built.parts, supplies)
    return "\n".join(lines) + "\n"


#: Result: what write() wrote: the sheet's path, [(path, renderer)] for each drawing written, a NotWritten for each one not
#: written (its code and subject are None for an older refusal), the [NotKeptResult] of the
#: earlier parts not kept, the [WiringChange] since the last build (none on a first build), each end the drawing joins
#: differently from the points ([DrawingDiffersResult], P279), and what a board's drawing was made from (`record`, or
#: None for Wokwi's own geometry).
WriteResult = collections.namedtuple("WriteResult", "sheet drawings not_written not_kept changes differs drawn_from",
                                     defaults=((), None))


def _spark_jumpers(planned, earlier_path, record):
    """The pairs of holes of the jumpers in the layout that spark drew itself: a jumper that is not in the earlier
    breadboard.json, or that is there and was spark's in the earlier record. A kept jumper of the person's is not.
    With no record (a project built before it), a jumper that equals one of the fresh plan counts as spark's."""
    layout = planned.layout
    if not layout:
        return []
    geometry = drawing.WokwiGeometry.load()
    earlier = kept_moves.EarlierDiagram.read(earlier_path, geometry.surface.type)
    person = {frozenset((wire.one, wire.other)) for wire in earlier.jumpers} if earlier else set()
    pairs = [frozenset((jumper.one.name, jumper.other.name)) for jumper in layout.jumpers]
    if record and not record.why_unread:
        sparks = record.drawn_jumpers
    else:
        sparks = {frozenset((jumper.one.name, jumper.other.name)) for jumper in planned.fresh.jumpers}
    return [pair for pair in pairs if pair not in person or pair in sparks]


def _change_lines(record, changes):
    """The section "Changes since the last build": None on a first build."""
    if record is None:
        return None
    if record.why_unread:
        return ["- Changes cannot be compared with the last build: %s %s. The steps below are the whole wiring."
                % (bench_changes.WiringRecord.FILE_NAME, record.why_unread)]
    return ["- " + line for line in CHANGE_LIST.render(changes)] or ["- Nothing to change on the bench."]


def _drawn_or_not(paths, planned):
    """([(path, renderer)] to write, [NotWritten]) for each drawing beside the sheet: a renderer that declines the
    layout is not written, and with no layout none is, for what stopped the plan."""
    layout = planned.layout
    said = [(path, renderer, renderer.why_not_written(layout) if layout else None) for path, renderer in paths]
    drawn = [(path, renderer) for path, renderer, why in said if layout and not why]
    if layout:
        return drawn, [why._replace(path=path) for path, _, why in said if why]
    return drawn, [drawing.NotWritten(path, renderer, planned.stopped.code, planned.stopped.subject,
                                      str(planned.stopped)) for path, renderer, _ in said]


def write(requirements_path, out, circuit_path=None):
    """Write the sheet to `out`, and each drawing beside it when the layout can be planned; what `check_spine --keep`
    calls beside the kept board. The layout is planned once. A drawing left from an earlier build is removed, since it
    describes another one."""
    read = _read_build(requirements_path, circuit_path)
    paths = [(Path(out).parent / renderer.FILE_NAME, renderer) for renderer in DRAWING_RENDERERS]
    record_path = Path(out).parent / bench_changes.WiringRecord.FILE_NAME
    # the earlier breadboard.json and record are read here, before the new ones overwrite them
    earlier_path = Path(out).parent / EDITABLE_DRAWING.FILE_NAME
    record = bench_changes.WiringRecord.read(record_path)
    planned = _plan_once(read, earlier_path, record)
    seated = read.steps.anchored()
    colors = {jumper.step: STEP_COLORS.color(jumper.step) for jumper in planned.layout.jumpers} if planned.layout else {}
    changes = (bench_changes.changes_between(record, seated, colors)
               if record and not record.why_unread else [])
    new_record = bench_changes.WiringRecord.from_build(seated, colors, record, _spark_jumpers(
        planned, earlier_path, record))
    drawn, not_written = _drawn_or_not(paths, planned)
    try:
        # every text is rendered before any file is written, so a renderer that fails leaves no new sheet either
        texts = [renderer.text(planned.layout) for _, renderer in drawn]
    except Exception:
        for path, _ in paths:
            path.unlink(missing_ok=True)
        raise
    Path(out).write_text(sheet(requirements_path, read=read, planned=planned, change_lines=_change_lines(record, changes)))
    new_record.write(record_path)
    for refused in not_written:
        refused.path.unlink(missing_ok=True)  # a drawing left from an earlier build describes another one
    try:
        for (path, _), text in zip(drawn, texts):
            path.write_text(text)
    except Exception:
        for path, _ in paths:
            path.unlink(missing_ok=True)  # an old drawing describes another build: never leave it beside a new sheet
        raise
    if not planned.layout:
        return WriteResult(Path(out), [], not_written, [], changes)
    return WriteResult(Path(out), drawn, not_written, planned.not_kept, changes, planned.differs,
                       drawing_catalog.find_board_px(planned.layout).get("source"))
