"""
The records-with-sourcing goldens (P715, #966, W6-R1): what parts.py, boards.py, tools.py and cost.py print today, and
what each write Operation writes, kept in tests/golden-records/.

A helper module beside golden_design.py, no tests in it: tests/test_golden_records.py runs each Case with
golden_firmware's run_script, in its own copy of one project (a bare copy of golden_checks' button-light fixture)
and its own store. `SPARK_ACCEPT=parts python3 -m unittest tests.test_golden_records` writes parts.py's goldens from
today's output and fails, so that a person reads `git diff tests/golden-records`.

No golden reaches the network, a vendor site, an installer or a package manager. A child's PATH is the fakes' folder
alone, which holds a fake pdftotext and nothing else, so no curl, claude or install manager of tool_finder.MANAGERS is
found
(GUARDED, and the guard test runs `command -v` for each in a child). Its proxies are a closed port, its HOME an empty
folder, and it carries no secret of the parent (golden_checks.child_env). store.fetch admits `file:` only under
unittest, which a child never imports, so `--sources` and `--fetch` ask a URL at the closed port itself and fail in one
connect. tools.py's `--install` runs with `--dry-run` alone.
"""

import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden_bench  # noqa: E402
import golden_checks  # noqa: E402
import golden_design  # noqa: E402
import golden_firmware  # noqa: E402
from spark.records import tool_finder  # noqa: E402
from fakes import fake_pdftotext  # noqa: E402
from golden_firmware import LOG_MARK  # noqa: E402

ROOT = golden_bench.ROOT
GOLDEN_DIR = ROOT / "tests" / "golden-records"
PROJECT = golden_firmware.PROJECT
#: The programs no child may find: each install manager's program, the downloader and Claude Code's own CLI.
GUARDED = tuple(program for _, program in tool_finder.MANAGERS if program) + ("curl", "claude")
#: The session id every child runs in (the suite's own, store.py's), so `--step` never names the person's session.
SESSION = "spark-suite"
#: A `written` name that starts with STORE is read from the run's store, not its project.
STORE = "{store}/"
#: Python modules a records child finds first: a fake littlefs, so `tools.py --status` reads the same on any machine.
FAKE_MODULES = ROOT / "tests" / "fake_records_modules"
#: The repository's folders a Case could write to (`--promote` of a project's record writes the plugin's parts/).
REPO_FOLDERS = ("parts", "boards", "data")
#: Where `--sources` and `--fetch` look: the closed port itself, so even a child with no proxy reaches nothing.
CLOSED_URL = golden_checks.CLOSED_PROXY + "/datasheet.pdf"
#: The errno of a refused connection differs by platform (61 on macOS, 111 on Linux).
ERRNO = re.compile(r"\[Errno \d+\] Connection refused")
#: The day a document was kept (`--keep`, `--fetch`), which changes from run to run.
DAY = re.compile(r'("retrieved": ?")\d{4}-\d\d-\d\d')


def make_fakes(folder):
    """The fake pdftotext in a `bin` folder in `folder`. Returns the `bin` folder, a child's whole PATH."""
    shims = Path(folder) / "bin"
    shims.mkdir(parents=True, exist_ok=True)
    fake_pdftotext(shims / "pdftotext")
    return shims


def child_env(store, shims):
    """golden_checks' child environment (PATH the fakes' folder alone, proxies closed, empty HOME, no secret) in the
    suite's session, with FAKE_MODULES first on its PYTHONPATH."""
    env = golden_checks.child_env(store, shims)
    return dict(env, PYTHONPATH="%s:%s" % (FAKE_MODULES, env["PYTHONPATH"]), CLAUDE_CODE_SESSION_ID=SESSION)


def repo_files():
    """{path under ROOT: (size, mtime)} of every file in REPO_FOLDERS, so a test can tell that a Case wrote none."""
    return {str(found.relative_to(ROOT)): (found.stat().st_size, found.stat().st_mtime_ns)
            for folder in REPO_FOLDERS for found in (ROOT / folder).rglob("*") if found.is_file()}


#: What a child runs to say which of GUARDED it finds, one path a line.
FIND_GUARDED = 'for name in "$@"; do command -v "$name"; done; exit 0'


