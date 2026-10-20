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
import tools
from run_scenario import NO_MAIN, READY, file_hashes

#: What `ImageEvidence.simulation` says: a passed run tested the image, or no simulation did (the records keep it).
SIMULATION_PASSED, SIMULATION_NONE = "passed", "none"
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

    def caveat(self):
        """What the person reads before the gate question, or None when a passed run tested the image."""
        return None if self.simulation == SIMULATION_PASSED else "no simulation tested this image"

    @abc.abstractmethod
    def why_not_ready(self, image):
        """None when the evidence says `image` may go on a board, else why not. DeployError when a log cannot be read."""

    def way_out(self, image):
        """What to do instead of a refusal, as words that end its sentence, or "" when there is nothing to add."""
        return ""

    @abc.abstractmethod
    def notes(self, image):
        """Sentences for the person about this evidence and `image`."""

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
        firmware = self.project / "firmware"
        if not (firmware / "main.py").is_file():
            return NO_MAIN % (self.project, READY)
        try:
            for source in sorted(firmware.rglob("*.py")):
                if "__pycache__" in source.parts:
                    continue
                try:
                    compile(source.read_bytes(), str(source), "exec")
                except SyntaxError as broken:
                    return "%s, line %s does not compile: %s" % (source.relative_to(self.project), broken.lineno, broken.msg)
            built = flash_image.image(flash_image.interpreter_path(None, self.project).read_bytes(),
                                      flash_image.files_under(firmware))
            if image.path.read_bytes() != built:
                return ("%s does not hold firmware/ as it is now: build it with flash_image.py --project %s --files "
                        "firmware -o %s" % (image.path.name, self.project.resolve(), image.path))
        except (tools.ToolProblem, OSError, ValueError, ImportError) as cannot:
            return "cannot check %s against firmware/: %s" % (image.path.name, cannot)
        return None

    def notes(self, image):
        return []

    def expected_files(self, image):
        return {path: hashlib.sha256(data).hexdigest()
                for path, data in flash_image.files_under(self.project / "firmware")}

    def argv(self):
        return [NO_SIMULATION_FLAG]
