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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.breadboard import wire_pills  # noqa: E402


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
