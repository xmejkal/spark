"""P737 step 4: research.py finds a record's geometry gaps, asks one question per gap that cites the kept drawing, and writes
the replies as unverified facts. No network; the store is a scratch folder; the replies come through the outside."""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import research  # noqa: E402
from fakes import FakeOutsideWorld  # noqa: E402
from spark.core.cli import run_operation  # noqa: E402
from spark.core.renderers import JsonEnvelope  # noqa: E402
from spark.core.replies import DeferringReplyStrategy, GivenReplyStrategy, Reply, RepliesStore  # noqa: E402
from spark.records.fact_needs import FactNeed, FactNeeds  # noqa: E402
from spark.sourcing.part_records import validate  # noqa: E402
from spark.sourcing.research import reply_strategy_for  # noqa: E402
from spark.sourcing.research.merge import fold_replies, not_published_of  # noqa: E402
from spark.sourcing.research.research_part import ResearchPart, find_gaps, has_fact, held_value, settle  # noqa: E402
from spark.sourcing.research.research_source import KeptDocumentsSource, question_for  # noqa: E402

NEEDS = FactNeeds.from_file()
DRAWING, SHA, FILE = "x-dimension-v1", "a" * 64, "x_dimension.pdf"
CITES = {"document": DRAWING, "at": "page 1"}
#: A module record with its outline and no `physical`, as a skeleton with one kept drawing looks.
RECORD = {
    "schema": 1, "id": "x-mod", "name": "X module", "kind": "microphone", "vendor": "x", "sku": "X1",
    "sources": ["https://example.org/x"], "needs": [{"signal": "I2S_SD", "pin": "DO", "direction": "out", "bus": "i2s"}],
    "power": [{"pin": "3V3", "rail": "logic", "direction": "in"}, {"pin": "GND", "rail": "ground", "direction": "in"}],
    "unused_pins": [], "pin_order": ["DO", "3V3", "GND"], "footprint": "pinrow3",
    "body_mm": {"width": 16, "height": 11, "verified": True, "source": "the maker's spec list", "cites": CITES},
    "pin_order_proof": {"verified": True, "source": "the maker's pinout table", "cites": CITES},
    "facts": {}, "host_requirements": [],
    "documents": {DRAWING: {"url": "https://example.org/x_dimension.pdf", "sha256": SHA, "file": FILE, "retrieved": "2026-11-10",
                            "title": "X dimension drawing (Unit: mm)", "version": None}},
}
HOLES = [{"x_mm": 2, "y_mm": 2, "drill_mm": 2}]
HEADER = {"pitch_mm": 2.54, "pins": [3], "rows": 1, "first_pad_from_edge_mm": 1.35}
BY = "replies file research-replies.json"


def reply(key, value, cites=CITES, note=None):
    return Reply(key, value, BY, None, note, cites)


def need(fact_path, status="will read", card="P734"):
    return FactNeed("module", fact_path, "spark.x.Y", status, card)


ANSWERS = {"physical.thickness_mm": reply("physical.thickness_mm", 1, note="the side view"),
           "physical.mounting_holes": reply("physical.mounting_holes", HOLES),
           "physical.header": reply("physical.header", HEADER)}


