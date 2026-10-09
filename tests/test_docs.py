"""P104: the docs name only what is there (docs/2026-10-05-readme-design.md §5)."""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import check_docs  # noqa: E402


def page(root, name, text):
    path = Path(root) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


class TheChecksTest(unittest.TestCase):
    def test_a_command_or_script_that_does_not_exist_is_named(self):
        said = check_docs.missing_names("run `/spark:build`, then `/spark:frobnicate`, check_all.py and frob.py")
        self.assertEqual(said, ["/spark:frobnicate names no command", "frob.py names no script"])

    def test_a_file_spark_writes_into_a_project_may_be_named(self):
        self.assertEqual(check_docs.missing_names("the project gets `pins.py`"), [])

    def test_every_command_skill_and_agent_must_be_listed(self):
        with tempfile.TemporaryDirectory() as root:
            for name in ("commands/build.md", "skills/spark-review/SKILL.md", "agents/part-finder.md"):
                page(root, name, "")
            page(root, "README.md", "/spark:build, spark-review, part-finder")
            page(root, "docs/guide/commands.md", "/spark:build, spark-review")
            self.assertEqual(check_docs.unlisted(Path(root)), ["docs/guide/commands.md does not name part-finder"])

    def test_a_table_row_naming_no_skill_or_agent_is_named(self):
        text = ("## Skills\n\n| skill | what |\n| --- | --- |\n| **spark-review** | x |\n| **spark-dream** | y |\n\n"
                "## Agents\n\n| agent | what |\n| --- | --- |\n| `part-finder` | z |\n")
        self.assertEqual(check_docs.unknown_in_tables(text), ["## Skills names spark-dream, which is no skill"])

    def test_a_flag_its_script_does_not_have_is_named(self):
        text = "```sh\npython3 scripts/check_all.py --project . --json --frob\n```\nand `board.py status --when-in DIR`"
        self.assertEqual(check_docs.missing_flags(text), ["check_all.py shows --frob, which its --help does not list"])

    def test_a_script_whose_help_fails_is_said_so(self):
        with tempfile.TemporaryDirectory() as root:
            page(root, "scripts/broken.py", "import no_such_module_anywhere\n")
            self.assertEqual(check_docs.missing_flags("`broken.py --x --y`", Path(root)),
                             ["broken.py --help exits 1, so the flags shown with it cannot be checked"])

    def test_a_broken_link_or_anchor_is_named(self):
        with tempfile.TemporaryDirectory() as root:
            guide = page(root, "docs/guide/a.md", "# A\n\n## The flow — an item's stages\n")
            text = "[ok](a.md#the-flow--an-items-stages) [gone](b.md) [bad](a.md#nowhere) [web](https://x.org/y)"
            self.assertEqual(check_docs.broken_links(guide, text),
                             ["a.md links b.md, which does not exist", "a.md links a.md#nowhere, which has no such heading"])

    def test_an_anchor_follows_github_s_slug(self):
        self.assertEqual(check_docs.slug("`/spark:build` — one command"), "sparkbuild--one-command")
        self.assertEqual(check_docs.slug("The flow — an item's stages"), "the-flow--an-items-stages")

    def test_a_link_to_a_folder_is_fine(self):
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / "parts").mkdir()
            guide = page(root, "docs/guide/a.md", "# A\n")
            self.assertEqual(check_docs.broken_links(guide, "[parts](../../parts/)"), [])

    def test_an_output_with_no_date_and_version_is_named(self):
        text = "<!-- output: run 2026-10-06, spark 0.6.0 -->\n```text\nok\n```\n\n```text\nundated\n```\n"
        self.assertEqual(check_docs.undated_outputs(text),
                         ["the output at line 6 has no `<!-- output: run DATE, spark VERSION -->` above it"])

    def test_a_runnable_example_must_end_as_marked(self):
        text = "<!-- runs: exit 0 -->\n```sh\ntrue\n```\n<!-- runs: exit 0 -->\n```sh\nexit 3\n```\n```sh\nexit 5\n```\n"
        self.assertEqual(check_docs.failed_examples(text), ["the example `exit 3` exits 3, not 0"])

    def test_a_runnable_example_that_hangs_is_named(self):
        with mock.patch.object(check_docs, "RUN_TIMEOUT", 1):
            said = check_docs.failed_examples("<!-- runs: exit 0 -->\n```sh\nsleep 5\n```\n")
        self.assertEqual(said, ["the example `sleep 5` takes longer than 1 s — not a light example"])

    def test_a_runnable_example_gets_a_store_of_its_own(self):
        outer = os.environ.get("SPARK_HOME", "")
        text = '<!-- runs: exit 0 -->\n```sh\ntest -n "$SPARK_HOME" && test "$SPARK_HOME" != "%s"\n```\n' % outer
        self.assertEqual(check_docs.failed_examples(text), [])

    def test_the_readme_must_say_the_plugin_s_version(self):
        with tempfile.TemporaryDirectory() as root:
            page(root, ".claude-plugin/plugin.json", '{"version": "9.9.9"}')
            self.assertEqual(check_docs.version_mismatch("v9.9.9 · MIT", Path(root)), [])
            self.assertEqual(check_docs.version_mismatch("v1.0.0 · MIT", Path(root)),
                             ["README.md does not say v9.9.9, the version plugin.json ships"])

    def test_a_personal_path_is_named(self):
        # A temp directory, not a home: test_orphans refuses a home path in any shipped file, tests included (P44).
        self.assertEqual(check_docs.personal_paths(Path("README.md"), "fine\nsee /private/var/folders/x\n"),
                         ["README.md line 2 names a personal path or checkout: /private/"])



class TheDocsTest(unittest.TestCase):
    def test_the_docs_name_only_what_is_there(self):
        self.assertEqual(check_docs.problems(), [])


if __name__ == "__main__":
    unittest.main()
