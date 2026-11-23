"""
The step of the phase the guide names now when that phase holds no offer (P1034, piece 2 of P793): the simulate's
scenario run (or the build, while sim/wokwi.toml is missing), the deploy's look, and the brief step of an idea out of date
after a need was dropped (P1027, slice 2). The firmware names none: Claude
writes firmware/main.py in the chat. Each step is next-only: the page shows no button for it, and `flow.py run-request`
never runs a scenario run or a look (the build is the build phase's own offer step). The step of run_scenario.py, a
script off the core, has the script's name as its op until the script moves onto the core (piece 5). The image fact is
read once more here (`guide.image_fact`): `guide_of` keeps its own inside, and exposing it costs more than its value. A
NextStep holds plain values only, so an event can carry it later.
"""

from spark.bench.board_envelope import look_step
from spark.bench.image_evidence import evidence_for
from spark.core.operation import READS, RUNS, WRITES
from spark.core.result import NextStep
from spark.flow import flow_codes
from spark.flow.guide import image_fact, scenario_names
from spark.flow.offer_steps import build_step, whole
from spark.records import store

# --- MVP ---
#: The scenario a step names while there is none (`guide.scenario_names` finds the scenarios).
SCENARIO_PLACEHOLDER = "sim/scenarios/<name>.scenario.yaml"
#: The answers file the brief step names: Claude writes the must lines the person agreed to there, outside any repository.
ANSWERS_PLACEHOLDER = "<answers.json>"


def brief_step(project):
    """The brief step, `init_project.py --answers`: it writes the must lines the person agreed to into the brief, as one
    commit when git holds it. The person's yes comes first, and then Claude runs it, so it needs no person."""
    return NextStep("init_project", ["--project", str(whole(project)), "--answers", ANSWERS_PLACEHOLDER], flow_codes.BRIEF_WHY,
                    (READS, RUNS, WRITES), True, None, store.read_given_env())


def scenario_steps(project):
    """One scenario run per scenario of the project, by name, or one with SCENARIO_PLACEHOLDER while there is none. The
    person runs it in their own terminal, and it spends Wokwi CI minutes, so it needs the person."""
    folder = whole(project)
    found = scenario_names(folder)
    why = flow_codes.SCENARIO_WHY if found else flow_codes.SCENARIO_FIRST_WHY
    return [NextStep("run_scenario", [name, "--project", str(folder)], why, (READS, RUNS, WRITES), False, True,
                     store.read_given_env()) for name in found or [SCENARIO_PLACEHOLDER]]


def look_first_step(project, no_simulation):
    """The deploy's first step, the look (`board_envelope.look_step`), with --no-simulation when no simulation tested
    the image. The person wires the board and plugs it into USB first, so it needs the person."""
    return NextStep(**look_step(whole(project), None, evidence_for(whole(project), no_simulation, False), flow_codes.LOOK_WHY,
                                needs_person=True))


def simulate_steps(project, phase):
    """The simulate's steps: the build while sim/wokwi.toml is no file, the scenario runs while no run tested the image
    or the firmware changed after it, else none (a failed run, problems, a phase that could not run)."""
    fact = image_fact(project).fact if phase.status in (flow_codes.NOT_STARTED, None) else None
    if fact == flow_codes.NO_SIM_FILES:
        return [build_step(project)]
    if phase.status == flow_codes.NOT_STARTED or (phase.status is None and fact != flow_codes.RUN_FAILED):
        return scenario_steps(project)
    return []


def steps_of(project, phases, guide):
    """The `next` of the guide's now phase when it holds no offer (P1034), by its phase: the brief step of an idea out of
    date (P1027). None for every other phase: the idea, the needs and the parts are said in the chat, the firmware is
    written there, and a breadboard now waits for piece 6."""
    now = next((phase for phase in phases if guide["now"] and phase.phase == guide["now"]["phase"]), None)
    if now and now.phase == flow_codes.IDEA and now.status == flow_codes.STALE:
        return [brief_step(project)]
    if now and now.phase == flow_codes.SIMULATE:
        return simulate_steps(project, now)
    if now and now.phase == flow_codes.DEPLOY:
        return [look_first_step(project, bool(guide["no_simulation"]))]
    return []
# --- end MVP ---