class GapsTest(unittest.TestCase):
    def test_has_fact_walks_a_block_a_nested_key_a_missing_key_and_a_null(self):
        record = {"body_mm": {"width": 1}, "physical": {"header": {"rows": 1}, "thickness_mm": None}}
        self.assertEqual([has_fact(record, path) for path in ("body_mm", "physical.header", "physical.header.rows", "physical.mounting_holes", "physical.thickness_mm", "facts.x")],
                         [True, True, True, False, False, False])

    def test_the_fixture_has_the_three_physical_gaps_and_body_mm_once_when_absent(self):
        self.assertEqual([gap.fact_path for gap in find_gaps(RECORD, NEEDS)], ["physical.thickness_mm", "physical.mounting_holes", "physical.header"])
        bare = {key: value for key, value in RECORD.items() if key != "body_mm"}
        self.assertEqual([gap.fact_path for gap in find_gaps(bare, NEEDS)][:1], ["body_mm"])
        self.assertEqual(len(find_gaps(bare, NEEDS)), 4)

    def test_a_key_not_published_a_held_block_and_an_unverified_fact_are_no_gaps(self):
        proof = {"verified": False, "source": "read", "why_it_matters": "fit", "not_published": ["header"]}
        held = dict(RECORD, physical={"thickness_mm": 1, "mounting_holes": HOLES}, physical_proof=proof)
        self.assertEqual(find_gaps(held, NEEDS), [])
        self.assertEqual(find_gaps(dict(RECORD, physical_proof=dict(proof, not_published=["thickness_mm", "mounting_holes", "header"])), NEEDS), [])
        unverified = dict(RECORD, body_mm=dict(RECORD["body_mm"], verified=False))
        self.assertNotIn("body_mm", [gap.fact_path for gap in find_gaps(unverified, NEEDS)])

    def test_an_odd_proof_or_not_published_is_read_as_nothing(self):
        self.assertEqual(not_published_of(dict(RECORD, physical_proof=["x"])), [])
        self.assertEqual(not_published_of(dict(RECORD, physical_proof={"not_published": "header"})), [])
        self.assertEqual(not_published_of(dict(RECORD, physical_proof={"not_published": ["header", 3]})), ["header"])
        self.assertEqual(len(find_gaps(dict(RECORD, physical_proof={"not_published": "header"}), NEEDS)), 3)

    def test_only_the_module_kind_rows_count(self):
        needs = FactNeeds((need("physical.header"), FactNeed("board", "physical.buttons", "spark.x", "reads")))
        self.assertEqual([gap.fact_path for gap in find_gaps(RECORD, needs)], ["physical.header"])


class SettleTest(unittest.TestCase):
    def test_a_matching_key_drops_a_differing_held_key_is_filled_and_an_open_key_stays(self):
        record = dict(RECORD, physical={"thickness_mm": 1})
        given = {"physical.thickness_mm": reply("physical.thickness_mm", 1), "physical.header": reply("physical.header", HEADER)}
        self.assertEqual(settle(given, record), ({"physical.header": given["physical.header"]}, []))
        changed = {"physical.thickness_mm": reply("physical.thickness_mm", 2)}
        self.assertEqual(settle(changed, record), (changed, ["physical.thickness_mm"]))

    def test_a_body_mm_reply_with_an_extra_key_is_settled_by_its_sizes(self):
        given = {"body_mm": reply("body_mm", {"width": 16, "height": 11, "depth": 3})}
        self.assertEqual(settle(given, RECORD), ({}, []))

    def test_a_body_mm_reply_equal_to_the_block_s_sizes_drops(self):
        self.assertEqual(held_value(RECORD, "body_mm"), {"width": 16, "height": 11})
        self.assertEqual(settle({"body_mm": reply("body_mm", {"width": 16, "height": 11})}, RECORD), ({}, []))
        given = {"body_mm": reply("body_mm", {"width": 17, "height": 11})}
        self.assertEqual(settle(given, RECORD), (given, ["body_mm"]))


class QuestionTest(unittest.TestCase):
    def test_a_question_with_cites_is_an_agent_s_and_without_is_either_s(self):
        question = question_for(need("physical.header"), NEEDS.question_of("physical.header"), CITES)
        self.assertEqual((question.key, question.kind, question.asked_of, question.unit, question.cites),
                         ("physical.header", "value", "agent", "mm", CITES))
        self.assertEqual(question.why, "spark.x.Y will read it (P734)")
        either = question_for(need("body_mm", "reads", None), NEEDS.question_of("body_mm"))
        self.assertEqual((either.asked_of, either.cites, either.why), ("either", None, "spark.x.Y reads it"))


