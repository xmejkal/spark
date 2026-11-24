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
from spark.flow import flow_codes, phase_readers, run_request  # noqa: E402

STALE = "docs/guide/design-basis.json and .md are stale: run python3 tools/design_basis.py --write"
BASIS = design_basis.DesignBasis.of(ROOT)


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
        usual = {reader.PHASE: reader.BY for reader in phase_readers.READERS}
        self.assertEqual([(one["key"], one["usual_by"]) for one in group("phase")],
                         [("phase:" + phase, usual[phase]) for phase in flow_codes.PHASES])

    def test_t3_a_phase_with_no_moment_and_a_moment_with_no_phase_are_named(self):  # T3
        self.assertEqual(BASIS.missing(), [])
        without = {phase: moment for phase, moment in design_basis.MOMENTS.items() if phase != "deploy"}
        with swapped(design_basis, "MOMENTS", without):
            self.assertEqual(design_basis.DesignBasis.of(ROOT).missing(), ["deploy"], "add deploy to MOMENTS in tools/design_basis.py")
        with swapped(design_basis, "MOMENTS", dict(design_basis.MOMENTS, ghost="x")):
            self.assertEqual(design_basis.DesignBasis.of(ROOT).missing(), ["ghost"], "remove ghost from MOMENTS in tools/design_basis.py")


class TheStatusesTest(unittest.TestCase):
    def test_t4_the_statuses_are_the_marks_with_their_word_and_glyph(self):  # T4
        expected = [("status:" + ("none" if status is None else status.replace(" ", "-")), word, mark)
                    for status, (word, mark) in phase_readers.MARKS.items()]
        self.assertEqual([(one["key"], one["word"], one["mark"]) for one in group("status")], expected)
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
            self.assertEqual(one["summary"], describe_operations.summary_of(cls))
            self.assertIsNotNone(one["summary"], op)
        self.assertTrue(any(one["network"] for one in ops))


class TheOffersTest(unittest.TestCase):
    def test_t6_the_offer_kinds_are_the_codes_and_from_page_needs_both_lists(self):  # T6
        kinds = tuple(flow_codes.SENDABLE) + tuple(run_request.IN_CHAT)
        self.assertEqual(set(design_basis.OFFER_STEPS), set(kinds))
        self.assertEqual([one["key"] for one in group("offer")], ["offer:" + kind for kind in design_basis.OFFER_STEPS])
        self.assertEqual({one["key"]: one["op"] for one in group("offer")},
                         {"offer:pick": "pick", "offer:requirements": "requirements", "offer:build": "build-board",
                          "offer:needs-drop": "needs-drop"})
        self.assertEqual({one["key"]: one["from_page"] for one in group("offer")},
                         {"offer:pick": True, "offer:requirements": True, "offer:build": True, "offer:needs-drop": False})
        with swapped(flow_codes, "SENDABLE", tuple(kind for kind in flow_codes.SENDABLE if kind != "build")):
            self.assertFalse(item("offer:build", design_basis.DesignBasis.of(ROOT))["from_page"])
        with swapped(run_request, "STEP_OPERATIONS", {op: one for op, one in run_request.STEP_OPERATIONS.items() if op != "build-board"}):
            self.assertFalse(item("offer:build", design_basis.DesignBasis.of(ROOT))["from_page"])

    def test_t10_each_label_is_its_flow_codes_constant_with_the_percent_kept(self):  # T10
        self.assertEqual({one["key"]: one["label"] for one in group("offer")},
                         {"offer:pick": flow_codes.PICK_LABEL, "offer:requirements": flow_codes.REQUIREMENTS_LABEL,
                          "offer:build": flow_codes.BUILD_LABEL, "offer:needs-drop": flow_codes.DROP_LABEL})
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
        self.assertEqual(names, [flow_codes.BY_YOU, flow_codes.BY_CLAUDE, flow_codes.BY_TERMINAL])
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


if __name__ == "__main__":
    unittest.main()
