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

So `skipped` is silent about the board and does not by itself fail the run, because you chose not
to run it. `could-not-run` exits non-zero, because you asked and got no answer.

**With one exception, and it overturns the simpler rule above.** If EVERY check was skipped, the
run exits non-zero as well. "I asked for nothing and was told everything is fine" is the cleanest
form of the failure this file exists to prevent, and it is exactly what an agent gets when it
builds its command wrong — which is not hypothetical: the command in `spark-review`'s own skill
leaves two of these seven permanently unasked.

(That skill's command is still wrong and this does not fix it: five checks running clean will and
should exit 0. Only the all-skipped case is caught here.)
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
# Siblings are IMPORTED, inside the check that needs them so nothing loads until it runs. They
# were loaded by file path with `importlib`, which registers nothing in `sys.modules`: in one
# process this file's `parts` was not `emit_board`'s `parts`, and their `PartError` classes
# were different objects, so an `except` for one could not catch the other. Audit A7.
sys.path.insert(0, str(SCRIPTS))

import design  # noqa: E402

EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN = 0, 1, 2

OK, PROBLEMS, COULD_NOT_RUN, SKIPPED = "ok", "problems", "could-not-run", "skipped"


class Check:
    """
    One deterministic check, and what it needs to run.

    `needs` names the inputs; a check whose inputs were not supplied is SKIPPED rather than
    passed, and says so, because "I was not asked" and "I found nothing" are different.
    """

    def __init__(self, name, needs, what):
        self.name, self.needs, self.what = name, needs, what

    def run(self, inputs, ambiguous=None):
        ambiguous = ambiguous or {}
        unchosen = [need for need in self.needs if need in ambiguous]
        if unchosen:
            # NOT skipped. The input exists — twice — and nothing decided between them, so this
            # check did not look. Saying "not asked" would be a check that could not look reading
            # as one that was never wanted.
            return {"check": self.name, "status": COULD_NOT_RUN, "what": self.what,
                    "reason": "; ".join("%s is ambiguous: %s — name one with --%s"
                                        % (need, ", ".join(ambiguous[need]), need)
                                        for need in unchosen)}
        missing = [need for need in self.needs if not inputs.get(need)]
        if missing:
            return {"check": self.name, "status": SKIPPED, "what": self.what,
                    "reason": "not given %s" % ", ".join(missing)}
        try:
            return dict({"check": self.name, "what": self.what}, **self.call(inputs))
        except (Exception, SystemExit) as broken:  # noqa: BLE001
            # SystemExit is a BaseException, so `except Exception` let it straight past: one
            # check's missing file killed the other six and exited 1, which reads as "problems
            # found" — the opposite of what happened.
            return {"check": self.name, "status": COULD_NOT_RUN, "what": self.what,
                    "problems": [], "unchecked": ["%s: %s" % (type(broken).__name__, broken)]}


def answer(problems=(), unchecked=(), unmeasured=()):
    """
    The one place a check's status is decided.

    Every check used to decide its own, and two got it wrong in the same direction: a board that
    could not be read, and a finding whose own severity was `could-not-run`, both landed in a
    notes field while the status stayed `ok`. Deciding it here makes `ok` unreachable while
    anything went unchecked — not by convention, but because there is no other way to build the
    answer.

    `unchecked` is a property of the RUN: something was asked and did not happen. `unmeasured` is
    a property of the BOARD: a real finding that needs a number nobody has taken. They were one
    field, which meant a caller could not tell "I could not look" from "look at this yourself".
    """
    problems, unchecked = list(problems), list(unchecked)
    status = PROBLEMS if problems else (COULD_NOT_RUN if unchecked else OK)
    result = {"status": status, "problems": problems, "unchecked": unchecked}
    if unmeasured:
        result["unmeasured"] = list(unmeasured)
    return result


def findings_result(findings, describe=lambda f: f):
    return answer(problems=[describe(f) for f in findings])


def circuit_of(inputs):
    """
    The built netlist, refusing one that is empty.

    A `tsci build` that failed part way leaves a file holding `[]`. Every check downstream then
    examines nothing, finds nothing, and reports `ok` — a clean bill of health for a board that
    was never built. The file existing is not the same as the board existing.
    """
    elements = json.loads(Path(inputs["circuit"]).read_text())
    if not elements:
        raise ValueError("%s holds no circuit elements — the build produced nothing, so there is "
                         "nothing to check" % Path(inputs["circuit"]).name)
    return elements


