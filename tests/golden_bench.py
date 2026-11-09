"""
The bench goldens (P380, #487): what look, deploy, grant --check, live and reach print today, kept in tests/golden/.

A helper module, no tests in it: tests/test_golden_bench.py runs each Case. A Case runs one script as a child process,
in a project built at test time, with the fake esptool, mpremote and serial of tests/fake_modules first on its
PYTHONPATH and its own store in SPARK_HOME. Its stdout is scrubbed of the run's own paths and hashes, then compared
with its golden file. `SPARK_ACCEPT=look python3 -m unittest tests.test_golden_bench` writes look's goldens from
today's output and fails, so that a person reads `git diff tests/golden` before the next run passes.
"""

import datetime
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
sys.path.insert(0, str(ROOT / "tests"))

from spark.bench import board_look  # noqa: E402
from spark.records import board_records  # noqa: E402
from spark.firmware import scenario_run  # noqa: E402
from spark.firmware import sim_project  # noqa: E402
from micropython_fakes import fake_interpreter  # noqa: E402

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
#: arguments after --project, the files of the canned flash id and device list, the exit code it must end with,
#: `plant`: (path under the store, text) pairs written into the run's store first (a text may be a callable that gives
#: it at run time, for a time that moves), `stderr_golden`: the name of the golden of the run's stderr, or None, and
#: `fake_board`: True when the run flashes a board that the fakes keep in a folder (tests/fake_modules, FAKE_BOARD).
Case = namedtuple("Case", "golden script argv flash_id_file devs_file exit_code plant stderr_golden fake_board",
                  defaults=((), None, False))
#: A store record of the canned board's last deploy that cannot be read (P416).
UNREADABLE_LAST_DEPLOY = (("boards/dc-da-0c-xx-xx-xx.json", "{not json"),)
#: The canned board's address, masked as every tracked file holds one (P505).
BOARD_MAC = "dc:da:0c:xx:xx:xx"
#: The USB serial of the canned device list: a live grant is found by it, a deploy grant by BOARD_MAC (P242).
SERIAL_MAC = "8c:bf:ea:xx:xx:xx"
GRANT_MINUTES = 60


def grant_text(mac, scope):
    """The text of a grant of `scope` for the board `mac`, given one minute ago, valid for GRANT_MINUTES. Made at run time,
    because a grant holds only for a time that moves."""
    now = datetime.datetime.now().astimezone().replace(microsecond=0)
    return json.dumps({"mac": mac, "board_token": board_look.board_token(mac), "granted_by": "tester",
                       "granted_at": (now - datetime.timedelta(minutes=1)).isoformat(),
                       "expires_at": (now + datetime.timedelta(minutes=GRANT_MINUTES)).isoformat(), "scope": scope})


def deploy_grant_text():
    """A deploy grant for the canned board: it takes deploy.py past the gate with a standing yes."""
    return grant_text(BOARD_MAC, "deploy")


def live_grant_text():
    """A live grant for the canned device list's board: it takes live.py past the grant check, and grant.py --check finds it."""
    return grant_text(SERIAL_MAC, "live")


