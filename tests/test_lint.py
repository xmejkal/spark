"""P386 R0: the repository passes Ruff with the settings in pyproject.toml.

The test runs the pinned Ruff over the whole repository. A finding fails it. So does anything Ruff writes to
stderr, because a warning (for example a broken `# noqa` note) is a finding that exit code 0 would hide.
Without Ruff on PATH the test skips. The suite stays offline, so there is no download fallback.
"""

import shutil
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
TIMEOUT_SECONDS = 120


# --- MVP ---
class TheRepositoryLintsCleanTest(unittest.TestCase):
    @unittest.skipUnless(shutil.which("ruff"), "ruff not found: uv tool install ruff==0.17.1")
    def test_ruff_finds_nothing_and_warns_of_nothing(self):
        run = subprocess.run(
            ["ruff", "check", "--no-cache", "--output-format", "concise", "."],
            cwd=ROOT, capture_output=True, text=True, timeout=TIMEOUT_SECONDS,
        )
        self.assertEqual((run.returncode, run.stderr.strip()), (0, ""), run.stdout + run.stderr)
