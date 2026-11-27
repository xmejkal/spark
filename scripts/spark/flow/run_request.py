"""
The page's request as an Operation on the core (P829, #1187): `flow.py run-request` reads `.spark/page-request.json`, which
`/spark:page` writes from the page's database row, deletes it at once and runs the step it names, a pick, the parts list
or the build, or one pick of several needs (P1067), only when spark offers each key now and the page was read at the
project's fingerprint now. The values of the step come from spark's own offers, never from the request. A refusal runs
nothing and still answers.
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
from spark.flow import flow_codes, offer_steps, request_codes
from spark.flow.fingerprint import SHORT, fingerprint_of
from spark.flow.guide import NO_MODEL_CODES, stops_only_for_no_model
from spark.flow.phase_readers import MARKS, pick_need
from spark.flow.show_flow import phases_of, privacy_for
from spark.firmware.project_secrets import ProjectSecrets

# --- MVP ---
#: The request file, in the project: one request, which `/spark:page` writes and this Operation deletes.
REQUEST_FILE = Path(".spark") / "page-request.json"
#: An id as the page writes it (`crypto.randomUUID()`), and `seen`, the first SHORT hex digits of the fingerprint.
ID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
SEEN_PATTERN = re.compile(r"^[0-9a-f]{12}$")
#: Value: one request, as the file holds it: the page's id, the offer's key, the fingerprint's first digits the page was
#: read at, and `keys`, the keys of several picks (P1067): a row holds `key` or `keys`, never both. A field the file lacks
#: is None; the page's `at` is its own, and spark does not read it.
PageRequest = namedtuple("PageRequest", "id key seen keys", defaults=(None,))
#: The line of a step that ran: its offer's label and its status. A refusal's line is its code's meaning.
RAN_LINE = "ran %s: %s"
#: Between two notes of a step in the answer's one note: the page ends the note with its own full stop.
NOTES_JOIN = "; "


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


def keys_of(request):
    """The keys of `request` in its order (P1067): [key] for a row of one key, its `keys` for a row of picks, or None when
    it holds both, neither, or a key that is no text."""
    if request is None or (request.key is None) == (request.keys is None):
        return None
    keys = [request.key] if request.keys is None else request.keys
    return list(keys) if isinstance(keys, list) and keys and all(isinstance(key, str) and key for key in keys) else None


def refusal_of(request, offered, fingerprint):
    """The code that refuses `request`, or None when it may run: it cannot be read, a kind of its keys is asked in the chat,
    its `seen` is not `fingerprint` now, or a key is not among the keys spark `offered` now, is not sendable
    (`flow_codes.is_sendable`) or its step's op is none of STEP_OPERATIONS. A row of `keys` names only picks, one per
    need (P1067). The page comes before the offers, so a second click on a pick, which is no offer once it ran, is stale."""
    keys = keys_of(request)
    if id_of(request) is None or keys is None or not (isinstance(request.seen, str) and SEEN_PATTERN.fullmatch(request.seen)):
        return request_codes.REQUEST_MALFORMED
    for key in keys:
        if flow_codes.in_chat(key):
            return request_codes.REQUEST_IN_CHAT
    if request.seen != fingerprint[:SHORT]:
        return request_codes.REQUEST_STALE
    for key in keys:
        if key not in offered or not flow_codes.is_sendable(key) or offered[key].step.op not in STEP_OPERATIONS:
            return request_codes.REQUEST_NOT_OFFERED
    needs = [pick_need(key) for key in keys]
    if request.keys is not None and (None in needs or len(set(needs)) < len(needs)):
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
    leaves an older record there. A parts-list write that ran ok answers its own notes' sentences, joined by NOTES_JOIN,
    such as the entries it kept that no pick explains (P1139); with none, or not ok, no note, so a refusal's sentence stays
    the line. Any other run answers its own status and no note."""
    status = result.status()
    stopped = {"stages": [{"name": finding.subject, "status": finding.severity, "code": finding.code} for finding in result.findings]}
    if kind == flow_codes.BUILD_BOARD and status == COULD_NOT_RUN and stops_only_for_no_model(stopped):
        return OK, next(code.meaning for code in NO_MODEL_CODES if code == result.findings[0].code)
    if kind == flow_codes.WRITE_REQUIREMENTS and status == OK and result.notes:
        return status, NOTES_JOIN.join(note["sentence"] for note in result.notes)
    return status, None


def refused_answer(request, offer, fingerprint, refused, subject=None):
    """The answer of a request refused with `refused`: nothing ran. It names the key and the label only of an offer spark
    holds now, so a request's own text, any length, never reaches the answer. `subject` is the Finding's: the files of a
    secrets refusal (P1060)."""
    data = {"for": id_of(request), "key": offer.key if offer else None, "keys": [offer.key] if offer else [],
            "label": offer.label if offer else None, "ran": False,
            "status": COULD_NOT_RUN, "mark": MARKS[COULD_NOT_RUN][1], "line": refused.meaning, "note": None, "fingerprint": fingerprint}
    return OperationResult(data, [Finding.of(COULD_NOT_RUN, subject, refused, refused.meaning)], lines=[refused.meaning])


