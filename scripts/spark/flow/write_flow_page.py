"""
The page of a project as an Operation on the core (P827, #1185): the flow's phases, each with a status word and a mark, and
the project's pictures and its wiring (P828, #1186), written as `page.html` in the project. `flow.py page` is its CLI. It
draws the reading that `flow.py show` prints (`show_flow.reading_of`, P1060) with the pure `compose_page`. A build with
--keep writes the same page through `write_kept_page`, with the three pictures it drew.
"""

from collections import namedtuple
from pathlib import Path

from spark.breadboard import sheet, tabbed_page
from spark.breadboard.svg_diagram import SvgBreadboardDiagram
from spark.flow import flow_codes
from spark.flow.flow_page import FlowHtmlPage, FlowPage, PageWiring, Picture
from spark.flow.phase_readers import REQUIREMENTS_FILE
from spark.flow.published_page import ARTIFACT_PATTERN, PublishedPageStore
from spark.flow.show_flow import privacy_for, reading_of
from spark.firmware.project_secrets import ProjectSecrets
from spark.core import codes
from spark.core.operation import COMMON_ARGUMENTS, READS, WRITES, Argument, Operation
from spark.core.outcomes import COULD_NOT_RUN
from spark.records import store
from spark.core.result import Finding, OperationResult

# --- MVP ---
#: The Finding of a page that cannot be written: its sentence, and what to do.
PAGE_SENTENCE = "%s was not written: %s"
PAGE_FIX = "make the project folder writable and run it again"
#: The fix of a page whose `.part` is taken by a link, a folder or another writer (P1054): the folder is writable.
PART_FIX = "something else holds %s.part: remove it if it is not yours, and run it again"
#: The refusal of a page whose project holds a secrets file that cannot be read or parsed (P1060 D5), and its fix. It
#: names the file, never its text: a parse error's text holds the line, and the line the secret.
SECRETS_UNREADABLE = "firmware/ holds a secrets file that cannot be read or parsed (%s), so spark cannot mask its values"
SECRETS_FIX = "repair or remove that file in firmware/, then run flow.py page again"
#: What WriteFlowPage adds to the refusal: the page it did not write is not the page on disk.
OLD_PAGE = ". The page on disk is the old one"
#: The Finding of an --artifact that is no Artifact id: its sentence, and what to do.
ARTIFACT_SENTENCE = "--artifact is no Artifact id: an id is a UUID in lower case, as get_artifact answers it"
ARTIFACT_FIX = "give the id of the published page, the slug that publish_files or get_artifact answers"
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
    """Adapter: writes the page into the project folder, and says the path it wrote. It writes through the store's
    whole-file write (`store.replace_file`: `.part`, then a rename, P1035 PR 2), so a write that fails halfway leaves the
    old page whole, and an old page that is not UTF-8 is written over, as before."""

    def write(self, project, file_name, text):
        path = Path(project) / file_name
        store.replace_file(path, text)
        return path


class SecretsUnreadableError(OSError):
    """Error: the project holds a secrets file that cannot be read or parsed (P1060 D5), so `write_page` writes nothing: the
    page is published, and a value spark cannot read it cannot mask. An OSError, so that every writer that reports a page
    not written reports this one in its own words. Its text names the files (`names`) and holds nothing of them."""

    def __init__(self, names):
        super().__init__(SECRETS_UNREADABLE % ", ".join(names))
        self.names = tuple(names)


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


def masked_page(page, privacy, svg_privacy):
    """`page` with every text masked by `privacy`: the title, each phase, the pictures' titles and reasons, the notes, the
    wiring and the guide. A picture's SVG takes `svg_privacy`, the paths-only mask (P1060): a secret's value masked inside a
    drawing would break the drawing."""
    masked = privacy.masked
    pictures = [Picture(masked(picture.title), svg_privacy.masked(picture.svg), masked(picture.why_missing)) for picture in page.pictures]
    wiring = PageWiring(*masked(tuple(page.wiring))) if page.wiring else None
    return FlowPage(masked(page.title), masked(page.phases), masked(page.stands_at), pictures, masked(page.notes), wiring,
                    page.fingerprint, page.written, masked(page.guide))


def compose_page(reading, parts):
    """The FlowPage of `reading`, a FlowReading, and `parts`, its PageParts: the reading's title, its phases as dicts,
    where it stands, the pictures, the bench note, the wiring, the fingerprint, the newest change as `written` and the
    guide. Pure: it reads no file, so every fact on the page is one that `flow.py show` prints (D22, P1060)."""
    return FlowPage(reading.title, [phase.to_dict() for phase in reading.phases], reading.stands_at,
                    parts.pictures, (flow_codes.BENCH_NOTE,), parts.wiring, reading.fingerprint, reading.stamp["newest"], reading.guide)


