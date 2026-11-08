"""
The checks goldens (P687, #925, W6-C1): what check_all.py, check_physics.py, check_footprints.py, compare_design.py,
check_bom.py and check_vendor_pins.py print today, kept in tests/golden-checks/.

A helper module beside golden_firmware.py, no tests in it: tests/test_golden_checks.py runs each Case with
golden_firmware's Case, plant and run_script, in its own copy of one project: the button-light fixture after
init_project.py. `SPARK_ACCEPT=check-all python3 -m unittest tests.test_golden_checks` writes check_all.py's goldens from
today's output and fails, so that a person reads `git diff tests/golden-checks` first.

No child reaches the network. Its PATH is the gh shim's folder alone, so the gh it finds runs tests/fake_gh.py. Its
proxies are a closed port, so store.fetch fails too. It carries no WOKWI_CLI_TOKEN.
"""

import io
import json
import shlex
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden_bench  # noqa: E402
import golden_firmware  # noqa: E402

ROOT = golden_bench.ROOT
GOLDEN_DIR = ROOT / "tests" / "golden-checks"
FIXTURE = ROOT / "tests" / "data" / "breadboard" / "button-light"
SPARK_CACHE = ROOT / ".spark" / "cache"
FAKE_GH_HEADER = SPARK_CACHE / "dfrobot_firebeetle2_esp32s3.pins_arduino.h"
#: A port nothing listens on: every child's proxy, so a URL a script opens fails at once.
CLOSED_PROXY = "http://127.0.0.1:9"
PROXIES = ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY")
GH_SHIM = """#!/bin/sh
# The golden net's gh (P687): the fake, by an absolute path, so a child never runs the real one.
exec %s "$@"
"""
BOARD_ID = "firebeetle2-esp32s3"
CIRCUIT = "dist/board/circuit.json"
#: The project's rules with `pulled_by_firmware` empty, so the button's input floats.
FLOATING_RULES = "floating-rules.json"
#: The library's board file copied into the project, so a live check keeps its header in the project's cache.
BOARD_FILE = "boards/%s.json" % BOARD_ID
OWN_BOARD = ((BOARD_FILE, (ROOT / BOARD_FILE).read_text()),)
NO_RULES = ((".spark/rules.json", None),)
PROJECT = golden_firmware.PROJECT


def zipped(name, text):
    """The bytes of a zip that holds one file, `name`, with `text`."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(name, text)
    return buffer.getvalue()


def fab_package(*rows):
    """The bytes of a fab package whose bom.csv holds `rows`, in check_bom.py's columns."""
    return zipped("bom.csv", "Designator,Comment,Value,Footprint,JLCPCB Part #\n" + "".join(r + "\n" for r in rows))


#: A fab package with no bom.csv (P688's item 3): a sentence and exit 2, not a SystemExit.
NO_BOM = (("fab-gerbers.zip", zipped("board.gtl", "G04 copper*\n")),)