#: A deploy grant in the store: deploy.py passes the gate, runs the erase, which the fake esptool fails with its retry
#: exit code, waits 5 s (the flasher's real wait), and ends with the flash failure.
DEPLOY_GRANT = (("grants/dc-da-0c-xx-xx-xx-deploy.json", deploy_grant_text),)
#: A live grant in the store, found by the serial of the canned device list.
LIVE_GRANT = (("grants/8c-bf-ea-xx-xx-xx.json", live_grant_text),)
CASES = [
    Case("look-ok.json", "look.py", ["--json"], "s3-flash-id-16mb.txt", "mpremote-devs-one.txt", 0),
    Case("look-ok.txt", "look.py", [], "s3-flash-id-16mb.txt", "mpremote-devs-one.txt", 0),
    Case("look-problems.json", "look.py", ["--json"], "s3-flash-id-8mb.txt", "mpremote-devs-one.txt", 1),
    Case("look-could-not-run-two-boards.json", "look.py", ["--json"], "s3-flash-id-16mb.txt", "mpremote-devs-two.txt", 2),
    Case("look-ok-one-board-two-ports.json", "look.py", ["--json"], "s3-flash-id-16mb.txt",
         "mpremote-devs-one-board-two-ports.txt", 0),
    Case("look-could-not-run-last-deploy-not-checked.json", "look.py", ["--json"], "s3-flash-id-16mb.txt",
         "mpremote-devs-one.txt", 2, UNREADABLE_LAST_DEPLOY),
    Case("look-could-not-run-no-simulation.json", "look.py", ["--json", "--no-simulation"], "s3-flash-id-16mb.txt",
         "mpremote-devs-one.txt", 2),
    Case("look-could-not-run-bad-argument.json", "look.py", ["--json", "--no-simulation", "--ignore-older-runs"],
         "s3-flash-id-16mb.txt", "mpremote-devs-one.txt", 2),
    Case("deploy-ok-dry-run.json", "deploy.py", ["--dry-run", "--json"], "s3-flash-id-16mb.txt",
         "mpremote-devs-one.txt", 0),
    Case("deploy-ok-dry-run.txt", "deploy.py", ["--dry-run"], "s3-flash-id-16mb.txt", "mpremote-devs-one.txt", 0),
    Case("deploy-could-not-run-no-terminal.json", "deploy.py", ["--json", "--token", LOOK_TOKEN],
         "s3-flash-id-16mb.txt", "mpremote-devs-one.txt", 2, (), "deploy-could-not-run-no-terminal.json.stderr"),
    Case("deploy-could-not-run-flash-failed-grant.json", "deploy.py", ["--json", "--token", LOOK_TOKEN],
         "s3-flash-id-16mb.txt", "mpremote-devs-one.txt", 2, DEPLOY_GRANT,
         "deploy-could-not-run-flash-failed-grant.json.stderr"),
    Case("deploy-could-not-run-flash-failed-grant.txt", "deploy.py", ["--token", LOOK_TOKEN], "s3-flash-id-16mb.txt",
         "mpremote-devs-one.txt", 2, DEPLOY_GRANT, "deploy-could-not-run-flash-failed-grant.txt.stderr"),
    Case("grant-problems-no-grant.json", "grant.py", ["--check", "--json"], "s3-flash-id-16mb.txt",
         "mpremote-devs-one.txt", 1),
    Case("grant-could-not-run-two-boards.json", "grant.py", ["--check", "--json"], "s3-flash-id-16mb.txt",
         "mpremote-devs-two.txt", 2),
    Case("live-problems-refused-no-grant.json", "live.py", ["--code", "print(1)", "--json"], "s3-flash-id-16mb.txt",
         "mpremote-devs-one.txt", 1),
    Case("live-could-not-run-two-boards.json", "live.py", ["--code", "print(1)", "--json"], "s3-flash-id-16mb.txt",
         "mpremote-devs-two.txt", 2),
    Case("reach-ok.json", "reach.py", ["--json"], "s3-flash-id-16mb.txt", "mpremote-devs-one.txt", 0),
    # P383: the three goldens of the happy paths, on a board the fakes keep
    Case("grant-ok-granted.json", "grant.py", ["--check", "--json"], "s3-flash-id-16mb.txt", "mpremote-devs-one.txt", 0, LIVE_GRANT),
    Case("live-ok-ran.json", "live.py", ["--code", 'print("reached")', "--json"], "s3-flash-id-16mb.txt", "mpremote-devs-one.txt", 0,
         LIVE_GRANT),
    Case("deploy-ok-ready-seen.json", "deploy.py", ["--json", "--token", LOOK_TOKEN], "s3-flash-id-16mb.txt", "mpremote-devs-one.txt", 0,
         DEPLOY_GRANT, "deploy-ok-ready-seen.json.stderr", True),
]


def op_of(case):
    """The op a Case belongs to: its script's name with dashes, such as `look` or `run-scenario` (P683). A golden's name
    starts with its op."""
    return Path(case.script).stem.replace("_", "-")


