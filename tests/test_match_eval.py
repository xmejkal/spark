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

    def test_an_unknown_matcher_or_an_unreadable_file_could_not_run(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(match_eval.main(["--cases", "/nonexistent.json", "--drawer", str(a_drawer())]), 2)
            self.assertEqual(match_eval.main(["--cases", "/nonexistent.json", "--drawer", str(a_drawer()), "--matcher", "nope"]), 2)
            self.assertEqual(match_eval.main(["--cases", "/nonexistent.json", "--drawer", str(a_drawer()), "--matcher", "name-contains"]), 2)
