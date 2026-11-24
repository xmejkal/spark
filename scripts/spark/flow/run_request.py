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
from spark.core.cli import run_operation, values_of
from spark.core.operation import COMMON_ARGUMENTS, READS, RUNS, WRITES, Operation
from spark.core.outcomes import COULD_NOT_RUN, OK, BadArgumentError
from spark.core.result import Finding, OperationResult
from spark.design.pick_parts import PickParts
from spark.design.write_requirements import WriteRequirements
from spark.flow import flow_codes, request_codes
from spark.flow.fingerprint import SHORT, fingerprint_of
from spark.flow.guide import NO_MODEL_CODES, stops_only_for_no_model
from spark.flow.phase_readers import MARKS
from spark.flow.show_flow import phases_of, privacy_for

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


#: The Operations the page may run, by op: today's three (P829). The page's allow-list, a subset of the Operation catalogue
#: (P1077 pins it); RunRequest runs the offer's step (P1030). Its end is P1082 #1587's.
STEP_OPERATIONS = {operation.name: operation for operation in (PickParts, WriteRequirements, BuildBoard)}


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
    is not `fingerprint` now, or its key is not among the keys spark `offered` now, its kind is none the page runs or its
    step's op is none of STEP_OPERATIONS. The page comes before the offers, so a second click on a pick, which is no offer
    once it ran, is stale."""
    key = key_of(request)
    if id_of(request) is None or key is None or not (isinstance(request.seen, str) and SEEN_PATTERN.fullmatch(request.seen)):
        return request_codes.REQUEST_MALFORMED
    if kind_of(key) in IN_CHAT:
        return request_codes.REQUEST_IN_CHAT
    if request.seen != fingerprint[:SHORT]:
        return request_codes.REQUEST_STALE
    if key not in offered or kind_of(key) not in flow_codes.SENDABLE or offered[key].step.op not in STEP_OPERATIONS:
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
    model of the board answers ok, with its code's meaning as the note (never a record's field name), as the guide counts it done (P1008). It
    asks the guide's rule of the run's own Findings, one per stopped stage, never .spark/build.json: a crashed build
    leaves an older record there. Any other run answers its own status and no note."""
    status = result.status()
    stopped = {"stages": [{"name": finding.subject, "status": finding.severity, "code": finding.code} for finding in result.findings]}
    if kind == flow_codes.BUILD_BOARD and status == COULD_NOT_RUN and stops_only_for_no_model(stopped):
        return OK, next(code.meaning for code in NO_MODEL_CODES if code == result.findings[0].code)
    return status, None


def refused_answer(request, offer, fingerprint, refused):
    """The answer of a request refused with `refused`: nothing ran. It names the key and the label only of an offer spark
    holds now, so a request's own text, any length, never reaches the answer."""
    data = {"for": id_of(request), "key": offer.key if offer else None, "label": offer.label if offer else None, "ran": False,
            "status": COULD_NOT_RUN, "mark": MARKS[COULD_NOT_RUN][1], "line": refused.meaning, "note": None, "fingerprint": fingerprint}
    return OperationResult(data, [Finding.of(COULD_NOT_RUN, None, refused, refused.meaning)], lines=[refused.meaning])


class RunRequest(Operation):
    """
    Operation: run the step the page asked for. It reads the request and deletes it (`read_request`), reads the flow, and
    refuses with one could-not-run Finding of `request_codes` (`refusal_of`), or runs the kind's Operation through
    `run_operation` with the values of spark's offer: its step, parsed by the Operation of the step's op (`values_of`). A
    step whose argv does not parse is refused too. Its data says for which request, what ran and how it ended, and the
    fingerprint after the run. A step's Findings and diagnostics are its own. `readers` and `operations` ({op: Operation})
    are what a test swaps (None: the real ones).
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
        phases = phases_of(project, self.readers)
        fingerprint = fingerprint_of(project, phases)
        offers = {offer.key: offer for phase in phases for offer in phase.offers}
        refused = refusal_of(request, offers, fingerprint)
        offer = offers.get(key_of(request))
        if refused:
            return refused_answer(request, offer, fingerprint, refused)
        step = offer.step
        try:
            values = values_of(STEP_OPERATIONS[step.op](), step.argv)[0]  # the real arguments, so a test's fake gets the real parse
        except BadArgumentError:
            return refused_answer(request, offer, fingerprint, request_codes.REQUEST_NOT_OFFERED)
        result = run_operation(self.operations.get(step.op) or STEP_OPERATIONS[step.op](), values, outside=outside)
        after = fingerprint_of(project, phases_of(project, self.readers))
        status, note = answer_of(kind_of(offer.key), result)
        line = RAN_LINE % (offer.label, MARKS[status][0] or OK) if note else line_of(offer.label, result)
        data = {"for": request.id, "key": offer.key, "label": offer.label, "ran": True, "status": status, "mark": MARKS[status][1],
                "line": line, "note": note, "fingerprint": after}
        return OperationResult(data, result.findings, lines=[RAN_LINE % (offer.label, MARKS[status][0] or OK)] + list(result.lines),
                               diagnostics=result.diagnostics)
# --- end MVP ---
