"""P737: the interaction mechanism. A typed Question, a Reply, the ReplyStrategy family (given ahead, deferring, live in a terminal,
chained), the one tty adapter, the project's replies file, and the Findings an open list makes. No network; the terminal is a fake."""

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
from fakes import Stream  # noqa: E402
from spark.core.replies import (AGENT, CHOICE, EITHER, LEFT_LINE, PERSON, TYPED_BY, VALUE, YES_NO, ChainedReplyStrategy,  # noqa: E402
                                DeferringReplyStrategy, GivenReplyStrategy, Question, RepliesStore, Reply, ReplyStrategy, Terminal,
                                TerminalReplyStrategy, misfit_fix, needs_reply_findings, order_open, reply_problems)

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

    def test_chained_takes_the_first_reply_and_none_when_no_part_answers_or_the_chain_is_empty(self):
        first, second = Reply(THICK.key, 1.6, "replies file a"), Reply(THICK.key, 2.0, "replies file b")
        chain = ChainedReplyStrategy([GivenReplyStrategy({THICK.key: first}), GivenReplyStrategy({THICK.key: second, HOLES.key: second})])
        self.assertIsInstance(chain, ReplyStrategy)
        self.assertEqual((chain.reply(THICK), chain.reply(HOLES), chain.reply(SOLDERED)), (first, second, None))
        self.assertEqual(ChainedReplyStrategy([]).reply(THICK), None)


class TerminalTest(unittest.TestCase):
    def test_live_needs_both_streams_to_be_a_tty(self):
        self.assertEqual([Terminal(Stream(tty=a), Stream(tty=b)).live for a, b in ((True, True), (True, False), (False, True))], [True, False, False])

    def test_ask_shows_the_masked_guarded_prompt_and_reads_one_stripped_line_and_say_adds_a_newline(self):
        shown = Stream()
        terminal = Terminal(Stream("  1.6 \n"), shown, mask=lambda text: text.replace("/srv/person", "~"))
        self.assertEqual(terminal.ask("read /srv/person/a\x1b.pdf: "), "1.6")
        terminal.say("done /srv/person")
        self.assertEqual(shown.getvalue(), "read ~/a?.pdf: done ~\n")

    def test_ctrl_c_and_ctrl_d_are_none_and_enter_is_an_empty_line(self):
        self.assertEqual(Terminal(Stream(interrupt=True), Stream()).ask("? "), None)
        self.assertEqual(Terminal(Stream(""), Stream()).ask("? "), None)  # the end of the input: readline gives "" with no newline
        self.assertEqual(Terminal(Stream("\n"), Stream()).ask("? "), "")


