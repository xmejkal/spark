"""
The files `check_spine.py --keep DIR` writes into DIR, and what an earlier build left there (P705): the built board,
the breadboard sheet and its drawings, the page, the pin map and the simulation project, each a kept entry {file, did,
why, line}. One meaning of `kept_`: what a run keeps between runs, as `kept_moves`' moves are.
"""

import shutil
from pathlib import Path

from spark.build import build_codes
from spark.breadboard import drawing, sheet, tabbed_page
from spark.design import loader
from spark.design import pin_assigner
from spark.firmware import sim_project
from spark.records import store

from spark.core.outcomes import OK, SKIPPED
from spark.core.result import envelope_item

#: Where --keep puts the pin map, the path every document gives `--emit-pins` (P196).
PIN_MODULE = Path("firmware") / "pins.py"
#: What stops the pin map from being written: no pin can be placed, or the design, the store or a file cannot be read.
PIN_MAP_REFUSALS = (pin_assigner.ImpossibleError, loader.DesignError, store.StoreError, OSError, ValueError)

#: The stage that reads the requirements file; its detail is why a refused file built nothing (P280).
REQUIREMENTS_STAGE = "requirements"
#: The `did` of a kept entry for a part the person moved in breadboard.json that the build could not keep (P273).
MOVE_NOT_KEPT = "move not kept"
#: The `did` of a kept entry for one thing a rebuild asks a person to change on the bench (P300).
CHANGED = "changed"
#: The `did` of a kept entry for one end the drawn breadboard joins differently from circuit.json's points (P279).
DRAWING_DIFFERS = "drawing differs"


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


def kept_into(workdir, destination):
    """
    Put the built board where a person — and every check — will look for it.

    The chain builds in a temp directory and deletes it, which is right for a check and wrong for
    the one command a stranger is told to run: after `/spark:build` their project held only
    `requirements.json`, so `check_all --project .` answered "not asked for" and the word
    **checked** was unreachable from the documented path. `--keep` used to print the temp path
    instead, which is not a place anyone looks, and was documented nowhere (backlog P51).

    `dist/` is pure build output and is replaced. A `.tsx` file is NOT: `board.tsx` is the thing a
    person edits — the smart bin's is hand-maintained — so an existing one is left alone and
    named. Delete it to have it regenerated. One behaviour, no flag to get it wrong with.

    Each file is {file, did, why, line}: `did` is `wrote` or `left alone`, and `line` what stderr says. With --json the
    report carries the rest under `kept` (P124, #58), so an agent reads what a person reads.
    """
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    kept = []
    for source in sorted(workdir.glob("*.tsx")):
        target = destination / source.name
        if target.exists():
            kept.append({"file": str(target), "did": "left alone", "why": "delete it to have it regenerated",
                         "line": "left alone: %s (delete it to have it regenerated)" % target})
        else:
            shutil.copy2(source, target)
            kept.append({"file": str(target), "did": "wrote", "why": None, "line": "wrote %s" % target})
    built = workdir / "dist"
    if built.is_dir():
        shutil.copytree(built, destination / "dist", dirs_exist_ok=True)
        kept.append({"file": str(destination / "dist"), "did": "wrote", "why": "this is what every check reads",
                     "line": "wrote %s — this is what every check reads" % (destination / "dist")})
    return kept


def _kept(workdir, destination):
    """`kept_into`, or one entry saying why nothing could be kept: the verdict is printed either way."""
    try:
        return kept_into(workdir, destination)
    except OSError as refused:
        return [{"file": str(destination), "did": "not kept", "why": str(refused),
                 "line": "not kept: %s — %s" % (destination, refused)}]


def drop_an_older_build(destination, stages):
    """
    For the board alone (P236): an earlier build's `dist/` describes another board, and every check reads it, so it
    is removed and said, as the breadboard sheet is. Returns the kept entries, none when there is nothing to remove.
    """
    old = Path(destination) / "dist"
    if not any(stage.status == SKIPPED for stage in stages) or not old.is_dir():
        return []
    shutil.rmtree(old)
    why = "board only: no board was built, and it described an earlier build"
    return [{"file": str(old), "did": "removed", "why": why, "line": "removed %s: %s" % (old, why)}]