def guarded_found(env, names=None):
    """The paths of the programs `names` (default GUARDED) a child with `env` finds: [] when none."""
    import subprocess
    asked = GUARDED if names is None else names
    done = subprocess.run(["/bin/sh", "-c", FIND_GUARDED, "sh", *asked], env=env, stdin=subprocess.DEVNULL,
                          capture_output=True, text=True, timeout=golden_bench.RUN_TIMEOUT_S)
    return done.stdout.split()


def planted(name, value):
    """A (name, text) pair to plant: `value` as indented JSON."""
    return (name, json.dumps(value, indent=2))


BOARD_ID = golden_checks.BOARD_ID
#: The project's own small record, citing a datasheet at the closed port that it keeps no document of.
GOLDEN_LED = {"schema": 1, "id": "golden-led", "name": "golden led", "kind": "indicator", "sources": [CLOSED_URL]}
SMALL_LED = planted("parts/golden-led.json", GOLDEN_LED)
#: The library's LED as the project's own, every URL it cites the closed port: a record that meets the contract.
LOCAL_LED = ("parts/golden-led.json", re.sub(r'"https?://[^"]+"', json.dumps(CLOSED_URL),
                                             (ROOT / "parts" / "led-red-5mm.json").read_text())
             .replace('"id": "led-red-5mm"', '"id": "golden-led"'))
FUNCTION = planted("in.json", [{"does": "indicate", "what": "status"}])
NEEDS = planted(".spark/needs.json", {"schema": 1, "needs": [{"id": "light", "does": "indicate", "what": "status"},
                                                             {"id": "press", "does": "sense", "what": "button"}]})
PICKED = planted(".spark/needs.json", {"schema": 1, "needs": [
    {"id": "brain", "does": "compute", "what": "control", "pick": [{"board": BOARD_ID}]},
    {"id": "light", "does": "indicate", "what": "status", "pick": [{"part": "led-red-5mm"}]}]})
#: The project on the store's list, with one step marked in the suite's session, whose transcript no child finds.
LISTED = planted(STORE + "projects.json", {"button light": PROJECT})
STEPPED = (STORE + "history.jsonl", json.dumps({"event": "step", "project": "button light", "step": "S",
                                                "session": SESSION, "start": "2026-11-08T09:00:00+00:00"}) + "\n")
DRAWER = planted(STORE + "drawer/red-leds.json", {"label": "red leds", "count": 5, "is": {"part": "led-red-5mm"}})
CATALOG = planted(STORE + "catalog/golden-led.json", GOLDEN_LED)
SHEET = ("sheet.pdf", "%PDF-1.4 golden\n")
SHEET_KEPT = STORE + "sources/52d4d0818e899676cc5d6b002096ebd21d4108b2df2bb7d7cc4717d38325a0b3/sheet.pdf"
ORDERS = planted("in.json", {"source": "dfrobot", "lines": 1, "stated": 1,
                             "items": [{"sku": "DFR0954", "name": "MAX98357 I2S Amplifier", "count": 2}]})
TOOLS = ".spark/tools.json"
WITH = ["--project", PROJECT]
#: One transcript of a run: three minutes, one search and one agent.
TRANSCRIPT = ("run.jsonl", "".join(json.dumps(entry) + "\n" for entry in (
    {"type": "user", "timestamp": "2026-11-08T09:00:00Z", "message": {"role": "user", "content": "go"}},
    {"type": "assistant", "timestamp": "2026-11-08T09:03:00Z", "message": {
        "id": "m1", "usage": {"input_tokens": 10, "cache_creation_input_tokens": 5, "output_tokens": 7},
        "content": [{"type": "tool_use", "name": "WebSearch", "input": {"query": "led"}},
                    {"type": "tool_use", "name": "Agent", "input": {"subagent_type": "part-finder"}}]}})))

