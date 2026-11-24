#!/usr/bin/env python3
"""
The suite, on the tree as COMMITTED — not the working tree.

    tools/check_commit.py                    # HEAD, the story run: what the push hook runs
    tools/check_commit.py fd25f15            # any commit
    tools/check_commit.py [commit] --full    # the full run: every test, slow ones too

A commit's message said "Ran 589 tests, OK" while the commit as committed ran 562 FAILED: the
run was on the working tree, and the file it imported was staged one commit later (sprint-4 close
audit, C3). A number a message carries must be measured on what the message describes, so this
archives the commit into a scratch directory and measures there. The push hook runs it.

The story run (P714) runs the tests that tools/story_tests.py chooses from what the branch changed since origin/main, with
the `@slow` tests skipped. It reads the texts of tests/ and scripts/ in the archive, so it follows the imports (P1017).
A doubt about a file makes it the quick run (P425): every test but the slow ones, with a line that says why. Neither
is the suite count. The full run, `--full`, runs every test, at a sweep: the end of a wave or an epic, or when the PO
asks.

The suite runs with a temp folder of its own, and whatever it leaves there fails the push (P172): one run
left 2,291 entries, 26 MB, and nothing counted them. The archive itself goes when the gate ends.

The archive has no `.git`, so the suite runs with `SPARK_GATE_TREE=archive` (`suite_runs.GATE_TREE`): the test that no
tracked file holds a board's address walks the archive's files, which are exactly the tracked ones (P797). Without it
that test asked `git grep`, which found no repository and so nothing, and the check never ran at the gate.
A red run names its red tests under the verdict line, each `FAIL:`, `ERROR:` and `...Error:` line (P797).

The page script's drift check (P1061): page_script.ts is the source, and the committed page_script.js must be what tsc
7.0 compiles from it. At every `--full`, and when the branch changed one of SCRIPT_SOURCES (or git could not tell), the
gate compiles the archive's `.ts` into a temporary folder and compares the bytes. A missing tsc, or another version, is
could-not-run; a tsc error or other bytes is a problem, with the fix `tsc -p scripts/spark/flow`. Either stops the gate
before the suite runs. A tree with no page_script.ts, from before P1061, has nothing to compile.

The mutation rows' check (P897, which puts back what P208 took out): every row of every tests/mutations/*.json must have
its `find` once in its file, whatever the branch changed, so that a merge which moves an anchored line says so at once.
The .py and .json rows of a changed file or a changed table also get their mutants compiled in memory; at `--full`, or
when git could not tell what changed, every such row does. On an idle machine: 0.45 s for the anchors of all rows, 0.4 to
0.8 s with the compile of one changed file or table, 22.7 s at `--full` (the review measured 1 to 4 s and 79 s at load
22). A refused row is a problem, printed as `table[index] name`, and it stops the gate before the suite, as the drift
check does. A row with no `file`, `find` or `replace` as strings is refused too. Nothing runs and nothing is written.
"""

import argparse
import json
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

from spark.core.outcomes import EXIT_FOR, EXIT_OK as EXIT_OK, EXIT_PROBLEMS as EXIT_PROBLEMS, EXIT_COULD_NOT_RUN, status_of  # noqa: E402
from suite_runs import GATE_ARCHIVE, GATE_TREE, SLOW_PREFIX  # noqa: E402
import story_tests  # noqa: E402  (beside this file)
import mutate  # noqa: E402  (beside this file, P897) the rows' own anchor and compile checks
from suite_lines import TEST_NAMED, red_tests  # noqa: E402  (beside this file, P797)

#: How many of the names left behind the gate's line shows; the count says the rest.
NAMES_SHOWN = 3
#: How many red tests a red push names, each with its error lines; a line counts the rest (P797).
RED_TESTS_SHOWN = 5

#: The word for the run of every test; story_tests holds the other two.
RUN_FULL = "full"
#: The test module that runs the page script's own tests with node (P829): it skips without node, and a skip is no pass.
NODE_TEST = "test_flow_script"
NO_NODE_LINE = "could not run: the story run holds %s, which runs the page script with node, and node is not installed"


