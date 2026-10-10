"""
Proof that the vendor check bites, and that it fails loudly when it cannot look.

This is the only check in the plugin that looks outside the project, which gives it a failure
mode none of the others have: the thing it compares against can be unreachable. A tool that
silently degrades to "no news is good news" the moment a fetch fails is worse than no tool,
because it still prints a tick and everybody believes it. So the tests below spend as much
effort on the refusals as on the detections.

The error class it exists for is a transcription. Someone reads a pinout and types numbers into
JSON, and every other check then compares things TO that file — so a wrong number is invisible
to all of them: the firmware, the board and the simulator agree, and all three are wrong
together. `D3 = GPIO3` is the canonical instance and is asserted here.

    python3 -m unittest discover -s tests
"""

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
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_vendor_pins  # noqa: E402

#: A believable fragment of an Espressif variant header, including the forms that are NOT
#: silkscreen labels and must not be demanded of a board file.
HEADER = """
#define USB_VID 0x3343
static const uint8_t TX = 43;
static const uint8_t RX = 44;
static const uint8_t SDA = 1;
static const uint8_t D3 = 38;
static const uint8_t D13 = 21;
static const uint8_t LED_BUILTIN = D13;
static const uint8_t T1 = 1;
static const uint8_t T2 = 2;
"""


class ParsingTest(unittest.TestCase):
    def test_it_reads_the_pin_aliases_and_ignores_the_rest(self):
        pins = check_vendor_pins.parse_pins(HEADER)
        self.assertEqual(pins["D3"], 38)
        self.assertEqual(pins["D13"], 21)
        self.assertEqual(pins["SDA"], 1)
        # `#define`s are not pin aliases, and an alias of an alias has no number of its own.
        self.assertNotIn("USB_VID", pins)
        self.assertNotIn("LED_BUILTIN", pins)

    def test_a_header_it_cannot_parse_yields_nothing_rather_than_a_guess(self):
        self.assertEqual(check_vendor_pins.parse_pins("/* no pins here */"), {})


class ComparisonTest(unittest.TestCase):
    def setUp(self):
        self.vendor = check_vendor_pins.parse_pins(HEADER)

    def test_the_silkscreen_read_as_a_gpio_number_is_caught(self):
        # The whole reason this check exists. D3 is GPIO38; reading the label as the number
        # gives GPIO3, which is a real pin on a real chip and therefore silent everywhere else.
        problems, compared, _ = check_vendor_pins.compare({"pins": {"D3": 3}}, self.vendor)
        self.assertEqual(len(problems), 1)
        self.assertIn("GPIO3 in the board file but GPIO38", problems[0])
        self.assertEqual(compared, 1)

    def test_a_correct_map_is_silent(self):
        problems, compared, _ = check_vendor_pins.compare(
            {"pins": {"D3": 38, "D13": 21, "SDA": 1}}, self.vendor)
        self.assertEqual(problems, [])
        self.assertEqual(compared, 3)

    def test_a_label_the_vendor_never_defines_is_caught(self):
        problems, _, _ = check_vendor_pins.compare({"pins": {"INVENTED": 15}}, self.vendor)
        self.assertEqual(len(problems), 1)
        self.assertIn("defines no pin called", problems[0])

    def test_an_unrecorded_vendor_pin_is_noted_but_is_not_a_failure(self):
        # Not knowing about a pin is worth reporting; it is not a wrong pin map.
        problems, _, missing = check_vendor_pins.compare({"pins": {"D3": 38}}, self.vendor)
        self.assertEqual(problems, [])
        self.assertIn("SDA", missing)
        # Touch-sensor aliases and LED_BUILTIN are not silkscreen labels; demanding them would
        # make every board file noisy for no gain.
        self.assertNotIn("T1", missing)
        self.assertNotIn("LED_BUILTIN", missing)


