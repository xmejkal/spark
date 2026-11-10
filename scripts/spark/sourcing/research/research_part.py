"""
The research Operation (P737, step 4): `research.py --part <id>` is its CLI. It finds the gaps that the fact need tree
names in one part record, asks each source in `SOURCE_ORDER` for an offer, answers the questions through `outside.replies`,
folds the replies into the record and writes it. A question nobody answered now goes on the run's open list: the status is
`could-not-run`, the replies file holds the template, and `next[0]` is the same run with `--replies`.
"""

import json
import shlex
from pathlib import Path

from spark.core import outcomes
from spark.core.codes import BAD_ARGUMENT
from spark.core.errors import SparkError
from spark.core.operation import ASKS, COMMON_ARGUMENTS, JSON_FLAG, READS, WRITES, Argument, Operation
from spark.core.replies import PERSON, RepliesStore, needs_reply_findings, order_open, reply_problems
from spark.core.result import Finding, NextStep, OperationResult
from spark.core.text_guards import guard_lines
from spark.records import record_kind
from spark.records.fact_needs import FactNeeds
from spark.records.record_kind import _write_record
from spark.sourcing.part_records import definition_path, validate
from spark.sourcing.research.merge import BODY, BODY_KEYS, NOT_PUBLISHED, PROOF, fold_replies
from spark.sourcing.research.research_source import RESEARCH_SOURCES, question_for
from spark.sourcing.sourcing_codes import PART_CONTRACT_BROKEN

# --- MVP ---
SCRIPT, OP = "research.py", "research-part"
#: The kind whose rows the needs file holds. Every part record gets them until a second kind has rows, as the file's `//` says.
MODULE_KIND = "module"
#: The sources, in the order the run asks them. Step 5 puts `dfrobot-wiki` first. Settings come later (slice 1).
SOURCE_ORDER = ("kept-documents",)
IN_LIBRARY_FIX = "spark's library is changed in spark's repository; research a copy of the record in the project's parts/"
CONTRACT_FIX = "fix the value in the replies file so the record meets its contract, then run again"
WROTE = "record written: %s (unverified)"
NO_GAPS = "no gaps: every fact the needs file lists is held or named in physical_proof.not_published"
PART_HELP = "the id of the part record to research: in the project's parts/ or the person's shelf"
PROJECT_HELP = "the project whose parts/ holds the record (default: here)"


def has_fact(record, fact_path):
    """Whether the record holds a value at this dotted path. A block (`body_mm`, `physical.header`) is present as itself."""
    return _walk(record, fact_path) is not None


def _walk(record, fact_path):
    value = record
    for key in fact_path.split("."):
        value = value.get(key) if isinstance(value, dict) else None
    return value


def held_value(record, fact_path):
    """What the record holds at the path, as a reply would say it: for `body_mm`, the width and height alone, because
    the block carries its provenance too."""
    value = _walk(record, fact_path)
    return {key: value.get(key) for key in BODY_KEYS} if fact_path == BODY and isinstance(value, dict) else value


def find_gaps(record, needs):
    """The FactNeed rows, one per fact path in file order, whose fact the record lacks, minus the keys that
    `physical_proof.not_published` names. A present but unverified fact is no gap: a drawing cannot verify what was read off it."""
    proof = record.get(PROOF)
    not_published = proof.get(NOT_PUBLISHED) or [] if isinstance(proof, dict) else []
    gaps, seen = [], set()
    for need in needs.of_kind(MODULE_KIND):
        if need.fact_path not in seen and not has_fact(record, need.fact_path) and need.fact_name not in not_published:
            gaps.append(need)
        seen.add(need.fact_path)
    return gaps


def settle(given, record):
    """`(rest, filled)`: the given replies minus the keys whose value the record already holds, and the keys of the rest
    that the record holds with another value. A rerun with the same file adds nothing twice and flags nothing; a reply that
    would change a held fact is in `filled`, so `reply_problems` names it."""
    rest = {key: reply for key, reply in given.items() if not (has_fact(record, key) and held_value(record, key) == reply.value)}
    return rest, [key for key in rest if has_fact(record, key)]


