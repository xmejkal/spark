#!/usr/bin/env python3
"""
The suite and every mutation anchor, on the tree as COMMITTED — not the working tree.

    tools/check_commit.py            # HEAD
    tools/check_commit.py fd25f15    # any commit

A commit's message said "Ran 589 tests, OK" while the commit as committed ran 562 FAILED: the
run was on the working tree, and the file it imported was staged one commit later (sprint-4 close
audit, C3). A number a message carries must be measured on what the message describes, so this
archives the commit into a scratch directory and measures there. Run before every push.

The suite runs with a temp folder of its own, and whatever it leaves there fails the push (P172): one run
left 2,291 entries, 26 MB, and nothing counted them. The archive itself goes when the gate ends.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

#: A developer's tool, not the product: it lives in tools/ and reaches the product's modules by path.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from outcomes import EXIT_FOR, EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN, status_of  # noqa: E402

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


def measure(tree):
    """
    (suite verdict line, anchors verdict line, ok, left) for the tree at `tree`. `left` is what the suite left in
    the empty temp folder it was given (P172), None when that could not be listed; the folder goes once counted.
    """
    lend_node_modules(tree)
    temp = tempfile.mkdtemp(prefix="spark-commit-temp-")
    try:
        suite = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                               cwd=str(tree), capture_output=True, text=True, env=dict(without_git_variables(), TMPDIR=temp))
        left = leftovers(temp)
    finally:
        shutil.rmtree(temp, ignore_errors=True)  # a plain rmtree: it never chmods and never follows a link
    suite_said = [line for line in (suite.stderr + suite.stdout).splitlines()
                  if line.startswith(("Ran ", "OK", "FAILED"))]
    tables = sorted((tree / "tests" / "mutations").glob("*.json"))
    anchors = subprocess.run([sys.executable, str(tree / "tools" / "mutate.py"), "--anchors",
                              *map(str, tables), "--root", str(tree)],
                             cwd=str(tree), capture_output=True, text=True)
    anchors_said = anchors.stdout.strip().splitlines()[-1:] if anchors.stdout.strip() else ["(no output)"]
    ok = suite.returncode == 0 and anchors.returncode == 0
    return " / ".join(suite_said), anchors_said[-1].strip(), ok, left


def main(argv=None):
    commit = (argv or sys.argv[1:] or ["HEAD"])[0]
    scratch = Path(tempfile.mkdtemp(prefix="spark-commit-"))
    try:
        return gate(ROOT, commit, scratch)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)  # the archive, 6.2 MB a push (P172); a link in it is unlinked, never followed


def gate(root, commit, scratch):
    """Archive `commit` into `scratch`, measure it, say the lines; the exit code."""
    try:
        archive(root, commit, scratch)
    except (ValueError, subprocess.CalledProcessError) as broken:
        print("could not archive %s: %s" % (commit, broken), file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    suite, anchors, ok, left = measure(scratch)
    short = subprocess.run(["git", "-C", str(root), "rev-parse", "--short", commit],
                           capture_output=True, text=True).stdout.strip()
    print("%s as committed: %s; %s" % (short, suite, anchors))
    if left != []:
        print("  " + temp_line(left))
    print("  " + size_line(root, commit))
    sys.path.insert(0, str(ROOT / "tools"))
    import check_backlog
    backlog = check_backlog.main()
    return EXIT_FOR[status_of(problems=not ok or backlog != 0 or bool(left), unchecked=left is None)]


if __name__ == "__main__":
    sys.exit(main())
