"""
The page's request as an Operation on the core (P829, #1187): `flow.py run-request` reads `.spark/page-request.json`, which
`/spark:page` writes from the page's database row, deletes it at once and runs the step it names, a pick, the parts list
or the build, only when spark offers that key now and the page was read at the project's fingerprint now. The values of
the step come from spark's own offer key, never from the request. A refusal runs nothing and still answers.
"""

import json
import re
from collections import namedtuple
from pathlib import Path

from spark.build.build_board import BuildBoard
from spark.core.cli import run_operation
from spark.core.operation import COMMON_ARGUMENTS, READS, RUNS, WRITES, Operation
from spark.core.outcomes import COULD_NOT_RUN, OK
from spark.core.result import Finding, OperationResult
from spark.design.pick_parts import NO_PASSED_OVER, PickParts
from spark.design.write_requirements import WriteRequirements
from spark.flow import flow_codes, request_codes
from spark.flow.fingerprint import SHORT, fingerprint_of
from spark.flow.guide import stops_only_for_no_model
from spark.flow.phase_readers import MARKS, REQUIREMENTS_FILE
from spark.flow.show_flow import privacy_for, read_flow

# --- MVP ---
#: The request file, in the project: one request, which `/spark:page` writes and this Operation deletes.
REQUEST_FILE = Path(".spark") / "page-request.json"
#: An id as the page writes it (`crypto.randomUUID()`), and `seen`, the first SHORT hex digits of the fingerprint.
ID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
SEEN_PATTERN = re.compile(r"^[0-9a-f]{12}$")
#: The kinds of offer that are asked in the chat, never from the page: a need's drop.
IN_CHAT = (flow_codes.NEEDS_DROP,)
#: Value: one request, as the file holds it: the page's id, the offer's key and the fingerprint's first digits the page
#: was read at. A field the file lacks is None; the page's `at` is its own, and spark does not read it.
PageRequest = namedtuple("PageRequest", "id key seen")
#: The line of a step that ran: its offer's label and its status. A refusal's line is its code's meaning.
RAN_LINE = "ran %s: %s"


def pick_values(project, key):
    """The values of the pick `key` (`pick:<need>:<id or entry>`) names: that one pick, no reasons, no dry run."""
    _, need, pick = key.split(":", 2)
    return {"project_and_picks": [str(project), "%s=%s" % (need, pick)], "passed_over": NO_PASSED_OVER, "dry_run": False}


def requirements_values(project, key):
    """The values of the parts list: the project's, no dry run and no replies, so nothing spark wrote is removed."""
    return {"project": str(project), "dry_run": False, "replies": None}


def build_values(project, key):
    """The values of the build: the project's requirements.json, kept in the project, its simulation project in sim/."""
    return {"requirements": str(Path(project) / REQUIREMENTS_FILE),
            "keep": project,
            "sim_dir": None, "firmware": None}


#: Value: the Operation a kind of offer runs and the function `(project, key) -> values` that gives its values.
KindRun = namedtuple("KindRun", "operation values")
#: The kinds the page may ask for, each with its run (P829): a pick, the parts list and the build.
KIND_RUNS = {flow_codes.PICK: KindRun(PickParts, pick_values),
             flow_codes.WRITE_REQUIREMENTS: KindRun(WriteRequirements, requirements_values),
             flow_codes.BUILD_BOARD: KindRun(BuildBoard, build_values)}


def request_file_of(project):
    return Path(project) / REQUEST_FILE


def read_request(project):
    """The PageRequest of `project`, or None when there is no regular file (a folder is left as it is and never read), it
    is no JSON object, or it cannot be deleted. The file is deleted at once, read or not, so one request runs once at
    most: one the folder will not let go could run again, so it is None."""
    path = request_file_of(project)
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        text = None
    try:
        path.unlink()
    except OSError:
        return None
    try:
        held = json.loads(text) if text is not None else None
    except ValueError:
        held = None
    return PageRequest(*(held.get(field) for field in PageRequest._fields)) if isinstance(held, dict) else None


def id_of(request):
    """The request's id when it is one the page writes, else None."""
    return request.id if request and isinstance(request.id, str) and ID_PATTERN.fullmatch(request.id) else None


def key_of(request):
    """The request's key when it is text, else None."""
    return request.key if request and isinstance(request.key, str) and request.key else None


def kind_of(key):
    """The kind of an offer's key: the word before its first colon."""
    return key.split(":", 2)[0]


