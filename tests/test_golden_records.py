"""P715 (#966, W6-R1): what parts.py, boards.py, tools.py and cost.py print today, and what their write Operations
write, stays what they print and write, so the records codes and moves break nothing. No golden reaches the network or
runs an installer: RecordsGuardTest proves the guard, and RecordsGoldenTest runs no Case unless a child finds none of
golden_records.GUARDED and finds the fake pdftotext."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

import golden_bench  # noqa: E402
import golden_checks  # noqa: E402
import golden_records  # noqa: E402
import tools  # noqa: E402


def guard_holds(folder, shims):
    """None when a child with the fakes in `shims` finds none of GUARDED and finds the fake pdftotext, else what it found."""
    env = golden_records.child_env(Path(folder) / "guard-store", shims)
    if env["PATH"] != str(shims):
        return "a child's PATH is not the fakes' folder alone: %s" % env["PATH"]
    found = golden_records.guarded_found(env)
    if found:
        return "a child finds an installer, a downloader or claude: %s" % found
    if any(env.get(name) != golden_checks.CLOSED_PROXY for name in golden_checks.PROXIES):
        return "a child's proxies are not the closed port"
    if env["HOME"] == os.environ.get("HOME"):
        return "a child keeps the parent's HOME"
    with mock.patch.dict(os.environ, {"PATH": env["PATH"]}):
        reader = tools.find("pdf-text", None, personal=Path(shims) / "no-tools.json").command
    if reader != [str(Path(shims) / "pdftotext")]:
        return "the pdf-text tool found is not the fake: %r" % reader
    return None


class RecordsGuardTest(unittest.TestCase):
    """The guard: a child's PATH is the fakes' folder alone, which holds no curl, claude or install manager, its proxies
    are the closed port, its HOME is empty, and it carries no secret."""

    @classmethod
    def setUpClass(cls):
        cls.folder = Path(tempfile.mkdtemp())
        cls.shims = golden_records.make_fakes(cls.folder)

    def env(self):
        return golden_records.child_env(self.folder / "store", self.shims)

    def test_the_guarded_list_is_every_manager_and_curl_and_claude(self):
        self.assertEqual(set(golden_records.GUARDED), {"npm", "python3", "brew", "apt-get", "curl", "claude"})

    def test_a_child_finds_no_installer_downloader_or_claude(self):
        self.assertEqual(golden_records.guarded_found(self.env()), [])

    def test_the_guard_finds_a_program_on_a_wider_path(self):
        # The guard can fail: /bin/sh is found by `command -v` on a PATH that names /bin.
        env = dict(self.env(), PATH="%s:/bin" % self.shims)
        with mock.patch.object(golden_records, "GUARDED", ("sh",)):
            self.assertEqual(golden_records.guarded_found(env), ["/bin/sh"])

    def test_a_curl_in_the_fakes_folder_is_found(self):
        folder = Path(tempfile.mkdtemp(dir=self.folder))
        shims = golden_records.make_fakes(folder)
        (shims / "curl").write_text("#!/bin/sh\nexit 1\n")
        (shims / "curl").chmod(0o755)
        self.assertIn("curl", guard_holds(folder, shims))

    def test_the_child_carries_no_secret_and_an_empty_home(self):
        secrets = {"GH_TOKEN": "gho_pretend", "ANTHROPIC_API_KEY": "sk-pretend", "WOKWI_CLI_TOKEN": "wok_pretend",
                   "MIRO_SECRET": "pretend"}
        with mock.patch.dict(os.environ, secrets):
            env = self.env()
        self.assertFalse(set(secrets) & set(env))
        self.assertEqual(list(Path(env["HOME"]).iterdir()), [])
        self.assertEqual(env["CLAUDE_CODE_SESSION_ID"], golden_records.SESSION)

    def test_the_guard_holds(self):
        self.assertIsNone(guard_holds(self.folder, self.shims))

    def test_the_fake_pdftotext_reads_page_one_and_ends_at_page_two(self):
        reader = str(self.shims / "pdftotext")
        one = subprocess.run([reader, "-layout", "-f", "1", "-l", "1", "x.pdf", "-"], env=self.env(), capture_output=True,
                             text=True, timeout=golden_bench.RUN_TIMEOUT_S)
        two = subprocess.run([reader, "-layout", "-f", "2", "-l", "2", "x.pdf", "-"], env=self.env(), capture_output=True,
                             text=True, timeout=golden_bench.RUN_TIMEOUT_S)
        self.assertEqual((one.returncode, two.returncode), (0, 1))
        self.assertIn("Forward voltage", one.stdout)


if __name__ == "__main__":
    unittest.main()
