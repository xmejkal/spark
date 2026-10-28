"""
What tested an image before a deploy (P337): the strategy that deploy.py and look.py ask whether an image is ready.

`ImageEvidence` holds settings, never an image: each method takes a fresh `ProjectImage`. `PassedRunEvidence` is
today's evidence, a run in sim/runs/ that passed on the image's sha256. It writes nothing.
"""

import abc
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import board_grant
import flash_image
import outcomes
import text_guards
import tools
from run_scenario import (EXPECT_PIN, NO_MAIN, READY, SET_CONTROL, WHY_LOG_UNREADABLE, ScenarioSteps, SimulationLimits,
                          file_hashes)

#: What `ImageEvidence.simulation` says: a passed run tested the image, or no simulation did (the records keep it).
SIMULATION_PASSED, SIMULATION_NONE = "passed", "none"
#: What the person reads before the gate question when no simulation tested the image (deploy.py's docs quote it).
NO_SIMULATION_CAVEAT = "no simulation tested this image"
# --- MVP ---
#: What the person reads when a passed run's log cannot say what its scenario did, or its scenario did less than a person expects.
#: A log that cannot be counted (outcomes.NOT_CHECKED) says ScenarioSteps.why, then the advice. A log with no counts line
#: (outcomes.NONE_RECORDED) is not "not checked": nothing was recorded in it, and it says so.
UNCOUNTED_ADVICE = "run its scenario again to count them"
OLDER_LOG_CAVEAT = "the passed run's log is older than step counting: run its scenario again to count its steps"
#: The two no-control sentences take a subject: one run says "the passed run's scenario has", several name their logs.
NO_CONTROL_CAVEAT = "%s no set-control step (the step that presses a button or sets a sensor)"
NO_CONTROL_NO_PIN_CAVEAT = ("%s no set-control step (the step that presses a button or sets a sensor) and no expect-pin "
                            "step (the step that reads a pin)")
#: What a passed run's limits section that cannot be read tells the person to do (the sentence starts with why it was not checked).
LIMITS_HINT = "fix `sim/WHAT-THIS-CANNOT-SHOW.md`, or run the scenario again"
ONE_RUN_MESSAGE = "the passed run's scenario has"
MANY_RUNS_MESSAGE = "the passed runs (%s) have"
#: P436: the words of the image check that could not run, as a sentence and as a tools.ToolProblem.
CANNOT_CHECK_REASON = "cannot check %s against firmware/: %s"
#: The flag that deploys an image from firmware/ with no simulation.
NO_SIMULATION_FLAG = "--no-simulation"
#: The flag that turns a run of another image from a refusal into a note.
IGNORE_OLDER_RUNS_FLAG = "--ignore-older-runs"
#: How a refusal for a run that tested another image ends: what to do instead (the PO, 2026-10-12: refuse by default).
OLDER_RUNS_WAY_OUT = (". If a log's scenario is gone, delete the log after the person says yes. To flash anyway, pass "
                      "%s, and deploy.py names the log in a note" % IGNORE_OLDER_RUNS_FLAG)
