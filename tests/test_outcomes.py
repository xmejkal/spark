"""
Proof that the three outcomes are one definition, and that every script answers in them.

    python3 -m unittest discover -s tests
"""

import contextlib
import importlib
import io
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
sys.path.insert(0, str(ROOT / "tools"))  # `mutate`, which test_every_script_answers_in_the_one_vocabulary imports

import board_facts  # noqa: E402
import boards  # noqa: E402
import outcomes  # noqa: E402
import run_scenario  # noqa: E402
import sim_project  # noqa: E402
from test_boards import DEFINITION, kept_definition_board  # noqa: E402

MAC = "8c:bf:ea:cc:97:70"
GOOD_RECORD = ('{"mac": "8c:bf:ea:cc:97:70", "deploys": [{"project": "blink", "verdict": "ready seen", '
               '"deployed": "2026-10-19T09:24:50+02:00"}]}')
LOG_HEADER = "# a, run 2026-10-24T10:00:00, timeout 1 ms\nverdict: passed\n"

#: Every script that exits with the three-way answer, and the local word it uses for "no".
SCRIPTS = {
    "check_all": "EXIT_PROBLEMS", "check_spine": "EXIT_PROBLEMS",
    "check_bom": "EXIT_PROBLEMS", "check_footprints": "EXIT_PROBLEMS", "check_physics": "EXIT_PROBLEMS",
    "emit_footprint": "EXIT_PROBLEMS", "assign_pins": "EXIT_IMPOSSIBLE", "init_project": "EXIT_NOTHING_TO_DO",
    "check_vendor_pins": "EXIT_MISMATCH", "mutate": "EXIT_ESCAPED", "boards": "EXIT_INVALID",
    "parts": "EXIT_INVALID",
}


class ThreeOutcomesTest(unittest.TestCase):
    def test_the_codes_are_zero_one_two_and_distinct(self):
        self.assertEqual((outcomes.EXIT_OK, outcomes.EXIT_PROBLEMS, outcomes.EXIT_COULD_NOT_RUN), (0, 1, 2))

    def test_every_status_word_has_its_code(self):
        self.assertEqual(outcomes.EXIT_FOR[outcomes.COULD_NOT_RUN], outcomes.EXIT_COULD_NOT_RUN)
        self.assertEqual(set(outcomes.EXIT_FOR), {outcomes.OK, outcomes.PROBLEMS, outcomes.COULD_NOT_RUN})

    def test_the_two_maps_are_each_other_reversed(self):
        # Five scripts wrote EXIT_FOR inline and two wrote its inverse; P42 gave both one home,
        # so a mutation that breaks the round trip must be caught here or nowhere.
        self.assertEqual(set(outcomes.STATUS_FOR), {0, 1, 2})
        for status, code in outcomes.EXIT_FOR.items():
            self.assertEqual(outcomes.STATUS_FOR[code], status)
        for code, status in outcomes.STATUS_FOR.items():
            self.assertEqual(outcomes.EXIT_FOR[status], code)

    def test_the_rule_itself(self):
        # The expression six scripts used to restate, one of them wrongly (P34).
        self.assertEqual(outcomes.status_of(), outcomes.OK)
        self.assertEqual(outcomes.status_of(unchecked=["a rail nobody stated"]), outcomes.COULD_NOT_RUN)
        self.assertEqual(outcomes.status_of(problems=["a short"]), outcomes.PROBLEMS)
        self.assertEqual(outcomes.status_of(problems=["a short"], unchecked=["and one unread"]), outcomes.PROBLEMS)

    def test_the_answer_a_check_hands_back(self):
        self.assertEqual(outcomes.answer(), {"status": outcomes.OK, "problems": [], "unchecked": []})
        self.assertEqual(outcomes.answer(unchecked=["x"])["status"], outcomes.COULD_NOT_RUN)
        self.assertNotIn("unmeasured", outcomes.answer())
        self.assertEqual(outcomes.answer(unmeasured=["a current nobody took"])["unmeasured"], ["a current nobody took"])

    def test_every_script_answers_in_the_one_vocabulary(self):
        for name, no in SCRIPTS.items():
            module = importlib.import_module(name)
            self.assertIs(module.EXIT_OK, outcomes.EXIT_OK, name)
            self.assertEqual(getattr(module, no), outcomes.EXIT_PROBLEMS, name)
            if hasattr(module, "EXIT_COULD_NOT_RUN"):
                self.assertEqual(module.EXIT_COULD_NOT_RUN, outcomes.EXIT_COULD_NOT_RUN, name)


