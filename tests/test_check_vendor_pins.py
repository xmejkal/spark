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

import json
import sys
import tempfile
import unittest
from pathlib import Path

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

if __name__ == "__main__":
    unittest.main()
