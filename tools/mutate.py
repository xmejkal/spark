#!/usr/bin/env python3
"""
Re-introduce each defect and prove the suite goes red.

    tools/mutate.py tests/mutations/<table>.json
    tools/mutate.py --anchors tests/mutations/*.json      # anchors and syntax only, a second
    tools/mutate.py tests/mutations/*.json --for scripts/run_scenario.py --copy    # one file's rows, in a copy
    tools/mutate.py tests/mutations/*.json --for $changed --copy   # a branch's: changed=$(git diff --name-only origin/main...HEAD)
    tools/mutate.py tests/mutations/*.json --retarget scripts/a.py scripts/spark/a.py   # a file moved: its rows follow
    tools/mutate.py --ledger                              # the ledger's lines, counted by status
    tools/mutate.py tests/mutations/*.json --tier critical,new --copy   # a sweep: only the rows of these tiers
    tools/mutate.py tests/mutations/*.json --tier-count   # how many rows each tier holds; runs nothing
    tools/mutate.py tests/mutations/*.json --tier critical,new --budget 20 --copy   # a sweep that stops within 20 minutes

Mutation testing is this project's acceptance bar and for two sprints it was enforced by memory.
That failed the way memory fails: ~30 mutations were run by hand in one sprint and two ESCAPED —
"the generator stops sizing traces" and "the placeholder list is never passed through" — each
surviving a green suite until somebody happened to try it. A retro action to build this tool did
not stick either, for want of a forcing function. This is the forcing function.

THE TABLE

    [{"file": "scripts/spark/design/copper.py",
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

A COPY (--copy) is deleted after the run, so the run does not run the whole suite again to prove the files restored: that
check cost 207 s on 2026-10-28 (P424), and a copy has nothing to restore. `--retarget OLD NEW` edits the text of the
tables and moves no other row; run `--anchors` after it. It exits 2 when no row names OLD, and runs alone. Both `near_tests` and the import check name a module under
`scripts/` by its dotted name when every folder on the way has an `__init__.py`, so a package module (`spark.core.outcomes`)
meets the tests that import it; `scripts/spark/firmware/stand_in/machine.py` stays `machine`. Rows do not run
in parallel: `--jobs 4` saved 24 s on 8 rows (rows file of P440), under the minute that would pay for the flag.

A red pre-check names its tests: the `FAIL:`, `ERROR:` and `FAILED` lines of the verdict (P787), so a red copy is never
guessed at.

THE LEDGER (P787) is `tests/mutations/ledger.jsonl`, in git: one line per row key, written after every run that plants
rows, with or without `--copy` (`--anchors` and `--retarget` write none). It says which rows were caught, when, by which
test, at which content of their file, so a sweep runs rows in tiers (THE TIERS below) instead of all 3000 at once. The run
writes it in the tree it was given, never in the copy: the copy is removed, and the real tree's ledger is merged with
the run's lines, the newer date winning, so a line a person wrote during the run is kept. In the real tree only a run whose
files are restored writes it (a verdict nothing can trust records nothing); a copy writes each row's line at once, below. `--ledger` prints the counts by status. `tools/ledger.py`
holds the words and the store.

THE TIERS (P787) put each row of the given tables under one of the plan's words, each a fact the tool reads from the row
and the ledger (`ledger.tier_of`): *critical*, the row carries `"tier": "critical"`; *new*, no ledger line at the row's
file's current blob, or a line there that says `escaped` (a missing test, so it runs again) or `refused` (--anchors'
business); *proving*, caught once at the current blob; *proven*, caught twice or more there. *Retired* is PR 5's and is
not decided yet. The blob rule alone says what is stale: an edit of a file makes every row on it new again, and a row
with no line is new, never proven. `--tier critical,new` runs only the rows of the named tiers, in the sweep's order:
critical, new in the tables' given order (name the oldest table first), proving, proven oldest date first; the header
line says which tiers and how many rows, and the rest of the output is as without it. Without `--tier` every row runs.
`--tier-count` prints how many rows each tier holds and runs nothing.

In a copy each row's ledger line is written as soon as the row is done, dated then, so a run that SIGTERM or a crash
stops keeps every line it recorded (PR 1's review, row 50: a 180-minute slice killed at minute 179 lost everything). In the
real tree the lines wait for the after-suite, which says whether anything can be trusted, and carry the run's end.

THE BUDGET (P787) `--budget MINUTES` counts from the run's start, the fixed overhead inside it: the copy, the pre-check
suite, the near sets. Before each row the run asks whether the row's expected seconds would cross what is left, and stops
there: every row from that one on is left for the next sweep. The expected seconds are a fact, never a guess
(`expected_seconds`): the row's ledger line's `s` (its last duration, at whatever blob), else the median of the rows run
so far in this run, else the pre-check suite's measured seconds (a row with no near test costs a whole suite). The
closing line says what ran, as `budget 20 min: ran 42 of 61 selected (critical 12/12, new 30/35, proving 0/9, proven 0/5);
19 left for the next sweep`, and `--json` gains `budget` with the same facts (`minutes, ran, selected, left, by_tier`).
A left row is not a pass: it was not run, and the exit code speaks for the rows that were. The PO's defaults (2026-11-12):
20 minutes for a wave-end sweep a person waits for, 180 for an unattended night slice.

WHAT PASSING MEANS

Every mutation turned the suite red, and the suite is green again with the files restored. A
mutation that leaves the suite green is a MISSING TEST, named, and the exit code says so. That is
the whole product: not "the tests pass" but "the tests would notice".
"""

