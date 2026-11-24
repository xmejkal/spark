"""
The files `check_spine.py --keep DIR` writes into DIR, and what an earlier build left there (P705): the built board,
the breadboard sheet and its drawings, the page, the pin map and the simulation project, each a kept entry {file, did,
why, line}. One meaning of `kept_`: what a run keeps between runs, as `kept_moves`' moves are.
"""

import re
import shutil
from collections import namedtuple
from pathlib import Path

from spark.build import build_codes
from spark.build.build_record import DIST_WRITTEN, OWN_FILES, STAGE_IN_THE_WAY, STAGE_SUFFIX, WRITTEN_SHA256, BuildRecordStore, PreviousVersionFiles, StagedFile, StageTakenError, replace_whole, sha256_of
from spark.build.build_service import verdict
from spark.build.stages import BUILD, REQUIREMENTS, SIMULATION, skipped_the_build
from spark.breadboard import drawing, sheet, svg_diagram, tabbed_page
from spark.design import board_sections, loader
from spark.design import pin_assigner
from spark.firmware import sim_project
from spark.records import board_records, store

from spark.core import codes
from spark.core.outcomes import OK, STATUS_FOR
from spark.core.result import envelope_item

#: Where --keep puts the pin map, the path every document gives `--emit-pins` (P196).
PIN_MODULE = Path("firmware") / "pins.py"
#: What stops the pin map from being written: no pin can be placed, or the design, the store or a file cannot be read.
PIN_MAP_REFUSALS = (pin_assigner.ImpossibleError, loader.DesignError, store.StoreError, OSError, ValueError)

#: The `did` of a kept entry for a part the person moved in breadboard.json that the build could not keep (P273).
MOVE_NOT_KEPT = "move not kept"
#: The `did` of a kept entry for one thing a rebuild asks a person to change on the bench (P300).
CHANGED = "changed"
#: The `did` of a kept entry for one end the drawn breadboard joins differently from circuit.json's points (P279).
DRAWING_DIFFERS = "drawing differs"
#: The `did` of a kept entry for a .tsx left alone whose traces join other pins than this build's board (P660).
TRACES_DIFFER = "traces differ"
#: The `did` of a kept entry for a .tsx left alone with a trace in a form spark does not read, so it was not compared.
TRACES_NOT_COMPARED = "traces not compared"
#: The `did` of a kept entry for a file spark made now: a `.tsx` that was not there, or `dist/`.
WROTE = "wrote"
#: The `did` of a kept entry for a `board.tsx` spark wrote earlier, nobody changed, and this build made again as another board (P874).
REPLACED = "replaced"
#: The `did` of a kept entry for a `board.tsx` spark wrote earlier and this build made the same board: nothing is written.
UNCHANGED = "unchanged"
#: The `did` of a kept entry for a .tsx that is not touched.
LEFT_ALONE = "left alone"
NOT_KEPT = "not kept"  # the `did` of a kept entry for a file that could not be kept
#: Why a board is left alone when the replace failed: its first step is the new board, its second the previous version.
WRITE_FAILED = "spark could not write the new board, so it is left as it was: %s"
#: Why a board spark wrote and nobody changed is left alone: the build did not finish, so its board is not to be trusted.
NOT_FINISHED = "this build did not finish, so spark did not replace it"
KEEP_FAILED = "spark could not keep the previous version, so the board is left as it was: %s"
#: How many traces of each side the stderr line names; --json lists them all.
TRACES_SHOWN = 10
#: A comment in a board file: JSX's `{/* … */}` and a line's `// …`. A trace in one is not a trace.
_COMMENT = re.compile(r"/\*.*?\*/|//[^\n]*", re.S)
#: The tag that opens a trace, with any whitespace after it, and a trace as the board emitter writes it:
#: `<trace from="A" to="B"`, any attribute after.
_TRACE_TAG = re.compile(r"%s\s" % re.escape(board_sections.TRACE_TAG.strip()))
_TRACE = re.compile(_TRACE_TAG.pattern + r'\s*from="([^"]*)"\s+to="([^"]*)"')


def left_off(requirements):
    """
    The needs the requirements file says it leaves off the board (C-2: the note `parts.py --requirements` writes, `unserved`),
    each as `soil (no pick)` or `battery (no record: lipo)` — so "the chain runs end to end" never stands alone over a goal the
    board does not serve. A note in no shape spark writes says nothing, as a file with no note does.
    """
    note = requirements.get("unserved") if isinstance(requirements, dict) else None
    return ["%s (%s%s)" % (item["need"], item.get("why"), ": " + ", ".join(map(str, item["picks"])) if item.get("picks") else "")
            for item in (note if isinstance(note, list) else []) if isinstance(item, dict) and isinstance(item.get("need"), str)]


