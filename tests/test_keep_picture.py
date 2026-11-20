"""
Proof that `parts.py --keep-picture` keeps a part's picture with its record, all or nothing, and that
`parts.py --picture-frame` prints the frame to draw it on (P946 #1349).

    python3 -m unittest tests.test_keep_picture
"""

import contextlib
import hashlib
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

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import parts  # noqa: E402

FIXTURE = ROOT / "tests" / "data" / "pictures" / "epaper-synthetic.svg"
EPAPER = ROOT / "tests" / "data" / "breadboard" / "epaper"
PART = "epaper-2in9-bwr-mh-et-live"
KEEP = ["--part", PART, "--made-by", "drawing", "--likeness", "near", "--credit", "a synthetic picture"]


def run(argv, json_out=True):
    """parts.py: (the envelope, or the text it printed, and its exit code)."""
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
        code = parts.main(argv + (["--json"] if json_out else []))
    return (json.loads(out.getvalue()) if json_out else out.getvalue()), code


class KeepPictureTest(unittest.TestCase):
    def setUp(self):
        self.home, scratch = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.home, True)
        self.addCleanup(shutil.rmtree, scratch, True)
        environment = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        environment.start()
        self.addCleanup(environment.stop)
        self.project = scratch / "epaper"
        shutil.copytree(EPAPER, self.project)
        (self.project / ".spark").mkdir(exist_ok=True)
        self.record_path = self.project / "parts" / (PART + ".json")
        self.picture = scratch / "epaper-breadboard-top.svg"
        shutil.copy(FIXTURE, self.picture)

    def keep(self, *more, picture=None):
        return run(["--keep-picture", str(picture or self.picture)] + KEEP + ["--project", str(self.project)] + list(more))

    def record(self):
        return json.loads(self.record_path.read_text())

    def test_the_dry_run_writes_nothing_and_says_what_it_would_set(self):
        before = self.record_path.read_bytes()
        said, code = self.keep("--dry-run")
        self.assertEqual((said["status"], code, said["data"]["written"]), ("ok", 0, False))
        self.assertEqual(said["data"]["picture"]["document"], said["data"]["key"])
        self.assertEqual(self.record_path.read_bytes(), before)
        self.assertFalse((self.home / "sources").exists())

    def test_keep_picture_lists_the_document_and_the_view_in_one_write(self):
        said, code = self.keep()
        self.assertEqual((said["status"], code), ("ok", 0))
        record = self.record()
        key = said["data"]["key"]
        sha = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
        self.assertEqual((record["documents"][key]["sha256"], record["documents"][key]["file"]), (sha, "epaper-breadboard-top.svg"))
        self.assertEqual(record["pictures"], {"breadboard-top": {"document": key, "made_by": "drawing", "likeness": "near",
                                                                 "credit": "a synthetic picture", "verified": False}})
        self.assertEqual((self.home / "sources" / sha / "epaper-breadboard-top.svg").read_bytes(), FIXTURE.read_bytes())
        self.assertIn("txs0108e", record["documents"])  # the record's own documents stay

    def test_a_refused_picture_keeps_nothing(self):
        before = self.record_path.read_bytes()
        self.picture.write_text(FIXTURE.read_text().replace('viewBox="0 0 85 44"', 'viewBox="0 0 90 44"'))
        said, code = self.keep()
        self.assertEqual((said["status"], code, [item["code"] for item in said["problems"]]), ("problems", 1, ["picture_view_box"]))
        self.assertEqual(said["problems"][0]["subject"], "svg")
        self.assertEqual(self.record_path.read_bytes(), before)
        self.assertFalse((self.home / "sources").exists())

    def test_a_record_whose_documents_or_pictures_is_no_object_is_refused_and_keeps_nothing(self):
        for field in ("documents", "pictures"):
            with self.subTest(field=field):
                record = json.loads((EPAPER / "parts" / (PART + ".json")).read_text())
                record[field] = ["x"]
                self.record_path.write_text(json.dumps(record))
                before = self.record_path.read_bytes()
                said, code = self.keep()
                self.assertEqual((said["status"], code), ("problems", 1))
                self.assertIn("%s is not an object" % field, said["problems"][0]["sentence"])
                self.assertEqual(self.record_path.read_bytes(), before)
                self.assertFalse((self.home / "sources").exists())

    def test_a_missing_file_could_not_run(self):
        said, code = self.keep(picture=self.picture.with_name("absent.svg"))
        self.assertEqual((said["status"], code, said["unchecked"][0]["code"]), ("could-not-run", 2, "file_refused"))

    def test_spark_s_library_a_board_and_a_record_with_no_frame_are_refused(self):
        for part_id in ("dfr0534-module", "firebeetle2-esp32s3", "nobody"):
            with self.subTest(part=part_id):
                said, code = run(["--keep-picture", str(self.picture), "--part", part_id, "--made-by", "drawing", "--likeness",
                                  "near", "--credit", "c", "--project", str(self.project)])
                self.assertEqual((said["status"], code, said["problems"][0]["subject"]), ("problems", 1, part_id))
        record = self.record()
        del record["physical"]
        self.record_path.write_text(json.dumps(record))
        said, code = self.keep()
        self.assertEqual((said["status"], code), ("problems", 1))
        self.assertIn("physical", said["problems"][0]["sentence"])
        self.assertFalse((self.home / "sources").exists())

    def test_each_required_argument_is_required(self):
        for missing in ("--part", "--made-by", "--likeness", "--credit"):
            with self.subTest(missing=missing):
                at = KEEP.index(missing)
                argv = ["--keep-picture", str(self.picture)] + KEEP[:at] + KEEP[at + 2:] + ["--project", str(self.project)]
                said, code = run(argv)
                self.assertEqual(code, 2, said)
        said, code = run(["--keep-picture", str(self.picture)] + KEEP[:4] + ["--likeness", "perfect"] + KEEP[6:])
        self.assertEqual(code, 2, said)

    def test_verified_follows_the_frame_size(self):
        self.keep()
        self.assertIs(self.record()["pictures"]["breadboard-top"]["verified"], False)
        record = self.record()
        record["body_mm"]["verified"] = True
        self.record_path.write_text(json.dumps(record))
        self.keep()
        self.assertIs(self.record()["pictures"]["breadboard-top"]["verified"], True)

    def test_a_second_keep_of_the_view_replaces_its_block_and_keeps_both_documents(self):
        first, _ = self.keep()
        self.picture.write_text(FIXTURE.read_text().replace("#1a5e9a", "#2b6fab"))
        second, code = self.keep()
        self.assertEqual(code, 0)
        record = self.record()
        self.assertNotEqual(first["data"]["key"], second["data"]["key"])
        self.assertIn(first["data"]["key"], record["documents"])
        self.assertEqual(record["pictures"]["breadboard-top"]["document"], second["data"]["key"])