import argparse
import contextlib
import json
import re
import signal
import statistics
import subprocess
import sys
import tempfile
import threading
import time
from collections import namedtuple
from datetime import datetime
from pathlib import Path

#: A developer's tool, not the product: it lives in tools/ and reaches the product's modules by path.
SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import scratch  # noqa: E402  (P435) stdlib only: removes the old folders a killed run left
import ledger  # noqa: E402  (P787) stdlib only: the ledger's lines and their store

from spark.core.outcomes import EXIT_OK, EXIT_COULD_NOT_RUN, EXIT_PROBLEMS as EXIT_ESCAPED, COULD_NOT_RUN, OK  # noqa: E402

CAUGHT, ESCAPED, REFUSED = "caught", "escaped", "refused"
#: The names of the three kinds of folder a run makes in the temp folder; the sweep at the next start removes old ones (P435).
RUN_PREFIX, IMPORT_PREFIX, COPY_PREFIX = "mutate-run-", "mutate-import-", "mutate-copy-"
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
    run = Path(tempfile.mkdtemp(prefix=prefix))
    try:
        (run / "tmp").mkdir()  # it must exist: a TMPDIR that does not is skipped, and the temp files go elsewhere
        # A mutation run never runs the quick run (P425): a defect only a slow test catches would escape it.
        environment = dict({name: value for name, value in os.environ.items() if name != "SPARK_SUITE"},
                           PYTHONDONTWRITEBYTECODE="1", PYTHONPYCACHEPREFIX=str(run / "pycache"), TMPDIR=str(run / "tmp"))
        yield environment
    finally:
        shutil.rmtree(run, ignore_errors=True)


class SuiteResult(namedtuple("SuiteResult", "green red_lines")):
    """
    Result: one suite run, true when green. `red_lines` are the lines of unittest's verdict that say what went red: each
    `FAIL:` and `ERROR:` line, each traceback's last `...Error:` line, the `Ran N tests` line and the `FAILED (...)` line
    (`RED_LINE`), so a red run names its tests (P787: a red pre-check that said only "not green" was read as a bug of
    `--copy`, which it was not shown to be). Empty when green.
    """
    __slots__ = ()

    def __bool__(self):
        return self.green


#: A line of unittest's verdict that names a red test or sums the red run.
RED_LINE = re.compile(r"^(?:(?:FAIL|ERROR): .*|FAILED \(.*|Ran \d+ tests? in .*|[\w.]+Error: .*)$", re.M)
#: The test module in a `FAIL:` or `ERROR:` line: `FAIL: test_add (test_m.T)` names `test_m` (3.11+: `(test_m.T.test_add)`).
RED_TEST = re.compile(r"^(?:FAIL|ERROR): \S+ \((\w+)")