Case = golden_design.Case
CASES = [
    # --- parts.py: one Case or more per OPERATIONS entry ---
    Case("parts-list-ok.txt", "parts.py", ["--list"], 0),
    Case("parts-list-could-not-run-bad-argument.json", "parts.py", ["--list", "--from", "-1", "--json"], 2),
    Case("parts-show-ok.txt", "parts.py", ["--show", "led-red-5mm"], 0),
    Case("parts-show-problems-no-such-part.json", "parts.py", ["--show", "no-such-part", "--json"], 1),
    Case("parts-validate-problems-contract.txt", "parts.py", ["--validate"] + WITH, 1, (SMALL_LED,)),
    Case("parts-signals-ok.txt", "parts.py", ["--signals", "tactile-button", "led-red-5mm"], 0),
    Case("parts-unverified-ok.txt", "parts.py", ["--unverified", "vl6180x-breakout"], 0),
    Case("parts-need-ok.json", "parts.py", ["--need", "button", "--json"], 0),
    Case("parts-need-ok-nothing.txt", "parts.py", ["--need", "teleporter"], 0),
    Case("parts-need-could-not-run-unknown-matcher.txt", "parts.py", ["--need", "button", "--matcher", "nosuch"], 2),
    Case("parts-skeleton-ok.txt", "parts.py", ["--skeleton", "golden-sensor", "--kind", "sensor", "--vendor", "nobody"]
         + WITH, 0, written=("parts/golden-sensor.json",)),
    Case("parts-skeleton-could-not-run-no-project.txt", "parts.py", ["--skeleton", "golden-sensor", "--kind", "sensor"],
         2),
    Case("parts-sources-problems-unreachable.txt", "parts.py", ["--sources", "golden-led"] + WITH, 1, (LOCAL_LED,)),
    Case("parts-sources-ok-dry-run.txt", "parts.py", ["--sources", "golden-led", "--dry-run"] + WITH, 0, (LOCAL_LED,)),
    Case("parts-fetch-ok-unreachable.txt", "parts.py", ["--fetch", "golden-led"] + WITH, 0, (SMALL_LED,),
         written=("parts/golden-led.json",)),
    Case("parts-fetch-ok-dry-run.txt", "parts.py", ["--fetch", "golden-led", "--dry-run"] + WITH, 0, (SMALL_LED,)),
    Case("parts-fetch-problems-no-record.json", "parts.py", ["--fetch", "no-such-part", "--json"] + WITH, 1),
    Case("parts-fetch-problems-no-record-dry-run.txt", "parts.py", ["--fetch", "no-such-part", "--dry-run"] + WITH, 1),
    Case("parts-keep-ok.txt", "parts.py", ["--keep", "sheet.pdf", "--url", CLOSED_URL], 0, (SHEET,),
         written=(SHEET_KEPT,)),
    Case("parts-keep-could-not-run-no-file.txt", "parts.py", ["--keep", "missing.pdf"], 2),
    Case("parts-read-ok.txt", "parts.py", ["--read", "sheet.pdf", "--want", "forward_voltage_v"], 0, (SHEET,)),
    Case("parts-read-problems-not-found.txt", "parts.py", ["--read", "sheet.pdf", "--want", "peak_wavelength_nm"], 1,
         (SHEET,)),
    Case("parts-kept-ok.txt", "parts.py", ["--kept", "kingbright"], 0),
    Case("parts-promote-ok.txt", "parts.py", ["--promote", "golden-led"] + WITH, 0, (CATALOG,),
         written=("parts/golden-led.json",)),
    # A project's record goes up to the plugin's library, the repository itself: only ever with --dry-run.
    Case("parts-promote-ok-dry-run-library.txt", "parts.py", ["--promote", "golden-led", "--dry-run"] + WITH, 0,
         (SMALL_LED,)),
    Case("parts-promote-could-not-run-no-project.txt", "parts.py", ["--promote", "golden-led"], 2),
    Case("parts-catalog-ok.txt", "parts.py", ["--catalog"], 0, (CATALOG,)),
    Case("parts-drawer-ok.txt", "parts.py", ["--drawer"], 0, (DRAWER,)),
    Case("parts-drawer-set-ok.txt", "parts.py", ["--drawer-set", "in.json"], 0,
         (planted("in.json", [{"label": "red leds", "count": 5}]),), written=(STORE + "drawer/red-leds.json",)),
    Case("parts-drawer-set-could-not-run-unreadable.txt", "parts.py", ["--drawer-set", "in.json"], 2,
         (("in.json", "{not json"),)),
    Case("parts-drawer-import-ok.txt", "parts.py", ["--drawer-import", "dfrobot", "in.json"], 0, (ORDERS,),
         written=(STORE + "drawer/dfrobot-dfr0954.json", STORE + "drawer-import/dfrobot.json")),
    Case("parts-function-set-ok.txt", "parts.py", ["--function-set", "golden-led", "in.json"] + WITH, 0,
         (SMALL_LED, FUNCTION), written=("parts/golden-led.json",)),
    Case("parts-function-set-problems-library.txt", "parts.py", ["--function-set", "led-red-5mm", "in.json"], 1,
         (FUNCTION,)),
    Case("parts-fact-set-ok.txt", "parts.py", ["--fact-set", "golden-led", "in.json"] + WITH, 0,
         (SMALL_LED, planted("in.json", {"about": "A red light."})), written=("parts/golden-led.json",)),
    Case("parts-fact-set-problems-not-a-fact.txt", "parts.py", ["--fact-set", "golden-led", "in.json"] + WITH, 1,
         (SMALL_LED, planted("in.json", {"colour": "red"}))),
    Case("parts-audit-ok.txt", "parts.py", ["--audit"] + WITH, 0),
    Case("parts-needs-ok.txt", "parts.py", ["--needs", PROJECT], 0, (NEEDS,)),
    Case("parts-needs-set-ok.txt", "parts.py", ["--needs-set", PROJECT, "in.json"], 0,
         (planted("in.json", [{"id": "light", "does": "indicate", "what": "status"}]),),
         written=(".spark/needs.json",)),
    Case("parts-needs-set-could-not-run-unreadable.txt", "parts.py", ["--needs-set", PROJECT, "in.json"], 2,
         (("in.json", "{not json"),)),
    Case("parts-match-ok.txt", "parts.py", ["--match", PROJECT], 0, (NEEDS,)),
    Case("parts-offer-ok.txt", "parts.py", ["--offer", "tactile-button"], 0),
    Case("parts-offer-problems-no-such-offer.txt", "parts.py", ["--offer", "nosuch"], 1),
    Case("parts-pick-ok.txt", "parts.py", ["--pick", PROJECT, "light=led-red-5mm", "press=tactile-button"], 0, (NEEDS,),
         written=(".spark/needs.json", STORE + "projects.json")),
    Case("parts-pick-problems-no-such-need.txt", "parts.py", ["--pick", PROJECT, "nosuch=led-red-5mm"], 1, (NEEDS,)),
    Case("parts-needs-drop-ok.txt", "parts.py", ["--needs-drop", PROJECT, "press"], 0, (NEEDS,),
         written=(".spark/needs.json",)),
    Case("parts-requirements-ok.txt", "parts.py", ["--requirements", PROJECT], 0, (PICKED, ("requirements.json", None)),
         written=("requirements.json",)),
    Case("parts-requirements-problems-no-board.txt", "parts.py", ["--requirements", PROJECT], 1, (NEEDS,)),
    Case("parts-step-ok.txt", "parts.py", ["--step", PROJECT, "S"], 0,
         written=(STORE + "history.jsonl", STORE + "projects.json")),
    Case("parts-step-could-not-run-unknown-step.txt", "parts.py", ["--step", PROJECT, "nap"], 2),
    Case("parts-tally-could-not-run-no-transcript.json", "parts.py", ["--tally", PROJECT, "--json"], 2,
         (LISTED, STEPPED)),
    Case("parts-tally-could-not-run-not-listed.txt", "parts.py", ["--tally", PROJECT], 2),
    Case("parts-describe-ok.txt", "parts.py", ["--describe"], 0),
    # --- boards.py: one Case per flag, and a refusal ---
    Case("boards-path-ok.txt", "boards.py", ["--path"] + WITH, 0),
    Case("boards-id-ok.txt", "boards.py", ["--id"] + WITH, 0),
    Case("boards-id-could-not-run-no-selection.txt", "boards.py", ["--id"] + WITH, 1, (("boards/active.json", None),)),
    Case("boards-list-ok.txt", "boards.py", ["--list"] + WITH, 0),
    Case("boards-paths-ok.txt", "boards.py", ["--paths"] + WITH, 0),
    Case("boards-validate-ok.txt", "boards.py", ["--validate"] + WITH, 0),
    Case("boards-get-ok.txt", "boards.py", ["--get", "pins.A0"] + WITH, 0),
    Case("boards-get-could-not-run-no-key.txt", "boards.py", ["--get", "no.such.key"] + WITH, 1),
    Case("boards-resolve-ok.txt", "boards.py", ["--resolve"] + WITH, 0),
    # --- tools.py: one Case per flag; --install only with --dry-run ---
    Case("tools-status-could-not-run.txt", "tools.py", ["--status"] + WITH, 2),
    Case("tools-install-ok-dry-run.txt", "tools.py",
         ["--install", "pdftotext", "micropython-esp32s3", "--dry-run"] + WITH, 0),
    Case("tools-on-ok.txt", "tools.py", ["--on", "pdftotext"] + WITH, 0, written=(TOOLS,)),
    Case("tools-off-ok.txt", "tools.py", ["--off", "pdftotext"] + WITH, 0, written=(TOOLS,)),
    Case("tools-use-ok.txt", "tools.py", ["--use", "pdf-text=pdftotext"] + WITH, 0, written=(TOOLS,)),
    Case("tools-pin-ok.txt", "tools.py", ["--pin", "pdftotext=24.02.0"] + WITH, 0, written=(TOOLS,)),
    Case("tools-new-ok.txt", "tools.py",
         ["--new", 'my-sim={"kind": "path", "exe": "my-sim", "meets": ["wokwi-project"]}'] + WITH, 0,
         written=(TOOLS,)),
    Case("tools-new-could-not-run-not-json.txt", "tools.py", ["--new", "my-sim={not json"] + WITH, 2),
    # --- cost.py: with its one transcript, and with none ---
    Case("cost-ok.txt", "cost.py", ["run.jsonl"], 0, (TRANSCRIPT,)),
    Case("cost-could-not-run-no-transcript.txt", "cost.py", [], 2),
]