def read_last_deploy(text):
    """board_facts.read_last_deploy with `text` as the store's record of the board (None: no record), in a store of its own."""
    with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
        if text is not None:
            record = board_facts.record_path(MAC)
            record.parent.mkdir(parents=True, exist_ok=True)
            record.write_text(text)
        return board_facts.read_last_deploy(MAC)


def read_log(text):
    """ScenarioSteps.from_log with `text` as the log (None: no file)."""
    log = Path(tempfile.mkdtemp()) / "a.log"
    if text is not None:
        log.write_text(text)
    return run_scenario.ScenarioSteps.from_log(log)


def read_firmware(case):
    """sim_project.firmware_in with `case` as the wokwi.toml: None (no file), text, ("folder", None) or ("bytes", the bytes)."""
    folder = Path(tempfile.mkdtemp())
    toml = folder / "wokwi.toml"
    if isinstance(case, tuple) and case[0] == "folder":
        toml.mkdir()
    elif isinstance(case, tuple):
        toml.write_bytes(case[1])
    elif case is not None:
        toml.write_text(case)
    return sim_project.firmware_in(toml)


def read_text(text):
    """ScenarioSteps.from_text with `text` as the scenario (None: an empty one)."""
    return run_scenario.ScenarioSteps.from_text(text or "")


def read_definition(case):
    """
    boards.read_simulated_part with `case` as what the board's record holds for its Wokwi definition: None (the record names
    none), text (the kept file's bytes), ("entry", value) (the `documents` entry itself, whatever it is) or ("record",
    value) (the board record itself, whatever it is).
    """
    if isinstance(case, tuple) and case[0] == "record":
        board = case[1]
    elif case is None:
        board = kept_definition_board()
        del board["documents"][boards.WOKWI_DEFINITION]
    elif isinstance(case, tuple):
        board = kept_definition_board()
        board["documents"][boards.WOKWI_DEFINITION] = case[1]
    else:
        board = kept_definition_board(case)
    return boards.read_simulated_part(board)


#: Every reader that follows the rule in outcomes.py: its function from an input to a Value, and for each input the state
#: it must give, as the literal the records and goldens hold. Each has a missing, a malformed and a good input.
READERS = {
    "board_facts.read_last_deploy": (read_last_deploy, {
        "missing": (None, "none-recorded"),
        "malformed": ("{not json", "not-checked"),
        "wrong shape": ('{"deploys": 3}', "not-checked"),
        "good": (GOOD_RECORD, "recorded")}),
    "ScenarioSteps.from_log": (read_log, {
        "missing": (None, "not-checked"),
        "malformed": (LOG_HEADER + "step counts: set-control x\n\n", "not-checked"),
        "older, with no counts line": (LOG_HEADER + "\nbody\n", "none-recorded"),
        "good": (LOG_HEADER + "step counts: set-control 1, wait-serial 2\n\n", "recorded")}),
    "boards.read_simulated_part": (read_definition, {
        "missing": (None, "none-recorded"),
        "malformed": ('{"pins": ', "not-checked"),
        "wrong shape": ('{"pins": [1]}', "not-checked"),
        "entry that is null": (("entry", None), "not-checked"),
        "file name with a null byte": (("entry", {"sha256": "a" * 64, "file": "a\0b"}), "not-checked"),
        "entry with an absolute sha256": (("entry", {"sha256": "/etc", "file": "passwd"}), "not-checked"),
        "record that is a list": (("record", []), "none-recorded"),
        "good": (DEFINITION, "recorded")}),
    "sim_project.firmware_in": (read_firmware, {
        "missing": (None, "none-recorded"),
        "no firmware line": ("[wokwi]\nversion = 1\n", "none-recorded"),
        "malformed": ("firmware = {nope\n", "not-checked"),
        "a number": ("[wokwi]\nversion = 1\nfirmware = 3\n", "not-checked"),
        "an empty name": ('firmware = ""\n', "not-checked"),
        "indented": ('  firmware = "x.bin"\n', "not-checked"),
        "no spaces around the equals sign": ('firmware="x.bin"\n', "not-checked"),
        "a folder where the file goes": (("folder", None), "not-checked"),
        "bytes that are no text": (("bytes", b"\xff\xfe"), "not-checked"),
        "good": ('[wokwi]\nversion = 1\nfirmware = "flash.bin"\n', "recorded")}),
    "ScenarioSteps.from_text": (read_text, {
        "missing": (None, "none-recorded"),
        "malformed": ("steps:\n  - just-a-word\n", "not-checked"),
        "good": ("steps:\n  - wait-serial: ready\n", "recorded")}),
}


