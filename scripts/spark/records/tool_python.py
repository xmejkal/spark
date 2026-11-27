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
import shutil
import subprocess
import sys
from collections import namedtuple

#: The seconds one child may take to answer. A pyenv shim takes about half a second.
PROBE_TIMEOUT_S = 20

#: What each child runs: the module is found without importing it. Exit 3 says there is no such module.
PROBE = """import importlib.metadata, importlib.util, json, sys
if importlib.util.find_spec(sys.argv[1]) is None:
    sys.exit(3)
try:
    release = importlib.metadata.version(sys.argv[1])
except importlib.metadata.PackageNotFoundError:
    release = None
print(json.dumps([sys.executable, release]))
"""

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
    kept for the process, a not-found one never, so a tool installed while spark runs is found at the next ask.
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

    def on_path(self, entry, install_line):
        """The sentence for a tool that is on the PATH but in no Python spark can use, else ''. It leads with that
        fact and ends with one step to copy: the install line run by the Python that holds the executable."""
        executable = self._executable(entry)
        if executable is None:
            return ""
        asked = self.tried.get((executable, entry["module"])) or []
        said = ", ".join("%s %s" % (path, why or "holds no %s module" % entry["module"]) for path, why in asked)
        step = "%s %s" % (asked[0][0], install_line[len("python3 "):]) \
            if asked and install_line.startswith("python3 -m pip install --user ") \
            else "tools.py --pin %s.exe=" % entry["module"]
        return "%s is on your PATH (%s), but no Python spark asked holds its module: %s. Copy this step: %s" % (
            entry["exe"], executable, said or "none could be asked", step)

    def row(self, name, entry, command):
        """The setup report's words for a tool found through the PATH, or '' when the running Python holds it."""
        found = self.find(entry) if command != [sys.executable] else None
        if found is None:
            return ""
        return "%s %s, runs with %s (found through %s)" % (name, found.release or "(unknown version)", found.python,
                                                           found.executable)


#: The one finder that `tool_finder` and `versions` read.
TOOL_PYTHONS = ToolPythonFinder()