def design_handed_to(workdir, project):
    """
    The design the chain is about to be handed (§5.7): the work folder's copy of the requirements, with the board and the
    part records they name, loaded once, now. `built` names this — what the chain ran on — and not what the person's files
    say by the time the build has finished, minutes later. None when it cannot be loaded: `run` says why, as a stage, and a
    chain that did not run end to end records nothing.
    """
    try:
        return loader.load(workdir / "requirements.json", project)
    except Exception:  # noqa: BLE001 — whatever is wrong with the input, `run` names it; only the record of the build goes without
        return None


def kept_into(workdir, destination, written=None, finished=True):
    """
    Put the built board where a person — and every check — will look for it. `dist/` is pure build output: one that holds
    the circuit the build reads replaces the earlier one whole, staged (P1088). A `.tsx` is a person's to edit, so one
    that is there is left alone and named, unless `written` (the build record's `{name: sha256}` of what spark wrote,
    P874) holds its bytes: then it is `replaced`, or `unchanged` when this build made the same board (`_replaced`).
    Without `written` (an old project, no requirements file) nothing is replaced: delete the file to have it regenerated.

    Each file is {file, did, why, line}: `did` is `wrote`, `replaced`, `unchanged` or `left alone`, and `line` what
    stderr says; a `.tsx` carries the `sha256` of the bytes spark made. A .tsx left alone whose traces are not this
    build's is followed by a `traces differ` entry (P660). A board spark wrote is replaced only when `finished` (the build
    stage ended ok). A `dist/` that cannot be copied is its own `not kept` entry; the `.tsx` entries stand (P891).
    With --json the report carries the rest under `kept`.
    """
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    written, kept = written or {}, []
    for source in sorted(workdir.glob("*.tsx")):
        target, made = destination / source.name, sha256_of(source)
        if not target.exists() and not target.is_symlink():
            shutil.copy2(source, target)
            kept.append({"file": str(target), "did": WROTE, "why": None, "sha256": made, "line": "wrote %s" % target})
        elif _spark_wrote(target, written.get(source.name)):
            kept += _replaced(source, target, made, written[source.name]) if finished else _unfinished(source, target)
        else:
            kept.append(_left_alone(target, "delete it to have it regenerated"))
            kept += _compare_traces(target, source)
    if (workdir / sheet.CIRCUIT).is_file():  # P1088: the build stage's own test of a board that was built
        try:
            left = replace_whole(workdir / "dist", destination / "dist")  # an earlier dist/ set aside that stays is named (P1088)
        except OSError as refused:  # a copy that fails midway is a shutil.Error; the entries above stand, so the record holds what spark wrote (P891)
            return kept + [{"file": str(destination / "dist"), "did": "not kept", "why": str(refused), "line": "not kept: %s — %s" % (destination / "dist", refused)}]
        kept += [{"file": str(destination / "dist"), "did": WROTE, "why": "this is what every check reads",
                  "line": "wrote %s — this is what every check reads" % (destination / "dist")}] + left
    return kept


def _left_alone(target, why):
    """The kept entry for a .tsx that is not touched."""
    return {"file": str(target), "did": LEFT_ALONE, "why": why, "line": "%s: %s (%s)" % (LEFT_ALONE, target, why)}


def _unfinished(source, target):
    """The kept entries for a board spark wrote and nobody changed, left alone because this build did not finish."""
    return [_left_alone(target, NOT_FINISHED)] + _compare_traces(target, source)


def _spark_wrote(target, recorded):
    """Whether `target` is a plain file whose bytes are `recorded`, the sha256 of what spark wrote. None (nothing recorded)
    and a link are no."""
    if recorded is None or target.is_symlink() or not target.is_file():
        return False
    try:
        return sha256_of(target) == recorded
    except OSError:
        return False


