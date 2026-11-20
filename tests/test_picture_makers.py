"""
Proof that a part's picture comes from an ordered list of exchangeable makers (P946 #1349): the first that answers gives
the picture, each one says what it uses, and the build draws a kept picture with spark's pads and labels over it.

    python3 -m unittest tests.test_picture_makers
"""

import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ElementTree
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.breadboard import drawing, part_pictures, picture_makers, sheet, svg_diagram  # noqa: E402
from spark.breadboard.picture_makers import (  # noqa: E402
    Decline, FramePictureMaker, MadePartPictures, PartPictureMaker, PictureCandidate, PictureMakerChain, PictureRequest,
    StoredPictureMaker)

FIXTURE = ROOT / "tests" / "data" / "pictures" / "epaper-synthetic.svg"
EPAPER_FOLDER = ROOT / "tests" / "data" / "breadboard" / "epaper"
EPAPER = EPAPER_FOLDER / "parts" / "epaper-2in9-bwr-mh-et-live.json"
SVG = "{http://www.w3.org/2000/svg}"


def epaper():
    return json.loads(EPAPER.read_text())


def keep(home, data, name="epaper-breadboard-top.svg"):
    """The documents entry of `data` put in the store at `home` as `keep` would put it."""
    sha = hashlib.sha256(data).hexdigest()
    folder = Path(home) / "sources" / sha
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_bytes(data)
    return {"url": None, "file": name, "sha256": sha}


def kept_epaper(home, data=None):
    """The e-paper's record with the synthetic picture kept in the store at `home` and listed as its breadboard-top."""
    record = epaper()
    record["documents"]["picture"] = keep(home, data or FIXTURE.read_bytes())
    record["pictures"] = {"breadboard-top": {"document": "picture", "made_by": "photo", "likeness": "near",
                                             "credit": "a synthetic picture", "verified": False}}
    return record


def request(record):
    return PictureRequest(record, "breadboard-top", picture_makers.shape_of(record))


class FakeMaker(PartPictureMaker):
    """Fake: a maker that answers with a marked candidate, or declines, and counts its calls."""

    def __init__(self, name, answers):
        self.NAME, self.answers, self.calls = name, answers, 0

    def uses(self):
        return picture_makers.MakerUses((), (), None, False)

    def make(self, request):
        self.calls += 1
        if not self.answers:
            return Decline(self.NAME, "the fake declines", ())
        return PictureCandidate("<rect/>", (0, 0, 1, 1), self.NAME, "rough", "the fake %s" % self.NAME)


class TheChainTest(unittest.TestCase):
    def test_the_first_maker_that_answers_gives_the_picture_and_the_declines_before_it(self):
        makers = [FakeMaker("a", False), FakeMaker("b", True), FakeMaker("c", True)]
        result = PictureMakerChain(makers).first(request(epaper()))
        self.assertEqual(result.candidate.made_by, "b")
        self.assertEqual([decline.maker for decline in result.declines], ["a"])
        self.assertEqual([maker.calls for maker in makers], [1, 1, 0])

    def test_no_maker_answers_gives_no_candidate_and_every_decline(self):
        result = PictureMakerChain([FakeMaker("a", False), FakeMaker("b", False)]).first(request(epaper()))
        self.assertEqual((result.candidate, [decline.maker for decline in result.declines]), (None, ["a", "b"]))

    def test_a_reordered_list_changes_which_maker_answers(self):
        one, other = FakeMaker("one", True), FakeMaker("other", True)
        self.assertEqual(PictureMakerChain([one, other]).first(request(epaper())).candidate.made_by, "one")
        self.assertEqual(PictureMakerChain([other, one]).first(request(epaper())).candidate.made_by, "other")
        home = tempfile.mkdtemp()
        with mock.patch.dict(os.environ, {"SPARK_HOME": home}):
            record = kept_epaper(home)
            stored_first = PictureMakerChain([StoredPictureMaker(), FramePictureMaker()]).first(request(record))
            frame_first = PictureMakerChain([FramePictureMaker(), StoredPictureMaker()]).first(request(record))
        self.assertEqual((stored_first.candidate.made_by, stored_first.candidate.likeness), ("photo", "near"))
        self.assertEqual((frame_first.candidate.made_by, frame_first.candidate.likeness), ("frame", "rough"))

    def test_the_build_s_order_is_the_stored_maker_alone(self):
        self.assertEqual(picture_makers.BUILD_MAKERS, ("stored",))
        self.assertEqual(sorted(picture_makers.MAKERS), ["frame", "stored"])

    def test_every_maker_says_what_it_uses(self):
        self.assertEqual(StoredPictureMaker().uses(), picture_makers.MakerUses((), ("kept-file",), None, False))
        self.assertEqual(FramePictureMaker().uses(), picture_makers.MakerUses((), ("physical",), None, False))
        self.assertEqual((StoredPictureMaker.NAME, FramePictureMaker.NAME), ("stored", "frame"))