#: How long the child may compile every .py file under firmware/ (P427). A guess: the worst compile measured was 1.9 s for 4 MB.
COMPILE_TIMEOUT_S = 30
#: What the child says about the first file that fails, as "kind" (the other line is {"checking": name}, before each file).
SYNTAX, TOO_DEEP, BYTES, UNREADABLE = "syntax", "too_deep", "bytes", "unreadable"
#: The sentences for a file that does not compile (P337; their words are pinned by tests/test_image_evidence.py).
SYNTAX_REASON = "%s, line %s does not compile: %s"
TOO_DEEP_REASON = "%s is too deeply nested or too big to compile"
BYTES_REASON = "%s does not compile: %s"
UNREADABLE_REASON = "cannot read %s: %s"
#: The sentences for a compiler that did not answer (P427): it stopped, or it ran too long. The file is the last one it began.
STOPPED_REASON = "%s could not be compiled: the compiler stopped (%s)"
SIGNAL_DETAIL, EXIT_DETAIL = "signal %d", "exit code %d"
TIMEOUT_REASON = "%s did not compile in %g s"
NO_ANSWER_REASON = "%s could not be compiled: the compiler gave no answer"
#: Named when the compiler stopped before it began a file.
NO_FILE_YET = "firmware/"
#: Named when an answer holds no file name and the child began no file.
NO_NAME = "a firmware file"
#: What each compile child runs (P427): read [name, path] pairs from stdin; say {"checking": name} before each file, then one
#: line for the first file that fails, or {"ok": true}. A JSON line holds no raw newline, so no file name can fake a line.
COMPILE_CHILD = """\
import json, sys

def say(**fields):
    print(json.dumps(fields), flush=True)

def failure(name, path):
    try:
        with open(path, "rb") as opened:
            code = opened.read()
    except OSError as cannot:
        return dict(name=name, kind="%s", msg=str(cannot))
    try:
        compile(code, path, "exec")
    except SyntaxError as broken:
        return dict(name=name, kind="%s", line=broken.lineno, msg=broken.msg)
    except (RecursionError, MemoryError):
        return dict(name=name, kind="%s")
    except ValueError as broken:  # a source with a null byte
        return dict(name=name, kind="%s", msg=str(broken))
    return None

for name, path in json.loads(sys.stdin.read()):
    say(checking=name)
    found = failure(name, path)
    if found:
        say(**found)
        sys.exit(0)
say(ok=True)
""" % (UNREADABLE, SYNTAX, TOO_DEEP, BYTES)


class CompileCheck:
    """
    The .py files compiled in one child process, so that a source which kills the compiler (a stack overflow, signal 11)
    kills the child and not spark (P427). `why_not` is None, or one sentence. It started like import_firmware.import_one:
    this interpreter with -I -B, in spark's own working directory: -I keeps a json.py planted there out, and a relative path
    means what it meant to the parent.
    """

    def __init__(self, files):
        """`files`: [(name shown, path)] in the order to compile."""
        self.files = [[str(name), str(path)] for name, path in files]

    def why_not(self):
        command = [sys.executable, "-I", "-B", "-c", COMPILE_CHILD]
        try:
            done = subprocess.run(command, input=json.dumps(self.files), capture_output=True, text=True, errors="replace",
                                  timeout=COMPILE_TIMEOUT_S)
        except subprocess.TimeoutExpired as late:
            said = late.stdout.decode(errors="replace") if isinstance(late.stdout, bytes) else late.stdout
            return TIMEOUT_REASON % (text_guards.printable(self._read(said)[0] or NO_FILE_YET), COMPILE_TIMEOUT_S)
        checking, result = self._read(done.stdout)
        if result is None:
            last = text_guards.printable(checking or NO_FILE_YET)
            if done.returncode == 0:
                return NO_ANSWER_REASON % last
            detail = SIGNAL_DETAIL % -done.returncode if done.returncode < 0 else EXIT_DETAIL % done.returncode
            return STOPPED_REASON % (last, detail)
        return self._sentence(result, checking)

    @staticmethod
    def _read(said):
        """(the last name the child began, its answer) from the JSON lines in `said`; a line cut short is no JSON and is skipped."""
        checking, result = None, None
        for line in (said or "").split("\n"):
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if not isinstance(entry, dict):
                continue
            if "checking" in entry:
                checking = str(entry["checking"])
            elif "ok" in entry or "kind" in entry:
                result = entry
                break
        return checking, result

    @staticmethod
    def _sentence(result, checking):
        if result.get("ok"):
            return None
        name = text_guards.printable(str(result.get("name") or checking or NO_NAME))
        kind = result.get("kind")
        if kind == SYNTAX:
            return SYNTAX_REASON % (name, result.get("line"), result.get("msg"))
        if kind == TOO_DEEP:
            return TOO_DEEP_REASON % name
        if kind == UNREADABLE:
            return UNREADABLE_REASON % (name, result.get("msg"))
        return BYTES_REASON % (name, result.get("msg"))