def write_page(project, readers=None, parts=None, renderer=None, store=None):
    """
    Read the flow of `project` once (`reading_of`), compose its FlowPage, mask it, render it and write it: a Written.
    `parts` is a function `project -> PageParts` (None: `kept_parts`), `store` a FlowPageStore. A `renderer` has
    `FILE_NAME`, `PURPOSE_MESSAGE` and `text(page)`: the page's phases are dicts, its pictures Pictures, and a renderer
    shows a phase through `flow_page.shown_phase`, which holds the tick guard. An OSError from the store is the caller's.
    The texts take the mask of the project's secrets (P1060), the SVG and the rendered page the paths-only one. A secrets
    file that cannot be read or parsed raises SecretsUnreadableError before anything is read or written (D5).
    """
    secrets = ProjectSecrets.read(project)
    if secrets.unreadable:
        raise SecretsUnreadableError(secrets.unreadable)
    page = compose_page(reading_of(project, readers), (parts or kept_parts)(project))
    paths = privacy_for(project, secrets=())
    page = masked_page(page, privacy_for(project, secrets.values), paths)
    renderer = renderer or FlowHtmlPage()
    # masked again once rendered: the inline breadboard's parse turns a character reference (&#47;) into a path
    path = (store or FlowPageStore()).write(project, renderer.FILE_NAME, paths.masked(renderer.text(page)))
    return Written(path, page.phases, page.stands_at, page.fingerprint, page.guide)


def write_kept_page(project, tabs):
    """(the path of the page written in `project`, what it is for): the page a build with --keep writes, with the pictures it
    drew (`tabs`: a title, an SVG or None, and why none) and the wiring the project keeps. The build is handed this function, and `kept_files` imports
    nothing of the flow. An OSError is the caller's."""
    pictures = [Picture(title, svg, None if svg else flow_codes.NOT_DRAWN_BECAUSE % why) for title, svg, why in tabs]
    return write_page(project, parts=lambda _project: PageParts(pictures, kept_wiring(project))).path, FlowHtmlPage.PURPOSE_MESSAGE


def not_written(file_name, refused):
    """(the sentence, the fix) of a page that `refused` kept from being written: a secrets file that cannot be read (D5)
    names the old page on disk, a `.part` that something else holds (P1054) its own fix."""
    if isinstance(refused, SecretsUnreadableError):
        return PAGE_SENTENCE % (file_name, refused) + OLD_PAGE, SECRETS_FIX
    return PAGE_SENTENCE % (file_name, refused), PART_FIX % file_name if isinstance(refused, store.PartTakenError) else PAGE_FIX


class WriteFlowPage(Operation):
    """
    Operation: write the project's page. It answers the file (relative to the project), what it did, where the project
    stands, each phase's status, the flow's fingerprint (P829), the guide (P977) and the Artifact the page is published as
    (P829 PR 4: `--artifact` keeps its id in .spark/page.json first, through PublishedPageStore). A page that cannot be written is one could-not-run Finding. The phases' own problems
    do not change its status: `flow.py show` reports those. `readers`, `parts`, `renderer` and `store` are what a test
    swaps (None: the real ones).
    """

    name = "write-flow-page"
    summary = "Write page.html in the project: each phase of the flow with a status word and a mark, and the project's pictures (P827)."
    arguments = (COMMON_ARGUMENTS["project"]._replace(help="the project folder (default: here)"),
                 Argument(("--artifact",), "artifact", str, "the id of the Artifact the page is published as (P829): kept in "
                          ".spark/page.json, the id only, and answered as data.artifact by every later page", metavar="ID"),
                 COMMON_ARGUMENTS["json"])
    effects = (READS, WRITES)
    data_keys = ("file", "did", "stands_at", "phases", "fingerprint", "guide", "artifact")
    privacy_for = staticmethod(privacy_for)

    def __init__(self, readers=None, parts=None, renderer=None, store=None):
        self.readers, self.parts, self.renderer, self.store = readers, parts, renderer, store

    def run(self, project, artifact=None, *, outside):
        renderer = self.renderer or FlowHtmlPage()
        if artifact is not None and not ARTIFACT_PATTERN.fullmatch(artifact):
            return OperationResult(findings=[Finding.of(COULD_NOT_RUN, "--artifact", codes.BAD_ARGUMENT, ARTIFACT_SENTENCE, ARTIFACT_FIX)],
                                   lines=[ARTIFACT_SENTENCE])
        published = PublishedPageStore(project)
        try:
            if artifact is not None:
                published.write(artifact)
            written = write_page(project, self.readers, self.parts, renderer, self.store)
        except (OSError, UnicodeError) as refused:  # a text the file cannot hold (a lone surrogate) is a page not written
            said, fix = not_written(renderer.FILE_NAME, refused)
            return OperationResult(findings=[Finding(COULD_NOT_RUN, renderer.FILE_NAME, flow_codes.PAGE_NOT_WRITTEN, said, fix)],
                                   lines=[said])
        data = {"file": renderer.FILE_NAME, "did": "wrote", "stands_at": written.stands_at,
                "phases": [{"phase": phase["phase"], "status": phase["status"]} for phase in written.phases],
                "fingerprint": written.fingerprint, "guide": written.guide, "artifact": published.read()}
        return OperationResult(data, lines=["wrote %s: %s" % (renderer.FILE_NAME, renderer.PURPOSE_MESSAGE)])
# --- end MVP ---