def build_project(folder):
    """The project the goldens run in: a bare copy of golden_checks' button-light fixture, whose active board is the
    firebeetle. Returns the project's Path."""
    project = Path(folder) / "button light"
    shutil.copytree(golden_checks.FIXTURE, project)
    (project / "boards").mkdir()
    (project / "boards" / "active.json").write_text(json.dumps({"board": BOARD_ID}))
    return project


def replacements_of(project, store, shims):
    """golden_bench's replacements, and the fakes' folder and the child's HOME beside the store, longest first."""
    places = dict(golden_bench.replacements_of(project, store))
    for path, name in ((Path(shims).parent, "<fakes>"), (Path(store).parent / "home", "<home>")):
        for form in (str(path), str(Path(path).resolve())):
            places[form] = name
    return dict(sorted(places.items(), key=lambda item: -len(item[0])))


def placed(name, project, store):
    """Where a planted or written `name` is: under `store` when it starts with STORE, else under `project`."""
    return Path(store) / name[len(STORE):] if name.startswith(STORE) else Path(project) / name


def run_case(case, project, store, shims):
    """The text of `case` run in `project` with `store` (its STORE files planted there first), then each of its
    `written` files after LOG_MARK, and its exit code. A day's date and a refused connection's errno are
    placeholders."""
    case = case._replace(plant=tuple((name, text if text is None else text.replace(PROJECT, str(project)))
                                     for name, text in case.plant))
    for name, text in case.plant:
        if name.startswith(STORE):
            placed(name, project, store).parent.mkdir(parents=True, exist_ok=True)
            placed(name, project, store).write_text(text)
    in_project = tuple(planted for planted in case.plant if not planted[0].startswith(STORE))
    code, text = golden_firmware.run_script(case._replace(plant=in_project), project, store, child_env(store, shims))
    for name in case.written:
        text += LOG_MARK % name + placed(name, project, store).read_text()
    return code, DAY.sub(r"\1<day>", ERRNO.sub("[Errno <n>] Connection refused", text))