class ImageEvidence(abc.ABC):
    """
    Strategy: what tested the image a deploy puts on a board. `grant_refusal` is None, or the board_grant WHY_ code
    that keeps a deploy grant from answering for this evidence.
    """

    grant_refusal = None
    #: SIMULATION_PASSED or SIMULATION_NONE
    simulation = SIMULATION_PASSED

    @abc.abstractmethod
    def why_not_ready(self, image):
        """None when the evidence says `image` may go on a board, else why not. DeployError when a log cannot be read;
        tools.ToolProblem when a tool the check needs is missing (P436)."""

    def caveats(self, image):
        """Sentences the person reads before the gate question about what tested `image`, or [] when there are none."""
        return []

    # --- MVP ---
    def find_limits(self, image):
        """The sim_project.Limit list of the project that no simulation can show, from this evidence's records, or [] when it holds none."""
        return []
    # --- end MVP ---

    def way_out(self, image):
        """What to do instead of a refusal, as words that end its sentence, or "" when there is nothing to add."""
        return ""

    def notes(self, image):
        """Sentences for the person about this evidence and `image`, or [] when there are none."""
        return []

    @abc.abstractmethod
    def expected_files(self, image):
        """{path in the image: sha256} the board must hold after the flash, or {} when nothing says."""

    @abc.abstractmethod
    def argv(self):
        """The flags that select this evidence, for rerun lines and the steps of an envelope."""


class PassedRunEvidence(ImageEvidence):
    """
    Strategy: a run log in sim/runs/ that passed on the image's sha256. A log that tested another image refuses,
    unless `ignore_older_runs` turns it into a note. A log that failed on this image always refuses.
    """

    def __init__(self, ignore_older_runs=False):
        self.ignore_older_runs = ignore_older_runs
        self.grant_refusal = board_grant.WHY_IGNORE_OLDER_RUNS if ignore_older_runs else None

    def why_not_ready(self, image):
        why = image.why_untested()
        if why or self.ignore_older_runs:
            return why
        return image.why_other_runs()

    # --- MVP ---
    def caveats(self, image):
        """
        What the passed runs of `image` did not test. Call it only for an image `why_not_ready` passed. It first says what the
        scenarios did not do, from the step counts in the logs' headers: a control in any counted log clears the no-control
        sentence, and a log that cannot be counted says its own sentence and makes no claim about a control, because it may press
        the button. Then it adds a sentence for each log whose limits section could not be read.
        """
        logs = image.find_passed_logs()
        read = [(log, ScenarioSteps.from_log(log)) for log in logs]
        merged = ScenarioSteps.merge([steps for _, steps in read])
        # With no control in any counted log, an unreadable log has said so in its steps sentence already.
        return self._control_caveats(logs, read, merged) + self._limits_caveats(logs, said_unreadable=not merged.count(SET_CONTROL))

    # --- MVP ---
    def find_limits(self, image):
        """The Limits in the limits section of every passed log of `image`, in name order, each once."""
        found = [limit for _, each in self._limits_of(image.find_passed_logs()) for limit in each.limits]
        return list(dict.fromkeys(found))
    # --- end MVP ---

    @staticmethod
    def _limits_of(logs):
        """[(log, SimulationLimits)], each log read once."""
        return [(log, SimulationLimits.from_log(log)) for log in logs]

    @staticmethod
    def _control_caveats(logs, read, merged):
        if not logs or merged.count(SET_CONTROL):
            return []
        uncounted = [PassedRunEvidence._named(log, PassedRunEvidence._uncounted_sentence(steps), len(logs) > 1)
                     for log, steps in read if steps.state != outcomes.RECORDED]
        if uncounted:
            return uncounted
        subject = MANY_RUNS_MESSAGE % ", ".join(log.name for log in logs) if len(logs) > 1 else ONE_RUN_MESSAGE
        return [(NO_CONTROL_CAVEAT if merged.count(EXPECT_PIN) else NO_CONTROL_NO_PIN_CAVEAT) % subject]

    @staticmethod
    def _limits_caveats(logs, said_unreadable):
        """A sentence for each log whose limits section is NOT_CHECKED. An unreadable log is skipped when `said_unreadable`: its steps sentence says so."""
        return [PassedRunEvidence._named(log, "%s; %s" % (outcomes.NOT_CHECKED_MESSAGE % each.why, LIMITS_HINT), len(logs) > 1)
                for log, each in PassedRunEvidence._limits_of(logs)
                if each.state == outcomes.NOT_CHECKED and not (said_unreadable and each.why == WHY_LOG_UNREADABLE)]

    @staticmethod
    def _uncounted_sentence(steps):
        """The sentence for a passed log whose steps are not RECORDED."""
        if steps.state == outcomes.NOT_CHECKED:
            return "%s; %s" % (outcomes.NOT_CHECKED_MESSAGE % steps.why, UNCOUNTED_ADVICE)
        return OLDER_LOG_CAVEAT

    @staticmethod
    def _named(log, said, named):
        """`said`, started with the log's name when `named` (several logs passed)."""
        return "%s: %s" % (log.name, said) if named else said

    def way_out(self, image):
        refused_for_other_runs = not self.ignore_older_runs and not image.why_untested() and image.why_other_runs()
        return OLDER_RUNS_WAY_OUT if refused_for_other_runs else ""

    def notes(self, image):
        changed = image.find_newer_files()
        notes = ["%s changed after this image was made: the board gets the image that passed, not the change. Run its "
                 "scenario again to test it." % ", ".join(changed)] if changed else []
        other = image.why_other_runs()
        return notes + [other] if other else notes

    def expected_files(self, image):
        passed = image.find_passed_log()
        return file_hashes(passed) if passed else {}

    def argv(self):
        return [IGNORE_OLDER_RUNS_FLAG] if self.ignore_older_runs else []


