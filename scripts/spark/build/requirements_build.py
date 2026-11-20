"""
The whole run of the chain for `check_spine.py`: the requirements file read, the work folder made, the
build's stages run (`build_service.BuildService`), and the lines that the history and a kept wokwi.toml need said.
The Operation `build_board.BuildBoard` calls it, keeps what --keep asks for, removes the work folder and answers (P804).
"""

import json
import os
import shutil
import subprocess
import tempfile
from collections import namedtuple
from pathlib import Path

from spark.build import board_engine
from spark.build.board_engine import modules_for, timed_out_sentence  # noqa: F401 — the CLI's handler, and tests read it here
from spark.build.build_service import BuildInputs, BuildService, vouches_for_a_build
from spark.build.kept_files import design_handed_to
from spark.build.stages import BUILD, CHECK_SPINE, CHECK_SPINE_CRASHED_ENDING, REQUIREMENTS, TIMED_OUT_ENDING
from spark.core.outcomes import NOT_CHECKED
from spark.design import loader
from spark.firmware import sim_project
from spark.records import store
from spark.sourcing import part_facts

#: The design the chain is proven against when nobody names one. A motor driver, a sensor on a
#: bus, and the power inlet that supplies the rail the modules only consume — the smallest set
#: that exercises pin assignment, a bus, a rail with an external source, and two footprint kinds.
REFERENCE = {"board": "firebeetle2-esp32s3",
             "parts": ["l9110s-module", "vl6180x-breakout", "jst-ph-2-power-inlet"]}


#: Result: the stages, the work folder (None when the requirements were refused), the requirements read and the
#: toolchain found (or None). The lines for the person went to `add_diagnostics` (P938).
RequirementsBuildResult = namedtuple("RequirementsBuildResult", "stages workdir requirements toolchain")


class RequirementsBuildService:
    """
    Service: the CLI's whole run of the chain for one requirements file, or the reference design: it reads the file,
    makes the work folder `spark-spine-*`, runs the stages of a `BuildService` and notes a build that ran end to end in
    the person's history. It is given `build_service`, an object with `for_toolchain` (BuildService, or a fake), and
    `note_built(design)`, which writes the history line (part_facts.note_built), each None for the real one. A refused
    file, a build past its limit and any crash of the stages are each one stage that could not run; an OSError from
    making the work folder or reading the toolchain and the kept files propagates, as it did from check_spine's main.
    It removes the work folder when it raises after making it (P939); one it returns, the caller (`BuildBoard`) removes.
    """

    def __init__(self, build_service=None, note_built=None):
        self.build_service, self.note_built = build_service, note_built

    def build(self, requirements_path=None, firmware=None, simulation=None, add_diagnostics=None):
        """A RequirementsBuildResult for the file at `requirements_path` (None: the reference design), the flash image
        `firmware` (None: the one the kept wokwi.toml in the folder `simulation` names) and that folder, or None. Each line
        for the person goes to `add_diagnostics(lines)` as it is said, so a crash later keeps it (P938)."""
        # Read AS input: a malformed file is a stage that could not run, not a traceback, and no folder is made.
        source = Path(requirements_path).resolve() if requirements_path else None
        try:
            requirements = loader.read(source) if source else dict(REFERENCE)
        except loader.DesignError as broken:
            return RequirementsBuildResult([REQUIREMENTS.stopped_by(broken)], None, None, None)
        # The project is the file's, up from its own folder; a file in no project is built from the plugin's library.
        project = loader.project_for(source) if source else None
        from_library = bool(source) and loader.is_library(project)
        workdir = Path(tempfile.mkdtemp(prefix="spark-spine-"))
        try:
            toolchain = self._work_folder(workdir, requirements, source)
            # What `built` will name is loaded now, once, before anything can change under it.
            handed = design_handed_to(workdir, project) if source and not from_library else None
            if simulation and (simulation / "diagram.json").is_file():  # P482: the build merges into a copy, never the person's file
                shutil.copy(simulation / "diagram.json", workdir / sim_project.KEPT_DIAGRAM)
            firmware, kept = self._firmware(firmware, simulation)
            stages = self._stages(toolchain, BuildInputs(requirements, workdir, project, from_library, firmware))
            if lines := self._firmware_line(kept, workdir):
                add_diagnostics(lines)
            # The history says a build ran end to end (§5.7), written by the chain itself; one it cannot keep is said, and the verdict stands.
            if handed is not None and vouches_for_a_build(stages):
                try:
                    # looked up at call time, so a test's patch of `part_facts.note_built` still reaches it
                    (self.note_built or part_facts.note_built)(handed)
                except (store.StoreError, OSError) as unrecorded:
                    add_diagnostics(["  the build was not recorded in your history: %s" % unrecorded])
            return RequirementsBuildResult(stages, workdir, requirements, toolchain)
        except BaseException:  # P939: a folder it returns, the caller removes after the keep step
            shutil.rmtree(workdir, ignore_errors=True)
            raise

    @staticmethod
    def _work_folder(workdir, requirements, source):
        """The toolchain found from the file's folder or the working directory, or None, with requirements.json written
        into `workdir`: tsci needs its toolchain reachable from the build folder, so its node_modules is linked in."""
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        toolchain = board_engine.find_toolchain(source.parent if source else Path.cwd())
        modules = modules_for(toolchain) if toolchain is not None else None
        if modules is not None and not (workdir / "node_modules").exists():
            os.symlink(modules, workdir / "node_modules")
        return toolchain

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
        service = self.build_service or BuildService
        try:
            return service.for_toolchain(toolchain).build(inputs)
        except (subprocess.TimeoutExpired, board_engine.TimedOutError) as late:  # the guard: BuildService keeps the stages for its own tools (P664)
            said = str(late) if isinstance(late, board_engine.TimedOutError) else timed_out_sentence(late)
            return [BUILD.ended(TIMED_OUT_ENDING, said)]
        except Exception as exc:  # noqa: BLE001
            # Anything unforeseen is could-not-run, never problems. An exception says this tool
            # failed, which is not the same as the chain failing, and reporting one as the other
            # sends somebody to debug a design that was never examined.
            return [CHECK_SPINE.ended(CHECK_SPINE_CRASHED_ENDING, type(exc).__name__, exc)]

    @staticmethod
    def _firmware_line(kept, workdir):
        """P429: the sentence, in a list, when the kept wokwi.toml's firmware line could not be read and the build wrote
        that file again, so the line is gone; else an empty list."""
        if kept is not None and kept.state == NOT_CHECKED and (workdir / "sim" / "wokwi.toml").is_file():
            return ["  sim/wokwi.toml %s The rebuild wrote it again with no image named, and a scenario run then names "
                    "the default one." % kept.why]
        return []
