"""
P200: tools/inventory.py says what each script is for, who reaches it, and which flags no page names.

    python3 -m unittest tests.test_inventory
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import inventory  # noqa: E402

COMMAND = '''"""
{purpose}

    {name}.py --shown
"""
import argparse
{imports}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--shown")
    parser.add_argument("--hidden")
    parser.parse_args()
'''


class TheInventoryOfASmallTreeTest(unittest.TestCase):
    """A command named by a page, a library it imports, and a command that nothing names."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "scripts").mkdir()
        (self.root / "commands").mkdir()
        (self.root / "scripts" / "alpha.py").write_text(COMMAND.format(purpose="Alpha makes the board.", name="alpha",
                                                                       imports="import beta"))
        (self.root / "scripts" / "beta.py").write_text('"""Beta reads the parts."""\n')
        (self.root / "scripts" / "gamma.py").write_text(COMMAND.format(purpose="Gamma checks nothing.", name="gamma",
                                                                       imports=""))
        (self.root / "commands" / "build.md").write_text("Run `alpha.py --shown` to make the board.\n")
        self.inventory = inventory.Inventory(self.root)
        self.script = {script.name: script for script in self.inventory.scripts}

    def test_each_script_says_what_its_docstring_says_it_is_for(self):
        self.assertEqual(self.script["alpha.py"].purpose, "Alpha makes the board.")
        self.assertEqual(self.script["beta.py"].purpose, "Beta reads the parts.")

    def test_a_command_is_reached_by_the_pages_that_name_it(self):
        self.assertEqual(self.inventory.pages_naming(self.script["alpha.py"]), ["commands/build.md"])
        self.assertEqual(self.inventory.pages_naming(self.script["gamma.py"]), [])

    def test_a_flag_its_help_prints_and_no_page_names_is_listed(self):
        self.assertEqual(self.script["alpha.py"].flags, ["--hidden", "--shown"])
        self.assertEqual(self.inventory.unnamed_flags(self.script["alpha.py"]), ["--hidden"])

    def test_a_library_is_reached_by_the_scripts_that_import_it(self):
        self.assertEqual([s.name for s in self.inventory.importers(self.script["beta.py"])], ["alpha.py"])

    def test_the_page_puts_what_nothing_reaches_first(self):
        page = self.inventory.markdown()
        nobody = page.split("## Nothing reaches these")[1].split("##")[0]
        self.assertIn("scripts/gamma.py", nobody)
        self.assertNotIn("scripts/alpha.py", nobody)
        self.assertNotIn("scripts/beta.py", nobody)
        self.assertIn("3 scripts: 2 commands, 1 library", page)


if __name__ == "__main__":
    unittest.main()
