"""
Proof that `parts.py --features-set` writes a board's measured features into its record in mm, all or nothing, and says
each anchor's offset from its pad (P956 #1362).

    python3 -m unittest tests.test_set_features
"""

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401
import features_fixture  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import parts  # noqa: E402


def run(argv):
    """parts.py --json: (the envelope, its exit code)."""
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
        code = parts.main(argv + ["--json"])
    return json.loads(out.getvalue()), code


class SetFeaturesTest(unittest.TestCase):
    def setUp(self):
        self.home, scratch = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.home, True)
        self.addCleanup(shutil.rmtree, scratch, True)
        environment = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        environment.start()
        self.addCleanup(environment.stop)
        self.project = scratch / "project"
        (self.project / "boards").mkdir(parents=True)
        (self.project / ".spark").mkdir()
        self.record_path = self.project / "boards" / (features_fixture.BOARD_ID + ".json")
        self.record_path.write_text(json.dumps(features_fixture.board(), indent=2))
        self.file = scratch / "features.json"
        self.write_file(features_fixture.features_file())

    def write_file(self, held):
        self.file.write_text(json.dumps(held))

    def set(self, *more, part=features_fixture.BOARD_ID):
        return run(["--features-set", str(self.file), "--part", part, "--project", str(self.project)] + list(more))

    def record(self):
        return json.loads(self.record_path.read_text())

    def test_writes_a_board_record_in_the_project(self):
        envelope, code = self.set()
        self.assertEqual(code, 0, envelope)
        physical = self.record()["physical"]
        self.assertEqual(len(physical["features"]), 14)
        mcu = next(feature for feature in physical["features"] if feature["name"] == "MCU")
        self.assertEqual((mcu["x"], mcu["y"], mcu["w"], mcu["h"], mcu["verified"]), (8.0, 25.0, 4.0, 4.0, False))
        self.assertEqual(physical["colour"]["value"], "#0a3d1f")
        self.assertEqual(physical["header"], features_fixture.board()["physical"]["header"], "the rest of physical stays")
        self.assertIs(envelope["data"]["written"], True)

    def test_a_new_measurement_replaces_the_old_one_whole(self):
        self.set()
        held = features_fixture.features_file()
        held["features"] = held["features"][:2]
        self.write_file(held)
        self.assertEqual(self.set()[1], 0)
        self.assertEqual([feature["name"] for feature in self.record()["physical"]["features"]], ["H1", "USB"])

    def test_a_box_a_little_past_the_outline_is_written_inside_it(self):
        held = features_fixture.features_file()
        held["features"][8]["y_px"] = 393  # CONN at y -0.3 mm: past the top edge by less than 0.5 mm
        self.write_file(held)
        self.assertEqual(self.set()[1], 0)
        conn = next(feature for feature in self.record()["physical"]["features"] if feature["name"] == "CONN")
        self.assertEqual((conn["x"], conn["y"]), (6.0, 0))

    def test_refusal_writes_nothing(self):
        held = features_fixture.features_file()
        held["features"][2].update(x_px=165, y_px=325)  # MCU at 0.5, 4.5 mm: over the pad A1
        self.write_file(held)
        before = self.record_path.read_text()
        envelope, code = self.set()
        self.assertEqual(code, 1)
        self.assertEqual([(problem["code"], problem["subject"]) for problem in envelope["problems"]], [("feature_over_pad", "MCU")])
        self.assertEqual(self.record_path.read_text(), before)

    def test_a_file_that_cannot_be_read_is_a_problem_on_the_file(self):
        self.file.write_text("{")
        envelope, code = self.set()
        self.assertEqual((code, envelope["problems"][0]["code"]), (1, "feature_unreadable"))

    def test_dry_run_writes_nothing(self):
        before = self.record_path.read_text()
        envelope, code = self.set("--dry-run")
        self.assertEqual((code, envelope["data"]["written"]), (0, False))
        self.assertEqual(self.record_path.read_text(), before)

    def test_library_record_is_refused(self):
        envelope, code = self.set(part="firebeetle2-esp32s3")
        self.assertEqual(code, 1)
        self.assertIn("spark's own library", envelope["problems"][0]["sentence"])

    def test_a_part_s_record_is_refused_in_this_version(self):
        envelope, code = self.set(part="led-red-5mm")
        self.assertEqual(code, 1)
        self.assertEqual(envelope["problems"][0]["sentence"], "led-red-5mm is a part's record: measured features are a board's in this version")

    def test_answer_lists_anchor_offsets(self):
        held = features_fixture.features_file()
        held["anchors"][0]["y_px"] = 357  # 0.3 mm from A1
        self.write_file(held)
        envelope, _ = self.set("--dry-run")
        self.assertEqual(envelope["data"]["anchors"], [{"pad": "A1", "x": 1.11, "y": 5.3, "off_mm": 0.3},
                                                       {"pad": "B6", "x": 18.89, "y": 17.7, "off_mm": 0.0}])


if __name__ == "__main__":
    unittest.main()