def _replaced(source, target, made, recorded):
    """
    The kept entries for a board spark wrote that nobody changed (P874): `unchanged` when this build made the same
    board. Else the new board is staged beside the target, the previous version is staged too, the board is swapped in,
    and only then the previous version is put in place, so a failure leaves both as they were. A failure of the file
    system is a `left alone` entry, and it removes the stages this run made.
    """
    if made == recorded:
        why = "spark wrote it and this build made the same board"
        return [{"file": str(target), "did": UNCHANGED, "why": why, "sha256": made, "line": "unchanged %s (this build made the same board)" % target}]
    board, previous, held, sentence = StagedFile(source, target.with_name(target.name + STAGE_SUFFIX)), PreviousVersionFiles(target.parent), None, WRITE_FAILED
    try:
        board.make()
        sentence = KEEP_FAILED
        held = previous.stage(target)
        sentence = WRITE_FAILED
        board.commit(target)
        kept = previous.commit(held)
    except OSError as refused:
        why = STAGE_IN_THE_WAY % refused.filename if isinstance(refused, StageTakenError) else sentence % refused
        return [_left_alone(target, why)] + _compare_traces(target, source)
    finally:
        board.remove()
        if held:
            held.remove()
    return [{"file": str(target), "did": REPLACED, "why": "spark wrote it and it was not changed since", "previous": str(kept),
             "sha256": made, "line": "replaced %s (the previous version is %s)" % (target, kept)}]


def _traces(text):
    """The traces of a board file as (from, to) in the order written, and how many it holds in a form spark does not
    read: a `<trace ` that is not `from="…" to="…"`, as a hand-kept board's ``from={`.Mcu > .${MCU.GND}`}``."""
    text = _COMMENT.sub("", text)
    read = _TRACE.findall(text)
    return read, len(_TRACE_TAG.findall(text)) - len(read)


def _compare_traces(kept_file, built_file):
    """
    The kept entry for a .tsx left alone whose traces are not this build's (P660), none when they are the same. A
    pin map that changed after the file was kept leaves it joining the old pins, and a person who wires from it or
    builds it by hand uses pins the firmware does not. A trace is its two ends, either way round; placement, comments
    and other attributes are not compared.
    """
    if not kept_file.is_file():
        return []
    try:
        kept, unread = _traces(kept_file.read_text(encoding="utf-8", errors="replace"))
        why = "%d trace(s) in it are in a form spark does not read" % unread if unread else None
    except OSError as unreadable:  # the file is left alone either way; what this run copies must not hang on it
        why = "it cannot be read: %s" % unreadable
    if why:
        return [{"file": str(kept_file), "did": TRACES_NOT_COMPARED, "why": why,
                 "line": "%s: %s (%s)" % (TRACES_NOT_COMPARED, kept_file, why)}]
    built, _ = _traces(built_file.read_text(encoding="utf-8", errors="replace"))
    kept_ends, built_ends = {frozenset(trace) for trace in kept}, {frozenset(trace) for trace in built}
    only_in_kept = ["%s to %s" % trace for trace in kept if frozenset(trace) not in built_ends]
    only_in_build = ["%s to %s" % trace for trace in built if frozenset(trace) not in kept_ends]
    if not only_in_kept and not only_in_build:
        return []
    why = ("it joins pins differently from the board this build made from the requirements, so do not wire or build "
           "from it: if you did not edit it, delete it to have it regenerated; if you did, carry this build's pins into it")
    return [{"file": str(kept_file), "did": TRACES_DIFFER, "why": why, "only_in_kept": only_in_kept,
             "only_in_build": only_in_build, "line": "%s: %s (%s)%s%s" % (
                 TRACES_DIFFER, kept_file, why, _show_traces("only in yours", only_in_kept),
                 _show_traces("only in this build", only_in_build))}]


def _show_traces(side, traces):
    """The indented lines that name one side's traces, TRACES_SHOWN of them and how many more."""
    lines = "".join("\n  %s: %s" % (side, trace) for trace in traces[:TRACES_SHOWN])
    more = len(traces) - TRACES_SHOWN
    return lines + ("\n  %s: %d more not shown" % (side, more) if more > 0 else "")


def _built(stages):
    """Whether the chain's build stage ended ok: a board that was not built, or that has problems, replaces no board."""
    return any(stage.name == BUILD.name and stage.status == OK for stage in stages)


def _kept(workdir, destination, recorded, finished):
    """`kept_into`, or one entry saying why nothing could be kept: the verdict is printed either way. It may replace a
    board spark wrote only when `recorded` (a requirements file is given) and the build record will be written, and `finished` (P874)."""
    try:
        return kept_into(workdir, destination, BuildRecordStore(destination).written_sha256() if recorded and _is_project(destination) else {}, finished)
    except OSError as refused:
        return [{"file": str(destination), "did": "not kept", "why": str(refused),
                 "line": "not kept: %s — %s" % (destination, refused)}]


