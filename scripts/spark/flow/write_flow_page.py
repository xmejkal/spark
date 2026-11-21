"""
The page of a project as an Operation on the core (P827, #1185): the flow's phases, each with a status word and a mark, and
the project's pictures and its wiring (P828, #1186), written as `page.html` in the project. `flow.py page` is its CLI. It
reads the same phases as `flow.py show` (`show_flow.read_flow`). A build with --keep writes the same page through
`write_kept_page`, with the three pictures it drew.
"""

import datetime
from collections import namedtuple
from pathlib import Path

from spark.breadboard import sheet, tabbed_page
from spark.breadboard.svg_diagram import SvgBreadboardDiagram
from spark.breadboard.tabbed_page import page_title
from spark.flow import flow_codes
from spark.flow.fingerprint import FILES, fingerprint_of
from spark.flow.flow_page import FlowHtmlPage, FlowPage, PageWiring, Picture
from spark.flow.phase_readers import REQUIREMENTS_FILE
from spark.flow.guide import guide_of
from spark.flow.show_flow import privacy_for, read_flow
from spark.core.operation import COMMON_ARGUMENTS, READS, WRITES, Operation
from spark.core.outcomes import COULD_NOT_RUN
from spark.core.result import Finding, OperationResult
from spark.core.zone_time import stamp

# --- MVP ---
#: The Finding of a page that cannot be written: its sentence, and what to do.
PAGE_SENTENCE = "%s was not written: %s"
PAGE_FIX = "make the project folder writable and run it again"
#: Value: what `write_page` wrote: the path, the masked phases, where the project stands, the flow's fingerprint and the
#: masked guide (P977).
Written = namedtuple("Written", "path phases stands_at fingerprint guide")
#: The titles of the pictures, in the order of a build's three tabs.
BREADBOARD_TITLE, SCHEMATIC_TITLE, PCB_TITLE = flow_codes.BREADBOARD_TITLE, "Schematic", "PCB"
#: Value: what a page shows of the project besides its phases: its pictures and its wiring (a PageWiring or None).
PageParts = namedtuple("PageParts", "pictures wiring")
#: Value: one picture the project keeps as a file: its title, the file (in the project) and what to say when it is not there.
KeptPicture = namedtuple("KeptPicture", "title file missing")
#: The pictures a project keeps, in the order of a build's three tabs: the sheet's step writes the first, the build's keep
#: step the other two (`tabbed_page.SCHEMATIC_FILE` and `PCB_FILE`).
KEPT_PICTURES = (KeptPicture(BREADBOARD_TITLE, Path(SvgBreadboardDiagram.FILE_NAME),
                             flow_codes.NO_PICTURE_FILE % SvgBreadboardDiagram.FILE_NAME),
                 KeptPicture(SCHEMATIC_TITLE, tabbed_page.SCHEMATIC_FILE, flow_codes.NOT_DRAWN_HERE),
                 KeptPicture(PCB_TITLE, tabbed_page.PCB_FILE, flow_codes.NOT_DRAWN_HERE))


class FlowPageStore:
    """Adapter: writes the page into the project folder, and says the path it wrote."""

    def write(self, project, file_name, text):
        path = Path(project) / file_name
        path.write_text(text, encoding="utf-8")
        return path


def kept_pictures(project):
    """The pictures `flow.py page` shows, by itself: each one the project holds as a file (`KEPT_PICTURES`), or why it is not
    there. The schematic and the PCB are files only once a build has kept them."""
    pictures = []
    for title, name, missing in KEPT_PICTURES:
        path = Path(project) / name
        try:
            pictures.append(Picture(title, path.read_text(encoding="utf-8"), None))
        except (OSError, ValueError):
            pictures.append(Picture(title, None, flow_codes.UNREADABLE_PICTURE % path.name if path.exists() else missing))
    return pictures


def kept_wiring(project):
    """The PageWiring of a built project, or why there is none: a refusal of the sheet in its own words, anything else (a
    broken circuit.json) in one fixed sentence. None when the project has no requirements.json: there is nothing to wire."""
    requirements = Path(project) / REQUIREMENTS_FILE
    if not requirements.is_file():
        return None
    try:
        data = sheet.wiring_data(requirements)
    except Exception as stopped:  # noqa: BLE001  a circuit.json can hold anything: whatever it raises, the page is written
        return PageWiring([], [], [], str(stopped) if isinstance(stopped, sheet.REFUSALS) else flow_codes.WIRING_UNREADABLE)
    return PageWiring([(step.number, step.words) for step in data.steps], [item._asdict() for item in data.before_power.items],
                      list(data.before_power.records), None)


def kept_parts(project):
    """The PageParts of `project`: its kept pictures and its wiring."""
    return PageParts(kept_pictures(project), kept_wiring(project))


