"""
What tested an image before a deploy (P337): the strategy that deploy.py and look.py ask whether an image is ready.

`ImageEvidence` holds settings, never an image: each method takes a fresh `ProjectImage`. `PassedRunEvidence` is
today's evidence, a run in sim/runs/ that passed on the image's sha256. It writes nothing.
"""

import abc

import board_grant
from run_scenario import file_hashes

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