def drop_an_older_build(destination, stages, kept=()):
    """An earlier dist/ this run did not write: left alone and named (P816), or named `not kept` (P1088), or removed for the board alone (P236)."""
    old, why = Path(destination) / "dist", why_not_built(stages, "board only: no board was built")
    if why is None or not old.is_dir() or str(old) in {entry["file"] for entry in kept}:
        return []
    if not skipped_the_build(stages):
        return [_left_alone(old, why + ", so it is an earlier build's, which every check reads")]
    shutil.rmtree(old)
    why = "board only: no board was built, and it described an earlier build"
    return [{"file": str(old), "did": "removed", "why": why, "line": "removed %s: %s" % (old, why)}]


def keep_breadboard(requirements, destination, stages=(), kept=None):
    """
    The breadboard sheet beside the kept board (P191, #143), and its drawn breadboard (P267), as kept entries {file, did,
    why, line}. Only from a build that finished in this run, which it records (dist/board/built-from.json) for breadboard.py
    to compare. An earlier build's sheet or drawing stays, named as an earlier build's (P1093); without `requirements` (the
    reference design) only that (P1114). A board-only build removes it (P236). A dist/ not copied writes no sheet (P1095).
    """
    sheet_path = Path(destination) / sheet.SHEET
    drawings = [(Path(destination) / renderer.FILE_NAME, renderer) for renderer in sheet.DRAWING_RENDERERS]
    why = why_not_built(stages, "board only: nothing to wire")
    why = why or (why_not_kept(destination, stages, kept) if kept is not None else None)  # P1095: a dist/ copy that failed
    why = why or (None if requirements else "spark's reference design has no breadboard sheet")  # P1114
    if why:
        named = [_left_from_earlier(sheet_path, "breadboard sheet", why, skipped_the_build(stages))] + [
            _left_from_earlier_drawing(path, renderer, why, skipped_the_build(stages)) for path, renderer in drawings]
        return [entry for entry in named if requirements or entry["did"] != "not written"]  # P1114: only what an earlier build left
    try:
        sheet.record_built_from(requirements, Path(destination) / sheet.BUILT_FROM)
        written = sheet.write(requirements, sheet_path, Path(destination) / sheet.CIRCUIT)
    except sheet.REFUSALS + (ValueError,) as stopped:
        return [{"file": str(sheet_path), "did": "not written", "why": str(stopped), "code": sheet.refusal_code(stopped) if isinstance(stopped, sheet.REFUSALS) else build_codes.STAGE_CRASHED,
                 "line": "no breadboard sheet: %s" % stopped}] + [
            _left_from_earlier_drawing(path, renderer, "the sheet was not written") for path, renderer in drawings]
    why = "the parts and how to wire them on a breadboard"
    kept = [{"file": str(written.sheet), "did": "wrote", "why": why, "line": "wrote %s — %s" % (written.sheet, why), **({"since": written.since} if written.since else {})}]
    kept += [{"file": str(path), "did": "wrote", "why": renderer.PURPOSE_MESSAGE, "line": "wrote %s — %s" % (path, renderer.PURPOSE_MESSAGE),
              **({"drawn_from": written.drawn_from} if written.drawn_from else {})} for path, renderer in written.drawings]
    kept += [not_written_entry(one) for one in written.not_written]
    kept += [{"file": str(written.sheet), "did": CHANGED, "code": change.code, "subject": change.name,  # what the person changes on the bench since the last sheet (P300)
              "color": change.color, "why": sheet.CHANGE_LIST.line(change),
              "line": "%s: %s" % (CHANGED, sheet.CHANGE_LIST.line(change))} for change in written.changes]
    kept += [{"file": str(Path(destination) / sheet.EDITABLE_DRAWING.FILE_NAME), "did": MOVE_NOT_KEPT,  # a part the person moved in breadboard.json that the build could not keep (P273)
              "subject": named.subject, "code": named.code, "why": named.why,
              "line": "move not kept: %s" % named.line} for named in written.not_kept]
    kept += [{"file": str(Path(destination) / sheet.EDITABLE_DRAWING.FILE_NAME), "did": DRAWING_DIFFERS,  # an end the drawing joins differently from the points (P279): the sheet's steps stand, the drawing is wrong
              "subject": differs.subject, "code": differs.code, "why": differs.why,
              "line": "%s: %s" % (DRAWING_DIFFERS, differs.why)} for differs in written.differs]
    return kept


