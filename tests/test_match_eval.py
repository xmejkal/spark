"""P211: tools/match_eval.py scores each matcher on a case file over an invented drawer."""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import match_eval  # noqa: E402


def a_drawer():
    """Ten offers, so that one past the first eight with no score is a miss: dht, f1 to f7, pir, tof, in key order."""
    folder = Path(tempfile.mkdtemp())
    said = [("tof", "distance", ["range"]), ("pir", "motion", ["people"]), ("dht", "humidity", ["air"])]
    said += [("f%d" % n, "thing", []) for n in range(1, 8)]
    for key, what, tags in said:
        (folder / (key + ".json")).write_text(json.dumps({"schema": 1, "label": key, "function": [{"does": "sense", "what": what}],
                                                         "tags": tags}))
    return folder


def a_cases_file(cases=None):
    """A real cases file, so that a refusal is about what it says it is about."""
    path = Path(tempfile.mkdtemp()) / "cases.json"
    path.write_text(json.dumps(CASES if cases is None else cases))
    return str(path)


def ran(argv):
    """match_eval.main's exit code and the envelope it printed (argv ends with --json)."""
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
        code = match_eval.main(argv)
    return code, json.loads(out.getvalue())


CASES = [{"does": "sense", "what": "range", "expect": "tof"}, {"does": "sense", "what": "lidar", "expect": "tof"},
         {"does": "sense", "what": "air", "not_first": "pir"}]


class TheEvalTest(unittest.TestCase):
    def test_word_overlap_finds_a_tag_and_a_miss_is_named(self):
        offers = match_eval.drawer_offers(a_drawer())
        said = match_eval.evaluate(match_eval.matching.MATCHERS["word-overlap"](), CASES, offers)
        self.assertEqual((said["cases"], said["rank_1"], said["shown"], said["misses"], said["precision"], said["precision_lost"]),
                         (2, 1, 1, ["sense lidar -> tof"], 1, []))

    def test_same_words_finds_neither_by_its_words(self):
        offers = match_eval.drawer_offers(a_drawer())
        said = match_eval.evaluate(match_eval.matching.MATCHERS["same-words"](), CASES, offers)
        # no exact match anywhere: ties keep the key order, so tof ranks tenth for both cases, and dht comes first for `air`
        self.assertEqual((said["rank_1"], said["shown"], len(said["misses"]), said["precision_lost"]), (0, 0, 2, []))

    def test_json_answers_for_an_agent(self):
        cases = Path(tempfile.mkdtemp()) / "cases.json"
        cases.write_text(json.dumps(CASES))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = match_eval.main(["--cases", str(cases), "--drawer", str(a_drawer()), "--json"])
        said = json.loads(out.getvalue())
        self.assertEqual((code, said["envelope"], said["status"], [m["matcher"] for m in said["data"]["matchers"]]),
                         (0, 1, "ok", ["same-words", "word-overlap"]))

    def test_a_matcher_that_is_no_matcher_for_match_is_refused_with_the_names_that_fit(self):
        for name in ("nope", "name-contains"):
            with self.subTest(matcher=name):
                code, said = ran(["--cases", a_cases_file(), "--drawer", str(a_drawer()), "--matcher", name, "--json"])
                self.assertEqual((code, said["status"]), (2, "could-not-run"))
                self.assertIn("same-words, word-overlap", said["unchecked"][0]["sentence"])

    def test_a_cases_file_that_is_not_there_could_not_run(self):
        code, said = ran(["--cases", "/nonexistent.json", "--drawer", str(a_drawer()), "--json"])
        self.assertEqual((code, said["status"]), (2, "could-not-run"))

    def test_a_missing_argument_is_the_envelope_and_not_a_usage_message(self):
        code, said = ran(["--drawer", str(a_drawer()), "--json"])
        self.assertEqual((code, said["status"]), (2, "could-not-run"))
        self.assertIn("--cases", said["unchecked"][0]["sentence"])
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as usage:
            self.assertEqual(match_eval.main(["--drawer", str(a_drawer())]), 2)
        self.assertEqual((out.getvalue().startswith("could-not-run: "), usage.getvalue()), (True, ""))

    def test_a_case_with_neither_expect_nor_not_first_could_not_run(self):
        code, said = ran(["--cases", a_cases_file([{"does": "sense", "what": "range"}]), "--drawer", str(a_drawer()), "--json"])
        self.assertEqual((code, said["status"]), (2, "could-not-run"))
        self.assertIn("expect", said["unchecked"][0]["sentence"])
        self.assertIn("not_first", said["unchecked"][0]["fix"])

    def test_a_drawer_file_that_is_not_an_object_could_not_run(self):
        for said_in_file in ("[1, 2]", "null", '"tof"', "7"):
            with self.subTest(file=said_in_file):
                folder = a_drawer()
                (folder / "odd.json").write_text(said_in_file)
                code, said = ran(["--cases", a_cases_file(), "--drawer", str(folder), "--json"])
                self.assertEqual((code, said["status"]), (2, "could-not-run"))
                self.assertIn("drawer file", said["unchecked"][0]["sentence"])
