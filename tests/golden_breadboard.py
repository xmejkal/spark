"""
The breadboard goldens (P686, #924, W6-B1): what breadboard.py prints today, and the files it writes beside the sheet,
kept in tests/golden-breadboard/.

A helper module beside golden_bench.py, no tests in it: tests/test_golden_breadboard.py runs each Case. A Case copies
one fixture of tests/data/breadboard/ under its own name (the sheet's title is the folder's name) and runs
breadboard.py there as a child, with its own empty store. Its stdout, then its stderr after STDERR_MARK, then each file
it wrote beside the sheet after LOG_MARK, are scrubbed of the run's own paths and compared with its golden file.
`SPARK_ACCEPT=breadboard python3 -m unittest tests.test_golden_breadboard` writes the goldens from today's output and
fails, so that a person reads `git diff tests/golden-breadboard` first.

breadboard.py runs no tool and opens no URL, so nothing is faked. The child carries no WOKWI_CLI_TOKEN all the same.
"""

import shutil
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden_bench  # noqa: E402
from golden_firmware import LOG_MARK, STDERR_MARK  # noqa: E402

GOLDEN_DIR = golden_bench.ROOT / "tests" / "golden-breadboard"
DATA = golden_bench.ROOT / "tests" / "data" / "breadboard"
REQUIREMENTS = "requirements.json"
#: What breadboard.py writes beside the sheet, which its stdout already prints.
WRITTEN = ("breadboard.json", "breadboard.svg", "wiring-record.json")

#: Value. One golden: its name (`breadboard-<status>-<scenario>`), the script, the fixture copied, the arguments, the
#: exit code it must end with, `plant`: (path under the project, a file of DATA to copy there, or None to remove it),
#: and `then`: a fixture whose requirements and build replace the project's after a first run, as a rebuild does.
Case = namedtuple("Case", "golden script fixture argv exit_code plant then", defaults=((), None))
CASES = [
    Case("breadboard-ok-xiao.txt", "breadboard.py", "button-light-xiao", [REQUIREMENTS], 0),
    Case("breadboard-ok-firebeetle.txt", "breadboard.py", "button-light", [REQUIREMENTS], 0),
    Case("breadboard-ok-not-drawn.txt", "breadboard.py", "motor", [REQUIREMENTS], 0),
    Case("breadboard-ok-rebuild.txt", "breadboard.py", "button-light-xiao", [REQUIREMENTS], 0, then="button-only-xiao"),
    Case("breadboard-could-not-run-not-built.txt", "breadboard.py", "button-light", [REQUIREMENTS], 2,
         (("dist/board/circuit.json", None),)),
    Case("breadboard-could-not-run-stale.txt", "breadboard.py", "button-light", [REQUIREMENTS], 2,
         ((REQUIREMENTS, "motor/" + REQUIREMENTS),)),
    Case("breadboard-could-not-run-bad-out.txt", "breadboard.py", "button-light", [REQUIREMENTS, "--out", "no/such/x.md"],
         2),
]


def child_env(store):
    """The bench's child environment with `store` as SPARK_HOME, which drops WOKWI_CLI_TOKEN with every secret (P699). The
    canned flash id and device list are the bench's own: breadboard.py never reads them."""
    return golden_bench.child_env(store, "s3-flash-id-16mb.txt", "mpremote-devs-one.txt")


def copy_project(case, folder):
    """`case`'s fixture copied into `folder` under its own name, with its planted files. Returns the project's Path."""
    project = Path(folder) / case.fixture
    shutil.copytree(DATA / case.fixture, project)
    for place, source in case.plant:
        if source is None:
            (project / place).unlink()
        else:
            shutil.copy(DATA / source, project / place)
    return project


def rebuild_as(project, fixture):
    """`project` as if its requirements changed and it was built again: `fixture`'s requirements and build
    (tests/test_breadboard_keep.py's change_requirements)."""
    shutil.copy(DATA / fixture / REQUIREMENTS, project / REQUIREMENTS)
    shutil.rmtree(project / "dist")
    shutil.copytree(DATA / fixture / "dist", project / "dist")


def run_child(case, project, store):
    return subprocess.run([sys.executable, str(golden_bench.ROOT / "scripts" / case.script), *case.argv],
                          cwd=str(project), env=child_env(store), stdin=subprocess.DEVNULL, capture_output=True,
                          text=True, timeout=golden_bench.RUN_TIMEOUT_S)


def run_script(case, project, store):
    """The text of `case`'s script run as a child in `project` with `store` as its SPARK_HOME, and its exit code: stdout,
    then stderr after STDERR_MARK, then each file of WRITTEN after LOG_MARK. A Case with `then` runs twice, and the text
    is the second run's. stdin is closed."""
    Path(store).mkdir(parents=True, exist_ok=True)
    if case.then:
        run_child(case, project, store)
        rebuild_as(project, case.then)
    done = run_child(case, project, store)
    text = done.stdout + (STDERR_MARK + done.stderr if done.stderr else "")
    for name in WRITTEN:
        if (Path(project) / name).is_file():
            text += LOG_MARK % name + (Path(project) / name).read_text()
    return done.returncode, text
