"""P1102: docs/guide/design-basis.json and .md, what every interface shows, follow the code."""

import io
import json
import sys
import tempfile
import unittest
from contextlib import contextmanager, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "scripts"))

import design_basis  # noqa: E402
from spark import operation_catalogue  # noqa: E402
from spark.core import describe_operations  # noqa: E402
from spark.flow import flow_codes, flow_page, run_request  # noqa: E402

STALE = "docs/guide/design-basis.json and .md are stale: run python3 tools/design_basis.py --write"
BASIS = design_basis.DesignBasis.of()


@contextmanager
def swapped(module, name, value):
    """The attribute of the module is the value inside the block, and as it was after it."""
    old = getattr(module, name)
    setattr(module, name, value)
    try:
        yield
    finally:
        setattr(module, name, old)


def group(name, basis=BASIS):
    return [item for item in basis.items if item["key"].startswith(name + ":")]


def item(key, basis=BASIS):
    return next(one for one in basis.items if one["key"] == key)


class TheCommittedFilesTest(unittest.TestCase):
    def test_t1_the_committed_files_are_the_ones_the_code_gives(self):  # T1
        self.assertEqual((ROOT / design_basis.JSON_PAGE).read_text(encoding="utf-8"), BASIS.json_text(), STALE)
        self.assertEqual((ROOT / design_basis.MARKDOWN_PAGE).read_text(encoding="utf-8"), BASIS.markdown(), STALE)


class ThePhasesTest(unittest.TestCase):
    def test_t2_the_phases_are_the_flow_codes_in_order_with_their_readers_actor(self):  # T2
        self.assertEqual([(one["key"], one["usual_by"]) for one in group("phase")],
                         [("phase:idea", "you"), ("phase:needs", "claude"), ("phase:parts", "you"),
                          ("phase:requirements", "claude"), ("phase:build", "claude"), ("phase:breadboard", "you"),
                          ("phase:firmware", "claude"), ("phase:simulate", "your terminal"),
                          ("phase:deploy", "your terminal")])

    def test_t3_a_phase_with_no_moment_and_a_moment_with_no_phase_are_named(self):  # T3
        self.assertEqual(BASIS.missing(), [])
        without = {phase: moment for phase, moment in design_basis.MOMENTS.items() if phase != "deploy"}
        with swapped(design_basis, "MOMENTS", without):
            self.assertEqual(design_basis.DesignBasis.of().missing(), ["deploy"], "add deploy to MOMENTS in tools/design_basis.py")
        with swapped(design_basis, "MOMENTS", dict(design_basis.MOMENTS, ghost="x")):
            self.assertEqual(design_basis.DesignBasis.of().missing(), ["ghost"], "remove ghost from MOMENTS in tools/design_basis.py")


class ThePhaseNamesTest(unittest.TestCase):
    def test_t15_each_phase_has_its_plain_name_and_one_with_none_is_named(self):  # T15 (P1119)
        self.assertEqual([one["name"] for one in group("phase")],
                         ["Idea", "Needs", "Parts", "Parts list", "Board files", "Wiring", "Firmware", "Simulation", "On the board"])
        without = {"idea": "Idea", "needs": "Needs", "parts": "Parts", "requirements": "Parts list", "breadboard": "Wiring",
                   "firmware": "Firmware", "simulate": "Simulation", "deploy": "On the board"}
        with swapped(flow_codes, "PHASE_NAMES", without):
            self.assertEqual(design_basis.DesignBasis.of().missing(), ["build"], "add build to PHASE_NAMES in flow_codes")

    def test_t16_the_unbuilt_steps_are_read_from_flow_codes_with_their_names(self):  # T16 (P1119)
        self.assertEqual([(one["key"], one["name"], one["status"]) for one in group("unbuilt")],
                         [("unbuilt:perfboard", "Perfboard", "not built"), ("unbuilt:pcb", "PCB", "not built"),
                          ("unbuilt:case", "Case", "not built")])
        with swapped(flow_codes, "UNBUILT_STEPS", (("lathe", "Lathe", "At the lathe."),)):
            self.assertEqual([(one["key"], one["name"], one["moment"]) for one in group("unbuilt", design_basis.DesignBasis.of())],
                             [("unbuilt:lathe", "Lathe", "At the lathe.")])


