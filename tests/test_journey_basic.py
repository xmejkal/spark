"""
The basic journey, end to end (P195, #154): the button-and-LED project through every stage that works today, so a stage
that breaks is named here and not found on the bench.

The stages are the replan's table (docs/2026-10-11-replan.md): the requirements, the build with its board, the Wokwi
diagram, the breadboard sheet and the pin map, then the PCB and 3D exports. Each later item of the v1 slice adds its stage to
STAGES. The build runs for real where `tsci` is found: the project's node_modules, then the PATH. Where it is not, the
build stage is could-not-run, and the skip names the stages that ran and the stages that did not.

    python3 -m unittest discover -s tests -p test_journey_basic.py
"""

import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_spine  # noqa: E402
import design  # noqa: E402

FIXTURE = ROOT / "tests" / "data" / "breadboard" / "button-light"

#: The spine's stages before the build: they need no board engine, so they run on every machine.
BEFORE_THE_BUILD = ("board", "schematic", "footprint")

#: The journey's stages whose files need no board engine: the pin map comes from the requirements alone (P196).
WITHOUT_THE_BUILD = ("requirements", "pin map")

#: The exports the replan lists as working (stage 8): tsci's format, and the file it writes.
EXPORTS = (("gerbers", "board-gerbers.zip"), ("glb", "board.glb"))

#: The longest one command of the walk may take. The whole walk took 11 s on 2026-10-11; this only stops a tool that
#: hangs from holding the suite.
COMMAND_TIMEOUT_S = 300


def _requirements(path):
    wanted = design.read(path)
    if wanted.get("board") != "firebeetle2-esp32s3" or wanted.get("parts") != ["tactile-button", "led-red-5mm"]:
        return "it no longer asks for the FireBeetle with a button and an LED"
    return None


def _board_file(path):
    return None if "<board" in path.read_text() else "it holds no <board>"


def _built(path):
    traces, errors = check_spine.count_in(json.loads(path.read_text()))
    if errors:
        return "%d error element(s) in it" % len(errors)
    return None if traces else "no pcb_trace in it: nothing joins the parts"


def _diagram(path):
    diagram = json.loads(path.read_text())
    lacking = {"wokwi-pushbutton", "wokwi-led"} - {part["type"] for part in diagram.get("parts", [])}
    if lacking:
        return "no %s in it" % ", ".join(sorted(lacking))
    return None if check_spine.wires_in(diagram) else "no wire in it"


def _sheet(path):
    # An end, not a mention: a resistor's own label names the part it serves ("R1 (10kΩ pull-up on TactileButton A)").
    ends = [end for line in re.findall(r"^\d+\. (.*)$", path.read_text(), re.MULTILINE) for end in line.split(" · ")]
    lacking = [name for name in ("TactileButton", "LedRed5mm") if not any(end.startswith(name + " ") for end in ends)]
    return "no wiring line has an end on %s" % " or ".join(lacking) if lacking else None


def _pins(path):
    # The firmware does `import pins`, so the file must run as Python and give the button and the LED a GPIO each.
    names = runpy.run_path(str(path))
    lacking = [name for name in ("BUTTON", "STATUS_LED") if not isinstance(names.get(name), int)]
    return "no GPIO for %s in it" % " or ".join(lacking) if lacking else None


def _gerbers(path):
    with zipfile.ZipFile(path) as fab:
        lacking = {"F_Cu.gbr", "Edge_Cuts.gbr"} - set(fab.namelist())
    return "no %s in it" % ", ".join(sorted(lacking)) if lacking else None


def _model(path):
    return None if path.read_bytes()[:4] == b"glTF" else "it does not start with glTF's magic bytes"


#: Each stage the journey reaches today: its name, a file it leaves in the project, and what that file must show.
#: Items 3-6 of the v1 slice each add a line.
STAGES = (
    ("requirements", "requirements.json", _requirements),
    ("build", "board.tsx", _board_file),
    ("build", "dist/board/circuit.json", _built),
    ("Wokwi diagram", "sim/diagram.json", _diagram),
    ("breadboard sheet", "breadboard.md", _sheet),
    ("pin map", "firmware/pins.py", _pins),
    ("PCB export", "board-gerbers.zip", _gerbers),
    ("3D export", "board.glb", _model),
)


def broken_stages(project):
    """Each stage whose file is missing, unreadable or wrong, as 'stage: why'; empty when the journey holds."""
    broken = []
    for stage, output, holds in STAGES:
        path = project / output
        if not path.is_file():
            broken.append("%s: no %s" % (stage, output))
            continue
        try:
            why = holds(path)
        except (OSError, ValueError, KeyError, AttributeError, TypeError, zipfile.BadZipFile,
                design.DesignError) as unreadable:
            why = "%s cannot be read: %s" % (output, unreadable)
        if why:
            broken.append("%s: %s" % (stage, why))
    return broken


