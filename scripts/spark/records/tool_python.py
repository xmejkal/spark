"""
The tool's Python (P1264): the Python that holds a Python tool's module, when it is not the Python that runs spark.

A person installs mpremote or esptool with their shell's `pip`, so the module is in the Python that the shell's
`mpremote` runs, and spark may run in another. `ToolPythonFinder.find` looks for the entry's `exe` on the PATH, asks the
Python that the executable's first line names, then the `python3` beside it (a pyenv shim), and keeps the answer. One
child asks each Python, started as a run starts it, in the same folder and environment and without `-I`.
`tool_finder.locate` and `versions.installed_release` read the one instance `TOOL_PYTHONS` and nothing else imports this.
"""

import json
import os
import shlex
import shutil
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

from spark.records import store

#: The seconds one child may take to answer. A pyenv shim takes about half a second.
PROBE_TIMEOUT_S = 20

#: What each child runs: the module is found without importing it. Exit 3 says there is no such module. The first line
#: leaves the start folder off `sys.path`, as `-I` would, but the user site stays on, so the child sees what the run sees.
PROBE = """import sys; del sys.path[0]  # the folder the child starts in: a json.py there must not run
import importlib.metadata, importlib.util, json
if importlib.util.find_spec(sys.argv[1]) is None:
    sys.exit(3)
try:
    release = importlib.metadata.version(sys.argv[1])
except importlib.metadata.PackageNotFoundError:
    release = None
print(json.dumps([sys.executable, release]))
"""

#: The words that /spark:setup keys on: the tool is on the PATH, and no Python spark can use holds its module (P1264, C3).
NO_PYTHON_HOLDS_IT = "but no Python spark asked holds its module"
#: The words of a Python that spark could not ask: a could-not-run, never a "holds no module" (learned rule 2.1).
CANNOT_ASK = "Spark cannot ask"
# The start of a Python tool's install line in data/tools.json: the step to copy runs it with the tool's own Python.
PIP_USER_INSTALL = "python3 -m pip install --user "
#: The script a step to copy runs, by its whole path (`tools.py` beside the `spark` package).
TOOLS_SCRIPT = Path(__file__).resolve().parents[2] / "tools.py"

#: The Python that holds the module (the child's own `sys.executable`, never a shim), its release or None, and the
#: executable on the PATH that it was found through.
ToolPython = namedtuple("ToolPython", "python release executable")


class ModuleReader:
    """Adapter: `probe(python, module)` asks one Python whether it holds a module, in one child process."""

    def __init__(self, run=None, timeout_s=PROBE_TIMEOUT_S):
        self.run, self.timeout_s = run, timeout_s

    def probe(self, python, module):
        """((interpreter, release), "") when `python` holds the module, (None, "") when it does not, and (None, why)
        when spark cannot ask it. A "why" is never read as "no module"."""
        try:
            done = (self.run or subprocess.run)([python, "-c", PROBE, module], capture_output=True, text=True,
                                                timeout=self.timeout_s)
        except subprocess.TimeoutExpired:
            return None, "did not answer in %d s" % self.timeout_s
        except OSError as cannot:
            return None, "cannot be started (%s)" % (cannot.strerror or cannot)
        if done.returncode == 3 and not done.stdout.strip():
            return None, ""
        try:
            interpreter, release = json.loads(done.stdout)
        except (ValueError, TypeError):
            return None, "gave an answer spark cannot read"
        return (interpreter, release), ""


def _first_line_python(executable):
    """The Python that an executable's first line names, when it is an absolute path of a Python, else None."""
    try:
        with open(executable, "rb") as script:
            first = script.read(300).split(b"\n")[0].decode("utf-8", "replace")
    except OSError:
        return None
    named = first[2:].split()[:1] if first.startswith("#!") else []
    if named and os.path.isabs(named[0]) and os.path.basename(named[0]).startswith("python") and os.path.isfile(named[0]):
        return named[0]
    return None


