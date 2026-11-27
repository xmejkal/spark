"""
run-scenario as an Operation on the core (P1078, #1582): one run of one scenario of a built project in Wokwi, or with
--dry-run its free checks alone. `scenario_run.ScenarioRun` holds the run; this answers with its verdict as the status and
a code, the log as `data.log`, and what it could not compare with the diagram as assumptions. `run_scenario.py` is its CLI.
`paid_run_step` is the step that names the paid run, for an ok dry run and for the flow (`phase_steps.scenario_steps`).
"""

from pathlib import Path

from spark.core.events import Event
from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, RUNS, WRITES, Argument, Operation
from spark.core.outcomes import COULD_NOT_RUN, OK, PROBLEMS
from spark.core.renderers import TextReport
from spark.core.result import Finding, Headline, NextStep, OperationResult
from spark.firmware.scenario_run import DEFAULT_TIMEOUT_MS, ScenarioRun
from spark.firmware.scenario_steps import PASSED
from spark.records import store

# --- MVP ---
#: The status line of each answer: a run that passed says its sentence, the caveat too; the others say what happened, and
#: their finding says why.
DRY_RUN_HEADLINE, REFUSED_HEADLINE = "%s: the free checks passed", "%s: not run, so no Wokwi minute was spent"
PASSED_HEADLINE, FAILED_HEADLINE, UNFINISHED_HEADLINE = "%s: %s", "%s: failed", "%s: the run did not finish"
#: The fix of a refused run and of a run that did not pass: the sentence names the cause, the log the run's own words.
REFUSED_FIX = "fix what the sentence names, then run the scenario again: a refused run spends no Wokwi minute"
RAN_FIX = "read the run's log in sim/runs/, fix what it names, then run the scenario again"
#: The text line that names the log, and the code of the event that says each not-checked line before the paid run.
LOG_LINE, FREE_CHECKS = "log: %s", "free_checks"
#: The why of an ok dry run's next step: the paid run itself.
PAID_RUN_WHY = "the free checks passed: the paid run spends Wokwi CI minutes, so the person runs it in their own terminal"

#: What `--help` says after the arguments (P481): the contract of a run, moved from run_scenario.py's docstring.
DETAILS = """The ready contract: the firmware prints `ready` once its setup is done, and nothing else containing that word before.
This adds a wait for the first serial text containing `ready` before the scenario's first step, because a step sent
earlier reaches a board that is still booting. So a scenario holds only behaviour: the conversation writes it from the
person's words, and spark ships none.

A run spends Wokwi CI minutes, so every check that costs nothing comes first: the simulation project, firmware/main.py,
the scenario's steps, the component ids its steps name against sim/diagram.json, littlefs, MicroPython and the image's
place. Only then the tool, the token and the paid run. A step whose id cannot be read, or a diagram that cannot be read,
says `not checked` and the run goes on (P399): each such line is an assumption of the answer, and a pass stays ok.

Each run puts MicroPython and the project's firmware/ into a new flash image, so a run never tests an older firmware. When
the build named no image (no --firmware), a real run names flash-with-firmware.bin in sim/wokwi.toml, as --firmware would
have: wokwi-cli refuses a wokwi.toml that names none.

--dry-run makes the free checks alone: it needs no token, starts no run and writes nothing (P399). An ok dry run names
the paid run as its next step, with the run's own --micropython and --timeout-ms.

A step's own `name:` key may hold a must line of the brief (copied exactly): the log's header names every step (P345),
and the look lists the must lines that no passed scenario named.

The log goes to sim/runs/<name>.log, and `data.log` names it: the date with its zone, the verdict, the step counts by kind
and the step names (P345), the sha256 of the image it tested and of each file in that image, what the simulation cannot
show, the scenario as run, and what wokwi-cli printed, which is the board's serial output among the scenario's progress.
deploy.py reads the verdict and the sha256s from the log's header (run_record, file_hashes).

A pass whose scenario has no set-control step says the look's rule in its own words, "passed, but it has no set-control
step (...)", and one whose steps cannot be counted says "passed, but its steps were not counted: <why>" (P485), once in
the text and as a note under --json. The log's verdict stays `passed`. A refused run is could-not-run with its code
(`no_token`, `no_sim_project`, ...), and `data.ran` is false; a run that failed is problems with its code (`never_ready`,
`step_failed`, ...)."""


def paid_run_step(project, scenario, why, extra=()):
    """The step that runs `scenario` in Wokwi: op run-scenario, the project made absolute (`offer_steps.whole`'s rule), then
    `extra`, the run's own flags. It spends Wokwi CI minutes, so the person runs it in their own terminal: it needs the
    person, and carries the store (`store.read_given_env`)."""
    return NextStep(RunScenario.name, [str(scenario), "--project", str(Path(project).absolute())] + list(extra), why,
                    (READS, RUNS, WRITES), False, True, store.read_given_env())