class KeptDocumentsSourceTest(unittest.TestCase):
    def setUp(self):
        self.kept = Path(tempfile.mkdtemp())
        self.source = KeptDocumentsSource(NEEDS, self.kept)
        self.gaps = find_gaps(RECORD, NEEDS)

    def keep(self, sha=SHA, file=FILE):
        (self.kept / sha).mkdir()
        (self.kept / sha / file).write_bytes(b"%PDF")

    def test_a_kept_drawing_gives_one_agent_question_per_gap_citing_page_1(self):
        self.keep()
        questions = self.source.offer(self.gaps, RECORD, FakeOutsideWorld()).questions
        self.assertEqual([(q.key, q.asked_of, q.cites) for q in questions],
                         [(gap.fact_path, "agent", CITES) for gap in self.gaps])

    def test_an_odd_documents_block_gives_no_question_and_no_crash(self):
        self.keep()
        for documents in (["x"], {DRAWING: "a string"}, {DRAWING: None}):
            with self.subTest(documents=documents):
                self.assertEqual(self.source.offer(self.gaps, dict(RECORD, documents=documents), FakeOutsideWorld()).questions, ())

    def test_no_kept_file_or_no_drawing_word_gives_no_question(self):
        self.assertEqual(self.source.offer(self.gaps, RECORD, FakeOutsideWorld()).questions, ())
        self.keep()
        datasheet = {"ds": dict(RECORD["documents"][DRAWING], title="X datasheet")}
        self.assertEqual(self.source.offer(self.gaps, dict(RECORD, documents=datasheet), FakeOutsideWorld()).questions, ())
        self.assertEqual(self.source.offer(self.gaps, dict(RECORD, documents=None), FakeOutsideWorld()).questions, ())


class FoldRepliesTest(unittest.TestCase):
    QUESTIONS = [question_for(gap, NEEDS.question_of(gap.fact_path), CITES) for gap in find_gaps(RECORD, NEEDS)]

    def test_physical_and_its_proof_are_written_unverified_with_the_source_and_the_note(self):
        after, written = fold_replies(RECORD, ANSWERS, self.QUESTIONS, {})
        self.assertEqual(written, ["physical", "physical_proof"])
        self.assertEqual(after["physical"], {"thickness_mm": 1, "mounting_holes": HOLES, "header": HEADER})
        self.assertEqual(after["physical_proof"], {"verified": False, "source": "read from x-dimension-v1 page 1 by " + BY,
                                                   "why_it_matters": "a hole or a header placed wrong puts the module where its pins miss the breadboard",
                                                   "cites": CITES, "note": "the side view"})
        self.assertEqual(validate(after, Path("x-mod.json")), [])
        self.assertNotIn("physical", RECORD)

    def test_not_published_keeps_the_keys_not_written_and_an_unknown_key_is_not_written(self):
        proof = {"verified": False, "source": "s", "why_it_matters": "w", "not_published": ["thickness_mm", "header"]}
        record = dict(RECORD, physical={"mounting_holes": HOLES}, physical_proof=proof)
        replies = {"physical.thickness_mm": ANSWERS["physical.thickness_mm"], "facts.x": reply("facts.x", 1)}
        after, written = fold_replies(record, replies, self.QUESTIONS, {})
        self.assertEqual((after["physical_proof"]["not_published"], written), (["header"], ["physical", "physical_proof"]))
        self.assertNotIn("facts.x", after)
        self.assertEqual(after["physical"], {"mounting_holes": HOLES, "thickness_mm": 1})

    def test_an_older_proof_is_merged_not_lost_and_an_odd_physical_is_replaced(self):
        old = {"verified": True, "source": "measured on the bench", "cites": {"document": DRAWING, "at": "page 2"}, "note": "calipers"}
        record = dict(RECORD, physical={"thickness_mm": 1}, physical_proof=old)
        replies = {"physical.header": ANSWERS["physical.header"]}
        after, written = fold_replies(record, replies, self.QUESTIONS, {})
        self.assertEqual(after["physical"], {"thickness_mm": 1, "header": HEADER})
        self.assertEqual(after["physical_proof"], {"verified": False, "source": "measured on the bench; read from x-dimension-v1 page 1 by " + BY,
                                                   "why_it_matters": "a hole or a header placed wrong puts the module where its pins miss the breadboard",
                                                   "cites": CITES, "note": "calipers"})
        for odd in (None, [1], "thin"):
            with self.subTest(physical=odd):
                after, written = fold_replies(dict(RECORD, physical=odd, physical_proof=[old]), replies, self.QUESTIONS, {})
                self.assertEqual((after["physical"], written), ({"header": HEADER}, ["physical", "physical_proof"]))
        incomplete = {"physical.header": reply("physical.header", HEADER, cites={"at": "page 1"})}
        after, _ = fold_replies(RECORD, incomplete, self.QUESTIONS, {})
        self.assertEqual(after["physical_proof"]["source"], "read from None page 1 by " + BY)
        self.assertTrue(validate(after, Path("x-mod.json")), "a citation with no document is the record's rule to refuse")

    def test_body_mm_takes_the_sizes_with_its_why_and_a_reply_with_no_cites_says_given_by(self):
        question = question_for(need("body_mm", "reads", None), NEEDS.question_of("body_mm"))
        bare = {key: value for key, value in RECORD.items() if key != "body_mm"}
        after, written = fold_replies(bare, {"body_mm": reply("body_mm", {"width": 16, "height": 11}, cites=None)}, [question], {"body_mm": question.why})
        self.assertEqual((written, after["body_mm"]), (["body_mm"], {"width": 16, "height": 11, "verified": False, "source": "given by " + BY,
                                                                      "why_it_matters": "spark.x.Y reads it"}))
        self.assertEqual(validate(after, Path("x-mod.json")), [])


