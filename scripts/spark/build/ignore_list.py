"""
Spark's section of a project's `.gitignore` (P1150, P1156), written by `/spark:init` with or without a repository, so a
later `git init` and `git add -A` never commit the link to the person's rules (a home path), the flash image (it can hold
a Wi-Fi password) or the run logs. A `.gitignore` that git tracks is left alone, and the lines are named. Files that git
already tracks and the section covers are named too: spark never untracks them (P1027).
"""

from pathlib import Path

from spark.build import ai_files
from spark.build.spark_section import SparkSection
from spark.records import store
from spark.records.project_commit import ProjectCommit

NAME = ".gitignore"
#: Spark's section of a project's .gitignore: the files spark writes that never go into git. `sim/*.bin` holds the flash
#: image (`sim_project.DEFAULT_IMAGE`, and an image built under another name) and the MicroPython interpreter, a vendor file.
LINES = (ai_files.LOCAL, "sim/*.bin", "sim/runs/")
MARKERS = SparkSection("# spark:begin",
                       "# spark:begin. /spark:init writes this section and rewrites it on each run. Edit outside the markers.",
                       "# spark:end")
BODY = "".join(line + "\n" for line in LINES)


class IgnoreList:
    """Service: spark's section of a project's `.gitignore`, written with or without a repository, and the files git
    already tracks that the section covers. Git is read only through the ProjectCommit Adapter, handed in for tests."""

    def __init__(self, project, git=None):
        self.project = Path(project)
        self.git = git if git is not None else ProjectCommit(self.project)

    def write(self):
        """(whether the file changed, the notes): the `.gitignore` note, then the note of the files git already tracks."""
        did, note = self._file()
        tracked = self.already_tracked()
        notes = [note] + ([self._tracked_note(tracked)] if tracked else [])
        return did, notes

    def already_tracked(self):
        """The files in git's index that spark's section covers, from the project folder; [] outside git."""
        return sorted(self.git.tracked_files(LINES))

    def _file(self):
        path = self.project / NAME
        if path.is_symlink() or path.is_dir():
            return False, "%s is a %s, so it is left alone" % (NAME, "link" if path.is_symlink() else "folder")
        existed = path.exists()
        text = ai_files.read(path) if existed else ""
        if text is None:
            return False, "%s is not UTF-8 text, so it is left alone" % NAME
        new, why = MARKERS.placed(text, BODY) if existed else (MARKERS.block(BODY), None)
        if new is None:
            return False, "%s %s, so it is left alone: fix the markers" % (NAME, why)
        if new == text:
            return False, "%s already has spark's section" % NAME
        if self.git.tracks(NAME):  # Q15, the card P1175: a change the person commits is theirs to make
            return False, ("git tracks your %s, so spark leaves it alone: add spark's section, or these lines: %s"
                           % (NAME, ", ".join(LINES)))
        store.write_file(path, new)
        if not existed:
            return True, "wrote %s with spark's section" % NAME
        return True, ("rewrote spark's section of %s" % NAME if MARKERS.found(text)
                      else "added spark's section to the end of your %s" % NAME)

    def _tracked_note(self, tracked):
        return ("git already tracks %d file(s) that spark's section covers: %s. `git rm --cached <file>` stops git tracking a "
                "file and keeps your copy. Earlier commits still hold it, so change a password that was in one"
                % (len(tracked), ", ".join(tracked)))
