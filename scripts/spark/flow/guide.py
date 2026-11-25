"""
The guide of a project (P977, #1407): from the Phases `show_flow.reading_of` reads, the phase the person acts on now, who
acts and one sentence for it, where each phase stands (its station, P1119), the phases done and later built from the
stations, the needs set aside, and why there is no simulation. It reads
and never writes. `flow.py show` and `flow.py page` answer it as `data.guide`.
"""

from collections import namedtuple
from pathlib import Path

from spark.breadboard import sheet
from spark.build import build_codes
from spark.build.build_record import BuildRecordStore
from spark.build.stages import SIMULATION
from spark.design import needs
from spark.firmware import firmware_codes
from spark.firmware.project_image import DeployError, ProjectImage
from spark.flow import deploy_reading, flow_codes, wired_board
from spark.flow.phase_readers import REQUIREMENTS_FILE, counted, set_aside
from spark.core.errors import CodedMessageError
from spark.core.outcomes import COULD_NOT_RUN, OK, PROBLEMS, SKIPPED

# --- MVP ---
#: The codes of a simulation stage whose build counts as done (the PO, 2026-11-21): Wokwi has no model of the board.
NO_MODEL_CODES = (build_codes.BOARD_NOT_IN_WOKWI,)
#: What reading the wiring sheet can raise: its own refusals, and a circuit.json that is no JSON, holds a value of the
#: wrong type or shape, or is nested too deep (tests/test_flow_page.py's TheMissingWiringTest).
SHEET_UNREADABLE = sheet.REFUSALS + (ValueError, KeyError, TypeError, AttributeError, IndexError, RecursionError)
#: Value: what the runs say of the image (a fact of flow_codes, or None) and the name of a log that failed on it, or None.
ImageFact = namedtuple("ImageFact", "fact log")
NO_IMAGE_FACT = ImageFact(None, None)
#: What the image's runs say that leaves the simulate open: a run failed on it, firmware changed after it, or none ran.
OPEN_IMAGE_FACTS = (flow_codes.RUN_FAILED, flow_codes.IMAGE_OLDER, flow_codes.IMAGE_UNTESTED)


def readable(read, default):
    """What `read()` gives, or `default` when a file it reads cannot be read: the phase that reads it says why."""
    try:
        return read()
    except (CodedMessageError, OSError):
        return default


def stops_only_for_no_model(record):
    """True when the build `record`'s one stage that ended neither ok nor skipped is the simulation, with a code of
    NO_MODEL_CODES. An old record with no code is never counted as done."""
    stopped = [stage for stage in (record or {}).get("stages") or [] if stage.get("status") not in (OK, SKIPPED)]
    return [stage.get("name") for stage in stopped] == [SIMULATION.name] and stopped[0].get("code") in NO_MODEL_CODES


def no_model_phases(project, by_name):
    """The phases counted as done because Wokwi has no model of the board: a build that could not run for that alone,
    and after it a simulate with no status or not started. The build phase keeps could-not-run, so the exit stays 2.
    It reads .spark/build.json once more: a stage code on every Phase would change the phases' JSON contract."""
    build, simulate = by_name.get(flow_codes.BUILD), by_name.get(flow_codes.SIMULATE)
    if not build or build.status != COULD_NOT_RUN or not stops_only_for_no_model(readable(BuildRecordStore(project).read, None)):
        return set()
    return {flow_codes.BUILD} | ({flow_codes.SIMULATE} if simulate and simulate.status in (flow_codes.NOT_STARTED, None) else set())


def image_fact(project):
    """The ImageFact of the image sim/wokwi.toml names: RUN_FAILED with the first failed log's name, IMAGE_OLDER,
    IMAGE_UNTESTED or IMAGE_TESTED. NO_SIM_FILES while sim/wokwi.toml is no file (P1034). NO_IMAGE_FACT when there is no
    image or a log cannot be read: the phase says why."""
    try:
        image = ProjectImage(Path(project))
        failed = image.failed_runs()
        if failed:
            return ImageFact(flow_codes.RUN_FAILED, failed[0][0].name)
        if image.find_newer_files():
            return ImageFact(flow_codes.IMAGE_OLDER, None)
        return ImageFact(flow_codes.IMAGE_TESTED if image.find_passed_logs() else flow_codes.IMAGE_UNTESTED, None)
    except DeployError as missing:
        return ImageFact(flow_codes.NO_SIM_FILES, None) if missing.reason == firmware_codes.NO_SIM_TOML else NO_IMAGE_FACT
    except OSError:
        return NO_IMAGE_FACT


def is_open(phase, fact):
    """True when the person acts on `phase` before the next: a status that is neither ok nor None, or a simulate with no
    status whose image `fact` leaves it open."""
    return phase.status not in (OK, None) or (phase.phase == flow_codes.SIMULATE and fact.fact in OPEN_IMAGE_FACTS)


