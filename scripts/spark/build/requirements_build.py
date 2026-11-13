"""
The whole run of the chain for `check_spine.py` (P783 PR 3): the requirements file read, the work folder made, the
build's stages run (`build_service.BuildService`), and the lines that the history and a kept wokwi.toml need said.
`check_spine.main` calls it, prints those lines and hands the stages to its `report`, which removes the work folder.
"""

import json
import os
import shlex
import shutil
import subprocess
import tempfile
from collections import namedtuple
from pathlib import Path

from spark.build import board_engine
from spark.build import build_codes
from spark.build.board_engine import modules_for
from spark.build.build_service import BuildInputs, BuildService, vouches_for_a_build
from spark.build.kept_files import REQUIREMENTS_STAGE, design_handed_to
from spark.build.stages import Stage
from spark.core.outcomes import COULD_NOT_RUN, NOT_CHECKED
from spark.design import loader
from spark.firmware import sim_project
from spark.records import store
from spark.sourcing import part_facts

#: The design the chain is proven against when nobody names one. A motor driver, a sensor on a
#: bus, and the power inlet that supplies the rail the modules only consume — the smallest set
#: that exercises pin assignment, a bus, a rail with an external source, and two footprint kinds.
REFERENCE = {"board": "firebeetle2-esp32s3",
             "parts": ["l9110s-module", "vl6180x-breakout", "jst-ph-2-power-inlet"]}

#: How much of a late command's own output the sentence keeps, as the other last-words sites cap theirs.
LAST_WORDS_CAP = 800


def timed_out_sentence(late):
    """What a command that ran past its limit said (P659): the command by its file names (two words, three when the
    second is `run`, as a converter run as `<runtime> run cli.ts`), the limit it had, and its last three lines of stderr, or of stdout when stderr is empty, capped."""
    words = shlex.split(late.cmd) if isinstance(late.cmd, str) else list(late.cmd)
    names = [Path(str(word)).name for word in words]
    cmd = names[:3] if names[1:2] == ["run"] else names[:2]
    out = late.stderr or late.stdout or ""
    said = out.decode(errors="replace") if isinstance(out, bytes) else out
    last = " | ".join(said.strip()[-LAST_WORDS_CAP:].splitlines()[-3:])
    return "`%s` did not finish in %ss%s" % (" ".join(cmd), late.timeout, "; its last words: " + last if last else "")


#: Result: the stages, the work folder (None when the requirements were refused), the requirements read, the toolchain
#: found (or None) and `diagnostics`, the lines for the person beside the verdict, unguarded.
RequirementsBuildResult = namedtuple("RequirementsBuildResult", "stages workdir requirements toolchain diagnostics")


class RequirementsBuildService:
    """
    Service: the CLI's whole run of the chain for one requirements file, or the reference design: it reads the file,
    makes the work folder `spark-spine-*`, runs the stages of a `BuildService` and notes a build that ran end to end in
    the person's history. It is given the BuildService class, or None for the real one; a test hands a fake with
    `for_toolchain`. It raises nothing: a refused file, a build past its limit and any crash are each one stage that
    could not run. It never removes the work folder: the caller's report does.
    """

    def __init__(self, build_service_class=None):
        self.build_service_class = build_service_class

    def build(self, requirements_path=None, firmware=None, simulation=None):
        """A RequirementsBuildResult for the file at `requirements_path` (None: the reference design), the flash image
        `firmware` (None: the one the kept wokwi.toml in the folder `simulation` names) and that folder, or None."""
        # Read AS input: a malformed file is a stage that could not run, not a traceback, and no folder is made.
        source = Path(requirements_path).resolve() if requirements_path else None
        try:
            requirements = loader.read(source) if source else dict(REFERENCE)
        except loader.DesignError as broken:
            return RequirementsBuildResult([Stage(REQUIREMENTS_STAGE, COULD_NOT_RUN, str(broken), broken.code)], None, None, None, [])
        # The project is the file's, up from its own folder; a file in no project is built from the plugin's library.
        project = loader.project_for(source) if source else None
        from_library = bool(source) and loader.is_library(project)
        workdir, toolchain = self._work_folder(requirements, source)
        # What `built` will name is loaded now, once, before anything can change under it.
        handed = design_handed_to(workdir, project) if source and not from_library else None
        if simulation and (simulation / "diagram.json").is_file():  # P482: the build merges into a copy, never the person's file
            shutil.copy(simulation / "diagram.json", workdir / sim_project.KEPT_DIAGRAM)
        firmware, kept = self._firmware(firmware, simulation)
        stages = self._stages(toolchain, BuildInputs(requirements, workdir, project, from_library, firmware))
        diagnostics = self._firmware_line(kept, workdir)
        # The history says a build ran end to end (§5.7), written by the chain itself; one it cannot keep is said, and the verdict stands.
        if handed is not None and vouches_for_a_build(stages):
            try:
                part_facts.note_built(handed)
            except (store.StoreError, OSError) as unrecorded:
                diagnostics.append("  the build was not recorded in your history: %s" % unrecorded)
        return RequirementsBuildResult(stages, workdir, requirements, toolchain, diagnostics)

    @staticmethod
    def _work_folder(requirements, source):
        """(the new work folder with requirements.json in it, the toolchain found from the file's folder or the working
        directory, or None): tsci needs its toolchain reachable from the build folder, so its node_modules is linked in."""
        workdir = Path(tempfile.mkdtemp(prefix="spark-spine-"))
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        toolchain = board_engine.find_toolchain(source.parent if source else Path.cwd())
        modules = modules_for(toolchain) if toolchain is not None else None
        if modules is not None and not (workdir / "node_modules").exists():
            os.symlink(modules, workdir / "node_modules")
        return workdir, toolchain

    @staticmethod
    def _firmware(firmware, simulation):
        """(the flash image the build names, the kept wokwi.toml's FirmwareLine or None): a rebuild runs the image the
        kept wokwi.toml already names, unless `firmware` names another."""
        kept = None
        if not firmware and simulation:
            kept = sim_project.firmware_in(simulation / "wokwi.toml")
            firmware = kept.name
        return firmware, kept

    def _stages(self, toolchain, inputs):
        """The build's stages; a build past its limit is one timed-out stage, and any other exception one crashed stage."""
        # BuildService is looked up at call time, so a test's patch of `requirements_build.BuildService` still reaches it.
        service = self.build_service_class or BuildService
        try:
            return service.for_toolchain(toolchain).build(inputs)
        except subprocess.TimeoutExpired as late:
            return [Stage("build", COULD_NOT_RUN, timed_out_sentence(late), build_codes.STAGE_TIMED_OUT)]
        except Exception as exc:  # noqa: BLE001
            # Anything unforeseen is could-not-run, never problems. An exception says this tool
            # failed, which is not the same as the chain failing, and reporting one as the other
            # sends somebody to debug a design that was never examined.
            return [Stage("check_spine", COULD_NOT_RUN,
                          "%s: %s" % (type(exc).__name__, exc), build_codes.STAGE_CRASHED)]

    @staticmethod
    def _firmware_line(kept, workdir):
        """P429: the sentence, in a list, when the kept wokwi.toml's firmware line could not be read and the build wrote
        that file again, so the line is gone; else an empty list."""
        if kept is not None and kept.state == NOT_CHECKED and (workdir / "sim" / "wokwi.toml").is_file():
            return ["  sim/wokwi.toml %s The rebuild wrote it again with no image named, and a scenario run then names "
                    "the default one." % kept.why]
        return []