class ToolPythonFinder:
    """Adapter: `find(entry)` gives the ToolPython of an entry that names an `exe` on the PATH, or None. A found answer is
    kept for the process, a not-found one never, so a tool installed while spark runs is found at the next ask. A tool
    uninstalled while one process runs stays found until `install`'s `forget()` or the next process.
    `which` and `reader` are looked up when used, so a test sees what it set."""

    def __init__(self, reader=None, which=None):
        self.reader, self.which = reader, which
        self.kept, self.tried = {}, {}

    def forget(self):
        """Drop what was kept, after an install."""
        self.kept.clear()
        self.tried.clear()

    def _executable(self, entry):
        """The executable on the PATH that the entry names, when it is a regular file, else None."""
        found = (self.which or shutil.which)(entry["exe"]) if self._asked(entry) else None
        return found if found and os.path.isfile(found) else None

    @staticmethod
    def _asked(entry):
        """Whether the entry is a Python tool that names an `exe` to look for."""
        return entry.get("kind") == "python" and bool(entry.get("exe")) and bool(entry.get("module"))

    def find(self, entry):
        executable = self._executable(entry)
        if executable is None:
            return None
        key = (executable, entry["module"])
        if key in self.kept:
            return self.kept[key]
        beside = os.path.join(os.path.dirname(executable), "python3")
        candidates = [path for path in dict.fromkeys([_first_line_python(executable), beside])
                      if path and os.path.isfile(path)]
        self.tried[key] = []
        for candidate in candidates:
            answer, why = (self.reader or ModuleReader()).probe(candidate, entry["module"])
            if answer:
                self.kept[key] = ToolPython(answer[0], answer[1], executable)
                return self.kept[key]
            self.tried[key].append((candidate, why))
        return None

    def looked(self, entry):
        """The sentence after an install line that says where spark looked, or '' for an entry with no `exe`."""
        if not self._asked(entry):
            return ""
        return ". Spark looked for the %s module in %s, the Python that runs spark, and for %s on the PATH." % (
            entry["module"], sys.executable, entry["exe"])

    def unusable(self, entry):
        """Whether the entry's executable is on the PATH although no Python holds its module (after `find` gave None)."""
        return self._executable(entry) is not None

    def on_path(self, entry, install_line, name=None, project=None):
        """The sentence for a tool that is on the PATH but in no Python spark can use, else ''. A Python that spark could
        not ask is said as that, with no install step. Else it ends with one step to copy: the install line run by the
        first Python that holds no module, or the line that turns the PATH lookup off for the tool `name`."""
        executable = self._executable(entry)
        if executable is None:
            return ""
        module = entry["module"]
        asked = self.tried.get((executable, module)) or []
        cannot, holds_none = [(path, why) for path, why in asked if why], [path for path, why in asked if not why]
        head = "%s is on your PATH (%s)" % (entry["exe"], executable)
        if cannot:
            lead = "%s. %s%s" % (head, " ".join("%s %s: %s." % (CANNOT_ASK, path, why) for path, why in cannot),
                                 "".join(" %s holds no %s module." % (path, module) for path in holds_none))
        else:
            lead = "%s, %s: %s." % (head, NO_PYTHON_HOLDS_IT, ", ".join("%s holds no %s module" % (path, module) for path in holds_none)
                                    or "none could be asked")
        line = install_line.split(" \u2014 needs ")[0]  # the hint's ending is for a person, not for the shell
        if holds_none and line.startswith(PIP_USER_INSTALL):
            return "%s Copy this step: %s %s" % (lead, shlex.quote(holds_none[0]), line[len("python3 "):])
        if cannot:
            return lead
        return "%s Copy this step: %s" % (lead, store.format_rerun_line(
            TOOLS_SCRIPT, (["--project", project] if project else []) + ["--pin", "%s.exe=" % (name or module)]))

    def row(self, name, entry, command):
        """The setup report's words for a tool found through the PATH, or '' when the running Python holds it."""
        found = self.find(entry) if command != [sys.executable] else None
        if found is None:
            return ""
        return "%s %s, runs with %s (found through %s)" % (name, found.release or "(unknown version)", found.python,
                                                           found.executable)


#: The one finder that `tool_finder` and `versions` read.
TOOL_PYTHONS = ToolPythonFinder()