def not_written_entry(one):
    """The kept entry of a drawing a build did not write (a `drawing.NotWritten`): `expected` is true for a code a retry
    gives again (`drawing.BY_DESIGN`): the agent does not retry, and for `not_drawn_yet` tells the person to wire it by
    hand from the sheet's steps (P691, P783). A part record that lacks the fact adds `record` and the filled `fix` (P945)."""
    known = one.record is not None and isinstance(one.code, codes.Code)
    return {"file": str(one.path), "did": "not written", "code": one.code, "subject": one.subject,
            "expected": one.code in drawing.BY_DESIGN, "why": one.why, "line": "no %s: %s" % (one.renderer.NOUN, one.why),
            **({"record": one.record, "fix": one.code.fix % one.record} if known else {})}


def why_not_built(stages, board_only_why):
    """Why no build finished in this run, or None when one did: the refused requirements file's own reason (P280),
    `board_only_why` for a board-only design, else that the build did not finish."""
    if any(stage.name == BUILD.name and stage.status == OK for stage in stages):
        return None
    refused = next((stage.detail for stage in stages if stage.name == REQUIREMENTS.name and stage.status != OK), None)
    if refused:
        return refused
    if skipped_the_build(stages):
        return board_only_why
    return "the build did not finish in this run"


def why_not_kept(destination, stages, kept):
    """Why this run kept no board of its own, or None: the page's three tabs (P271) and the sheet read only the circuit.json
    kept in this run, so a refused requirements file, a build that did not finish, a board-only one, or a dist/ that was
    not copied (P1095) leaves no page and no new sheet."""
    why = why_not_built(stages, "board only: nothing to draw")
    if why:
        return why
    if not any(entry["file"] == str(Path(destination) / "dist") and entry["did"] == WROTE for entry in kept):
        return "the build was not kept in this run"
    return None


#: Why the flow page was not written when reading the project's files for it failed: the class of the failure, no traceback.
FLOW_PAGE_FAILED = "the flow page could not be written (%s)"


class KeptPictureFiles:
    """
    Adapter: the schematic and the PCB that `tsci export` drew, as files of the project beside circuit.json (P828): the
    flow page reads them when it runs alone. An export that gave nothing removes the file an earlier build left, since
    that file describes another design. Only a project keeps them (`active`). A file that cannot be written or removed
    never stops the build or the page: it is one entry in `problems`, and the page shows that picture as not kept.
    """

    FILES = (tabbed_page.SCHEMATIC_FILE, tabbed_page.PCB_FILE)

    def __init__(self, destination, active=True):
        self.destination, self.active, self.problems = Path(destination), active, []

    def keep(self, exports):
        """Write each export's SVG to its file, or remove the file when the export gave none: `exports` are
        `tabbed_page.SvgExportResult`s in the order of `FILES`. They come back as the page may show them: one whose file
        could not be kept says why instead of its SVG."""
        if not self.active:
            return list(exports)
        return [self._keep_one(self.destination / name, export) for name, export in zip(self.FILES, exports)]

    def drop(self):
        """Remove both files: a run that drew no page leaves no picture of an earlier design."""
        for name in self.FILES if self.active else ():
            self._remove(self.destination / name)

    def _keep_one(self, path, export):
        if export.svg is None:
            self._remove(path)
            return export
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(export.svg, encoding="utf-8")
        except OSError as refused:
            return tabbed_page.SvgExportResult(None, self._problem(path, refused))
        return export

    def _remove(self, path):
        try:
            if path.exists():  # a path under a file is no path: it is not there
                path.unlink()
        except OSError as refused:
            self._problem(path, refused)

    def _problem(self, path, refused):
        """Note one file that could not be kept, as a kept entry; the sentence is what the page says of its picture."""
        why = "its file cannot be kept (%s)" % (refused.strerror or type(refused).__name__)
        self.problems.append({"file": str(path), "did": "not kept", "why": why, "line": "not kept: %s (%s)" % (path, why)})
        return why