class ARefusalIsNotAPass(unittest.TestCase):
    """
    Every way this check can fail to look must be distinguishable from finding nothing.

    `status` is the contract. "ok" means it compared and agreed; "could-not-run" means it never
    compared at all, and the exit codes differ so a caller that reads only the code can still
    tell those apart.
    """

    def _board_file(self, contents):
        directory = Path(tempfile.mkdtemp())
        (directory / "boards").mkdir()
        path = directory / "boards" / "someboard.json"
        path.write_text(json.dumps(contents))
        return path

    def test_a_board_that_names_no_vendor_source_cannot_be_checked(self):
        path = self._board_file({"pins": {"D3": 38}})
        result = check_vendor_pins.check_board(path, offline=True, repo="x/y")
        self.assertEqual(result["status"], "could-not-run")
        self.assertIn("arduino_variant", result["reason"])

    def test_offline_with_no_cache_refuses_rather_than_passing(self):
        path = self._board_file({"pins": {"D3": 38}, "vendor": {"arduino_variant": "nope"}})
        result = check_vendor_pins.check_board(path, offline=True, repo="x/y")
        self.assertEqual(result["status"], "could-not-run")
        self.assertIn("no cached header", result["reason"])

    def test_a_projects_own_copy_of_a_shipped_board_is_checked_against_the_plugins_cache(self):
        # P10: the override you are told to make for a verified board found no cache beside
        # itself and switched the check off. The irrigation project, 2026-09-29: `????`.
        shipped = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        path = self._board_file(shipped)
        result = check_vendor_pins.check_board(path, offline=True, repo="")
        self.assertEqual(result["status"], "ok", result.get("reason"))
        self.assertIn("cache", result["source"])
        wrong = dict(shipped, pins=dict(shipped["pins"], D3=3))
        self.assertEqual(check_vendor_pins.check_board(self._board_file(wrong), offline=True, repo="")["status"], "mismatch",
                         "and a wrong pin in the copy is still caught")

    def test_a_cached_header_is_used_and_said_so(self):
        path = self._board_file({"pins": {"D3": 38}, "vendor": {"arduino_variant": "v"}})
        cache = path.parent.parent / ".spark" / "cache"
        cache.mkdir(parents=True)
        (cache / "v.pins_arduino.h").write_text(HEADER)

        result = check_vendor_pins.check_board(path, offline=True, repo="x/y")
        self.assertEqual(result["status"], "ok")
        self.assertIn("cache", result["source"])

    def test_a_cached_header_still_catches_a_wrong_pin(self):
        path = self._board_file({"pins": {"D3": 3}, "vendor": {"arduino_variant": "v"}})
        cache = path.parent.parent / ".spark" / "cache"
        cache.mkdir(parents=True)
        (cache / "v.pins_arduino.h").write_text(HEADER)

        result = check_vendor_pins.check_board(path, offline=True, repo="x/y")
        self.assertEqual(result["status"], "mismatch")

    def test_the_exit_codes_tell_the_three_outcomes_apart(self):
        self.assertNotEqual(check_vendor_pins.EXIT_OK, check_vendor_pins.EXIT_MISMATCH)
        self.assertNotEqual(check_vendor_pins.EXIT_MISMATCH, check_vendor_pins.EXIT_COULD_NOT_RUN)
        self.assertNotEqual(check_vendor_pins.EXIT_OK, check_vendor_pins.EXIT_COULD_NOT_RUN)


class TheRealBoardsAgreeWithTheirVendors(unittest.TestCase):
    """The boards this plugin ships, against the headers cached beside them."""

    def test_every_shipped_board_matches_its_vendor_header(self):
        for path in sorted((ROOT / "boards").glob("*.json")):
            board = json.loads(path.read_text())
            if not (board.get("vendor") or {}).get("arduino_variant"):
                continue
            with self.subTest(board=path.stem):
                result = check_vendor_pins.check_board(path, offline=True, repo="x/y")
                if result["status"] == "could-not-run":
                    self.skipTest("no cached header for %s" % path.stem)
                self.assertEqual(result["status"], "ok", result.get("problems"))



class TheExitCodeTellsTheThreeApartTest(unittest.TestCase):
    """
    P42. `main` never ran in this suite, so a mutation that made a refusal read as a pass stayed
    green — in the one check whose whole job is to catch a board file that disagrees with its
    vendor.
    """

    def _exit(self, *boards):
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return check_vendor_pins.main(["--offline", *boards])

    def test_a_board_that_agrees_with_its_vendor_exits_ok(self):
        self.assertEqual(self._exit(str(ROOT / "boards" / "firebeetle2-esp32s3.json")), check_vendor_pins.EXIT_OK)

    def test_a_board_naming_no_vendor_source_exits_could_not_run(self):
        import json
        import tempfile
        root = Path(tempfile.mkdtemp())
        (root / "boards").mkdir()
        path = root / "boards" / "mystery.json"
        path.write_text(json.dumps({"pins": {"D3": 38}}))
        self.assertEqual(self._exit(str(path)), check_vendor_pins.EXIT_COULD_NOT_RUN)

    def test_a_board_that_disagrees_exits_mismatch(self):
        import json
        import tempfile
        shipped = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        root = Path(tempfile.mkdtemp())
        (root / "boards").mkdir()
        path = root / "boards" / "wrong.json"
        path.write_text(json.dumps(dict(shipped, pins=dict(shipped["pins"], D3=3))))
        self.assertEqual(self._exit(str(path)), check_vendor_pins.EXIT_MISMATCH)