def caught_by(result):
    """
    The ledger's `by` for a near run that went red: the module of the first test the verdict names, or `suite` when no
    line names one (a crash before any test). A plain `False` (a test's stand-in for the run) names none either.
    """
    for red in getattr(result, "red_lines", ()):
        found = RED_TEST.match(red)
        if found:
            return found.group(1)
    return ledger.SUITE


def suite_is_green(root, tests, only=(), failfast=False):
    """
    Run the suite once — or `only` those test modules — from source alone; the verdict is on stderr,
    which is why it is captured. `failfast` stops at the first failure: one is all a catch needs. The answer is a
    `SuiteResult`: true when green, and when red it carries the lines that say which tests.

    `-B` writes no bytecode and `_from_source`'s fresh `PYTHONPYCACHEPREFIX` means none pre-existing is read (P172:
    one run of the suite left 87 caches behind, and a sweep left its tests' folders).
    """
    stop = ["-f"] if failfast else []
    command, where = (([sys.executable, "-B", "-m", "unittest"] + stop + list(only), Path(root) / tests) if only else
                      ([sys.executable, "-B", "-m", "unittest", "discover", "-s", tests] + stop, Path(root)))
    with _from_source(RUN_PREFIX) as environment:
        result = subprocess.run(command, cwd=str(where), capture_output=True, text=True, env=environment)
    verdict = (result.stderr or "") + (result.stdout or "")
    green = result.returncode == 0 and "\nOK" in verdict
    return SuiteResult(green, () if green else tuple(RED_LINE.findall(verdict)) or (verdict.strip().splitlines() or ["no output"])[-1:])


