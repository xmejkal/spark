#!/usr/bin/env python3
"""
Every deterministic check, in one call, with one answer.

    check_all.py --circuit dist/board/circuit.json --rules .spark/rules.json
    check_all.py --design design.json --boards boards/*.json --package fab.zip --json

There are seven checks in this plugin and the review loop invoked one of them. That is the
predictable outcome of a skill listing commands: the list is written once and the scripts keep
arriving. So the list lives here, next to the scripts, and everything else asks this.

WHAT IT IS FOR
A caller that is not a person. One command, one JSON document, one exit code — so an agent can
run the whole deterministic half of a review without knowing what the deterministic half
contains, and so adding a check does not mean editing a skill.

THE DISTINCTION THAT MATTERS
Three outcomes, not two, and the third is the one that gets lost:

  ok             it ran and found nothing
  problems       it ran and found something
  could-not-run  it was given what it needs and still could not look

and separately `skipped`, for a check whose inputs were not offered at all. Those last two are
routinely conflated, and the conflation is dangerous in one direction only: a check that could
not look reports zero problems, which reads exactly like a clean board. An eval on this project
once scored zero on every run because its fixtures were outside the sandbox, and the obvious
reading was that the reviewer did not work.

So `skipped` is silent about the board and exits 0, because you chose not to run it.
`could-not-run` exits non-zero, because you asked and got no answer.
"""

import argparse
import importlib.util
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent

EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN = 0, 1, 2

OK, PROBLEMS, COULD_NOT_RUN, SKIPPED = "ok", "problems", "could-not-run", "skipped"


