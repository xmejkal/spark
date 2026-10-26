#!/usr/bin/env python3
"""
The suite, on the tree as COMMITTED — not the working tree.

    tools/check_commit.py                    # HEAD, the quick run: what the push hook runs
    tools/check_commit.py fd25f15            # any commit
    tools/check_commit.py [commit] --full    # the full run: every test, slow ones too

A commit's message said "Ran 589 tests, OK" while the commit as committed ran 562 FAILED: the
run was on the working tree, and the file it imported was staged one commit later (sprint-4 close
audit, C3). A number a message carries must be measured on what the message describes, so this
archives the commit into a scratch directory and measures there. The push hook runs it.

The quick run (P425) skips the tests marked `@slow` in tests/suite_runs.py and says how many it skipped; it is not the
suite count. The full run, `--full`, runs every test: before a PR is marked ready and before an auto-mode merge.

The suite runs with a temp folder of its own, and whatever it leaves there fails the push (P172): one run
left 2,291 entries, 26 MB, and nothing counted them. The archive itself goes when the gate ends.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

#: A developer's tool, not the product: it lives in tools/ and reaches the product's modules by path.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.append(str(ROOT / "tests"))  # after the rest: only suite_runs is wanted, and no test helper may shadow a module

from outcomes import EXIT_FOR, EXIT_OK as EXIT_OK, EXIT_PROBLEMS as EXIT_PROBLEMS, EXIT_COULD_NOT_RUN, status_of  # noqa: E402
from suite_runs import SLOW_PREFIX  # noqa: E402

#: How many of the names left behind the gate's line shows; the count says the rest.
NAMES_SHOWN = 3


def archive(root, commit, into):
    """The committed tree, extracted; nothing from the working tree."""
    listed = subprocess.run(["git", "-C", str(root), "archive", commit], capture_output=True)
    if listed.returncode != 0:
        raise ValueError(listed.stderr.decode(errors="replace").strip() or "git archive failed")
    subprocess.run(["tar", "-x", "-C", str(into)], input=listed.stdout, check=True)


def lend_node_modules(tree):
    """
    Let the archived tree use this checkout's installed JS dependencies.

    `git archive` carries `bun.lock` and not `node_modules`, so the converter's own suite cannot
    run in the archive without either a network install on every push or this. The code under test
    is still the COMMITTED code — only the dependencies are borrowed, and they are the ones the
    committed lockfile names. `check_spine` lends `node_modules` to its build directory for exactly
    the same reason.
    """
    installed = ROOT / "tools" / "circuit-to-wokwi" / "node_modules"
    borrower = tree / "tools" / "circuit-to-wokwi"
    if installed.is_dir() and borrower.is_dir() and not (borrower / "node_modules").exists():
        (borrower / "node_modules").symlink_to(installed)


def code_lines(source):
    """A file's lines that are neither docstring, comment nor blank — the size W15b talks about."""
    import ast
    import io
    import tokenize
    total = len(source.splitlines())
    blank = sum(1 for line in source.splitlines() if not line.strip())
    comments = sum(token.string.count("\n") + 1 for token in tokenize.generate_tokens(io.StringIO(source).readline)
                   if token.type == tokenize.COMMENT)
    docs = 0
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            written = ast.get_docstring(node, clean=False)
            if written:
                docs += written.count("\n") + 1
    return total - blank - comments - docs


def scripts_size(root, rev):
    """The code lines of `scripts/*.py` at a commit, read from git with no checkout; None for an unknown commit."""
    listed = subprocess.run(["git", "-C", str(root), "ls-tree", "--name-only", rev, "scripts/"],
                            capture_output=True, text=True)
    if listed.returncode != 0:
        return None
    return sum(code_lines(subprocess.run(["git", "-C", str(root), "show", "%s:%s" % (rev, name)],
                                         capture_output=True, text=True).stdout)
               for name in listed.stdout.split() if name.endswith(".py"))


def size_line(root, commit, base="origin/main"):
    """
    "scripts/: 5,228 code lines (+40 since origin/main)" — the product's size and what this push adds to it
    (P99). It replaced a cap that failed the suite: P95 raised that cap six times, each time to whatever was
    measured, and it prompted one refactor of two lines. A number said at every push, with its reason in
    the card's closing comment (DoD 7), is what the PO asked the cap to be.
    """
    now = scripts_size(root, commit)
    if now is None:
        return "scripts/: size not measured (no commit %s)" % commit
    merge_base = subprocess.run(["git", "-C", str(root), "merge-base", commit, base], capture_output=True, text=True)
    then = scripts_size(root, merge_base.stdout.strip()) if merge_base.returncode == 0 else None
    growth = "" if then is None else " (%+d since %s)" % (now - then, base)
    return "scripts/: {:,} code lines{}".format(now, growth)


def without_git_variables():
    """
    The environment minus every GIT_* variable. Git hands its hooks GIT_DIR — absolute in a worktree — and a suite that
    inherits it runs its throwaway repositories' git against the repository being pushed (P105).
    """
    return {name: value for name, value in os.environ.items() if not name.startswith("GIT_")}


