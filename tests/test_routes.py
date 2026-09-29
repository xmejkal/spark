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
CHAIN = ("parts.py", "assign_pins.py", "emit_board.py", "emit_footprint.py", "check_spine.py")

BUILD_COMMAND = ROOT / "commands" / "build.md"
DESIGN_SKILL = ROOT / "skills" / "spark-design" / "SKILL.md"


def allowed_scripts(command_path):
    """The scripts a command's frontmatter lets it run, by file name."""
    text = command_path.read_text()
    front = text.split("---")[1] if text.startswith("---") else ""
    return set(re.findall(r"scripts/([a-z_]+\.py)", front))


class TheDocumentedFlowNamesTheChainTest(unittest.TestCase):
    def test_the_build_command_exists_and_may_run_every_link(self):
        self.assertTrue(BUILD_COMMAND.is_file(), "no /spark:build command")
        missing = sorted(set(CHAIN) - allowed_scripts(BUILD_COMMAND))
        self.assertEqual(missing, [], "/spark:build may not run: %s" % missing)

    def test_both_documents_name_every_link(self):
        # The command is the first thing a user reads, the skill the second; a link either one
        # forgets is a step the user takes with outside knowledge. The footprint step vanished
        # from the command and the suite stayed green while only the skill was held to this.
        for document in (BUILD_COMMAND, DESIGN_SKILL):
            text = document.read_text()
            missing = [script for script in CHAIN if script not in text]
            self.assertEqual(missing, [], "%s never names: %s" % (document.name, missing))

    def test_the_design_skill_does_not_start_with_a_hand_written_board(self):
        # The generator comes before any instruction to write tscircuit by hand.
        text = DESIGN_SKILL.read_text()
        self.assertLess(text.index("emit_board.py"), text.index("<chip>"))

    def test_the_command_shows_each_link_being_typed(self):
        # A mention is not a step. With the footprint line removed from the steps block, the
        # name survived in the prose and the frontmatter and the name test stayed green (W12).
        # What the user types is what the code blocks show, so every link must be typed there.
        # Split on fence lines: the odd segments are inside a fence. (A regex pairing "```\n"
        # with the next "```" paired each block's closer with the next opener and read the prose
        # between blocks instead — every link came back missing on the real file.)
        segments = re.split(r"^```.*$", BUILD_COMMAND.read_text(), flags=re.M)
        blocks = segments[1::2]
        self.assertGreater(len(blocks), 1, "the command document has lost its code blocks")
        typed = set(re.findall(r"scripts/([a-z_]+\.py)", "\n".join(blocks)))
        missing = sorted(set(CHAIN) - typed)
        self.assertEqual(missing, [], "/spark:build never shows these being typed: %s" % missing)

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
        # Named in a document, and runnable as documented: each answers --help with usage. Every
        # script a command may run is held to it too — check_design answered "no design at
        # --help", exit 1, for a year (intake O4c).
        import subprocess
        routed = set(CHAIN)
        for command in (ROOT / "commands").glob("*.md"):
            routed |= allowed_scripts(command)
        for script in sorted(routed):
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


class AStrangerCanBuildTest(unittest.TestCase):
    """
    The audit followed /spark:build's documented steps from a fresh directory and reached no
    build (B5, B6, B19): every script refused "no project here", and the board file imported a
    footprint no document said how to write. This runs the documented steps, as documented, from
    a directory that holds nothing but the requirements file. The tsci build itself needs
    tscircuit and stays a manual proof, gated on its verdict.
    """

    def setUp(self):
        import json
        import tempfile
        self.here = Path(tempfile.mkdtemp())
        example = json.loads(re.search(r"```json\n(.*?)```", BUILD_COMMAND.read_text(), re.S).group(1))
        (self.here / "requirements.json").write_text(json.dumps(example))

    def run_step(self, *argv):
        import subprocess
        script = ROOT / "scripts" / argv[0]
        result = subprocess.run([sys.executable, str(script), *argv[1:]], cwd=str(self.here),
                                capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr

    def test_the_library_is_listed_from_nowhere(self):
        code, out, err = self.run_step("boards.py", "--list")
        self.assertEqual(code, 0, err)
        self.assertIn("firebeetle2-esp32s3", out)
        code, out, err = self.run_step("parts.py", "--list")
        self.assertEqual(code, 0, err)
        self.assertIn("l9110s-module", out)

    def test_the_documented_steps_produce_a_board_file_and_its_footprint(self):
        code, out, err = self.run_step("assign_pins.py", "requirements.json")
        self.assertEqual(code, 0, err + out)
        self.assertIn("MOTOR_IA", out)
        code, board, err = self.run_step("emit_board.py", "requirements.json")
        self.assertEqual(code, 0, err)
        self.assertIn("<board", board)
        self.assertIn("plugin's library", err, "a design built from nowhere is told so")
        (self.here / "board.tsx").write_text(board)
        code, _, err = self.run_step("emit_footprint.py", "--board", "firebeetle2-esp32s3",
                                     "-o", "FireBeetle2Esp32S3.tsx")
        self.assertEqual(code, 0, err)
        self.assertTrue((self.here / "FireBeetle2Esp32S3.tsx").is_file())
        self.assertIn('from "./FireBeetle2Esp32S3"', board)

if __name__ == "__main__":
    unittest.main()