class PinCapability(Check):
    def call(self, inputs):
        # This called `check_design.check()` — a function that has never existed — and passed it
        # path strings where it wanted parsed dicts. The plugin's flagship check therefore never
        # ran once through the runner, and the AttributeError surfaced as `could-not-run`, which
        # reads as "your environment is wrong" rather than "this plugin is broken".
        import check_design
        design_path = Path(inputs["design"])
        design = json.loads(design_path.read_text())
        reference = inputs.get("board") or design.get("board")
        if not reference:
            raise ValueError("the design does not say which board it is built around")
        board = json.loads(check_design.resolve_board(reference, design_path).read_text())
        return findings_result(check_design.run(design, board), str)


class RulesVsNetlist(Check):
    def call(self, inputs):
        import compare_design
        circuit_of(inputs)  # refuse an empty netlist before comparing anything against it
        result = compare_design.compare(inputs["circuit"], inputs["rules"])
        if result["status"] == "could-not-run":
            return answer(unchecked=[result.get("reason") or "no reason given"])
        return answer(problems=[p["detail"] for p in result.get("problems", [])])


class Physics(Check):
    def call(self, inputs):
        import check_physics
        findings = check_physics.run(circuit_of(inputs),
                                     json.loads(Path(inputs["rules"]).read_text()))

        def of(severity):
            return ["%s: %s" % (f.subject, f.detail)
                    for f in findings if f.severity == severity]

        # `could-not-run` findings were dropped on the floor here — an unknown I2C bus speed made
        # the rise-time rule unanswerable and the check still printed a tick with no note at all.
        return answer(problems=of("problem"), unchecked=of("could-not-run"),
                      unmeasured=of("needs-measurement"))


def placeholder_components_in(project):
    """
    Components in this project whose footprint is a stand-in, by emitted name.

    Derived from the project's part records and requirements files with the GENERATOR's own
    functions — `requested_parts` for instance names, `placeholder_components` for the naming —
    so the checker is keyed by exactly the string that reached the netlist. Deriving the name a
    second time here would be one more copy of a rule to drift.

    Every requirements file is read, not one: `check_all` is handed one circuit and cannot know
    which requirements produced it. A name from another board simply matches nothing in this
    netlist, so the union is safe.

    Returns (names, notes). Each file is read on its own, through `design` — the loader the
    generator itself uses — and a file that cannot be read is a NOTE, not a reason to empty the
    list: before, one unreadable file made this return `()` under `except Exception`, and the
    check then measured every placeholder as if it were real without a word. A stand-in the
    check did not learn about is something the reader has to be told.
    """
    if not project:
        return (), []
    import design
    import emit_board
    root = Path(project)
    names, notes = set(), []
    for requirements in sorted(root.glob("*requirements.json")):
        try:
            part_list = design.parts_of(design.read(requirements), root)
            names |= set(emit_board.placeholder_components(part_list))
        except design.DesignError as broken:
            notes.append("%s could not be read, so any stand-in footprint it names was "
                         "measured as if real: %s" % (requirements.name, broken))
    return tuple(sorted(names)), notes


class Buildability(Check):
    def call(self, inputs):
        import check_footprints
        placeholders, notes = placeholder_components_in(inputs.get("project"))
        findings = check_footprints.run(circuit_of(inputs), placeholders)

        def of(severity):
            return ["%s: %s" % (f.subject, f.detail)
                    for f in findings if f.severity == severity]

        # Split, for the same reason physics does: a rule that could not read an element has not
        # approved it, and folding the two together is what let 10 of 70 holes go unexamined
        # under a tick.
        return answer(problems=of("problem"), unchecked=of("could-not-run") + notes)