def leftovers(folder):
    """The names in `folder`, sorted; None when it cannot be listed — a count not taken is never a count of none."""
    try:
        return sorted(os.listdir(folder))
    except OSError:
        return None


def temp_line(left):
    """The gate's line about what the suite left in its temp folder (P172); `left` None means it could not be counted."""
    if left is None:
        return "temp: what the suite left behind could not be counted — P172"
    shown = ", ".join(left[:NAMES_SHOWN]) + (", …" if len(left) > NAMES_SHOWN else "")
    return "temp: the suite left {:,} {} behind ({}) — P172".format(len(left), "entry" if len(left) == 1 else "entries", shown)


def suite_line(said, quick, slow_skipped):
    """
    The suite's verdict line from the lines the runner said: "quick run: Ran N of M tests in S s (K slow tests skipped;
    the full run is check_commit.py --full) / OK", or "full run: Ran M tests in S s / OK". The quick line is built so
    that it cannot be quoted as the suite's count: it names what it left out.
    """
    ran = next((re.match(r"Ran (\d+) tests? in ([\d.]+)s", line) for line in said if line.startswith("Ran ")), None)
    verdict = [line for line in said if not line.startswith("Ran ")]
    if ran is None:
        return " / ".join(["quick run" if quick else "full run"] + said)
    total, seconds = int(ran.group(1)), float(ran.group(2))
    if quick:
        counted = "Ran {:,} of {:,} tests in {:.1f} s ({:,} slow {} skipped; the full run is check_commit.py --full)".format(
            total - slow_skipped, total, seconds, slow_skipped, "test" if slow_skipped == 1 else "tests")
        return " / ".join(["quick run: " + counted] + verdict)
    return " / ".join(["full run: Ran {:,} tests in {:.1f} s".format(total, seconds)] + verdict)


def measure(tree, full=False):
    """
    (suite verdict line, ok, left) for the tree at `tree`. `left` is what the suite left in
    the empty temp folder it was given (P172), None when that could not be listed; the folder goes once counted.
    The quick run (P425) sets SPARK_SUITE=quick, so the tests marked slow skip; `full` runs every test.
    """
    lend_node_modules(tree)
    temp = tempfile.mkdtemp(prefix="spark-commit-temp-")
    try:
        env = {name: value for name, value in without_git_variables().items() if name != "SPARK_SUITE"}
        env.update(TMPDIR=temp)
        if not full:
            env["SPARK_SUITE"] = "quick"
        suite = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"] + ([] if full else ["-v"]),
                               cwd=str(tree), capture_output=True, text=True, env=env)
        left = leftovers(temp)
    finally:
        shutil.rmtree(temp, ignore_errors=True)  # a plain rmtree: it never chmods and never follows a link
    suite_said = [line for line in (suite.stderr + suite.stdout).splitlines() if line.startswith(("Ran ", "OK", "FAILED"))]
    # The verdict's own `skipped=N` caps the count: a failure's traceback can embed a child's -v lines.
    skipped_in_all = sum(int(count) for line in suite_said for count in re.findall(r"skipped=(\d+)", line))
    slow_skipped = min(skipped_in_all, sum(1 for line in suite.stderr.splitlines() if " ... skipped '%s" % SLOW_PREFIX in line))
    # The mutation tables' anchors are no longer checked here (P208): the tables are history, and a moved line no
    # longer blocks a push.
    return suite_line(suite_said, not full, slow_skipped), suite.returncode == 0, left


def main(argv=None):
    parser = argparse.ArgumentParser(description="The suite on the tree as committed: the quick run by default.")
    parser.add_argument("commit", nargs="?", default="HEAD", help="the commit to measure (default HEAD)")
    parser.add_argument("--full", action="store_true",
                        help="the full run: every test, the slow ones too; before a PR is marked ready and before an auto-mode merge")
    given = parser.parse_args(sys.argv[1:] if argv is None else argv)
    scratch = Path(tempfile.mkdtemp(prefix="spark-commit-"))
    try:
        return gate(ROOT, given.commit, scratch, given.full)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)  # the archive, 6.2 MB a push (P172); a link in it is unlinked, never followed


def gate(root, commit, scratch, full=False):
    """Archive `commit` into `scratch`, measure it, say the lines; the exit code."""
    began = time.monotonic()
    try:
        archive(root, commit, scratch)
    except (ValueError, subprocess.CalledProcessError) as broken:
        print("could not archive %s: %s" % (commit, broken), file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    suite, ok, left = measure(scratch, full=full)
    short = subprocess.run(["git", "-C", str(root), "rev-parse", "--short", commit],
                           capture_output=True, text=True).stdout.strip()
    print("%s as committed, %s" % (short, suite))
    if left != []:
        print("  " + temp_line(left))
    print("  " + size_line(root, commit))
    sys.path.insert(0, str(ROOT / "tools"))
    import check_backlog
    backlog = check_backlog.main()
    if not full:
        print("  quick run: the seconds above are the tests alone; the board check and the size line come on top, "
              "{:.0f} s for the whole gate".format(time.monotonic() - began))
    return EXIT_FOR[status_of(problems=not ok or backlog != 0 or bool(left), unchecked=left is None)]


if __name__ == "__main__":
    sys.exit(main())