def refusal_of(request, offered, fingerprint):
    """The code that refuses `request`, or None when it may run: it cannot be read, its kind is asked in the chat, its `seen`
    is not `fingerprint` now, or its key is not among the keys spark `offered` now or its kind is none the page runs. The
    page comes before the offers, so a second click on a pick, which is no offer once it ran, is stale."""
    key = key_of(request)
    if id_of(request) is None or key is None or not (isinstance(request.seen, str) and SEEN_PATTERN.fullmatch(request.seen)):
        return request_codes.REQUEST_MALFORMED
    if kind_of(key) in IN_CHAT:
        return request_codes.REQUEST_IN_CHAT
    if request.seen != fingerprint[:SHORT]:
        return request_codes.REQUEST_STALE
    if key not in offered or kind_of(key) not in KIND_RUNS:
        return request_codes.REQUEST_NOT_OFFERED
    return None


def line_of(label, result):
    """One sentence for the step whose offer has `label`: the sentence of its first Finding of the run's status, or, when it
    ended ok, spark's own line. A step's first line is no sentence: the build's is blank."""
    status = result.status()
    found = [finding.sentence for finding in result.findings if finding.severity == status]
    return found[0] if found else RAN_LINE % (label, MARKS[status][0] or OK)


def answer_of(kind, result):
    """(status, note) of the answer of a step of `kind` that ran: a build that could not run only because Wokwi has no
    model of the board answers ok, with its simulation's sentence as the note, as the guide counts it done (P1008). It
    asks the guide's rule of the run's own Findings, one per stopped stage, never .spark/build.json: a crashed build
    leaves an older record there. Any other run answers its own status and no note."""
    status = result.status()
    stopped = {"stages": [{"name": finding.subject, "status": finding.severity, "code": finding.code} for finding in result.findings]}
    if kind == flow_codes.BUILD_BOARD and status == COULD_NOT_RUN and stops_only_for_no_model(stopped):
        return OK, result.findings[0].sentence
    return status, None


class RunRequest(Operation):
    """
    Operation: run the step the page asked for. It reads the request and deletes it (`read_request`), reads the flow, and
    refuses with one could-not-run Finding of `request_codes` (`refusal_of`), or runs the kind's Operation through
    `run_operation` with the values of spark's offer (`KIND_RUNS`). Its data says for which request, what ran and how it
    ended, and the fingerprint after the run. A step's Findings and diagnostics are its own. `readers` and `operations`
    ({kind: Operation}) are what a test swaps (None: the real ones).
    """

    name = "run-request"
    summary = ("Run the step the page asked for in .spark/page-request.json, a pick, the parts list or the build, only when "
               "spark offers it now and the project has not changed since the page was read (P829).")
    arguments = (COMMON_ARGUMENTS["project"]._replace(help="the project folder (default: here)"), COMMON_ARGUMENTS["json"])
    effects = (READS, RUNS, WRITES)
    data_keys = ("for", "key", "label", "ran", "status", "mark", "line", "note", "fingerprint")
    privacy_for = staticmethod(privacy_for)

    def __init__(self, readers=None, operations=None):
        self.readers, self.operations = readers, operations or {}

    def run(self, project, *, outside):
        request = read_request(project)
        phases = read_flow(project, self.readers)[0]
        fingerprint = fingerprint_of(project, phases)
        offers = {offer.key: offer for phase in phases for offer in phase.offers}
        refused = refusal_of(request, offers, fingerprint)
        # the key and the label only of an offer spark holds now: a request's own text, any length, never reaches the answer
        offer = offers.get(key_of(request))
        if refused:
            data = {"for": id_of(request), "key": offer.key if offer else None, "label": offer.label if offer else None, "ran": False,
                    "status": COULD_NOT_RUN, "mark": MARKS[COULD_NOT_RUN][1], "line": refused.meaning, "note": None,
                    "fingerprint": fingerprint}
            return OperationResult(data, [Finding.of(COULD_NOT_RUN, None, refused, refused.meaning)], lines=[refused.meaning])
        kind = kind_of(offer.key)
        step = self.operations.get(kind) or KIND_RUNS[kind].operation()
        result = run_operation(step, KIND_RUNS[kind].values(project, offer.key), outside=outside)
        after = fingerprint_of(project, read_flow(project, self.readers)[0])
        status, note = answer_of(kind, result)
        line = RAN_LINE % (offer.label, MARKS[status][0] or OK) if note else line_of(offer.label, result)
        data = {"for": request.id, "key": offer.key, "label": offer.label, "ran": True, "status": status, "mark": MARKS[status][1],
                "line": line, "note": note, "fingerprint": after}
        return OperationResult(data, result.findings, lines=[RAN_LINE % (offer.label, MARKS[status][0] or OK)] + list(result.lines),
                               diagnostics=result.diagnostics)
# --- end MVP ---