class ResearchPart(Operation):
    """
    Operation: research one part record. It reads the record, finds its gaps, asks the sources, answers through
    `outside.replies`, folds, validates and writes. A reply to a fact the record holds, or a key no question has, is a
    problem and nothing is written. A record of spark's own library is refused: it is changed in the repository.
    """

    name = OP
    arguments = (Argument(("--part",), "part", str, PART_HELP, required=True),
                 COMMON_ARGUMENTS["project"]._replace(help=PROJECT_HELP), COMMON_ARGUMENTS["replies"], COMMON_ARGUMENTS["json"])
    effects = (READS, WRITES, ASKS)

    def run(self, part, project, replies, *, outside):
        path, record = self._record(part, project)
        needs = FactNeeds.from_file()
        gaps = find_gaps(record, needs)
        questions, sources = self._questions(gaps, record, outside, needs)
        answers = {question.key: outside.replies(question) for question in questions}
        open_questions = order_open([question for question in questions if answers[question.key] is None])
        replies_path = Path(replies) if replies else RepliesStore.for_project(project).path
        rest, filled = settle(RepliesStore(replies_path).load() if replies else {}, record)
        findings, written = reply_problems(rest, questions, filled), []
        if not findings:
            findings, written = self._fold(path, record, answers, questions, part)
        following = []
        if open_questions:
            RepliesStore(replies_path).dump(open_questions)
            findings += needs_reply_findings(open_questions, replies_path, "%s --part %s --project %s" % (SCRIPT, part, shlex.quote(str(project))))
            following = [NextStep(OP, ["--part", part, "--project", str(project), "--replies", str(replies_path), JSON_FLAG], "%d open" % len(open_questions),
                                  self.effects, needs_person=True if any(q.asked_of == PERSON for q in open_questions) else None)]
        data = {"part": part, "sources": sources, "gaps": [need.fact_path for need in gaps], "written": written,
                "open": [question.to_dict() for question in open_questions]}
        return OperationResult(data, findings, following, self._lines(data, replies_path), notes=[WROTE % ", ".join(written)] if written else None)

    @staticmethod
    def _record(part, project):
        """The record's path and the record. A record in spark's library is a SparkError `bad_argument`."""
        path = definition_path(part, project)
        if path.parent.resolve() == record_kind.LIBRARY.resolve():
            raise SparkError("%s is a record of spark's own library", part, code=BAD_ARGUMENT, fix=IN_LIBRARY_FIX)
        return path, json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _questions(gaps, record, outside, needs):
        """The questions of every source in order, then one EITHER question with no citation per gap no source asked about,
        so no gap is silent; and the source list the run prints."""
        questions, remaining, sources = [], list(gaps), []
        for name in SOURCE_ORDER:
            source = RESEARCH_SOURCES[name](needs)
            offered = source.offer(remaining, record, outside).questions
            questions += offered
            remaining = [need for need in remaining if need.fact_path not in {question.key for question in offered}]
            sources.append({"name": name, "where": source.where})
        questions += [question_for(need, needs.question_of(need.fact_path)) for need in remaining]
        return questions, sources

    @staticmethod
    def _fold(path, record, answers, questions, part):
        """The replies folded into the record and written, or the contract problems as Findings and nothing written."""
        given = {key: reply for key, reply in answers.items() if reply is not None}
        after, written = fold_replies(record, given, questions, {question.key: question.why for question in questions})
        broken = validate(after, path)
        if broken:
            return [Finding(outcomes.PROBLEMS, part, PART_CONTRACT_BROKEN, sentence, CONTRACT_FIX) for sentence in broken], []
        if written:
            _write_record(path, after)
        return [], written

    @staticmethod
    def _lines(data, replies_path):
        """What a person reads: the source order first, then the gaps, what was written and what is open."""
        lines = ["sources: " + ", ".join("%d %s (%s)" % (index + 1, source["name"], source["where"]) for index, source in enumerate(data["sources"], 0))]
        lines.append("gaps: " + ", ".join(data["gaps"]) if data["gaps"] else NO_GAPS)
        lines += ["written: " + ", ".join(data["written"])] if data["written"] else []
        lines += ["open: %d, fill %s" % (len(data["open"]), replies_path)] if data["open"] else []
        return [guard_lines(line) for line in lines]
# --- end MVP ---
