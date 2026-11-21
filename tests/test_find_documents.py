"""
Proof that `parts.py --find-documents` keeps a DFRobot board's top view and dimension drawing in the person's store and
lists them in the board's `documents`, all or nothing, draws nothing, and fetches nothing again once they are kept
(P952 #1358). The fetch is a fake and every page is made up (`wiki_fixture`): no test reaches the network.

    python3 -m unittest tests.test_find_documents
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
import wiki_fixture as wiki  # noqa: E402
from fakes import FakeStoreFetch  # noqa: E402
from photo_fixture import photo_with_location  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import parts  # noqa: E402
from spark.core.cli import run_cli  # noqa: E402
from spark.core.operation import READS  # noqa: E402
from spark.core.outside import build_bare_outside_world  # noqa: E402
from spark.records import store  # noqa: E402
from spark.sourcing.find_documents import FindDocuments  # noqa: E402

TOP_SHA = hashlib.sha256(wiki.TOP_VIEW_BYTES).hexdigest()
DRAWING_SHA = hashlib.sha256(wiki.DRAWING_BYTES).hexdigest()


class FindDocumentsTest(unittest.TestCase):
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
        self.record_path = self.project / "boards" / (wiki.BOARD_ID + ".json")
        self.write_record(wiki.board())
        self.fetch = FakeStoreFetch(wiki.answers())

    def write_record(self, record):
        self.record_path.write_text(json.dumps(record, indent=2))

    def record(self):
        return json.loads(self.record_path.read_text())

    def find(self, *more, part=wiki.BOARD_ID, fetch=None):
        """--find-documents --json with the fake fetch: (the envelope, its exit code)."""
        argv = ["--find-documents", part, "--project", str(self.project)] + list(more) + ["--json"]
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            code = run_cli(parts.HELP, FindDocuments(fetch=fetch or self.fetch), argv, outside_builder=build_bare_outside_world)
        return json.loads(out.getvalue()), code

    def kept(self):
        """Every file in the store's sources, as sha256/name."""
        sources = store.place("sources")
        return sorted(str(one.relative_to(sources)) for one in sources.rglob("*") if one.is_file()) if sources.is_dir() else []

    def test_the_walk_c6_gets_its_top_view_and_drawing_kept_and_listed_and_a_second_run_fetches_nothing(self):
        envelope, code = self.find()
        self.assertEqual(code, 0, envelope)
        self.assertEqual(self.fetch.asked, [wiki.PAGE, wiki.TOP_VIEW, wiki.DRAWING])
        self.assertEqual(self.kept(), sorted(["%s/%s" % (TOP_SHA, "f24d6c2eaa74dacadb153d6f43c12432_0x0.png"),
                                              "%s/%s" % (DRAWING_SHA, "DFR1075_firebeetle-esp32-c6-microcontroller_dimension_v1.pdf")]))
        documents = self.record()["documents"]
        top, drawing = envelope["data"]["top_view"], envelope["data"]["drawing"]
        self.assertEqual((documents[top["key"]]["url"], documents[top["key"]]["sha256"], documents[top["key"]]["title"]),
                         (wiki.TOP_VIEW, TOP_SHA, "Board Overview"))
        self.assertEqual((documents[drawing["key"]]["url"], documents[drawing["key"]]["sha256"], documents[drawing["key"]]["title"]),
                         (wiki.DRAWING, DRAWING_SHA, "Dimension"))
        self.assertIsNone(documents[top["key"]]["version"], "a version is what the document prints (P61)")
        self.assertNotIn("pictures", self.record(), "nothing is shown: the record gets no pictures block")
        self.assertEqual((envelope["data"]["page"], envelope["data"]["written"]), (wiki.PAGE, True))
        before = self.record_path.read_text()
        envelope, code = self.find()
        self.assertEqual(code, 0, envelope)
        self.assertEqual(self.fetch.asked, [wiki.PAGE, wiki.TOP_VIEW, wiki.DRAWING], "the second run fetches nothing")
        self.assertEqual(envelope["data"]["fetched"], [])
        self.assertEqual(self.record_path.read_text(), before, "and lists nothing new")
        self.assertEqual(envelope["data"]["top_view"]["key"], top["key"])

    def test_a_listed_document_whose_file_is_not_in_the_store_is_fetched_again_and_kept_under_its_listed_file(self):
        # the walk's real case: the record lists the drawing as dimension.pdf, and the store has no file under its sha256
        record = wiki.walk_board()
        record["documents"][wiki.FOUND_KEYS[0]]["sha256"] = TOP_SHA
        record["documents"][wiki.FOUND_KEYS[1]]["sha256"] = DRAWING_SHA
        self.write_record(record)
        store.keep(wiki.TOP_VIEW_BYTES, "board-overview.png")
        before = self.record_path.read_text()
        envelope, code = self.find()
        self.assertEqual(code, 0, envelope)
        self.assertEqual(self.fetch.asked, [wiki.PAGE, wiki.DRAWING], "the kept top view is not fetched again")
        self.assertIn("%s/dimension.pdf" % DRAWING_SHA, self.kept())
        self.assertEqual(self.record_path.read_text(), before, "the same bytes are not listed twice")
        self.assertEqual(envelope["data"]["drawing"]["key"], wiki.FOUND_KEYS[1])
        self.find()
        self.assertEqual(self.fetch.asked, [wiki.PAGE, wiki.DRAWING], "a second run fetches nothing")

    def test_the_same_bytes_listed_under_another_url_are_kept_under_that_entrys_file_and_not_listed_twice(self):
        record = wiki.board()
        record["documents"]["photo"] = {"url": "https://example.net/top.png", "sha256": TOP_SHA, "file": "top.png",
                                        "retrieved": "2026-11-19", "title": "Top", "version": None}
        self.write_record(record)
        before = self.record_path.read_text()
        self.fetch.answers[wiki.PAGE] = wiki.page(documents=())
        envelope, code = self.find()
        self.assertEqual(code, 1, envelope)
        self.assertEqual(self.kept(), ["%s/top.png" % TOP_SHA])
        self.assertEqual(self.record_path.read_text(), before)
        self.assertEqual((envelope["data"]["top_view"]["key"], envelope["data"]["top_view"]["new"]), ("photo", False))

    def test_changed_bytes_at_a_listed_url_are_listed_beside_the_old_entry_with_a_note(self):
        record = wiki.board()
        record["documents"]["old-dimension"] = {"url": wiki.DRAWING, "sha256": "a" * 64, "file": "dimension.pdf",
                                                "retrieved": "2026-11-20", "title": "Dimension", "version": None}
        self.write_record(record)
        envelope, code = self.find()
        self.assertEqual(code, 0, envelope)
        documents = self.record()["documents"]
        self.assertEqual(documents["old-dimension"]["sha256"], "a" * 64, "nothing is overwritten")
        new = envelope["data"]["drawing"]["key"]
        self.assertNotEqual(new, "old-dimension")
        self.assertEqual((documents[new]["sha256"], documents[new]["file"]), (DRAWING_SHA, "dimension.pdf"))
        self.assertTrue(any("changed since 2026-11-20" in note["sentence"] for note in envelope["notes"]), envelope["notes"])

    def test_a_page_that_does_not_answer_is_could_not_run_exit_2_and_nothing_is_written(self):
        before = self.record_path.read_text()
        fetch = FakeStoreFetch({})
        envelope, code = self.find(fetch=fetch)
        self.assertEqual(code, 2)
        self.assertEqual([(item["code"], wiki.PAGE in item["sentence"]) for item in envelope["unchecked"]], [("url_unreachable", True)])
        self.assertEqual(self.record_path.read_text(), before)
        self.assertEqual(self.kept(), [])

    def test_a_file_that_does_not_answer_is_could_not_run_and_the_other_is_kept(self):
        fetch = FakeStoreFetch({wiki.PAGE: wiki.page(), wiki.DRAWING: wiki.DRAWING_BYTES})
        envelope, code = self.find(fetch=fetch)
        self.assertEqual(code, 2)
        self.assertEqual([(item["code"], wiki.TOP_VIEW in item["sentence"]) for item in envelope["unchecked"]], [("url_unreachable", True)])
        self.assertIsNone(envelope["data"]["top_view"])
        self.assertEqual([entry["url"] for entry in self.record()["documents"].values() if entry.get("sha256") == DRAWING_SHA], [wiki.DRAWING])
        self.assertNotIn(wiki.TOP_VIEW, [entry.get("url") for entry in self.record()["documents"].values()])

    def test_a_dry_run_reaches_no_url_and_names_the_page_it_would_read(self):
        before = self.record_path.read_text()
        fetch = FakeStoreFetch({})
        envelope, code = self.find("--dry-run", fetch=fetch)
        self.assertEqual(code, 0, envelope)
        self.assertEqual(fetch.asked, [])
        self.assertEqual((envelope["data"]["page"], envelope["data"]["written"]), (wiki.PAGE, False))
        self.assertEqual(self.record_path.read_text(), before)
        self.assertEqual(FindDocuments().effects_of({"dry_run": True}), (READS,), "a dry run declares no fetch")

    def test_parts_py_routes_the_flag_and_its_dry_run_reaches_no_url(self):
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            code = parts.main(["--find-documents", wiki.BOARD_ID, "--project", str(self.project), "--dry-run", "--json"])
        envelope = json.loads(out.getvalue())
        self.assertEqual((code, envelope["op"], envelope["data"]["page"]), (0, "find-documents", wiki.PAGE))

    def test_a_record_in_sparks_library_is_refused_and_nothing_is_fetched(self):
        envelope, code = self.find(part="firebeetle2-esp32s3")
        self.assertEqual(code, 1)
        self.assertIn("spark's own library", envelope["problems"][0]["sentence"])
        self.assertEqual(self.fetch.asked, [])

    def test_a_record_whose_documents_is_no_object_is_refused_and_the_store_gets_no_file(self):
        record = wiki.board()
        record["documents"] = ["not", "an", "object"]
        self.write_record(record)
        before = self.record_path.read_text()
        envelope, code = self.find()
        self.assertEqual(code, 1, envelope)
        self.assertIn("documents is not an object", envelope["problems"][0]["sentence"])
        self.assertEqual(self.kept(), [], "the record is written dry before any file is kept")
        self.assertEqual(self.record_path.read_text(), before)

    def test_a_parts_record_is_declined_naming_research_and_nothing_is_fetched(self):
        envelope, code = self.find(part="led-red-5mm")
        self.assertEqual(code, 1)
        self.assertEqual(envelope["problems"][0]["code"], "no_such_part")
        self.assertIn("research.py", envelope["problems"][0]["sentence"])
        self.assertEqual(self.fetch.asked, [])

    def test_a_board_nobody_has_is_a_problem_on_its_id(self):
        envelope, code = self.find(part="no-such-board")
        self.assertEqual((code, envelope["problems"][0]["code"], envelope["problems"][0]["subject"]), (1, "no_such_part", "no-such-board"))

    def test_a_board_of_no_known_vendor_declines_and_next_is_the_photo_step(self):
        record = wiki.board()
        record["sources"] = {"vendor": "https://wiki.seeedstudio.com/x/"}
        self.write_record(record)
        envelope, code = self.find()
        self.assertEqual(code, 1)
        self.assertEqual(envelope["problems"][0]["code"], "no_vendor_finder")
        self.assertEqual(self.fetch.asked, [])
        self.assertEqual(envelope["next"][0]["op"], "features-set")
        self.assertIs(envelope["next"][0]["needs_person"], True)

    def test_a_board_with_no_sku_declines_and_fetches_nothing(self):
        record = wiki.board()
        del record["sku"]
        self.write_record(record)
        envelope, code = self.find()
        self.assertEqual((code, envelope["problems"][0]["code"]), (1, "no_sku"))
        self.assertEqual(self.fetch.asked, [])

    def test_a_decline_names_what_is_missing_and_next_is_the_photo_step(self):
        self.fetch.answers[wiki.PAGE] = wiki.page(sections=(("h4", "Board Overview", ()), ("h4", "Pinout", (wiki.PINOUT_PICTURE,))))
        envelope, code = self.find()
        self.assertEqual(code, 1)
        self.assertEqual([problem["code"] for problem in envelope["problems"]], ["no_top_view"])
        declines = envelope["data"]["declines"]
        self.assertEqual([decline["maker"] for decline in declines], ["dfrobot"])
        self.assertTrue(declines[0]["missing"], "a decline names what is missing")
        self.assertEqual(envelope["next"][0]["op"], "features-set")
        self.assertIn("/spark:identify", envelope["next"][0]["why"])
        self.assertIs(envelope["next"][0]["needs_person"], True)
        self.assertEqual(envelope["data"]["drawing"]["key"], [key for key, entry in self.record()["documents"].items()
                                                              if entry.get("url") == wiki.DRAWING][0], "the drawing is kept on its own")

    def test_a_page_with_no_dimension_document_keeps_the_top_view_and_says_so(self):
        self.fetch.answers[wiki.PAGE] = wiki.page(documents=(("Schematics", wiki.SCHEMATICS, "application/zip"),))
        envelope, code = self.find()
        self.assertEqual(code, 1)
        self.assertEqual([problem["code"] for problem in envelope["problems"]], ["no_dimension_drawing"])
        self.assertEqual(self.fetch.asked, [wiki.PAGE, wiki.TOP_VIEW])
        self.assertIsNotNone(envelope["data"]["top_view"])

    def test_a_drawing_in_a_zip_is_listed_not_kept_and_said(self):
        zipped = "https://dfimg.dfrobot.com/wiki/1/DFR0975_dimension.zip"
        self.fetch.answers[wiki.PAGE] = wiki.page(documents=(("Dimension", zipped, "application/zip"),))
        envelope, code = self.find()
        self.assertEqual(code, 0, envelope)
        self.assertNotIn(zipped, self.fetch.asked)
        listed = [entry for entry in self.record()["documents"].values() if entry.get("url") == zipped]
        self.assertEqual(listed, [{"url": zipped, "kept": False, "title": "Dimension"}])
        self.assertIs(envelope["data"]["drawing"]["kept"], False)
        self.assertTrue(any("zip" in note["sentence"] for note in envelope["notes"]), envelope["notes"])
        self.find()
        self.assertEqual(self.fetch.asked.count(wiki.PAGE), 1, "a listed zip and a kept top view: a second run fetches nothing")

    def test_a_top_view_whose_bytes_are_a_jpeg_is_kept_and_listed_with_no_location(self):
        # a possible case: today's top view is a true PNG, but a .png name with JPEG bytes loses its GPS all the same,
        # and the listed sha256 (the dry run's) is the kept file's (the real run's)
        photo, latitude = photo_with_location()
        self.fetch.answers[wiki.TOP_VIEW] = photo
        envelope, code = self.find()
        self.assertEqual(code, 0, envelope)
        sha = self.record()["documents"][envelope["data"]["top_view"]["key"]]["sha256"]
        kept = (store.place("sources") / sha / "f24d6c2eaa74dacadb153d6f43c12432_0x0.png").read_bytes()
        self.assertNotIn(latitude, kept, "the coordinates are still in the file")
        self.assertEqual(hashlib.sha256(kept).hexdigest(), sha)

    def test_the_answer_next_is_the_features_step_with_the_top_views_key(self):
        envelope, _ = self.find()
        step = envelope["next"][0]
        self.assertEqual(step["op"], "features-set")
        self.assertEqual(step["argv"][:4], ["--features-set", "<file>", "--part", wiki.BOARD_ID])
        self.assertIn("documents.%s" % envelope["data"]["top_view"]["key"], step["why"])
        self.assertTrue(any("revision" in note["sentence"] for note in envelope["notes"]), "the top view's revision is not checked")


if __name__ == "__main__":
    unittest.main()