def now_phase(phases, no_model, fact, all_aside=False):
    """The phase to act on now: the first open one not counted as done, or the idea while no need is written, or the parts
    while every need is set aside (P980: there is no pick to write the parts list from). None when no phase is open: a
    deploy that saw ready on the image now (P1043), or a flow of other readers, which a test gives."""
    now = next((phase for phase in phases if phase.phase not in no_model and is_open(phase, fact)), None)
    if now and now.phase == flow_codes.REQUIREMENTS and now.status != COULD_NOT_RUN and all_aside:  # a broken file is not hidden
        return next((phase for phase in phases if phase.phase == flow_codes.PARTS), now)
    if now and now.phase == flow_codes.NEEDS and now.status == flow_codes.NOT_STARTED:
        return phases[0]
    return now


def count_steps(project):
    """The number of steps of the project's wiring sheet, or None when the build's files cannot give them."""
    try:
        return len(sheet.wiring_data(Path(project) / REQUIREMENTS_FILE).steps)
    except SHEET_UNREADABLE:
        return None


def is_sheet_current(project, by_name):
    """True when the wiring sheet is there and current: the breadboard phase has no status and breadboard.md is kept."""
    breadboard = by_name.get(flow_codes.BREADBOARD)
    return breadboard is not None and breadboard.status is None and (Path(project) / sheet.SHEET).is_file()


#: Where the conversation writes a project's scenarios (P1034).
SCENARIOS, SCENARIO_GLOB = Path("sim") / "scenarios", "*.scenario.yaml"


def scenario_names(project):
    """The scenarios of `project`, each as its path in the project, sorted."""
    folder = Path(project)
    return sorted(path.relative_to(folder).as_posix() for path in (folder / SCENARIOS).glob(SCENARIO_GLOB))


def who_and_sentence(now, open_needs, fact, written=True):
    """(who acts, the sentence) of the phase to act on now: a simulate with no sim/wokwi.toml by Claude (P1034), a
    simulate that opens a scenario run while no scenario is `written` (P1034), a simulate with no status by its ImageFact
    `fact` (flow_codes.IMAGE_NOW), else the phase's own `by` and its sentence by (phase, status) in
    flow_codes.NOW_SENTENCES, else the problems or could-not-run line."""
    if now.phase == flow_codes.SIMULATE and fact.fact == flow_codes.NO_SIM_FILES:
        return [flow_codes.BY_CLAUDE], flow_codes.SIM_FILES_NOW
    if now.phase == flow_codes.SIMULATE and not written and (now.status == flow_codes.NOT_STARTED or fact.fact == flow_codes.IMAGE_UNTESTED):
        return [flow_codes.BY_TERMINAL], flow_codes.SCENARIO_FIRST_NOW
    if now.phase == flow_codes.SIMULATE and now.status is None:
        by, said = flow_codes.IMAGE_NOW[fact.fact]
        return by, said % fact.log if fact.fact == flow_codes.RUN_FAILED else said
    said = flow_codes.NOW_SENTENCES.get((now.phase, now.status))
    if said == flow_codes.PARTS_NOW:
        return [now.by], said % (flow_codes.ONE_NEED_HAS if len(open_needs) == 1 else flow_codes.MANY_NEEDS_HAVE % len(open_needs), ", ".join(open_needs))
    return [now.by], said or (flow_codes.PROBLEMS_NOW if now.status == PROBLEMS else flow_codes.COULD_NOT_RUN_NOW) % now.phase


def chat_offer_of(now, fact):
    """The key of the chat offer whose job the NOW sentence of `now` asks Claude for (P1122, `flow_codes.CHAT_NOW`), or
    None, in `who_and_sentence`'s order: none for a simulate with no sim/wokwi.toml (the build's own step), a simulate with
    no status by its ImageFact `fact`, else by the phase's status. An open deploy after a deploy is `deploy_chat_offer`'s."""
    if now.phase == flow_codes.SIMULATE and fact.fact == flow_codes.NO_SIM_FILES:
        return None
    value = fact.fact if now.phase == flow_codes.SIMULATE and now.status is None else now.status
    return flow_codes.CHAT_NOW.get((now.phase, value))


def deploy_chat_offer(state):
    """The key of the chat offer of an open deploy after a deploy (P1122), or None, by the value `deploy_reading.deploy_now`
    picks its sentence by in the DeployState `state`: a stale deploy's fact, the verdict of a flash that did not finish,
    else the status."""
    if state.status == flow_codes.STALE:
        value = state.fact
    elif deploy_reading.not_finished(state.logged):
        value = state.logged.verdict
    else:
        value = state.status
    return flow_codes.CHAT_NOW.get((flow_codes.DEPLOY, value))