def build_project(folder):
    """The project the goldens run in, built in `folder` as tests/test_deploy.py's ProjectCase builds it: the S3 board,
    firmware that prints ready, and one passed run with its image. The image is made the newest file, so that no note
    says the firmware changed after it. Returns the project's Path."""
    project = Path(folder) / "bench s3"
    sim = project / "sim"
    (sim / "scenarios").mkdir(parents=True)
    (sim / "diagram.json").write_text('{"parts": []}')
    (sim / "wokwi.toml").write_text(sim_project.wokwi_toml([]))
    (project / "firmware").mkdir()
    (project / "firmware" / "main.py").write_text("print('ready')\n")
    (project / "requirements.json").write_text(json.dumps({"board": BOARD_ID, "parts": []}))
    (project / "boards").mkdir()
    (project / "boards" / "active.json").write_text(json.dumps({"board": BOARD_ID}))
    # The fixture invents this note: the firebeetle S3 board has no display. It makes the run copy a limits section into the log (P345).
    (sim / "WHAT-THIS-CANNOT-SHOW.md").write_text(sim_project.limits_note(
        [("ONBOARD_DISPLAY", board_records.ONBOARD_ROLES[board_records.ONBOARD_DISPLAY].not_in_diagram)]))
    scenario = sim / "scenarios" / "s.scenario.yaml"
    scenario.write_text('name: s\nversion: 1\nsteps:\n  - wait-serial: "LED on"\n')
    micropython = project / "micropython.bin"
    micropython.write_bytes(fake_interpreter())
    told = {"FAKE_WOKWI_SERIAL": "ready\nLED on\n", "FAKE_WOKWI_EXIT": "0",
            "FAKE_WOKWI_OUT": '[s] Expected text matched: "ready"\n', "FAKE_WOKWI_ERR": ""}
    with mock.patch.dict(os.environ, told):
        scenario_run.ScenarioRun(project, scenario, micropython=micropython).run(FAKE_WOKWI_CLI)
    newest = max(path.stat().st_mtime for path in project.rglob("*") if path.is_file()) + 10
    for image in sim.glob("*.bin"):
        os.utime(image, (newest, newest))
    return project


#: The name of a variable that holds a secret of the parent's (WOKWI_CLI_TOKEN, GH_TOKEN, AWS_SECRET_ACCESS_KEY, an API
#: key, a password), which no child carries: a net that needs a token gives its child a fake one (P699, P715).
SECRET_NAME = re.compile(r"TOKEN|SECRET|PASSWORD|API_?KEY|(?:^|_)KEY(?:_|$)")


def child_env(store, flash_id_file, devs_file):
    """The environment of a child: the parent's without SPARK_* (ACCEPT_VARIABLE too) and without a secret, then the fakes
    first on PYTHONPATH, `store` as SPARK_HOME, and the canned flash id and device list. HOME stays the parent's: the
    bench reads esptool's version from the person's own site-packages, under it."""
    env = {name: value for name, value in os.environ.items()
           if not name.startswith("SPARK_") and not SECRET_NAME.search(name.upper())}
    env.update(PYTHONPATH=str(FAKE_MODULES), SPARK_HOME=str(store), TZ="UTC", PYTHONDONTWRITEBYTECODE="1",
               FAKE_ESPTOOL_FLASH_ID_FILE=str(CANNED / flash_id_file), FAKE_MPREMOTE_DEVS_FILE=str(CANNED / devs_file))
    return env


def run_script(case, project, store, token=None):
    """(exit code, stdout, stderr) of `case`'s script run as a child in `project`, with `store` as its SPARK_HOME. stdin is
    closed and stdout is a pipe, so the script sees no terminal. `token` replaces LOOK_TOKEN in the arguments."""
    argv = [token if arg == LOOK_TOKEN else arg for arg in case.argv]
    for place, text in case.plant:
        (Path(store) / place).parent.mkdir(parents=True, exist_ok=True)
        (Path(store) / place).write_text(text() if callable(text) else text)
    env = child_env(store, case.flash_id_file, case.devs_file)
    if case.fake_board:
        env["FAKE_BOARD"] = str(Path(store) / "fake-board")
        (Path(store) / "fake-board").mkdir(parents=True, exist_ok=True)
    done = subprocess.run([sys.executable, str(ROOT / "scripts" / case.script), "--project", str(project), *argv],
                          cwd=str(project), env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                          timeout=RUN_TIMEOUT_S)
    return done.returncode, done.stdout, done.stderr


