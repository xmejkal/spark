#!/usr/bin/env python3
"""
The suite and every mutation anchor, on the tree as COMMITTED — not the working tree.

    tools/check_commit.py            # HEAD
    tools/check_commit.py fd25f15    # any commit

A commit's message said "Ran 589 tests, OK" while the commit as committed ran 562 FAILED: the
run was on the working tree, and the file it imported was staged one commit later (sprint-4 close
audit, C3). A number a message carries must be measured on what the message describes, so this
archives the commit into a scratch directory and measures there. Run before every push.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

#: A developer's tool, not the product: it lives in tools/ and reaches the product's modules by path.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from outcomes import EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN  # noqa: E402


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


def measure(tree):
    """(suite verdict line, anchors verdict line, ok) for the tree at `tree`."""
    lend_node_modules(tree)
    suite = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                           cwd=str(tree), capture_output=True, text=True)
    suite_said = [line for line in (suite.stderr + suite.stdout).splitlines()
                  if line.startswith(("Ran ", "OK", "FAILED"))]
    tables = sorted((tree / "tests" / "mutations").glob("*.json"))
    anchors = subprocess.run([sys.executable, str(tree / "tools" / "mutate.py"), "--anchors",
                              *map(str, tables), "--root", str(tree)],
                             cwd=str(tree), capture_output=True, text=True)
    anchors_said = anchors.stdout.strip().splitlines()[-1:] if anchors.stdout.strip() else ["(no output)"]
    ok = suite.returncode == 0 and anchors.returncode == 0
    return " / ".join(suite_said), anchors_said[-1].strip(), ok


def main(argv=None):
    commit = (argv or sys.argv[1:] or ["HEAD"])[0]
    root = ROOT
    scratch = Path(tempfile.mkdtemp(prefix="spark-commit-"))
    try:
        archive(root, commit, scratch)
    except (ValueError, subprocess.CalledProcessError) as broken:
        print("could not archive %s: %s" % (commit, broken), file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    suite, anchors, ok = measure(scratch)
    short = subprocess.run(["git", "-C", str(root), "rev-parse", "--short", commit],
                           capture_output=True, text=True).stdout.strip()
    print("%s as committed: %s; %s" % (short, suite, anchors))
    return EXIT_OK if ok else EXIT_PROBLEMS


if __name__ == "__main__":
    sys.exit(main())
