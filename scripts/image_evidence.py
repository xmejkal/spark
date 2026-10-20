"""
What tested an image before a deploy (P337): the strategy that deploy.py and look.py ask whether an image is ready.

`ImageEvidence` holds settings, never an image: each method takes a fresh `ProjectImage`. `PassedRunEvidence` is
today's evidence, a run in sim/runs/ that passed on the image's sha256. It writes nothing.
"""

import abc

import board_grant
from run_scenario import file_hashes

#: How a refusal for a run that tested another image ends: what to do instead (the PO, 2026-10-12: refuse by default).
OLDER_RUNS_WAY_OUT = (". If a log's scenario is gone, delete the log after the person says yes. To flash anyway, pass "
                      "--ignore-older-runs, and deploy.py names the log in a note")


def newer_files(project, image):
    """The files under firmware/ changed after the image was made, as project paths. The board gets the image, not them."""
    made = image.stat().st_mtime
    return sorted(str(path.relative_to(project)) for path in (project / "firmware").rglob("*")
                  if path.is_file() and "__pycache__" not in path.parts and path.stat().st_mtime > made)


class ImageEvidence(abc.ABC):
    """
    Strategy: what tested the image a deploy puts on a board. `simulation` is "passed" for a passed run. `grant_refusal`
    is None, or the board_grant WHY_ code that keeps a deploy grant from answering for this evidence.
    """

    simulation = None
    grant_refusal = None

    @abc.abstractmethod
    def why_not_ready(self, image, with_way_out=False):
        """None when the evidence says `image` may go on a board, else why not. `with_way_out` adds what to do instead.
        DeployError when a log cannot be read."""

    @abc.abstractmethod
    def notes(self, image):
        """Sentences for the person about this evidence and `image`."""

    @abc.abstractmethod
    def expected_files(self, image):
        """{path in the image: sha256} the board must hold after the flash, or {} when nothing says."""

    @abc.abstractmethod
    def argv(self):
        """The flags that select this evidence, for rerun lines and the steps of an envelope."""

    def caveat(self):
        """None, or the words before the gate question."""
        return None


class PassedRunEvidence(ImageEvidence):
    """
    Strategy: a run log in sim/runs/ that passed on the image's sha256. A log that tested another image refuses,
    unless `ignore_older_runs` turns it into a note. A log that failed on this image always refuses.
    """

    simulation = "passed"

    def __init__(self, ignore_older_runs=False):
        self.ignore_older_runs = ignore_older_runs
        self.grant_refusal = board_grant.WHY_IGNORE_OLDER_RUNS if ignore_older_runs else None

    def why_not_ready(self, image, with_way_out=False):
        why = image.why_untested()
        if why or self.ignore_older_runs:
            return why
        other = image.why_other_runs()
        return other + OLDER_RUNS_WAY_OUT if other and with_way_out else other

    def notes(self, image):
        changed = newer_files(image.project, image.path)
        notes = ["%s changed after this image was made: the board gets the image that passed, not the change. Run its "
                 "scenario again to test it." % ", ".join(changed)] if changed else []
        other = image.why_other_runs()
        return notes + [other] if other else notes

    def expected_files(self, image):
        passed = image.find_passed_log()
        return file_hashes(passed) if passed else {}

    def argv(self):
        return ["--ignore-older-runs"] if self.ignore_older_runs else []