class TheStatusesTest(unittest.TestCase):
    def test_t4_the_statuses_are_the_marks_with_their_word_and_glyph(self):  # T4
        self.assertEqual([(one["key"], one["word"], one["mark"]) for one in group("status")],
                         [("status:ok", None, "✓"), ("status:problems", "problems", "✗"),
                          ("status:could-not-run", "could not run", "?"), ("status:not-started", "not started", "○"),
                          ("status:partial", "partly done", "◐"), ("status:stale", "out of date", "↻"),
                          ("status:none", None, "·")])
        self.assertIn("status:none", [one["key"] for one in group("status")])


class TheOperationsTest(unittest.TestCase):
    def test_t5_the_operations_are_the_catalogue_each_once_with_its_area_and_summary(self):  # T5
        ops = group("op")
        self.assertEqual([one["key"] for one in ops], ["op:" + op for op in operation_catalogue.CATALOGUE])
        areas = {op: area for area, table in operation_catalogue.TABLES for op in table}
        for one in ops:
            op = one["key"][3:]
            cls = operation_catalogue.CATALOGUE[op]
            self.assertEqual(one["area"], areas[op])
            self.assertEqual(one["network"], op in operation_catalogue.NETWORK, op)
            self.assertEqual(one["summary"], " ".join(describe_operations.summary_of(cls).split()))
            self.assertIsNotNone(one["summary"], op)
        self.assertTrue(any(one["network"] for one in ops))


class TheOffersTest(unittest.TestCase):
    def test_t6_the_offer_kinds_are_the_table_and_from_page_needs_the_row_and_the_allow_list(self):  # T6 (P1115)
        self.assertEqual([one["kind"] for one in group("offer")], list(flow_codes.OFFER_KINDS))
        self.assertEqual([(one["key"], one["phase"]) for one in group("offer")],
                         [("offer:pick", "parts"), ("offer:requirements", "requirements"), ("offer:build", "build"),
                          ("offer:needs-drop", "needs"), ("offer:write-firmware", "firmware"),
                          ("offer:run-simulation", "simulate"), ("offer:look-at-board", "deploy")])
        self.assertEqual({one["key"]: one["op"] for one in group("offer")},
                         {"offer:pick": "pick", "offer:requirements": "requirements", "offer:build": "build-board",
                          "offer:needs-drop": "needs-drop", "offer:write-firmware": None, "offer:run-simulation": None,
                          "offer:look-at-board": None})
        self.assertEqual({one["key"]: one["from_page"] for one in group("offer")},
                         {"offer:pick": True, "offer:requirements": True, "offer:build": True, "offer:needs-drop": False,
                          "offer:write-firmware": False, "offer:run-simulation": False, "offer:look-at-board": False})
        self.assertEqual({one["key"]: one["tell"] for one in group("offer")},
                         {"offer:pick": None, "offer:requirements": None, "offer:build": None, "offer:needs-drop": None,
                          "offer:write-firmware": "Write the firmware for this project's board.",
                          "offer:run-simulation": "Help me run the simulation of this project.",
                          "offer:look-at-board": "Look at this project's board with me."})
        build = flow_codes.OFFER_KINDS["build"]._replace(from_page=False)
        with swapped(flow_codes, "OFFER_KINDS", dict(flow_codes.OFFER_KINDS, build=build)):
            self.assertFalse(item("offer:build", design_basis.DesignBasis.of())["from_page"])
        with swapped(run_request, "STEP_OPERATIONS", {op: one for op, one in run_request.STEP_OPERATIONS.items() if op != "build-board"}):
            self.assertFalse(item("offer:build", design_basis.DesignBasis.of())["from_page"])

    def test_t10_each_label_is_its_flow_codes_constant_with_the_percent_kept(self):  # T10
        self.assertEqual({one["key"]: one["label"] for one in group("offer")},
                         {"offer:pick": "Pick “%s” for %s", "offer:requirements": "Write the parts list",
                          "offer:build": "Build the board", "offer:needs-drop": "Drop the %s need",
                          "offer:write-firmware": "Write the firmware", "offer:run-simulation": "Run the simulation",
                          "offer:look-at-board": "Look at the board"})
        self.assertIn("%s", item("offer:pick")["label"])


