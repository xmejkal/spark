"""
The research Operation (P737, steps 4 and 5): `research.py --part <id>` is its CLI. It finds the gaps that the fact need
tree names in one part record, asks each source in `SOURCE_ORDER` for an offer and folds each offer into the record
before the next source asks (a pipeline: the wiki keeps the drawing, the kept documents cite it), answers the questions
through `outside.replies`, folds the replies and writes the record. A question nobody answered now goes on the run's open
list: the status is `could-not-run`, the replies file holds the template, and `next[0]` is the same run with `--replies`.
"""

import json
import shlex
from collections import namedtuple
from pathlib import Path

from spark.core import outcomes
from spark.core.codes import BAD_ARGUMENT
from spark.core.errors import SparkError
from spark.core.events import Event
from spark.core.operation import ASKS, COMMON_ARGUMENTS, FETCHES, JSON_FLAG, READS, WRITES, Argument, Operation
from spark.core.replies import PERSON, RepliesStore, needs_reply_findings, order_open, reply_problems
from spark.core.result import Finding, NextStep, OperationResult
from spark.core.text_guards import guard_lines, printable
from spark.records import record_kind
from spark.records.fact_needs import FactNeeds
from spark.records.record_kind import _write_record
from spark.sourcing.part_records import PHYSICAL_KEYS, PartError, definition_path, validate
from spark.sourcing.research import PHASE, REFUSED_LINE
from spark.sourcing.research.merge import (
    BODY, DOCUMENTS, NOT_LISTED, body_sizes, fold_documents, fold_not_published, fold_replies, not_published_of)
from spark.sourcing.research.research_source import RESEARCH_SOURCES, names_a_drawing, question_for
from spark.sourcing.sourcing_codes import PART_CONTRACT_BROKEN

# --- MVP ---
SCRIPT, OP = "research.py", "research-part"
#: The kind whose rows the needs file holds. Every part record gets them until a second kind has rows, as the file's `//` says.
MODULE_KIND = "module"
#: The sources, in the order the run asks them: a dependency, not a preference, because each offer is folded before the
#: next source asks (the wiki keeps the drawing the kept documents cite). Settings come later (slice 1).
SOURCE_ORDER = ("dfrobot-wiki", "kept-documents")
#: Value: what one round of the sources left: the record with their documents folded in, the questions, the source list
#: the run prints, the problems the sources met as (source name, SparkError) and the record keys the fold changed.
Round = namedtuple("Round", "record questions sources problems written")
IN_LIBRARY_FIX = "spark's library is changed in spark's repository; research a copy of the record in the project's parts/"
CONTRACT_FIX = "fix the value in the replies file so the record meets its contract, then run again"
WROTE = "record written: %s (unverified)"
NO_GAPS = "no gaps: every fact the needs file lists is held or named in physical_proof.not_published"
KEPT = "documents: %d kept in the store, %d listed but not keepable"
NONE_ASKED = "none asked"
PART_HELP = "the id of the part record to research: in the project's parts/ or the person's shelf"
PROJECT_HELP = "the project whose parts/ holds the record (default: here)"
NO_SUCH_PART_FIX = "parts.py --need <words> finds what exists; a new record starts with parts.py --skeleton"


def refusal(outside, refused):
    """The SparkError `refused`, said once through `outside.report` as a LINE, for the caller to raise."""
    outside.report(Event.line(PHASE, REFUSED_LINE % (refused.code, printable(str(refused)), refused.fix)))
    return refused


def has_fact(record, fact_path):
    """Whether the record holds a value at this dotted path. A block (`body_mm`, `physical.header`) is present as itself."""
    return _walk(record, fact_path) is not None


def _walk(record, fact_path):
    value = record
    for key in fact_path.split("."):
        value = value.get(key) if isinstance(value, dict) else None
    return value


def held_value(record, fact_path):
    """What the record holds at the path, as a reply says it: for `body_mm`, the width and height alone (`merge.body_sizes`)."""
    return _comparable(fact_path, _walk(record, fact_path))


def _comparable(fact_path, value):
    return body_sizes(value) if fact_path == BODY else value