class PictureFrameTest(unittest.TestCase):
    def test_picture_frame_prints_the_svg_alone_and_its_json(self):
        text, code = run(["--picture-frame", PART, "--project", str(EPAPER)], json_out=False)
        self.assertEqual(code, 0)
        self.assertTrue(text.startswith("<svg "), text[:40])
        self.assertTrue(text.rstrip().endswith("</svg>"))
        self.assertIn('viewBox="0 0 85 44"', text)
        said, code = run(["--picture-frame", PART, "--project", str(EPAPER)])
        self.assertEqual((said["data"]["view_box"], said["data"]["made_by"], said["data"]["likeness"]), ([0, 0, 85, 44], "frame", "rough"))
        self.assertEqual(said["data"]["svg"].strip(), text.strip())

    def test_a_board_has_its_frame_too(self):
        said, code = run(["--picture-frame", "firebeetle2-esp32s3"])
        self.assertEqual((code, said["data"]["view_box"]), (0, [0, 0, 25.4, 60]))

    def test_picture_frame_of_a_record_with_no_physical_block_names_the_field(self):
        scratch = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, scratch, True)
        shutil.copytree(EPAPER, scratch / "epaper")
        path = scratch / "epaper" / "parts" / (PART + ".json")
        record = json.loads(path.read_text())
        del record["physical"], record["physical_proof"]
        path.write_text(json.dumps(record))
        said, code = run(["--picture-frame", PART, "--project", str(scratch / "epaper")])
        self.assertEqual((said["status"], code, said["problems"][0]["subject"]), ("problems", 1, PART))
        self.assertIn("(physical)", said["problems"][0]["sentence"])
        said, code = run(["--picture-frame", "nobody-at-all"])
        self.assertEqual((said["status"], code), ("problems", 1))


if __name__ == "__main__":
    unittest.main()