# --- MVP ---
def import_spec(root, file):
    """
    Where to import the module at `file` from and by what name, as (folder for sys.path, dotted name) (P440). A path under
    `scripts/` is imported by its path below it (`scripts/spark/core/outcomes.py` is `spark.core.outcomes`, an `__init__.py`
    is its package) only when every folder between `scripts/` and the file has an `__init__.py`. Any other path, such as
    `scripts/spark/firmware/stand_in/machine.py`, is imported by its stem from its own folder.
    """
    parts = Path(file).parts
    if parts[:1] == ("scripts",) and all((Path(root).joinpath(*parts[:i + 1]) / "__init__.py").is_file() for i in range(1, len(parts) - 1)):
        dotted = list(Path(file).with_suffix("").parts[1:])
        if dotted and dotted[-1] == "__init__":
            dotted.pop()
        if dotted:
            return Path(root) / "scripts", ".".join(dotted)
    return (Path(root) / file).parent, Path(file).stem


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
        dotted = import_spec(root, mutated_file)[1]
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
    The last line of what importing `file` says, from source alone, or None when it imports. A module of a package is
    imported by its dotted name with `scripts/` on the path, so it finds its package (P440); see `import_spec`.
    """
    folder, dotted = import_spec(root, file)
    with _from_source(IMPORT_PREFIX) as environment:
        done = subprocess.run([sys.executable, "-B", "-c", "import sys; sys.path.insert(0, sys.argv[1]); __import__(sys.argv[2])",
                               str(folder), dotted], cwd=str(root), capture_output=True, text=True, env=environment)
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


# --- MVP ---
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
    if not moved:
        print("no row of %s has %s as its file; nothing moved" % (", ".join(map(str, tables)), old), file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    for table, (changed, _) in moved.items():
        Path(table).write_text(changed)
    print("  moved %d row(s) from %s to %s in %d of %d table(s); run --anchors to prove them" % (
        sum(count for _, count in moved.values()), old, new, len(moved), len(tables)))
    return EXIT_OK


# --- MVP ---
def copy_of(root):
    """
    The tree at `root` in a temporary folder, without .git, worktrees or caches (P208). A run that mutates the copy never
    rewrites a file that a person or another agent has open: two council agents once mutated inside one worktree. The
    JavaScript dependencies are borrowed, not copied, as the push gate does.
    """
    import shutil
    made = Path(tempfile.mkdtemp(prefix=COPY_PREFIX))
    copy = made / root.name
    try:
        shutil.copytree(root, copy, symlinks=True,
                        ignore=shutil.ignore_patterns(".git", ".worktrees", "node_modules", "__pycache__", LOCK_NAME))
        for folder in (Path("."), Path("tools") / "circuit-to-wokwi"):
            if (root / folder / "node_modules").is_dir() and (copy / folder).is_dir():
                (copy / folder / "node_modules").symlink_to(root / folder / "node_modules")
    except BaseException:  # a file it cannot read, a read-only root, or a stop: no half-made folder stays
        scratch.remove_tree(made)
        raise
    return copy


# --- MVP ---
def remove_old_scratch():
    """
    Remove the folders of the three prefixes that a stopped run left in the temp folder, older than a day (P435). Every
    mutation run does it at its start, with or without --copy (--anchors and --retarget do not).
    """
    for prefix in (RUN_PREFIX, IMPORT_PREFIX, COPY_PREFIX):
        scratch.remove_old_folders(tempfile.gettempdir(), prefix, time.time())


# --- MVP ---
@contextlib.contextmanager
def sigterm_as_exit():
    """
    Inside, SIGTERM raises SystemExit, so a `finally` runs (P435). Installed only in the main thread and only over the
    default handler, and restored on the way out. SIGKILL cannot be caught: the sweep at the next start covers it.
    """
    def stop(number, frame):
        raise SystemExit(128 + number)

    # Only the default handler is replaced: a handler somebody else set (a runner, a test harness) is theirs and stays.
    installed = threading.current_thread() is threading.main_thread() and signal.getsignal(signal.SIGTERM) == signal.SIG_DFL
    if installed:
        signal.signal(signal.SIGTERM, stop)
    try:
        yield
    finally:
        if installed:
            signal.signal(signal.SIGTERM, signal.SIG_DFL)


# --- MVP ---
@contextlib.contextmanager
def sigterm_held():
    """
    Inside, a SIGTERM waits (main thread only): the copy's removal finishes, and the signal arrives after, to the handler
    of sigterm_as_exit, which exits 143. Without it the handler's SystemExit would stop the removal half way.
    """
    if threading.current_thread() is not threading.main_thread():
        yield
        return
    held = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGTERM})
    try:
        yield
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, held)


class Budget:
    """
    Value: the minutes a run may take, counted from `started` (a monotonic second taken at the run's start, so the copy
    and the pre-check suite count inside), as `--budget` gives them (P787). `left(now)` is what remains; `allows(now,
    seconds)` says whether a row expected to take `seconds` ends within it. Not a clock: the run reads `time.monotonic`
    as the rest of this tool does, and a test fakes the durations through the ledger's `s` and through `started`.
    """

    def __init__(self, minutes, started):
        self.minutes, self.started = minutes, started

    def left(self, now):
        """The seconds left at `now`, negative once the budget is crossed."""
        return self.minutes * 60 - (now - self.started)

    def allows(self, now, seconds):
        """A row that takes `seconds` fits when it ends within the budget; one that would cross it does not."""
        return seconds <= self.left(now)


def expected_seconds(row, known, durations, suite_seconds):
    """
    The seconds `row` is expected to take, a fact and never a guess (P787): its ledger line's `s` (`known`, by key: the
    row's last duration, at whatever blob), else the median of `durations`, the rows run so far in this run, else
    `suite_seconds`, the pre-check suite's measured time, which a row with no near test costs.
    """
    key = ledger.row_key(row)
    if key in known:
        return known[key]
    if durations:
        return statistics.median(durations)
    return suite_seconds


class AnotherRunIsActive(Exception):
    """A lock is held: some other mutate run is rewriting these files right now."""


class RedBeforeMutation(Exception):
    """The suite is not green before any mutation: a red suite catches nothing. The message names the red tests."""


def run(root, tests, mutations, copied=False, ledger_store=None, budget=None):
    """
    Every mutation, each restored before the next, and the suite confirmed green at the end.

    `copied` says `root` is a copy that is deleted after the run, so there is nothing to restore and the end check is
    skipped (P424: it cost a whole suite, 207 s on 2026-10-28). `ledger_store`, a `ledger.LedgerStore`, gets one line per
    row when the run's files are restored (P787); None records nothing. `budget`, a `Budget`, stops the run before the
    row that would cross it; None runs every row.
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
        checked = time.monotonic()
        before = suite_is_green(root, tests)
        if not before:
            raise RedBeforeMutation("the suite is not green BEFORE any mutation; a red suite catches nothing"
                                    + "".join("\n  " + line for line in getattr(before, "red_lines", ())))
        suite_seconds = time.monotonic() - checked  # what a row with no near test costs: the budget's last fact
        return _run(root, tests, mutations, near_sets(root, tests, mutations), copied, ledger_store, budget, suite_seconds)
    finally:
        lock.unlink(missing_ok=True)


