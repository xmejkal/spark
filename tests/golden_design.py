"""
The design-with-build goldens (P699, #946, W6-D1): what assign_pins.py, emit_board.py, emit_footprint.py, check_spine.py
and init_project.py print today, and what `check_spine.py --keep` writes, kept in tests/golden-design/.

A helper module beside golden_checks.py, no tests in it: tests/test_golden_design.py runs each Case with
golden_firmware's run_script, in its own copy of golden_checks' project (the button-light fixture after init_project.py),
or of the bare fixture for a `fresh` Case. `SPARK_ACCEPT=check-spine python3 -m unittest tests.test_golden_design`
writes check_spine.py's goldens from today's output and fails, so that a person reads `git diff tests/golden-design`.

No golden runs a real tool. A child's PATH is the fakes' folder alone, its proxies a closed port, and it carries no
WOKWI_CLI_TOKEN (golden_checks.child_env). The project's tools list names the board engine and the diagram converter
as the two fakes, with no other place to look and no needs: tools.find looks for bun and node first, and finds neither
on that PATH. It names wokwi-cli with no place to look but that PATH, where it is not. The fake tsci and the
converter's shim call /bin/mkdir, /bin/cp and this Python by their absolute paths, so they run on that PATH.

The reference design (check_spine.py with no argument) is built from the plugin's folder, where the project's tools list
does not apply. Its Case stops at the converter, which the child's store does not name, so the design's two chips are
never staged: a chip's binary older than its source in a checkout would run `wokwi-cli chip compile`.
"""

import json
import shlex
import shutil
import sys
from collections import namedtuple
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden_bench  # noqa: E402
import golden_checks  # noqa: E402
import golden_firmware  # noqa: E402
from fakes import fake_tsci  # noqa: E402
from golden_firmware import LOG_MARK  # noqa: E402

ROOT = golden_bench.ROOT
GOLDEN_DIR = ROOT / "tests" / "golden-design"
PROJECT = golden_firmware.PROJECT
BOARD_ID = golden_checks.BOARD_ID
CIRCUIT = golden_checks.CIRCUIT
REQUIREMENTS = "requirements.json"
#: The two fakes in the fakes' folder. Not called tsci or circuit-to-wokwi, so a name looked up on the PATH finds nothing.
TSCI = "fake-tsci"
CONVERTER = "fake-circuit-to-wokwi"
CONVERTER_SHIM = """#!/bin/sh
# The golden net's diagram converter (P699): the fake, run by this Python, both by an absolute path.
exec %s "$@"
"""
#: What the fake tsci touches each time it builds, so a test can tell that it ran.
BUILT_MARKER = "tsci-built"
#: Placed in a Case's env: the folder that holds the fakes' folder, the canned circuits and the marker.
FAKES = "{fakes}"
#: The fixture keeps no copper: one pcb_trace per source_trace, which the fake tsci adds to what it builds.
BUILD_TRACES = [{"type": "pcb_trace", "pcb_trace_id": "pcb_trace_%d" % n, "route": []} for n in range(9)]
#: The built circuit with two errors added, which the fake tsci builds when FAKE_TSCI_CIRCUIT names it.
ERRORED_CIRCUIT = "errored-circuit.json"
#: What the fake tsci builds for the reference design (check_spine.REFERENCE): its three supplies, as
#: emit_board.supply_inputs states them, each component grounded, and copper, so that no island stops the build.
REFERENCE_CIRCUIT = "reference-circuit.json"
REFERENCE_FEEDS = (("Mcu", "3V3", "V33"), ("L9110sModule", "VCC", "MOTOR6V"), ("Vl6180xBreakout", "VIN", "V33"))


