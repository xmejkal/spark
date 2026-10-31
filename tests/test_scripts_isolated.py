"""
Every entry script starts under `python3 -I` (P369, #471).

    python3 -m unittest tests.test_scripts_isolated

`-I` takes the script's own folder off `sys.path` and ignores PYTHONPATH, so a script that imports a sibling must put its
own folder on the path itself. An entry script is a script with a `__main__` guard; a library has none. A new entry
script is covered by the glob.
"""

import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent

#: Exempt entry scripts, with the reason.
EXEMPT = {"import_child.py": "its first argument is a module (P443)"}
#: `--help` of these exits with a code other than 0: cost.py prints its own usage and exits 2.
HELP_EXIT = {"cost.py": 2}


class EveryScriptRunsIsolatedTest(unittest.TestCase):
    def test_help_starts_under_isolated_mode(self):
        scripts = [p for p in sorted((ROOT / "scripts").glob("*.py"))
                   if p.name not in EXEMPT and 'if __name__ == "__main__"' in p.read_text(encoding="utf-8")]
        self.assertGreater(len(scripts), 20)
        for script in scripts:
            with self.subTest(script=script.name):
                run = subprocess.run([sys.executable, "-I", "-B", str(script), "--help"],
                                     capture_output=True, text=True, timeout=30)
                self.assertNotIn("Traceback", run.stderr)
                self.assertNotIn("ModuleNotFoundError", run.stderr)
                self.assertEqual(run.returncode, HELP_EXIT.get(script.name, 0), run.stderr)


if __name__ == "__main__":
    unittest.main()
