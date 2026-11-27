"""
check_all as an Operation on the core (P804): every deterministic check in one call, with one answer. check_all.py is its
CLI, and its `--json` is the document `check.every_check` gives, indented (`JsonDocument`), with `written` and
`not_written` (P1255). It keeps its answer in the check record `.spark/check-design.json` (`records/check_record`), which
`flow.py show` and the page read. An MCP tool or an agent calls it with plain values.
"""

from pathlib import Path

from spark.checks import check
from spark.checks import check_codes
from spark.checks.checked_folder import CheckedFolder
from spark.core.operation import COMMON_ARGUMENTS, READS, WRITES, Argument, Operation
from spark.core.outcomes import COULD_NOT_RUN, SKIPPED
from spark.core.renderers import JsonDocument
from spark.core.result import Finding, OperationResult
from spark.core.zone_time import stamp
from spark.design import loader
from spark.records.board_records import PROJECT_BOARDS_DIR
from spark.records.check_record import (NOT_KEPT_SENTENCE, CheckRecordStore, answer_not_saved, answer_saved, input_name,
                                        record_file)

# --- MVP ---
#: Why a run keeps no check record, as a note and a line (P1255). A run with no project, or a folder in no project, says nothing.
SUB_FOLDER = NOT_KEPT_SENTENCE % "a sub-folder of a project keeps none"
OUTSIDE = NOT_KEPT_SENTENCE % "an input is outside the project, spark and the store"
#: The kept lines of a check record (`record_lines`): a check with problems, the checks that could not look, the count
#: of the checks that found nothing and what it rests on, and the checks not asked for.
FOUND_LINE, BLIND_LINE = "%s found %s", "%s could not look"
CLEAN_LINE, RESTING_PART, NOT_ASKED_LINE = "%d check(s) found nothing", "resting on %d unmeasured value(s)", "not asked for: %s"
#: The requirements file of a folder, whose `board` chooses the board to verify (`check.folder_boards` globs `*` before it).
REQUIREMENTS = "requirements.json"
#: The characters that make a CONVENTIONS pattern a glob, which names no default input.
GLOB = frozenset("*?[")

#: What `--help` says after the arguments.
DETAILS = """It writes one file, .spark/check-design.json, the check record that `flow.py show` and the page read: the
status, the result lines (each check that found problems, the checks that could not look, how many found nothing and
the checks not asked for), the time and the sha256 of each input. The inputs are the circuit, the rules, the fab
package, the requirements files, boards/ and each board file checked, each named by its path in the project, or as
spark:<path> or store:<path> for a board of spark's library or of the store's shelf. No gate reads it. It is kept only
for a project folder: a run with no --project, or on a folder in no project, keeps none, and a sub-folder of a project
or an input outside the project, spark and the store keeps none and says why. When the project has a page.html, it
writes that page again."""


def record_project(checked):
    """(the project whose check record a run over the CheckedFolder `checked` keeps, None), or (None, why) when it keeps
    none: `why` is None for no folder and for a folder in no project, and SUB_FOLDER for a sub-folder, whose build reads
    its project's records. The library is tested first, because `CheckedFolder.at` gives spark's folder as the project of
    a folder in no project, which then reads as a sub-folder."""
    if checked is None or loader.is_library(checked.project):
        return None, None
    if checked.elsewhere():
        return None, SUB_FOLDER
    return checked.project, None


def record_inputs(checked, inputs):
    """The names of the inputs a record over `inputs` (`every_check`'s, after the flags' merge) hashes, by
    `check_record.input_name`, None for one outside the project and its roots: each CONVENTIONS input found or given, else
    its first pattern when it is no glob, so a later build makes the record older; then the folder's requirements files
    and boards/, which choose the board; then each board file checked."""
    names = []
    for name, (_, patterns) in check.CONVENTIONS.items():
        if inputs.get(name):
            names.append(input_name(checked.project, inputs[name]))
        elif not GLOB & set(patterns[0]):
            names.append(patterns[0])
    names += sorted({REQUIREMENTS, *(found.name for found in Path(checked.folder).glob("*" + REQUIREMENTS))})
    names += [PROJECT_BOARDS_DIR + "/"] + [input_name(checked.project, board) for board in inputs.get("boards") or []]
    return list(dict.fromkeys(names))


