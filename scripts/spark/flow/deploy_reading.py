"""
The flow's half of the deploy (P1043, #1533): what the newest board log in sim/runs/board/ and the image the project
holds now say of the deploy phase. The bench's `board_log` reads the log: its time, image, verdict and cause. This
module adds the image's fact, the phase's status and its sentences, and `data.deploy`. It reads and never writes, and no
tool's text, port or path reaches a sentence.
"""

from pathlib import Path

from spark.bench import board_codes, board_log, ready_probe
from spark.firmware import firmware_codes
from spark.firmware.project_image import DeployError, ProjectImage
from spark.flow import flow_codes
from spark.core.errors import CodedMessageError
from spark.core.outcomes import OK, PROBLEMS

# --- MVP ---
#: How many hex digits of the image's sha256 a says line shows. `data.deploy.image` holds them all.
SHORT_IMAGE = 12


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


def read_back_of(logged):
    """Whether spark read the board's files back after the write: True for ready seen, else by the cause (None: the log
    cannot tell, or the cause is not recorded)."""
    return True if logged.verdict == ready_probe.SEEN else flow_codes.CAUSE_WORDS.get(logged.cause, (None, None))[1]


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


def deployed_says(count, logged, fact):
    """The deploy phase's says after a deploy: a stale fact's opener, then one line with the time, the image, the verdict's
    words, the cause and last how many logs there are."""
    line = [flow_codes.DEPLOYED_MESSAGE % (logged.at, logged.image[:SHORT_IMAGE], verdict_words(logged))]
    line += [cause_words(logged)] if logged.verdict != ready_probe.SEEN else []
    line += [flow_codes.DEPLOYS_LOGGED[count != 1] % count]
    opener = flow_codes.STALE_DEPLOY_SAYS.get(fact)
    return ([opener] if opener else []) + [" ".join(line)]


def deploy_now(project, status):
    """(who acts, the sentence) of an open deploy after a deploy (P1043): a stale one by its fact (STALE_DEPLOY_NOW, P1043-D4),
    problems with its cause's words, a partial one by its cause's group: a lost board after ready, a port gone or download
    mode, a start not seen, or a cause not recorded. None for any other status, which keeps its own sentence."""
    if status not in (flow_codes.STALE, flow_codes.PARTIAL, PROBLEMS):
        return None
    _, logged, fact, _ = deploy_state(project)
    if status == flow_codes.STALE:
        return flow_codes.STALE_DEPLOY_NOW[fact]
    words = flow_codes.CAUSE_WORDS.get(logged.cause, (None, None))[0]
    if status == PROBLEMS:
        return [flow_codes.BY_TERMINAL], flow_codes.DEPLOY_PROBLEMS_NOW % (words or flow_codes.NO_READY_SEEN_WORDS)
    if logged.cause == board_codes.BOARD_LOST:
        return [flow_codes.BY_TERMINAL], flow_codes.DEPLOY_LOST_NOW
    if logged.cause in (board_codes.PORT_GONE, board_codes.DOWNLOAD_MODE_STAYED):
        return [flow_codes.BY_TERMINAL], flow_codes.DEPLOY_AWAY_NOW % words
    return [flow_codes.BY_TERMINAL], flow_codes.DEPLOY_NO_START_NOW if words else flow_codes.DEPLOY_UNKNOWN_NOW


def deploy_data(project):
    """`data.deploy` of `show`: `{at, image, verdict, cause, fact, read_back}` of the newest board log, or None with no
    log, or one that cannot be read (the phase says why). A null `cause` is ready seen, or a cause not recorded."""
    try:
        _, logged, fact, _ = deploy_state(project)
    except (CodedMessageError, OSError):
        return None
    if logged is None:
        return None
    return {"at": logged.at, "image": logged.image, "verdict": logged.verdict, "cause": logged.cause, "fact": fact,
            "read_back": read_back_of(logged)}
# --- end MVP ---
