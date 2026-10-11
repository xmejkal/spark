# Tools spark depends on — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every tool spark depends on is found, checked and installed from one merged list (spark's defaults, the person's, the project's), so a spark user can turn integrations on and off, change versions, swap a tool and add their own without editing spark's code — and `/spark:setup` installs what is missing with one yes.

**Architecture:** A data file, `data/tools.json`, lists each tool (what it is for, how to find it, how to install it, which contract it meets) and the roles that point at tools. One helper, `scripts/tools.py`, merges it with `~/.local/share/spark/tools.json` and the project's `.spark/tools.json` (project wins, field by field) and answers `find(role_or_name, project)`. The seven scripts that search for their own tools ask `find` instead, one per task. The simulation converter is bundled into one file that runs on Node. Last, `tools.py`'s subcommands and `/spark:setup` install and register, then a cold run proves it.

**Tech Stack:** Python 3 standard library only (spark's rule: no third-party imports in `scripts/`), `unittest`, spark's `tools/mutate.py`; Node 20+ for the bundled converter; `bun build` at development time only.

**Spec:** `docs/2026-10-03-tools-design.md` (approved by the PO 2026-10-03). Backlog: P82 (with B10).

## Global Constraints

- **Never `sudo`.** No command spark builds or runs contains it; a tool that needs it is named with its command, never run.
- **Nothing installs without the person's yes.** Scripts never install during a check; they report what is missing and its install line.
- **A missing tool is could-not-run** (`COULD_NOT_RUN`, exit 2, `[????]`), never a traceback and never a failure.
- **Tests run offline on the Mac**, install nothing, and never run a Wokwi simulation (a fake stands in for `wokwi-cli`).
- **No third-party Python import in `scripts/`**; `scripts/` stays within its 5,000 code-line budget (`tests/test_orphans.py`), currently 4,227.
- **The layers:** spark `data/tools.json` → personal `~/.local/share/spark/tools.json` → project `.spark/tools.json`; merged entry by entry, field by field; the project wins.
- **Top-level keys of a tools file** are tool names, plus `roles` (role → tool name) and `contracts` (role → contract id, read from spark's defaults only); keys starting `//` are comments.
- **No script other than `scripts/tools.py` names a tool's executable** (`tsci`, `bun`, `wokwi-cli`, `pdftotext`, `node`) as a string literal — a test enforces it.
- **Every task ships a mutation table** `tests/mutations/sprint-10-p82-<task>.json`, run with `python3 tools/mutate.py <table>`, every mutation caught; `python3 tools/mutate.py --anchors tests/mutations/*.json` clean; the full suite (`python3 -m unittest discover -s tests -t tests`) green before each commit (the pre-push gate re-runs both).
- **Commit messages** end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`; numbers in them come from output already shown (W13).

## Review Focus

1. **A tools file that is not JSON, or not an object** (a personal file half-edited by hand) — expected: the step that asked ends could-not-run naming the file and the parse error; never a traceback. Test in Task 1.
2. **A project entry that names a tool spark does not know and gives no `kind` or `exe`** — expected: refused by name ("no way to find it: the entry names no exe"), not a KeyError. Test in Task 1.
3. **A tool turned `"on": false` in the project while spark's default has it on** — expected: the project wins; the step says it is turned off and how to turn it on. Test in Task 1.
4. **No `~/.local/share/spark` folder at all** (a fresh machine) — expected: the personal layer is simply absent; nothing is created until a choice is written. Test in Task 1 (absent) and Task 6 (created on `--on`).
5. **Node missing when the bundled converter is asked for** — expected: simulation could-not-run, "node is not installed — install: brew install node", not a crash. Test in Task 4.

---

## File structure

| file | responsibility |
| --- | --- |
| `data/tools.json` (create) | spark's defaults: one entry per tool, the roles, the contracts |
| `scripts/tools.py` (create) | merge the layers; `find`; locate by kind; the install line; later the CLI (`--status`, `--install`, `--on`, `--off`, `--use`, `--pin`) |
| `tests/test_tools.py` (create) | everything about `tools.py`, offline, with temporary layer files |
| `scripts/parts.py` (modify) | `--read` asks `tools.find("pdf-text")` |
| `scripts/sim_project.py` (modify) | chip compile asks `tools.find("simulator")` |
| `scripts/check_spine.py` (modify) | tsci from `tools.find("board-engine")`; the converter from `tools.find("diagram-converter")`, run on Node |
| `scripts/init_project.py` (modify) | pinned versions read from the tscircuit entry |
| `scripts/flash_image.py` (modify) | littlefs and the MicroPython build from `tools.find` |
| `tools/circuit-to-wokwi/dist/converter.mjs` (create, generated) | the bundled converter; `dist/converter.sources.sha256` beside it |
| `commands/setup.md` (create) | `/spark:setup`: the conversation around `tools.py` |
| `tests/test_self_confirmation.py`, `tests/test_orphans.py` (modify) | list `tools.py`'s constants a test reads; the "no tool names in scripts" rule |
| `README.md`, `docs/mcp.md`, `commands/build.md` (modify) | say what the entries do not |

---

### Task 1: The tools list, the helper, and its first user (`pdftotext`)

**Files:**
- Create: `data/tools.json`, `scripts/tools.py`, `tests/test_tools.py`, `tests/mutations/sprint-10-p82-1.json`
- Modify: `scripts/parts.py` (the `read_datasheet` and `datasheet_pages` functions), `tests/test_self_confirmation.py` (`MAY_READ`), `tests/test_orphans.py` (the new rule)

**Interfaces:**
- Produces: `tools.merged(project=None, personal=None) -> {"tools": {name: entry}, "roles": {role: name}, "contracts": {role: id}}`; `tools.find(name, project=None, personal=None) -> Tool(name, role, entry, command)` where `command` is a `list[str]`; `tools.ToolProblem(Exception)` whose `str()` is the whole sentence a person reads; `tools.install_line(entry) -> str | None`; constants `PLUGIN`, `DEFAULTS`, `SPARK_HOME`, `PERSONAL`, `DOWNLOADS`, `PROJECT_FILE`.

- [ ] **Step 1: Write the failing tests** — `tests/test_tools.py`:

```python
"""P82: the tools spark depends on, from one merged list (docs/2026-10-03-tools-design.md)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import tools  # noqa: E402

DEFAULTS = {
    "roles": {"pdf-text": "pdftotext"},
    "contracts": {"pdf-text": "page-text"},
    "pdftotext": {"for": "reading a datasheet", "kind": "path", "exe": "pdftotext",
                  "meets": ["page-text"], "install": {"brew": "brew install poppler"}},
}


def layer(data):
    path = Path(tempfile.mkdtemp()) / "tools.json"
    path.write_text(data if isinstance(data, str) else json.dumps(data))
    return path


def project_with(data):
    root = Path(tempfile.mkdtemp())
    (root / ".spark").mkdir()
    (root / ".spark" / "tools.json").write_text(json.dumps(data))
    return root


class TheLayersMergeFieldByFieldTest(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(tools, "DEFAULTS", layer(DEFAULTS))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.nobody = Path(tempfile.mkdtemp()) / "absent.json"

    def test_the_project_wins_one_field_and_inherits_the_rest(self):
        personal = layer({"pdftotext": {"install": {"brew": "brew install poppler-qt5"}}})
        project = project_with({"pdftotext": {"exe": "pdftotext-23"}})
        entry = tools.merged(project, personal)["tools"]["pdftotext"]
        self.assertEqual(entry["exe"], "pdftotext-23")
        self.assertEqual(entry["install"], {"brew": "brew install poppler-qt5"})
        self.assertEqual(entry["meets"], ["page-text"])

    def test_no_personal_file_is_simply_absent(self):
        self.assertIn("pdftotext", tools.merged(None, self.nobody)["tools"])
        self.assertFalse(self.nobody.exists(), "reading creates nothing")

    def test_a_tools_file_that_is_not_json_is_named(self):
        with self.assertRaises(tools.ToolProblem) as refused:
            tools.merged(None, layer("{not json"))
        self.assertIn("is not JSON", str(refused.exception))

    def test_a_tools_file_that_is_not_an_object_is_named(self):
        with self.assertRaises(tools.ToolProblem) as refused:
            tools.merged(None, layer("[1, 2]"))
        self.assertIn("a tools file is an object", str(refused.exception))

    def test_contracts_are_spark_s_to_state(self):
        personal = layer({"contracts": {"pdf-text": "anything"}})
        self.assertEqual(tools.merged(None, personal)["contracts"]["pdf-text"], "page-text")


class FindingATool(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(tools, "DEFAULTS", layer(DEFAULTS))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.nobody = Path(tempfile.mkdtemp()) / "absent.json"

    def test_a_role_leads_to_its_tool_and_its_command(self):
        with mock.patch.object(tools.shutil, "which", return_value="/opt/bin/pdftotext"):
            found = tools.find("pdf-text", None, self.nobody)
        self.assertEqual((found.name, found.role, found.command), ("pdftotext", "pdf-text", ["/opt/bin/pdftotext"]))

    def test_a_missing_tool_says_what_installs_it(self):
        with mock.patch.object(tools.shutil, "which", return_value=None):
            with self.assertRaises(tools.ToolProblem) as missing:
                tools.find("pdf-text", None, self.nobody)
        said = str(missing.exception)
        self.assertIn("pdf-text (pdftotext) is not installed", said)
        self.assertIn("brew install poppler", said)
        self.assertNotIn("sudo", said)

    def test_a_tool_that_does_not_meet_the_role_s_contract_is_refused(self):
        personal = layer({"roles": {"pdf-text": "my-reader"},
                          "my-reader": {"kind": "path", "exe": "my-reader"}})
        with self.assertRaises(tools.ToolProblem) as refused:
            tools.find("pdf-text", None, personal)
        self.assertIn("my-reader does not say it meets 'page-text'", str(refused.exception))

    def test_a_tool_turned_off_in_the_project_says_how_to_turn_it_on(self):
        project = project_with({"pdftotext": {"on": False}})
        with self.assertRaises(tools.ToolProblem) as off:
            tools.find("pdf-text", project, self.nobody)
        self.assertIn("/spark:setup add pdftotext", str(off.exception))

    def test_an_entry_with_no_way_to_find_it_is_refused_by_name(self):
        personal = layer({"mystery": {"for": "something"}})
        with self.assertRaises(tools.ToolProblem) as refused:
            tools.find("mystery", None, personal)
        self.assertIn("no way to find it", str(refused.exception))

    def test_an_npm_tool_is_found_in_the_project_before_the_path(self):
        root = Path(tempfile.mkdtemp())
        (root / "node_modules" / ".bin").mkdir(parents=True)
        (root / "node_modules" / ".bin" / "tsci").write_text("#!/bin/sh\n")
        personal = layer({"tscircuit": {"kind": "npm", "exe": "tsci"}})
        with mock.patch.object(tools.shutil, "which", return_value="/global/tsci"):
            found = tools.find("tscircuit", root, personal)
        self.assertEqual(found.command, [str(root / "node_modules" / ".bin" / "tsci")])
```

Also in `tests/test_orphans.py`, inside `NothingShipsUnusedTest`, add the rule (the allow-list shrinks task by task and must end empty in Task 4):

```python
    #: Scripts that still name a tool's executable, until their task moves them to tools.find (P82).
    NOT_YET_MOVED = {"sim_project.py": {"wokwi-cli"}, "check_spine.py": {"tsci", "bun"}}

    def test_no_script_but_tools_names_a_tool_s_executable(self):
        names = {entry.get("exe") for key, entry in json.loads((ROOT / "data" / "tools.json").read_text()).items()
                 if isinstance(entry, dict) and entry.get("exe")} | {"bun"}
        named = {}
        for path in sorted((ROOT / "scripts").glob("*.py")):
            if path.name == "tools.py":
                continue
            text = path.read_text()
            found = {name for name in names if '"%s"' % name in text}
            if found - self.NOT_YET_MOVED.get(path.name, set()):
                named[path.name] = sorted(found - self.NOT_YET_MOVED.get(path.name, set()))
        self.assertEqual(named, {}, "ask tools.find for the tool instead (P82)")

    def test_every_script_still_allowed_to_name_a_tool_still_does(self):
        stale = {name: sorted(tools_named) for name, tools_named in self.NOT_YET_MOVED.items()
                 if not all('"%s"' % tool in (ROOT / "scripts" / name).read_text() for tool in tools_named)}
        self.assertEqual(stale, {}, "a moved script left in NOT_YET_MOVED")
```

(Add `import json` at the top of `tests/test_orphans.py` if it is not there.)

- [ ] **Step 2: Run them — they fail**

Run: `python3 -m unittest tests.test_tools tests.test_orphans 2>&1 | tail -5`
Expected: `ModuleNotFoundError: No module named 'tools'` for `test_tools`; the rule test fails naming `parts.py` (`"pdftotext"`) once `data/tools.json` exists.

- [ ] **Step 3: Write `data/tools.json`**

```json
{
  "//": "The tools spark depends on (P82, docs/2026-10-03-tools-design.md). A person's ~/.local/share/spark/tools.json and a project's .spark/tools.json override any field of any entry; the project wins. `roles` points a job at a tool; `contracts` says what the job needs, and only this file states them.",
  "roles": {"pdf-text": "pdftotext"},
  "contracts": {"pdf-text": "page-text"},
  "pdftotext": {
    "for": "reading a datasheet page by page (parts.py --read)",
    "kind": "path",
    "exe": "pdftotext",
    "meets": ["page-text"],
    "install": {"brew": "brew install poppler", "apt": "sudo apt install poppler-utils"}
  }
}
```

- [ ] **Step 4: Write `scripts/tools.py`**

```python
#!/usr/bin/env python3
"""
The tools spark depends on, found from one merged list (P82, docs/2026-10-03-tools-design.md).

spark's dependencies were decided in seven places, each with its own lookup and its own error
message. Now one list says what each tool is for, how to find it, how to install it and which
contract it meets: spark's defaults in data/tools.json, the person's in
~/.local/share/spark/tools.json, the project's in .spark/tools.json — merged entry by entry and
field by field, the project winning. Every script asks `find`; nothing else names a tool.

A missing tool is a ToolProblem whose sentence says what installs it. Nothing here installs.
"""

import importlib.util
import json
import shutil
import sys
from collections import namedtuple
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import boards  # noqa: E402

PLUGIN = SCRIPTS.parent
DEFAULTS = PLUGIN / "data" / "tools.json"
SPARK_HOME = Path.home() / ".local" / "share" / "spark"
PERSONAL = SPARK_HOME / "tools.json"
DOWNLOADS = SPARK_HOME / "downloads"
PROJECT_FILE = Path(".spark") / "tools.json"
#: Keys of a tools file that are not tools.
RESERVED = ("roles", "contracts")
#: The install managers tried in order, each with the program that has to be there for it to apply.
MANAGERS = (("npm", "npm"), ("pip", "python3"), ("brew", "brew"))

Tool = namedtuple("Tool", "name role entry command")


class ToolProblem(Exception):
    """A tool spark cannot use — missing, refused, turned off, or a list it cannot read. The message is the whole sentence."""


def _read(path):
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text())
    except ValueError as broken:
        raise ToolProblem("%s is not JSON (%s) — fix it or delete it" % (path, broken))
    if not isinstance(data, dict):
        raise ToolProblem("%s holds a %s; a tools file is an object" % (path, type(data).__name__))
    return data


def merged(project=None, personal=None):
    """The three layers as one list: tools merged field by field, roles key by key, the project winning."""
    lists = {"tools": {}, "roles": {}, "contracts": {}}
    paths = [DEFAULTS, Path(personal) if personal else PERSONAL]
    if project:
        paths.append(Path(project) / PROJECT_FILE)
    for path in paths:
        data = _read(path)
        for key, value in data.items():
            if key.startswith("//") or key in RESERVED:
                continue
            if not isinstance(value, dict):
                raise ToolProblem("%s: the entry %r is not an object" % (path, key))
            lists["tools"].setdefault(key, {}).update(value)
        lists["roles"].update(data.get("roles") or {})
        if path == DEFAULTS:
            lists["contracts"].update(data.get("contracts") or {})
    return lists


def install_line(entry):
    """The one command that installs this tool here, with its version filled in — or None."""
    install = entry.get("install") or {}
    for manager, needs in MANAGERS:
        if manager in install and shutil.which(needs):
            return install[manager].format(version=entry.get("version", ""), core=entry.get("core", ""))
    return None


def locate(entry, project):
    """The command that runs this tool, by its kind — or None when it is not here."""
    kind = entry.get("kind", "path")
    if kind == "python":
        return [sys.executable] if importlib.util.find_spec(entry["module"]) else None
    if kind == "download":
        path = DOWNLOADS / entry["file"]
        return [str(path)] if path.is_file() else None
    if kind == "bundled":
        path = PLUGIN / entry["file"]
        return [str(path)] if path.is_file() else None
    exe = entry["exe"]
    if kind == "npm" and project:
        for directory in boards.walk_up(Path(project)):
            local = directory / "node_modules" / ".bin" / exe
            if local.is_file():
                return [str(local)]
    found = shutil.which(exe)
    if found:
        return [found]
    for also in entry.get("also") or []:
        path = Path(also).expanduser()
        if path.is_file():
            return [str(path)]
    return None


def find(name, project=None, personal=None):
    """A role or a tool's name -> the Tool to run, or a ToolProblem saying why not and what to do."""
    lists = merged(project, personal)
    role = name if name in lists["roles"] else None
    tool_name = lists["roles"].get(name, name)
    entry = lists["tools"].get(tool_name)
    if entry is None:
        raise ToolProblem("%s: no tool called %r in any tools file" % (name, tool_name))
    contract = lists["contracts"].get(role) if role else None
    if contract and contract not in (entry.get("meets") or []):
        raise ToolProblem("%s: %s does not say it meets %r, so this step will not use it"
                          % (role, tool_name, contract))
    if entry.get("on") is False:
        raise ToolProblem("%s is turned off — turn it on: /spark:setup add %s" % (tool_name, tool_name))
    if entry.get("kind", "path") in ("path", "npm") and not entry.get("exe"):
        raise ToolProblem("%s: no way to find it — the entry names no exe" % tool_name)
    command = locate(entry, project)
    if command is None:
        line = install_line(entry)
        raise ToolProblem("%s (%s) is not installed — install: %s"
                          % (role or tool_name, tool_name, line or "see its entry in %s" % DEFAULTS))
    return Tool(tool_name, role, entry, command)
```

- [ ] **Step 5: Run the tools tests — they pass**

Run: `python3 -m unittest tests.test_tools -v 2>&1 | tail -3`
Expected: `OK` (12 tests).

- [ ] **Step 6: Move `parts.py --read` to `tools.find`** — in `scripts/parts.py`, `datasheet_pages` takes the command it runs (no default, so no tool name is written here), and `read_datasheet` asks the list for it:

```python
def datasheet_pages(path, command):
    """(number, text) per page of a PDF, as the pdf-text tool lays it out — one page at a time, on demand."""
    import subprocess
    number = 1
    while True:
        done = subprocess.run(list(command) + ["-layout", "-f", str(number), "-l", str(number), str(path), "-"],
                              capture_output=True, text=True)
        if done.returncode != 0:
            return
        yield number, done.stdout
        number += 1


def read_datasheet(path, wanted, labels=None, project=None):
    """Print what `scan_datasheet` found, with the pages read; EXIT_OK only when every fact was FOUND."""
    import tools
    try:
        reader = tools.find("pdf-text", project)
    except tools.ToolProblem as missing:
        print("parts.py: --read: %s" % missing, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    read = []
    def counted():
        for page in datasheet_pages(path, reader.command):
            read.append(page[0])
            yield page
```

(the rest of `read_datasheet` is unchanged), and the CLI branch passes the project:
`return read_datasheet(args.read, args.want or [], labels, project)`.

Update the one existing test that checks the missing-tool message, if any, to expect `"pdf-text (pdftotext) is not installed"`: run `/usr/bin/grep -n "brew install poppler" tests/test_parts.py` and adjust what it finds.

- [ ] **Step 7: List `tools.py`'s constants the tests read** — in `tests/test_self_confirmation.py` `MAY_READ`, add:

```python
    "tools.DEFAULTS": STRUCTURE, "tools.PERSONAL": STRUCTURE, "tools.DOWNLOADS": STRUCTURE,
    "tools.PLUGIN": STRUCTURE,
```

(only those the tests actually read — `test_every_reason_is_still_needed` fails on an unused one; remove any it names).

- [ ] **Step 8: Run the full suite — green**

Run: `python3 -m unittest discover -s tests -t tests 2>&1 | tail -3`
Expected: `OK`. The rule test passes: `parts.py` no longer contains `"pdftotext"`.

- [ ] **Step 9: Mutation table** — `tests/mutations/sprint-10-p82-1.json`:

```json
[
 {"file": "scripts/tools.py", "name": "the project no longer wins a field",
  "find": "            lists[\"tools\"].setdefault(key, {}).update(value)", "replace": "            lists[\"tools\"].setdefault(key, value)"},
 {"file": "scripts/tools.py", "name": "a contract can be rewritten by a person",
  "find": "        if path == DEFAULTS:\n            lists[\"contracts\"]", "replace": "        if True:\n            lists[\"contracts\"]"},
 {"file": "scripts/tools.py", "name": "a tool that does not meet the contract is used anyway",
  "find": "    if contract and contract not in (entry.get(\"meets\") or []):", "replace": "    if False:"},
 {"file": "scripts/tools.py", "name": "a tool turned off is used anyway",
  "find": "    if entry.get(\"on\") is False:", "replace": "    if False:"},
 {"file": "scripts/tools.py", "name": "the project's node_modules is not looked in first",
  "find": "    if kind == \"npm\" and project:", "replace": "    if False:"},
 {"file": "scripts/tools.py", "name": "a missing tool does not say what installs it",
  "find": "                          % (role or tool_name, tool_name, line or \"see its entry in %s\" % DEFAULTS))", "replace": "                          % (role or tool_name, tool_name, \"\"))"}
]
```

Run: `python3 tools/mutate.py tests/mutations/sprint-10-p82-1.json`
Expected: every line `[caught ]`, then `every mutation was caught, and the suite is green with the files restored`.

- [ ] **Step 10: Commit**

```bash
git add data/tools.json scripts/tools.py scripts/parts.py tests/test_tools.py tests/test_orphans.py tests/test_self_confirmation.py tests/mutations/sprint-10-p82-1.json
git commit -m "P82, task 1: one list of the tools spark depends on, and tools.find — parts.py --read is its first user"
```

---

### Task 2: `wokwi-cli` from the list (`sim_project.py`)

**Files:**
- Modify: `data/tools.json`, `scripts/sim_project.py:18-29,147`, `tests/test_orphans.py` (`NOT_YET_MOVED`), `tests/test_sim_project.py`
- Create: `tests/mutations/sprint-10-p82-2.json`

**Interfaces:**
- Consumes: `tools.find`, `tools.ToolProblem` (Task 1).
- Produces: `sim_project.find_wokwi_cli(project=None) -> str | None` keeps its name and return type for its callers; its message comes from the entry.

- [ ] **Step 1: Write the failing test** — in `tests/test_sim_project.py`:

```python
class WokwiCliComesFromTheToolsListTest(unittest.TestCase):
    def test_wokwi_cli_is_found_through_the_simulator_role(self):
        import tools
        found = tools.Tool("wokwi-cli", "simulator", {}, ["/somewhere/wokwi-cli"])
        with mock.patch.object(tools, "find", return_value=found) as asked:
            self.assertEqual(sim_project.find_wokwi_cli(), "/somewhere/wokwi-cli")
        self.assertEqual(asked.call_args[0][0], "simulator")

    def test_no_wokwi_cli_is_none_with_the_reason_kept(self):
        import tools
        with mock.patch.object(tools, "find", side_effect=tools.ToolProblem("simulator (wokwi-cli) is not installed — install: npm install -g wokwi-cli")):
            self.assertIsNone(sim_project.find_wokwi_cli())
        self.assertIn("npm install -g wokwi-cli", sim_project.INSTALL_HINT)
```

- [ ] **Step 2: Run it — it fails** (`find_wokwi_cli` does not call `tools.find`; `INSTALL_HINT` names the releases page).

Run: `python3 -m unittest tests.test_sim_project.WokwiCliComesFromTheToolsListTest 2>&1 | tail -3` — Expected: `FAILED`.

- [ ] **Step 3: Add the entry and the role** to `data/tools.json`:

```json
  "roles": {"pdf-text": "pdftotext", "simulator": "wokwi-cli"},
  "contracts": {"pdf-text": "page-text", "simulator": "wokwi-project"},
  "wokwi-cli": {
    "for": "compiling custom chips (free, local) and running Wokwi scenarios (paid minutes)",
    "kind": "path",
    "exe": "wokwi-cli",
    "also": ["~/.local/bin/wokwi-cli"],
    "meets": ["wokwi-project"],
    "install": {"npm": "npm install -g wokwi-cli"},
    "needs_account": "a Wokwi token in WOKWI_CLI_TOKEN — create one at wokwi.com/dashboard/ci"
  }
```

- [ ] **Step 4: Rewrite the lookup** in `scripts/sim_project.py`, replacing `WOKWI_CLI_HOME`, `INSTALL_HINT` and `find_wokwi_cli`:

```python
import tools  # noqa: E402

#: What to tell a person who has no wokwi-cli: the list's own install line, and that compiling is free.
INSTALL_HINT = "install: npm install -g wokwi-cli — `chip compile` runs locally and needs no account"


def find_wokwi_cli(project=None):
    """wokwi-cli, wherever the tools list says to look (PATH, ~/.local/bin), else None."""
    try:
        return tools.find("simulator", project).command[0]
    except tools.ToolProblem:
        return None
```

Remove `"wokwi-cli"` from `NOT_YET_MOVED` in `tests/test_orphans.py` (`{"check_spine.py": {"tsci", "bun"}}` remains).

- [ ] **Step 5: Run the full suite — green**

Run: `python3 -m unittest discover -s tests -t tests 2>&1 | tail -3` — Expected: `OK`. Any existing test that patched `sim_project.WOKWI_CLI_HOME` now patches `tools.find` instead; run `/usr/bin/grep -n WOKWI_CLI_HOME tests/*.py` and update each.

- [ ] **Step 6: Mutation table** — `tests/mutations/sprint-10-p82-2.json`:

```json
[
 {"file": "scripts/sim_project.py", "name": "wokwi-cli is looked for outside the list again",
  "find": "        return tools.find(\"simulator\", project).command[0]", "replace": "        return None"},
 {"file": "data/tools.json", "name": "wokwi-cli no longer meets the simulator's contract",
  "find": "    \"meets\": [\"wokwi-project\"],", "replace": "    \"meets\": [],"}
]
```

Run: `python3 tools/mutate.py tests/mutations/sprint-10-p82-2.json` — Expected: both `[caught ]`. If the second escapes, add to `tests/test_tools.py` a test that loads the real `data/tools.json` and asserts `tools.merged()["tools"]["wokwi-cli"]["meets"]` contains `"wokwi-project"` — strengthen, never drop (W12).

- [ ] **Step 7: Commit**

```bash
git add data/tools.json scripts/sim_project.py tests/test_sim_project.py tests/test_orphans.py tests/test_tools.py tests/mutations/sprint-10-p82-2.json
git commit -m "P82, task 2: wokwi-cli comes from the tools list, through the simulator role"
```

---

### Task 3: tscircuit from the list (`check_spine.py`, `init_project.py`)

**Files:**
- Modify: `data/tools.json`, `scripts/check_spine.py:91-104` (`find_toolchain`), `scripts/init_project.py:348-352` (the pins), `tests/test_orphans.py`, `tests/test_check_spine.py`, `tests/test_init_project.py`
- Create: `tests/mutations/sprint-10-p82-3.json`

**Interfaces:**
- Consumes: `tools.find`, `tools.merged`.
- Produces: `check_spine.find_toolchain(start) -> Path | None` (unchanged signature); `init_project.PINNED_TSCI`, `init_project.PINNED_CORE` stay module constants, now read from the `tscircuit` entry (`version`, `core`).

- [ ] **Step 1: Write the failing test** — in `tests/test_init_project.py`:

```python
    def test_the_pins_are_the_tools_list_s(self):
        import tools
        entry = tools.merged()["tools"]["tscircuit"]
        self.assertEqual((init_project.PINNED_TSCI, init_project.PINNED_CORE), (entry["version"], entry["core"]))
```

- [ ] **Step 2: Run it — it fails** (`KeyError: 'tscircuit'`). Run: `python3 -m unittest tests.test_init_project 2>&1 | tail -3`.

- [ ] **Step 3: Add the entry** to `data/tools.json` (versions copied from `init_project.py` today):

```json
  "roles": {"pdf-text": "pdftotext", "simulator": "wokwi-cli", "board-engine": "tscircuit"},
  "contracts": {"pdf-text": "page-text", "simulator": "wokwi-project", "board-engine": "tscircuit-board"},
  "tscircuit": {
    "for": "building the board spark writes",
    "kind": "npm",
    "exe": "tsci",
    "version": "0.1.2113",
    "core": "0.0.2600",
    "meets": ["tscircuit-board"],
    "install": {"npm": "npm install --save-dev @tscircuit/cli@{version} tscircuit@{core}"}
  }
```

- [ ] **Step 4: Read the pins from the list** — in `scripts/init_project.py`, replace the two literals (keep the comment above them):

```python
import tools  # noqa: E402

_TSCIRCUIT = tools.merged()["tools"]["tscircuit"]
PINNED_TSCI = _TSCIRCUIT["version"]

#: The `tscircuit` core every number in the documents was measured on. Pinned as a direct
#: dependency, because the CLI's peer range accepts anything and would take the newest.
PINNED_CORE = _TSCIRCUIT["core"]
```

- [ ] **Step 5: `find_toolchain` asks the list** — in `scripts/check_spine.py`:

```python
def find_toolchain(start):
    """
    `tsci`, or None — the board-engine from the tools list: the project's own node_modules first,
    upward from `start`, then the PATH (a project's pinned version beats whatever is installed
    globally).
    """
    try:
        return Path(tools.find("board-engine", start).command[0])
    except tools.ToolProblem:
        return None
```

with `import tools  # noqa: E402` beside the other imports. The spec's version line (section 2, item 3)
lands here too, generic in `tools.py` and used by the drift check that already exists:

```python
def version_note(name, reported, field="version", project=None, personal=None):
    """'' when the reported version is the one the list states for this field, else the one line to print."""
    stated = merged(project, personal)["tools"].get(name, {}).get(field)
    if not stated or reported in (None, "unknown version") or str(reported) == str(stated):
        return ""
    return "; spark was measured on %s %s %s" % (name, field, stated)
```

and in `check_spine.core_note(version)`: `return tools.version_note("tscircuit", version, field="core")`
(keep its docstring). Test, in `tests/test_tools.py`:

```python
    def test_a_version_other_than_the_list_s_says_so_in_one_line(self):
        personal = layer({"pdftotext": {"version": "26.09.0"}})
        self.assertEqual(tools.version_note("pdftotext", "26.09.0", personal=personal), "")
        self.assertIn("measured on pdftotext version 26.09.0", tools.version_note("pdftotext", "24.0", personal=personal))
```

Remove `"tsci"` from `NOT_YET_MOVED` (`{"check_spine.py": {"bun"}}` remains). In `tests/test_check_spine.py`, the two `find_toolchain` tests that build a `node_modules/.bin/tsci` keep passing (the list's npm kind walks up); run them.

- [ ] **Step 6: Run the full suite — green.** Run: `python3 -m unittest discover -s tests -t tests 2>&1 | tail -3` — Expected: `OK`.

- [ ] **Step 7: Mutation table** — `tests/mutations/sprint-10-p82-3.json`:

```json
[
 {"file": "data/tools.json", "name": "the pinned core drifts from the documents' core",
  "find": "    \"core\": \"0.0.2600\",", "replace": "    \"core\": \"0.0.2700\","},
 {"file": "scripts/check_spine.py", "name": "tsci is looked for outside the list again",
  "find": "        return Path(tools.find(\"board-engine\", start).command[0])", "replace": "        return None"}
]
```

Run it; both `[caught ]` (the first by `test_init_project`'s existing check that the core matches `commands/build.md`). Then `python3 tools/mutate.py --anchors tests/mutations/*.json` — re-anchor any older mutation on the moved lines (`sprint-7-p51.json` names `PINNED_CORE = "0.0.2600"`: anchor it on the `data/tools.json` line instead) and run that table too.

- [ ] **Step 8: Commit** — `git commit -m "P82, task 3: tscircuit and its pinned versions come from the tools list"` (with the files above).

---

### Task 4: The converter bundled into one file that runs on Node (B10)

**Files:**
- Create: `tools/circuit-to-wokwi/dist/converter.mjs` (generated), `tools/circuit-to-wokwi/dist/converter.sources.sha256` (generated), `tools/circuit-to-wokwi/bundle.sh`, `tests/mutations/sprint-10-p82-4.json`
- Modify: `data/tools.json`, `scripts/check_spine.py:160-186,421-455`, `tests/test_check_spine.py`, `tests/test_orphans.py`, `.gitignore` (keep `node_modules` ignored; `dist/` committed)

**Interfaces:**
- Consumes: `tools.find("diagram-converter", project)` and `tools.find("node", project)`.
- Produces: `check_spine.find_converter(start) -> Path | None` (a project's own `tools/circuit-to-wokwi/cli.ts` still wins for development; otherwise the bundle); the simulation stage runs `node <bundle>` with the same arguments as before.

- [ ] **Step 1: The bundle script** — `tools/circuit-to-wokwi/bundle.sh`:

```bash
#!/bin/sh
# Builds the converter into one file that runs on Node with no node_modules (P82, ends B10).
# Development only: needs bun and `bun install` here. Re-run after any change under lib/ or cli.ts.
set -e
cd "$(dirname "$0")"
bun build cli.ts --target=node --format=esm --outfile=dist/converter.mjs
cat cli.ts $(find lib -name '*.ts' | sort) | shasum -a 256 | cut -d' ' -f1 > dist/converter.sources.sha256
echo "dist/converter.mjs: $(wc -c < dist/converter.mjs) bytes"
```

Run: `sh tools/circuit-to-wokwi/bundle.sh` — Expected: `dist/converter.mjs: <N> bytes`.

- [ ] **Step 2: Write the failing tests** — in `tests/test_check_spine.py`:

```python
class TheConverterShipsAsOneFileTest(unittest.TestCase):
    """B10: an installed spark has no node_modules in tools/circuit-to-wokwi, so the converter ships built."""

    BUNDLE = ROOT / "tools" / "circuit-to-wokwi" / "dist" / "converter.mjs"

    def test_the_bundle_is_built_from_the_sources_as_they_are(self):
        import hashlib
        folder = ROOT / "tools" / "circuit-to-wokwi"
        sources = [folder / "cli.ts"] + sorted((folder / "lib").rglob("*.ts"))
        digest = hashlib.sha256(b"".join(path.read_bytes() for path in sources)).hexdigest()
        self.assertEqual((folder / "dist" / "converter.sources.sha256").read_text().strip(), digest,
                         "the converter changed and the bundle was not rebuilt: sh tools/circuit-to-wokwi/bundle.sh")

    def test_the_bundle_runs_on_node_with_no_node_modules(self):
        import shutil, subprocess, tempfile
        if not shutil.which("node"):
            self.skipTest("node is not installed")
        alone = Path(tempfile.mkdtemp()) / "converter.mjs"
        shutil.copy(self.BUNDLE, alone)
        done = subprocess.run(["node", str(alone), "--help"], capture_output=True, text=True, timeout=60)
        self.assertNotIn("Cannot find package", done.stdout + done.stderr)

    def test_no_node_means_could_not_run_naming_the_install(self):
        import tools
        with mock.patch.object(tools, "find", side_effect=tools.ToolProblem("node (node) is not installed — install: brew install node")):
            stage = check_spine.converter_stage_problem(Path(tempfile.mkdtemp()))
        self.assertEqual(stage.status, check_spine.COULD_NOT_RUN)
        self.assertIn("brew install node", stage.detail)
```

(`ROOT`, `mock`, `tempfile`, `Path` are already imported in `test_check_spine.py`; check with `/usr/bin/grep -n "^import\|^from" tests/test_check_spine.py`.)

- [ ] **Step 3: Run them — they fail** (no `converter.sources.sha256` until Step 1 ran; no `converter_stage_problem`). Run: `python3 -m unittest tests.test_check_spine.TheConverterShipsAsOneFileTest 2>&1 | tail -3`.

- [ ] **Step 4: The entries** — in `data/tools.json`:

```json
  "roles": {"pdf-text": "pdftotext", "simulator": "wokwi-cli", "board-engine": "tscircuit", "diagram-converter": "circuit-to-wokwi"},
  "contracts": {"pdf-text": "page-text", "simulator": "wokwi-project", "board-engine": "tscircuit-board", "diagram-converter": "circuit-json-to-wokwi"},
  "circuit-to-wokwi": {
    "for": "turning the built board into a Wokwi diagram",
    "kind": "bundled",
    "file": "tools/circuit-to-wokwi/dist/converter.mjs",
    "needs": ["node"],
    "meets": ["circuit-json-to-wokwi"]
  },
  "node": {
    "for": "running the bundled converter and npm tools",
    "kind": "path",
    "exe": "node",
    "version": "20",
    "install": {"brew": "brew install node"}
  }
```

- [ ] **Step 5: Run the converter on Node** — in `scripts/check_spine.py`, replace the bun check and the `["bun", "run", ...]` call:

```python
def converter_stage_problem(project):
    """None when the converter and Node are both here; else the could-not-run Stage saying which and how to install it."""
    try:
        tools.find("node", project)
        tools.find("diagram-converter", project)
    except tools.ToolProblem as missing:
        return Stage("simulation", COULD_NOT_RUN, str(missing))
    return None
```

and in the simulation stage:

```python
    converter = find_converter(project)
    missing = converter_stage_problem(project)
    if converter is None or missing:
        return stages + [missing or Stage("simulation", COULD_NOT_RUN, "no circuit-to-wokwi converter found")]
    # (the lines from `loaded = design.load(...)` to `diagram_path = sim_dir / "diagram.json"` stay as they are)
    runner = (["bun", "run"] if converter.suffix == ".ts" else tools.find("node", project).command)
    made = subprocess.run(
        runner + [str(converter), "--circuit", str(circuit_path), "--out", str(diagram_path),
                  "--mapping", str(sim_dir / "wokwi-mapping.json"), "--chips", str(sim_dir / "chips")],
        cwd=str(converter.parent), capture_output=True, text=True, timeout=BUILD_TIMEOUT_S,
        env=dict(os.environ, SPARK_BOARD_JSON=str(sim_dir / "board.json")))
```

`PLUGIN_CONVERTER` becomes `SCRIPTS.parent / "tools" / "circuit-to-wokwi" / "dist" / "converter.mjs"`; `find_converter` keeps a project's own `cli.ts` first (development). The `["bun", "run"]` branch stays only for a project's own TypeScript converter and is the one place `"bun"` remains: keep `{"check_spine.py": {"bun"}}` in `NOT_YET_MOVED` **with a one-line reason comment** ("a project's own TypeScript converter, for its developer"), and update `test_every_script_still_allowed_to_name_a_tool_still_does` expectations accordingly.

- [ ] **Step 6: Run the full suite — green**, including `TheConvertersOwnSuiteTest` (bun, development) and the documented example (`test_routes`): Run `python3 -m unittest discover -s tests -t tests 2>&1 | tail -3` — Expected: `OK`.

- [ ] **Step 7: Prove B10 is gone** — a fresh clone without `node_modules`:

```bash
D=$(mktemp -d); git clone -q . "$D/spark" && cd "$D/spark" && python3 -m unittest tests.test_check_spine tests.test_converter 2>&1 | tail -3
```

Expected: `OK` — the three converter tests that failed in a fresh clone on 2026-10-03 ("Cannot find package 'circuit-json'") now pass or skip only for a missing `bun` used by the converter's own development suite.

- [ ] **Step 8: Mutation table** — `tests/mutations/sprint-10-p82-4.json`:

```json
[
 {"file": "scripts/check_spine.py", "name": "the simulation runs without asking for Node",
  "find": "        tools.find(\"node\", project)\n", "replace": ""},
 {"file": "scripts/check_spine.py", "name": "a missing Node is a crash, not could-not-run",
  "find": "        return Stage(\"simulation\", COULD_NOT_RUN, str(missing))", "replace": "        raise missing"}
]
```

Run it — both `[caught ]`.

- [ ] **Step 9: Commit** — `git commit -m "P82, task 4 / B10: the converter ships as one file that runs on Node — no bun, no node_modules"` (with the files above, including `dist/`).

---

### Task 5: littlefs and the MicroPython build from the list (`flash_image.py`)

**Files:**
- Modify: `data/tools.json`, `scripts/flash_image.py:41-43,66-80`, `tests/test_flash_image.py`
- Create: `tests/mutations/sprint-10-p82-5.json`

**Interfaces:**
- Consumes: `tools.find("littlefs")`, `tools.find("firmware-image")`, `tools.DOWNLOADS`.
- Produces: `flash_image.py --micropython` becomes optional; without it, the `firmware-image` tool's downloaded file is used.

- [ ] **Step 1: Find the build spark measured on** — the bin's simulation uses a MicroPython file; take its checksum and match it to micropython.org's page for the ESP32-S3:

```bash
find ~/Development/smartbin-local/firmware/micropython/sim -name '*.bin' -size +1M | head -3
shasum -a 256 <that file>
```

Open `https://micropython.org/download/ESP32_GENERIC_S3/`, find the release whose file has that checksum, and note its exact URL and file name. If none matches, use the newest stable release's URL and checksum, and say so in the entry's `note`.

- [ ] **Step 2: The entries** — in `data/tools.json` (fill `url`, `file`, `sha256` from Step 1):

```json
  "roles": {"pdf-text": "pdftotext", "simulator": "wokwi-cli", "board-engine": "tscircuit",
            "diagram-converter": "circuit-to-wokwi", "littlefs": "littlefs-python", "firmware-image": "micropython-esp32s3"},
  "contracts": {"pdf-text": "page-text", "simulator": "wokwi-project", "board-engine": "tscircuit-board",
                "diagram-converter": "circuit-json-to-wokwi", "littlefs": "esp32-littlefs", "firmware-image": "micropython-esp32-bin"},
  "littlefs-python": {
    "for": "packing the firmware's files into the flash image",
    "kind": "python",
    "module": "littlefs",
    "meets": ["esp32-littlefs"],
    "install": {"pip": "python3 -m pip install --user littlefs-python"}
  },
  "micropython-esp32s3": {
    "for": "the interpreter the flash image starts with, for an ESP32-S3",
    "kind": "download",
    "file": "<file from step 1>",
    "url": "<url from step 1>",
    "sha256": "<sha256 from step 1>",
    "meets": ["micropython-esp32-bin"],
    "install": {"download": "download into ~/.local/share/spark/downloads"}
  }
```

- [ ] **Step 3: Write the failing tests** — in `tests/test_flash_image.py`:

```python
class TheInterpreterComesFromTheToolsListTest(unittest.TestCase):
    def test_without_micropython_the_list_s_download_is_used(self):
        import tools
        found = tools.Tool("micropython-esp32s3", "firmware-image", {}, ["/downloads/mp.bin"])
        with mock.patch.object(tools, "find", return_value=found) as asked:
            self.assertEqual(flash_image.interpreter_path(None), Path("/downloads/mp.bin"))
        self.assertEqual(asked.call_args[0][0], "firmware-image")

    def test_no_littlefs_is_could_not_run_with_its_install(self):
        import tools
        with mock.patch.object(tools, "find", side_effect=tools.ToolProblem("littlefs (littlefs-python) is not installed — install: python3 -m pip install --user littlefs-python")):
            with contextlib.redirect_stderr(io.StringIO()) as err:
                code = flash_image.main(["--files", tempfile.mkdtemp(), "-o", str(Path(tempfile.mkdtemp()) / "out.bin")])
        self.assertEqual(code, flash_image.EXIT_COULD_NOT_RUN)
        self.assertIn("pip install --user littlefs-python", err.getvalue())
```

(add `import contextlib, io` if missing). Run — FAIL.

- [ ] **Step 4: Implement** — in `scripts/flash_image.py`:

```python
import tools  # noqa: E402


def interpreter_path(given):
    """The MicroPython build: the one given, else the tools list's download."""
    if given:
        return Path(given)
    return Path(tools.find("firmware-image").command[0])
```

`main`: `--micropython` gets `required=False`; before building:

```python
    try:
        tools.find("littlefs")
        interpreter = interpreter_path(args.micropython)
    except tools.ToolProblem as missing:
        print("flash_image.py: %s" % missing, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
```

and use `interpreter` wherever `args.micropython` was read.

- [ ] **Step 5: Run the full suite — green.** Expected `OK`.

- [ ] **Step 6: Mutation table** — `tests/mutations/sprint-10-p82-5.json`:

```json
[
 {"file": "scripts/flash_image.py", "name": "the list's MicroPython build is not used",
  "find": "    return Path(tools.find(\"firmware-image\").command[0])", "replace": "    return Path(\"micropython.bin\")"},
 {"file": "scripts/flash_image.py", "name": "a missing littlefs is a traceback again",
  "find": "        tools.find(\"littlefs\")\n", "replace": ""}
]
```

Run it — both `[caught ]`.

- [ ] **Step 7: Commit** — `git commit -m "P82, task 5: littlefs and the MicroPython build come from the tools list; the build is a checked download"`.

---

### Task 6: `/spark:setup` — status, install with one yes, and the choices

**Files:**
- Modify: `scripts/tools.py` (the CLI), `data/tools.json` (the MCP entries), `tests/test_tools.py`
- Create: `commands/setup.md`, `tests/mutations/sprint-10-p82-6.json`
- Modify: `README.md` (Install), `docs/mcp.md`, `commands/build.md` (the "one command" text: it needs the board engine — run `/spark:setup` first)

**Interfaces:**
- Consumes: everything above.
- Produces: `tools.status(project, personal) -> list[(state, role_or_name, text)]` with state in `"ok" | "missing" | "off" | "person"`; `tools.install(names, project, personal, run=subprocess.run) -> list[str]` (the commands it ran); `tools.choose(field_path, value, where) -> Path` (writes one field); CLI `tools.py --status|--install NAME...|--on NAME|--off NAME|--use ROLE=TOOL|--pin NAME=VERSION [--project DIR] [--personal]`.

- [ ] **Step 1: The MCP entries** — in `data/tools.json`:

```json
  "jlcpcb": {"for": "finding parts with a datasheet link", "kind": "mcp", "owner": "spark", "meets": ["candidates-with-datasheet"]},
  "espressif-docs": {"for": "searching Espressif's documentation", "kind": "mcp", "owner": "spark", "needs": ["node"], "meets": ["maker-docs-search"]},
  "wokwi-mcp": {"for": "driving a simulation interactively (paid minutes)", "kind": "mcp", "on": false,
                "mcp": {"command": "wokwi-cli", "args": ["mcp"]}, "needs": ["wokwi-cli"]},
  "sigrok": {"for": "reading a logic analyzer at the bench", "kind": "mcp", "on": false,
             "mcp": {"command": "sigrok-mcp-server"}, "needs": ["sigrok-cli"],
             "install": {"brew": "brew install sigrok-cli"}, "needs_hardware": "the instrument plugged into this machine"}
```

with roles `"parts-search": "jlcpcb", "chip-docs": "espressif-docs", "bench": "sigrok"`.

- [ ] **Step 2: Write the failing tests** — in `tests/test_tools.py`:

```python
class SetupTest(unittest.TestCase):
    def setUp(self):
        defaults = dict(DEFAULTS, **{"sigrok": {"kind": "mcp", "on": False, "mcp": {"command": "sigrok-mcp-server"}},
                                     "roles": {"pdf-text": "pdftotext", "bench": "sigrok"}})
        patcher = mock.patch.object(tools, "DEFAULTS", layer(defaults))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.personal = Path(tempfile.mkdtemp()) / "spark" / "tools.json"

    def test_status_says_ok_missing_and_off(self):
        with mock.patch.object(tools.shutil, "which", side_effect=lambda exe: None if exe == "pdftotext" else "/usr/bin/" + exe):
            states = {name: state for state, name, _ in tools.status(None, self.personal)}
        self.assertEqual(states["pdf-text"], "missing")
        self.assertEqual(states["bench"], "off")

    def test_install_runs_each_missing_tool_s_line_and_never_sudo(self):
        ran = []
        with mock.patch.object(tools.shutil, "which", side_effect=lambda exe: None if exe == "pdftotext" else "/usr/bin/" + exe):
            tools.install(["pdftotext"], None, self.personal, run=lambda argv, **kw: ran.append(argv))
        self.assertEqual(ran, [["brew", "install", "poppler"]])
        self.assertFalse(any("sudo" in part for argv in ran for part in argv))

    def test_turning_on_writes_one_field_and_creates_the_folder(self):
        tools.choose(["sigrok", "on"], True, self.personal)
        self.assertEqual(json.loads(self.personal.read_text()), {"sigrok": {"on": True}})

    def test_use_refuses_a_tool_that_does_not_meet_the_contract(self):
        with self.assertRaises(tools.ToolProblem):
            tools.use("pdf-text", "mystery", None, self.personal)
        self.assertFalse(self.personal.exists(), "nothing written for a refused swap")
```

Run — FAIL (no `status`, `install`, `choose`, `use`).

- [ ] **Step 3: Implement in `scripts/tools.py`**:

```python
def status(project=None, personal=None):
    """(state, role or name, what to say) for every role and every MCP entry — the picture /spark:setup shows."""
    lists = merged(project, personal)
    rows = []
    for role, name in sorted(lists["roles"].items()):
        entry = lists["tools"].get(name, {})
        if entry.get("on") is False:
            rows.append(("off", role, "%s — turn on: /spark:setup add %s" % (name, name)))
            continue
        if entry.get("kind") == "mcp":
            rows.append(("ok", role, "%s (MCP%s)" % (name, ", spark's own" if entry.get("owner") == "spark" else "")))
            continue
        try:
            found = find(role, project, personal)
            rows.append(("ok", role, "%s — %s" % (name, " ".join(found.command))))
        except ToolProblem as missing:
            rows.append(("missing", role, str(missing)))
        for needs_key in ("needs_account", "needs_hardware"):
            if entry.get(needs_key):
                rows.append(("person", role, entry[needs_key]))
    return rows


def install(names, project=None, personal=None, run=None):
    """Run each named tool's install line (never sudo); return the commands run. MCP entries register with Claude Code."""
    import shlex
    import subprocess
    run = run or (lambda argv, **kw: subprocess.run(argv, check=True, **kw))
    lists = merged(project, personal)
    ran = []
    for name in names:
        entry = lists["tools"][name]
        if entry.get("kind") == "mcp" and entry.get("mcp"):
            argv = ["claude", "mcp", "add", "--scope", "project" if project else "user", name, "--",
                    entry["mcp"]["command"]] + list(entry["mcp"].get("args") or [])
        elif entry.get("kind") == "download":
            DOWNLOADS.mkdir(parents=True, exist_ok=True)
            argv = ["curl", "-fsSL", "-o", str(DOWNLOADS / entry["file"]), entry["url"]]
        else:
            line = install_line(entry)
            if not line:
                continue
            argv = shlex.split(line)
        if "sudo" in argv:
            continue
        run(argv, cwd=str(project) if project else None)
        ran.append(argv)
        if entry.get("kind") == "download":
            verify_download(entry)
    return ran


def verify_download(entry):
    """A downloaded file must have the checksum its entry states; otherwise it is deleted and named."""
    import hashlib
    path = DOWNLOADS / entry["file"]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != entry.get("sha256"):
        path.unlink()
        raise ToolProblem("%s: the download's checksum %s is not the %s its entry states — deleted"
                          % (entry["file"], digest[:12], str(entry.get("sha256"))[:12]))


def choose(field_path, value, where):
    """Write one field (`["sigrok", "on"]` → true) into a tools file, keeping everything else in it."""
    where = Path(where)
    data = _read(where)
    node = data
    for key in field_path[:-1]:
        node = node.setdefault(key, {})
    node[field_path[-1]] = value
    where.parent.mkdir(parents=True, exist_ok=True)
    where.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return where


def use(role, tool_name, project=None, personal=None):
    """Point a role at another tool — refused before anything is written if the tool does not meet the role's contract."""
    lists = merged(project, personal)
    entry = lists["tools"].get(tool_name)
    contract = lists["contracts"].get(role)
    if entry is None or (contract and contract not in (entry.get("meets") or [])):
        raise ToolProblem("%s: %s does not say it meets %r, so this step will not use it" % (role, tool_name, contract))
    return choose(["roles", role], tool_name, Path(project) / PROJECT_FILE if project else (personal or PERSONAL))
```

and `main(argv=None)` with `argparse` for the six subcommands, printing `status` as `  [ok  ] role  text` / `[????]` / `[off ]` / `[!   ]`, exiting `EXIT_OK` when nothing is missing, else `EXIT_COULD_NOT_RUN`. `--on NAME` = `choose([NAME, "on"], True, …)` then `install([NAME], …)`; `--off NAME` writes `False` and, for an MCP entry, runs `claude mcp remove NAME --scope …`.

- [ ] **Step 4: `commands/setup.md`**:

```markdown
---
description: Show which tools spark needs and which are missing, and install them with one yes; turn integrations on or off, pin a version, swap a tool.
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/tools.py *)
---

# spark:setup

1. Show the picture: `${CLAUDE_PLUGIN_ROOT}/scripts/tools.py --status --project .`
2. If anything reads `[????]`, list those to the person and ask **once**: install them now? With a yes:
   `${CLAUDE_PLUGIN_ROOT}/scripts/tools.py --install <names…> --project .` — never with `sudo`; a line that
   needs it, an account (`[!]`) or hardware is told to the person, not run.
3. Choices the person asks for — `add sigrok`, `remove sigrok`, `use simulator=<tool>`, `pin tscircuit=<version>`
   — are `--on`, `--off`, `--use`, `--pin`; a personal choice by default, `--project` for this design.
4. After an MCP server was added or removed, say that Claude Code loads servers when a session starts.

Any other spark command that reports a missing tool (`… is not installed — install: …`) is answered the same
way: ask once, install with `--install`, and carry on with the step.
```

- [ ] **Step 5: Run the full suite — green**; `test_orphans` now finds `tools.py` routed from `commands/setup.md`.

- [ ] **Step 6: Mutation table** — `tests/mutations/sprint-10-p82-6.json`:

```json
[
 {"file": "scripts/tools.py", "name": "a command with sudo is run",
  "find": "        if \"sudo\" in argv:\n            continue", "replace": ""},
 {"file": "scripts/tools.py", "name": "a swap that breaks the contract is written anyway",
  "find": "    if entry is None or (contract and contract not in (entry.get(\"meets\") or [])):", "replace": "    if False:"},
 {"file": "scripts/tools.py", "name": "a choice overwrites the whole file",
  "find": "    data = _read(where)\n", "replace": "    data = {}\n"},
 {"file": "scripts/tools.py", "name": "an off integration reads as ok",
  "find": "            rows.append((\"off\", role,", "replace": "            rows.append((\"ok\", role,"}
]
```

Run it — every `[caught ]`. (For "a choice overwrites the whole file", add first a test that writes two choices and reads both back, if none catches it.)

- [ ] **Step 7: Docs** — `commands/build.md` and `commands/research.md` each gain, where they say what
to do when a step reports a problem: *"A line `… is not installed — install: …` is answered by asking the
person once and running `${CLAUDE_PLUGIN_ROOT}/scripts/tools.py --install <name> --project .`, then running
the step again"* (spec section 2, "installed on the spot"). `README.md`'s Install section: after `/plugin install spark`, "then `/spark:setup` — it shows what spark needs and installs what is missing with one yes". `docs/mcp.md`: replace the hand-written commands with "`/spark:setup add wokwi-mcp` / `add sigrok`", keeping what was checked on 2026-10-03. `commands/build.md`: the "one command" line says it needs the board engine and points at `/spark:setup`; remove "the one command needs neither".

- [ ] **Step 8: Commit** — `git commit -m "P82, task 6: /spark:setup — the picture, one yes to install, and the choices that write one line"`.

---

### Task 7: The proof (P82's acceptance line)

**Files:** none changed unless the run finds a defect; then a new failing test and its fix, in this task.

- [ ] **Step 1: The cold run** — a machine state no earlier step touched:

```bash
export SPARK_COLD=$(mktemp -d)
export CLAUDE_CONFIG_DIR="$SPARK_COLD/claude"
cd "$SPARK_COLD" && git clone -q https://github.com/xmejkal/spark.git && mkdir project && cd project
python3 ../spark/scripts/tools.py --status --project .
```

Expected: `[????]` lines for what this machine lacks (none if everything is installed globally — then also run with `PATH` reduced to `/usr/bin:/bin:$(dirname $(which python3)):$(dirname $(which node))` to make `tsci` missing).

- [ ] **Step 2: One install, then the chain**

```bash
python3 ../spark/scripts/init_project.py --project . --board firebeetle2-esp32s3
python3 ../spark/scripts/tools.py --install tscircuit --project .
# the documented example's requirements, from commands/build.md
python3 ../spark/scripts/check_spine.py requirements.json --keep .
```

Expected: the last line `the chain runs end to end`, with no install command typed beyond `--install`.

- [ ] **Step 3: Record it** — in `scrum/PRODUCT_BACKLOG.md`, P82 gets `— DONE <date>` and a **Done** paragraph quoting the run's last lines (W13: numbers from the output shown); B10 gets `— DONE <date>` pointing at Task 4. `scrum/STORY_MAP.md` slice 1 shows P82 and B10 done. Commit: `git commit -m "P82 done: from an empty Claude config, /spark:setup then /spark:build run end to end"`.