def with_deploy_now(project, said, now, deploy=None):
    """`said` with who acts, the sentence and the chat offer of an open deploy after a deploy (P1043, P1122,
    `deploy_reading.deploy_now`), from `deploy`, the DeployState the run read its deploy phase from (None: read it here, as
    `image_fact` reads the image: a fact on every Phase would change the phases' JSON). Else `said` as it is."""
    if not (now and now.phase == flow_codes.DEPLOY):
        return said
    state = deploy or deploy_reading.read_deploy(project)
    told = deploy_reading.deploy_now(state)
    return dict(said, by=told[0], says=told[1], chat_offer=deploy_chat_offer(state)) if told else said


def no_open_phase(said, by_name):
    """The guide's sentence when nothing is open: NO_OPEN_PHASE_NOW when there is no now and the deploy is ok (P1043), else
    None, so a flow of other readers gets none."""
    deploy = by_name.get(flow_codes.DEPLOY)
    return flow_codes.NO_OPEN_PHASE_NOW if said is None and deploy is not None and deploy.status == OK else None


def job_offer(now):
    """The key of the offer that does the job of the phase to act on now: its one offer of a kind the page sends, or None
    when it holds none or more than one (P1030: one rule, so the CLI's `next` and the page's NOW button name one offer). A
    breadboard now names none: the build's offer is in the build phase, until a NOW sentence names its button (piece 6)."""
    own = [offer.key for offer in now.offers if offer.key.split(":", 1)[0] in flow_codes.SENDABLE]
    return own[0] if len(own) == 1 else None


def now_of(now, open_needs, fact, count, written=True):
    """`{phase, by, says, offer, chat_offer, needs, steps}` of the phase to act on now. With `count`, the steps of a current
    wiring sheet beside firmware not started, it is two jobs, the person's and Claude's, and `steps` is that count (else
    None). `written` is false while a simulate now has no scenario. `chat_offer` is the key of the chat offer the sentence
    asks Claude for, or None (P1122, `chat_offer_of`)."""
    by, says = ([flow_codes.BY_YOU, flow_codes.BY_CLAUDE], flow_codes.TWO_JOBS_NOW % count) if count is not None else \
        who_and_sentence(now, open_needs, fact, written)
    return {"phase": now.phase, "by": by, "says": says, "offer": job_offer(now), "chat_offer": chat_offer_of(now, fact),
            "needs": open_needs if now.phase == flow_codes.PARTS else [], "steps": count}


def has_no_picks(by_name):
    """True when the needs phase has no status: no needs are written, so the requirements have no picks behind them (a
    requirements.json written by hand, or a last need dropped). An unreadable needs.json gives could-not-run, so false."""
    needs_phase = by_name.get(flow_codes.NEEDS)
    return needs_phase is not None and needs_phase.status is None


def place_of(index, name, at, no_model, wiring):
    """Where the phase `name`, at `index` of the phases, stands beside the now phase at `at` (P1119): done before it, now,
    later after it. A simulate with no model is later wherever it stands, and the breadboard is now while `wiring` is."""
    if name == flow_codes.SIMULATE and name in no_model:
        return flow_codes.LATER_PLACE
    if name == flow_codes.BREADBOARD and wiring == flow_codes.NOW_PLACE:
        return flow_codes.NOW_PLACE
    return flow_codes.DONE_PLACE if index < at else flow_codes.NOW_PLACE if index == at else flow_codes.LATER_PLACE


def note_of(phase, place, no_model, wiring, no_picks):
    """The one note of `phase` at `place` (P1119, `flow_codes.NO_PICKS_NOTE` and its kin), or None. Before now, with
    `no_picks` the needs and the parts are not done and the requirements have no picks behind them (P980), and the breadboard
    is unseen while `wiring` is done (a current sheet) or has no sheet. A phase counted as done for no model says so, and
    a later phase whose status is ok may change."""
    name, done = phase.phase, place == flow_codes.DONE_PLACE
    if done and no_picks and name in (flow_codes.NEEDS, flow_codes.PARTS):
        return flow_codes.NOT_DONE_NOTE
    if done and no_picks and name == flow_codes.REQUIREMENTS:
        return flow_codes.NO_PICKS_NOTE
    if name in no_model:
        return flow_codes.NO_MODEL_NOTE
    if done and name == flow_codes.BREADBOARD:
        return flow_codes.UNSEEN_NOTE if wiring == flow_codes.DONE_PLACE else flow_codes.NO_SHEET_NOTE
    return flow_codes.MAY_CHANGE_NOTE if place == flow_codes.LATER_PLACE and phase.status == OK else None


