"""
The bench goldens (P380, #487): what look, deploy, grant --check, live and reach print today, kept in tests/golden/.

A helper module, no tests in it: tests/test_golden_bench.py runs each Case. A Case runs one script as a child process,
in a project built at test time, with the fake esptool, mpremote and serial of tests/fake_modules first on its
PYTHONPATH and its own store in SPARK_HOME. Its stdout is scrubbed of the run's own paths and hashes, then compared
with its golden file. `SPARK_ACCEPT=look python3 -m unittest tests.test_golden_bench` writes look's goldens from
today's output and fails, so that a person reads `git diff tests/golden` before the next run passes.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
from collections import namedtuple
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import run_scenario  # noqa: E402
import sim_project  # noqa: E402

GOLDEN_DIR = ROOT / "tests" / "golden"
FAKE_MODULES = ROOT / "tests" / "fake_modules"
CANNED = ROOT / "tests" / "data" / "board_look"
FAKE_WOKWI_CLI = [sys.executable, str(ROOT / "tests" / "fake_wokwi_cli.py")]
#: How long one child may take, in seconds. A look runs mpremote and esptool, each a child of its own.
RUN_TIMEOUT_S = 60
#: The environment variable that names the op whose goldens a run writes.
ACCEPT_VARIABLE = "SPARK_ACCEPT"
#: Placed in a Case's argv: the token that the look-ok Case printed.
LOOK_TOKEN = "{look-token}"
BOARD_ID = "firebeetle2-esp32s3"

#: Value. One golden: its name (`<op>-<status>[-<scenario>]`, the extension says which output), the script, its
#: arguments after --project, the canned flash id and device list, and the exit code it must end with.
Case = namedtuple("Case", "golden script argv flash_id devs exit_code")
CASES = [
    Case("look-ok.json", "look.py", ["--json"], "s3-flash-id-16mb.txt", "mpremote-devs-one.txt", 0),
    Case("look-ok.txt", "look.py", [], "s3-flash-id-16mb.txt", "mpremote-devs-one.txt", 0),
    Case("look-problems.json", "look.py", ["--json"], "s3-flash-id-8mb.txt", "mpremote-devs-one.txt", 1),
    Case("look-could-not-run-two-boards.json", "look.py", ["--json"], "s3-flash-id-16mb.txt", "mpremote-devs-two.txt", 2),
    Case("look-could-not-run-no-simulation.json", "look.py", ["--json", "--no-simulation"], "s3-flash-id-16mb.txt",
         "mpremote-devs-one.txt", 2),
    Case("deploy-ok-dry-run.json", "deploy.py", ["--dry-run", "--json"], "s3-flash-id-16mb.txt",
         "mpremote-devs-one.txt", 0),
    Case("deploy-ok-dry-run.txt", "deploy.py", ["--dry-run"], "s3-flash-id-16mb.txt", "mpremote-devs-one.txt", 0),
    Case("deploy-could-not-run-no-terminal.json", "deploy.py", ["--json", "--token", LOOK_TOKEN],
         "s3-flash-id-16mb.txt", "mpremote-devs-one.txt", 2),
    Case("grant-problems-no-grant.json", "grant.py", ["--check", "--json"], "s3-flash-id-16mb.txt",
         "mpremote-devs-one.txt", 1),
    Case("grant-could-not-run-two-boards.json", "grant.py", ["--check", "--json"], "s3-flash-id-16mb.txt",
         "mpremote-devs-two.txt", 2),
    Case("live-problems-refused-no-grant.json", "live.py", ["--code", "print(1)", "--json"], "s3-flash-id-16mb.txt",
         "mpremote-devs-one.txt", 1),
    Case("live-could-not-run-two-boards.json", "live.py", ["--code", "print(1)", "--json"], "s3-flash-id-16mb.txt",
         "mpremote-devs-two.txt", 2),
    Case("reach-ok.json", "reach.py", ["--json"], "s3-flash-id-16mb.txt", "mpremote-devs-one.txt", 0),
]


def op_of(case):
    """The op a Case belongs to: the first word of its golden's name, such as `look`."""
    return case.golden.split("-")[0]