def load(module_name):
    """Import a sibling script by filename, so this file is the only place they are named."""
    spec = importlib.util.spec_from_file_location(module_name, SCRIPTS / (module_name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Check:
    """
    One deterministic check, and what it needs to run.

    `needs` names the inputs; a check whose inputs were not supplied is SKIPPED rather than
    passed, and says so, because "I was not asked" and "I found nothing" are different.
    """

    def __init__(self, name, needs, what):
        self.name, self.needs, self.what = name, needs, what

    def run(self, inputs):
        missing = [need for need in self.needs if not inputs.get(need)]
        if missing:
            return {"check": self.name, "status": SKIPPED, "what": self.what,
                    "reason": "not given %s" % ", ".join(missing)}
        try:
            return dict({"check": self.name, "what": self.what}, **self.call(inputs))
        except Exception as broken:  # noqa: BLE001 - one broken check must not hide the others
            return {"check": self.name, "status": COULD_NOT_RUN, "what": self.what,
                    "reason": "%s: %s" % (type(broken).__name__, broken)}


def findings_result(findings, describe=lambda f: f):
    problems = [describe(f) for f in findings]
    return {"status": PROBLEMS if problems else OK, "problems": problems}


class PinCapability(Check):
    def call(self, inputs):
        check_design = load("check_design")
        result = check_design.check(inputs["design"], inputs.get("board"))
        return {"status": PROBLEMS if result.get("problems") else OK,
                "problems": [str(p) for p in result.get("problems", [])]}


class RulesVsNetlist(Check):
    def call(self, inputs):
        compare_design = load("compare_design")
        result = compare_design.compare(inputs["circuit"], inputs["rules"])
        status = {"ok": OK, "problems": PROBLEMS,
                  "could-not-run": COULD_NOT_RUN}[result["status"]]
        return {"status": status,
                "problems": [p["detail"] for p in result.get("problems", [])],
                "reason": result.get("reason")}


class Physics(Check):
    def call(self, inputs):
        check_physics = load("check_physics")
        findings = check_physics.run(json.loads(Path(inputs["circuit"]).read_text()),
                                     json.loads(Path(inputs["rules"]).read_text()))
        problems = [f for f in findings if f.severity == "problem"]
        return {"status": PROBLEMS if problems else OK,
                "problems": ["%s: %s" % (f.subject, f.detail) for f in problems],
                "unmeasured": ["%s: %s" % (f.subject, f.detail)
                               for f in findings if f.severity == "needs-measurement"]}


class Buildability(Check):
    def call(self, inputs):
        check_footprints = load("check_footprints")
        findings = check_footprints.run(json.loads(Path(inputs["circuit"]).read_text()))
        return findings_result(findings, lambda f: "%s: %s" % (f.subject, f.detail))


class VendorTruth(Check):
    def call(self, inputs):
        check_vendor_pins = load("check_vendor_pins")
        problems, unchecked = [], []
        for path in inputs["boards"]:
            result = check_vendor_pins.check_board(Path(path), offline=True, repo="")
            if result["status"] == "could-not-run":
                unchecked.append("%s: %s" % (result["board"], result["reason"]))
            else:
                problems += ["%s: %s" % (result["board"], p)
                             for p in result.get("problems", [])]
        return {"status": PROBLEMS if problems else OK,
                "problems": problems, "unmeasured": unchecked}


class Firmware(Check):
    def call(self, inputs):
        check_firmware = load("check_firmware")
        source = Path(inputs["firmware"]).read_text()
        constants = check_firmware.read_pin_constants(source)
        if not constants:
            return {"status": COULD_NOT_RUN,
                    "reason": "no PIN_* constants in %s — nothing to compare, which is not the "
                              "same as agreeing" % Path(inputs["firmware"]).name}
        board = json.loads(Path(inputs["board_file"]).read_text())
        return findings_result(check_firmware.check_against_board(constants, board))


class TheOrder(Check):
    def call(self, inputs):
        check_bom = load("check_bom")
        rows = check_bom.read_bom(Path(inputs["package"]))
        problems = (check_bom.check_duplicate_parts(rows)
                    + check_bom.check_missing_parts(rows))
        if inputs.get("circuit"):
            problems += check_bom.check_design_warnings(Path(inputs["circuit"]))
        return {"status": PROBLEMS if problems else OK, "problems": problems}


#: Ordered by how much a miss costs, so the first thing a reader sees is the most expensive.
CHECKS = [
    VendorTruth("vendor-truth", ["boards"],
                "the board definition matches the vendor's own pin header"),
    Buildability("buildability", ["circuit"],
                 "holes take their pins, packages hold their values"),
    TheOrder("the-order", ["package"],
             "the fab package orders the parts the schematic specifies"),
    Physics("physics", ["circuit", "rules"],
            "the board obeys physics, not just itself"),
    RulesVsNetlist("rules-vs-netlist", ["circuit", "rules"],
                   "written rules hold in the design that was built"),
    Firmware("firmware-vs-board", ["firmware", "board_file"],
             "every pin the firmware drives is one this board can do it with"),
    PinCapability("pin-capability", ["design"],
                  "every pin can do what it is being asked to do"),
]


def run(inputs):
    return [check.run(inputs) for check in CHECKS]


def render(results):
    lines = []
    for result in results:
        marker = {OK: "ok  ", PROBLEMS: "FAIL", COULD_NOT_RUN: "????",
                  SKIPPED: "--  "}[result["status"]]
        lines.append("  [%s] %-18s %s" % (marker, result["check"], result["what"]))
        if result["status"] == SKIPPED:
            continue
        if result.get("reason"):
            lines.append("           %s" % result["reason"])
        for problem in result.get("problems", []):
            lines.append("           - %s" % problem)
        for note in result.get("unmeasured", []):
            lines.append("           ? %s" % note)

    problems = sum(len(r.get("problems", [])) for r in results)
    unchecked = [r["check"] for r in results if r["status"] == COULD_NOT_RUN]
    skipped = [r["check"] for r in results if r["status"] == SKIPPED]

    lines.append("")
    if unchecked:
        lines.append("  %d check(s) could not look: %s" % (len(unchecked), ", ".join(unchecked)))
    if skipped:
        lines.append("  %d not asked for: %s" % (len(skipped), ", ".join(skipped)))
    lines.append("  %s" % ("%d problem(s)" % problems if problems
                           else "nothing found by the checks that ran"))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_all.py",
        description="Run every deterministic check and answer once.")
    parser.add_argument("--design", help="a design description, for the pin-capability check")
    parser.add_argument("--board", help="the board definition that design is built around")
    parser.add_argument("--board-file", help="a board definition, for the firmware check")
    parser.add_argument("--firmware", help="a firmware file holding PIN_* constants")
    parser.add_argument("--boards", nargs="*", default=[],
                        help="board definitions to verify against their vendor headers")
    parser.add_argument("--circuit", help="the built netlist")
    parser.add_argument("--rules", help="the project's rules file")
    parser.add_argument("--package", help="the exported fab package")
    parser.add_argument("--json", action="store_true", help="for a caller that is not a person")
    args = parser.parse_args(argv)

    results = run(vars(args))
    print(json.dumps({"tool": "check_all", "results": results}, indent=2)
          if args.json else render(results))

    if any(r.get("problems") for r in results):
        return EXIT_PROBLEMS
    if any(r["status"] == COULD_NOT_RUN for r in results):
        return EXIT_COULD_NOT_RUN
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