class TerminalReplyStrategyTest(unittest.TestCase):
    """The questions asked live. Every test gives `user_name`, so no test reads the login."""

    def live(self, typed, question, interrupt=False):
        shown = Stream()
        strategy = TerminalReplyStrategy(Terminal(Stream(typed, interrupt=interrupt), shown), user_name=lambda: "ada")
        return strategy, strategy.reply(question), shown.getvalue()

    def test_an_agent_question_is_never_shown_and_stays_open(self):
        strategy, reply, shown = self.live("1.6\n", THICK)
        self.assertEqual((reply, shown, strategy.left), (None, "", False))

    def test_a_value_question_shows_the_text_the_hint_the_why_and_the_cited_page_and_reads_json(self):
        holes = HOLES._replace(asked_of=EITHER)
        strategy, reply, shown = self.live('[{"x_mm": 2.5, "y_mm": 2.5, "drill_mm": 3.2}]\n', holes)
        self.assertEqual(shown, "Where are the mounting holes? (mm, Enter = later)\nthe sheet places the module\nsee SEN0526 dimension drawing, page page 1\n> ")
        self.assertEqual(reply, Reply(holes.key, [{"x_mm": 2.5, "y_mm": 2.5, "drill_mm": 3.2}], TYPED_BY % "ada", None, None, DRAWING))

    def test_a_value_that_is_not_json_stays_text_and_a_number_is_a_number(self):
        thick = THICK._replace(asked_of=EITHER, cites=None, unit=None, answer_form="a number")
        self.assertEqual(self.live("1.6\n", thick)[1].value, 1.6)
        strategy, reply, shown = self.live("about two\n", thick)
        self.assertEqual((reply.value, shown.startswith("How thick is the board? (a number, Enter = later)\n> ")), ("about two", True))

    def test_a_question_with_a_unit_refuses_a_line_that_is_not_a_number_or_json_and_says_the_form(self):
        thick = THICK._replace(asked_of=EITHER, cites=None, answer_form="a number")
        strategy, reply, shown = self.live("1,6\n", thick)
        self.assertEqual((reply, shown.endswith("> the reply is '1,6', and the question takes a number or JSON in mm: a number\n")), (None, True))
        self.assertEqual(self.live("[1.6]\n", thick)[1].value, [1.6])

    def test_enter_leaves_the_question_open_and_the_person_is_not_marked_as_left(self):
        strategy, reply, shown = self.live("\n", REVISION)
        self.assertEqual((reply, strategy.left, shown.endswith("> ")), (None, False, True))

    def test_a_choice_by_number_or_by_text_and_a_stray_choice_is_said_and_stays_open(self):
        self.assertEqual(self.live("2\n", REVISION)[1].value, "V2.0")
        self.assertEqual([self.live(typed, REVISION)[1] for typed in ("0\n", "3\n", "\u00b2\n")], [None, None, None])  # out of range, a unicode digit
        strategy, reply, shown = self.live("V1.0\n", REVISION)
        self.assertEqual((reply.value, "  1 V1.0\n  2 V2.0\n> " in shown), ("V1.0", True))
        strategy, reply, shown = self.live("V3.0\n", REVISION)
        self.assertEqual((reply, shown.endswith("> the reply is 'V3.0', and the choices are V1.0, V2.0\n")), (None, True))

    def test_a_yes_or_no_takes_yes_y_no_n_and_anything_else_is_said_and_stays_open(self):
        self.assertEqual([self.live(typed, SOLDERED)[1].value for typed in ("yes\n", "Y\n", "no\n", "n\n")], [True, True, False, False])
        strategy, reply, shown = self.live("maybe\n", SOLDERED)
        self.assertEqual((reply, "(yes or no, Enter = later)" in shown, shown.endswith("takes yes or no (true or false)\n")), (None, True, True))

    def test_ctrl_d_leaves_this_and_every_later_question_open_like_ctrl_c(self):
        strategy, reply, shown = self.live("", REVISION)
        self.assertEqual((reply, strategy.left, shown.endswith("> " + LEFT_LINE + "\n")), (None, True, True))

    def test_ctrl_c_says_the_rest_stays_open_once_and_every_later_question_is_silent(self):
        strategy, reply, shown = self.live("", REVISION, interrupt=True)
        self.assertEqual((reply, strategy.left, shown.endswith("> " + LEFT_LINE + "\n")), (None, True, True))
        later = strategy.reply(SOLDERED)
        self.assertEqual((later, strategy.terminal.stdout.getvalue()), (None, shown))


class RepliesStoreTest(unittest.TestCase):
    def setUp(self):
        self.project = Path(tempfile.mkdtemp())
        self.store = RepliesStore.for_project(self.project)

    def test_the_file_is_the_project_s_spark_folder_s(self):
        self.assertEqual(self.store.path, self.project / ".spark" / "research-replies.json")

    def test_dump_with_answers_keeps_a_typed_value_and_a_null_for_the_rest(self):
        self.store.dump([THICK, HOLES], {THICK.key: Reply(THICK.key, 1.6, "typed in a terminal by ada"), HOLES.key: None})
        self.assertEqual({key: entry["value"] for key, entry in json.loads(self.store.path.read_text())["replies"].items()}, {THICK.key: 1.6, HOLES.key: None})

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
            "revision": "V2.0",
            "physical.header": {"pitch_mm": 2.54, "rows": 1}}}))
        replies = self.store.load()
        self.assertEqual(sorted(replies), ["physical.header", "physical.thickness_mm", "revision"])
        self.assertEqual(replies["physical.header"].value, {"pitch_mm": 2.54, "rows": 1}, "a bare object with no `value` key is the value (P737 step 4)")
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
            if text is not None:  # a rerun's dump reads the same file: the same coded answer, never a crash
                with self.assertRaises(SparkError, msg=text) as refused:
                    self.store.dump([THICK])
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
        self.assertEqual(by_subject["header.soldered"].fix, "answer as the question asks: true or false")  # no example: never "null"

    def test_a_bad_reply_s_fix_quotes_the_example_or_the_answer_form(self):
        self.assertEqual(misfit_fix(HOLES), 'answer as the question\'s answer_form says, for example [{"x_mm": "<number>", "y_mm": "<number>", "drill_mm": "<number>"}]')
        self.assertEqual(misfit_fix(THICK._replace(answer_form="a number in mm")), "answer as the question asks: a number in mm")
        self.assertEqual(misfit_fix(REVISION), "answer as the question asks: one of the choices")

    def test_an_unknown_key_far_from_every_open_key_and_a_reply_with_no_question_open(self):
        far = {"zzz": Reply("zzz", 1, "a test")}
        found = reply_problems(far, [HOLES, THICK])
        self.assertEqual([(f.code, f.fix) for f in found], [("unknown_reply", "remove it, or take a key from the run's data.open")])
        self.assertEqual([f.code for f in reply_problems(far, [])], ["unknown_reply"])
        self.assertEqual(reply_problems({}, [HOLES]), [])


if __name__ == "__main__":
    unittest.main()
