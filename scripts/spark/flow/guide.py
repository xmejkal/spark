"""
The guide of a project (P977, #1407): from the Phases `show_flow.reading_of` reads, the phase the person acts on now, who
acts and one sentence for it, where each phase stands (its station, P1119), the phases done and later built from the
stations, the needs set aside, and why there is no simulation with the free checks' state (P1209, `checks_reading`). It reads
and never writes. `flow.py show` and `flow.py page` answer it as `data.guide`.
"""

from collections import namedtuple
from pathlib import Path

from spark.breadboard import sheet
from spark.build.build_record import BuildRecordStore
from spark.design import entry_origin, needs
from spark.firmware import firmware_codes
from spark.firmware.project_image import DeployError, ProjectImage
from spark.flow import checks_reading, deploy_reading, flow_codes, wired_board
from spark.flow.no_model import stops_only_for_no_model
from spark.flow.phase_readers import REQUIREMENTS_FILE, counted, read_requirements, set_aside
from spark.core.errors import CodedMessageError
from spark.core.outcomes import COULD_NOT_RUN, OK, PROBLEMS

# --- MVP ---
#: What reading the wiring sheet can raise: its own refusals, and a circuit.json that is no JSON, holds a value of the
#: wrong type or shape, or is nested too deep (tests/test_flow_page.py's TheMissingWiringTest).
SHEET_UNREADABLE = sheet.REFUSALS + (ValueError, KeyError, TypeError, AttributeError, IndexError, RecursionError)
#: Value: what the runs say of the image (a fact of flow_codes, or None) and the name of a log that failed on it, or None.
ImageFact = namedtuple("ImageFact", "fact log")
NO_IMAGE_FACT = ImageFact(None, None)
#: No fact, as NO_IMAGE_FACT, and the code of a run log that cannot be read: a board with no model never reads it as "no run failed" (P1220).
UNREADABLE_FACT = ImageFact(None, firmware_codes.LOG_UNREADABLE)
#: What the image's runs say that leaves the simulate open: a run failed on it, firmware changed after it, or none ran.
OPEN_IMAGE_FACTS = (flow_codes.RUN_FAILED, flow_codes.IMAGE_OLDER, flow_codes.IMAGE_UNTESTED)


def readable(read, default):
    """What `read()` gives, or `default` when a file it reads cannot be read: the phase that reads it says why."""
    try:
        return read()
    except (CodedMessageError, OSError):
        return default


def no_model_phases(project, by_name):
    """The phases counted as done because Wokwi has no model of the board: a build that stopped for that alone, and after
    it a simulate with no status or not started. A new record's build phase has no status (P1207, the simulation stage is
    skipped). An old record's build phase keeps could-not-run, so for an old record the exit stays 2. A stale build is
    never counted. It reads .spark/build.json once more: a stage code on every Phase would change the phases' JSON contract."""
    build, simulate = by_name.get(flow_codes.BUILD), by_name.get(flow_codes.SIMULATE)
    if not build or build.status not in (COULD_NOT_RUN, None) or not stops_only_for_no_model(readable(BuildRecordStore(project).read, None)):
        return set()
    return {flow_codes.BUILD} | ({flow_codes.SIMULATE} if simulate and simulate.status in (flow_codes.NOT_STARTED, None) else set())


def image_fact(project, default_without_toml=False):
    """The ImageFact of the image sim/wokwi.toml names: RUN_FAILED with the first failed log's name, IMAGE_OLDER,
    IMAGE_UNTESTED or IMAGE_TESTED. NO_SIM_FILES while sim/wokwi.toml is no file (P1034). NO_IMAGE_FACT when there is no
    image or a log cannot be read (UNREADABLE_FACT for the log): the phase says why. `default_without_toml` takes the board's default
    image with no sim/wokwi.toml, as the deploy does, for a board Wokwi has no model of (P1220)."""
    try:
        image = ProjectImage(Path(project), default_without_toml=default_without_toml)
        failed = image.failed_runs()
        if failed:
            return ImageFact(flow_codes.RUN_FAILED, failed[0][0].name)
        if image.find_newer_files():
            return ImageFact(flow_codes.IMAGE_OLDER, None)
        return ImageFact(flow_codes.IMAGE_TESTED if image.find_passed_logs() else flow_codes.IMAGE_UNTESTED, None)
    except DeployError as missing:
        if missing.reason == firmware_codes.NO_SIM_TOML:
            return ImageFact(flow_codes.NO_SIM_FILES, None)
        return UNREADABLE_FACT if missing.reason == firmware_codes.LOG_UNREADABLE else NO_IMAGE_FACT
    except OSError:
        return NO_IMAGE_FACT