class VendorTruth(Check):
    def call(self, inputs):
        import check_vendor_pins
        problems, unchecked = [], []
        for path in inputs["boards"]:
            result = check_vendor_pins.check_board(Path(path), offline=True, repo="")
            if result["status"] == "could-not-run":
                unchecked.append("%s: %s" % (result["board"], result["reason"]))
            else:
                problems += ["%s: %s" % (result["board"], p)
                             for p in result.get("problems", [])]
        # These went into `unmeasured` and the status stayed `ok`. In any project whose board
        # files are not this repo's, every board lands here — so the one check that looks outside
        # the project could never run there and always said it was fine.
        return answer(problems=problems, unchecked=unchecked)


class Firmware(Check):
    def call(self, inputs):
        import check_firmware
        source = Path(inputs["firmware"]).read_text()
        constants = check_firmware.read_pin_constants(source)
        if not constants:
            return answer(unchecked=[
                "no PIN_* constants in %s — nothing to compare, which is not the same as "
                "agreeing" % Path(inputs["firmware"]).name])
        board = json.loads(Path(inputs["board_file"]).read_text())
        return findings_result(check_firmware.check_against_board(constants, board))


class TheOrder(Check):
    def call(self, inputs):
        import check_bom
        rows = check_bom.read_bom(Path(inputs["package"]))
        problems = (check_bom.check_duplicate_parts(rows)
                    + check_bom.check_missing_parts(rows))
        unchecked = []
        if inputs.get("circuit"):
            circuit = Path(inputs["circuit"])
            # A typo'd --circuit used to drop the fatal-at-fab warnings in silence, because the
            # reader returned [] for a file it never opened.
            if circuit.is_file():
                circuit_of(inputs)
                problems += check_bom.check_design_warnings(circuit)
            else:
                unchecked.append("no circuit at %s, so the design's own fab warnings were never "
                                 "read" % circuit)
        return answer(problems=problems, unchecked=unchecked)


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


#: Where each input lives in a project laid out the usual way. Globs, first list wins.
#:
#: This exists so the caller has ONE argument. The command a skill documented named five paths,
#: and got two of them wrong: it globbed `boards/*.json`, which matches the selection file rather
#: than a board definition, and it never passed `--design` or `--firmware` at all — so the
#: flagship check was permanently unasked and the review still called itself complete.
CONVENTIONS = {
    "circuit": list(design.CIRCUIT_PATHS),
    "rules": [".spark/rules.json"],
    "package": ["*-gerbers.zip", "fab/*.zip"],
    "design": ["*.design.json", ".spark/design.json"],
    "firmware": ["firmware/*/config.py", "firmware/config.py", "config.py"],
}


def discover(project):
    """
    Find each input by convention, and say what was found and what was looked for.

    Two rules keep auto-discovery from being worse than the explicit paths it replaces:

      * every resolved path is PRINTED. Silently picking up a stale artifact is the one way this
        makes things worse rather than better, and the BOM check has already been bitten by it.
      * a glob matching more than one file is AMBIGUOUS, not a coin toss. Two fab packages in a
        directory is exactly when checking the wrong one costs money.
    """
    project = Path(project)
    found, notes = {}, []

    ambiguous = {}
    for name, patterns in CONVENTIONS.items():
        matches = []
        for pattern in patterns:
            matches = sorted(project.glob(pattern))
            if matches:
                break
        if len(matches) == 1:
            found[name] = str(matches[0])
            notes.append("%-12s %s" % (name, matches[0].relative_to(project)))
        elif matches:
            # Recorded, not dropped. Leaving the input unset made every check that needed it
            # report SKIPPED — "I was not asked" — when the truth is "there were two of these and
            # I refused to choose". On a two-board project that turned six of seven checks off and
            # still exited 0 with a top-level status of "ok", which is this tool's own founding
            # rule broken at the top level.
            ambiguous[name] = [str(m.relative_to(project)) for m in matches]
            notes.append("%-12s AMBIGUOUS, %d matches: %s — name one explicitly"
                         % (name, len(matches),
                            ", ".join(str(m.relative_to(project)) for m in matches)))
        else:
            notes.append("%-12s not found (looked for %s)" % (name, ", ".join(patterns)))

    # The board library knows where board definitions are; a glob does not, and guessing is how
    # the selection file ended up being checked against a vendor header it does not have.
    try:
        import boards
        definitions = [str(boards.definition_path(project, board_id))
                       for board_id in boards.available(project)]
        if definitions:
            found["boards"] = definitions
            notes.append("%-12s %d definition(s): %s"
                         % ("boards", len(definitions),
                            ", ".join(sorted(boards.available(project)))))
        active = boards.definition_path(project)
        found["board_file"] = str(active)
        notes.append("%-12s %s" % ("board_file", Path(active).name))
    except Exception as broken:  # noqa: BLE001 - a project with no board chosen is a normal state
        notes.append("%-12s not resolved (%s)" % ("boards", broken))

    return found, notes, ambiguous


