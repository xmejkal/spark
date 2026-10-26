"""
What tested an image before a deploy (P337): the strategy that deploy.py and look.py ask whether an image is ready.

`ImageEvidence` holds settings, never an image: each method takes a fresh `ProjectImage`. `PassedRunEvidence` is
today's evidence, a run in sim/runs/ that passed on the image's sha256. It writes nothing.
"""

import abc
import hashlib
from pathlib import Path

import board_grant
import flash_image
import outcomes
import tools
from run_scenario import EXPECT_PIN, NO_MAIN, READY, SET_CONTROL, ScenarioSteps, file_hashes

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
NO_CONTROL_CAVEAT = "the passed run's scenario has no set-control step (the step that presses a button or sets a sensor)"
NO_CONTROL_NO_PIN_CAVEAT = ("the passed run's scenario has no set-control step (the step that presses a button or sets a "
                            "sensor) and no expect-pin step (the step that reads a pin)")
#: The flag that deploys an image from firmware/ with no simulation.
NO_SIMULATION_FLAG = "--no-simulation"
#: The flag that turns a run of another image from a refusal into a note.
IGNORE_OLDER_RUNS_FLAG = "--ignore-older-runs"
#: How a refusal for a run that tested another image ends: what to do instead (the PO, 2026-10-12: refuse by default).
OLDER_RUNS_WAY_OUT = (". If a log's scenario is gone, delete the log after the person says yes. To flash anyway, pass "
                      "%s, and deploy.py names the log in a note" % IGNORE_OLDER_RUNS_FLAG)


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
        """None when the evidence says `image` may go on a board, else why not. DeployError when a log cannot be read."""

    def caveats(self, image):
        """Sentences the person reads before the gate question about what tested `image`, or [] when there are none."""
        return []

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
        """What the passed run's scenario did not do, from the step counts in its log's header. Call it only for an image `why_not_ready` passed."""
        passed = image.find_passed_log()
        if passed is None:
            return []
        steps = ScenarioSteps.from_log(passed)
        if steps.state == outcomes.NOT_CHECKED:
            return ["%s; %s" % (outcomes.NOT_CHECKED_MESSAGE % steps.why, UNCOUNTED_ADVICE)]
        if steps.state == outcomes.NONE_RECORDED:
            return [OLDER_LOG_CAVEAT]
        if steps.count(SET_CONTROL):
            return []
        return [NO_CONTROL_CAVEAT if steps.count(EXPECT_PIN) else NO_CONTROL_NO_PIN_CAVEAT]

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
        """None, or one sentence. It never raises for firmware/ or the image: a broken file is a sentence."""
        return (self._why_no_main() or self._why_not_compiling() or self._why_run_failed(image)
                or self._why_image_differs(image))

    def caveats(self, image):
        return [NO_SIMULATION_CAVEAT]

    def _why_no_main(self):
        if not (self.project / "firmware" / "main.py").is_file():
            return NO_MAIN % (self.project, READY)
        return None

    def _why_not_compiling(self):
        for source in sorted((self.project / "firmware").rglob("*.py")):
            if "__pycache__" in source.parts:
                continue
            name = source.relative_to(self.project)
            try:
                code = source.read_bytes()
            except OSError as cannot:
                return "cannot read %s: %s" % (name, cannot)
            try:
                compile(code, str(source), "exec")
            except SyntaxError as broken:
                return "%s, line %s does not compile: %s" % (name, broken.lineno, broken.msg)
            except (RecursionError, MemoryError):
                return "%s is too deeply nested or too big to compile" % name
            except ValueError as broken:  # a source with a null byte
                return "%s does not compile: %s" % (name, broken)
        return None

    def _why_run_failed(self, image):
        """A run that did not pass on this image refuses here too: a passed run is not needed, a failed one still counts."""
        for log, verdict, sha256 in image.read_run_logs():
            if sha256 == image.sha256 and verdict != "passed":
                return ("%s did not pass on this image (verdict: %s): deploy.py flashes no image that a run failed"
                        % (log.name, verdict))
        return None

    def _why_image_differs(self, image):
        try:
            built = flash_image.interpreter_for(None, self.project).image(flash_image.files_under(self.project / "firmware"))
            held = image.path.read_bytes()
        except (tools.ToolProblem, OSError, ValueError, ImportError) as cannot:
            return "cannot check %s against firmware/: %s" % (image.path.name, cannot)
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