def is_open(phase, fact):
    """True when the person acts on `phase` before the next: a status that is neither ok nor None, or a simulate with no
    status whose image `fact` leaves it open."""
    return phase.status not in (OK, None) or (phase.phase == flow_codes.SIMULATE and fact.fact in OPEN_IMAGE_FACTS)


def now_phase(phases, no_model, fact, all_aside=False):
    """The phase to act on now: the first open one not counted as done, or the idea while no need is written, or the parts
    while every need is set aside (P980: there is no pick to write the parts list from). An idea that is ok (the brief holds a goal,
    P1142) gives way to the needs, and a stale one does not. None when no phase is open: a
    deploy that saw ready on the image now (P1043), or a flow of other readers, which a test gives."""
    now = next((phase for phase in phases if phase.phase not in no_model and is_open(phase, fact)), None)
    if now and now.phase == flow_codes.REQUIREMENTS and now.status != COULD_NOT_RUN and all_aside:  # a broken file is not hidden
        return next((phase for phase in phases if phase.phase == flow_codes.PARTS), now)
    if now and now.phase == flow_codes.NEEDS and now.status == flow_codes.NOT_STARTED and phases[0].status != OK:
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
    """The NowSentence of the phase to act on now (P1133): a simulate with no sim/wokwi.toml by Claude (P1034), a simulate
    that opens a scenario run while no scenario is `written` (P1034), a simulate with no status by its ImageFact `fact`
    (flow_codes.IMAGE_NOW), else the phase's own `by` and its sentence by (phase, status) in flow_codes.NOW_SENTENCES,
    else the problems or could-not-run line. Its `chosen_by` is the (phase, value) the branch chose the sentence by."""
    if now.phase == flow_codes.SIMULATE and fact.fact == flow_codes.NO_SIM_FILES:
        return flow_codes.NowSentence([flow_codes.BY_CLAUDE], flow_codes.SIM_FILES_NOW, (flow_codes.SIMULATE, flow_codes.NO_SIM_FILES))
    if now.phase == flow_codes.SIMULATE and not written and (now.status == flow_codes.NOT_STARTED or fact.fact == flow_codes.IMAGE_UNTESTED):
        return flow_codes.NowSentence([flow_codes.BY_TERMINAL], flow_codes.SCENARIO_FIRST_NOW, (flow_codes.SIMULATE, flow_codes.NO_SCENARIO))
    if now.phase == flow_codes.SIMULATE and now.status is None:
        by, said = flow_codes.IMAGE_NOW[fact.fact]
        return flow_codes.NowSentence(by, said % fact.log if fact.fact == flow_codes.RUN_FAILED else said, (flow_codes.SIMULATE, fact.fact))
    said = flow_codes.NOW_SENTENCES.get((now.phase, now.status))
    if said == flow_codes.PARTS_NOW:
        return flow_codes.NowSentence([now.by], said % (flow_codes.ONE_NEED_HAS if len(open_needs) == 1 else flow_codes.MANY_NEEDS_HAVE % len(open_needs), ", ".join(open_needs)),
                                      (now.phase, now.status))
    if said:
        return flow_codes.NowSentence([now.by], said, (now.phase, now.status))
    if now.status == PROBLEMS:
        return flow_codes.NowSentence([now.by], flow_codes.PROBLEMS_NOW % now.phase, (now.phase, PROBLEMS))
    return flow_codes.NowSentence([now.by], flow_codes.COULD_NOT_RUN_NOW % now.phase, (now.phase, COULD_NOT_RUN))


def chat_offer_of(sentence):
    """The key of the chat offer whose job the NowSentence `sentence` asks Claude for (P1122, P1133): the one lookup of its
    `chosen_by` in `flow_codes.CHAT_NOW`, or None."""
    return flow_codes.CHAT_NOW.get(sentence.chosen_by)