def keep_tabbed_page(destination, stages, kept, exporter, flow_page=None):
    """
    The page beside the kept board (P271, #307): the breadboard picture the sheet's step just wrote, and tscircuit's
    schematic and PCB of the same kept circuit.json (also kept as files, P828), as one kept entry {file, did, why, line}. In a project, `flow_page`
    (P827; `flow_page(project, tabs)` gives the path and what it is for) writes the flow page with those three pictures; without it, or in a
    folder that is no project, the tabbed page. A page left from an earlier build is removed when this run cannot draw one,
    since it describes another board.
    """
    page = Path(destination) / tabbed_page.TabbedHtmlPage.FILE_NAME
    why = why_not_kept(destination, stages, kept)
    project = _is_project(destination)
    pictures = KeptPictureFiles(destination, project)
    if why:
        if not any(entry["file"] == str(Path(destination) / "dist") and entry["did"] in (LEFT_ALONE, NOT_KEPT) for entry in kept):  # P816: an earlier dist/ that stays keeps its pictures
            pictures.drop()
        kept.extend(pictures.problems)
        return _left_from_earlier(page, tabbed_page.TabbedHtmlPage.NOUN, why)
    exports = pictures.keep([exporter.export_svg(Path(destination) / sheet.CIRCUIT, form) for form in ("schematic-svg", "pcb-svg")])
    kept.extend(pictures.problems)
    tabs = [_breadboard_tab(destination, kept), tabbed_page.exported_tab("Schematic", exports[0]),
            tabbed_page.exported_tab("PCB", exports[1])]
    flow = flow_page if flow_page is not None and project else None
    why = tabbed_page.TabbedHtmlPage.PURPOSE_MESSAGE
    try:
        if flow is not None:
            page, why = flow(destination, tabs)
        else:
            title = tabbed_page.page_title(Path(destination).resolve().name)
            page.write_text(tabbed_page.TabbedHtmlPage().text(tabs, title=title), encoding="utf-8")
    except OSError as refused:
        return {"file": str(page), "did": "not written", "why": str(refused), "line": "no page: %s" % refused}
    except Exception as failed:  # noqa: BLE001  the flow page reads the project's files: whatever they hold, the build ends as it ends
        why = FLOW_PAGE_FAILED % type(failed).__name__
        return {"file": str(page), "did": "not written", "why": why, "line": "no page: %s" % why}
    return {"file": str(page), "did": "wrote", "why": why, "line": "wrote %s — %s" % (page, why)}


def _breadboard_tab(destination, kept):
    """The breadboard tab: the picture this run wrote, or why it did not."""
    picture = str(Path(destination) / svg_diagram.SvgBreadboardDiagram.FILE_NAME)
    entry = next((entry for entry in kept if entry["file"] == picture), None)
    if entry is not None and entry["did"] == WROTE:
        try:
            return tabbed_page.Tab("Breadboard", Path(picture).read_text(encoding="utf-8"), None)
        except (OSError, ValueError) as unread:
            return tabbed_page.Tab("Breadboard", None, "breadboard.svg cannot be read: %s" % unread)
    return tabbed_page.Tab("Breadboard", None, entry["why"] if entry else "the breadboard picture was not written")


def _left_from_earlier_drawing(path, renderer, why, remove=True):
    """`_left_from_earlier` for a drawing, except the one a person edits: breadboard.json is left in place when it holds
    parts, since it may hold their moves, which the next build that finishes keeps where they still fit (P273)."""
    if renderer is sheet.EDITABLE_DRAWING and path.exists() and sheet.holds_parts(path):
        return {"file": str(path), "did": "left alone", "why": "no %s: %s; it may hold your moves, which the next build "
                "keeps where they fit" % (renderer.NOUN, why),
                "line": "left alone: %s (it may hold your moves; no %s: %s)" % (path, renderer.NOUN, why)}
    return _left_from_earlier(path, renderer.NOUN, why, remove)


def _left_from_earlier(path, what, why, remove=True):
    """One kept entry for a file this run did not write: removed when an earlier build left it, left alone and named as an earlier build's when not `remove`, else not written."""
    if path.exists() and not remove:
        return _left_alone(path, why + ", so it is an earlier build's")  # P1093: the witness stays (D6)
    if path.exists():
        path.unlink()
        return {"file": str(path), "did": "removed", "why": why + ", and it described an earlier build",
                "line": "no %s: %s; removed %s, which described an earlier build" % (what, why, path)}
    return {"file": str(path), "did": "not written", "why": why, "line": "no %s: %s" % (what, why)}