def inputs_for(args):
    """
    What each check will be given, and the record of where it came from.

    An explicit flag always beats a convention, so `--project` is a starting point rather than a
    straitjacket: discover the usual layout, then let the caller correct any one of them.
    """
    explicit = {key: value for key, value in vars(args).items() if value}
    if not args.project:
        return vars(args), [], {}
    discovered, resolved, ambiguous = discover(args.project)
    # An explicit flag settles an ambiguity: that is what naming one is for.
    ambiguous = {name: matches for name, matches in ambiguous.items() if name not in explicit}
    return dict(discovered, **explicit), resolved, ambiguous


def run(inputs, ambiguous=None):
    return [check.run(inputs, ambiguous) for check in CHECKS]


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
        for note in result.get("unchecked", []):
            lines.append("           ! %s" % note)
        for note in result.get("unmeasured", []):
            lines.append("           ? %s" % note)

    problems = sum(len(r.get("problems", [])) for r in results)
    unchecked = [r["check"] for r in results if r.get("unchecked")]
    skipped = [r["check"] for r in results if r["status"] == SKIPPED]
    completed = [r for r in results if r["status"] != SKIPPED and not r.get("unchecked")]

    lines.append("")
    if unchecked:
        lines.append("  %d check(s) could not look: %s" % (len(unchecked), ", ".join(unchecked)))
    if skipped:
        lines.append("  %d not asked for: %s" % (len(skipped), ", ".join(skipped)))

    # The last line is the one a hurried reader takes away, so it must never be able to say
    # less than happened. "Nothing found by the checks that ran" was true and useless when the
    # number of checks that ran was zero.
    if problems:
        lines.append("  %d problem(s)" % problems)
    elif not completed:
        lines.append("  nothing completed. This says nothing about the board.")
    elif unchecked or skipped:
        lines.append("  nothing found by the %d check(s) that completed, of %d"
                     % (len(completed), len(results)))
    else:
        lines.append("  nothing found by any of the %d checks" % len(results))
    return "\n".join(lines)


def verdict(results):
    """The one answer, from the same rule the individual checks answer by."""
    if any(r.get("problems") for r in results):
        return PROBLEMS
    # Both, deliberately. Reading only the field trusts every call site to have filled it in, and
    # reading only the status trusts every call site to have set it — and the whole reason this
    # function exists is that one of them did not.
    if any(r.get("unchecked") or r["status"] == COULD_NOT_RUN for r in results):
        return COULD_NOT_RUN
    if all(r["status"] == SKIPPED for r in results):
        # Asking for nothing and being told "ok" is the cleanest version of the failure this
        # whole file exists to prevent.
        return COULD_NOT_RUN
    return OK


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_all.py",
        description="Run every deterministic check and answer once.")
    parser.add_argument("--project",
                        help="a project directory; every input is discovered in it by "
                             "convention, and each resolved path is printed")
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

    inputs, resolved, ambiguous = inputs_for(args)
    results = run(inputs, ambiguous)
    overall = verdict(results)

    if args.json:
        print(json.dumps({"tool": "check_all", "status": overall,
                          "resolved": resolved, "results": results}, indent=2))
    else:
        if resolved:
            # Printed every time, not on a flag. Silently picking up a stale artifact is the one
            # way discovery is worse than the five paths it replaces.
            print("  resolved from %s:" % args.project)
            for note in resolved:
                print("    %s" % note)
            print()
        print(render(results))
    return {OK: EXIT_OK, PROBLEMS: EXIT_PROBLEMS,
            COULD_NOT_RUN: EXIT_COULD_NOT_RUN}[overall]


if __name__ == "__main__":
    sys.exit(main())