class TheShapeTest(unittest.TestCase):
    def test_t7_every_key_is_unique_and_is_group_colon_name_with_no_space(self):  # T7
        keys = [one["key"] for one in BASIS.items]
        self.assertEqual(len(keys), len(set(keys)))
        for key in keys:
            head, colon, name = key.partition(":")
            self.assertTrue(head and colon and name and " " not in key, key)

    def test_t8_the_page_names_its_command_and_its_hand_written_parts(self):  # T8
        top = "\n".join(BASIS.markdown().splitlines()[:8])
        self.assertIn("python3 tools/design_basis.py --write", top)
        self.assertIn("hand-written", top)
        self.assertIn(design_basis.HAND_WRITTEN, top)

    def test_t9_main_prints_without_a_write_and_writes_exactly_two_files_with_it(self):  # T9
        with tempfile.TemporaryDirectory() as folder:
            root, out = Path(folder), io.StringIO()
            with redirect_stdout(out):
                design_basis.main([], root)
            self.assertEqual(out.getvalue(), BASIS.markdown())
            self.assertEqual(list(root.rglob("*")), [])
            with redirect_stdout(io.StringIO()):
                design_basis.main(["--write"], root)
            self.assertEqual(sorted(path.name for path in root.rglob("*") if path.is_file()), ["design-basis.json", "design-basis.md"])
            self.assertEqual((root / design_basis.JSON_PAGE).read_text(encoding="utf-8"), BASIS.json_text())

    def test_t11_the_actors_are_the_three_by_values_and_each_phase_uses_one(self):  # T11
        names = [one["name"] for one in group("by")]
        self.assertEqual(names, ["you", "claude", "your terminal"])
        for one in group("phase"):
            self.assertIn(one["usual_by"], names)

    def test_t12_the_unbuilt_steps_are_perfboard_pcb_and_case_each_with_a_moment(self):  # T12
        steps = group("unbuilt")
        self.assertEqual([one["key"] for one in steps], ["unbuilt:perfboard", "unbuilt:pcb", "unbuilt:case"])
        for one in steps:
            self.assertEqual(one["status"], "not built")
            self.assertTrue(one["moment"])

    def test_t13_the_page_is_short_its_cells_are_short_and_the_json_is_stable(self):  # T13
        lines = BASIS.markdown().splitlines()
        self.assertLess(len(lines), 400)
        for line in lines:
            if line.startswith("|"):
                for cell in line.split("|"):
                    self.assertLessEqual(len(cell), 300, cell[:60])
        text = BASIS.json_text()
        self.assertEqual(json.dumps(json.loads(text), indent=1, ensure_ascii=False) + "\n", text)


class ThePageSectionsTest(unittest.TestCase):
    def test_t14_each_page_section_names_basis_keys_or_a_whole_group(self):  # T14 (P1123)
        keys = {one["key"] for one in BASIS.items}
        groups = {key.partition(":")[0] for key in keys}
        named = [(section.NAME, key) for section in flow_page.FlowHtmlPage.SECTIONS for key in section.KEYS]
        self.assertTrue(named)
        for name, key in named:
            head, _colon, rest = key.partition(":")
            self.assertTrue(key in keys or (rest == "*" and head in groups), "%s names %s, no key of the design basis" % (name, key))


if __name__ == "__main__":
    unittest.main()