def _run(root, tests, mutations, near_by_file, copied, ledger_store=None, budget=None, suite_seconds=None):
    results, imports_before, lines = [], {}, []
    known = {entry["key"]: entry["s"] for entry in ledger_store.read()} if budget is not None and ledger_store is not None else {}
    for mutation in mutations:
        if budget is not None and not budget.allows(time.monotonic(), expected_seconds(mutation, known, [entry["s"] for entry in lines], suite_seconds)):
            break  # this row and every one after it are left for the next sweep
        started = time.monotonic()
        path = root / mutation["file"]
        file = mutation["file"]
        blob = ledger.blob_of(path.read_bytes()) if path.is_file() else None  # the file as the run read it, before the row

        def noted(status, which_run=None, who=None, detail=""):
            """The row's result for the report, and its ledger line: `which_run` is near or full, `who` the ledger's `by`."""
            results.append({"name": mutation.get("name", mutation["find"]), "status": status, "by": which_run, "detail": detail})
            lines.append(ledger.line(mutation, blob, _stamp(), status, who, round(time.monotonic() - started)))
            if ledger_store is not None and copied:  # a copy has no after-suite to distrust the row later: written now (row 50)
                ledger_store.record(lines[-1:])

        if file.endswith(".py") and file not in imports_before:  # a file that never imported alone cannot be judged so
            imports_before[file] = path.is_file() and _import_error(root, file) is None
        original, refusal = apply(root, mutation)
        if refusal:
            noted(REFUSED, detail=refusal)
            continue
        try:
            refusal = _loads(file, path.read_text())
            if not refusal and imports_before.get(file):
                failed = _import_error(root, file)
                refusal = failed and "the mutant of %s does not import: %s" % (file, failed)
            if refusal:
                noted(REFUSED, detail=refusal)
                continue
            near = near_by_file.get(mutation["file"], ())
            near_run = suite_is_green(root, tests, only=near, failfast=True) if near else None
            caught_near = bool(near) and not near_run
            green = False if caught_near else suite_is_green(root, tests, failfast=True)
        finally:
            path.write_text(original)
        if green:
            noted(ESCAPED, who=ledger.ESCAPE, detail="the suite stayed green — no test notices this defect")
        else:
            noted(CAUGHT, NEAR if caught_near else FULL, caught_by(near_run) if caught_near else ledger.SUITE)

    restored = copied or bool(suite_is_green(root, tests))
    if ledger_store is not None and restored and not copied:  # a verdict nothing can trust records nothing
        ended = _stamp()  # the run's end, when the facts are known (the review of PR 1), on every line at once
        ledger_store.record([dict(entry, date=ended) for entry in lines])
    return results, restored