def keep_pins(requirements, destination, finished):
    """
    The pin map the firmware imports, beside the kept board (P196, #155), as one kept entry {file, did, why, line}: what
    `assign_pins.py requirements.json --emit-pins` writes, from the same code, and from the requirements alone, so it
    needs no finished build. One spark wrote is rewritten, since it says not to edit it. When the pins cannot be placed it
    stays, named as from the earlier requirements (P1109), unless a build `finished`. Not spark's: left alone, as `board.tsx` is.
    """
    target = Path(destination) / PIN_MODULE
    ours = target.is_file() and target.read_bytes().startswith(pin_assigner.PIN_MODULE_HEADER.encode())
    if target.exists() and not ours:
        why = "spark did not write it; delete it to have it written"
        return {"file": str(target), "did": LEFT_ALONE, "why": why, "line": "%s: %s (%s)" % (LEFT_ALONE, target, why)}
    try:
        module = pin_assigner.pin_module_for(str(requirements))
    except PIN_MAP_REFUSALS as stopped:
        if ours:  # P1109: the firmware imports it; it stays beside the earlier dist/ and sheet, but not beside a new build (D6)
            return _left_from_earlier(target, "pin map", "%s; the pin map is from the earlier requirements" % stopped, finished)
        return {"file": str(target), "did": "not written", "why": str(stopped), "line": "no pin map: %s" % stopped}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(module.module)
    why, missing = "the pins the firmware imports", [envelope_item(each) for each in module.missing_facts]
    return dict({"file": str(target), "did": "wrote", "why": why, "line": "wrote %s — %s%s" % (target, why, "".join(
        "\n  missing fact: %s. %s" % (item["sentence"], item["fix"]) for item in missing))}, **{"missing_facts": missing} if missing else {})


def _kept_pins(requirements, destination, finished):
    """`keep_pins`, or one entry saying why the file system refused it: the verdict is printed either way."""
    try:
        return keep_pins(requirements, destination, finished)
    except OSError as refused:
        target = Path(destination) / PIN_MODULE
        return {"file": str(target), "did": "not written", "why": str(refused), "line": "no pin map: %s" % refused}


# --- MVP ---
#: Why the build record is kept: the kept entry's `why`.
BUILD_RECORD_WHY = "what this build was built from and how it ended, which flow.py reads"


def keep_build_record(destination, requirements, stages, kept, records=None):
    """
    The record of this build in the project's `.spark/build.json` (P825), as a list of one kept entry {file, did, why,
    line}: `wrote`, or `not kept` with the OSError. None is written, and the list is empty, when `destination` is no
    project folder itself (`board_records.project_root`): a `.spark/` folder would make it one. A could-not-run build is
    recorded too. `requirements` is named relative to the project when it is inside it, else by its whole path, and is None for the reference design (P1095); `kept` gives the
    pin map's missing facts. `records` is the BuildRecordStore a test gives.
    """
    destination = Path(destination)
    if not _is_project(destination):
        return []
    records = records or BuildRecordStore(destination)
    try:
        # each stage's code when it did not end ok (P977), which the flow's guide reads; never its detail, which can hold a path
        record = {"status": STATUS_FOR[verdict(stages)], "stages": [dict({"name": stage.name, "status": stage.status}, **({"code": stage.code} if stage.code else {})) for stage in stages],
                  "missing_facts": [item for entry in kept for item in entry.get("missing_facts", [])],
                  "requirements": requirements and _named_from(requirements, destination), "requirements_sha256": requirements and sha256_of(requirements),
                  WRITTEN_SHA256: _written_sha256(records, kept),
                  DIST_WRITTEN: str(destination / "dist") in {entry["file"] for entry in kept if entry["did"] == WROTE}}
        path = records.write(record)
    except OSError as refused:
        return [{"file": str(records.path), "did": "not kept", "why": str(refused), "line": "not kept: %s — %s" % (records.path, refused)}]
    return [{"file": str(path), "did": "wrote", "why": BUILD_RECORD_WHY, "line": "wrote %s — %s" % (path, BUILD_RECORD_WHY)}]


def _written_sha256(records, kept):
    """What the record holds of the files spark wrote (P874): the sha256 a `wrote`, `replaced` or `unchanged` entry carries, which
    is of the bytes spark made and never of the file on disk (a person may have saved since); else the record's earlier value,
    since a build that stopped before the board, or left it alone, still rewrites the record."""
    now = {Path(item["file"]).name: item["sha256"] for item in kept if item.get("sha256")}
    before = records.written_sha256()
    return {name: now.get(name, before.get(name)) for name in OWN_FILES if name in now or name in before}