def find_gaps(record, needs):
    """The FactNeed rows, one per fact path in file order, whose fact the record lacks, minus the keys that
    `physical_proof.not_published` names. A present but unverified fact is no gap: a drawing cannot verify what was read off it."""
    not_published = not_published_of(record)
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
    rest = {key: reply for key, reply in given.items() if not (has_fact(record, key) and held_value(record, key) == _comparable(key, reply.value))}
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
    effects = (READS, WRITES, ASKS, FETCHES)

    def run(self, part, project, replies, *, outside):
        path, record = self._record(part, project, outside)
        needs = FactNeeds.from_file()
        gaps = find_gaps(record, needs)
        held = self._round(gaps, record, outside, needs)
        answers = {question.key: outside.replies(question) for question in held.questions}
        open_questions = order_open([question for question in held.questions if answers[question.key] is None])
        replies_path = Path(replies) if replies else RepliesStore.for_project(project).path
        rest, filled = settle(RepliesStore(replies_path).load() if replies else {}, held.record)
        findings, written = reply_problems(rest, held.questions, filled), []
        if not findings:
            findings, written = self._fold(path, record, held, answers, part)
        findings += [Finding(outcomes.COULD_NOT_RUN, name, problem.code, printable(str(problem)), problem.fix) for name, problem in held.problems]
        following = []
        if open_questions:
            RepliesStore(replies_path).dump(open_questions)
            findings += needs_reply_findings(open_questions, replies_path, "%s --part %s --project %s" % (SCRIPT, part, shlex.quote(str(project))))
            following = [NextStep(OP, ["--part", part, "--project", str(project), "--replies", str(replies_path), JSON_FLAG], "%d open" % len(open_questions),
                                  self.effects, needs_person=True if any(q.asked_of == PERSON for q in open_questions) else None)]
        data = {"part": part, "sources": held.sources, "gaps": [need.fact_path for need in gaps], "written": written,
                "open": [question.to_dict() for question in open_questions]}
        return OperationResult(data, findings, following, self._lines(data, replies_path, held), notes=[WROTE % ", ".join(written)] if written else None)

    @staticmethod
    def _record(part, project, outside):
        """The record's path and the record. No record of that id is a SparkError with `definition_path`'s code (`no_such_part`),
        and a record in spark's library is a SparkError `bad_argument`; each is said as an Event first."""
        try:
            path = definition_path(part, project)
        except PartError as missing:
            raise refusal(outside, SparkError("%s", missing, code=missing.code, fix=NO_SUCH_PART_FIX))
        if path.parent.resolve() == record_kind.LIBRARY.resolve():
            raise refusal(outside, SparkError("%s is a record of spark's own library", part, code=BAD_ARGUMENT, fix=IN_LIBRARY_FIX))
        return path, json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _round(gaps, record, outside, needs):
        """One round of the sources, in order, each offer folded into the record before the next asks; then, when a page was
        read with no problem and the documents name no drawing, the physical gaps go to `not_published`; then one EITHER
        question with no citation per gap no source asked about, so no gap is silent. With no gaps, no source runs."""
        questions, remaining, sources, problems, written, pages = [], list(gaps), [], [], set(), []
        for name in SOURCE_ORDER if gaps else ():
            source = RESEARCH_SOURCES[name](needs)
            offer = source.offer(remaining, record, outside)
            record, changed = fold_documents(record, offer)
            written |= set(changed)
            problems += [(name, problem) for problem in offer.problems]
            pages += offer.urls_read if not offer.problems else ()
            questions += offer.questions
            asked = {question.key for question in questions}
            remaining = [need for need in find_gaps(record, needs) if need.fact_path not in asked]
            sources.append({"name": name, "where": source.where})
        if pages and not names_a_drawing(record.get(DOCUMENTS)):
            unpublished = [need.fact_name for need in remaining if need.fact_name in PHYSICAL_KEYS]
            record, changed = fold_not_published(record, unpublished, NOT_LISTED % (pages[0], outside.clock.now().date().isoformat()))
            written |= set(changed)
            remaining = [need for need in remaining if need.fact_name not in unpublished]
        questions += [question_for(need, needs.question_of(need.fact_path)) for need in remaining]
        return Round(record, questions, sources, problems, sorted(written))

    @staticmethod
    def _fold(path, record, held, answers, part):
        """The replies folded into the round's record and written, with what the sources changed, or the contract problems the
        fold added (as `_set_in_home` judges a write: the problems of the result minus the record's own, `record` as read
        from disk) as Findings, and nothing written."""
        given = {key: reply for key, reply in answers.items() if reply is not None}
        after, written = fold_replies(held.record, given, held.questions, {question.key: question.why for question in held.questions})
        written = sorted(set(written) | set(held.written))
        if not written:
            return [], []
        broken = sorted(set(validate(after, path)) - set(validate(record, path)))
        if broken:
            return [Finding(outcomes.PROBLEMS, part, PART_CONTRACT_BROKEN, sentence, CONTRACT_FIX) for sentence in broken], []
        _write_record(path, after)
        return [], written

    @staticmethod
    def _lines(data, replies_path, held):
        """What a person reads: the source order first, then what the sources kept, the gaps, what was written and what is open."""
        lines = ["sources: " + (", ".join("%d %s (%s)" % (index, source["name"], source["where"]) for index, source in enumerate(data["sources"], 1)) or NONE_ASKED)]
        if DOCUMENTS in held.written:
            entries = held.record[DOCUMENTS].values()
            lines.append(KEPT % (sum(1 for entry in entries if entry.get("kept") is not False), sum(1 for entry in entries if entry.get("kept") is False)))
        lines.append("gaps: " + ", ".join(data["gaps"]) if data["gaps"] else NO_GAPS)
        lines += ["written: " + ", ".join(data["written"])] if data["written"] else []
        lines += ["open: %d, fill %s" % (len(data["open"]), replies_path)] if data["open"] else []
        return [guard_lines(line) for line in lines]
# --- end MVP ---
