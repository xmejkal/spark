"""
The board's printed marks (P969, #1388): the row letters, the column numbers, the rail lines and the rail signs as
facts with their boxes, made with no picture around them (scripts/spark/breadboard/board_marks.py).

    python3 -m unittest tests.test_board_marks
"""

import os
import subprocess
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

from spark.breadboard import board_marks, breadboard_scene, sheet, svg_diagram  # noqa: E402

WALK = ROOT / "tests" / "data" / "breadboard" / "walk-c6"
NS = {"svg": "http://www.w3.org/2000/svg"}
#: What the SVG's text rounding can move a box edge by, in px.
SLACK = 0.01


def walk_layout():
    with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
        return sheet._plan_layout(sheet._read_build(WALK / "requirements.json"))


def centred_texts(root):
    """(text, left, top, right, bottom) of the glyphs of each centred text printed on the board itself, the root's own
    (a caption and a note line start at their x): 0.6 of its size wide a character, its middle 0.35 of its size above
    its baseline, 0.8 of its size high."""
    found = []
    for text in root.findall("svg:text", NS):
        if text.get("text-anchor") == "middle":
            x, base, size = float(text.get("x")), float(text.get("y")), float(text.get("font-size"))
            half = 0.3 * size * len(text.text)
            found.append((text.text, x - half, base - 0.35 * size - 0.4 * size, x + half, base - 0.35 * size + 0.4 * size))
    return found


def holds(box, glyphs):
    return (box.left - SLACK <= glyphs[0] and box.top - SLACK <= glyphs[1] and
            glyphs[2] <= box.right + SLACK and glyphs[3] <= box.bottom + SLACK)


class TheBoardMarksTest(unittest.TestCase):
    def test_the_module_loads_with_no_picture_code(self):
        # (a) the printed marks leave the SVG renderer: importing them loads no svg_diagram
        code = ("import sys; sys.path.insert(0, sys.argv[1]); import spark.breadboard.board_marks; "
                "print('spark.breadboard.svg_diagram' in sys.modules)")
        run = subprocess.run([sys.executable, "-c", code, str(ROOT / "scripts")], capture_output=True, text=True,
                             env={**os.environ, "SPARK_HOME": tempfile.mkdtemp()})
        self.assertEqual((run.stdout.strip(), run.returncode), ("False", 0), run.stderr)

    def test_every_printed_text_of_the_walk_lies_in_a_mark_box_or_a_sign_box(self):
        # (b) the walk's SVG prints each letter, number and sign inside a box that the marks give the router and the pills
        layout = walk_layout()
        surface = layout.geometry.surface
        marks = board_marks.BoardMarks(surface, board_marks.BoardPalette.load().sizes)
        boxes = list(marks.obstacles(()).marks) + list(marks.sign_boxes())
        root = ElementTree.fromstring(svg_diagram.SvgBreadboardDiagram().text(breadboard_scene.BreadboardSceneMaker().make(layout)))
        texts = centred_texts(root)
        self.assertGreater(len(texts), 20)
        self.assertGreaterEqual(len([text for text, *_ in texts if text in ("+", "−")]), 4)
        for text, *glyphs in texts:
            with self.subTest(text=text, glyphs=glyphs):
                self.assertTrue([box for box in boxes if holds(box, glyphs)])


if __name__ == "__main__":
    unittest.main()
