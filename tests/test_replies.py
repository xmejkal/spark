"""P737 step 2: the interaction mechanism. A typed Question, a Reply, the ReplyStrategy family (given ahead, or deferring), the
project's replies file, and the Findings an open list makes. No network, no terminal."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.core import outcomes  # noqa: E402
from spark.core.errors import SparkError  # noqa: E402
from spark.core.replies import (AGENT, CHOICE, EITHER, PERSON, VALUE, YES_NO, DeferringReplyStrategy, GivenReplyStrategy,  # noqa: E402
                                Question, RepliesStore, Reply, ReplyStrategy, needs_reply_findings, order_open, reply_problems)

DRAWING = {"document": "SEN0526 dimension drawing", "at": "page 1"}
HOLES = Question("physical.mounting_holes", "Where are the mounting holes?", VALUE, AGENT, why="the sheet places the module",
                 unit="mm", answer_form="a list of {x_mm, y_mm, drill_mm}", example=[{"x_mm": "<number>", "y_mm": "<number>", "drill_mm": "<number>"}],
                 cites=DRAWING)
THICK = Question("physical.thickness_mm", "How thick is the board?", VALUE, AGENT, unit="mm", cites=DRAWING)
SOLDERED = Question("header.soldered", "Is the header soldered on?", YES_NO, PERSON)
REVISION = Question("revision", "Which revision is printed on the board?", CHOICE, EITHER, choices=["V1.0", "V2.0"])


class QuestionTest(unittest.TestCase):
    def test_a_question_is_a_value_whose_dict_is_the_envelope_item(self):
        self.assertEqual(HOLES.to_dict(), {"key": "physical.mounting_holes", "text": "Where are the mounting holes?", "kind": "value", "asked_of": "agent",
                                           "why": "the sheet places the module", "unit": "mm", "answer_form": "a list of {x_mm, y_mm, drill_mm}",
                                           "example": [{"x_mm": "<number>", "y_mm": "<number>", "drill_mm": "<number>"}], "choices": None,
                                           "cites": DRAWING})
        self.assertEqual(json.loads(json.dumps(THICK.to_dict()))["cites"], DRAWING)

    def test_a_kind_or_an_asked_of_outside_the_words_is_a_defect(self):
        with self.assertRaises(ValueError):
            Question("k", "t", "maybe", AGENT)
        with self.assertRaises(ValueError):
            Question("k", "t", VALUE, "nobody")
        with self.assertRaises(ValueError):
            Question("k", "t", CHOICE, PERSON)  # a choice with no choices

    def test_misfit_says_what_a_value_lacks_and_none_when_it_fits(self):
        self.assertIsNone(SOLDERED.misfit(True))
        self.assertIn("yes or no", SOLDERED.misfit("yes"))
        self.assertIsNone(REVISION.misfit("V2.0"))
        self.assertIn("V1.0", REVISION.misfit("V3"))
        self.assertIsNone(THICK.misfit(1.6))
        self.assertIsNone(HOLES.misfit([{"x_mm": 2, "y_mm": 2, "drill_mm": 3}]))
        for empty in ("", [], {}, float("nan"), float("inf")):
            self.assertIsNotNone(THICK.misfit(empty), empty)


class StrategyTest(unittest.TestCase):
    def test_given_answers_from_the_dict_and_none_for_a_key_it_lacks(self):
        reply = Reply("physical.thickness_mm", 1.6, "replies file research-replies.json")
        strategy = GivenReplyStrategy({reply.key: reply})
        self.assertIsInstance(strategy, ReplyStrategy)
        self.assertEqual((strategy.reply(THICK), strategy.reply(HOLES)), (reply, None))

    def test_deferring_answers_nothing_and_holds_nothing(self):
        strategy = DeferringReplyStrategy()
        self.assertIsInstance(strategy, ReplyStrategy)
        self.assertEqual([strategy.reply(question) for question in (HOLES, THICK, SOLDERED)], [None, None, None])
        self.assertEqual(vars(strategy), {})


class RepliesStoreTest(unittest.TestCase):
    def setUp(self):
        self.project = Path(tempfile.mkdtemp())
        self.store = RepliesStore.for_project(self.project)

    def test_the_file_is_the_project_s_spark_folder_s(self):
        self.assertEqual(self.store.path, self.project / ".spark" / "research-replies.json")

    def test_dump_writes_a_template_with_a_null_per_open_key_and_keeps_what_is_answered(self):
        self.store.dump([HOLES, THICK])
        written = json.loads(self.store.path.read_text())
        self.assertEqual(written, {"replies": {"physical.mounting_holes": {"value": None, "note": "", "cites": DRAWING},
                                               "physical.thickness_mm": {"value": None, "note": "", "cites": DRAWING}}})
        written["replies"]["physical.thickness_mm"]["value"] = 1.6
        self.store.path.write_text(json.dumps(written))
        self.store.dump([HOLES, THICK, SOLDERED])  # a rerun adds the new key and keeps the answer
        again = json.loads(self.store.path.read_text())["replies"]
        self.assertEqual((again["physical.thickness_mm"]["value"], again["header.soldered"]), (1.6, {"value": None, "note": "", "cites": None}))

    def test_load_gives_a_reply_per_answered_key_and_leaves_a_null_out(self):
        self.store.path.parent.mkdir()
        self.store.path.write_text(json.dumps({"replies": {
            "physical.thickness_mm": {"value": 1.6, "note": "read off the side view", "cites": {"document": "SEN0526 dimension drawing", "at": "page 1"}},
            "physical.mounting_holes": {"value": None},
            "revision": "V2.0"}}))
        replies = self.store.load()
        self.assertEqual(sorted(replies), ["physical.thickness_mm", "revision"])
        self.assertEqual(replies["physical.thickness_mm"], Reply("physical.thickness_mm", 1.6, "replies file research-replies.json", None,
                                                                 "read off the side view", {"document": "SEN0526 dimension drawing", "at": "page 1"}))
        self.assertEqual(replies["revision"], Reply("revision", "V2.0", "replies file research-replies.json"))

    def test_a_missing_file_a_bad_json_and_a_wrong_shape_are_each_a_bad_argument(self):
        for text in (None, "{not json", '{"replies": [1]}', '["a"]'):
            if text is not None:
                self.store.path.parent.mkdir(exist_ok=True)
                self.store.path.write_text(text)
            with self.assertRaises(SparkError, msg=text) as refused:
                self.store.load()
            self.assertEqual(refused.exception.code, "bad_argument", text)


class OpenListTest(unittest.TestCase):
    def test_a_person_s_question_goes_first_and_the_rest_keep_their_order(self):
        self.assertEqual(order_open([HOLES, SOLDERED, THICK, REVISION]), [SOLDERED, HOLES, THICK, REVISION])

    def test_one_needs_reply_finding_per_open_question_with_the_key_the_text_and_the_file(self):
        found = needs_reply_findings([SOLDERED, HOLES], Path(".spark/research-replies.json"), "research.py --part x")
        self.assertEqual([(f.severity, f.subject, f.code) for f in found],
                         [(outcomes.COULD_NOT_RUN, "header.soldered", "needs_reply"), (outcomes.COULD_NOT_RUN, "physical.mounting_holes", "needs_reply")])
        self.assertEqual(found[0].sentence, "waiting on a reply: Is the header soldered on?")
        self.assertEqual(found[0].fix, "fill .spark/research-replies.json and run research.py --part x --replies .spark/research-replies.json")

    def test_reply_problems_name_an_unknown_key_with_the_nearest_open_one_a_filled_key_and_a_misfit(self):
        replies = {key: Reply(key, value, "replies file r.json") for key, value in
                   (("physical.mounting_hole", [{"x_mm": 1, "y_mm": 1, "drill_mm": 2}]), ("body_mm.width", 16), ("header.soldered", "yes"), ("physical.thickness_mm", 1.6))}
        found = reply_problems(replies, [HOLES, SOLDERED, THICK], filled={"body_mm.width", "body_mm.height"})
        by_subject = {f.subject: f for f in found}
        self.assertEqual(sorted(by_subject), ["body_mm.width", "header.soldered", "physical.mounting_hole"])
        self.assertTrue(all(f.severity == outcomes.PROBLEMS for f in found))
        self.assertEqual(by_subject["physical.mounting_hole"].code, "unknown_reply")
        self.assertIn("physical.mounting_holes", by_subject["physical.mounting_hole"].fix)
        self.assertEqual(by_subject["body_mm.width"].code, "unknown_reply")
        self.assertIn("not open", by_subject["body_mm.width"].sentence)
        self.assertEqual(by_subject["header.soldered"].code, "bad_reply")
        self.assertIn("yes or no", by_subject["header.soldered"].sentence)


if __name__ == "__main__":
    unittest.main()
