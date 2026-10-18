"""
A copy of the plugin's board library in which the XIAO ESP32-C6 lacks one fact, for the tests of a board that stops
the chain (P278, #314): the shipped XIAO states all its facts now, so a test that needs a board with a gap makes one.

    with board_missing("physical.header"):
        ...     # boards.LIBRARY is a scratch copy; the XIAO's file there has no physical.header
"""

import contextlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import boards  # noqa: E402

XIAO = "xiao-esp32-c6"


def library_without(field):
    """A scratch copy of the board library, whose XIAO file lacks `field` (dotted, like `power.io_volts`)."""
    copy = Path(tempfile.mkdtemp()) / "boards"
    shutil.copytree(ROOT / "boards", copy)
    file = copy / (XIAO + ".json")
    record = json.loads(file.read_text())
    holder = record
    *parents, last = field.split(".")
    for key in parents:
        holder = holder[key]
    del holder[last]
    file.write_text(json.dumps(record, indent=2) + "\n")
    return copy


@contextlib.contextmanager
def board_missing(field):
    """boards.LIBRARY is a scratch copy in which the XIAO lacks `field`, for the length of the block."""
    with mock.patch.object(boards, "LIBRARY", library_without(field)):
        yield
