"""
The board log (P1043): the file `sim/runs/board/<moment>.log` that a deploy writes after a flash, beside the run logs.
A library. `BoardLog` is its text and `write_board_log` writes it. `newest_logged_deploy` reads the newest log back for
the flow's deploy reader: its time, its image, its verdict and its cause. It never takes the port, the facts line, the
console text or a tool's text, so none of them reaches a sentence.

The cause has one source, spark's own: the reason line that a log has from P1043 on, else the fixed start of spark's
sentence, before its first colon (`CAUSES`, for the older logs). A start that is not in the table gives no cause.
"""

import collections
from pathlib import Path

from spark.bench import board_codes, download_mode, ready_probe
from spark.core.errors import CodedMessageError

# --- MVP ---
#: The board logs' folder in a project, beside the run logs, whose *.log glob does not reach it.
BOARD_LOGS = Path("sim") / "runs" / "board"
#: What the first line starts with, before the moment; and the start of the image line and of the reason line.
MOMENT_LINE, IMAGE_LINE, REASON_LINE = "# deploy ", "image sha256: ", "reason: "
#: The line of the reason, counted from 0: after the moment, the image and the simulation, which are one line each.
REASON_AT = 3
#: The three verdicts a board log holds (ready_probe's). A registered project's `ready not read` is never in a log.
VERDICTS = (ready_probe.SEEN, ready_probe.NOT_SEEN, ready_probe.UNKNOWN)
#: The verdict line: a verdict, VERDICT_SEP, then spark's sentence. Every verdict word starts with VERDICT_START.
VERDICT_START, VERDICT_SEP = "ready ", ": "
#: The codes a reason line may hold: the causes of a verdict that is not ready seen.
REASONS = (board_codes.FILES_UNREAD, board_codes.FIRMWARE_NOT_STARTED, board_codes.NO_FILES_NAMED, board_codes.BOARD_LOST,
           board_codes.PORT_GONE, board_codes.DOWNLOAD_MODE_STAYED, board_codes.FILES_DIFFER, board_codes.FIRMWARE_ERROR,
           board_codes.NO_READY_LINE)
#: The cause of an older log's sentence, by its fixed start before the first colon. A lost board and files that differ
#: have no fixed start, so such an old log has no cause. A wait's start comes from its constant, so a changed wait leaves
#: the older logs with no cause, never a wrong one.
CAUSES = {"mpremote could not read the board's files": board_codes.FILES_UNREAD,
          "mpremote could not start the firmware": board_codes.FIRMWARE_NOT_STARTED,
          "the passed run's log names no files (an older spark)": board_codes.NO_FILES_NAMED,
          "the board's port is gone": board_codes.PORT_GONE,
          "the board still waits in download mode after %d s" % download_mode.RESET_WAIT_S: board_codes.DOWNLOAD_MODE_STAYED,
          "the firmware stopped with an error": board_codes.FIRMWARE_ERROR,
          "the firmware printed no %r in %d s" % (ready_probe.READY, ready_probe.READY_WAIT_S): board_codes.NO_READY_LINE}
#: The start of an older log's sentence after a board lost when ready was printed (ready_probe.LOST_NO_CALL): mpremote's
#: own text comes before its first colon, so CAUSES cannot hold it (the review of #1579).
LOST_START = "the firmware printed %r, %s" % (ready_probe.READY, ready_probe.LOST.split(" (", 1)[0])
#: Value: what the reader takes from one board log: the moment as written (with its zone), the image's sha256, the
#: verdict and the cause's code, or None (ready seen, or not recorded).
LoggedDeploy = collections.namedtuple("LoggedDeploy", "at image verdict cause")


class BoardLogError(CodedMessageError):
    """Error: a board log cannot be read. Its code is BOARD_LOG_UNREADABLE (`unreadable`)."""


def unreadable(name, missing):
    """The BoardLogError of the log `name`: its sentence names the file under sim/runs/board/ only, and what is `missing`."""
    return BoardLogError("%s cannot be read: %s", (BOARD_LOGS / name).as_posix(), missing, code=board_codes.BOARD_LOG_UNREADABLE)


class BoardLog(collections.namedtuple("BoardLog", "moment port image_sha256 facts_line verdict sentence heard simulation reason",
                                      defaults=(None,))):
    """Value: the facts of the board's log after a flash. `heard` is the console text, then what the board printed.
    `reason` is the cause's code (P1043), written as line 4, or None for no line."""

    def text(self):
        """The log file's text."""
        return "# deploy %s on %s\nimage sha256: %s\nsimulation: %s\n%s%s\n%s: %s\n\n%s\n" % (
            self.moment.isoformat(timespec="seconds"), self.port, self.image_sha256, self.simulation,
            REASON_LINE + self.reason + "\n" if self.reason else "", self.facts_line, self.verdict, self.sentence, self.heard)


def write_board_log(project, log):
    """The board's log (a BoardLog) in sim/runs/board/ beside the run logs, whose *.log glob does not reach it. Returns
    its path."""
    path = project / BOARD_LOGS / ("%s.log" % log.moment.strftime("%Y-%m-%dT%H-%M-%S"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(log.text())
    return path


def cause_of(sentence):
    """The code of `sentence`'s start before its first colon, by CAUSES, or BOARD_LOST for LOST_START, or None. Never the
    start itself."""
    if sentence.startswith(LOST_START):
        return board_codes.BOARD_LOST
    return CAUSES.get(sentence.split(":", 1)[0])


def old_cause_of(sentence, lines):
    """The cause of an older log with no reason line, by its sentence. A read again (download_mode.READ_AGAIN) after a
    first read that may have read the files gives no FILES_UNREAD: the log cannot tell whether they were read."""
    cause = cause_of(sentence)
    return None if cause == board_codes.FILES_UNREAD and download_mode.READ_AGAIN in lines else cause


def logged_deploy(name, text):
    """The LoggedDeploy of one board log's `text`. BoardLogError when its moment, image or verdict line is missing, or
    its verdict is not one of VERDICTS."""
    lines = text.splitlines()
    at = lines[0][len(MOMENT_LINE):].split(" ", 1)[0] if lines and lines[0].startswith(MOMENT_LINE) else ""
    image = next((line[len(IMAGE_LINE):] for line in lines if line.startswith(IMAGE_LINE)), "")
    said = next((line.split(VERDICT_SEP, 1) for line in lines[REASON_AT:] if line.startswith(VERDICT_START) and VERDICT_SEP in line),
                None)
    if not at or not image or said is None:
        raise unreadable(name, "no moment, image or verdict line")
    if said[0] not in VERDICTS:
        raise unreadable(name, "its verdict is not one of %s" % ", ".join(VERDICTS))
    reason = lines[REASON_AT][len(REASON_LINE):] if lines[REASON_AT].startswith(REASON_LINE) else None
    return LoggedDeploy(at, image, said[0], reason if reason in REASONS else old_cause_of(said[1], lines) if said[0] != ready_probe.SEEN else None)


def newest_logged_deploy(project):
    """(how many board logs `project` holds, the LoggedDeploy of the newest by name), or (0, None) with none.
    BoardLogError when the newest cannot be read."""
    logs = sorted((Path(project) / BOARD_LOGS).glob("*.log"))
    if not logs:
        return 0, None
    try:
        text = logs[-1].read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise unreadable(logs[-1].name, "it is not UTF-8 text") from None
    return len(logs), logged_deploy(logs[-1].name, text)
# --- end MVP ---