class ThreeStatesTest(unittest.TestCase):
    def test_the_three_words_and_the_sentence_that_says_one(self):
        self.assertEqual((outcomes.RECORDED, outcomes.NONE_RECORDED, outcomes.NOT_CHECKED, outcomes.NOT_CHECKED_MESSAGE),
                         ("recorded", "none-recorded", "not-checked", "not checked: %s"))

    def test_each_reader_gives_its_state_and_never_raises(self):
        for name, (read, inputs) in READERS.items():
            self.assertLessEqual({"missing", "malformed", "good"}, set(inputs), name)
            for case, (text, state) in inputs.items():
                with self.subTest(reader=name, case=case):
                    try:
                        value = read(text)
                    except Exception as error:  # the rule: a reader never raises
                        self.fail("%s raised %r" % (name, error))
                    self.assertEqual(value.state, state)
                    if state == "not-checked":
                        self.assertTrue(isinstance(value.why, str) and value.why)
                    else:
                        self.assertIsNone(value.why)


class OneUpwardWalkTest(unittest.TestCase):
    def test_the_walk_is_nearest_first_and_ends_at_the_root(self):
        import boards
        walked = boards.walk_up(ROOT / "scripts")
        self.assertEqual(walked[0], (ROOT / "scripts").resolve())
        self.assertEqual(walked[1], ROOT.resolve())
        self.assertEqual(walked[-1], Path(walked[-1].anchor))


class AnsweringParserTest(unittest.TestCase):
    """P433: a bad argument is an answer a script can give, and the usage is printed only when the script chooses."""

    def parser(self):
        parser = outcomes.AnsweringParser(prog="demo.py")
        parser.add_argument("--n", type=int)
        return parser

    def test_a_bad_argument_raises_before_argparse_prints_anything(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), self.assertRaises(outcomes.BadArgument) as raised:
            self.parser().parse_args(["--n", "x"])
        self.assertEqual((out.getvalue(), err.getvalue()), ("", ""))
        self.assertIn("invalid int value", str(raised.exception))

    def test_a_good_argument_parses(self):
        self.assertEqual(self.parser().parse_args(["--n", "3"]).n, 3)

    def test_exit_with_usage_prints_what_argparse_prints_and_exits_with_the_could_not_run_code(self):
        out, err = io.StringIO(), io.StringIO()
        parser = self.parser()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as raised:
            parser.exit_with_usage("argument --n: boom")
        self.assertEqual((raised.exception.code, out.getvalue()), (2, ""))
        self.assertEqual(err.getvalue(), "usage: demo.py [-h] [--n N]\ndemo.py: error: argument --n: boom\n")


if __name__ == "__main__":
    unittest.main()
