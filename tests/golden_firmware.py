"""
The firmware goldens (P683, #920, W6-F1): what run_scenario.py, flash_image.py and import_firmware.py print today, kept
in tests/golden-firmware/.

A helper module beside golden_bench.py, no tests in it: tests/test_golden_firmware.py runs each Case. A Case runs one
script as a child process in its own copy of the bench's golden project, with its own store. Its stdout, then its
stderr after STDERR_MARK, then a scenario run's log after LOG_MARK, are scrubbed of the run's own paths and times and
compared with its golden file. `SPARK_ACCEPT=run-scenario python3 -m unittest tests.test_golden_firmware` writes
run_scenario.py's goldens from today's output and fails, so that a person reads `git diff tests/golden-firmware` first.

No golden run spends a Wokwi minute (the PO, 2026-10-31). The project's tools list names the shim as wokwi-cli, with no
other place to look, every child carries FAKE_TOKEN, and the shim runs tests/fake_wokwi_cli.py with that token alone.
"""

import json
import shlex
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden_bench  # noqa: E402

GOLDEN_DIR = golden_bench.ROOT / "tests" / "golden-firmware"
#: The token every child carries, so the PO's real WOKWI_CLI_TOKEN never reaches a child.
FAKE_TOKEN = "golden-net-fake-token"
#: The shim's exit code when the token is not FAKE_TOKEN.
REFUSED_EXIT = 97
SHIM = """#!/bin/sh
# The golden net's wokwi-cli (P683): the fake tool, run only with the fake token. Any other token, a real one too, is
# refused here, so the child fails its golden and spends nothing.
if [ "$WOKWI_CLI_TOKEN" != %(token)s ]; then
  echo "wokwi-cli shim: WOKWI_CLI_TOKEN is not the golden net's fake token" >&2
  exit %(refused)d
fi
exec %(fake)s "$@"
"""
#: Placed in a Case's argv: the run's own project.
PROJECT = "{project}"
STDERR_MARK = "--- stderr ---\n"
LOG_MARK = "--- %s ---\n"
SCENARIO = "sim/scenarios/s.scenario.yaml"
#: What the fake tool prints and exits with for a run whose firmware prints ready (golden_bench.build_project's own).
READY_RUN = {"FAKE_WOKWI_SERIAL": "ready\nLED on\n", "FAKE_WOKWI_EXIT": "0",
             "FAKE_WOKWI_OUT": '[s] Expected text matched: "ready"\n', "FAKE_WOKWI_ERR": ""}
#: A run whose firmware never prints ready, so wokwi-cli times out (its exit 42).
NEVER_READY_RUN = {"FAKE_WOKWI_SERIAL": "booting\n", "FAKE_WOKWI_EXIT": "42", "FAKE_WOKWI_OUT": "",
                   "FAKE_WOKWI_ERR": "Error: Timeout"}
#: A firmware module the machine stand-in imports, and one whose import raises.
GOOD_MODULE = ("firmware/led.py", "from machine import Pin\n\nLED = Pin(2, Pin.OUT)\n")
RAISING_MODULE = ("firmware/sensor.py", "import missing_driver\n")

