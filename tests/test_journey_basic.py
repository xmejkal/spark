"""
The basic journey, end to end (P195, #154): the button-and-LED project through every stage that works today, so a stage
that breaks is named here and not found on the bench.

The stages are the replan's table (docs/2026-10-11-replan.md): the requirements, the build with its board, the Wokwi
diagram, the breadboard sheet and the pin map, the firmware imported with the `machine` stand-in (P59), then the PCB and 3D
exports, every deterministic check on the fresh project (P197), and the scenario run by the Wokwi harness (P130), with
a fake wokwi-cli so the suite spends no Wokwi minute. Each later item of the v1 slice adds its stage to STAGES. The build runs for real where `tsci` is found: the project's node_modules, then the PATH. Where it is not, the
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
import unittest.mock
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_spine  # noqa: E402
import design  # noqa: E402
import run_scenario  # noqa: E402

FIXTURE = ROOT / "tests" / "data" / "breadboard" / "button-light"
#: The firmware a person (or the conversation) writes once the pin map exists (P59): main.py over light.py.
FIRMWARE_FIXTURE = FIXTURE / "firmware"
#: The scenario the conversation wrote from the person's words (P130), and wokwi-cli as the suite runs it: faked.
SCENARIO_FIXTURE = FIXTURE / "scenarios" / "the-button-lights-the-led.scenario.yaml"
FAKE_WOKWI_CLI = [sys.executable, str(ROOT / "tests" / "fake_wokwi_cli.py")]
#: The image the build's wokwi.toml names once the harness names one: commands/build.md's flash-with-firmware.bin.
FLASH_IMAGE = "flash-with-firmware.bin"
#: The stand-in `machine` the firmware imports under, put first on the path of a process of its own (never this one's).
STAND_IN = ROOT / "scripts" / "stand_in"

#: The spine's stages before the build: they need no board engine, so they run on every machine.
BEFORE_THE_BUILD = ("board", "schematic", "footprint")

#: The journey's stages whose files need no board engine: the pin map comes from the requirements alone (P196), and the
#: firmware needs only the pin map (P59).
WITHOUT_THE_BUILD = ("requirements", "pin map", "firmware")

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
    if lacking:
        return "no GPIO for %s in it" % " or ".join(lacking)
    return None if names.get("BUTTON_PULL") == "up" else "no BUTTON_PULL = \"up\": the firmware does not know to pull it up"


#: Run in a process of its own: the LED's level with the button released, then pressed. Released, nothing sets the pin:
#: only the firmware's internal pull-up holds it high (P204). A press joins it to ground, so pressed is 0.
LIGHT_PROBE = """
import machine, light, pins
light.update()
print(machine.level(pins.STATUS_LED))
machine.set_level(pins.BUTTON, 0)
light.update()
print(machine.level(pins.STATUS_LED))
"""


def _firmware(path):
    # The LED lights while the button is held: imports under the stand-in, then reads 0 released and 1 pressed.
    if not (path.parent / "pins.py").is_file():
        return None  # light.py reads the pin map, and the pin map stage names its absence
    done = subprocess.run([sys.executable, "-B", "-c", "import sys; sys.path[:0] = sys.argv[1:]\n" + LIGHT_PROBE,
                           str(STAND_IN), str(path.parent)], capture_output=True, text=True, timeout=COMMAND_TIMEOUT_S)
    if done.returncode != 0:
        return "it does not import under the stand-in: %s" % (done.stderr.strip().splitlines() or ["no reason given"])[-1]
    released, pressed = done.stdout.split()
    if released != "0":
        return "with the button released the LED reads %s, not 0" % released
    return None if pressed == "1" else "with the button pressed the LED reads %s, not 1" % pressed


def _run_log(path):
    # P130: the harness ran the project's scenario, and passed, on an image of the project's own firmware.
    text = path.read_text()
    if "verdict: passed" not in text:
        return "the run did not pass: %s" % text.splitlines()[1]
    image = path.parent.parent / FLASH_IMAGE
    return None if b"light.run()" in image.read_bytes() else "the flash image does not hold the project's main.py"


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
    ("firmware", "firmware/light.py", _firmware),
    ("Wokwi run", "sim/runs/the-button-lights-the-led.log", _run_log),
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


def write_the_firmware(project):
    """What a person does once the pin map exists: the button-and-LED firmware goes into firmware/ beside pins.py."""
    (project / "firmware").mkdir(exist_ok=True)
    for source in sorted(FIRMWARE_FIXTURE.glob("*.py")):
        shutil.copy(source, project / "firmware")


def run_the_scenario(project):
    """The scenario goes into sim/scenarios/ and the harness runs it, as a person does, with a fake wokwi-cli and interpreter."""
    if not (project / "sim").is_dir():
        return  # no build, no simulation project: the build stage names it
    (project / "sim" / "scenarios").mkdir(exist_ok=True)
    scenario = Path(shutil.copy(SCENARIO_FIXTURE, project / "sim" / "scenarios"))
    interpreter = Path(tempfile.mkdtemp()) / "micropython.bin"
    interpreter.write_bytes(b"\xe9" + b"\x00" * 999)
    with unittest.mock.patch.dict(os.environ, {"FAKE_WOKWI_SERIAL": "ready\nLED on\nLED off\n"}):
        run_scenario.run(project, scenario, FAKE_WOKWI_CLI, micropython=interpreter)


class TheFirmwareStageBitesTest(unittest.TestCase):
    """
    The firmware stage's own check goes red for a wrong firmware (F3, P59). The journey above only proves the fixture
    passes, so a `_firmware` that returned None would have kept it green. These run on every machine: no build needed.
    """

    @staticmethod
    def light_with(old=None, new=None, pins=True):
        """The fixture's light.py with one change, beside a pins.py unless told not to; returns the path to light.py."""
        folder = Path(tempfile.mkdtemp()) / "firmware"
        folder.mkdir()
        if pins:
            (folder / "pins.py").write_text("BUTTON = 4\nSTATUS_LED = 5\n")
        source = (FIRMWARE_FIXTURE / "light.py").read_text()
        assert old is None or old in source, "the fixture no longer holds %r" % old
        (folder / "light.py").write_text(source if old is None else source.replace(old, new))
        return folder / "light.py"

    def test_the_fixture_firmware_passes(self):
        self.assertIsNone(_firmware(self.light_with()))

    def test_an_led_lit_with_the_button_released_is_named(self):
        light = self.light_with("LED_ON, LED_OFF = 1, 0", "LED_ON, LED_OFF = 0, 1")
        self.assertEqual(_firmware(light), "with the button released the LED reads 1, not 0")

    def test_an_led_that_never_lights_is_named(self):
        light = self.light_with("    led.value(LED_ON if lit else LED_OFF)", "    pass")
        self.assertEqual(_firmware(light), "with the button pressed the LED reads 0, not 1")

    def test_a_firmware_that_does_not_pull_the_button_up_is_named(self):
        light = self.light_with("Pin.IN, Pin.PULL_UP)", "Pin.IN)")
        self.assertEqual(_firmware(light), "with the button released the LED reads 1, not 0")

    def test_a_firmware_that_does_not_import_is_named_with_its_exception(self):
        light = self.light_with("import time\n", "import time\nraise OSError('no bus')\n")
        self.assertEqual(_firmware(light), "it does not import under the stand-in: OSError: no bus")

    def test_without_the_pin_map_the_pin_map_stage_names_it_and_this_one_says_nothing(self):
        self.assertIsNone(_firmware(self.light_with(pins=False)))


