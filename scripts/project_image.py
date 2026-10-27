"""
The image a project would put on a board, and the run logs that tested it (P219, P239).

A library for deploy.py and board_look.py: `ProjectImage` finds the image sim/wokwi.toml names, reads the run logs in
sim/runs/ that name an image's sha256, and says why an image is not yet one to put on a board. It writes nothing.
"""

import functools
import hashlib

import outcomes
import run_scenario
import sim_project


class DeployError(Exception):
    """Error: why the image cannot go on the board yet. The message is the whole sentence."""


class ProjectImage:
    """
    Value: the flash image of one project and the run logs about it. Its methods read the project's files and never
    write. `ProjectImage(project)` raises DeployError when sim/wokwi.toml or the image it names is missing; it reads no
    log. `sha256` is read once, so build a new ProjectImage to see a changed file.
    """

    def __init__(self, project):
        toml = project / "sim" / "wokwi.toml"
        if not toml.is_file():
            raise DeployError("no sim/wokwi.toml in %s: build with /spark:build --keep . first" % project)
        named = sim_project.firmware_in(toml)
        if named.state == outcomes.NOT_CHECKED:
            raise DeployError("sim/wokwi.toml %s%s" % (named.why, named.fix()))
        self.path = toml.parent / (named.name or run_scenario.DEFAULT_IMAGE)
        outside = sim_project.why_outside_sim(toml.parent, self.path)
        if outside:
            raise DeployError(outside)
        if not self.path.is_file():
            raise DeployError("no %s yet: run a scenario first (run_scenario.py), which writes the image and tests it"
                              % self.path)
        self.project = project
        #: run_scenario.py writes every log here, in whichever sub-folder of sim/ the image is
        self.runs = project / "sim" / "runs"

    @functools.cached_property
    def sha256(self):
        """The image file's sha256, as hex."""
        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def read_run_logs(self):
        """
        [(log, verdict, the tested image's sha256 or None)] for each log in the runs folder, by name. A path that is no
        file is skipped. DeployError when a log cannot be read.
        """
        records = []
        for log in sorted(self.runs.glob("*.log")):
            if not log.is_file():
                continue
            try:
                records.append((log,) + run_scenario.run_record(log))
            except OSError as cannot:
                raise DeployError("cannot read %s: %s" % (log, cannot))
        return records

    def why_untested(self):
        """
        None when a passed run in the runs folder names this image's sha256 and no run with another verdict does.
        Else why not.
        """
        named = [(log, verdict) for log, verdict, sha256 in self.read_run_logs() if sha256 == self.sha256]
        failed = [(log, verdict) for log, verdict in named if verdict != "passed"]
        if failed:
            return ("%s did not pass on this image (verdict: %s): deploy.py flashes only an image that passed"
                    % (failed[0][0].name, failed[0][1]))
        if not named:
            return ("no run in sim/runs/ tested %s as it is now, and a log from an older spark names no image: "
                    "run its scenario again with run_scenario.py" % self.path.name)
        return None

    def find_passed_log(self):
        """The first log in the runs folder that passed on this image's sha256, or None. Its file lines are what a board must hold."""
        return next((log for log, verdict, sha256 in self.read_run_logs()
                     if sha256 == self.sha256 and verdict == "passed"), None)

    def find_newer_files(self):
        """The files under firmware/ changed after the image was made, as project paths. The board gets the image, not them."""
        made = self.path.stat().st_mtime
        return sorted(str(path.relative_to(self.project)) for path in (self.project / "firmware").rglob("*")
                      if path.is_file() and "__pycache__" not in path.parts and path.stat().st_mtime > made)

    def why_other_runs(self):
        """A sentence naming each log in the runs folder that does not name this image's sha256, or None when every log does."""
        logs = [(log.name, sha256) for log, _, sha256 in self.read_run_logs() if sha256 != self.sha256]
        if not logs:
            return None
        others = [name for name, sha256 in logs if sha256]
        older = [name for name, sha256 in logs if not sha256]
        said = []
        if others:
            said.append("%s tested another image, not this one" % ", ".join(others))
        if older:
            said.append("%s %s no image (an older spark)" % (", ".join(older), "names" if len(older) == 1 else "name"))
        again = "that scenario" if len(logs) == 1 else "those scenarios"
        return "%s: run %s again to test this one" % (", and ".join(said), again)