def build_project(folder):
    """The project the goldens run in, built in `folder` as tests/test_deploy.py's ProjectCase builds it: the S3 board,
    firmware that prints ready, and one passed run with its image. The image is made the newest file, so that no note
    says the firmware changed after it. Returns the project's Path."""
    project = Path(folder) / "bench s3"
    sim = project / "sim"
    (sim / "scenarios").mkdir(parents=True)
    (sim / "diagram.json").write_text("{}")
    (sim / "wokwi.toml").write_text(sim_project.wokwi_toml([]))
    (project / "firmware").mkdir()
    (project / "firmware" / "main.py").write_text("print('ready')\n")
    (project / "requirements.json").write_text(json.dumps({"board": BOARD_ID, "parts": []}))
    (project / "boards").mkdir()
    (project / "boards" / "active.json").write_text(json.dumps({"board": BOARD_ID}))
    scenario = sim / "scenarios" / "s.scenario.yaml"
    scenario.write_text('name: s\nversion: 1\nsteps:\n  - wait-serial: "LED on"\n')
    micropython = project / "micropython.bin"
    micropython.write_bytes(b"\xe9" + b"\x00" * 999)
    told = {"FAKE_WOKWI_SERIAL": "ready\nLED on\n", "FAKE_WOKWI_EXIT": "0",
            "FAKE_WOKWI_OUT": '[s] Expected text matched: "ready"\n', "FAKE_WOKWI_ERR": ""}
    with mock.patch.dict(os.environ, told):
        run_scenario.ScenarioRun(project, scenario, micropython=micropython).run(FAKE_WOKWI_CLI)
    newest = max(path.stat().st_mtime for path in project.rglob("*") if path.is_file()) + 10
    for image in sim.glob("*.bin"):
        os.utime(image, (newest, newest))
    return project


def run_script(case, project, store, token=None):
    """(exit code, stdout) of `case`'s script run as a child in `project`, with `store` as its SPARK_HOME. stdin is
    closed and stdout is a pipe, so the script sees no terminal. `token` replaces LOOK_TOKEN in the arguments."""
    argv = [token if arg == LOOK_TOKEN else arg for arg in case.argv]
    env = dict(os.environ, PYTHONPATH=str(FAKE_MODULES), SPARK_HOME=str(store), TZ="UTC", PYTHONDONTWRITEBYTECODE="1",
               FAKE_ESPTOOL_FLASH_ID_FILE=str(CANNED / case.flash_id), FAKE_MPREMOTE_DEVS_FILE=str(CANNED / case.devs))
    env.pop(ACCEPT_VARIABLE, None)
    done = subprocess.run([sys.executable, str(ROOT / "scripts" / case.script), "--project", str(project), *argv],
                          cwd=str(project), env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                          timeout=RUN_TIMEOUT_S)
    return done.returncode, done.stdout


def places_of(project, store):
    """What scrub replaces, longest first: each path in its written and its resolved form, the Python, the image's
    hash. The token keeps its MAC half, and its image half follows the installed littlefs, so it is replaced too."""
    places = {}
    for path, name in ((project, "<project>"), (store, "<store>"), (ROOT, "<repo>")):
        places[str(path)] = places[str(Path(path).resolve())] = name
    places[sys.executable] = "<python>"
    for image in Path(project).glob("sim/*.bin"):
        sha = hashlib.sha256(image.read_bytes()).hexdigest()
        places[sha] = "<image-sha256>"
        places["-" + sha[:4]] = "-<image>"
    return dict(sorted(places.items(), key=lambda item: -len(item[0])))


#: reach --json's moment of the run (`reach.py`'s `at`), which no golden can hold.
MOMENT = re.compile(r'"at": "[^"]*"')


def scrub(text, places):
    """`text` with each key of `places` replaced by its placeholder, longest first, and reach's moment by `<at>`."""
    pattern = re.compile("|".join(re.escape(place) for place in places))
    return MOMENT.sub('"at": "<at>"', pattern.sub(lambda found: places[found.group(0)], text))


def check_golden(case, text):
    """None when `text` equals `case`'s golden, else the reason it does not. When ACCEPT_VARIABLE names the case's op,
    the golden is written from `text` and the reason says so, so the run still fails."""
    golden = GOLDEN_DIR / case.golden
    if not text.strip():
        return "%s printed nothing on stdout, and an empty golden guards nothing" % case.golden
    if os.environ.get(ACCEPT_VARIABLE) == op_of(case):
        GOLDEN_DIR.mkdir(exist_ok=True)
        golden.write_text(text)
        return "goldens written for %s: read git diff tests/golden, then run again" % op_of(case)
    if not golden.exists():
        return "%s does not exist: write it with %s=%s" % (golden.name, ACCEPT_VARIABLE, op_of(case))
    return None if golden.read_text() == text else "%s differs from today's output" % golden.name
