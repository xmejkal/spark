"""
The flow's half of the deploy (P1043, #1533): what the newest board log in sim/runs/board/ and the image the project
holds now say of the deploy phase. The bench's `board_log` reads the log: its time, image, verdict and cause. This
module adds the image's fact, the phase's status and its sentences, and `data.deploy`. It reads and never writes, and no
tool's text, port or path reaches a sentence.
"""

from collections import namedtuple
from pathlib import Path

from spark.bench import board_codes, board_log, ready_probe
from spark.firmware import firmware_codes
from spark.firmware.project_image import DeployError, ProjectImage
from spark.flow import flow_codes
from spark.core.errors import CodedMessageError
from spark.core.outcomes import COULD_NOT_RUN, OK, PROBLEMS
from spark.core.zone_time import day_and_time

# --- MVP ---
#: How many hex digits of the image's sha256 a says line shows. `data.deploy.image` holds them all.
SHORT_IMAGE = 12
#: Value: the deploy as one run of `show` or the page reads it, once (the review of #1579): how many board logs, the newest
#: LoggedDeploy, its fact and the phase's status, as `deploy_state` gives them; or COULD_NOT_RUN with the `error` that a
#: log or the image raised. The reader, the guide and `data.deploy` all take this one state, so a log that lands between
#: two reads cannot make them disagree.
DeployState = namedtuple("DeployState", "count logged fact status error")


def deploy_fact(project, logged):
    """What the image `project` holds now says of the LoggedDeploy `logged`: DEPLOY_NO_IMAGE with no image, FIRMWARE_NEWER
    when a file under firmware/ changed after the image, IMAGE_DIFFERS when the log names another image, else
    DEPLOY_CURRENT. A firmware line spark cannot use is a CodedMessageError, as the simulate reads it."""
    try:
        image = ProjectImage(Path(project), default_without_toml=True)
    except DeployError as missing:
        if missing.reason == firmware_codes.NO_IMAGE:
            return flow_codes.DEPLOY_NO_IMAGE
        raise CodedMessageError("%s", missing, code=missing.reason)
    if image.find_newer_files():
        return flow_codes.FIRMWARE_NEWER
    return flow_codes.IMAGE_DIFFERS if image.sha256 != logged.image else flow_codes.DEPLOY_CURRENT


def deploy_state(project):
    """(how many board logs, the newest LoggedDeploy, its fact, the phase's status), by the order no log, a log that
    cannot be read (BoardLogError), the fact, then the verdict: (0, None, None, NOT_STARTED) with no log. A stale image
    wins over the verdict. Only ready seen on the image now is OK."""
    count, logged = board_log.newest_logged_deploy(project)
    if not count:
        return 0, None, None, flow_codes.NOT_STARTED
    fact = deploy_fact(project, logged)
    if fact != flow_codes.DEPLOY_CURRENT:
        return count, logged, fact, flow_codes.STALE
    if logged.verdict == ready_probe.SEEN:
        return count, logged, fact, OK
    return count, logged, fact, PROBLEMS if logged.verdict == ready_probe.NOT_SEEN else flow_codes.PARTIAL


def read_deploy(project):
    """The DeployState of `project`, read once. It never raises: a log or an image that cannot be read gives COULD_NOT_RUN
    with its error, which the deploy phase says."""
    try:
        return DeployState(*deploy_state(project), None)
    except (CodedMessageError, OSError) as unread:
        return DeployState(0, None, None, COULD_NOT_RUN, unread)


def read_back_of(logged):
    """Whether spark read the board's files back after the write: True for ready seen and ready not seen, which only a
    read of the files gives (ready_probe's files_read), else by the cause (None: the log cannot tell, or the cause is not
    recorded)."""
    return True if logged.verdict != ready_probe.UNKNOWN else flow_codes.CAUSE_WORDS.get(logged.cause, (None, None))[1]


def verdict_words(logged):
    """The words of the logged verdict: ready seen and ready not seen as they are, ready unknown by its cause's read-back,
    and a lost board after ready by its own words."""
    if logged.verdict == ready_probe.SEEN:
        return flow_codes.SEEN_WORDS
    if logged.verdict == ready_probe.NOT_SEEN:
        return flow_codes.NOT_SEEN_WORDS
    if logged.cause == board_codes.BOARD_LOST:
        return flow_codes.LOST_WORDS
    return {False: flow_codes.NO_READ_BACK_WORDS, True: flow_codes.READ_BACK_WORDS}.get(read_back_of(logged), flow_codes.UNSURE_WORDS)


