"""
`parts.py --fact-set`: a record's facts filled in its own home, as an Operation on the core (P726 PR 3). It was
`parts._op_fact_set`. The chain facts, `facts` entries by name (a bench result and its source, P374), what the record says of
itself, a board's onboard levels (P464), and what the sheet reads (`legs`, `host_requirements`, P741); never spark's library.
The CLI reads the file and hands the object in (`Argument.payload`).
"""

from spark.core import codes
from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, WRITES, Argument
from spark.records import missing_facts, provenance
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.record_kind import Answer, CHAIN_FACTS, _absent, _problem
from spark.sourcing import drawer
from spark.sourcing.part_operation import PartOperation
from spark.sourcing.part_records import broken_problems
from spark.sourcing.record_home import set_fields

# --- MVP ---
#: The sentence of a payload that is not a fact write.
NOT_A_FACT_WRITE = ("a fact write is a JSON object of facts the chain reads: %s, or `facts` entries by name, or `physical` "
                    "with its `physical_proof`, or what the sheet reads: %s; or of what a record says of itself: %s")


class SetFacts(PartOperation):
    """Operation: `fact-set` as parts.py answers it: what was set, `was` and `now`, the shelf copy's fate, or why the write
    was refused; a part nobody has is a problem on its id."""

    name = "fact-set"
    data_keys = ('part', 'path', 'was', 'now', 'written', 'shelf_copy')
    arguments = (Argument(("--fact-set",), "part_and_facts", str,
                          "fill what a record owes — a JSON object of the facts the chain reads, or `facts` entries {value, verified, source} by name (a bench result is verified true and its source says who, when and how; a text in it has its control characters turned into a space and is cut at 1000 characters, and a key with a control character is refused), or its about, description and tags, or a board's onboard LED or button level, `pin_roles` {onboard_led|onboard_button: {active_level: {value, verified, source}}} (a board of the project's own, merged role by role), or what the sheet reads, `legs` {pin of pin_order: how to tell the leg apart} (merged leg by leg) and `host_requirements` [the lines the host board must meet] (replaced as a whole, like tags), in FILE (- for stdin) — in the record's own home (--project picks the project's copy); never spark's library",
                          nargs=2, metavar=("PART", "FILE"), payload=1),
                 ANSWER_ARGUMENTS["project"], ANSWER_ARGUMENTS["dry_run"], COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, WRITES)

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def build_answer(self, part_and_facts, project, dry_run):
        part_id, facts = part_and_facts
        if not (isinstance(facts, dict) and facts and set(facts) <= set(CHAIN_FACTS + drawer.DESCRIBING + drawer.PROVENANCE_KEYS + drawer.SHEET_KEYS)):
            return Answer(problems=[_problem(part_id, NOT_A_FACT_WRITE % (", ".join(CHAIN_FACTS), ", ".join(drawer.SHEET_KEYS), ", ".join(drawer.DESCRIBING)),
                                             code=codes.BAD_ARGUMENT)])
        facts = {key: drawer.scrub(key, value) if key in drawer.DESCRIBING + drawer.PROVENANCE_KEYS + drawer.SHEET_KEYS else value for key, value in facts.items()}
        wrong = [drawer.CHECKS[key][1] for key in drawer.DESCRIBING if key in facts and not drawer.CHECKS[key][0](facts[key])] + drawer.list_provenance_key_problems(facts)
        if wrong:
            return Answer(problems=[_problem(part_id, sentence) for sentence in wrong])
        return set_fields(part_id, project, facts, dry_run, lambda record, after, path: missing_facts.board_write_problems(record, after, path, facts, project) if "pin_roles" in facts else (
            ["%s is absent — a write fills a fact, it never empties one" % key for key in facts if _absent(key, facts[key])]
            + drawer.list_sheet_key_problems(facts, record)
            + sorted(set(provenance.list_entry_problems(facts.get("facts"), record.get("facts"))) | set(broken_problems(after, path)) - set(broken_problems(record, path)))))
# --- end MVP ---
