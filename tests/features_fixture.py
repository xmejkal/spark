"""
The synthetic board the P956 tests measure and draw (#1362): a made-up board of 20 x 40 mm with two rows of six pads,
its record built here, and `tests/data/pictures/features-synthetic.json`, a features file read off a made-up picture.
A helper module, no tests in it. No vendor's bytes: every number is made up.
"""

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEATURES_FILE = ROOT / "tests" / "data" / "pictures" / "features-synthetic.json"
GOLDEN_SVG = ROOT / "tests" / "data" / "pictures" / "features-synthetic.svg"
BOARD_ID = "synthetic-board"
_BOARD = {
    "schema": 1, "id": BOARD_ID, "name": "Synthetic board", "chip": "esp32c6",
    "documents": {"synthetic-top-view": {"url": None, "file": "top.png", "sha256": "0" * 64}},
    "physical": {
        "width_mm": 20.0, "height_mm": 40.0, "corner_radius_mm": None,
        "header": {"rows": 2, "pins": [6, 6], "pitch_mm": 2.54, "row_spacing_mm": 17.78, "first_pad_from_edge_mm": 5.0,
                   "flush_edge": "+y", "doubtful_pads": [], "pad_mm": 1.5},
        "header_order": {"row_a": ["A1", "A2", "A3", "A4", "A5", "A6"], "row_b": ["B1", "B2", "B3", "B4", "B5", "B6"]},
        "mounting_holes": {"count": 4, "diameter_mm": 1.6, "spacing_x_mm": 16.0, "spacing_y_mm": 36.0}},
    "power_pads": {"B6": {"rail": "ground", "direction": "out"}}}


def board():
    """A fresh copy of the synthetic board's record."""
    return copy.deepcopy(_BOARD)


def mirrored_board():
    """The synthetic board with its rows swapped: a picture of the real board then lies mirrored on its frame."""
    record = board()
    order = record["physical"]["header_order"]
    record["physical"]["header_order"] = {"row_b": order["row_b"], "row_a": order["row_a"]}
    return record


def features_file():
    """The features file as an object, to change in a test and write to a temporary file."""
    return json.loads(FEATURES_FILE.read_text())