class RunRequest(Operation):
    """
    Operation: run the step the page asked for. It reads the request and deletes it (`read_request`), reads the flow, and
    refuses with one could-not-run Finding of `request_codes` (`refusal_of`), or runs the kind's Operation through
    `run_operation` with the values of spark's offer: its step, parsed by the Operation of the step's op (`values_of`). The
    picks of a row's `keys` run as one step, their offers' steps joined (`offer_steps.joined_picks`, P1067). A
    step whose argv does not parse is refused too, and so is any request while a secrets file cannot be read (P1060 D5),
    with no key or label. Its data says for which request, what ran and how it ended, and the fingerprint after the run. A step's Findings and diagnostics are its own. `readers` and `operations` ({op: Operation})
    are what a test swaps (None: the real ones).
    """

    name = "run-request"
    summary = ("Run the step the page asked for in .spark/page-request.json, a pick or several picks, the parts list or the "
               "build, only when spark offers it now and the project has not changed since the page was read (P829, P1067).")
    #: The one text of the request's shape and its refusals (P1067): `--help` prints it, and the docs link to it.
    details = """flow.py run-request reads .spark/page-request.json, the page's request, and deletes it at once. A request
is {id, key, seen, at} for one click, or {id, keys, seen, at} for one Send of several picks (P1067): a row holds key or
keys, never both. id is the page's UUID for the request, key one offer's key, keys a list of the keys of picks, one per
need, seen the first 12 hex digits of the fingerprint the page was read at, and at the page's own time, which spark does
not read. It runs the step only when seen is the first 12 hex digits of the fingerprint now, each key is an offer now,
its kind is pick, requirements or build, and its step names an Operation spark runs from the page. The picks of keys run
as one pick of all their needs, as parts.py --pick PROJECT NEED=ID NEED=ID does: any problem saves none of them. The
values come from spark's offers' steps, never from the request. Else it runs nothing:
request_malformed (no regular file, no JSON object, an id that is no UUID, a seen that is not 12 hex digits, key and keys
both or neither, a key that is no text, keys that is empty or no list of text, or a file it cannot delete),
request_in_chat (a need's drop, or a chat offer: a job only Claude does, such as write-firmware), request_stale (the
project changed after the page was read), request_not_offered (not an offer now, a kind the page never runs, or in keys a
key that is no pick or a second pick of one need) or request_secrets_unreadable (a secrets file in firmware/ that cannot
be read or parsed). With --json it prints data.for, data.key, data.keys, data.label, data.ran, data.status, data.mark,
data.line, data.note and data.fingerprint, the one after the run, a refusal too. key, keys and label name only offers
spark holds now: for keys, key is null, keys lists the picks and label joins their labels with "; ", and a refusal of
keys names no key. After a run, write the page again with flow.py page."""
    arguments = (COMMON_ARGUMENTS["project"]._replace(help="the project folder (default: here)"), COMMON_ARGUMENTS["json"])
    effects = (READS, RUNS, WRITES)
    data_keys = ("for", "key", "keys", "label", "ran", "status", "mark", "line", "note", "fingerprint")
    privacy_for = staticmethod(privacy_for)

    def __init__(self, readers=None, operations=None):
        self.readers, self.operations = readers, operations or {}

    def run(self, project, *, outside):
        request = read_request(project)
        phases = phases_of(project, self.readers)
        fingerprint = fingerprint_of(project, phases)
        offers = {offer.key: offer for phase in phases for offer in phase.offers}
        unreadable = ProjectSecrets.read(project).unreadable  # D5 first: the answer is published, and the mask has a hole
        if unreadable:  # no offer: its key and label can hold a value of the file that could not be read (#1610 review)
            return refused_answer(request, None, fingerprint, request_codes.REQUEST_SECRETS_UNREADABLE, ", ".join(unreadable))
        refused = refusal_of(request, offers, fingerprint)
        offer = offers.get(key_of(request))
        if refused:
            return refused_answer(request, offer, fingerprint, refused)
        chosen = [offers[key] for key in keys_of(request)]
        step = chosen[0].step if request.keys is None else offer_steps.joined_picks([each.step for each in chosen])
        try:
            values = values_of(STEP_OPERATIONS[step.op](), step.argv)[0]  # the real arguments, so a test's fake gets the real parse
        except BadArgumentError:
            return refused_answer(request, offer, fingerprint, request_codes.REQUEST_NOT_OFFERED)
        result = run_operation(self.operations.get(step.op) or STEP_OPERATIONS[step.op](), values, outside=outside)
        after = fingerprint_of(project, phases_of(project, self.readers))
        status, note = answer_of(flow_codes.kind_of(chosen[0].key), result)
        label = flow_codes.LABELS_JOIN.join(each.label for each in chosen)
        line = RAN_LINE % (label, MARKS[status][0] or OK) if note else line_of(label, result)
        data = {"for": request.id, "key": None if offer is None else offer.key, "keys": [each.key for each in chosen], "label": label,
                "ran": True, "status": status, "mark": MARKS[status][1], "line": line, "note": note, "fingerprint": after}
        return OperationResult(data, result.findings, lines=[RAN_LINE % (label, MARKS[status][0] or OK)] + list(result.lines),
                               diagnostics=result.diagnostics)
# --- end MVP ---