def keep_breadboard(requirements, destination, stages=()):
    """
    The breadboard sheet beside the kept board (P191, #143), and its drawn breadboard (P267), as kept entries {file,
    did, why, line}. Only from a build that finished in this run, which it records (dist/board/built-from.json) for
    breadboard.py to compare; a sheet or a drawing left from an earlier build is removed, since it describes another
    board.
    """
    sheet_path = Path(destination) / sheet.SHEET
    drawings = [(Path(destination) / renderer.FILE_NAME, renderer) for renderer in sheet.DRAWING_RENDERERS]
    why = why_not_built(stages, "board only: nothing to wire")
    if why:
        return [_left_from_earlier(sheet_path, "breadboard sheet", why)] + [
            _left_from_earlier_drawing(path, renderer, why) for path, renderer in drawings]
    try:
        sheet.record_built_from(requirements, Path(destination) / sheet.BUILT_FROM)
        written = sheet.write(requirements, sheet_path, Path(destination) / sheet.CIRCUIT)
    except sheet.REFUSALS + (ValueError,) as stopped:
        return [{"file": str(sheet_path), "did": "not written", "why": str(stopped), "code": sheet.refusal_code(stopped) if isinstance(stopped, sheet.REFUSALS) else build_codes.STAGE_CRASHED,
                 "line": "no breadboard sheet: %s" % stopped}] + [
            _left_from_earlier_drawing(path, renderer, "the sheet was not written") for path, renderer in drawings]
    why = "the parts and how to wire them on a breadboard"
    kept = [{"file": str(written.sheet), "did": "wrote", "why": why, "line": "wrote %s — %s" % (written.sheet, why)}]
    kept += [{"file": str(path), "did": "wrote", "why": renderer.PURPOSE_MESSAGE, "line": "wrote %s — %s" % (path, renderer.PURPOSE_MESSAGE),
              **({"drawn_from": written.drawn_from} if written.drawn_from else {})} for path, renderer in written.drawings]
    kept += [{"file": str(one.path), "did": "not written", "code": one.code, "subject": one.subject,
              "expected": one.code in drawing.BY_DESIGN, "why": one.why,
              "line": "no %s: %s" % (one.renderer.NOUN, one.why)} for one in written.not_written]
    # what the person changes on the bench since the last sheet (P300)
    kept += [{"file": str(written.sheet), "did": CHANGED, "code": change.code, "subject": change.name,
              "color": change.color, "why": sheet.CHANGE_LIST.line(change),
              "line": "%s: %s" % (CHANGED, sheet.CHANGE_LIST.line(change))} for change in written.changes]
    # a part the person moved in breadboard.json that the build could not keep (P273)
    kept += [{"file": str(Path(destination) / sheet.EDITABLE_DRAWING.FILE_NAME), "did": MOVE_NOT_KEPT,
              "subject": named.subject, "code": named.code, "why": named.why,
              "line": "move not kept: %s" % named.line} for named in written.not_kept]
    # an end the drawing joins differently from the points (P279): the sheet's steps stand, the drawing is wrong
    kept += [{"file": str(Path(destination) / sheet.EDITABLE_DRAWING.FILE_NAME), "did": DRAWING_DIFFERS,
              "subject": differs.subject, "code": differs.code, "why": differs.why,
              "line": "%s: %s" % (DRAWING_DIFFERS, differs.why)} for differs in written.differs]
    return kept


def why_not_built(stages, board_only_why):
    """Why no build finished in this run, or None when one did: the refused requirements file's own reason (P280),
    `board_only_why` for a board-only design, else that the build did not finish."""
    if any(stage.name == "build" and stage.status == OK for stage in stages):
        return None
    refused = next((stage.detail for stage in stages if stage.name == REQUIREMENTS_STAGE and stage.status != OK), None)
    if refused:
        return refused
    if any(stage.status == SKIPPED for stage in stages):
        return board_only_why
    return "the build did not finish in this run"


def why_no_page(destination, stages, kept):
    """Why the page (P271) cannot be drawn in this run, or None: its three tabs read the one circuit.json kept in this
    run, so a refused requirements file, a build that did not finish, a board-only one, or a dist/ that was not copied
    leaves no page."""
    why = why_not_built(stages, "board only: nothing to draw")
    if why:
        return why
    if not any(entry["file"] == str(Path(destination) / "dist") and entry["did"] == "wrote" for entry in kept):
        return "the build was not kept in this run"
    return None


def keep_tabbed_page(destination, stages, kept, exporter):
    """
    The page beside the kept board (P271, #307): the breadboard picture the sheet's step just wrote, and tscircuit's
    schematic and PCB of the same kept circuit.json, as one kept entry {file, did, why, line}. A page left from an
    earlier build is removed when this run cannot draw one, since it describes another board.
    """
    page = Path(destination) / tabbed_page.TabbedHtmlPage.FILE_NAME
    why = why_no_page(destination, stages, kept)
    if why:
        return _left_from_earlier(page, tabbed_page.TabbedHtmlPage.NOUN, why)
    circuit = Path(destination) / sheet.CIRCUIT
    tabs = [_breadboard_tab(destination, kept),
            tabbed_page.exported_tab("Schematic", exporter.export_svg(circuit, "schematic-svg")),
            tabbed_page.exported_tab("PCB", exporter.export_svg(circuit, "pcb-svg"))]
    try:
        title = tabbed_page.page_title(Path(destination).resolve().name)
        page.write_text(tabbed_page.TabbedHtmlPage().text(tabs, title=title), encoding="utf-8")
    except OSError as refused:
        return {"file": str(page), "did": "not written", "why": str(refused), "line": "no page: %s" % refused}
    why = tabbed_page.TabbedHtmlPage.PURPOSE_MESSAGE
    return {"file": str(page), "did": "wrote", "why": why, "line": "wrote %s — %s" % (page, why)}


