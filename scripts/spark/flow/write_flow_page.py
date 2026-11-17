"""
The page of a project as an Operation on the core (P827, #1185): the flow's phases, each with a status word and a mark, and
the project's pictures, written as `page.html` in the project. `flow.py page` is its CLI. It reads the same phases as
`flow.py show` (`show_flow.read_flow`). A build with --keep writes the same page through `KeptFlowPage`, with the three
pictures it drew.
"""

from collections import namedtuple
from pathlib import Path

from spark.breadboard.drawing import SvgBreadboardDiagram
from spark.breadboard.tabbed_page import page_title
from spark.flow import flow_codes
from spark.flow.flow_page import FlowHtmlPage, FlowPage, Picture
from spark.flow.show_flow import privacy_for, read_flow
from spark.core.operation import COMMON_ARGUMENTS, READS, WRITES, Operation
from spark.core.outcomes import COULD_NOT_RUN
from spark.core.result import Finding, OperationResult

# --- MVP ---
#: The Finding of a page that cannot be written: its sentence, and what to do.
PAGE_SENTENCE = "%s was not written: %s"
PAGE_FIX = "make the project folder writable and run it again"
#: Value: what `write_page` wrote: the path, the masked phases and where the project stands.
Written = namedtuple("Written", "path phases stands_at")
#: The titles of the pictures, in the order of a build's three tabs.
BREADBOARD_TITLE, SCHEMATIC_TITLE, PCB_TITLE = "Breadboard", "Schematic", "PCB"


class FlowPageStore:
    """Adapter: writes the page into the project folder, and says the path it wrote."""

    def write(self, project, file_name, text):
        path = Path(project) / file_name
        path.write_text(text, encoding="utf-8")
        return path


def kept_pictures(project):
    """The pictures `flow.py page` shows, by itself: the breadboard drawing the project holds (breadboard.svg), or why there
    is none, and the schematic and the PCB, which only a build draws."""
    name = SvgBreadboardDiagram.FILE_NAME
    try:
        breadboard = Picture(BREADBOARD_TITLE, (Path(project) / name).read_text(encoding="utf-8"), None)
    except (OSError, ValueError):
        said = flow_codes.UNREADABLE_PICTURE if (Path(project) / name).exists() else flow_codes.NO_PICTURE_FILE
        breadboard = Picture(BREADBOARD_TITLE, None, said % name)
    return [breadboard] + [Picture(title, None, flow_codes.NOT_DRAWN_HERE) for title in (SCHEMATIC_TITLE, PCB_TITLE)]


def masked_page(page, privacy):
    """`page` with every text masked by `privacy`: the title, each phase, the pictures' SVG and reasons, the notes."""
    masked = privacy.masked
    pictures = [Picture(*masked(tuple(picture))) for picture in page.pictures]
    return FlowPage(masked(page.title), masked(page.phases), masked(page.stands_at), pictures, masked(page.notes))


def write_page(project, readers=None, pictures=None, renderer=None, store=None):
    """
    Read the flow of `project`, build its FlowPage, mask it, render it and write it: a Written. `pictures` is a function
    `project -> [Picture]` (None: `kept_pictures`), `store` a FlowPageStore. A `renderer` has `FILE_NAME`, `PURPOSE_MESSAGE`
    and `text(page)`: the page's phases are dicts, its pictures Pictures, and a renderer shows a phase through
    `flow_page.shown_phase`, which holds the tick guard. An OSError from the store is the caller's.
    """
    phases, stands_at = read_flow(project, readers)
    page = FlowPage(page_title(Path(project).resolve().name), [phase.to_dict() for phase in phases], stands_at,
                    (pictures or kept_pictures)(project), (flow_codes.BENCH_NOTE,))
    page = masked_page(page, privacy_for(project))
    renderer = renderer or FlowHtmlPage()
    path = (store or FlowPageStore()).write(project, renderer.FILE_NAME, renderer.text(page))
    return Written(path, page.phases, page.stands_at)


def write_kept_page(project, tabs):
    """(the path of the page written in `project`, what it is for): the page a build with --keep writes, with the pictures it
    drew (`tabs`: a title, an SVG or None, and why none). The build is handed this function, and `kept_files` imports
    nothing of the flow. An OSError is the caller's."""
    pictures = [Picture(title, svg, None if svg else flow_codes.NOT_DRAWN_BECAUSE % why) for title, svg, why in tabs]
    return write_page(project, pictures=lambda _project: pictures).path, FlowHtmlPage.PURPOSE_MESSAGE


class WriteFlowPage(Operation):
    """
    Operation: write the project's page. It answers the file (relative to the project), what it did, where the project
    stands and each phase's status. A page that cannot be written is one could-not-run Finding. The phases' own problems
    do not change its status: `flow.py show` reports those. `readers`, `pictures`, `renderer` and `store` are what a test
    swaps (None: the real ones).
    """

    name = "write-flow-page"
    summary = "write page.html in the project: each phase of the flow with a status word and a mark, and the project's pictures"
    arguments = (COMMON_ARGUMENTS["project"]._replace(help="the project folder (default: here)"), COMMON_ARGUMENTS["json"])
    effects = (READS, WRITES)
    data_keys = ("file", "did", "stands_at", "phases")
    privacy_for = staticmethod(privacy_for)

    def __init__(self, readers=None, pictures=None, renderer=None, store=None):
        self.readers, self.pictures, self.renderer, self.store = readers, pictures, renderer, store

    def run(self, project, *, outside):
        renderer = self.renderer or FlowHtmlPage()
        try:
            written = write_page(project, self.readers, self.pictures, renderer, self.store)
        except OSError as refused:
            said = PAGE_SENTENCE % (renderer.FILE_NAME, refused)
            return OperationResult(findings=[Finding(COULD_NOT_RUN, renderer.FILE_NAME, flow_codes.PAGE_NOT_WRITTEN, said, PAGE_FIX)],
                                   lines=[said])
        data = {"file": renderer.FILE_NAME, "did": "wrote", "stands_at": written.stands_at,
                "phases": [{"phase": phase["phase"], "status": phase["status"]} for phase in written.phases]}
        return OperationResult(data, lines=["wrote %s: %s" % (renderer.FILE_NAME, renderer.PURPOSE_MESSAGE)])
# --- end MVP ---