def needs_node(story):
    """True when `story` is a story run that holds NODE_TEST: then the gate needs node."""
    return story is not None and NODE_TEST in story.modules


def node_refusal(story, which=shutil.which):
    """The line that stops the gate when `story` needs node and `which` (a test's swap) finds none, else None."""
    if needs_node(story) and which("node") is None:
        return NO_NODE_LINE % NODE_TEST
    return None


#: The pinned major.minor of tsc, TypeScript's compiler, that compiles the page script (P1061, D29).
TSC_VERSION = "7.0"
#: The page script's folder, from the root; `tsc -p` reads its tsconfig.json.
SCRIPT_FOLDER = "scripts/spark/flow"
#: The four files, from the root, whose change runs the page script's drift check: the source first.
SCRIPT_SOURCES = tuple(SCRIPT_FOLDER + "/" + name
                       for name in ("page_script.ts", "page_script.js", "tsconfig.json", "artifact_runtime.d.ts"))
TSC_REFUSAL = ("could not run: the gate compiles the page script's TypeScript with tsc %s (P1061), and %s; install %s "
               "for the node this PATH finds: npm install -g typescript@%s")
#: How many of tsc's error lines a drift line quotes.
TSC_LINES_SHOWN = 1


def needs_tsc(tree, changed, full=False):
    """
    True when the archived `tree` holds the page script's source, and `full` asks for every check, or `changed` (None
    when git could not tell: a doubt runs more) holds one of SCRIPT_SOURCES. A tree with none of the four, a test's or
    one from before P1061, has nothing to compile. A tree whose `changed` deleted the source while another of the four
    stays still needs tsc, so that a deletion never turns the check off (the review of #1606).
    """
    named = changed is not None and any(name in SCRIPT_SOURCES for name in changed)
    if not (tree / SCRIPT_SOURCES[0]).is_file():
        return named and any((tree / name).is_file() for name in SCRIPT_SOURCES[1:])
    return full or changed is None or named


#: The mutation tables, from the root (P897).
MUTATION_TABLES = "tests/mutations"
#: The files whose mutants `mutate.unloadable` compiles or parses; a .ts, .js or .md row is only anchored.
COMPILED = (".py", ".json")
ROWS_FIX = "  rows: re-anchor each refused row, or remove it with its reason (docs/guide/developing.md)"


def refused_rows(tree, changed):
    """
    The `[refused]` lines of the mutation rows in `tree` (P897), [] when none, and how many rows and tables were read:
    (lines, rows, tables, compiled): `compiled` counts the .py and .json rows that were checked. Every row whose `find` does not occur once in its file is refused, and so is each
    row of a file or table in `changed` whose mutant does not compile or parse (every row when `changed` is None: the
    full run, or git could not tell). It runs nothing and writes nothing.
    """
    lines, rows, tables = [], [], sorted((tree / MUTATION_TABLES).glob("*.json"))
    for table in tables:
        try:
            loaded = json.loads(table.read_text())
            if not isinstance(loaded, list):
                raise TypeError("the table is not a list")
        except (OSError, ValueError, TypeError) as broken:
            lines.append("%s/%s: not a list of rows: %s" % (MUTATION_TABLES, table.name, broken))
            continue
        for index, row in enumerate(loaded):
            where = "%s[%d]" % (table.name, index)
            if not isinstance(row, dict) or not all(isinstance(row.get(key), str) for key in ("file", "find", "replace")):
                lines.append("%s: a row needs `file`, `find` and `replace`, each a string" % where)
            else:
                rows.append(dict(row, table=table.name, index=index, name="%s %s" % (where, row.get("name", row["find"]))))
    wrong = mutate.anchors(tree, rows)
    lines += ["%s: `find` occurs %d time(s) in %s" % (name, count, file) for name, file, count in wrong]
    if changed is None:
        subset = rows
    else:
        named = {Path(name).name for name in changed if name.startswith(MUTATION_TABLES + "/")}
        subset = [row for row in rows if row["table"] in named]
        subset += [row for row in mutate.related(rows, changed) if row not in subset]
    lines += ["%s: %s" % (name, why) for name, _file, why in mutate.unloadable(tree, subset)]
    return lines, len(rows), len(tables), len([row for row in subset if row["file"].endswith(COMPILED)])


