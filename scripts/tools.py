#!/usr/bin/env python3
"""
The tools spark depends on, found from one merged list (P82, docs/2026-10-03-tools-design.md).

spark's dependencies were decided in seven places, each with its own lookup and its own error
message. Now one list says what each tool is for, how to find it, how to install it and which
contract it meets: spark's defaults in data/tools.json, the person's in
~/.local/share/spark/tools.json, the project's in .spark/tools.json — merged entry by entry and
field by field, the project winning. Every script asks `find`; nothing else names a tool.

A missing tool is a ToolProblem whose sentence says what installs it. Only `install` installs, and
only for /spark:setup once the person has said yes; it never runs `sudo`. As a command, this is what
/spark:setup runs:

    tools.py --status [--project DIR]                  the picture: [ok  ] [????] [off ] [!   ]
    tools.py --install NAME... [--project DIR]         install the named tools, their needs first
    tools.py --on NAME | --off NAME                    turn an integration on (and install it) or off
    tools.py --use ROLE=TOOL | --pin NAME=VERSION      point a job at another tool; pin a version

A choice is written to the person's file, or to the project's with --project (--personal overrides).
(Not to be confused with the repository's `tools/` folder, which holds the developers' own tools.)
"""

import argparse
import importlib.util
import json
import os
import platform
import shutil
import string
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import boards  # noqa: E402
import store  # noqa: E402
from outcomes import EXIT_OK, EXIT_COULD_NOT_RUN  # noqa: E402

PLUGIN = SCRIPTS.parent
DEFAULTS = PLUGIN / "data" / "tools.json"
#: The person's tools list and downloads, in their store. Read once, when the process starts — which for a
#: command is the moment it is asked — and a module constant, so a test can point them elsewhere.
PERSONAL = store.place("tools")
DOWNLOADS = store.place("downloads")
PROJECT_FILE = Path(".spark") / "tools.json"
#: Keys of a tools file that are not tools.
RESERVED = ("roles", "contracts")
#: The install managers tried in order, each with the program that has to be there for it to apply.
#: apt comes last and its lines carry sudo, so they are shown to the person and never run.
MANAGERS = (("npm", "npm"), ("pip", "python3"), ("brew", "brew"), ("download", None), ("apt", "apt-get"))

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
        if not isinstance(data.get("roles") or {}, dict):
            raise ToolProblem("%s: `roles` is not an object — it maps a job to a tool, e.g. {\"pdf-text\": \"pdftotext\"}" % path)
        lists["roles"].update(data.get("roles") or {})
        if path == DEFAULTS:
            lists["contracts"].update(data.get("contracts") or {})
    return lists


def _filled(line, entry):
    """An install line with {version} and {core} filled from the entry; any other placeholder is the entry's fault."""
    try:
        return line.format(version=entry.get("version", ""), core=entry.get("core", ""))
    except (KeyError, IndexError, ValueError) as unknown:
        raise ToolProblem("the install line %r names %s; only {version} and {core} are filled" % (line, unknown))


def install_line(entry):
    """The one command that installs this tool here, with its version filled in — or None."""
    install = entry.get("install") or {}
    for manager, needs in MANAGERS:
        if manager in install and (needs is None or shutil.which(needs)):
            return _filled(install[manager], entry)
    return None


#: What a person needs before a manager's line can run, said when none is here.
FIRST = {"npm": "Node (nodejs.org)", "pip": "Python 3", "brew": "Homebrew (brew.sh)", "apt": "a Debian or Ubuntu system"}


def install_hint(entry):
    """The line to tell a person: the one that runs here, else the first one listed with what it needs first."""
    line = install_line(entry)
    if line:
        return line
    install = entry.get("install") or {}
    for manager, _ in MANAGERS:
        if manager in install:
            return "%s — needs %s first" % (_filled(install[manager], entry), FIRST[manager])
    return None


def platform_key():
    """This machine as a build is named in a `fetch` block: macos-arm64, macos-x64, linux-x64, linux-arm64 — or None."""
    system = {"Darwin": "macos", "Linux": "linux"}.get(platform.system())
    machine = {"x86_64": "x64", "amd64": "x64", "arm64": "arm64", "aarch64": "arm64"}.get(platform.machine().lower())
    return "%s-%s" % (system, machine) if system and machine else None