def fed_circuit(feeds):
    """A circuit.json of `feeds`, (component, pin, net) each, every component's GND on net GND, and BUILD_TRACES."""
    nets = {name: "source_net_%d" % n for n, name in enumerate(dict.fromkeys(["GND"] + [net for _, _, net in feeds]))}
    elements = [{"type": "source_net", "source_net_id": net_id, "name": name} for name, net_id in nets.items()]
    for n, (component, pin, net) in enumerate(feeds):
        elements.append({"type": "source_component", "source_component_id": "source_component_%d" % n,
                         "ftype": "simple_chip", "name": component})
        for port, on in ((pin, net), ("GND", "GND")):
            port_id = "source_port_%d_%s" % (n, port)
            elements += [{"type": "source_port", "source_port_id": port_id, "name": port, "port_hints": [port],
                          "source_component_id": "source_component_%d" % n},
                         {"type": "source_trace", "source_trace_id": "source_trace_%d_%s" % (n, port),
                          "connected_source_port_ids": [port_id], "connected_source_net_ids": [nets[on]]}]
    return elements + BUILD_TRACES
BUILD_ERRORS = [{"type": "source_trace_not_connected_error", "message": "Could not find port",
                 "selectors_not_found": [".BTN1 > .pin1"]},
                {"type": "pcb_trace_error", "message": "a trace crosses another"}]

#: The library's board record with no footprint to export, planted as the project's own.
NO_FOOTPRINT_BOARD = json.loads((ROOT / golden_checks.BOARD_FILE).read_text())
NO_FOOTPRINT_BOARD["physical"] = {key: value for key, value in NO_FOOTPRINT_BOARD["physical"].items()
                                  if key != "footprint_export"}
NO_FOOTPRINT = ((golden_checks.BOARD_FILE, json.dumps(NO_FOOTPRINT_BOARD, indent=2)),)


def requirements(**fields):
    """A requirements.json planted in the project: the firebeetle board and `fields`."""
    return ((REQUIREMENTS, json.dumps(dict({"board": BOARD_ID}, **fields), indent=2)),)


#: Value. golden_firmware's Case, and `fresh`: the Case runs in a bare copy of the fixture, before init_project.py;
#: `written`: files under the project that the run writes, each added to the golden after LOG_MARK.
Case = namedtuple("Case", golden_firmware.Case._fields + ("fresh", "written"), defaults=((), {}, False, ()))
CASES = [
    Case("assign-pins-ok.json", "assign_pins.py", [REQUIREMENTS, "--json"], 0),
    Case("assign-pins-ok.txt", "assign_pins.py", [REQUIREMENTS], 0),
    Case("assign-pins-problems-impossible.txt", "assign_pins.py", [REQUIREMENTS], 1,
         requirements(parts=[{"part": "led-red-5mm", "name": "Led%d" % n} for n in range(24)])),
    Case("assign-pins-could-not-run-no-requirements.txt", "assign_pins.py", ["missing.requirements.json"], 2),
    Case("emit-board-ok.txt", "emit_board.py", [REQUIREMENTS], 0),
    Case("emit-board-could-not-run-no-footprint.txt", "emit_board.py", [REQUIREMENTS], 2, NO_FOOTPRINT),
    Case("emit-board-could-not-run-refused.txt", "emit_board.py", [REQUIREMENTS], 2,
         requirements(parts=[{"part": "tactile-button", "name": "Btn"}, {"part": "led-red-5mm", "name": "btn"}])),
    Case("emit-footprint-ok.json", "emit_footprint.py", ["--board", BOARD_ID, "--project", PROJECT, "-o", "fp.tsx",
                                                         "--json"], 0),
    Case("emit-footprint-could-not-run-no-footprint.txt", "emit_footprint.py", ["--board", BOARD_ID, "--project", PROJECT],
         2, NO_FOOTPRINT),
    Case("check-spine-ok.json", "check_spine.py", [REQUIREMENTS, "--json"], 0),
    Case("check-spine-ok-keep.txt", "check_spine.py", [REQUIREMENTS, "--keep", "."], 0,
         written=("firmware/pins.py", "sim/diagram.json", "sim/wokwi.toml")),
    Case("check-spine-problems-build.txt", "check_spine.py", [REQUIREMENTS], 1,
         env={"FAKE_TSCI_CIRCUIT": FAKES + "/" + ERRORED_CIRCUIT}),
    Case("check-spine-could-not-run-no-tsci.txt", "check_spine.py", [REQUIREMENTS], 2,
         ((".spark/tools.json", json.dumps({"tscircuit": {"kind": "path", "exe": "tsci", "also": [], "needs": []}})),)),
    Case("check-spine-could-not-run-requirements.txt", "check_spine.py", [REQUIREMENTS], 2, ((REQUIREMENTS, "{not json"),)),
    Case("check-spine-ok-board-only.json", "check_spine.py", [REQUIREMENTS, "--json"], 0, requirements(board_only=True)),
    Case("check-spine-could-not-run-reference.json", "check_spine.py", ["--json"], 2,
         env={"FAKE_TSCI_CIRCUIT": FAKES + "/" + REFERENCE_CIRCUIT}),
    Case("init-project-ok.txt", "init_project.py", ["--project", PROJECT, "--board", BOARD_ID, "--circuit", CIRCUIT], 0,
         fresh=True),
    Case("init-project-nothing-to-do.txt", "init_project.py", ["--project", PROJECT], 1),
    Case("init-project-could-not-run-no-board.txt", "init_project.py", ["--project", PROJECT, "--board", "no-such-board"],
         2),
]