class WhereTheHeaderIsKept(unittest.TestCase):
    """
    P179. A live check writes the header it fetched into the cache of the project that owns the
    board file, found by the walk every script shares (`boards.project_root`), and says which file.
    An offline check reads that copy first and says whose cache answered. Before the fix the
    write followed P10's read fallback, so the first live check of any new board wrote into
    spark's own folder, and a later `--offline` passed from a file in nobody's project (P100
    round 0, 2026-10-09).

    spark's own folder is a stand-in here (`PLUGIN_ROOT` patched to a temporary copy), so no run,
    red, green or interrupted, can change the real one.
    """

    SHIPPED = "firebeetle2-esp32s3"

    def setUp(self):
        self.plugin = Path(tempfile.mkdtemp()).resolve()
        shipped_cache = ROOT / ".spark" / "cache"
        (self.plugin / ".spark" / "cache").mkdir(parents=True)
        for header in shipped_cache.glob("*.pins_arduino.h"):
            (self.plugin / ".spark" / "cache" / header.name).write_bytes(header.read_bytes())
        self.seeded = self._plugin_files()
        patcher = mock.patch.object(check_vendor_pins, "PLUGIN_ROOT", self.plugin)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _plugin_files(self):
        return {f.name: f.read_bytes() for f in (self.plugin / ".spark" / "cache").iterdir()}

    def _project(self, contents):
        """A board file in `<project>/boards/`, in a folder that is a project (it holds `.spark/`)."""
        project = Path(tempfile.mkdtemp()).resolve()
        (project / "boards").mkdir()
        (project / ".spark").mkdir()
        path = project / "boards" / "someboard.json"
        path.write_text(json.dumps(contents))
        return project, path

    def _board(self, variant, d3=38):
        return {"pins": {"D3": d3}, "vendor": {"arduino_variant": variant}}

    def _live(self, path, fetched=HEADER):
        with mock.patch.object(check_vendor_pins, "fetch_variant_header", return_value=fetched):
            return check_vendor_pins.check_board(path, offline=False, repo="x/y")

    def _line(self, path, fetched=HEADER):
        out = io.StringIO()
        with mock.patch.object(check_vendor_pins, "fetch_variant_header", return_value=fetched), \
                contextlib.redirect_stdout(out):
            check_vendor_pins.main([str(path)])
        return out.getvalue()

    @staticmethod
    def _kept(project, variant):
        return project / ".spark" / "cache" / (variant + ".pins_arduino.h")

    def test_a_live_fetch_for_a_new_board_is_kept_in_its_project_not_in_spark(self):
        project, path = self._project(self._board("p179_new"))
        result = self._live(path)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(self._kept(project, "p179_new").read_text(), HEADER)
        self.assertEqual(self._plugin_files(), self.seeded, "nothing is written into spark's own folder")
        self.assertEqual(result["wrote"], str(self._kept(project, "p179_new")), "and the answer says which file")

    def test_a_live_fetch_for_a_projects_copy_of_a_shipped_board_leaves_sparks_header_alone(self):
        shipped = json.loads((ROOT / "boards" / (self.SHIPPED + ".json")).read_text())
        variant = shipped["vendor"]["arduino_variant"]
        project, path = self._project(shipped)
        fetched = self.seeded[variant + ".pins_arduino.h"].decode() + "\n// fetched by P179's test\n"
        self._live(path, fetched)
        self.assertEqual(self._plugin_files(), self.seeded, "spark's shipped header is not overwritten")
        self.assertEqual(self._kept(project, variant).read_text(), fetched)

    def test_a_relative_path_from_inside_boards_is_kept_in_the_project(self):
        project, _ = self._project(self._board("p179_rel"))
        here = os.getcwd()
        self.addCleanup(os.chdir, here)
        os.chdir(project / "boards")
        result = self._live(Path("someboard.json"))
        self.assertTrue(self._kept(project, "p179_rel").is_file())
        self.assertFalse((project / "boards" / ".spark").exists(), "not two folders up from the path as typed")
        self.assertEqual(result["wrote"], str(self._kept(project, "p179_rel")), "and the file is named whole")

    def _loose(self, variant):
        """A board file in a folder no project owns."""
        loose = Path(tempfile.mkdtemp()).resolve()
        path = loose / "someboard.json"
        path.write_text(json.dumps(self._board(variant)))
        return loose, path

    def test_a_board_file_in_no_project_is_refused_live_and_nothing_is_written(self):
        loose, path = self._loose("p179_loose")
        with mock.patch.object(check_vendor_pins, "fetch_variant_header", return_value=HEADER) as fetch:
            result = check_vendor_pins.check_board(path, offline=False, repo="x/y")
        fetch.assert_not_called()  # no network call is spent on a refusal (refuter B9)
        self.assertEqual(result["status"], "could-not-run")
        self.assertIn("no project", result["reason"])
        self.assertIn(str(path), result["reason"], "and names the board file it could not place")
        self.assertFalse((loose / ".spark").exists() or (loose.parent / ".spark").exists())
        self.assertEqual(self._plugin_files(), self.seeded)

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root writes anywhere")
    def test_a_cache_that_cannot_be_written_is_could_not_run_and_names_the_file(self):
        project, path = self._project(self._board("p179_locked"))
        (project / ".spark").chmod(0o500)
        self.addCleanup((project / ".spark").chmod, 0o700)
        result = self._live(path)
        self.assertEqual(result["status"], "could-not-run")
        self.assertIn(str(self._kept(project, "p179_locked")), result["reason"])

    def test_the_live_refusal_offers_offline_only_when_spark_keeps_the_header(self):
        # Refuter B8: "or use --offline" for a header spark does not keep was a second refusal.
        _, unshipped = self._loose("p179_unshipped")
        self.assertIn("--offline would not help", self._live(unshipped)["reason"])
        shipped = json.loads((ROOT / "boards" / (self.SHIPPED + ".json")).read_text())
        _, path = self._loose(shipped["vendor"]["arduino_variant"])
        self.assertIn("or use --offline", self._live(path)["reason"])

    def test_an_offline_refusal_names_both_places_it_looked(self):
        project, path = self._project(self._board("p179_nowhere"))
        result = check_vendor_pins.check_board(path, offline=True, repo="")
        self.assertEqual(result["status"], "could-not-run")
        self.assertIn(str(self._kept(project, "p179_nowhere")), result["reason"], "the project's place")
        self.assertIn(str(self.plugin / ".spark" / "cache"), result["reason"], "and spark's")

    def test_an_offline_refusal_for_a_board_in_no_project_says_so(self):
        loose = Path(tempfile.mkdtemp()).resolve()
        path = loose / "someboard.json"
        path.write_text(json.dumps(self._board("p179_nowhere")))
        result = check_vendor_pins.check_board(path, offline=True, repo="")
        self.assertEqual(result["status"], "could-not-run")
        self.assertIn("no project owns %s" % path, result["reason"])
        self.assertIn(str(self.plugin / ".spark" / "cache"), result["reason"])

    def test_the_live_line_says_which_file_it_wrote(self):
        project, path = self._project(self._board("p179_said"))
        self.assertIn("wrote %s" % self._kept(project, "p179_said"), self._line(path))

    def test_a_fetch_that_parses_no_pins_still_says_which_file_it_wrote(self):
        project, path = self._project(self._board("p179_empty"))
        result = self._live(path, "/* no pins here */")
        self.assertEqual(result["status"], "could-not-run")
        self.assertEqual(result["wrote"], str(self._kept(project, "p179_empty")))
        self.assertIn("wrote %s" % self._kept(project, "p179_empty"), self._line(path, "/* no pins here */"))

    def test_an_offline_read_says_spark_answered_when_the_project_has_no_copy(self):
        shipped = json.loads((ROOT / "boards" / (self.SHIPPED + ".json")).read_text())
        _, path = self._project(shipped)
        result = check_vendor_pins.check_board(path, offline=True, repo="")
        self.assertEqual(result["status"], "ok", result.get("reason"))
        self.assertTrue(result["source"].startswith("spark's cache"), result["source"])

    def test_an_offline_read_prefers_the_projects_own_copy(self):
        # spark's copy says D3 is GPIO3, the project's says GPIO38, the board says 38: only the
        # project's copy agrees, so an `ok` proves which one answered (TL-2b).
        (self.plugin / ".spark" / "cache" / "p179_both.pins_arduino.h").write_text(HEADER.replace("D3 = 38", "D3 = 3"))
        project, path = self._project(self._board("p179_both"))
        self._kept(project, "p179_both").parent.mkdir(parents=True)
        self._kept(project, "p179_both").write_text(HEADER)
        result = check_vendor_pins.check_board(path, offline=True, repo="")
        self.assertEqual(result["status"], "ok", result.get("problems"))
        self.assertTrue(result["source"].startswith("the project's cache"), result["source"])

    def test_what_a_live_check_wrote_is_what_a_later_offline_check_reads(self):
        project, path = self._project(self._board("p179_again"))
        self._live(path)
        result = check_vendor_pins.check_board(path, offline=True, repo="")
        self.assertEqual(result["status"], "ok", result.get("reason"))
        self.assertTrue(result["source"].startswith("the project's cache"), result["source"])


if __name__ == "__main__":
    unittest.main()