def fetch_of(entry):
    """(file, url, sha256, executable) of what spark downloads for this tool here, or None when it downloads nothing.

    A `download` entry is one file for every machine (the MicroPython build); a `fetch` block names one
    build per platform (wokwi-cli, whose releases are a binary each). No build for this machine is a ToolProblem.
    """
    if entry.get("kind") == "download":
        return entry["file"], entry["url"], entry["sha256"], bool(entry.get("executable"))
    fetch = entry.get("fetch")
    if not fetch:
        return None
    build = fetch["platforms"].get(platform_key())
    if not build:
        raise ToolProblem("there is no build of it for %s — its list has %s"
                          % (platform_key() or "this machine", ", ".join(sorted(fetch["platforms"]))))
    return fetch["file"], build["url"], build["sha256"], bool(fetch.get("executable"))


def locate(entry, project):
    """The command that runs this tool, by its kind — or None when it is not here."""
    kind = entry.get("kind", "path")
    if kind == "mcp":
        return None  # Claude Code runs a server; spark has no command for it
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
        for directory in boards.walk_up(Path(project).absolute()):
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
    if entry.get("fetch"):
        path = DOWNLOADS / entry["fetch"]["file"]
        if path.is_file() and os.access(str(path), os.X_OK):
            return [str(path)]
    return None


def installed_versions(entry, command):
    """{field: version} of an npm tool's packages as installed beside the command found ({} when not from node_modules)."""
    packages = entry.get("packages") or {}
    bin_dir = Path(command[0]).parent if command else None
    if not packages or bin_dir is None or bin_dir.name != ".bin" or bin_dir.parent.name != "node_modules":
        return {}
    found = {}
    for field, package in packages.items():
        try:
            found[field] = json.loads((bin_dir.parent / package / "package.json").read_text()).get("version")
        except (OSError, ValueError):
            found[field] = None
    return found


def pin_differences(entry, command):
    """[(field, installed, pinned)] for each package whose installed version is not the one the list pins."""
    return [(field, here, entry.get(field)) for field, here in installed_versions(entry, command).items()
            if entry.get(field) and here != entry.get(field)]


def version_note(name, reported, field="version", project=None, personal=None):
    """'' when the reported version is the one the list states for this field, else the one line to print."""
    stated = merged(project, personal)["tools"].get(name, {}).get(field)
    if not stated or reported in (None, "unknown version") or str(reported) == str(stated):
        return ""
    return "; spark was measured on %s %s %s" % (name, field, stated)


def setter_of(tool_name, field, project=None, personal=None):
    """The tools file whose value of this field wins, or None when no file sets it."""
    paths = [DEFAULTS, Path(personal) if personal else PERSONAL] + ([Path(project) / PROJECT_FILE] if project else [])
    found = None
    for path in paths:
        if field in (_read(path).get(tool_name) or {}):
            found = path
    return found


def off_sentence(tool_name, project=None, personal=None):
    """Why a tool is off and how to turn it on in the file that turned it off — a project's file wins over the person's."""
    setter = setter_of(tool_name, "on", project, personal)
    if project and setter == Path(project) / PROJECT_FILE:
        return ("%s is turned off in this project's .spark/tools.json — turn it on there: /spark:setup add %s --project ."
                % (tool_name, tool_name))
    if setter == DEFAULTS:
        return "%s is off unless you turn it on — /spark:setup add %s" % (tool_name, tool_name)
    return "%s is turned off in %s — turn it on: /spark:setup add %s" % (tool_name, setter, tool_name)


def find(name, project=None, personal=None, _seen=()):
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
    problem = entry_problem(entry)
    if problem:
        raise ToolProblem("%s: %s" % (tool_name, problem))
    if entry.get("on") is False:
        raise ToolProblem(off_sentence(tool_name, project, personal))
    if tool_name in _seen:
        raise ToolProblem("%s: its needs go round in a loop — %s" % (tool_name, " → ".join(_seen + (tool_name,))))
    for need in entry.get("needs") or []:
        try:
            find(need, project, personal, _seen + (tool_name,))
        except ToolProblem as inner:
            raise ToolProblem("%s needs %s: %s" % (tool_name, need, inner))
    command = locate(entry, project)
    if command is None:
        raise ToolProblem("%s (%s) is not installed — install: %s"
                          % (role or tool_name, tool_name, install_hint(entry) or "see its entry in %s" % DEFAULTS))
    return Tool(tool_name, role, entry, command)