def tilde_form(path):
    """`path` as Privacy prints it when it sits under the home folder (`~/...`), or None (P677)."""
    try:
        return "~/" + str(Path(path).relative_to(Path.home()))
    except ValueError:
        return None


def replacements_of(project, store):
    """What scrub replaces, longest first: each path in its written and its resolved form, the Python, the image's
    hash. The token keeps its MAC half, and its image half follows the installed littlefs, so it is replaced too.
    Privacy prints the repo and the Python as `~/...` on a machine that keeps them under home, so that form is replaced
    too. The run's own store is `<spark-home>` and its project `<project-dir>`, which only a line a person pastes prints:
    `<store>` and `<project>` are Privacy's own words (P677), so a path that Privacy missed is a golden diff."""
    places = {}
    for path, name in ((project, "<project-dir>"), (store, "<spark-home>"), (ROOT, "<repo>"), (sys.executable, "<python>")):
        for form in (str(path), str(Path(path).resolve())):
            places[form] = name
            if name in ("<repo>", "<python>") and tilde_form(form):
                places[tilde_form(form)] = name
    for image in Path(project).glob("sim/*.bin"):
        sha = hashlib.sha256(image.read_bytes()).hexdigest()
        places[sha] = "<image-sha256>"
        places["-" + sha[:4]] = "-<image>"
    return dict(sorted(places.items(), key=lambda item: -len(item[0])))


#: reach --json's moment of the run (`reach.py`'s `at`), which no golden can hold. Only a moment's shape matches, so a
#: changed value in `at` still fails its golden.
MOMENT = re.compile(r'"at": "\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d{4}"')

#: A clock time with its zone and a colon in the offset, as a grant's `yes:` line and the envelope's `who` print it
#: (P508). The grant is made at run time, so only the shape can match, and a changed shape still fails.
CLOCK = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d")


#: The name of a board log, a moment of the run (sim/runs/board/<moment>.log), which CLOCK does not match (P383).
BOARD_LOG = re.compile(r"\d{4}-\d\d-\d\dT\d\d-\d\d-\d\d\.log")
#: The facts file's sha256 in the deploy's line. The facts hold the moment of the deploy, so the hash moves (P383).
FACTS_SHA = re.compile(r"(spark\.json sha256: )[0-9a-f]{64}")


#: A word in a script's shell quotes that starts with a placeholder. A script quotes a path only when it holds a space,
#: so the quotes go, and a golden reads the same on a machine whose paths have none.
QUOTED_PLACE = re.compile(r"'(<(?:project-dir|spark-home|repo|python)>[^'\s]*(?: [^'\s]+)*)'")


def scrub(text, places):
    """`text` with each key of `places` replaced by its placeholder, longest first, the quotes around a placed path
    dropped, reach's moment replaced by `<at>` and a grant's clock times by `<time>`."""
    pattern = re.compile("|".join(re.escape(place) for place in places))
    placed = QUOTED_PLACE.sub(r"\1", pattern.sub(lambda found: places[found.group(0)], text))
    return FACTS_SHA.sub(r"\1<facts-sha256>", BOARD_LOG.sub("<time>.log", CLOCK.sub("<time>", MOMENT.sub('"at": "<at>"', placed))))


def check_golden(case, text, name=None, golden_dir=GOLDEN_DIR):
    """None when `text` equals `case`'s golden in `golden_dir` (the file `name` names, for its stderr), else the reason
    it does not. When ACCEPT_VARIABLE names the case's op, the golden is written from `text` and the reason says so, so
    the run still fails."""
    name = name or case.golden
    golden = golden_dir / name
    if not text.strip():
        return "%s printed nothing, and an empty golden guards nothing" % name
    if os.environ.get(ACCEPT_VARIABLE) == op_of(case):
        golden_dir.mkdir(exist_ok=True)
        golden.write_text(text)
        return "goldens written for %s: read git diff %s, then run again" % (op_of(case), golden_dir.relative_to(ROOT))
    if not golden.exists():
        return "%s does not exist: write it with %s=%s" % (golden.name, ACCEPT_VARIABLE, op_of(case))
    return None if golden.read_text() == text else "%s differs from today's output" % golden.name