def stations_of(phases, at, no_model, wiring, no_picks=False):
    """
    The station of each of the `phases` the guide is given, in their order (P1119): `{"phase", "place", "note"}`, with
    `place_of` and `note_of`. `at` is the index of the now phase, `len(phases)` with none. `no_model` holds the phases
    counted as done for no Wokwi model. `wiring` is where the wiring stands: NOW_PLACE beside the firmware (the two jobs),
    DONE_PLACE with a current sheet, else None. `no_picks`: no needs are written (`has_no_picks`). Pure: it reads no file.
    """
    stations = []
    for index, phase in enumerate(phases):
        place = place_of(index, phase.phase, at, no_model, wiring)
        stations.append({"phase": phase.phase, "place": place, "note": note_of(phase, place, no_model, wiring, no_picks)})
    return stations


def named(station):
    """The name DONE and LATER show for a station: its phase, with its note's words in parentheses (NOTED_PHASE)."""
    note = station["note"]
    if note is None:
        return station["phase"]
    words = flow_codes.STATION_NOTES_BY_PHASE.get((note, station["phase"])) or flow_codes.STATION_NOTES[note]
    return flow_codes.NOTED_PHASE % (station["phase"], words)


def names_at(stations, place):
    """The names (`named`) of the `stations` at `place`, in order: `done` with DONE_PLACE and `later` with LATER_PLACE. A
    station with a note of LEFT_OUT_NOTES is in no list."""
    return [named(station) for station in stations if station["place"] == place and station["note"] not in flow_codes.LEFT_OUT_NOTES]


def with_wiring(project, now, by_name, count):
    """True when the job now holds the wiring (P1062, the review of #1619): the two jobs beside a current sheet (`count`),
    or the deploy beside a current sheet. The page opens its wiring fold by it. Spark never says the board is wired."""
    return count is not None or (now.phase == flow_codes.DEPLOY and is_sheet_current(project, by_name))


def stands_at_of(guide):
    """Where a project stands: the guide's now phase, the one rule (P1030). None when the guide has no now, which only a
    flow of other readers in a test gives."""
    return guide["now"]["phase"] if guide["now"] else None


def guide_of(project, phases, steps=count_steps, deploy=None, board=None):
    """
    What the person does now, what is done, what comes later and what they set aside, from the Phases of `project`:
    `{"now": {phase, by, says, offer, chat_offer, needs, steps, with_wiring}, "stations", "done", "later", "set_aside", "no_simulation", "no_open_phase", "wired"}`.
    `stations` places each phase beside the now (`stations_of`, P1119), and `done` and `later` are built from it. `steps` counts the wiring
    sheet's steps. The needs are read once more, by the parts phase's own rule (`counted`, `set_aside`). `deploy` is the
    run's DeployState (P1043), None to read it here. `board` is the run's WiredBoard (P1044), None to read it here:
    `wired` is `{sheet_at, deploy_at}`, the witnesses of a board that can be wired, or None when spark saw none.
    """
    by_name, listed = {phase.phase: phase for phase in phases}, readable(lambda: needs.read(project), [])
    no_model = no_model_phases(project, by_name)
    simulate = by_name.get(flow_codes.SIMULATE)
    fact = image_fact(project) if simulate and simulate.status in (None, flow_codes.NOT_STARTED) and flow_codes.SIMULATE not in no_model \
        else NO_IMAGE_FACT
    all_aside = bool(listed) and not counted(listed)
    now = now_phase(phases, no_model, fact, all_aside)
    at = phases.index(now) if now else len(phases)
    open_needs = [need["id"] for need in counted(listed) if not need.get("pick")]
    beside_sheet = now and now.phase == flow_codes.FIRMWARE and now.status == flow_codes.NOT_STARTED and is_sheet_current(project, by_name)
    count = steps(project) if beside_sheet else None
    two_jobs = count is not None  # no count: no two jobs, so the breadboard stays in done
    written = not (now and now.phase == flow_codes.SIMULATE) or bool(scenario_names(project))
    said = with_deploy_now(project, now_of(now, open_needs, fact, count, written), now, deploy) if now else None
    said = dict(said, with_wiring=with_wiring(project, now, by_name, count)) if said else None
    # beside the firmware, the wiring is part of now
    wiring = flow_codes.NOW_PLACE if two_jobs else flow_codes.DONE_PLACE if is_sheet_current(project, by_name) else None
    stations = stations_of(phases, at, no_model, wiring, has_no_picks(by_name))
    if board is None:
        board = wired_board.read_wired(project, deploy if deploy is not None else deploy_reading.read_deploy(project))
    return {"now": said, "stations": stations, "done": names_at(stations, flow_codes.DONE_PLACE),
            "later": names_at(stations, flow_codes.LATER_PLACE), "set_aside": [need["id"] for need in set_aside(listed)],
            "no_simulation": flow_codes.NO_SIMULATION_NOW if flow_codes.BUILD in no_model else None,
            "no_open_phase": no_open_phase(said, by_name), "wired": wired_board.wired_data(board)}
# --- end MVP ---
