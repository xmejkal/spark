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

    def test_every_script_a_command_may_run_is_executable_as_written(self):
        # The one command in /spark:build is `${CLAUDE_PLUGIN_ROOT}/scripts/check_spine.py …`, no
        # interpreter named, and check_spine.py was mode 100644: exit 126 as written (audit B4).
        import os
        for command in sorted((ROOT / "commands").glob("*.md")):
            for script in allowed_scripts(command):
                path = ROOT / "scripts" / script
                self.assertTrue(os.access(path, os.X_OK), "%s is not executable, and %s runs it by path"
                                % (script, command.name))
                self.assertTrue(path.read_text().startswith("#!/usr/bin/env python3"), script)

    def test_every_chain_script_has_a_command_line(self):
        # Named in a document, and runnable as documented: each answers --help with usage.
        import subprocess
        for script in CHAIN:
            result = subprocess.run([sys.executable, str(ROOT / "scripts" / script), "--help"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, script)
            self.assertIn("usage:", result.stdout, script)



class TheDocumentedExampleRunsTest(unittest.TestCase):
    """
    The example in `/spark:build` is the first thing a user will type. Its first version named a
    motor driver and no power inlet, so the generator said "nothing sources net.MOTOR6V" and the
    build stopped on a one-member net — and a commit message said it ran end to end, because the
    output was grepped rather than read. This runs the example, from the document, through every
    stage before the build (the build needs tsci, which the suite must not depend on).
    """

    @staticmethod
    def example(path):
        import json
        block = re.search(r"```json\n(.*?)```", path.read_text(), re.S).group(1)
        return json.loads(block)

    def test_the_command_and_the_skill_show_the_same_example(self):
        self.assertEqual(self.example(BUILD_COMMAND), self.example(DESIGN_SKILL))

    def test_the_example_reaches_the_build_stage_with_nothing_to_say(self):
        import json
        import tempfile
        from unittest import mock
        import check_spine
        requirements = self.example(BUILD_COMMAND)
        workdir = Path(tempfile.mkdtemp())
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        with mock.patch.object(check_spine, "find_toolchain", return_value=None):
            stages = check_spine.run(requirements, workdir)
        names = [stage.name for stage in stages]
        self.assertNotIn("schematic-notes", names, [s.detail for s in stages])
        self.assertEqual(names, ["board", "schematic", "footprint", "build"], names)
        self.assertEqual([s.status for s in stages[:-1]], [check_spine.OK] * 3)
        self.assertEqual(stages[-1].status, check_spine.COULD_NOT_RUN)   # no tsci offered here

if __name__ == "__main__":
    unittest.main()