def with_deploy_now(project, sentence, now, deploy=None):
    """The NowSentence of an open deploy after a deploy (P1043, P1122, `deploy_reading.deploy_now`) in place of `sentence`,
    from `deploy`, the DeployState the run read its deploy phase from (None: read it here, as `image_fact` reads the image:
    a fact on every Phase would change the phases' JSON). Else `sentence` as it is."""
    if not (now and now.phase == flow_codes.DEPLOY):
        return sentence
    state = deploy or deploy_reading.read_deploy(project)
    told = deploy_reading.deploy_now(state)
    return told or sentence


def requirements_now(by, written):
    """The NowSentence of a stale parts list (P1140): `by` acts, the sentence of STALE_REQUIREMENTS by `written` (whether the
    file is as spark last wrote it), chosen by (REQUIREMENTS, STALE), a pair that has no chat offer."""
    return flow_codes.NowSentence(by, flow_codes.STALE_REQUIREMENTS[written][1], (flow_codes.REQUIREMENTS, flow_codes.STALE))


def with_requirements_now(project, sentence, now):
    """The NowSentence of a stale parts list by whether the file is as spark last wrote it (P1140, `requirements_now`,
    `flow_codes.STALE_REQUIREMENTS`, the table the phase line reads too) in place of `sentence`, read here as
    `with_deploy_now` reads the deploy. Else `sentence`."""
    if not (now and now.phase == flow_codes.REQUIREMENTS and now.status == flow_codes.STALE):
        return sentence
    written = readable(lambda: entry_origin.EntryOriginStore(project).is_as_written(read_requirements(project)), None)
    return requirements_now(sentence.by, written)


def no_open_phase(said, by_name):
    """The guide's sentence when nothing is open: NO_OPEN_PHASE_NOW when there is no now and the deploy is ok (P1043), else
    None, so a flow of other readers gets none."""
    deploy = by_name.get(flow_codes.DEPLOY)
    return flow_codes.NO_OPEN_PHASE_NOW if said is None and deploy is not None and deploy.status == OK else None


def job_offer(now):
    """The key of the offer that does the job of the phase to act on now: its one offer of a kind the page sends, or None
    when it holds none or more than one (P1030: one rule, so the CLI's `next` and the page's NOW button name one offer). A
    breadboard now names none: the build's offer is in the build phase, until a NOW sentence names its button (piece 6)."""
    own = [offer.key for offer in now.offers if flow_codes.is_sendable(offer.key)]
    return own[0] if len(own) == 1 else None


def now_sentence(now, open_needs, fact, count, written=True):
    """The first NowSentence of the phase to act on now: with `count`, the steps of a current wiring sheet beside firmware not
    started, two jobs, the person's and Claude's; else `who_and_sentence`. `written` is false while a simulate now has no
    scenario. `with_deploy_now` and `with_requirements_now` may put another in its place."""
    if count is not None:
        return flow_codes.NowSentence([flow_codes.BY_YOU, flow_codes.BY_CLAUDE], flow_codes.TWO_JOBS_NOW % count, (now.phase, now.status))
    return who_and_sentence(now, open_needs, fact, written)


def now_of(now, sentence, open_needs, count):
    """`{phase, by, says, offer, chat_offer, needs, steps}` of the phase to act on now, from its last NowSentence `sentence`.
    `steps` is `count` (two jobs) or None. `chat_offer` is the key of the chat offer the sentence asks Claude for, or None:
    the one `chat_offer_of` of the last sentence (P1122, P1133)."""
    return {"phase": now.phase, "by": sentence.by, "says": sentence.says, "offer": job_offer(now), "chat_offer": chat_offer_of(sentence),
            "needs": open_needs if now.phase == flow_codes.PARTS else [], "steps": count}


def has_no_picks(by_name):
    """True when the needs phase has no status: no needs are written, so the requirements have no picks behind them (a
    requirements.json written by hand, or a last need dropped). An unreadable needs.json gives could-not-run, so false."""
    needs_phase = by_name.get(flow_codes.NEEDS)
    return needs_phase is not None and needs_phase.status is None


