"""
The registration as an Operation on the core (P920, #1302): a project that is not spark's writes its name into spark's
store once, so that its own tool can record its deploys with `bench.py record`. `bench.py register` is its CLI. Every run
writes the launcher again, also when the registration is unchanged: that is the launcher's repair. It touches no board.
"""

import shlex
from pathlib import Path

from spark.bench import bench_privacy
from spark.bench.stops import stop_result
from spark.core.errors import SparkError
from spark.core.operation import COMMON_ARGUMENTS, READS, WRITES, Argument, Operation
from spark.core.result import OperationResult
from spark.core.text_guards import printable
from spark.records import launcher
from spark.records import store
from spark.records.registered_project_store import NOT_REGISTERED_YET, RegisteredProjectStore

# --- MVP ---
SCRIPT = "bench.py"
#: A stop names no project folder: the button words of the one it reads are none.
HERE = Path(".")
NAME_HELP = "the project's name in spark's store: lower-case letters, digits and '-', such as pixel-games"
ORIGIN_HELP = ("text that every worktree of the project shares: its origin remote, or the git common folder of a project "
               "with no remote")
TOOL_HELP = 'the name of the tool that deploys the project, such as box.py: bench.py show says it after "by"'
#: The lines of a registration: what the store holds now, and where the launcher is.
REGISTERED_LINES = {True: "registered: %s, made by %s, from %s", False: "registered already, nothing changed: %s, made by %s, from %s"}
LAUNCHER_LINE = "launcher: %s"
#: The command that runs this registration again: the next command of every stop, for its values.
AGAIN = "bench.py register %s --origin %s --tool %s"
AGAIN_FIX = "repair the file or the folder that the sentence names, then run %s again"
#: What a stop after the registration says: the name is in the store, and the launcher is not.
NO_LAUNCHER = "%s is registered, but the launcher was not written."


class RegisterProject(Operation):
    """
    Operation: register a project that is not spark's. `registered` is the RegisteredProjectStore (None: the store's own)
    and `write_launcher()` writes the launcher and gives its path (default: launcher.write_launcher). A name that is not
    plain or is taken, and a store that refuses, are one unchecked item, and nothing is registered.
    """

    name = "register-project"
    summary = ("register a project that is not spark's, once, so that its own tool records its deploys with bench.py record; "
               "it touches no board")
    arguments = (Argument(("name",), "name", str, NAME_HELP, metavar="NAME"),
                 Argument(("--origin",), "origin", str, ORIGIN_HELP, required=True),
                 Argument(("--tool",), "tool", str, TOOL_HELP, required=True),
                 COMMON_ARGUMENTS["json"])
    effects = (READS, WRITES)
    data_keys = ("registered", "changed", "launcher")
    privacy_for = staticmethod(bench_privacy.privacy_for)

    def __init__(self, registered=None, write_launcher=launcher.write_launcher):
        self.registered, self.write_launcher = registered or RegisteredProjectStore(), write_launcher

    def run(self, name, origin, tool, *, outside):
        again = AGAIN % tuple(shlex.quote(value) for value in (name, origin, tool))
        try:
            project, changed = self.registered.register(name, origin, tool, outside.clock.now().isoformat(timespec="seconds"))
        except SparkError as refused:
            return stop_result(refused, SCRIPT, HERE, None)
        except store.StoreError as cannot:
            return self._stopped(cannot, NOT_REGISTERED_YET, AGAIN_FIX % again)
        registered = {"registered": project._asdict(), "changed": changed}
        try:
            path = self.write_launcher()
        except store.StoreError as cannot:  # the name is in the store: the same command again writes the launcher
            return self._stopped(cannot, NO_LAUNCHER % name, AGAIN_FIX % again)._replace(data=dict(registered, launcher=None))
        lines = [REGISTERED_LINES[changed] % (project.name, project.tool, project.origin), LAUNCHER_LINE % path]
        return OperationResult(dict(registered, launcher=str(path)), lines=[printable(line) for line in lines])

    @staticmethod
    def _stopped(cannot, said, fix):
        """stop_result's answer for a store that refused, with `fix`, and a last line: what the store holds now, and `fix`."""
        stopped = stop_result(cannot, SCRIPT, HERE, None)
        return stopped._replace(findings=[found._replace(fix=fix) for found in stopped.findings],
                                diagnostics=list(stopped.diagnostics) + ["%s: %s %s" % (SCRIPT, said, fix)])
# --- end MVP ---
