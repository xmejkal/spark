"""P505 (#694): no tracked file holds a real board's full MAC address. A full address is either masked (its last three
bytes `xx`) or made up for a test (`8c:bf:ea:00:00:0N`, `aa:bb:cc:...`, `11:22:33:...`, `de:ad:be:ef:...`).

In a repository `git grep` reads the tracked files. The push hook runs the suite in a `git archive` of the commit, with no
`.git` and with `SPARK_GATE_TREE=archive` (`suite_runs.GATE_TREE`): there the archive's files ARE the tracked files, and
the test walks them (P797: `git grep` found no repository there, said nothing, and the test passed blind at every push).
Anywhere else with no repository, such as a mutation copy holding ignored folders, it skips and says why."""

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit
from suite_runs import GATE_ARCHIVE, GATE_TREE  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
#: A full address with ':' or '-' between its bytes (mixed separators too), not part of a longer run of hex pairs.
MAC = re.compile(r"(?<![0-9a-fA-F:-])[0-9a-fA-F]{2}(?:[:-][0-9a-fA-F]{2}){5}(?![0-9a-fA-F:-])")
#: An Espressif address written with no separators (a USB serial), the spelling the first pattern cannot see.
BARE = re.compile(r"(?<![0-9a-fA-F])8cbfea[0-9a-f]{6}", re.IGNORECASE)
MADE_UP = re.compile(r"(?:8c:bf:ea:00:00:0\d|aa:bb:cc:.*|11:22:33:.*|de:ad:be:ef:.*)")
#: What `git grep` is asked for: a line that may hold a full address; `_real` judges it.
CANDIDATE = r"[0-9a-f]{2}([:-][0-9a-f]{2}){5}|8cbfea[0-9a-f]{6}"
#: Folders the walk never enters: git's own, Python's caches, the JS dependencies the gate lends by a link.
NOT_WALKED = frozenset({".git", "__pycache__", "node_modules"})
#: Why the test skips: nothing here says which files are tracked.
NOT_CHECKED = "no git repository and not the gate's archive: the addresses were not checked"
#: How much of a file git reads to call it binary: a NUL byte there (`git grep -I`).
SNIFF_BYTES = 8000


def real_addresses(root=ROOT, environ=os.environ):
    """
    [file, line number] of each full address that is neither masked nor made up, in the tracked text files under `root`;
    None when nothing says which files are tracked: no repository, and `environ` does not mark the gate's archive.
    """
    root = Path(root)
    if (root / ".git").exists():  # a folder, or a file in a worktree
        found = subprocess.run(["git", "grep", "-nIiE", CANDIDATE], cwd=root, capture_output=True, text=True).stdout.splitlines()
        return [line.split(":", 2)[:2] for line in found if _real(line.split(":", 2)[2])]
    if environ.get(GATE_TREE) != GATE_ARCHIVE:
        return None
    candidate = re.compile(CANDIDATE, re.IGNORECASE)
    return [[name, str(number)] for name, text in _text_files(root)
            for number, line in enumerate(text.splitlines(), 1) if candidate.search(line) and _real(line)]


def _text_files(root):
    """(name below `root`, text) of each file the walk reads: never a link, never a folder of NOT_WALKED, never binary."""
    for folder, folders, files in os.walk(root):  # os.walk never follows a linked folder
        folders[:] = sorted(each for each in folders if each not in NOT_WALKED)
        for name in sorted(files):
            whole = Path(folder) / name
            if whole.is_symlink():
                continue
            data = whole.read_bytes()
            if b"\0" not in data[:SNIFF_BYTES]:
                yield whole.relative_to(root).as_posix(), data.decode(errors="replace")


def _real(text):
    """True when the text holds a full address that is neither masked nor made up."""
    spaced = [m.group(0).lower().replace("-", ":") for m in MAC.finditer(text)]
    bare = [m.group(0).lower() for m in BARE.finditer(text)]
    return any(not MADE_UP.fullmatch(each) for each in spaced) or any(not each.startswith("8cbfea00000") for each in bare)


class NoRealBoardAddressTest(unittest.TestCase):
    #: The tree and the environment the test reads; a test aims a subclass at a folder of its own.
    root, environ = ROOT, os.environ

    def test_no_tracked_file_holds_a_real_full_mac(self):
        found = real_addresses(self.root, self.environ)
        if found is None:
            self.skipTest(NOT_CHECKED)
        self.assertEqual(found, [], "mask it as 8c:bf:ea:xx:xx:xx, or use a made-up address in a test")


def a_tree(files):
    """A folder with no `.git` holding `files` (name: text)."""
    root = Path(tempfile.mkdtemp())
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    return root


#: A made-up address that the test treats as real: none of MADE_UP's patterns, not masked. Built from its bytes, so this
#: file holds no address for the real test to find.
LOOKS_REAL = "board %s\n" % ":".join(["24", "6f", "28", "1a", "2b", "3c"])
GATE = {GATE_TREE: GATE_ARCHIVE}


class TheGateArchiveIsWalkedTest(unittest.TestCase):
    """P797: in the hook's archive there is no `.git`; the files are walked, and anywhere else with none the test skips."""

    def test_an_address_in_the_archive_is_found_and_a_masked_one_is_not(self):
        root = a_tree({"docs/a.md": "x\n" + LOOKS_REAL, "docs/b.md": "board 24:6f:28:xx:xx:xx\n"})
        self.assertEqual(real_addresses(root, GATE), [["docs/a.md", "2"]])

    def test_a_linked_folder_a_cache_and_a_binary_file_are_not_walked(self):
        root = a_tree({"kept/a.md": LOOKS_REAL, "__pycache__/m.txt": LOOKS_REAL, "bin.dat": "\0" + LOOKS_REAL})
        os.symlink(root / "kept", root / "lent")
        outside = a_tree({"x.md": "ok\n"})
        (outside / "kept").symlink_to(root / "kept")
        self.assertEqual(real_addresses(root, GATE), [["kept/a.md", "1"]])
        self.assertEqual(real_addresses(outside, GATE), [])

    def test_with_no_repository_and_no_marker_the_test_skips_and_says_why(self):
        root = a_tree({"a.md": LOOKS_REAL})
        self.assertIsNone(real_addresses(root, {}))
        self.assertIsNone(real_addresses(root, {GATE_TREE: "copy"}))

        class Elsewhere(NoRealBoardAddressTest):
            pass
        Elsewhere.root, Elsewhere.environ = root, {}
        result = unittest.TestResult()
        Elsewhere("test_no_tracked_file_holds_a_real_full_mac").run(result)
        self.assertEqual([reason for _, reason in result.skipped], [NOT_CHECKED], "a skip is said, never a silent pass")
        self.assertEqual((result.failures, result.errors), ([], []))


if __name__ == "__main__":
    unittest.main()
