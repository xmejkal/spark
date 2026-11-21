"""
The wire pills' places (P969, #1388): where each jumper's pill goes, made with no picture around it
(scripts/spark/breadboard/wire_pills.py).

    python3 -m unittest tests.test_wire_pills
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.breadboard import board_marks, breadboard_scene, sheet, wire_pills, wire_routing  # noqa: E402
from spark.breadboard.spacing import BodyBox  # noqa: E402

DATA = ROOT / "tests" / "data" / "breadboard"


def grown(one, other, by):
    """The box of the line from `one` to `other`, `by` px more on every side."""
    return BodyBox(min(one[0], other[0]) - by, min(one[1], other[1]) - by, max(one[0], other[0]) + by,
                   max(one[1], other[1]) + by)


class TheWirePillsTest(unittest.TestCase):
    def test_the_module_loads_with_no_picture_code(self):
        # the pills' places leave the SVG renderer: importing them loads no svg_diagram
        code = ("import sys; sys.path.insert(0, sys.argv[1]); import spark.breadboard.wire_pills; "
                "print('spark.breadboard.svg_diagram' in sys.modules)")
        run = subprocess.run([sys.executable, "-c", code, str(ROOT / "scripts")], capture_output=True, text=True,
                             env={**os.environ, "SPARK_HOME": tempfile.mkdtemp()})
        self.assertEqual((run.stdout.strip(), run.returncode), ("False", 0), run.stderr)

    def test_the_wire_sizes_are_the_praised_pages_at_spark_s_pitch(self):
        self.assertEqual(tuple(wire_pills.WIRE_SIZES_PX), (4.0, 2.2, 3.0, 0.8))
        self.assertEqual(wire_pills.WIRE_SIZES_PX._fields, ("under_stroke", "stroke", "end_dot", "end_ring"))

    def test_the_wire_boxes_are_each_piece_grown_by_half_the_under_stroke_then_each_end_hole_by_its_dot(self):
        with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
            layout = sheet._plan_layout(sheet._read_build(DATA / "button-light-xiao" / "requirements.json"))
        bodies = [BodyBox.of(part, layout.geometry.part(part.type)) for part in layout.parts]
        marks = board_marks.BoardMarks(layout.geometry.surface, board_marks.BoardPalette.load().sizes,
                                       breadboard_scene.PxLabelMeasure(7))
        paths = wire_routing.TrackJumperRouter().route(layout, marks.obstacles(bodies))
        pieces = [grown(a, b, 2.0) for path in paths.values() for a, b in zip(path.points, path.points[1:])
                  if a != b]
        dots = [grown((hole.x, hole.y), (hole.x, hole.y), 3.4) for jumper in layout.jumpers
                for hole in (jumper.one, jumper.other)]
        self.assertTrue(pieces and dots)
        self.assertEqual(wire_pills.wire_boxes(layout.jumpers, paths, {}), pieces + dots)