def record_lines(findings, results, unmeasured):
    """The lines a check record keeps, from the Findings `CheckDesign.run` made and the `results`: one per check that
    found problems, one for the checks that could not look, the count of the other checks that ran, with the `unmeasured`
    lines it rests on, and the checks not asked for."""
    lines = [FOUND_LINE % (found.subject, found.sentence) for found in findings if found.code == check_codes.CHECK_FOUND_PROBLEMS]
    blind = [found.subject for found in findings if found.code == check_codes.CHECK_COULD_NOT_LOOK]
    lines += [BLIND_LINE % ", ".join(blind)] if blind else []
    named, skipped = {found.subject for found in findings}, [result["check"] for result in results if result["status"] == SKIPPED]
    clean = [result for result in results if result["check"] not in named and result["status"] != SKIPPED]
    count = ([CLEAN_LINE % len(clean)] if clean else []) + ([RESTING_PART % unmeasured] if unmeasured else [])
    return lines + ([", ".join(count)] if count else []) + ([NOT_ASKED_LINE % ", ".join(skipped)] if skipped else [])


class CheckDesign(Operation):
    """
    Operation: every deterministic check, over the inputs given or found in the folder `project` (`check.every_check`).
    Its data is the dict check_all prints with --json, its lines the text, and its Findings `check.findings_of` the
    results, or one could-not-run Finding when `project` names no usable folder. It reads files, and writes one: the
    check record of its project (P1255).
    """

    name = "check-design"
    summary = "Run every deterministic check and answer once."
    details = DETAILS
    arguments = (Argument(("--project",), "project", str,
                          "the folder the requirements file and the kept build (--keep) are in; every input is "
                          "discovered by convention and each resolved path is printed. The rules, parts and boards "
                          "come from the project the build reads: the nearest one up from the folder"),
                 Argument(("--boards",), "boards", str, "board definitions to verify against their vendor headers. Without it: the board that each requirements.json of the folder names, else the project's board. When none names a board with a definition: every board of the project, the shelf and spark's library", [], nargs="*"),
                 Argument(("--circuit",), "circuit", str, "the built netlist"),
                 Argument(("--rules",), "rules", str, "the project's rules file"),
                 Argument(("--package",), "package", str, "the exported fab package"),
                 COMMON_ARGUMENTS["json"]._replace(help="for a caller that is not a person: one JSON document with the status, "
                                                   "`unmeasured` (how many ? lines the answer rests on) and each check's result"))
    effects = (READS, WRITES)
    json_renderer = JsonDocument
    #: The keys of a normal answer; a refusal holds `tool`, `status` and `reason` only.
    data_keys = ("tool", "status", "unmeasured", "resolved", "results", "project", "written", "not_written")

    def effects_of(self, values):
        """With no `--project` a run keeps no record, so it only reads."""
        return self.effects if values.get("project") else (READS,)

    def written_project(self, values):
        """The project whose check record a run keeps (`record_project`), so the core writes its page again, or None."""
        return record_project(CheckedFolder.named(values.get("project"))[0])[0]

    def run(self, project=None, *, outside, **paths):
        """Every check over `project` and `paths` (boards, circuit, rules, package, each a plain value), its answer kept (`keep`)."""
        said, inputs, checked = check.every_check(project, **paths)
        if "reason" in said:
            findings = [Finding.of(COULD_NOT_RUN, None, check_codes.PROJECT_UNUSABLE, str(said["reason"]))]
        else:
            findings = check.findings_of(said["results"])
        result = OperationResult(said, findings, lines=check.render_every_check(said, project).split("\n"))
        return result if "reason" in said else self.keep(result, checked, inputs, outside)

    def keep(self, result, checked, inputs, outside):
        """`result` with `data.written` and `data.not_written` (P1255): its status and `record_lines` kept in the check
        record of the project `record_project` names, over the inputs `record_inputs` names, at `outside.clock`'s time
        (`check_record.answer_saved`). With no record, `not_written` is the sentence that says why, a note and a line
        too, or None for a run that keeps none and says nothing."""
        project, why = record_project(checked)
        names = record_inputs(checked, inputs) if project else []
        if None in names:
            project, why = None, OUTSIDE
        if project is None:
            said = answer_not_saved(result, record_file(self.name), why)
            return said._replace(data=dict(said.data, not_written=why))
        answer = {"status": result.status(), "data": {}, "lines": record_lines(result.findings, result.data["results"], result.data["unmeasured"])}
        kept = answer_saved(CheckRecordStore(project, self.name), result, names, stamp(outside.clock.now()), answer)
        return kept._replace(data=dict(kept.data, not_written=None if kept.data["written"] else kept.notes[-1]["sentence"]))
# --- end MVP ---