def make_fakes(folder):
    """The fake tsci and the converter's shim, in a `bin` folder in `folder`, beside the canned circuits. The fake builds
    the fixture's circuit with BUILD_TRACES, and touches BUILT_MARKER in `folder`. Returns the `bin` folder, a child's whole PATH."""
    folder = Path(folder)
    shims = folder / "bin"
    shims.mkdir(exist_ok=True)
    circuit = json.loads((golden_checks.FIXTURE / CIRCUIT).read_text()) + BUILD_TRACES
    (folder / ERRORED_CIRCUIT).write_text(json.dumps(circuit + BUILD_ERRORS))
    (folder / REFERENCE_CIRCUIT).write_text(json.dumps(fed_circuit(REFERENCE_FEEDS)))
    fake_tsci(folder, ": >> %s" % shlex.quote(str(folder / BUILT_MARKER)), circuit, binary=shims / TSCI)
    fake = " ".join(shlex.quote(part) for part in (sys.executable, str(ROOT / "tests" / "fake_converter.py")))
    (shims / CONVERTER).write_text(CONVERTER_SHIM % fake)
    (shims / CONVERTER).chmod(0o755)
    return shims


def fakes_named(shims):
    """The tools list that names the two fakes in `shims`, and wokwi-cli as a name on the PATH alone: no other place to
    look, no fetch, and no needs."""
    named = {tool: {"kind": "path", "exe": str(Path(shims) / exe), "also": [], "fetch": None, "needs": []}
             for tool, exe in (("tscircuit", TSCI), ("circuit-to-wokwi", CONVERTER))}
    return dict(named, **{"wokwi-cli": {"kind": "path", "exe": "wokwi-cli", "also": [], "fetch": None}})


def build_project(folder, shims):
    """golden_checks' project, whose tools list names the fakes in `shims`. Returns the project's Path."""
    project = golden_checks.build_project(folder, shims)
    (project / ".spark" / "tools.json").write_text(json.dumps(fakes_named(shims), indent=2))
    return project


def copy_project(case, built, work):
    """`case`'s project in `work`: a copy of `built`, or of the bare fixture for a fresh Case. Returns its Path."""
    project = Path(work) / built.name
    shutil.copytree(golden_checks.FIXTURE if case.fresh else built, project)
    return project


def run_case(case, project, store, shims):
    """The text of `case` run in `project` (golden_firmware.run_script, with golden_checks' child env), then each of its
    `written` files after LOG_MARK, and its exit code."""
    fakes = str(Path(shims).parent)
    case = case._replace(env={name: value.replace(FAKES, fakes) for name, value in case.env.items()})
    code, text = golden_firmware.run_script(case, project, store, golden_checks.child_env(store, shims))
    for name in case.written:
        text += LOG_MARK % name + (Path(project) / name).read_text()
    return code, text


def places(project, store, shims):
    """What a run's text is scrubbed of: golden_bench's places and the fakes' folder, longest first."""
    found = dict(golden_bench.replacements_of(project, store))
    for form in (str(Path(shims).parent), str(Path(shims).parent.resolve())):
        found[form] = "<fakes>"
    return dict(sorted(found.items(), key=lambda item: -len(item[0])))