#: Value. One golden: its name (`<op>-<status>[-<scenario>]`, the op is the script's), the script, its arguments
#: (PROJECT is the run's project), the exit code it must end with, `plant`: (path under the project, text) pairs written
#: into the run's project first (None removes the file), and `env`: what the child's environment adds.
Case = namedtuple("Case", "golden script argv exit_code plant env", defaults=((), {}))
CASES = [
    Case("run-scenario-ok.txt", "run_scenario.py", [SCENARIO, "--project", PROJECT, "--micropython", "micropython.bin"], 0,
         env=READY_RUN),
    Case("run-scenario-problems-never-ready.txt", "run_scenario.py",
         [SCENARIO, "--project", PROJECT, "--micropython", "micropython.bin"], 1, env=NEVER_READY_RUN),
    Case("run-scenario-could-not-run-no-token.txt", "run_scenario.py",
         [SCENARIO, "--project", PROJECT, "--micropython", "micropython.bin"], 2, env={"WOKWI_CLI_TOKEN": ""}),
    Case("run-scenario-could-not-run-no-sim.txt", "run_scenario.py",
         [SCENARIO, "--project", PROJECT, "--micropython", "micropython.bin"], 2, (("sim/diagram.json", None),)),
    Case("flash-image-ok.txt", "flash_image.py",
         ["--project", PROJECT, "--micropython", "micropython.bin", "--files", "firmware", "-o", "flash.bin"], 0),
    Case("flash-image-could-not-run-no-interpreter.txt", "flash_image.py",
         ["--project", PROJECT, "--micropython", "missing.bin", "--files", "firmware", "-o", "flash.bin"], 2),
    Case("import-firmware-ok.json", "import_firmware.py", [PROJECT, "--json"], 0, (GOOD_MODULE,)),
    Case("import-firmware-problems.json", "import_firmware.py", [PROJECT, "--json"], 1, (GOOD_MODULE, RAISING_MODULE)),
]


def name_the_shim(project, folder):
    """Write the shim into `folder` and name it as wokwi-cli in `project`'s tools list, with no other place to look
    (`also` empty, no `fetch`), so tools.find finds the shim or nothing. Returns the shim's Path."""
    shim = Path(folder) / "wokwi-cli-shim"
    fake = " ".join(shlex.quote(part) for part in golden_bench.FAKE_WOKWI_CLI)
    shim.write_text(SHIM % {"token": shlex.quote(FAKE_TOKEN), "refused": REFUSED_EXIT, "fake": fake})
    shim.chmod(0o755)
    (Path(project) / ".spark").mkdir(exist_ok=True)
    (Path(project) / ".spark" / "tools.json").write_text(json.dumps(
        {"wokwi-cli": {"kind": "path", "exe": str(shim), "also": [], "fetch": None}}, indent=2))
    return shim


def child_env(store):
    """The bench's child environment with `store` as SPARK_HOME, and FAKE_TOKEN as WOKWI_CLI_TOKEN in place of the
    parent's, which on the PO's machine is a real one."""
    env = golden_bench.child_env(store, "s3-flash-id-16mb.txt", "mpremote-devs-one.txt")
    env["WOKWI_CLI_TOKEN"] = FAKE_TOKEN
    return env


def plant(case, project):
    """Write or remove each of `case`'s planted files in `project`: text as text, bytes as bytes (P687's fab packages), in
    a folder made when it is missing (P699's part records)."""
    for place, text in case.plant:
        if text is None:
            (Path(project) / place).unlink()
            continue
        (Path(project) / place).parent.mkdir(parents=True, exist_ok=True)
        if isinstance(text, bytes):
            (Path(project) / place).write_bytes(text)
        else:
            (Path(project) / place).write_text(text)


def run_script(case, project, store, env=None):
    """The text of `case`'s script run as a child in `project` with `store` as its SPARK_HOME, and its exit code: stdout,
    then stderr after STDERR_MARK, then the log the run wrote after LOG_MARK. stdin is closed. `env` is the child's
    environment before the Case's own (default: child_env, P687 gives the checks' own)."""
    plant(case, project)
    for log in Path(project).glob("sim/runs/*.log"):  # the project's own passed run: only a log this run writes is shown
        log.unlink()
    env = dict(child_env(store) if env is None else env, **case.env)
    argv = [str(project) if arg == PROJECT else arg for arg in case.argv]
    done = subprocess.run([sys.executable, str(golden_bench.ROOT / "scripts" / case.script), *argv], cwd=str(project),
                          env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                          timeout=golden_bench.RUN_TIMEOUT_S)
    text = done.stdout + (STDERR_MARK + done.stderr if done.stderr else "")
    for log in sorted(Path(project).glob("sim/runs/*.log")):
        text += LOG_MARK % log.relative_to(project) + log.read_text()
    return done.returncode, text

