#!/usr/bin/env python3
"""
Re-introduce each defect and prove the suite goes red.

    tools/mutate.py tests/mutations/<table>.json
    tools/mutate.py --anchors tests/mutations/*.json      # anchors only, a second

Mutation testing is this project's acceptance bar and for two sprints it was enforced by memory.
That failed the way memory fails: ~30 mutations were run by hand in one sprint and two ESCAPED —
"the generator stops sizing traces" and "the placeholder list is never passed through" — each
surviving a green suite until somebody happened to try it. A retro action to build this tool did
not stick either, for want of a forcing function. This is the forcing function.

THE TABLE

    [{"file": "scripts/copper.py",
      "name": "drop the width margin",
      "find": "TRACE_WIDTH_MARGIN = 1.15",
      "replace": "TRACE_WIDTH_MARGIN = 1.0"}, ...]

`find` must occur EXACTLY ONCE in `file`, or the mutation is refused before anything runs. A
substitution that silently matched nothing was scored "caught" by an earlier hand-rolled
harness, because the suite it ran was the unmutated one.

THE THREE RULES THE HAND-ROLLED HARNESSES LEARNED, built in:

  * stderr is captured. `unittest` writes its verdict there, and a harness that drops it prints
    nothing for every mutation — which reads as success.
  * the file is restored in a `finally`, whatever happens, and the tool confirms the restore by
    running the suite once more at the end and refusing to report "all caught" if it is not green.
  * the bytecode cache is never consulted. Python validates a `.pyc` by the source's mtime in
    whole seconds and its size. `a + b` -> `a - b` is a same-size edit, and mutate-then-restore
    within one second is invisible to that check: the "restored" suite ran the MUTATED bytecode
    and reported red, which this tool's own tests caught on their first full run. So every suite
    run is `-B` with a fresh, empty cache prefix — pure source, every time.

WHAT PASSING MEANS

Every mutation turned the suite red, and the suite is green again with the files restored. A
mutation that leaves the suite green is a MISSING TEST, named, and the exit code says so. That is
the whole product: not "the tests pass" but "the tests would notice".
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

#: A developer's tool, not the product: it lives in tools/ and reaches the product's modules by path.
SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from outcomes import EXIT_OK, EXIT_COULD_NOT_RUN, EXIT_PROBLEMS as EXIT_ESCAPED, COULD_NOT_RUN, OK, PROBLEMS  # noqa: E402

CAUGHT, ESCAPED, REFUSED = "caught", "escaped", "refused"


def suite_is_green(root, tests):
    """
    Run the suite once, from source alone; the verdict is on stderr, which is why it is captured.

    `-B` writes no bytecode and a fresh `PYTHONPYCACHEPREFIX` means none pre-existing is read.
    Without both, a same-size mutation restored within a second is scored against stale `.pyc`.
    """
    import os
    import tempfile
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                       PYTHONPYCACHEPREFIX=tempfile.mkdtemp(prefix="mutate-pycache-"))
    result = subprocess.run(
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", tests],
        cwd=str(root), capture_output=True, text=True, env=environment)
    verdict = (result.stderr or "") + (result.stdout or "")
    return result.returncode == 0 and "\nOK" in verdict


def apply(root, mutation):
    """
    Substitute, or refuse. Returns the original text so the caller can restore it.

    Refusal is a result, not an error: a `find` that matches zero or two places means the table
    is wrong, and running the suite against an unmutated file would score a phantom "caught".
    """
    path = root / mutation["file"]
    if not path.is_file():
        # `anchors` refused this; `apply` read it and the tool died with a traceback (audit C8).
        return None, "%s does not exist" % mutation["file"]
    original = path.read_text()
    count = original.count(mutation["find"])
    if count != 1:
        return None, "`find` occurs %d time(s) in %s; it must occur exactly once" % (
            count, mutation["file"])
    path.write_text(original.replace(mutation["find"], mutation["replace"]))
    return original, None


def anchors(root, mutations):
    """
    Every mutation whose `find` does not occur exactly once — checked without running anything.

    A table is written against the code of its day and a later change moves the code under it:
    the mutation for the R6 escape was REFUSED for four days after P11 moved its anchor and
    nothing noticed until an audit ran the table (B8); the R9 table was refused three commits
    after it was written, when P20 re-indented the loop it anchored to. A refused mutation
    guards nothing. Anchors take a second to check; the suite takes minutes per table, so this is
    what runs at every commit and the full run is what runs per item and at the sprint's close.
    """
    wrong = []
    for mutation in mutations:
        path = root / mutation["file"]
        count = path.read_text().count(mutation["find"]) if path.is_file() else 0
        if count != 1:
            wrong.append((mutation.get("name", mutation["find"]), mutation["file"], count))
    return wrong


#: Two runs at once rewrite and restore the same files under each other, and both then report
#: verdicts neither earned — which happened, on 2026-09-29, when an R9 run and a P11 run
#: overlapped in the background. The lock is the tool refusing to produce a verdict it cannot
#: trust; it is removed in a `finally`, and a stale one left by a killed run says how to clear it.
LOCK_NAME = ".mutate.lock"


class AnotherRunIsActive(Exception):
    """A lock is held: some other mutate run is rewriting these files right now."""


class RedBeforeMutation(Exception):
    """The suite is not green before any mutation: a red suite catches nothing."""


def run(root, tests, mutations):
    """Every mutation, each restored before the next, and the suite confirmed green at the end."""
    lock = root / LOCK_NAME
    if lock.exists():
        raise AnotherRunIsActive("%s exists: another run is rewriting these files, or a killed "
                                 "one left its lock. Wait for it, or remove the lock once you "
                                 "are sure and check `git status` for a mutated file" % lock)
    lock.write_text(str(__import__("os").getpid()))
    try:
        # The pre-check ran BEFORE the lock was taken, so two runs started within its six
        # seconds both passed the lock test and both took the lock (audit C8). Under it now.
        if not suite_is_green(root, tests):
            raise RedBeforeMutation("the suite is not green BEFORE any mutation; a red suite catches nothing")
        return _run(root, tests, mutations)
    finally:
        lock.unlink(missing_ok=True)


def _run(root, tests, mutations):
    results = []
    for mutation in mutations:
        path = root / mutation["file"]
        original, refusal = apply(root, mutation)
        if refusal:
            results.append({"name": mutation.get("name", mutation["find"]),
                            "status": REFUSED, "detail": refusal})
            continue
        try:
            green = suite_is_green(root, tests)
        finally:
            path.write_text(original)
        results.append({"name": mutation.get("name", mutation["find"]),
                        "status": ESCAPED if green else CAUGHT,
                        "detail": "" if not green else
                        "the suite stayed green — no test notices this defect"})

    restored = suite_is_green(root, tests)
    return results, restored


def verdict(results, restored):
    if not restored:
        return EXIT_COULD_NOT_RUN
    if any(r["status"] in (ESCAPED, REFUSED) for r in results):
        return EXIT_ESCAPED
    return EXIT_OK


def render(results, restored, code):
    lines = [""]
    for r in results:
        mark = {CAUGHT: "caught ", ESCAPED: "ESCAPED", REFUSED: "refused"}[r["status"]]
        lines.append("  [%s] %s%s" % (mark, r["name"], ("  — " + r["detail"]) if r["detail"] else ""))
    lines.append("")
    if not restored:
        lines.append("  THE SUITE IS NOT GREEN WITH THE FILES RESTORED. Nothing above can be "
                     "trusted; something is left mutated or was already broken.")
    elif code == EXIT_OK:
        lines.append("  every mutation was caught, and the suite is green with the files restored")
    else:
        escaped = sum(1 for r in results if r["status"] == ESCAPED)
        refused = sum(1 for r in results if r["status"] == REFUSED)
        lines.append("  %d escaped, %d refused: each ESCAPED line is a missing test"
                     % (escaped, refused))
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("table", nargs="+", help="JSON lists of {file, find, replace, name?}")
    parser.add_argument("--anchors", action="store_true",
                        help="only check that every `find` occurs exactly once; run nothing")
    parser.add_argument("--root", default=".", help="the project root the files are under")
    parser.add_argument("--tests", default="tests", help="the test directory, relative to root")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    mutations = []
    for table in args.table:
        try:
            mutations += json.loads(Path(table).read_text())
        except (OSError, ValueError) as broken:
            print("could not read the table %s: %s" % (table, broken), file=sys.stderr)
            return EXIT_COULD_NOT_RUN

    if args.anchors:
        wrong = anchors(root, mutations)
        for name, file, count in wrong:
            print("  [refused] %s — `find` occurs %d time(s) in %s" % (name, count, file))
        print("  %d mutation(s) in %d table(s): %s" % (
            len(mutations), len(args.table),
            "every anchor present, once" if not wrong else "%d would be refused" % len(wrong)))
        return EXIT_ESCAPED if wrong else EXIT_OK

    try:
        results, restored = run(root, args.tests, mutations)
    except (AnotherRunIsActive, RedBeforeMutation) as stopped:
        print(str(stopped), file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    code = verdict(results, restored)
    if args.json:
        print(json.dumps({"tool": "mutate", "restored": restored,
                          "status": {EXIT_OK: OK, EXIT_ESCAPED: "escaped",
                                     EXIT_COULD_NOT_RUN: COULD_NOT_RUN}[code],
                          "mutations": results}, indent=2))
    else:
        sys.stdout.write(render(results, restored, code))
    return code


if __name__ == "__main__":
    sys.exit(main())