class NoSimulationEvidence(ImageEvidence):
    """
    Strategy: no simulation tested the image, so firmware/ stands for it. The image is ready when firmware/ has a
    main.py, every .py file under it compiles and the image file holds firmware/ as it is now. It does not run the
    firmware: the board is the test. It writes nothing.
    """

    simulation = SIMULATION_NONE
    grant_refusal = board_grant.WHY_NO_SIMULATION

    def __init__(self, project):
        self.project = Path(project)

    def why_not_ready(self, image):
        """None, or one sentence. A broken file is a sentence; a missing tool raises a tools.ToolProblem (P436)."""
        return (self._why_no_main() or self._why_not_compiling() or self._why_run_failed(image)
                or self._why_image_differs(image))

    def caveats(self, image):
        return [NO_SIMULATION_CAVEAT]

    def _why_no_main(self):
        if not (self.project / "firmware" / "main.py").is_file():
            return NO_MAIN % (self.project, READY)
        return None

    def _why_not_compiling(self):
        firmware = self.project / "firmware"
        files = [(source.relative_to(self.project), source) for source in sorted(firmware.rglob("*.py"))
                 if "__pycache__" not in source.parts]
        return CompileCheck(files).why_not() if files else None

    def _why_run_failed(self, image):
        """A run that did not pass on this image refuses here too: a passed run is not needed, a failed one still counts."""
        for log, verdict, sha256 in image.read_run_logs():
            if sha256 == image.sha256 and verdict != "passed":
                return ("%s did not pass on this image (verdict: %s): deploy.py flashes no image that a run failed"
                        % (log.name, verdict))
        return None

    # --- MVP --- P436: a missing tool raises its ToolProblem (tool_missing: /spark:setup); an unreadable file is a sentence
    def _why_image_differs(self, image):
        try:
            tools.find("littlefs")  # as flash_image.main does, so a missing littlefs names its install line
            built = flash_image.interpreter_for(None, self.project).image(flash_image.files_under(self.project / "firmware"))
            held = image.path.read_bytes()
        except (tools.ToolProblem, ImportError) as cannot:
            raise tools.ToolProblem(CANNOT_CHECK_REASON % (image.path.name, cannot))
        except (OSError, ValueError) as cannot:
            return CANNOT_CHECK_REASON % (image.path.name, cannot)
        except Exception as cannot:  # littlefs.errors.LittleFSError, imported lazily as flash_image does
            if type(cannot).__name__ != "LittleFSError":
                raise
            return "firmware/ does not fit the image's file system: %s" % cannot
        if held != built:
            return ("%s does not hold firmware/ as it is now: build it with flash_image.py --project %s --files "
                    "firmware -o %s" % (image.path.name, self.project.resolve(), image.path))
        return None

    def expected_files(self, image):
        return {path: hashlib.sha256(data).hexdigest()
                for path, data in flash_image.files_under(self.project / "firmware")}

    def argv(self):
        return [NO_SIMULATION_FLAG]


def evidence_for(project, no_simulation, ignore_older_runs):
    """The evidence the flags of look.py and deploy.py select (they exclude each other in argparse)."""
    return NoSimulationEvidence(project) if no_simulation else PassedRunEvidence(ignore_older_runs)
