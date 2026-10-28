"""
A tree planted in a temp folder, for the tests that read code with `ast` (P440): `tests/test_measure.py` and `tests/test_architecture.py`.

It is not named `test_*.py`, so the suite never loads it as tests.
"""

import tempfile
from pathlib import Path

#: The modules that import nothing of spark. A planted tree holds them, or rule U1 reports each one as missing.
LEAF_NAMES = ("board_codes", "outcomes", "provenance", "text_guards", "zone_time")


def planted(files, leaves=True):
    """A temp root holding `files` ({path under the root: source}) and, unless `leaves` is False, the five leaf modules."""
    root = Path(tempfile.mkdtemp())
    if leaves:
        files = dict({"scripts/%s.py" % name: '"""A leaf."""\n' for name in LEAF_NAMES}, **files)
    for name, source in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(source)
    return root


def function_of(name, lines):
    """A function `name` that is exactly `lines` lines long."""
    return "def %s():\n%s" % (name, "    pass\n" * (lines - 1))
