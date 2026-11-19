"""
P200: tools/inventory.py says what each script is for, who reaches it, and which flags no page names.

    python3 -m unittest tests.test_inventory
"""

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

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


#: A CLI on the core (P839): it imports no argparse, and `run_cli` builds its parser from its Operation's arguments. The
#: real spark package is on its path, as each script of scripts/ puts its own.
CORE_COMMAND = '''"""
Delta checks the board.
"""
import sys
from pathlib import Path

sys.path.insert(0, {scripts!r})
{imports}
from spark.core.operation import Argument, Operation


class CheckBoard(Operation):
    name = "check-board"
    arguments = (Argument(({flag!r},), "renamed", str, "what the old flag took"),)


if __name__ == "__main__":
    {main}
'''
#: The ways a core CLI imports `run_cli`, and the ways its `--help` can go wrong (the review of P839).
BY_NAME, BY_MODULE = "from spark.core.cli import HelpText, run_cli", "from spark.core import cli"
RUNS = 'sys.exit(run_cli(HelpText("delta.py"), CheckBoard(), outside_builder=None))'
RUNS_BY_MODULE = 'sys.exit(cli.run_cli(cli.HelpText("epsilon.py"), CheckBoard(), outside_builder=None))'
FAILS, HANGS = "sys.exit(1)", "import time; time.sleep(30)"
#: The seconds the test gives a --help: long enough for a CLI to start, far shorter than HANGS.
SECONDS = 3


def core_command(flag="--renamed", imports=BY_NAME, main=RUNS):
    return CORE_COMMAND.format(scripts=str(ROOT / "scripts"), imports=imports, flag=flag, main=main)


class TheFlagsOfACliOnTheCoreTest(unittest.TestCase):
    """P839: a core CLI whose flag was renamed, and a page that still names the old flag; one that imports the module."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "scripts").mkdir()
        (self.root / "commands").mkdir()
        (self.root / "scripts" / "delta.py").write_text(core_command())
        (self.root / "scripts" / "epsilon.py").write_text(core_command("--module", BY_MODULE, RUNS_BY_MODULE))
        (self.root / "commands" / "check.md").write_text("Run `delta.py --old` to check the board.\n")
        self.inventory = inventory.Inventory(self.root)
        self.script = {script.name: script for script in self.inventory.scripts}

    def test_its_flags_are_the_flags_of_its_operation(self):
        self.assertEqual(self.script["delta.py"].flags, ["--renamed"])

    def test_the_renamed_flag_is_named_on_no_page(self):
        self.assertEqual(self.inventory.unnamed_flags(self.script["delta.py"]), ["--renamed"])
        self.assertIn("| `scripts/delta.py` | Delta checks the board. | commands/check.md | --renamed |",
                      self.inventory.markdown())

    def test_a_cli_that_imports_the_module_has_its_flags_read_too(self):
        self.assertEqual(self.script["epsilon.py"].flags, ["--module"])


class AHelpThatGivesNoFlagsTest(unittest.TestCase):
    """The review of P839: a --help that exits non-zero or runs past its seconds says so on stderr, and the run goes on."""

    def flags_and_said(self, main):
        root = Path(tempfile.mkdtemp())
        (root / "scripts").mkdir()
        (root / "scripts" / "delta.py").write_text(core_command(main=main))
        said = io.StringIO()
        with contextlib.redirect_stderr(said):
            found = inventory.Inventory(root, seconds=SECONDS)
        return found.scripts[0].flags, said.getvalue()

    def test_a_help_that_exits_non_zero_is_said(self):
        self.assertEqual(self.flags_and_said(FAILS), ([], "inventory: scripts/delta.py --help exited 1, its flags are not read\n"))

    def test_a_help_past_its_seconds_is_said(self):
        self.assertEqual(self.flags_and_said(HANGS),
                         ([], "inventory: scripts/delta.py --help ran past %d s, its flags are not read\n" % SECONDS))


if __name__ == "__main__":
    unittest.main()
