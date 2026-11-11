"""
The audit of every record and drawer link, as an Operation on the core (P707, N19): `parts.py --audit` is its CLI. A design
Operation, because it says which board stops the chain at the footprint stage (`footprint_emitter`), a design fact (C-7).
`walk` (it was `audit`) and the Operation's `run` (it was `_op_audit`) moved here from `goal_handlers` (W6-S3b). It writes nothing.
"""

import shlex

from spark.core import codes, outcomes
from spark.core.errors import CodedMessageError, SparkError
from spark.core.operation import JSON_DEST, COMMON_ARGUMENTS, READS, Argument, Operation
from spark.core.renderers import FullEnvelope
from spark.core.result import Finding, OperationResult
from spark.core.text_guards import guard_lines
from spark.records import board_records, record_kind, records_codes, store
from spark.records.record_kind import owes, _parse, _shape_problems, _with_project
from spark.sourcing import drawer
from spark.sourcing.part_records import broken_problems, function_of
from spark.design import design_codes, footprint_emitter

# --- MVP ---
#: The fix of a store that could not be read: the file is named in the sentence.
UNREADABLE_FIX = "fix the file the sentence names, then run --audit again"
#: The fix of a negative --from.
START_FIX = "--from takes a whole number from 0 up"
#: The sentence of a drawer entry that points at a record nobody has.
DANGLING_SENTENCE = "points at a record nobody has"


def walk(project=None):
    """
    Every record in every layer — the catalog included — every drawer link, and each record a link reaches in the person's
    other projects, walked once (§5.4, P89): per layer how many are current, owe facts, or are broken; which say nothing
    of what they do (spark's layers and this project only); which entries point at nothing; which boards stop the chain at
    the footprint stage, their files lacking what the footprint is drawn from (C-7, P121).
    """
    walked = [("part", found, layer, path) for found, (layer, path) in store.records("parts", record_kind.LIBRARY,
                                                                                     project, drafts=True).items()]
    walked += [("board", found, layer, path) for found, (layer, path) in board_records.records(project).items()]
    known, mine, seen = drawer.linkable(project), store.projects(), {row[3].resolve() for row in walked}
    dangling, linked = [], []
    for entry, said in drawer.entries().items():
        if not (isinstance(said.get("is"), dict) and said["is"]):
            continue
        where, path = drawer.resolve(said["is"], known)
        if where is None:
            dangling.append(entry)
        elif where in mine and path.resolve() not in seen:
            seen.add(path.resolve())
            linked.append((next(iter(said["is"])), path.stem, where, path))
    counts, owed, broken, silent, stops = {}, [], [], [], []
    for kind, found, layer, path in walked + linked:
        row = counts.setdefault(layer, {"current": 0, "owed": 0, "broken": 0})
        record = _parse(path)
        wrong = (["does not parse as a JSON object"] if not isinstance(record, dict) else _shape_problems(
            board_records.validate, record, path, "board definition") if kind == "board"
            else broken_problems(record, path))
        owing = [] if wrong or kind == "board" else owes(record)
        row["broken" if wrong else "owed" if owing else "current"] += 1
        if wrong:
            broken.append({"id": found, "layer": layer, "problems": wrong})
        elif owing:
            owed.append({"id": found, "layer": layer, "owes": owing})
        elif kind == "board" and footprint_emitter.footprint_gaps(record):  # C-7: a board owes nothing, and may still stop the chain
            stops.append({"id": found, "layer": layer, "stops_why": footprint_emitter.why_no_footprint(record),
                          "stop_line": footprint_emitter.footprint_stop_line(record)})  # P411: the text shows the line; `--audit` drops it from the JSON
        if isinstance(record, dict) and not function_of(record, board=kind == "board") and (kind, found, layer, path) not in linked:
            silent.append(found)
    return counts, owed, broken, silent, dangling, stops


class AuditRecords(Operation):
    """
    Operation: `audit` as parts.py answers it: the counts per layer, the records that owe facts (paged from `--from`), the
    broken ones and the dangling drawer entries as problems, the silent ones, and the boards that stop at the footprint.
    A store that cannot be read is one could-not-run Finding with the store's own code, as parts.py answered it before.
    """

    name = "audit"
    arguments = (Argument(("--audit",), "audit", bool, "every record in every layer and every drawer link: what owes facts, what is broken"),
                 Argument(("--project",), "project", COMMON_ARGUMENTS["project"].kind, "a project whose own parts/ beats the shipped library"),
                 Argument(("--from",), "start", int, "with a listing: start at item N (truncated.next says where)", 0),
                 COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS,)
    json_renderer = FullEnvelope

    def run(self, project, start, *, outside, audit=True):
        if start < 0:
            raise SparkError("--from %d: a listing cannot start before its first item", start, code=codes.BAD_ARGUMENT, fix=START_FIX)
        project = project.resolve() if project else None
        try:
            counts, owed, broken, silent, dangling, stops = walk(project)
        except CodedMessageError as unreadable:  # a store's refusal: could-not-run, never a traceback
            raise SparkError("%s", unreadable, code=unreadable.code, fix=UNREADABLE_FIX)
        except OSError as unreadable:
            raise SparkError("--audit: %s", unreadable, code=design_codes.RECORD_UNREADABLE, fix=UNREADABLE_FIX)
        shown, truncated = store.page_with_store(owed, start, "audit", ["--audit"] + _with_project(project))
        lines = ["  %-12s %3d current, %3d owe facts, %3d broken" % (layer, row["current"], row["owed"], row["broken"])
                 for layer, row in counts.items()]
        lines += ["  BROKEN %s (%s): %s" % (b["id"], b["layer"], "; ".join(b["problems"])) for b in broken]  # each, once
        lines += ["  %s (%s) owes: %s" % (o["id"], o["layer"], ", ".join(o["owes"])) for o in owed]
        lines += ["  says nothing of what it does — set it once with --function-set <part> <file>%s: %s"
                  % (" --project %s" % shlex.quote(str(project)) if project else "", ", ".join(silent))] if silent else []
        lines += ["  drawer entry %s points at a record nobody has" % entry for entry in dangling]
        lines += ["  %s (%s) %s" % (s["id"], s["layer"], s["stop_line"]) for s in stops]
        findings = [Finding(outcomes.PROBLEMS, b["id"], records_codes.RECORD_FILE_BROKEN, "broken: " + "; ".join(b["problems"]), None) for b in broken]
        findings += [Finding(outcomes.PROBLEMS, entry, design_codes.DRAWER_ENTRY_DANGLING, DANGLING_SENTENCE, None) for entry in dangling]
        data = {"layers": counts, "owed": shown, "broken": broken, "no_function": silent, "dangling": dangling,
                "stops_at_footprint": [{key: s[key] for key in ("id", "layer", "stops_why")} for s in stops]}
        return OperationResult(data, findings, (), [guard_lines(line) for line in lines], truncated=truncated, notes=(), assumptions=())
# --- end MVP ---
