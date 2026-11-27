"""
The folder `--project` names and the project the build reads for it (P319), moved out of check.py (P1325) to keep
that module inside its line budget. No behaviour changed.
"""

from dataclasses import dataclass
from pathlib import Path

from spark.records import board_records
from spark.design import design_codes, loader
from spark.checks import check_codes
from spark.core.result import Refusal

#: Each input is read in one of two roots (P319): the FOLDER `--project` names, where the build and the requirements
#: are, or the PROJECT the build reads, where the records are.
FOLDER, PROJECT = "folder", "project"


@dataclass(frozen=True)
class CheckedFolder:
    """
    Value: the folder `--project` names and the project the build reads for it (P319): one job, to say where each input is
    read. A board folder with no `.spark/` builds with its parent's records, so its checks read the parent's too.
    """
    folder: Path
    project: Path

    @classmethod
    def at(cls, folder):
        """The folder and its project, found the way `loader.project_for` finds a requirements file's."""
        folder = Path(folder)
        if not folder.is_dir():
            # a folder that is not there walked up to a project nobody named
            raise loader.DesignError("no directory at %s — `--project` names a project directory", folder,
                                     code=design_codes.NO_PROJECT_FOLDER)
        project = board_records.project_or_library(folder.resolve())
        return cls(folder, folder if project == folder.resolve() else project)  # the folder as given, when it is one

    @classmethod
    def named(cls, project):
        """Value: (the CheckedFolder of `--project`, None), (None, None) when none is named, or (None, the Refusal that
        says why the folder cannot be read)."""
        try:
            return (cls.at(project) if project else None), None
        except loader.DesignError as broken:
            return None, Refusal(str(broken), check_codes.PROJECT_UNUSABLE)

    def root(self, where):
        """The root a `CONVENTIONS` entry is read in."""
        return self.project if where == PROJECT else self.folder

    def elsewhere(self):
        """Whether the records come from a project other than the folder itself."""
        return self.project != self.folder
