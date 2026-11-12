"""
`parts.py --skeleton`: a record to fill in, written to the project's parts/, as an Operation on the core (P726 PR 2). It was
`part_handlers._op_skeleton`. Refused when any layer holds the id (P740): the project layer wins, so a skeleton would hide or
overwrite the record that exists. The dry run says what it would write and writes nothing.
"""

import json

from spark.core import codes
from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, WRITES, Argument
from spark.core.outcomes import add_env, step
from spark.records import record_kind, store
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.record_kind import Answer, DEFINITION_SUFFIX, _cannot, _problem, _with_project
from spark.sourcing.part_facts import skeleton
from spark.sourcing.part_operation import PartOperation
from spark.sourcing.part_records import NOT_A_PLAIN_ID

# --- MVP ---
#: The help of the options `--skeleton` reads, worded as parts.py's OPTIONS rows (parts.py reads them here).
KIND_HELP = "with --skeleton: the part's kind (motor-driver, sensor, regulator, …)"
VENDOR_HELP = "with --skeleton: who makes it"
SKU_HELP = "with --skeleton: the maker's exact part number (SEN0526); research.py finds a DFRobot module's wiki page by it"
#: The layers `--promote` copies a record out of, into the project (`part_facts.promote`).
PROMOTABLE = ("shelf", "catalog")
#: What to do instead of a skeleton, by the layer that holds the record (P740).
SKELETON_FIXES = {"project": "fill it in, do not overwrite it",
                  "shelf": "`--promote %(id)s --project .` copies it into the project",
                  "catalog": "`--promote %(id)s --project .` copies the draft into the project",
                  "library": "spark ships it; name it in the requirements as it is"}
#: The sentence of a skeleton asked for with no project or no kind.
NEEDS_PROJECT_AND_KIND = "--skeleton needs --project (the record belongs to a project's parts/) and --kind"


class WriteSkeleton(PartOperation):
    """Operation: `skeleton` as parts.py answers it: the record written, or what a dry run would write, every null a fact to
    record; an id a layer holds is a problem with the step that promotes it; no project or no kind is a could-not-run item."""

    name = "skeleton"
    arguments = (Argument(("--skeleton",), "part_id", str, "write a record to fill in, to the project's parts/ (refused when any layer holds the id)",
                          metavar="PART"),
                 Argument(("--kind",), "kind", str, KIND_HELP),
                 Argument(("--vendor",), "vendor", str, VENDOR_HELP),
                 Argument(("--sku",), "sku", str, SKU_HELP),
                 ANSWER_ARGUMENTS["project"], ANSWER_ARGUMENTS["dry_run"], COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, WRITES)

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def build_answer(self, part_id, project, dry_run, **given):
        """`given` holds the three facts the skeleton starts from, each a flag: `kind`, `vendor` and `sku`."""
        if not project or not given["kind"]:
            return Answer(unchecked=[_cannot(NEEDS_PROJECT_AND_KIND, code=codes.BAD_ARGUMENT)])
        if not store.PLAIN.fullmatch(part_id):  # P87: a file every reader would refuse is never written
            return Answer(problems=[_problem(part_id, NOT_A_PLAIN_ID % part_id)])
        held = store.records("parts", record_kind.LIBRARY, project, drafts=True).get(part_id)
        if held:  # P740: the project layer wins over every other, so a skeleton here would hide the record that exists
            layer, path = held
            would = "overwrite" if layer == "project" else "hide"
            return Answer(problems=[_problem(part_id, "%s already holds %s; a skeleton here would %s it" % (layer, path, would),
                                             SKELETON_FIXES[layer] % {"id": part_id})],
                          next=[add_env(step("promote", ["--promote", part_id] + _with_project(project),
                                             "copy the %s record into the project" % layer, ["writes"]), store.read_given_env())]
                          if layer in PROMOTABLE else ())
        target = project / "parts" / (part_id + DEFINITION_SUFFIX)
        record = skeleton(part_id, given["kind"], given["vendor"], given["sku"])
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
        return Answer({"path": str(target), "record": record, "written": not dry_run},
                      ["  %s %s — every null is a fact to record; `parts.py --validate --project .` says what is missing"
                       % ("would write" if dry_run else "wrote", target)])
# --- end MVP ---