def _breadboard_tab(destination, kept):
    """The breadboard tab: the picture this run wrote, or why it did not."""
    picture = str(Path(destination) / drawing.SvgBreadboardDiagram.FILE_NAME)
    entry = next((entry for entry in kept if entry["file"] == picture), None)
    if entry is not None and entry["did"] == "wrote":
        try:
            return tabbed_page.Tab("Breadboard", Path(picture).read_text(encoding="utf-8"), None)
        except (OSError, ValueError) as unread:
            return tabbed_page.Tab("Breadboard", None, "breadboard.svg cannot be read: %s" % unread)
    return tabbed_page.Tab("Breadboard", None, entry["why"] if entry else "the breadboard picture was not written")


def _left_from_earlier_drawing(path, renderer, why):
    """`_left_from_earlier` for a drawing, except the one a person edits: breadboard.json is left in place when it holds
    parts, since it may hold their moves, which the next build that finishes keeps where they still fit (P273)."""
    if renderer is sheet.EDITABLE_DRAWING and path.exists() and sheet.holds_parts(path):
        return {"file": str(path), "did": "left alone", "why": "no %s: %s; it may hold your moves, which the next build "
                "keeps where they fit" % (renderer.NOUN, why),
                "line": "left alone: %s (it may hold your moves; no %s: %s)" % (path, renderer.NOUN, why)}
    return _left_from_earlier(path, renderer.NOUN, why)


def _left_from_earlier(path, what, why):
    """One kept entry for a file this run did not write: removed when an earlier build left it, else not written."""
    if path.exists():
        path.unlink()
        return {"file": str(path), "did": "removed", "why": why + ", and it described an earlier build",
                "line": "no %s: %s; removed %s, which described an earlier build" % (what, why, path)}
    return {"file": str(path), "did": "not written", "why": why, "line": "no %s: %s" % (what, why)}


def keep_pins(requirements, destination):
    """
    The pin map the firmware imports, beside the kept board (P196, #155), as one kept entry {file, did, why, line}: what
    `assign_pins.py requirements.json --emit-pins` writes, from the same code, and from the requirements alone, so it
    needs no finished build. One spark wrote is rewritten, since it says not to edit it, and is removed when the pins
    cannot be placed: it describes another design. A `pins.py` spark did not write is left alone, as `board.tsx` is.
    """
    target = Path(destination) / PIN_MODULE
    ours = target.is_file() and target.read_bytes().startswith(pin_assigner.PIN_MODULE_HEADER.encode())
    if target.exists() and not ours:
        why = "spark did not write it; delete it to have it written"
        return {"file": str(target), "did": "left alone", "why": why, "line": "left alone: %s (%s)" % (target, why)}
    try:
        module = pin_assigner.pin_module_for(str(requirements))
    except PIN_MAP_REFUSALS as stopped:
        if ours:
            target.unlink()
            return {"file": str(target), "did": "removed", "why": "%s, and it described an earlier design" % stopped,
                    "line": "no pin map: %s; removed %s, which described an earlier design" % (stopped, target)}
        return {"file": str(target), "did": "not written", "why": str(stopped), "line": "no pin map: %s" % stopped}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(module.module)
    why, missing = "the pins the firmware imports", [envelope_item(each) for each in module.missing_facts]
    return dict({"file": str(target), "did": "wrote", "why": why, "line": "wrote %s — %s%s" % (target, why, "".join(
        "\n  missing fact: %s. %s" % (item["sentence"], item["fix"]) for item in missing))}, **{"missing_facts": missing} if missing else {})


def _kept_pins(requirements, destination):
    """`keep_pins`, or one entry saying why the file system refused it: the verdict is printed either way."""
    try:
        return keep_pins(requirements, destination)
    except OSError as refused:
        target = Path(destination) / PIN_MODULE
        return {"file": str(target), "did": "not written", "why": str(refused), "line": "no pin map: %s" % refused}


def simulation_dir(args):
    """Where the simulation project is kept: --sim-dir, else DIR/sim under --keep DIR (JB1, P116), else nowhere."""
    if getattr(args, "sim_dir", None):
        return Path(args.sim_dir)
    return Path(args.keep) / "sim" if getattr(args, "keep", None) else None


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
        simulated = any(stage.name == "simulation" and stage.status == OK for stage in stages)
        if simulated and not (workdir / "sim" / sim_project.LIMITS_NOTE).is_file():  # the copy merges, so an older note would stay for the next run
            (Path(destination) / sim_project.LIMITS_NOTE).unlink(missing_ok=True)
        shutil.copytree(workdir / "sim", destination, dirs_exist_ok=True)
    except OSError as refused:  # shutil.Error is one
        return {"file": str(destination), "did": "not kept", "why": str(refused),
                "line": "not kept: %s — %s" % (destination, refused)}
    why = "the simulation project: diagram.json, wokwi.toml and the chips"
    return {"file": str(destination), "did": "wrote", "why": why, "line": "wrote %s — %s" % (destination, why)}