class ResearchPartTest(unittest.TestCase):
    """A scratch store and a project with the fixture record in parts/; the drawing kept under the store's sources."""

    def setUp(self):
        self.home, self.project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        (self.home / "sources" / SHA).mkdir(parents=True)
        (self.home / "sources" / SHA / FILE).write_bytes(b"%PDF")
        (self.project / "parts").mkdir()
        self.path = self.project / "parts" / "x-mod.json"
        self.path.write_text(json.dumps(RECORD))
        self.replies_file = self.project / ".spark" / "research-replies.json"

    def research(self, strategy, replies=None):
        return run_operation(ResearchPart(), {"part": "x-mod", "project": self.project, "replies": replies},
                             FakeOutsideWorld(replies=strategy))

    def record(self):
        return json.loads(self.path.read_text())

    def test_run_1_asks_three_questions_writes_the_template_and_leaves_the_record(self):
        result = self.research(DeferringReplyStrategy())
        self.assertEqual(result.status(), "could-not-run")
        self.assertEqual([(found.code, found.subject) for found in result.findings],
                         [("needs_reply", "physical.thickness_mm"), ("needs_reply", "physical.mounting_holes"), ("needs_reply", "physical.header")])
        self.assertEqual([question["cites"] for question in result.data["open"]], [CITES] * 3)
        self.assertEqual(result.data["sources"], [{"name": "kept-documents", "where": "local"}])
        self.assertEqual(json.loads(self.replies_file.read_text())["replies"]["physical.header"]["value"], None)
        step = result.next[0]
        self.assertEqual((step.op, step.argv[-3:], step.why, step.needs_person), ("research-part", ["--replies", str(self.replies_file), "--json"], "3 open", None))
        self.assertEqual(result.lines[0], "sources: 1 kept-documents (local)")
        self.assertEqual((self.record(), result.notes), (RECORD, None))
        self.assertIn('"next"', JsonEnvelope.render(result, "research-part", "research-part"))

    def test_run_2_writes_the_record_and_a_rerun_with_the_same_file_adds_nothing(self):
        self.research(DeferringReplyStrategy())
        RepliesStore(self.replies_file).dump([])
        held = json.loads(self.replies_file.read_text())
        held["replies"].update({key: {"value": answer.value, "cites": CITES} for key, answer in ANSWERS.items()})
        self.replies_file.write_text(json.dumps(held))
        result = self.research(reply_strategy_for(self.replies_file), self.replies_file)
        self.assertEqual((result.status(), result.data["written"], result.notes),
                         ("ok", ["physical", "physical_proof"], ["record written: physical, physical_proof (unverified)"]))
        self.assertEqual(self.record()["physical"], {"thickness_mm": 1, "mounting_holes": HOLES, "header": HEADER})
        self.assertEqual(validate(self.record(), self.path), [])
        again = self.research(reply_strategy_for(self.replies_file), self.replies_file)
        self.assertEqual((again.status(), again.data["gaps"], again.data["written"], again.lines[1]),
                         ("ok", [], [], "no gaps: every fact the needs file lists is held or named in physical_proof.not_published"))

    def test_a_stray_key_and_a_reply_that_would_change_a_held_fact_are_problems_and_nothing_is_written(self):
        self.replies_file.parent.mkdir()
        self.replies_file.write_text(json.dumps({"replies": {"physical.thicknes_mm": 1, "body_mm": {"value": {"width": 17, "height": 11}}}}))
        result = self.research(reply_strategy_for(self.replies_file), self.replies_file)
        self.assertEqual(result.status(), "problems")
        self.assertEqual([(found.code, found.subject) for found in result.findings if found.severity == "problems"],
                         [("unknown_reply", "physical.thicknes_mm"), ("unknown_reply", "body_mm")])
        self.assertIn("physical.thickness_mm", result.findings[0].fix)
        self.assertEqual(self.record(), RECORD)

    def test_a_mixed_run_writes_the_answered_and_keeps_the_rest_open(self):
        two = {key: answer for key, answer in ANSWERS.items() if key != "physical.header"}
        result = self.research(GivenReplyStrategy(two))
        self.assertEqual((result.status(), result.data["written"], [q["key"] for q in result.data["open"]]),
                         ("could-not-run", ["physical", "physical_proof"], ["physical.header"]))
        self.assertEqual(self.record()["physical"], {"thickness_mm": 1, "mounting_holes": HOLES})
        self.assertEqual(list(json.loads(self.replies_file.read_text())["replies"]), ["physical.header"])

    def test_a_record_broken_before_research_is_still_written_when_the_fold_adds_no_problem(self):
        broken = {key: value for key, value in RECORD.items() if key != "pin_order_proof"}
        self.path.write_text(json.dumps(broken))
        result = self.research(GivenReplyStrategy(ANSWERS))
        self.assertEqual((result.status(), result.data["written"]), ("ok", ["physical", "physical_proof"]))
        self.assertEqual(self.record()["physical"]["header"], HEADER)

    def test_a_value_the_contract_refuses_is_a_problem_and_nothing_is_written(self):
        bad = dict(ANSWERS, **{"physical.thickness_mm": reply("physical.thickness_mm", -1)})
        result = self.research(GivenReplyStrategy(bad))
        self.assertEqual((result.status(), [found.code for found in result.findings]), ("problems", ["part_contract_broken"]))
        self.assertEqual(self.record(), RECORD)

    def test_an_unknown_id_is_no_such_part_not_a_crash_and_the_text_run_says_it(self):
        result = run_operation(ResearchPart(), {"part": "nope", "project": self.project, "replies": None}, FakeOutsideWorld(replies=DeferringReplyStrategy()))
        self.assertEqual([(found.code, found.severity) for found in result.findings], [("no_such_part", "could-not-run")])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = research.main(["--part", "nope", "--project", str(self.project)])
        self.assertEqual(code, 2)
        self.assertTrue(out.getvalue().startswith("  no_such_part: no part called 'nope'"), out.getvalue())
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = research.main(["--part", "x-mod", "--project", str(self.project), "--replies", str(self.project / "none.json")])
        self.assertEqual((code, out.getvalue()[:33], "cannot be read" in out.getvalue()), (2, "  bad_argument: the replies file ", True))

    def test_a_library_record_is_refused_and_a_record_with_no_gaps_writes_no_file(self):
        result = run_operation(ResearchPart(), {"part": "led-red-5mm", "project": self.project, "replies": None},
                               FakeOutsideWorld(replies=DeferringReplyStrategy()))
        self.assertEqual([found.code for found in result.findings], ["bad_argument"])
        proof = {"verified": False, "source": "s", "why_it_matters": "w", "not_published": ["thickness_mm", "mounting_holes", "header"]}
        self.path.write_text(json.dumps(dict(RECORD, physical_proof=proof)))
        result = self.research(DeferringReplyStrategy())
        self.assertEqual((result.status(), result.data["gaps"], self.replies_file.exists()), ("ok", [], False))

    def test_the_script_prints_the_envelope_and_a_missing_replies_file_is_a_bad_argument(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = research.main(["--part", "x-mod", "--project", str(self.project), "--json"], outside=FakeOutsideWorld(replies=DeferringReplyStrategy()))
        self.assertEqual((code, len(json.loads(out.getvalue())["data"]["open"])), (2, 3))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = research.main(["--part", "x-mod", "--project", str(self.project), "--replies", str(self.project / "none.json"), "--json"])
        self.assertEqual((code, json.loads(out.getvalue())["unchecked"][0]["code"]), (2, "bad_argument"))


if __name__ == "__main__":
    unittest.main()