def walk(project):
    """
    The journey's commands in `project`, as a person runs them: the one build command (commands/build.md), which keeps
    the simulation project too (JB1), then each export with the same tsci. The spine's verdict, as its --json prints it, with each
    export that failed and tsci's last words under `exports failed`.
    """
    spine = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_spine.py"), "requirements.json",
         "--keep", ".", "--json"],
        cwd=str(project), capture_output=True, text=True, timeout=COMMAND_TIMEOUT_S)
    try:
        verdict = json.loads(spine.stdout)
    except ValueError:  # a spine that printed no verdict: what it said instead is the failure's reason
        verdict = {"status": "crashed", "stages": [{"name": "check_spine", "status": "crashed",
                                                     "detail": spine.stderr.strip()[-800:] or "no output"}]}
    toolchain = check_spine.find_toolchain(project)
    if toolchain is None or not any(s["name"] == "build" and s["status"] == check_spine.OK for s in verdict["stages"]):
        return verdict
    modules = check_spine.modules_for(toolchain)
    if modules is not None:
        os.symlink(modules, project / "node_modules")
    verdict["exports failed"] = {}
    for export_format, output in EXPORTS:
        exported = subprocess.run([str(toolchain), "export", "-f", export_format, "board.tsx", "-o", output],
                                  cwd=str(project), capture_output=True, text=True, timeout=COMMAND_TIMEOUT_S)
        if exported.returncode != 0:
            verdict["exports failed"][output] = (exported.stderr or exported.stdout).strip()[-400:]
    return verdict


class TheBasicJourneyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The store is a scratch one already: store.py swaps it in for any process running unittest (P88).
        cls.project = Path(tempfile.mkdtemp()) / "button-light"
        cls.project.mkdir()
        shutil.copy(FIXTURE / "requirements.json", cls.project)
        cls.verdict = walk(cls.project)

    def stage(self, name):
        return next((stage for stage in self.verdict["stages"] if stage["name"] == name), {})

    def skip_without_the_build(self):
        # Only a missing board engine is a skip. One that is installed and cannot build is a failure: JB2 was one.
        if check_spine.find_toolchain(self.project) is not None:
            return
        build = self.stage("build")
        ran = list(WITHOUT_THE_BUILD) + [stage["name"] for stage in self.verdict["stages"] if stage["status"] == check_spine.OK]
        later = dict.fromkeys(stage for stage, _, _ in STAGES if stage not in WITHOUT_THE_BUILD)
        self.skipTest("build: %s (%s). Ran: %s. Not run: %s"
                      % (build.get("status"), (build.get("detail") or "no build stage").splitlines()[0],
                         ", ".join(ran), ", ".join(later)))

    def test_the_stages_before_the_build_run_on_every_machine(self):
        self.assertEqual([entry for entry in broken_stages(self.project) if entry.split(":")[0] in WITHOUT_THE_BUILD], [])
        for name in BEFORE_THE_BUILD:
            with self.subTest(stage=name):
                self.assertEqual(self.stage(name).get("status"), check_spine.OK, self.verdict)

    def test_the_kept_pin_map_is_what_emit_pins_writes(self):
        # The card's measure (P196): the build's pins.py and `assign_pins.py requirements.json --emit-pins` agree.
        emitted = Path(tempfile.mkdtemp()) / "pins.py"
        subprocess.run([sys.executable, str(ROOT / "scripts" / "assign_pins.py"), "requirements.json", "--emit-pins",
                        str(emitted)], cwd=str(self.project), capture_output=True, timeout=COMMAND_TIMEOUT_S)
        self.assertEqual((self.project / "firmware" / "pins.py").read_text(), emitted.read_text())

    def test_every_stage_leaves_what_the_next_one_reads(self):
        self.skip_without_the_build()
        self.assertEqual(self.verdict["status"], check_spine.OK, self.verdict)
        self.assertEqual(broken_stages(self.project), [], self.verdict)

    def test_removing_any_stage_s_file_names_that_stage(self):
        # The card's proof: this test is only worth its run time if it goes red, by name, when a stage stops writing.
        self.skip_without_the_build()
        self.assertEqual(broken_stages(self.project), [], "the walk did not finish, so removing a file proves nothing")
        for stage, output, _ in STAGES:
            with self.subTest(output=output):
                copy = Path(tempfile.mkdtemp()) / "button-light"
                shutil.copytree(self.project, copy, symlinks=True)
                (copy / output).unlink(missing_ok=True)  # one already missing is the test above's failure
                self.assertEqual(broken_stages(copy), ["%s: no %s" % (stage, output)])


if __name__ == "__main__":
    unittest.main()