class TheStoredMakerTest(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp()
        environment = mock.patch.dict(os.environ, {"SPARK_HOME": self.home})
        environment.start()
        self.addCleanup(environment.stop)
        self.addCleanup(shutil.rmtree, self.home, True)

    def test_it_reads_the_kept_file_by_its_sha256(self):
        made = StoredPictureMaker().make(request(kept_epaper(self.home)))
        self.assertIsInstance(made, PictureCandidate)
        self.assertEqual((made.view_box, made.credit), ((0.0, 0.0, 85.0, 44.0), "a synthetic picture"))
        self.assertIn("data:image/jpeg;base64,", made.markup)
        self.assertNotIn("<title", made.markup)

    def test_it_declines_each_broken_input_and_never_raises(self):
        def changed(change):
            record = kept_epaper(self.home)
            change(record)
            return record

        def bytes_changed(record):
            entry = record["documents"]["picture"]
            (Path(self.home) / "sources" / entry["sha256"] / entry["file"]).write_bytes(b"<svg/>")

        def refused(record):
            record["documents"]["picture"] = keep(self.home, FIXTURE.read_bytes().replace(b"<rect x=\"68\"", b"<script/><rect x=\"68\""))

        cases = {
            "no pictures": (lambda record: record.pop("pictures"), "no kept picture for breadboard-top"),
            "pictures no object": (lambda record: record.update(pictures=["x"]), "no kept picture for breadboard-top"),
            "no block for the view": (lambda record: record["pictures"].pop("breadboard-top"), "no kept picture for breadboard-top"),
            "a document key not in documents": (lambda record: record["pictures"]["breadboard-top"].update(document="other"),
                                                "the document 'other' names no kept file"),
            "documents no object": (lambda record: record.update(documents=[]), "the document 'picture' names no kept file"),
            "an entry with no plain file name": (lambda record: record["documents"]["picture"].update(file="../x.svg"),
                                                 "the document 'picture' names no kept file"),
            "a file not in the store": (lambda record: record["documents"]["picture"].update(sha256="b" * 64),
                                        "the kept file is not in the store"),
            "changed bytes": (bytes_changed, "the kept file's bytes are not the ones kept"),
            "a picture the check refuses": (refused, "the picture breaks picture_element at svg/script[0]"),
        }
        for name, (change, reason) in cases.items():
            with self.subTest(name):
                made = StoredPictureMaker().make(request(changed(change)))
                self.assertIsInstance(made, Decline)
                self.assertEqual((made.maker, made.reason), ("stored", reason))

    def test_a_missing_picture_names_the_command_that_keeps_one(self):
        record = epaper()
        made = StoredPictureMaker().make(request(record))
        self.assertEqual(made.missing, ("pictures.breadboard-top: parts.py --keep-picture FILE --part epaper-2in9-bwr-mh-et-live "
                                        "--project .",))

    def test_a_picture_of_another_size_than_the_frame_declines(self):
        record = kept_epaper(self.home, FIXTURE.read_bytes().replace(b'viewBox="0 0 85 44"', b'viewBox="0 0 90 44"'))
        self.assertEqual(StoredPictureMaker().make(request(record)).reason, "the picture breaks picture_view_box at svg")


class TheFrameMakerTest(unittest.TestCase):
    def test_the_frame_is_the_body_with_a_ring_and_a_label_per_pad_in_the_guide_group(self):
        record = epaper()
        text = FramePictureMaker().svg(picture_makers.shape_of(record))
        root = ElementTree.fromstring(text)
        self.assertEqual((root.get("viewBox"), root.get("width"), root.get("height")), ("0 0 85 44", "85mm", "44mm"))
        guide = root.find(SVG + "g")
        self.assertEqual(guide.get("data-guide"), "pads")
        rings = [(float(ring.get("cx")), float(ring.get("cy"))) for ring in guide.iter(SVG + "circle")]
        shape = picture_makers.shape_of(record)
        self.assertEqual(rings, [tuple(place) for place in shape.pins.values()])
        self.assertEqual([text.text for text in guide.iter(SVG + "text")],
                         ["VCC", "GND", "SDI", "SCLK", "CS", "D/C", "Reset", "Busy"])
        made = FramePictureMaker().make(request(record))
        self.assertEqual((made.made_by, made.likeness, made.credit), ("frame", "rough", "spark's frame of epaper-2in9-bwr-mh-et-live"))

    def test_a_board_s_frame_is_its_outline_and_its_pads(self):
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        root = ElementTree.fromstring(FramePictureMaker().svg(picture_makers.shape_of(board)))
        self.assertEqual(root.get("viewBox"), "0 0 25.4 60")
        self.assertEqual(len(list(root.iter(SVG + "circle"))), 32)

    def test_a_record_with_no_physical_block_gets_no_frame_and_the_decline_names_the_field(self):
        record = epaper()
        del record["physical"]
        self.assertIsNone(picture_makers.shape_of(record))
        made = FramePictureMaker().make(request(record))
        self.assertEqual((made.maker, made.missing[0].split(":")[0]), ("frame", "physical"))

    def test_a_record_that_lacks_a_field_of_its_frame_raises_with_the_field(self):
        record = epaper()
        del record["body_mm"]["width"]
        with self.assertRaises(drawing.NotDrawnError) as caught:
            picture_makers.shape_of(record)
        self.assertEqual(caught.exception.subject, "body_mm.width")


class TheBuildDrawsAKeptPictureTest(unittest.TestCase):
    """The e-paper fixture built with its synthetic picture kept in a temporary store."""

    def draw(self, change=None):
        home = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, home, True)
        project = Path(tempfile.mkdtemp()) / "epaper"
        self.addCleanup(shutil.rmtree, project.parent, True)
        shutil.copytree(EPAPER_FOLDER, project)
        record = kept_epaper(home)
        if change:
            change(home, record)
        (project / "parts" / EPAPER.name).write_text(json.dumps(record, indent=2))
        with mock.patch.dict(os.environ, {"SPARK_HOME": home}):
            read = sheet._read_build(project / "requirements.json")
            layout = drawing.BreadboardPlanner(*sheet._drawing_inputs(read)).plan(read.steps)
            pictures = MadePartPictures(PictureMakerChain([StoredPictureMaker()]), part_pictures.PictogramPartPictures())
            return ElementTree.fromstring(svg_diagram.SvgBreadboardDiagram(pictures=pictures).text(layout))

    def test_a_kept_picture_replaces_the_box_and_spark_draws_every_pad_and_label_over_it(self):
        root = self.draw()
        groups = list(root)
        picture = next(index for index, group in enumerate(groups) if group.get("data-part") == "Epaper2in9BwrMhEtLive")
        self.assertEqual(len(list(groups[picture].iter(SVG + "image"))), 1)
        self.assertEqual(groups[picture].find(SVG + "title").text, "a synthetic picture")
        for label in ("GND", "SDI", "SCLK", "CS", "D/C", "Reset", "Busy"):  # VCC is the FireBeetle's pad too
            with self.subTest(label=label):
                drawn = [index for index, element in enumerate(groups)
                         for text in element.iter(SVG + "text") if text.text == label]
                self.assertEqual(len(drawn), 1)
                self.assertGreater(drawn[0], picture)

    def test_a_kept_picture_that_fails_is_the_box_with_a_note(self):
        def broken(home, record):
            entry = record["documents"]["picture"]
            (Path(home) / "sources" / entry["sha256"] / entry["file"]).write_bytes(b"<svg/>")

        root = self.draw(broken)
        group = next(group for group in root if group.get("data-part") == "Epaper2in9BwrMhEtLive")
        self.assertEqual(list(group.iter(SVG + "image")), [])
        notes = [text.text for text in root.iter(SVG + "text") if text.text and "kept picture not shown" in text.text]
        self.assertEqual(len(notes), 1)
        self.assertIn("e-paper: kept picture not shown (the kept file's bytes are not the ones kept)", notes[0])

    def test_a_part_with_no_kept_picture_keeps_its_pictogram_and_no_note(self):
        root = self.draw(lambda home, record: record.pop("pictures"))
        self.assertFalse([text for text in root.iter(SVG + "text") if text.text and "kept picture" in text.text])
        board = next(group for group in root if group.get("data-part") == "board")
        self.assertTrue(any(rect.get("fill") == "#16202a" for rect in board.iter(SVG + "rect")))

    def test_the_sheet_draws_with_the_build_s_makers(self):
        renderer = next(one for one in sheet.DRAWING_RENDERERS if isinstance(one, svg_diagram.SvgBreadboardDiagram))
        self.assertIsInstance(renderer.pictures, MadePartPictures)
        self.assertEqual([maker.NAME for maker in renderer.pictures.chain.makers], ["stored"])


if __name__ == "__main__":
    unittest.main()