def _is_project(destination):
    """Whether `destination` is a project folder itself (`board_records.project_root`)."""
    try:
        return board_records.project_root(destination) == Path(destination).resolve()
    except board_records.BoardError:
        return False


def _named_from(requirements, project):
    """The requirements file relative to the project when it is inside it, else its whole path. A path as typed is
    relative to the folder the build ran from, which a reader of the record does not know."""
    whole = requirements.resolve()
    try:
        return str(whole.relative_to(project.resolve()))
    except ValueError:
        return str(whole)
# --- end MVP ---


def simulation_dir(sim_dir, keep):
    """Where the simulation project is kept: `sim_dir` (--sim-dir), else DIR/sim under `keep` (--keep DIR; JB1, P116), else
    nowhere."""
    if sim_dir:
        return Path(sim_dir)
    return Path(keep) / "sim" if keep else None


# --- MVP ---
#: Value: what a build run asks to keep (P804): the requirements file as given (None for the reference design), the
#: folder --keep names and the folder --sim-dir names, each None when not given.
KeepAsked = namedtuple("KeepAsked", "requirements_file keep sim_dir")


def keep_all(stages, workdir, asked, exporter, flow_page=None):
    """
    What a build run keeps (P804), as kept entries {file, did, why, line}: the built board in `asked.keep` (`_kept`); the
    breadboard sheet (the reference design names an earlier one, P1114); with a requirements file the pin map; the build record (P1095); the simulation project in
    `simulation_dir`; and last the page (its tabs drawn by `exporter`; in a project the flow page `flow_page` writes, P827),
    since the flow page reads what the others kept. None when --keep was not given, or was given with no work
    folder and no requirements file that is there. Even then, a kept simulation project is one entry. With no work folder, a refused
    requirements file that is there still removes the page and names the pin map an earlier build left (P280, P1093, P1109); a missing one, which can be a typo,
    removes nothing. It removes no work folder: the caller does.
    """
    requirements_file, keep = asked.requirements_file, asked.keep
    keeps = keep and (workdir is not None or bool(requirements_file) and Path(requirements_file).is_file())
    kept = (_kept(workdir, keep, bool(requirements_file), _built(stages)) if workdir is not None else []) if keeps else None
    if kept is not None:  # P1095: the reference design (no requirements file) names an earlier dist/ and records its build too
        kept += keep_breadboard(Path(requirements_file) if requirements_file else None, Path(keep), stages, kept) + drop_an_older_build(Path(keep), stages, kept)
        kept += [_kept_pins(Path(requirements_file), Path(keep), _built(stages))] if requirements_file else []
        kept += keep_build_record(Path(keep), Path(requirements_file) if requirements_file else None, stages, kept)  # P825: what flow.py reads
    simulation_folder = simulation_dir(asked.sim_dir, keep)
    simulation = keep_simulation(workdir, simulation_folder, stages) if workdir is not None and simulation_folder else None
    if simulation is not None:
        kept = (kept or []) + [simulation]
    if keeps and requirements_file:
        kept.append(keep_tabbed_page(Path(keep), stages, kept, exporter or tabbed_page.TscircuitExport(None), flow_page))
    return kept
# --- end MVP ---


def keep_simulation(workdir, destination, stages):
    """
    The simulation project the last stage wrote, copied to `destination` as one kept entry {file, did, why, line}, or None
    when the stage wrote none. It is merged into what is there, so a person's scenarios stay. When the simulation stage is OK
    (it ran to the end, so `write_limits` has had its say), a limits note from an earlier build goes if this build wrote none.
    Any other outcome leaves the project's note, since the older diagram stays too.
    """
    if not (workdir / "sim").is_dir():
        return None
    try:
        simulated = any(stage.name == SIMULATION.name and stage.status == OK for stage in stages)
        if simulated and not (workdir / "sim" / sim_project.LIMITS_NOTE).is_file():  # the copy merges, so an older note would stay for the next run
            (Path(destination) / sim_project.LIMITS_NOTE).unlink(missing_ok=True)
        shutil.copytree(workdir / "sim", destination, dirs_exist_ok=True)
    except OSError as refused:  # shutil.Error is one
        return {"file": str(destination), "did": "not kept", "why": str(refused),
                "line": "not kept: %s — %s" % (destination, refused)}
    why = "the simulation project: diagram.json, wokwi.toml and the chips"
    return {"file": str(destination), "did": "wrote", "why": why, "line": "wrote %s — %s" % (destination, why)}