def _stamp():
    """Now, with the machine's zone, in whole seconds: the ledger's `date`."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


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
    parser.add_argument("table", nargs="*", help="JSON lists of {file, find, replace, name?}")
    parser.add_argument("--anchors", action="store_true",
                        help="only check that every `find` occurs exactly once and that each mutant compiles (.py) "
                             "or parses (.json); run nothing. A run also imports each mutated module")
    parser.add_argument("--root", default=".", help="the project root the files are under")
    parser.add_argument("--tests", default="tests", help="the test directory, relative to root")
    parser.add_argument("--for", dest="paths", nargs="+", metavar="PATH",
                        help="only the rows for these files, or for everything under these folders")
    parser.add_argument("--copy", action="store_true",
                        help="mutate a temporary copy of the tree, never the files you or an agent have open; "
                             "the copy is removed also when SIGTERM stops the run")
    parser.add_argument("--retarget", nargs=2, metavar=("OLD", "NEW"),
                        help="instead of a run: in these tables, move every row whose `file` is OLD to NEW (the text is "
                             "edited, so the tables keep their alignment); then prove them with --anchors")
    parser.add_argument("--ledger", action="store_true",
                        help="instead of a run: count the lines of the ledger (tests/mutations/ledger.jsonl under --root) "
                             "by status; every run that plants rows writes the ledger, --anchors and --retarget do not")
    parser.add_argument("--tier", metavar="TIERS",
                        help="only the rows of these tiers, a comma list of %s, in that order (the ledger decides each "
                             "row's tier: critical is the row's own `\"tier\"` key; new has no line at its file's current "
                             "blob, or an escaped or refused one; proving was caught once there, proven twice or more)" % ",".join(ledger.TIERS))
    parser.add_argument("--tier-count", action="store_true",
                        help="instead of a run: how many rows of the given tables each tier holds; runs nothing")
    parser.add_argument("--budget", type=int, metavar="MINUTES",
                        help="stop before the row that would cross this many minutes, counted from the run's start (the copy "
                             "and the pre-check suite inside); a row's expected seconds are its ledger line's `s`, else the "
                             "median of this run's rows, else the pre-check suite's; the closing line says how many rows ran, "
                             "how many are left, per tier. A left row is not a pass. The PO's defaults: 20 for a sweep, 180 for a night")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    ledger_store = ledger.LedgerStore(root / args.tests / "mutations" / ledger.LEDGER_NAME)
    if args.ledger:
        if args.table or args.anchors or args.paths or args.copy or args.retarget or args.tier is not None or args.tier_count or args.budget is not None:
            parser.error("--ledger runs alone: it takes no table, --anchors, --for, --copy, --retarget, --tier, --tier-count or --budget")
        return print_ledger(ledger_store, root, args.json)
    if not args.table:
        parser.error("the following arguments are required: table")
    if args.retarget:
        if args.anchors or args.paths or args.copy or args.tier is not None or args.tier_count or args.budget is not None:
            parser.error("--retarget runs alone: it takes no --anchors, --for, --copy, --tier, --tier-count or --budget")
        return retarget_tables(args.table, *args.retarget)
    if args.tier_count and (args.anchors or args.copy or args.tier is not None or args.budget is not None):
        parser.error("--tier-count runs alone: it takes the tables and --for, no --anchors, --copy, --tier or --budget")
    if args.budget is not None and args.budget <= 0:
        parser.error("--budget takes a whole number of minutes above 0, not %d" % args.budget)
    if args.budget is not None and args.anchors:
        parser.error("--anchors runs no row: it takes no --budget")
    wanted = list(dict.fromkeys(args.tier.split(","))) if args.tier is not None else []  # `--tier ""` is an error; `new,new` is new
    if args.tier is not None and any(tier not in ledger.TIERS for tier in wanted):
        parser.error("--tier takes a comma list of %s, not %s" % (",".join(ledger.TIERS), args.tier))
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
    if args.tier_count:
        return print_tier_counts(ledger.tiers_of(root, mutations, ledger_store.read()), len(args.table), args.json)
    header = tiers = None
    if wanted or args.budget is not None:  # before the run: the run's own lines would move rows to proving
        tiers = ledger.tiers_of(root, mutations, ledger_store.read())
    if wanted:
        mutations = tiers.selected(wanted)
        header = {"selected": wanted, "rows": len(mutations), "counts": tiers.counts()}
        if not mutations:
            print("  no row is in the tier(s) %s: nothing to run" % args.tier, file=sys.stderr)
            return EXIT_OK
        if not args.json:
            print(tier_header(header))

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
    budget = Budget(args.budget, started) if args.budget is not None else None  # the overhead below counts inside it
    remove_old_scratch()
    where = None
    with sigterm_as_exit():  # also around the copy's removal: no window back at the default handler
        try:
            where = copy_of(root) if args.copy else root
            results, restored = run(where, args.tests, mutations, copied=where is not root, ledger_store=ledger_store, budget=budget)
        except (AnotherRunIsActive, RedBeforeMutation) as stopped:
            print(str(stopped), file=sys.stderr)
            return EXIT_COULD_NOT_RUN
        finally:
            if where is not None and where is not root:
                with sigterm_held():
                    scratch.remove_tree(where.parent)
    code = verdict(results, restored)
    recorded = {"path": str(ledger_store.path.relative_to(root)), "recorded": len(results) if restored else 0,
                "rows": len(ledger_store.read())}
    spent = budget_report(budget, tiers, wanted or ledger.TIERS, mutations[:len(results)]) if budget is not None else None
    if args.json:
        print(json.dumps({"tool": "mutate", "restored": restored,
                          "status": {EXIT_OK: OK, EXIT_ESCAPED: "escaped",
                                     EXIT_COULD_NOT_RUN: COULD_NOT_RUN}[code],
                          "seconds": round(time.monotonic() - started), "mutations": results, "ledger": recorded,
                          **({"tiers": header} if header else {}), **({"budget": spent} if spent else {})}, indent=2))
    else:
        sys.stdout.write(render(results, restored, code))
        print("  %d mutation(s) in %.0f s" % (len(results), time.monotonic() - started))
        print("  %d row(s) recorded in %s (%d in all)" % (recorded["recorded"], recorded["path"], recorded["rows"]))
        if spent:
            print(budget_line(spent))
    return code


def budget_report(budget, tiers, wanted, ran):
    """
    `--budget`'s facts, for the JSON and the closing line: the minutes, how many rows `ran` of the selected, how many are
    left (selected and not run: not a pass), and the same per tier. `wanted` names the selected tiers (all four without
    `--tier`); a tier not wanted selected nothing. A row is counted under its tier by its key.
    """
    by_tier = {}
    for tier in ledger.TIERS:
        rows = tiers.rows[tier] if tier in wanted else []
        keys = {ledger.row_key(row) for row in rows}
        by_tier[tier] = {"ran": sum(1 for row in ran if ledger.row_key(row) in keys), "selected": len(rows)}
    selected = sum(counts["selected"] for counts in by_tier.values())
    return {"minutes": budget.minutes, "ran": len(ran), "selected": selected, "left": selected - len(ran), "by_tier": by_tier}


def budget_line(report):
    """`budget 20 min: ran 42 of 61 selected (critical 12/12, new 30/35, proving 0/9, proven 0/5); 19 left for the next sweep`."""
    return "  budget %d min: ran %d of %d selected (%s); %d left for the next sweep" % (
        report["minutes"], report["ran"], report["selected"],
        ", ".join("%s %d/%d" % (tier, counts["ran"], counts["selected"]) for tier, counts in report["by_tier"].items()), report["left"])


def tier_header(header):
    """The header line of a `--tier` run: which tiers it selected, how many rows that is, and every tier's count."""
    return "  tiers %s: %d row(s) selected (%s)" % (",".join(header["selected"]), header["rows"], tier_counts(header["counts"]))