class RunReport(TextReport):
    """Renderer: TextReport whose Note leaves out a note the status line already says: a pass's caveat is its headline's
    sentence and a note for --json, so the text says it once (P1078)."""

    @classmethod
    def layout(cls, result, style, tool):
        said = result.headline.sentence
        kept = [note for note in result.notes or () if not (isinstance(note, str) and note in said)]
        return super().layout(result._replace(notes=kept or None), style, tool)


class RunScenario(Operation):
    """
    Operation: one run of one scenario in a project's sim/, through `ScenarioRun`. Its data is `project`, `scenario`, `log`
    (the log the run wrote, or None) and `ran` (False when the free checks refused it, and for a dry run). A refusal is a
    could-not-run Finding with its code, a run that failed a problem with its code; the not-checked lines are assumptions,
    so a pass stays ok. A run reads the project, runs wokwi-cli through `outside.run` and writes the image and the log; a
    dry run only reads, so its world refuses any program.
    """

    name = "run-scenario"
    summary = "Run one scenario in Wokwi. A run spends Wokwi CI minutes."
    details = DETAILS
    arguments = (Argument(("scenario",), "scenario", Path, "the scenario file, relative to the project: sim/scenarios/<name>.scenario.yaml",
                          required=True),
                 COMMON_ARGUMENTS["project"]._replace(help="the project folder with sim/ and firmware/ (default: here)"),
                 Argument(("--timeout-ms",), "timeout_ms", int, "simulated time the run may take", DEFAULT_TIMEOUT_MS),
                 Argument(("--micropython",), "micropython", Path, "the interpreter .bin; omitted, the one /spark:setup downloads"),
                 Argument(("--dry-run",), "dry_run", bool, "make the free checks only: no token, no run, nothing written"),
                 COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, RUNS, WRITES)
    data_keys = ("project", "scenario", "log", "ran")
    text_renderer = RunReport

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def written_project(self, values):
        """The project a paid run writes its image and log to: the core then writes page.html again (P1035)."""
        return None if values["dry_run"] else Path(values["project"])

    def run(self, scenario, project, dry_run, *, outside, **given):
        """`given` holds `micropython` and `timeout_ms`, the run's own values."""
        run = ScenarioRun(project, scenario, given["micropython"], given["timeout_ms"], outside=outside)
        data = {"project": str(project), "scenario": str(scenario), "log": None, "ran": False}
        if dry_run:
            return self.dry_answer(run, data, project, extra=self.extra_of(given))
        status, sentence, log, ran = run.start(lambda lines: [outside.report(Event.line(FREE_CHECKS, line)) for line in lines])
        if not ran:
            return self.refused(run, data, sentence)
        return self.ran_answer(run, dict(data, log=str(log) if log else None, ran=True), status, sentence)

    @staticmethod
    def extra_of(given):
        """The run's own flags for its next step: --micropython made absolute, and --timeout-ms when it is not the default."""
        extra = ["--micropython", str(Path(given["micropython"]).absolute())] if given["micropython"] else []
        return extra + (["--timeout-ms", str(given["timeout_ms"])] if given["timeout_ms"] != DEFAULT_TIMEOUT_MS else [])

    @staticmethod
    def refused(run, data, refusal):
        """The answer of a run the free checks refused: one could-not-run Finding with the refusal's code."""
        return OperationResult(data, [Finding.of(COULD_NOT_RUN, None, refusal.code, str(refusal), REFUSED_FIX)],
                               headline=Headline(REFUSED_HEADLINE % run.scenario.name, Headline.of_status(COULD_NOT_RUN), blocker=refusal.code))

    def dry_answer(self, run, data, project, extra):
        """The answer of the free checks alone: a refusal, or their lines and the paid run as the next step."""
        status, said = run.dry_run()
        if status != OK:
            return self.refused(run, data, said[0])
        step = paid_run_step(project, data["scenario"], PAID_RUN_WHY, extra)
        return OperationResult(data, next=[step], lines=[str(line) for line in said], assumptions=run.not_checked() or None,
                               headline=Headline(DRY_RUN_HEADLINE % run.scenario.name, Headline.of_status(OK)))

    @staticmethod
    def ran_answer(run, data, status, sentence):
        """The answer of a run that reached wokwi-cli: ok with its sentence (and its caveat as a note), or the Finding of
        its code. The not-checked lines were said before the run as events; here they are the assumptions."""
        name, lines = run.scenario.name, [LOG_LINE % data["log"]] if data["log"] else []
        assumptions = run.not_checked() or None
        if status == OK:
            notes = [str(sentence)] if sentence != PASSED else None
            return OperationResult(data, lines=lines, notes=notes, assumptions=assumptions,
                                   headline=Headline(PASSED_HEADLINE % (name, sentence), Headline.of_status(OK)))
        found = Finding.of(status, name if status == PROBLEMS else None, sentence.code, str(sentence), RAN_FIX)
        said = FAILED_HEADLINE if status == PROBLEMS else UNFINISHED_HEADLINE
        return OperationResult(data, [found], lines=lines, assumptions=assumptions,
                               headline=Headline(said % name, Headline.of_status(status), blocker=sentence.code))
# --- end MVP ---
