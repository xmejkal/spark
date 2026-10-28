#!/usr/bin/env python3
"""
Re-introduce each defect and prove the suite goes red.

    tools/mutate.py tests/mutations/<table>.json
    tools/mutate.py --anchors tests/mutations/*.json      # anchors and syntax only, a second
    tools/mutate.py tests/mutations/*.json --for scripts/run_scenario.py --copy    # one file's rows, in a copy
    tools/mutate.py tests/mutations/*.json --for $changed --copy   # a branch's: changed=$(git diff --name-only origin/main...HEAD)

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

THE FOUR RULES BUILT IN (the first three learned from the hand-rolled harnesses):

  * stderr is captured. `unittest` writes its verdict there, and a harness that drops it prints
    nothing for every mutation — which reads as success.
  * the file is restored in a `finally`, whatever happens, and the tool confirms the restore by
    running the suite once more at the end and refusing to report "all caught" if it is not green.
  * a mutant that cannot load is refused, naming the file (P186). A replacement that breaks the
    file's syntax or import, or a JSON file's format, turns the suite red for a reason no test
    chose: a wrongly indented `pass` was scored caught that way. `--anchors` checks syntax and
    format without running anything; a run also imports the mutated module.
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
import contextlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

#: A developer's tool, not the product: it lives in tools/ and reaches the product's modules by path.
SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from outcomes import EXIT_OK, EXIT_COULD_NOT_RUN, EXIT_PROBLEMS as EXIT_ESCAPED, COULD_NOT_RUN, OK  # noqa: E402

CAUGHT, ESCAPED, REFUSED = "caught", "escaped", "refused"
#: Which run caught a mutation (P98): the tests near the mutated file, or the whole suite.
NEAR, FULL = "near", "full"


@contextlib.contextmanager
def _from_source(prefix):
    """
    The environment for one run from source alone, in a folder of its own: an empty bytecode cache and the run's temp
    files (TMPDIR), and the folder goes with the run (P172). Without the empty cache, a same-size mutation restored
    within a second is judged by stale `.pyc`.
    """
    import os
    import shutil
    import tempfile
    run = Path(tempfile.mkdtemp(prefix=prefix))
    try:
        (run / "tmp").mkdir()  # it must exist: a TMPDIR that does not is skipped, and the temp files go elsewhere
        # A mutation run never runs the quick run (P425): a defect only a slow test catches would escape it.
        environment = dict({name: value for name, value in os.environ.items() if name != "SPARK_SUITE"},
                           PYTHONDONTWRITEBYTECODE="1", PYTHONPYCACHEPREFIX=str(run / "pycache"), TMPDIR=str(run / "tmp"))
        yield environment
    finally:
        shutil.rmtree(run, ignore_errors=True)


def suite_is_green(root, tests, only=(), failfast=False):
    """
    Run the suite once — or `only` those test modules — from source alone; the verdict is on stderr,
    which is why it is captured. `failfast` stops at the first failure: one is all a catch needs.

    `-B` writes no bytecode and `_from_source`'s fresh `PYTHONPYCACHEPREFIX` means none pre-existing is read (P172:
    one run of the suite left 87 caches behind, and a sweep left its tests' folders).
    """
    stop = ["-f"] if failfast else []
    command, where = (([sys.executable, "-B", "-m", "unittest"] + stop + list(only), Path(root) / tests) if only else
                      ([sys.executable, "-B", "-m", "unittest", "discover", "-s", tests] + stop, Path(root)))
    with _from_source("mutate-run-") as environment:
        result = subprocess.run(command, cwd=str(where), capture_output=True, text=True, env=environment)
    verdict = (result.stderr or "") + (result.stdout or "")
    return result.returncode == 0 and "\nOK" in verdict


def dotted_name(file):
    """
    The name a module is imported by (P440): a path under `scripts/` by its path below it (`scripts/spark/core/outcomes.py`
    is `spark.core.outcomes`, an `__init__.py` is its package), any other path by its stem alone.
    """
    parts = list(Path(file).with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts[1:]) if len(parts) > 1 and parts[0] == "scripts" else parts[-1]


def near_tests(root, tests, mutated_file):
    """
    The test modules near a mutated file (P98): for a `.py` file the ones that import its module, for any
    other file the ones that name it. Each mutation meets these first — a defect a nearby test catches
    costs a second, not the whole suite — and only what they miss goes to the whole suite, so an escape is
    never reported on their word. Empty: the whole suite decides alone.

    A module in a package is imported by its dotted name (P440): `import spark.core.outcomes`, `from spark.core.outcomes
    import X` and `from spark.core import outcomes` all name it.
    """
    target = Path(mutated_file)
    if target.suffix != ".py":
        said = re.compile(re.escape(target.name))
    else:
        dotted = dotted_name(mutated_file)
        package, _, module = dotted.rpartition(".")
        said = re.compile(r"^\s*(?:import|from)\s+%s\b" % re.escape(dotted)
                          + (r"|^\s*from\s+%s\s+import\s+[^\n]*\b%s\b" % (re.escape(package), re.escape(module)) if package else ""), re.M)
    return sorted(path.stem for path in sorted((Path(root) / tests).glob("test_*.py"))
                  if said.search(path.read_text(errors="replace")))


def near_sets(root, tests, mutations):
    """
    Each mutated file's near tests, kept only where they pass on the clean tree on their own: a set that
    fails alone (a test leaning on another module's import) would make every mutation near it look caught.
    """
    found = {}
    for file in sorted({mutation["file"] for mutation in mutations}):
        near = tuple(near_tests(root, tests, file))
        found[file] = near if near and suite_is_green(root, tests, only=near) else ()
    return found


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


def _loads(file, text):
    """Why `text`, as `file`, cannot load, or None: a .py that does not compile, a .json that does not parse."""
    if file.endswith(".json"):
        try:
            json.loads(text)
        except ValueError as broken:
            return "the mutant of %s is not JSON: %s" % (file, broken)
    elif file.endswith(".py"):
        try:
            compile(text, file, "exec")
        except SyntaxError as broken:
            return "the mutant of %s does not compile: line %s, %s" % (file, broken.lineno, broken.msg)
    return None


def unloadable(root, mutations):
    """Every mutation whose mutant does not compile or parse, as (name, file, why), checked in memory: nothing runs."""
    said = []
    for mutation in mutations:
        path = root / mutation["file"]
        text = path.read_text() if path.is_file() else ""
        if text.count(mutation["find"]) == 1:
            why = _loads(mutation["file"], text.replace(mutation["find"], mutation["replace"]))
            if why:
                said.append((mutation.get("name", mutation["find"]), mutation["file"], why))
    return said


def _import_error(root, file):
    """
    The last line of what importing `file` says, from source alone, or None when it imports. A path under `scripts/` is
    imported by its dotted name with `scripts/` on the path, so a module of a package finds its package (P440); any other
    path is imported by its stem with its own folder on the path.
    """
    folder = root / "scripts" if Path(file).parts[:1] == ("scripts",) else (root / file).parent
    with _from_source("mutate-import-") as environment:
        done = subprocess.run([sys.executable, "-B", "-c", "import sys; sys.path.insert(0, sys.argv[1]); __import__(sys.argv[2])",
                               str(folder), dotted_name(file)], cwd=str(root), capture_output=True, text=True, env=environment)
    return None if done.returncode == 0 else (done.stderr.strip().splitlines() or ["exit %d" % done.returncode])[-1]


def anchors(root, mutations):
    """
    Every mutation whose `find` does not occur exactly once — checked without running anything.

    A table is written against the code of its day and a later change moves the code under it:
    the mutation for the R6 escape was REFUSED for four days after P11 moved its anchor and
    nothing noticed until an audit ran the table (B8); the R9 table was refused three commits
    after it was written, when P20 re-indented the loop it anchored to. A refused mutation
    guards nothing. Anchors take a second to check; the suite takes minutes per table, so this is
    what runs at every commit and the full run is what runs per item and when an epic is done.
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


def related(mutations, paths):
    """
    The mutations of the files under `paths` (P208): a file's own rows, or a folder's and everything under it. An
    argument may hold several names, one per line: zsh passes `$(git diff --name-only …)` in a variable as one.
    """
    wanted = [str(Path(part)) for path in paths for part in path.split()]
    return [mutation for mutation in mutations
            if any(mutation["file"] == path or mutation["file"].startswith(path + "/") for path in wanted)]


def retarget(text, old, new):
    """
    A table's text with the `file` of every row that names `old` changed to `new`, and how many rows that was (P440).

    It edits the text, never `json.dumps` of the rows: no table prints back as it is written, because they are hand-aligned,
    and 48 rows write `"file":"` with no space. It proves the edit by parsing both texts: the rows after must be the rows
    before with `old` replaced and nothing else. It raises ValueError when either text is not JSON or the proof fails.
    """
    changed, count = re.subn(r'("file"\s*:\s*)"%s"' % re.escape(old), lambda match: match.group(1) + json.dumps(new), text)
    before = json.loads(text)
    if json.loads(changed) != [dict(row, file=new) if isinstance(row, dict) and row.get("file") == old else row for row in before]:
        raise ValueError("the text edit of %s changed more or less than the rows that name it" % old)
    return changed, count


def retarget_tables(tables, old, new):
    """Move every row of `old` to `new` in the table files `tables`, all or none; the exit code, with the line it printed."""
    moved = {}
    for table in tables:
        try:
            changed, count = retarget(Path(table).read_text(), old, new)
        except (OSError, ValueError) as broken:
            print("could not retarget %s: %s" % (table, broken), file=sys.stderr)
            return EXIT_COULD_NOT_RUN
        if count:
            moved[table] = (changed, count)
    for table, (changed, _) in moved.items():
        Path(table).write_text(changed)
    print("  moved %d row(s) from %s to %s in %d of %d table(s); run --anchors to prove them" % (
        sum(count for _, count in moved.values()), old, new, len(moved), len(tables)))
    return EXIT_OK


def copy_of(root):
    """
    The tree at `root` in a temporary folder, without .git, worktrees or caches (P208). A run that mutates the copy never
    rewrites a file that a person or another agent has open: two council agents once mutated inside one worktree. The
    JavaScript dependencies are borrowed, not copied, as the push gate does.
    """
    import shutil
    import tempfile
    copy = Path(tempfile.mkdtemp(prefix="mutate-copy-")) / root.name
    shutil.copytree(root, copy, symlinks=True,
                    ignore=shutil.ignore_patterns(".git", ".worktrees", "node_modules", "__pycache__", LOCK_NAME))
    for folder in (Path("."), Path("tools") / "circuit-to-wokwi"):
        if (root / folder / "node_modules").is_dir() and (copy / folder).is_dir():
            (copy / folder / "node_modules").symlink_to(root / folder / "node_modules")
    return copy


class AnotherRunIsActive(Exception):
    """A lock is held: some other mutate run is rewriting these files right now."""


class RedBeforeMutation(Exception):
    """The suite is not green before any mutation: a red suite catches nothing."""


def run(root, tests, mutations, copied=False):
    """
    Every mutation, each restored before the next, and the suite confirmed green at the end.

    `copied` says `root` is a copy that is deleted after the run, so there is nothing to restore and the end check is
    skipped (P424: it cost a whole suite, 207 s on 2026-10-28).
    """
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
        return _run(root, tests, mutations, near_sets(root, tests, mutations), copied)
    finally:
        lock.unlink(missing_ok=True)


def _run(root, tests, mutations, near_by_file, copied=False):
    results, imports_before = [], {}
    for mutation in mutations:
        path = root / mutation["file"]
        file = mutation["file"]
        if file.endswith(".py") and file not in imports_before:  # a file that never imported alone cannot be judged so
            imports_before[file] = path.is_file() and _import_error(root, file) is None
        original, refusal = apply(root, mutation)
        if refusal:
            results.append({"name": mutation.get("name", mutation["find"]),
                            "status": REFUSED, "by": None, "detail": refusal})
            continue
        try:
            refusal = _loads(file, path.read_text())
            if not refusal and imports_before.get(file):
                failed = _import_error(root, file)
                refusal = failed and "the mutant of %s does not import: %s" % (file, failed)
            if refusal:
                results.append({"name": mutation.get("name", mutation["find"]),
                                "status": REFUSED, "by": None, "detail": refusal})
                continue
            near = near_by_file.get(mutation["file"], ())
            caught_near = bool(near) and not suite_is_green(root, tests, only=near, failfast=True)
            green = False if caught_near else suite_is_green(root, tests, failfast=True)
        finally:
            path.write_text(original)
        results.append({"name": mutation.get("name", mutation["find"]),
                        "status": ESCAPED if green else CAUGHT,
                        "by": None if green else (NEAR if caught_near else FULL),
                        "detail": "" if not green else
                        "the suite stayed green — no test notices this defect"})

    return results, copied or suite_is_green(root, tests)


def verdict(results, restored):
    if not restored:
        return EXIT_COULD_NOT_RUN
    if any(r["status"] in (ESCAPED, REFUSED) for r in results):
        return EXIT_ESCAPED
    return EXIT_OK


def render(results, restored, code):
    lines = [""]
    for r in results:
        mark = {CAUGHT: "caught %s" % r.get("by", FULL), ESCAPED: "ESCAPED", REFUSED: "refused"}[r["status"]]
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
                        help="only check that every `find` occurs exactly once and that each mutant compiles (.py) "
                             "or parses (.json); run nothing. A run also imports each mutated module")
    parser.add_argument("--root", default=".", help="the project root the files are under")
    parser.add_argument("--tests", default="tests", help="the test directory, relative to root")
    parser.add_argument("--for", dest="paths", nargs="+", metavar="PATH",
                        help="only the rows for these files, or for everything under these folders")
    parser.add_argument("--copy", action="store_true",
                        help="mutate a temporary copy of the tree, never the files you or an agent have open")
    parser.add_argument("--retarget", nargs=2, metavar=("OLD", "NEW"),
                        help="instead of a run: in these tables, move every row whose `file` is OLD to NEW (the text is "
                             "edited, so the tables keep their alignment); then prove them with --anchors")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.retarget:
        return retarget_tables(args.table, *args.retarget)
    root = Path(args.root).resolve()
    mutations = []
    for table in args.table:
        try:
            mutations += json.loads(Path(table).read_text())
        except (OSError, ValueError) as broken:
            print("could not read the table %s: %s" % (table, broken), file=sys.stderr)
            return EXIT_COULD_NOT_RUN
    if args.paths:
        mutations = related(mutations, args.paths)
        if not mutations:
            print("  no mutation is about %s: nothing to run" % " ".join(args.paths), file=sys.stderr)
            return EXIT_OK

    if args.anchors:
        wrong = anchors(root, mutations)
        for name, file, count in wrong:
            print("  [refused] %s — `find` occurs %d time(s) in %s" % (name, count, file))
        broken = unloadable(root, mutations)
        for name, file, why in broken:
            print("  [refused] %s — %s" % (name, why))
        wrong += broken
        print("  %d mutation(s) in %d table(s): %s" % (
            len(mutations), len(args.table),
            "every anchor present, once" if not wrong else "%d would be refused" % len(wrong)))
        return EXIT_ESCAPED if wrong else EXIT_OK

    started = time.monotonic()
    where = copy_of(root) if args.copy else root
    try:
        results, restored = run(where, args.tests, mutations, copied=where is not root)
    except (AnotherRunIsActive, RedBeforeMutation) as stopped:
        print(str(stopped), file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    finally:
        if where is not root:
            __import__("shutil").rmtree(where.parent, ignore_errors=True)
    code = verdict(results, restored)
    if args.json:
        print(json.dumps({"tool": "mutate", "restored": restored,
                          "status": {EXIT_OK: OK, EXIT_ESCAPED: "escaped",
                                     EXIT_COULD_NOT_RUN: COULD_NOT_RUN}[code],
                          "seconds": round(time.monotonic() - started), "mutations": results}, indent=2))
    else:
        sys.stdout.write(render(results, restored, code))
        print("  %d mutation(s) in %.0f s" % (len(results), time.monotonic() - started))
    return code


if __name__ == "__main__":
    sys.exit(main())
