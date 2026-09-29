"""
Proof that the documented flow reaches the chain.

Two working boards were produced by `assign_pins`, `emit_board` and `check_spine`, and no skill,
command or agent named any of them (cold test G13, backlog R7): a user following the documented
flow was told to write the board file by hand. The skills, commands and agents ARE the product's
entry points — the text is the artefact — so this is the one place in the suite that reads text,
and it reads only the text that a user is routed by.

    python3 -m unittest discover -s tests
"""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

#: The chain, in order. A document that routes to the chain names every link.
CHAIN = ("parts.py", "assign_pins.py", "emit_board.py", "check_spine.py")

BUILD_COMMAND = ROOT / "commands" / "build.md"
DESIGN_SKILL = ROOT / "skills" / "spark-design" / "SKILL.md"
HARDWARE_AGENT = ROOT / "agents" / "hardware-engineer.md"


def allowed_scripts(command_path):
    """The scripts a command's frontmatter lets it run, by file name."""
    text = command_path.read_text()
    front = text.split("---")[1] if text.startswith("---") else ""
    return set(re.findall(r"scripts/([a-z_]+\.py)", front))


class TheDocumentedFlowNamesTheChainTest(unittest.TestCase):
    def test_the_build_command_exists_and_may_run_the_spine(self):
        self.assertTrue(BUILD_COMMAND.is_file(), "no /spark:build command")
        self.assertIn("check_spine.py", allowed_scripts(BUILD_COMMAND))
        self.assertIn("emit_board.py", allowed_scripts(BUILD_COMMAND))

    def test_the_design_skill_names_every_link(self):
        text = DESIGN_SKILL.read_text()
        missing = [script for script in CHAIN if script not in text]
        self.assertEqual(missing, [], "spark-design never names: %s" % missing)

    def test_the_design_skill_does_not_start_with_a_hand_written_board(self):
        # The generator comes before any instruction to write tscircuit by hand.
        text = DESIGN_SKILL.read_text()
        self.assertLess(text.index("emit_board.py"), text.index("<chip>"))

    def test_the_hardware_engineer_runs_the_chain(self):
        text = HARDWARE_AGENT.read_text()
        for script in ("emit_board.py", "check_spine.py"):
            self.assertIn(script, text)

    def test_the_readme_lists_the_command(self):
        self.assertIn("/spark:build", (ROOT / "README.md").read_text())


class EveryRouteLeadsSomewhereTest(unittest.TestCase):
    def test_every_script_a_command_may_run_exists(self):
        # The inverse failure: a command allowed to run a script that is not there.
        for command in sorted((ROOT / "commands").glob("*.md")):
            for script in allowed_scripts(command):
                self.assertTrue((ROOT / "scripts" / script).is_file(),
                                "%s may run scripts/%s, which does not exist" % (command.name, script))

    def test_every_chain_script_has_a_command_line(self):
        # Named in a document, and runnable as documented: each answers --help with usage.
        import subprocess
        for script in CHAIN:
            result = subprocess.run([sys.executable, str(ROOT / "scripts" / script), "--help"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, script)
            self.assertIn("usage:", result.stdout, script)


if __name__ == "__main__":
    unittest.main()