class TheRunStageBitesTest(unittest.TestCase):
    """The Wokwi run stage's own check goes red, as the firmware stage's does: a fake that always passes proves nothing alone."""

    @staticmethod
    def log_with(verdict="passed", main=b"import light\nlight.run()\n"):
        runs = Path(tempfile.mkdtemp()) / "sim" / "runs"
        runs.mkdir(parents=True)
        (runs.parent / FLASH_IMAGE).write_bytes(b"\xff" * 64 + main)
        (runs / "the-button-lights-the-led.log").write_text("# the run\nverdict: %s\n" % verdict)
        return runs / "the-button-lights-the-led.log"

    def test_a_passed_run_on_the_project_s_firmware_passes(self):
        self.assertIsNone(_run_log(self.log_with()))

    def test_a_failed_run_is_named_with_its_verdict(self):
        self.assertEqual(_run_log(self.log_with("timed out")), "the run did not pass: verdict: timed out")

    def test_an_image_without_the_project_s_main_py_is_named(self):
        self.assertEqual(_run_log(self.log_with(main=b"")), "the flash image does not hold the project's main.py")


class TheBasicJourneyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The store is a scratch one already: store.py swaps it in for any process running unittest (P88).
        cls.project = Path(tempfile.mkdtemp()) / "button-light"
        cls.project.mkdir()
        shutil.copy(FIXTURE / "requirements.json", cls.project)
        cls.verdict = walk(cls.project)
        write_the_firmware(cls.project)
        run_the_scenario(cls.project)

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

    def test_the_firmware_imports_with_the_stand_in_and_main_py_is_left_unrun(self):
        # P59: the one command, as a person runs it, on the project after the walk.
        done = subprocess.run([sys.executable, str(ROOT / "scripts" / "import_firmware.py"), "--json"],
                              cwd=str(self.project), capture_output=True, text=True, timeout=COMMAND_TIMEOUT_S)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(sorted(entry["module"] for entry in json.loads(done.stdout)["modules"]), ["light", "pins"])

    def test_every_stage_leaves_what_the_next_one_reads(self):
        self.skip_without_the_build()
        self.assertEqual(self.verdict["status"], check_spine.OK, self.verdict)
        self.assertEqual(broken_stages(self.project), [], self.verdict)

    def test_a_fresh_project_gets_a_clean_check(self):
        # P197: init after the build, as commands/init.md says, then every deterministic check, as a person runs them.
        # Exit 0 must come from checks that looked: none could-not-run, physics among them, and the `?` lines counted.
        self.skip_without_the_build()
        copy = Path(tempfile.mkdtemp()) / "button-light"
        shutil.copytree(self.project, copy, symlinks=True)
        init = subprocess.run([sys.executable, str(ROOT / "scripts" / "init_project.py"), "--project", ".",
                               "--board", "firebeetle2-esp32s3"],
                              cwd=str(copy), capture_output=True, text=True, timeout=COMMAND_TIMEOUT_S)
        self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
        checked = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_all.py"), "--project", ".", "--json"],
                                 cwd=str(copy), capture_output=True, text=True, timeout=COMMAND_TIMEOUT_S)
        answer = json.loads(checked.stdout)
        self.assertEqual((checked.returncode, answer["status"]), (0, check_spine.OK), checked.stdout[-3000:])
        statuses = {result["check"]: result["status"] for result in answer["results"]}
        self.assertNotIn("could-not-run", statuses.values(), statuses)
        # "Never from skipping": the fab package's check is the only one a fresh project may not be asked.
        self.assertLessEqual({check for check, status in statuses.items() if status == "skipped"}, {"the-order"},
                             statuses)
        self.assertEqual(statuses["physics"], check_spine.OK, "physics must look, not be skipped")
        self.assertIsInstance(answer["unmeasured"], int, "P108: the ok says how many values it rests on")
        rules = next(result for result in answer["results"] if result["check"] == "rules-vs-netlist")
        self.assertIn("TactileButton.A: held up by the board's internal pull-up", " ".join(rules.get("unmeasured", [])),
                      "P204: the firmware's pull-up is said, since no netlist shows it")

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
