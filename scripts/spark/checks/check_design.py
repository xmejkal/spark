"""
check_all as an Operation on the core (P804): every deterministic check in one call, with one answer. check_all.py is its
CLI, and its `--json` is the document `check.run_every_check` returns, indented (`JsonDocument`), so no golden changed.
An MCP tool or an agent calls it with plain values.
"""

from spark.checks import check
from spark.checks import check_codes
from spark.core.operation import COMMON_ARGUMENTS, READS, Argument, Operation
from spark.core.outcomes import COULD_NOT_RUN
from spark.core.renderers import JsonDocument
from spark.core.result import Finding, OperationResult

# --- MVP ---


class CheckDesign(Operation):
    """
    Operation: every deterministic check, over the inputs given or found in the folder `project` (`check.run_every_check`).
    Its data is the dict check_all prints with --json, its lines the text, and its Findings `check.findings_of` the
    results, or one could-not-run Finding when `project` names no usable folder. It reads files and writes none.
    """

    name = "check-design"
    arguments = (Argument(("--project",), "project", str,
                          "the folder the requirements file and the kept build (--keep) are in; every input is "
                          "discovered by convention and each resolved path is printed. The rules, parts and boards "
                          "come from the project the build reads: the nearest one up from the folder"),
                 Argument(("--boards",), "boards", str, "board definitions to verify against their vendor headers", [], nargs="*"),
                 Argument(("--circuit",), "circuit", str, "the built netlist"),
                 Argument(("--rules",), "rules", str, "the project's rules file"),
                 Argument(("--package",), "package", str, "the exported fab package"),
                 COMMON_ARGUMENTS["json"]._replace(help="for a caller that is not a person: one JSON document with the status, "
                                                   "`unmeasured` (how many ? lines the answer rests on) and each check's result"))
    effects = (READS,)
    json_renderer = JsonDocument
    #: The keys of a normal answer; a refusal holds `tool`, `status` and `reason` only.
    data_keys = ("tool", "status", "unmeasured", "resolved", "results", "project")

    def run(self, project=None, *, outside, **paths):
        """Every check over `project` and `paths` (boards, circuit, rules, package, each a plain value)."""
        said = check.run_every_check(project, **paths)
        if "reason" in said:
            findings = [Finding(COULD_NOT_RUN, None, check_codes.PROJECT_UNUSABLE, str(said["reason"]), None)]
        else:
            findings = check.findings_of(said["results"])
        return OperationResult(said, findings, lines=check.render_every_check(said, project).split("\n"))
# --- end MVP ---