Case = golden_firmware.Case
CASES = [
    Case("check-all-ok.txt", "check_all.py", ["--project", PROJECT], 0, NO_RULES),
    Case("check-all-problems-floating-input.json", "check_all.py",
         ["--project", PROJECT, "--rules", FLOATING_RULES, "--json"], 1),
    Case("check-all-could-not-run.txt", "check_all.py", ["--project", PROJECT], 2),
    Case("check-physics-could-not-run.txt", "check_physics.py", [CIRCUIT], 2),
    Case("check-physics-could-not-run-no-rules.json", "check_physics.py", [CIRCUIT, "--json"], 2, NO_RULES),
    Case("check-footprints-ok.json", "check_footprints.py", [CIRCUIT, "--json"], 0),
    Case("check-footprints-could-not-run-no-circuit.txt", "check_footprints.py", ["dist/board/missing.json"], 2),
    Case("compare-design-ok.json", "compare_design.py", [CIRCUIT, "--json"], 0),
    Case("compare-design-problems-floating-input.txt", "compare_design.py", [CIRCUIT, "--rules", FLOATING_RULES], 1),
    Case("compare-design-could-not-run-no-rules.txt", "compare_design.py", [CIRCUIT], 2, NO_RULES),
    Case("check-bom-ok.txt", "check_bom.py", ["fab-gerbers.zip"], 0,
         (("fab-gerbers.zip", fab_package("R1,220,220,0603,C25804")),)),
    Case("check-bom-problems-no-supplier-part.txt", "check_bom.py", ["fab-gerbers.zip"], 1,
         (("fab-gerbers.zip", fab_package("R1,220,220,0603,")),)),
    Case("check-bom-could-not-run-no-package.txt", "check_bom.py", ["fab-gerbers.zip"], 2),
    Case("check-bom-could-not-run-no-bom.txt", "check_bom.py", ["fab-gerbers.zip"], 2, NO_BOM),
    Case("check-all-could-not-run-no-bom.txt", "check_all.py", ["--project", PROJECT], 2, NO_BOM),
    Case("check-vendor-pins-ok-offline.txt", "check_vendor_pins.py", ["--offline", BOARD_FILE], 0, OWN_BOARD),
    Case("check-vendor-pins-ok-live.json", "check_vendor_pins.py", [BOARD_FILE, "--json"], 0, OWN_BOARD),
    Case("check-vendor-pins-problems-mismatch.txt", "check_vendor_pins.py", [BOARD_FILE], 1, OWN_BOARD,
         {"FAKE_GH_FIND": "A0 = 4;", "FAKE_GH_REPLACE": "A0 = 5;"}),
    Case("check-vendor-pins-could-not-run-fetch-failed.txt", "check_vendor_pins.py", [BOARD_FILE], 2, OWN_BOARD,
         {"FAKE_GH_EXIT": "1"}),
]


def name_the_gh(folder):
    """Write the gh shim into a `bin` folder in `folder`, which runs tests/fake_gh.py with this Python. Returns the
    `bin` folder, a child's whole PATH."""
    shim_folder = Path(folder) / "bin"
    shim_folder.mkdir(exist_ok=True)
    fake = " ".join(shlex.quote(part) for part in (sys.executable, str(ROOT / "tests" / "fake_gh.py")))
    (shim_folder / "gh").write_text(GH_SHIM % fake)
    (shim_folder / "gh").chmod(0o755)
    return shim_folder


def child_env(store, shim_folder):
    """The bench's child environment with `store` as SPARK_HOME, `shim_folder` as the whole PATH, every proxy a closed
    port, no Wokwi token, and an empty HOME beside the store: a tools list's `~/...` place (wokwi-cli's `also`, which
    `sim_project.find_wokwi_cli` reads with no project) finds no real tool there (P699)."""
    env = golden_bench.child_env(store, "s3-flash-id-16mb.txt", "mpremote-devs-one.txt")
    for name in ("WOKWI_CLI_TOKEN", "no_proxy", "NO_PROXY"):
        env.pop(name, None)
    home = Path(store).parent / "home"
    home.mkdir(parents=True, exist_ok=True)
    env.update(dict.fromkeys(PROXIES, CLOSED_PROXY), PATH=str(shim_folder), HOME=str(home))
    return env


def build_project(folder, shim_folder):
    """The project the goldens run in: the button-light fixture, set up by init_project.py as a child with its own
    store, and FLOATING_RULES beside its rules. Returns the project's Path."""
    project = Path(folder) / "button light"
    shutil.copytree(FIXTURE, project)
    done = subprocess.run([sys.executable, str(ROOT / "scripts" / "init_project.py"), "--project", str(project),
                           "--board", BOARD_ID, "--circuit", str(project / CIRCUIT)], cwd=str(project),
                          env=child_env(Path(folder) / "init-store", shim_folder), stdin=subprocess.DEVNULL,
                          capture_output=True, text=True, timeout=golden_bench.RUN_TIMEOUT_S)
    if done.returncode != 0:
        raise RuntimeError("init_project.py failed: %s%s" % (done.stdout, done.stderr))
    rules = json.loads((project / ".spark" / "rules.json").read_text())
    rules["pulled_by_firmware"] = []
    (project / FLOATING_RULES).write_text(json.dumps(rules, indent=2))
    return project