def tsc_refusal(which=shutil.which, run=subprocess.run):
    """The could-not-run line for a tsc that `which` does not find, or whose `--version` is not TSC_VERSION; else None."""
    found = which("tsc")
    if found is None:
        return TSC_REFUSAL % (TSC_VERSION, "no tsc is on this PATH", "it", TSC_VERSION)
    said = run([found, "--version"], capture_output=True, text=True).stdout.strip()
    if not said.startswith("Version %s." % TSC_VERSION):
        return TSC_REFUSAL % (TSC_VERSION, "the tsc on this PATH says %r" % said, TSC_VERSION, TSC_VERSION)
    return None


def script_drift(tree, tsc, run=subprocess.run):
    """
    The problems line when `tsc` (the path `which` found), compiling `tree`'s page script into a temporary folder, says
    errors, or writes other bytes than the committed page_script.js; else None. The folder goes, whatever tsc did.
    """
    committed = tree / SCRIPT_SOURCES[1]
    with tempfile.TemporaryDirectory(prefix="spark-tsc-") as out:
        compiled = run([tsc, "-p", SCRIPT_FOLDER, "--outDir", out], cwd=str(tree), capture_output=True, text=True)
        if compiled.returncode != 0:
            first = (compiled.stdout + compiled.stderr).strip().splitlines()[:TSC_LINES_SHOWN]
            return ("page script: tsc -p %s says %s (P1061); fix the .ts, then run it again and commit both files"
                    % (SCRIPT_FOLDER, " ".join(first) or "nothing, and exits %d" % compiled.returncode))
        output = Path(out) / committed.name
        if not output.is_file() or not committed.is_file() or output.read_bytes() != committed.read_bytes():
            return ("page script: the committed %s is not tsc's compiled output of %s (P1061); fix it with tsc -p %s, "
                    "then commit both files" % (SCRIPT_SOURCES[1], Path(SCRIPT_SOURCES[0]).name, SCRIPT_FOLDER))
    return None


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
    """The code lines of `scripts/**/*.py` at a commit, less the MicroPython stand-in, read from git with no checkout;
    None for an unknown commit."""
    listed = subprocess.run(["git", "-C", str(root), "ls-tree", "-r", "--name-only", rev, "scripts/"],
                            capture_output=True, text=True)
    if listed.returncode != 0:
        return None
    return sum(code_lines(subprocess.run(["git", "-C", str(root), "show", "%s:%s" % (rev, name)],
                                         capture_output=True, text=True).stdout)
               for name in listed.stdout.split() if name.endswith(".py") and "stand_in" not in name.split("/"))


def merge_base(root, commit, base):
    """The commit where `commit` left `base`; None when git cannot tell."""
    found = subprocess.run(["git", "-C", str(root), "merge-base", commit, base], capture_output=True, text=True)
    return found.stdout.strip() if found.returncode == 0 else None


def changed_files(root, commit, base="origin/main"):
    """The names of the files that `commit` changed since it left `base`, a deleted one too; None when git cannot tell."""
    since = merge_base(root, commit, base)
    if since is None:
        return None
    listed = subprocess.run(["git", "-C", str(root), "diff", "--no-renames", "--name-only", since, commit],
                            capture_output=True, text=True)
    return listed.stdout.splitlines() if listed.returncode == 0 else None


def story_texts(tree):
    """
    What `story_tests.select` reads of the archived `tree`: the texts of tests/test_*.py and tests/golden_*.py by stem,
    and of scripts/ by the path from the tree's root (P1017).
    """
    def texts(folder, pattern, key=lambda found: found.stem):
        return {key(found): found.read_text(errors="replace") for found in (tree / folder).glob(pattern)}
    return (texts("tests", "test_*.py"), texts("tests", "golden_*.py"),
            texts("scripts", "**/*.py", key=lambda found: found.relative_to(tree).as_posix()))