def place_of(index, name, at, no_model, breadboard_place):
    """Where the phase `name`, at `index` of the phases, stands beside the now phase at `at` (P1119): done before it, now,
    later after it. A simulate with no model is later wherever it stands, and the breadboard is now while
    `breadboard_place` is."""
    if name == flow_codes.SIMULATE and name in no_model:
        return flow_codes.LATER_PLACE
    if name == flow_codes.BREADBOARD and breadboard_place == flow_codes.NOW_PLACE:
        return flow_codes.NOW_PLACE
    return flow_codes.DONE_PLACE if index < at else flow_codes.NOW_PLACE if index == at else flow_codes.LATER_PLACE


def note_of(phase, place, no_model, breadboard_place, no_picks):
    """The one note of `phase` at `place` (P1119, `flow_codes.NO_PICKS_NOTE` and its kin), or None. Before now, with
    `no_picks` the needs and the parts are not done and the requirements have no picks behind them (P980), and the breadboard
    is unseen while `breadboard_place` is done (a current sheet) or has no sheet. A phase counted as done for no model says
    so, and a later phase whose status is ok may change."""
    name, done = phase.phase, place == flow_codes.DONE_PLACE
    if done and no_picks and name in (flow_codes.NEEDS, flow_codes.PARTS):
        return flow_codes.NOT_DONE_NOTE
    if done and no_picks and name == flow_codes.REQUIREMENTS:
        return flow_codes.NO_PICKS_NOTE
    if name in no_model:
        return flow_codes.NO_MODEL_NOTE
    if done and name == flow_codes.BREADBOARD:
        return flow_codes.UNSEEN_NOTE if breadboard_place == flow_codes.DONE_PLACE else flow_codes.NO_SHEET_NOTE
    return flow_codes.MAY_CHANGE_NOTE if place == flow_codes.LATER_PLACE and phase.status == OK else None


def stations_of(phases, at, no_model, breadboard_place, no_picks=False):
    """
    The station of each of the `phases` the guide is given, in their order (P1119): `{"phase", "place", "note"}`, with
    `place_of` and `note_of`. `at` is the index of the now phase, `len(phases)` with none. `no_model` holds the phases
    counted as done for no Wokwi model. `breadboard_place` is where the breadboard stands: NOW_PLACE beside the firmware
    (the two jobs), DONE_PLACE with a current sheet, else None. `no_picks`: no needs are written (`has_no_picks`). Pure: it
    reads no file.
    """
    stations = []
    for index, phase in enumerate(phases):
        place = place_of(index, phase.phase, at, no_model, breadboard_place)
        stations.append({"phase": phase.phase, "place": place, "note": note_of(phase, place, no_model, breadboard_place, no_picks)})
    return stations


def note_words(station):
    """The words of a station's note (P1119): its phase's own (`flow_codes.STATION_NOTES_BY_PHASE`), else the note's
    (`flow_codes.STATION_NOTES`). None for no note, or a note of LEFT_OUT_NOTES, which is in no list and on no line."""
    note = station["note"]
    if note is None or note in flow_codes.LEFT_OUT_NOTES:
        return None
    return flow_codes.STATION_NOTES_BY_PHASE.get((note, station["phase"])) or flow_codes.STATION_NOTES[note]


def named(station):
    """The name DONE and LATER show for a station: its phase, with its note's words in parentheses (NOTED_PHASE)."""
    words = note_words(station)
    return flow_codes.NOTED_PHASE % (station["phase"], words) if words else station["phase"]


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


def gate_a_of(fact, reached, no_model):
    """Gate A's one condition (P1220, D10): no failed run on the current image, and the row "Tested before the board". None
    before the On the board station is `reached`. Else `{shut_by, fact, says}`: `shut_by` is [RUN_FAILED] while a run failed
    on the image the ImageFact `fact` reads, [] when none did, and None when the runs cannot be read. `no_model` is True for
    a board Wokwi has no model of: its row says so unless a run failed. Gate A's other conditions are not built (P79 #16),
    so [] never means that gate A is open. Data only: no code refuses on it."""
    if not reached:
        return None
    if fact.fact == flow_codes.RUN_FAILED:
        return {"shut_by": [flow_codes.RUN_FAILED], "fact": fact.fact, "says": flow_codes.GATE_A_SAYS[fact.fact] % fact.log}
    code = flow_codes.NO_MODEL_NOTE if no_model and fact != UNREADABLE_FACT else fact.fact
    if code is None:
        return {"shut_by": None, "fact": None, "says": flow_codes.GATE_A_CANNOT_TELL}
    return {"shut_by": [], "fact": code, "says": flow_codes.GATE_A_SAYS[code]}