def tier_counts(counts):
    """`critical 12, new 30, proving 9, proven 10`: every tier's count, in the tiers' order."""
    return ", ".join("%s %d" % (tier, counts[tier]) for tier in ledger.TIERS)


def print_tier_counts(tiers, tables, as_json):
    """`--tier-count`: how many rows of the tables each tier holds, as one line or as JSON; exit 0, nothing runs."""
    counts = tiers.counts()
    if as_json:
        print(json.dumps({"tool": "mutate", "tables": tables, "rows": sum(counts.values()), "tiers": counts}, indent=2))
    else:
        print("  tiers of %d row(s) in %d table(s): %s" % (sum(counts.values()), tables, tier_counts(counts)))
    return EXIT_OK


def print_ledger(ledger_store, root, as_json):
    """`--ledger`: the ledger's lines counted by status, as one line or as JSON; exit 0 (an empty ledger is empty)."""
    counts = ledger_store.counts()
    path = str(ledger_store.path.relative_to(root))
    if as_json:
        print(json.dumps({"tool": "mutate", "ledger": path, "rows": sum(counts.values()), "statuses": counts}, indent=2))
    else:
        said = ", ".join("%d %s" % (count, status) for status, count in counts.items())
        print("  ledger %s: %d row(s)%s" % (path, sum(counts.values()), ": " + said if said else ""))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