def story_tests_in(tree, changed):
    """The StoryTests for the files `changed`, from the tests and scripts of the archived `tree`."""
    return story_tests.select(changed, *story_texts(tree))


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
    since = merge_base(root, commit, base)
    then = None if since is None else scripts_size(root, since)
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


def red_shown(red):
    """The red lines the gate prints: those of the first RED_TESTS_SHOWN red tests, then one line that counts the rest."""
    starts = [at for at, line in enumerate(red) if line.startswith(TEST_NAMED)]
    if len(starts) <= RED_TESTS_SHOWN:
        return list(red)
    rest = len(starts) - RED_TESTS_SHOWN
    return list(red[:starts[RED_TESTS_SHOWN]]) + ["… and {:,} more red {}".format(rest, "test" if rest == 1 else "tests")]


def suite_line(said, run, slow_skipped, scope=None):
    """
    The suite's verdict line from the lines the runner said: "quick run: Ran N of M tests in S s (K slow tests skipped;
    the full run is check_commit.py --full) / OK", "full run: Ran M tests in S s / OK", or, with the `scope` that says how much
    was chosen, "story run: Ran N tests in S s (K slow tests skipped; <scope>; the full run is check_commit.py --full) / OK".
    The quick and story lines are built so that they cannot be quoted as the suite's count: they name what they left out.
    """
    ran = next((re.match(r"Ran (\d+) tests? in ([\d.]+)s", line) for line in said if line.startswith("Ran ")), None)
    verdict = [line for line in said if not line.startswith("Ran ")]
    if ran is None:
        return " / ".join([run + " run"] + said)
    total, seconds = int(ran.group(1)), float(ran.group(2))
    if run == story_tests.RUN_STORY:
        counted = "Ran {:,} tests in {:.1f} s ({:,} slow {} skipped; {}; the full run is check_commit.py --full)".format(
            total - slow_skipped, seconds, slow_skipped, "test" if slow_skipped == 1 else "tests", scope)
        return " / ".join([run + " run: " + counted] + verdict)
    if run == story_tests.RUN_QUICK:
        counted = "Ran {:,} of {:,} tests in {:.1f} s ({:,} slow {} skipped; the full run is check_commit.py --full)".format(
            total - slow_skipped, total, seconds, slow_skipped, "test" if slow_skipped == 1 else "tests")
        return " / ".join(["quick run: " + counted] + verdict)
    return " / ".join(["full run: Ran {:,} tests in {:.1f} s".format(total, seconds)] + verdict)


def measure(tree, full=False, story=None):
    """
    (suite verdict line, ok, left, red) for the tree at `tree`. `left` is what the suite left in
    the empty temp folder it was given (P172), None when that could not be listed; the folder goes once counted.
    `red` are the lines that name each red test and its error (P797), empty when the run is green.
    The quick run (P425) sets SPARK_SUITE=quick, so the tests marked slow skip; `full` runs every test.
    A `story` in the state CHOSEN runs only its modules (P714), as a quick run does; any other runs the whole suite.
    """
    run = RUN_FULL if full else story.run_word() if story else story_tests.RUN_QUICK
    what = ["tests.%s" % module for module in story.modules] if run == story_tests.RUN_STORY else ["discover", "-s", "tests"]
    scope = None if story is None else story.scope()
    lend_node_modules(tree)
    temp = tempfile.mkdtemp(prefix="spark-commit-temp-")
    try:
        env = {name: value for name, value in without_git_variables().items() if name != "SPARK_SUITE"}
        env.update({"TMPDIR": temp, GATE_TREE: GATE_ARCHIVE})
        if not full:
            env["SPARK_SUITE"] = "quick"
        suite = subprocess.run([sys.executable, "-m", "unittest"] + what + ([] if full else ["-v"]),
                               cwd=str(tree), capture_output=True, text=True, env=env)
        left = leftovers(temp)
    finally:
        shutil.rmtree(temp, ignore_errors=True)  # a plain rmtree: it never chmods and never follows a link
    suite_said = [line for line in (suite.stderr + suite.stdout).splitlines() if line.startswith(("Ran ", "OK", "FAILED"))]
    last_line_said = (suite.stderr + suite.stdout).splitlines()[-1:]  # a test module that cannot compile stops the runner before any verdict
    # The verdict's own `skipped=N` caps the count: a failure's traceback can embed a child's -v lines.
    skipped_in_all = sum(int(count) for line in suite_said for count in re.findall(r"skipped=(\d+)", line))
    slow_skipped = min(skipped_in_all, sum(1 for line in suite.stderr.splitlines() if " ... skipped '%s" % SLOW_PREFIX in line))
    # The mutation rows' anchors are checked before the suite, in `gate` (`refused_rows`, P897), not here: this only runs tests.
    ok = suite.returncode == 0
    return suite_line(suite_said or last_line_said, run, slow_skipped, scope), ok, left, [] if ok else red_tests(suite.stderr + suite.stdout)


