"""
Is this image the one a passed run tested? The checks deploy.py and board_look.py share (P219).

A library: the image sim/wokwi.toml names, the run logs that name an image's sha256, and the sentences that say why an
image is not yet one to put on a board.
"""

import hashlib

import run_scenario
import sim_project


#: What to try when esptool cannot reach the board.
BOOT_HINT = ("if esptool could not connect, hold the board's BOOT button, press and release RESET, release BOOT, "
             "and run it again")


class DeployProblem(Exception):
    """Why the image cannot go onto the board yet. The message is the whole sentence."""


def image_of(project):
    """The flash image sim/wokwi.toml names, which run_scenario.py writes. DeployProblem when there is none yet."""
    toml = project / "sim" / "wokwi.toml"
    if not toml.is_file():
        raise DeployProblem("no sim/wokwi.toml in %s: build with /spark:build --keep . first" % project)
    image = toml.parent / (sim_project.firmware_in(toml) or run_scenario.DEFAULT_IMAGE)
    if not image.is_file():
        raise DeployProblem("no %s yet: run a scenario first (run_scenario.py), which writes the image and tests it" % image)
    return image


def run_logs(runs):
    """
    (log, verdict, the tested image's sha256 or None) for each log in the runs folder, by name. A path that is no file
    is skipped. DeployProblem when a log cannot be read.
    """
    records = []
    for log in sorted(runs.glob("*.log")):
        if not log.is_file():
            continue
        try:
            records.append((log,) + run_scenario.run_record(log))
        except OSError as cannot:
            raise DeployProblem("cannot read %s: %s" % (log, cannot))
    return records


def untested(image, runs):
    """
    None when a passed run in the runs folder names this image's sha256 and no run with another verdict does.
    Else why not.
    """
    digest = hashlib.sha256(image.read_bytes()).hexdigest()
    named = [(log, verdict) for log, verdict, sha256 in run_logs(runs) if sha256 == digest]
    failed = [(log, verdict) for log, verdict in named if verdict != "passed"]
    if failed:
        return ("%s did not pass on this image (verdict: %s): deploy.py flashes only an image that passed"
                % (failed[0][0].name, failed[0][1]))
    if not named:
        return ("no run in sim/runs/ tested %s as it is now, and a log from an older spark names no image: "
                "run its scenario again with run_scenario.py" % image.name)
    return None


def passed_log(image, runs):
    """The first log in the runs folder that passed on this image's sha256, or None. Its file lines are what a board must hold."""
    digest = hashlib.sha256(image.read_bytes()).hexdigest()
    return next((log for log, verdict, sha256 in run_logs(runs) if sha256 == digest and verdict == "passed"), None)


def tested_another(image, runs):
    """A sentence naming each log in the runs folder that does not name this image's sha256, or None when every log does."""
    digest = hashlib.sha256(image.read_bytes()).hexdigest()
    logs = [(log.name, sha256) for log, _, sha256 in run_logs(runs) if sha256 != digest]
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


def runnable(tool):
    """The command that runs a tool: a Python package as `python -m <module>`, anything else as it was found."""
    if tool.entry.get("kind") == "python":
        return tool.command + ["-m", tool.entry["module"]]
    return list(tool.command)