def guide_of(project, phases, steps=count_steps, deploy=None, board=None):
    """
    What the person does now, what is done, what comes later and what they set aside, from the Phases of `project`:
    `{"now": {phase, by, says, offer, chat_offer, needs, steps, with_wiring}, "stations", "done", "later", "set_aside", "no_simulation", "simulation", "no_open_phase", "wired", "gate_a"}`.
    `no_simulation` is the flag's sentence and `simulation` the line show and the page draw (`checks_reading.simulation_of`).
    `stations` places each phase beside the now (`stations_of`, P1119), and `done` and `later` are built from it. `steps` counts the wiring
    sheet's steps. The needs are read once more, by the parts phase's own rule (`counted`, `set_aside`). `deploy` is the
    run's DeployState (P1043), None to read it here. `board` is the run's WiredBoard (P1044), None to read it here:
    `wired` is `{sheet_at, deploy_at}`, the witnesses of a board that can be wired, or None when spark saw none.
    `gate_a` is `gate_a_of`'s row (P1220), None before the deploy has a board log or is now.
    """
    by_name, listed = {phase.phase: phase for phase in phases}, readable(lambda: needs.read(project), [])
    no_model = no_model_phases(project, by_name)
    simulate = by_name.get(flow_codes.SIMULATE)
    fact = image_fact(project, flow_codes.SIMULATE in no_model) if simulate and simulate.status in (None, flow_codes.NOT_STARTED) \
        else NO_IMAGE_FACT
    all_aside = bool(listed) and not counted(listed)
    now = now_phase(phases, no_model, fact, all_aside)
    deployed = by_name.get(flow_codes.DEPLOY)
    reached = bool(deployed) and (deployed.status != flow_codes.NOT_STARTED or bool(now and now.phase == flow_codes.DEPLOY))  # the On the board station
    at = phases.index(now) if now else len(phases)
    open_needs = [need["id"] for need in counted(listed) if not need.get("pick")]
    beside_sheet = now and now.phase == flow_codes.FIRMWARE and now.status == flow_codes.NOT_STARTED and is_sheet_current(project, by_name)
    count = steps(project) if beside_sheet else None
    two_jobs = count is not None  # no count: no two jobs, so the breadboard stays in done
    written = not (now and now.phase == flow_codes.SIMULATE) or bool(scenario_names(project))
    sentence = with_requirements_now(project, with_deploy_now(project, now_sentence(now, open_needs, fact, count, written), now, deploy), now) \
        if now else None
    said = dict(now_of(now, sentence, open_needs, count), with_wiring=with_wiring(project, now, by_name, count)) if now else None
    # beside the firmware, the wiring is part of now
    breadboard_place = flow_codes.NOW_PLACE if two_jobs else flow_codes.DONE_PLACE if is_sheet_current(project, by_name) else None
    stations = stations_of(phases, at, no_model, breadboard_place, has_no_picks(by_name))
    if board is None:
        board = wired_board.read_wired(project, deploy if deploy is not None else deploy_reading.read_deploy(project))
    no_sim, firmware = flow_codes.BUILD in no_model, by_name.get(flow_codes.FIRMWARE)  # one no-model rule for both keys
    return {"now": said, "stations": stations, "done": names_at(stations, flow_codes.DONE_PLACE),
            "later": names_at(stations, flow_codes.LATER_PLACE), "set_aside": [need["id"] for need in set_aside(listed)],
            "no_simulation": flow_codes.NO_SIMULATION_NOW if no_sim else None,
            "simulation": checks_reading.simulation_of(project, firmware is not None and firmware.status != flow_codes.NOT_STARTED, no_sim),
            "no_open_phase": no_open_phase(said, by_name), "wired": wired_board.wired_data(board),
            "gate_a": gate_a_of(fact, reached, flow_codes.SIMULATE in no_model)}
# --- end MVP ---