def status(project=None, personal=None):
    """(state, role or name, what to say) for every role and every MCP entry — the picture /spark:setup shows.

    state is "ok", "missing", "off" or "person" (something only the person can do: an account, an instrument).
    """
    lists = merged(project, personal)
    rows = []
    named = sorted(lists["roles"].items())
    named += sorted((name, name) for name, entry in lists["tools"].items()
                    if entry.get("kind") == "mcp" and name not in lists["roles"].values())
    for label, name in named:
        entry = lists["tools"].get(name, {})
        if entry.get("on") is False:
            rows.append(("off", label, off_sentence(name, project, personal)))
            continue
        try:
            if entry.get("kind") == "mcp":
                for need in entry.get("needs") or []:
                    try:
                        find(need, project, personal)
                    except ToolProblem as inner:
                        raise ToolProblem("%s needs %s: %s" % (name, need, inner))
                rows.append(("ok", label, "%s (MCP%s)" % (name, ", spark's own" if entry.get("owner") == "spark" else "")))
            else:
                found = find(label, project, personal)
                notes = "".join("; %s %s here, the list pins %s — /spark:setup installs the pinned one"
                                % (field, here, pinned) for field, here, pinned in pin_differences(found.entry, found.command))
                rows.append(("ok", label, "%s — %s%s" % (name, " ".join(found.command), notes)))
        except ToolProblem as missing:
            rows.append(("missing", label, str(missing)))
        if entry.get("needs_account") and not os.environ.get(entry.get("account_env") or "", ""):
            rows.append(("person", label, "needs " + entry["needs_account"]))
        if entry.get("needs_hardware"):
            rows.append(("person", label, "needs " + entry["needs_hardware"]))
    return rows


def to_install(project=None, personal=None):
    """The tools /spark:setup would install: each missing tool or missing need of an entry that is on."""
    lists = merged(project, personal)
    names = []
    for name in list(lists["roles"].values()) + [n for n, e in lists["tools"].items() if e.get("kind") == "mcp"]:
        entry = lists["tools"].get(name, {})
        if entry.get("on") is False:
            continue
        for wanted in list(entry.get("needs") or []) + ([] if entry.get("kind") == "mcp" else [name]):
            want = lists["tools"].get(wanted)
            if want is None or entry_problem(want) or wanted in names:
                continue  # a broken entry is a row in the picture, not something to install
            if locate(want, project) is None:
                names.append(wanted)
    return names


def run_checked(argv, **kw):
    """How spark runs an install command: as given, failing loudly."""
    return subprocess.run(argv, check=True, **kw)


def plan(names, project=None, personal=None):
    """What installing these names would do, in order, needs first: [{name, argv, problem, fetch, from_project}].

    Nothing runs here, so /spark:setup can show every command — and which ones a project's own
    .spark/tools.json chose — before the person's yes.
    """
    import shlex
    lists = merged(project, personal)
    project_file = _read(Path(project) / PROJECT_FILE) if project else {}
    order = []
    for name in names:
        for wanted in list(lists["tools"].get(name, {}).get("needs") or []) + [name]:
            if wanted not in order:
                order.append(wanted)
    steps = []
    for name in order:
        step = {"name": name, "argv": None, "problem": None, "fetch": None, "from_project": name in project_file}
        steps.append(step)
        entry = lists["tools"].get(name)
        problem = "no tool called that in any tools file" if entry is None else entry_problem(entry)
        if problem:
            step["problem"] = "%s: %s" % (name, problem)
            continue
        try:
            if entry.get("kind") == "mcp":
                if not entry.get("mcp"):
                    steps.pop()  # spark's own: the plugin declares it
                    continue
                command = entry["mcp"]["command"]
                if command in lists["tools"] and not entry_problem(lists["tools"][command]) \
                        and locate(lists["tools"][command], project):
                    command = locate(lists["tools"][command], project)[0]
                step["argv"] = ["claude", "mcp", "add", "--scope", "project" if project else "user", name, "--",
                                command] + list(entry["mcp"].get("args") or [])
                continue
            here = locate(entry, project)
            if here is not None and not pin_differences(entry, here):
                steps.pop()  # already here, at the pinned version
                continue
            fetch = fetch_of(entry)
            if fetch:
                step["fetch"] = fetch
                step["argv"] = ["curl", "-fsSL", "-o", str(DOWNLOADS / (fetch[0] + ".part")), fetch[1]]
                continue
            line = install_line(entry)
            if not line:
                step["problem"] = "%s: no way to install it here — %s" % (name, install_hint(entry) or "see its entry in %s" % DEFAULTS)
                continue
            argv = shlex.split(line)
        except ToolProblem as unusable:
            step["problem"] = "%s: %s" % (name, unusable)
            continue
        if "sudo" in argv:
            step["problem"] = "%s needs sudo, which spark never runs — run it yourself: %s" % (name, " ".join(argv))
            continue
        step["argv"] = argv
    return steps