def main(argv=None):
    parser = argparse.ArgumentParser(description="The mutation rows' anchors, then the suite on the tree as committed: the story run by default.")
    parser.add_argument("commit", nargs="?", default="HEAD", help="the commit to measure (default HEAD)")
    parser.add_argument("--full", action="store_true",
                        help="the full run: every test, the slow ones too; a sweep at the end of a wave or an epic, or when the PO asks")
    given = parser.parse_args(sys.argv[1:] if argv is None else argv)
    scratch = Path(tempfile.mkdtemp(prefix="spark-commit-"))
    try:
        return gate(ROOT, given.commit, scratch, given.full)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)  # the archive, 6.2 MB a push (P172); a link in it is unlinked, never followed


def gate(root, commit, scratch, full=False, which=shutil.which, run=subprocess.run):
    """Archive `commit` into `scratch`, check the page script, measure it, say the lines; the exit code. `which` and
    `run` find and run node and tsc (a test's swaps)."""
    began = time.monotonic()
    try:
        archive(root, commit, scratch)
    except (ValueError, subprocess.CalledProcessError) as broken:
        print("could not archive %s: %s" % (commit, broken), file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    changed = None if full else changed_files(root, commit)
    story = None if full else story_tests_in(scratch, changed)
    compiles = needs_tsc(scratch, changed, full)
    refused = node_refusal(story, which) or (compiles and tsc_refusal(which, run))
    if refused:
        print(refused)
        return EXIT_COULD_NOT_RUN
    drift = compiles and script_drift(scratch, which("tsc"), run)
    if drift:
        print(drift)
        return EXIT_PROBLEMS
    stale, row_count, table_count, compiled = refused_rows(scratch, changed)
    if stale:
        for line in stale:
            print("  [refused] " + line)
        print(ROWS_FIX)
        return EXIT_PROBLEMS
    suite, ok, left, red = measure(scratch, full=full, story=story)
    short = subprocess.run(["git", "-C", str(root), "rev-parse", "--short", commit],
                           capture_output=True, text=True).stdout.strip()
    print("%s as committed, %s" % (short, suite))
    for line in red_shown(red):  # a red push names its tests (P797)
        print("    " + line)
    if story is not None and story.state == story_tests.QUICK_RUN:
        print("  no story run: " + story.why)
    if left != []:
        print("  " + temp_line(left))
    print("  " + size_line(root, commit))
    if table_count:
        print("  rows: every anchor of %d rows in %d tables occurs once, and the mutants of the %d rows checked compile"
              % (row_count, table_count, compiled))
    if compiles:
        print("  page script: the committed %s is tsc %s's compiled output of %s (P1061)"
              % (Path(SCRIPT_SOURCES[1]).name, TSC_VERSION, Path(SCRIPT_SOURCES[0]).name))
    sys.path.insert(0, str(ROOT / "tools"))
    import check_backlog
    backlog = check_backlog.main()
    if not full:
        print("  {} run: the seconds above are the tests alone; the board check and the size line come on top, "
              "{:.0f} s for the whole gate".format(story.run_word(), time.monotonic() - began))
    return EXIT_FOR[status_of(problems=not ok or backlog != 0 or bool(left), unchecked=left is None)]


if __name__ == "__main__":
    sys.exit(main())