def masked_page(page, privacy):
    """`page` with every text masked by `privacy`: the title, each phase, the pictures' SVG and reasons, the notes, the wiring."""
    masked = privacy.masked
    pictures = [Picture(*masked(tuple(picture))) for picture in page.pictures]
    wiring = PageWiring(*masked(tuple(page.wiring))) if page.wiring else None
    return FlowPage(masked(page.title), masked(page.phases), masked(page.stands_at), pictures, masked(page.notes), wiring,
                    page.fingerprint, page.written, masked(page.guide))


def newest_change(project):
    """The newest change time of the fingerprint's files in `project`, in the machine's zone (`zone_time.stamp`), or None
    when none is there. Python writes it, so the page stays the same bytes for the same flow (P829)."""
    times = [path.stat().st_mtime for path in (Path(project) / name for name in FILES) if path.is_file()]
    return stamp(datetime.datetime.fromtimestamp(max(times))) if times else None


def write_page(project, readers=None, parts=None, renderer=None, store=None):
    """
    Read the flow of `project`, build its FlowPage, mask it, render it and write it: a Written. `parts` is a function
    `project -> PageParts` (None: `kept_parts`), `store` a FlowPageStore. A `renderer` has `FILE_NAME`, `PURPOSE_MESSAGE`
    and `text(page)`: the page's phases are dicts, its pictures Pictures, and a renderer shows a phase through
    `flow_page.shown_phase`, which holds the tick guard. An OSError from the store is the caller's.
    """
    phases, stands_at = read_flow(project, readers)
    shown = (parts or kept_parts)(project)
    guide = guide_of(project, phases)  # once: the page draws it and the answer holds it
    page = FlowPage(page_title(Path(project).resolve().name), [phase.to_dict() for phase in phases], stands_at,
                    shown.pictures, (flow_codes.BENCH_NOTE,), shown.wiring, fingerprint_of(project, phases), newest_change(project), guide)
    privacy = privacy_for(project)
    page = masked_page(page, privacy)
    renderer = renderer or FlowHtmlPage()
    # masked again once rendered: the inline breadboard's parse turns a character reference (&#47;) into a path
    path = (store or FlowPageStore()).write(project, renderer.FILE_NAME, privacy.masked(renderer.text(page)))
    return Written(path, page.phases, page.stands_at, page.fingerprint, page.guide)


def write_kept_page(project, tabs):
    """(the path of the page written in `project`, what it is for): the page a build with --keep writes, with the pictures it
    drew (`tabs`: a title, an SVG or None, and why none) and the wiring the project keeps. The build is handed this function, and `kept_files` imports
    nothing of the flow. An OSError is the caller's."""
    pictures = [Picture(title, svg, None if svg else flow_codes.NOT_DRAWN_BECAUSE % why) for title, svg, why in tabs]
    return write_page(project, parts=lambda _project: PageParts(pictures, kept_wiring(project))).path, FlowHtmlPage.PURPOSE_MESSAGE


class WriteFlowPage(Operation):
    """
    Operation: write the project's page. It answers the file (relative to the project), what it did, where the project
    stands, each phase's status, the flow's fingerprint (P829) and the guide (P977). A page that cannot be written is one could-not-run Finding. The phases' own problems
    do not change its status: `flow.py show` reports those. `readers`, `parts`, `renderer` and `store` are what a test
    swaps (None: the real ones).
    """

    name = "write-flow-page"
    summary = "Write page.html in the project: each phase of the flow with a status word and a mark, and the project's pictures (P827)."
    arguments = (COMMON_ARGUMENTS["project"]._replace(help="the project folder (default: here)"), COMMON_ARGUMENTS["json"])
    effects = (READS, WRITES)
    data_keys = ("file", "did", "stands_at", "phases", "fingerprint", "guide")
    privacy_for = staticmethod(privacy_for)

    def __init__(self, readers=None, parts=None, renderer=None, store=None):
        self.readers, self.parts, self.renderer, self.store = readers, parts, renderer, store

    def run(self, project, *, outside):
        renderer = self.renderer or FlowHtmlPage()
        try:
            written = write_page(project, self.readers, self.parts, renderer, self.store)
        except (OSError, UnicodeError) as refused:  # a text the file cannot hold (a lone surrogate) is a page not written
            said = PAGE_SENTENCE % (renderer.FILE_NAME, refused)
            return OperationResult(findings=[Finding(COULD_NOT_RUN, renderer.FILE_NAME, flow_codes.PAGE_NOT_WRITTEN, said, PAGE_FIX)],
                                   lines=[said])
        data = {"file": renderer.FILE_NAME, "did": "wrote", "stands_at": written.stands_at,
                "phases": [{"phase": phase["phase"], "status": phase["status"]} for phase in written.phases],
                "fingerprint": written.fingerprint, "guide": written.guide}
        return OperationResult(data, lines=["wrote %s: %s" % (renderer.FILE_NAME, renderer.PURPOSE_MESSAGE)])
# --- end MVP ---