def install(names, project=None, personal=None, run=None):
    """Install each named tool that is not here (or not at its pin), its needs first; return the commands run. Never sudo.

    An MCP entry registers with Claude Code (user scope, or project scope for a project's choice). A download
    lands as `<file>.part`, is checked against its sha256, and only then takes its name. What cannot be
    done — a sudo line, a failed command, a wrong checksum — is raised at the end, after the rest.
    """
    run = run or run_checked
    ran, problems = [], []
    for step in plan(names, project, personal):
        if step["problem"]:
            problems.append(step["problem"])
            continue
        argv, fetch = step["argv"], step["fetch"]
        if fetch:
            DOWNLOADS.mkdir(parents=True, exist_ok=True)
        try:
            run(argv, cwd=str(project) if project else None)
        except (OSError, subprocess.CalledProcessError) as failed:
            problems.append("%s: `%s` failed (%s)" % (step["name"], " ".join(argv), failed))
            if fetch and (DOWNLOADS / (fetch[0] + ".part")).exists():
                (DOWNLOADS / (fetch[0] + ".part")).unlink()
            continue
        ran.append(argv)
        if fetch:
            try:
                settle_download(*fetch)
            except ToolProblem as wrong:
                problems.append(str(wrong))
    if problems:
        raise ToolProblem("\n".join(problems))
    return ran


def settle_download(file, url, sha256, executable=False):
    """`<file>.part` becomes `<file>` only when its checksum is the one the entry states; otherwise it is deleted and named."""
    import hashlib
    part = DOWNLOADS / (file + ".part")
    digest = hashlib.sha256(part.read_bytes()).hexdigest() if part.is_file() else "nothing"
    if digest != sha256:
        if part.exists():
            part.unlink()
        raise ToolProblem("%s: the download's checksum %s is not the %s its entry states — deleted"
                          % (file, digest[:12], str(sha256)[:12]))
    if executable:
        part.chmod(0o755)
    part.replace(DOWNLOADS / file)


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


#: What each kind of entry must say for spark to find or run it.
KIND_NEEDS = {"path": ("exe",), "npm": ("exe",), "python": ("module",), "download": ("file", "url", "sha256"),
              "bundled": ("file",), "mcp": ()}


def entry_problem(entry):
    """None for an entry spark can find and install from; else what it lacks, as the end of a sentence."""
    if not isinstance(entry, dict):
        return "an entry is a JSON object"
    kind = entry.get("kind", "path")
    if kind not in KIND_NEEDS:
        return "kind %r is not one of %s" % (kind, ", ".join(KIND_NEEDS))
    lacking = [field for field in KIND_NEEDS[kind] if not entry.get(field)]
    if kind == "mcp" and entry.get("owner") != "spark" and not (entry.get("mcp") or {}).get("command"):
        lacking.append("mcp.command")
    if lacking:
        return "no way to find it — a %s entry needs %s" % (kind, ", ".join(lacking))
    files = [entry["file"]] if kind == "download" else []
    fetch = entry.get("fetch")
    if fetch is not None:
        if not isinstance(fetch, dict) or not fetch.get("file") or not isinstance(fetch.get("platforms"), dict) \
                or not all(isinstance(b, dict) and b.get("url") and b.get("sha256") for b in fetch["platforms"].values()):
            return "its fetch block needs a file and, per platform, a url and a sha256"
        files.append(fetch["file"])
    for file in files:
        if not isinstance(file, str) or Path(file).name != file or file in (".", ".."):
            return "%r must be a plain file name — spark keeps every download in %s" % (file, DOWNLOADS)
    for manager, line in (entry.get("install") or {}).items():
        try:
            unknown = [field for _, field, _, _ in string.Formatter().parse(str(line)) if field not in (None, "version", "core")]
        except ValueError:
            unknown = ["a stray brace"]
        if unknown:
            return "its %s install line names {%s}; only {version} and {core} are filled" % (manager, unknown[0])
    return None


new_entry_problem = entry_problem  # what `--new` checks is what every step checks


MARKS = {"ok": "[ok  ]", "missing": "[????]", "off": "[off ]", "person": "[!   ]"}


def print_status(project, personal):
    """The picture, one row per line; returns how many rows read missing — a broken entry counts, though nothing installs it."""
    print("  spark's tools — personal: %s · project: %s\n"
          % (personal or PERSONAL, Path(project) / PROJECT_FILE if project else "(none)"))
    rows = status(project, personal)
    for state, label, text in rows:
        print("  %s %-17s %s" % (MARKS[state], label, text))
    missing = to_install(project, personal)
    if missing:
        print("\n  %d to install: %s" % (len(missing), " ".join(missing)))
    return sum(1 for state, _, _ in rows if state == "missing")