def cause_words(logged):
    """The cause's sentence of a verdict that is not ready seen: spark's words for its code, or NO_CAUSE_MESSAGE."""
    words = flow_codes.CAUSE_WORDS.get(logged.cause)
    return flow_codes.CAUSE_MESSAGE % words[0] if words else flow_codes.NO_CAUSE_MESSAGE


def deploy_parts(logged, fact):
    """(a stale fact's opener or None, the verdict's words, [the cause's sentence] or [] for ready seen): the one rule that
    `deployed_says` and `deployed_line` (P1062) each say in their own template."""
    cause = [cause_words(logged)] if logged.verdict != ready_probe.SEEN else []
    return flow_codes.STALE_DEPLOY_SAYS.get(fact), verdict_words(logged), cause


def deployed_says(count, logged, fact):
    """The deploy phase's says after a deploy, one line: a stale fact's opener, then the time, the image, the verdict's
    words, the cause and last how many logs there are, each sentence after the one before."""
    opener, words, cause = deploy_parts(logged, fact)
    line = [flow_codes.DEPLOYED_MESSAGE % (logged.at, logged.image[:SHORT_IMAGE], words)] + cause
    line += [flow_codes.DEPLOYS_LOGGED[count != 1] % count]
    return [" ".join(([opener] if opener else []) + line)]


def deployed_line(deploy):
    """ON THE BOARD's sentence on the page (P1062), from `data.deploy` (`deploy_data`), or None for None: a stale fact's
    opener, the time read in the machine's zone, the verdict's words and the cause unless ready was seen, by the rule of
    `deploy_parts`. It holds no image digits and no count: the deploy phase's own line says those."""
    if deploy is None:
        return None
    logged = board_log.LoggedDeploy(deploy["at"], deploy["image"], deploy["verdict"], deploy["cause"])
    opener, words, cause = deploy_parts(logged, deploy["fact"])
    line = [flow_codes.DEPLOYED_LINE % (day_and_time(deploy["at"]), words[:1].upper() + words[1:])] + cause
    return " ".join(([opener] if opener else []) + line)


def deploy_now(state):
    """(who acts, the sentence) of an open deploy after a deploy (P1043), by its DeployState: a stale one by its fact
    (STALE_DEPLOY_NOW, P1043-D4), problems with its cause's words, a partial one by its cause's group: a lost board after
    ready, a port gone or download mode, a start not confirmed, or a cause not recorded. None for any other status, which
    keeps its own sentence."""
    status, logged = state.status, state.logged
    if status not in (flow_codes.STALE, flow_codes.PARTIAL, PROBLEMS):
        return None
    if status == flow_codes.STALE:
        return flow_codes.STALE_DEPLOY_NOW[state.fact]
    words = flow_codes.CAUSE_WORDS.get(logged.cause, (None, None))[0]
    if status == PROBLEMS:
        return [flow_codes.BY_TERMINAL], flow_codes.DEPLOY_PROBLEMS_NOW % (words or flow_codes.NO_READY_SEEN_WORDS)
    if logged.cause == board_codes.BOARD_LOST:
        return [flow_codes.BY_TERMINAL], flow_codes.DEPLOY_LOST_NOW
    if logged.cause in (board_codes.PORT_GONE, board_codes.DOWNLOAD_MODE_STAYED):
        return [flow_codes.BY_TERMINAL], flow_codes.DEPLOY_AWAY_NOW % words
    return [flow_codes.BY_TERMINAL], flow_codes.DEPLOY_NO_START_NOW if words else flow_codes.DEPLOY_UNKNOWN_NOW


def deploy_data(state):
    """`data.deploy` of `show`: `{at, image, verdict, cause, fact, read_back}` of the newest board log in the DeployState
    `state`, or None with no log, or one that cannot be read (the phase says why). A null `cause` is ready seen, or a
    cause not recorded."""
    logged = state.logged
    if logged is None:
        return None
    return {"at": logged.at, "image": logged.image, "verdict": logged.verdict, "cause": logged.cause, "fact": state.fact,
            "read_back": read_back_of(logged)}
# --- end MVP ---