def main(argv=None, run=None):
    parser = argparse.ArgumentParser(prog="tools.py", description="The tools spark depends on: what is here, "
                                     "what is missing, and the choices — what /spark:setup runs.")
    does = parser.add_mutually_exclusive_group(required=True)
    does.add_argument("--status", action="store_true")
    does.add_argument("--install", nargs="+", metavar="NAME")
    does.add_argument("--on", metavar="NAME")
    does.add_argument("--off", metavar="NAME")
    does.add_argument("--use", metavar="ROLE=TOOL")
    does.add_argument("--pin", metavar="NAME[.FIELD]=VERSION", help="e.g. tscircuit.core=0.0.2700 (FIELD defaults to version)")
    does.add_argument("--new", metavar="NAME=JSON", help="describe a tool of your own, e.g. "
                      'my-sim=\'{"kind": "path", "exe": "my-sim", "meets": ["wokwi-project"]}\'')
    parser.add_argument("--project", type=Path, help="the project: read its .spark/tools.json, and write a choice there")
    parser.add_argument("--personal", action="store_true", help="write a choice to the person's file even with --project")
    parser.add_argument("--dry-run", action="store_true", help="with --install: print each command and run nothing")
    args = parser.parse_args(argv)
    project = args.project
    where = PERSONAL if (args.personal or not project) else Path(project) / PROJECT_FILE
    scope = "user" if where == PERSONAL else "project"
    try:
        if args.status:
            return EXIT_COULD_NOT_RUN if print_status(project, None) else EXIT_OK
        if args.install and args.dry_run:
            for step in plan(args.install, project, None):
                if step["problem"]:
                    print("  cannot:    %s" % step["problem"])
                else:
                    print("  would run: %s%s" % (" ".join(step["argv"]), "   ← chosen by this project's .spark/tools.json"
                                                 " — check it before you say yes" if step["from_project"] else ""))
                    if step["from_project"]:
                        print("             (from .spark/tools.json)")
        elif args.install:
            for argv_ran in install(args.install, project, None, run):
                print("  ran: %s" % " ".join(argv_ran))
        elif args.on:
            choose([args.on, "on"], True, where)
            if merged(project)["tools"].get(args.on, {}).get("on") is False:
                raise ToolProblem("%s is still off: %s" % (args.on, off_sentence(args.on, project)))
            for argv_ran in install([args.on], project if scope == "project" else None, None, run):
                print("  ran: %s" % " ".join(argv_ran))
            print("  %s is on (%s)" % (args.on, where))
        elif args.off:
            entry = merged(project)["tools"].get(args.off, {})
            choose([args.off, "on"], False, where)
            if entry.get("kind") == "mcp" and entry.get("mcp"):
                try:
                    (run or run_checked)(["claude", "mcp", "remove", "--scope", scope, args.off])
                except (OSError, subprocess.CalledProcessError):
                    print("  %s was not registered with Claude Code at %s scope — nothing to remove" % (args.off, scope))
            elif entry.get("owner") == "spark":
                print("  %s is spark's own server and stays loaded with the plugin — disable it in /mcp" % args.off)
            print("  %s is off (%s)" % (args.off, where))
        elif args.use:
            role, _, tool_name = args.use.partition("=")
            print("  %s → %s (%s)" % (role, tool_name, use(role, tool_name, project if scope == "project" else None,
                                                          None)))
        elif args.new:
            name, _, text = args.new.partition("=")
            try:
                entry = json.loads(text)
            except ValueError as broken:
                raise ToolProblem("%s: the entry is not JSON (%s)" % (name, broken))
            problem = new_entry_problem(entry)
            if problem:
                raise ToolProblem("%s: %s — nothing written" % (name, problem))
            print("  %s written (%s); point a job at it: /spark:setup use <role>=%s" % (name, choose([name], entry, where), name))
        elif args.pin:
            target, _, value = args.pin.partition("=")
            name, _, field = target.partition(".")
            written = choose([name, field or "version"], value, where)
            print("  %s %s pinned to %s (%s); to install it: tools.py --install %s%s"
                  % (name, field or "version", value, written, name, " --project %s" % project if project else ""))
    except ToolProblem as problem:
        print("tools.py: %s" % problem, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    if (args.on or args.off) and merged(project)["tools"].get(args.on or args.off, {}).get("kind") == "mcp":
        print("  Claude Code loads MCP servers when a session starts: restart it for this to take effect.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
