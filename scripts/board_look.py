"""
Read the board on USB without changing it, and compare it with the project's board record (P219, #201).

A library: look.py only parses arguments, calls `looker(project).run(project, port)` and prints the Report. The gate
module of step 4 will call it too. It reads the image checks from image_check.py and never imports deploy.py.
The seams are the readers: `BoardReader` is how a board is read, and `EsptoolReader` is the one reader today.

    PortFinder     the boards on USB, from mpremote's list. It never opens a port.
    EsptoolReader  one board's chip, flash size and MAC, from `esptool flash_id`.
    compare        each field of the reading against the record: same, differs or unknown.
    Look           the project's record, the port, the reading, the Report.
    Report         the verdict (match, warning or stop), the exit status and the token.

A board restarts when esptool reads it. Nothing is erased or written.
"""

import hashlib
import json
import re
import subprocess
from collections import namedtuple
from pathlib import Path

import boards
import image_check
import outcomes
import tools

#: mpremote devs lists these for Bluetooth and the debug console, and they are no board.
NOT_A_BOARD = "0000:0000"
Port = namedtuple("Port", "device serial usb product")
#: What esptool said, each field None when it could not be parsed. flash_mb is a number of MB.
Reading = namedtuple("Reading", "chip flash_mb mac")
MB = 1024 * 1024
#: How long a subprocess may take, in seconds: mpremote only lists, esptool connects to a board and may wait for it.
LIST_TIMEOUT_S, READ_TIMEOUT_S = 15, 60


def board_token(mac):
    """The board half of the look's token: 4 hex of sha256(MAC). It shows a look was made on this board; it is no secret."""
    return hashlib.sha256(mac.encode()).hexdigest()[:4]


#: How esptool 5.5.0 starts the line of its failure on stderr; the lines after it are a URL or a hint (P282's research).
ESPTOOL_ERROR = "ERROR: "


class LookStop(Exception):
    """The look cannot go on. The message is the whole sentence. When esptool could not read the board, `port` is its
    port and `tool_said` esptool's own line of the failure, shown to the person and never decided on (P282)."""

    def __init__(self, message, port=None, tool_said=None):
        super().__init__(message)
        self.port, self.tool_said = port, tool_said


def esptool_said(stderr):
    """esptool's own line of the failure in `stderr`: the first that starts with ESPTOOL_ERROR, else None."""
    return next((line.strip() for line in (stderr or "").splitlines() if line.startswith(ESPTOOL_ERROR)), None)


class PortFinder:
    """The boards on USB. It runs mpremote's `devs`, which only lists, never opens a port or runs code on a board."""

    def __init__(self, shell, run=subprocess.run):
        self.command, self.run = image_check.runnable(shell) + ["devs"], run

    def boards(self):
        try:
            done = self.run(self.command, capture_output=True, text=True, timeout=LIST_TIMEOUT_S)
        except OSError as cannot:
            raise LookStop("could not list the boards on USB: %s" % cannot)
        except subprocess.TimeoutExpired:
            raise LookStop("could not list the boards on USB: mpremote took more than %d s. %s"
                           % (LIST_TIMEOUT_S, image_check.BOOT_HINT))
        if done.returncode:
            lines = (done.stderr or "").strip().splitlines()
            raise LookStop("could not list the boards on USB: %s" % (lines[-1] if lines else "mpremote exited with %d" % done.returncode))
        rows = [line.split(None, 3) for line in done.stdout.splitlines()]
        return [Port(*(row + [""])[:4]) for row in rows if len(row) >= 3 and row[2] != NOT_A_BOARD]

    def require_one_port(self, script):
        """The port of the one board on USB. LookStop when there is none, or when there are two or more: it lists them
        and names `script`'s --port (P218's D25)."""
        return self.require_one_board(script).device

    def require_one_board(self, script, port=None):
        """The Port row of the one board on USB, or of `port` when it is given. LookStop as require_one_port says, and
        when `port` is not in the list."""
        found = self.boards()
        if port:
            named = [each for each in found if each.device == port]
            if not named:
                raise LookStop("no board on %s: mpremote devs does not list it." % port)
            return named[0]
        if not found:
            raise LookStop("no board found. Plug it straight into the computer with a data cable, not a hub that gives power only.")
        if len(found) > 1:
            lines = ["  %s  %s  %s" % (each.device, each.serial, each.product) for each in found]
            raise LookStop("%d boards on USB:\n%s\n%s --port %s  (unplug one to tell them apart)"
                           % (len(found), "\n".join(lines), script, found[0].device))
        return found[0]


class BoardReader:
    """How a board is read. `read(port)` returns a Reading, or raises LookStop when the board cannot be read."""

    def read(self, port):
        raise NotImplementedError


class EsptoolReader(BoardReader):
    """esptool 5.5.0's `flash_id` output, parsed with anchored lines. A field that does not parse is None."""

    def __init__(self, flasher, run=subprocess.run):
        self.flasher, self.run = flasher, run

    def read(self, port):
        if self.flasher.name != "esptool":
            raise LookStop("could not read: the look reads only esptool, and the flasher is %s" % self.flasher.name)
        command = image_check.runnable(self.flasher) + ["--port", port, "flash_id"]
        try:
            done = self.run(command, capture_output=True, text=True, timeout=READ_TIMEOUT_S)
        except OSError as cannot:
            raise LookStop("could not read the board on %s: %s" % (port, cannot), port)
        except subprocess.TimeoutExpired:
            raise LookStop("could not read the board on %s: esptool took more than %d s. %s"
                           % (port, READ_TIMEOUT_S, image_check.BOOT_HINT), port)
        if done.returncode:
            raise LookStop("could not read the board on %s. %s" % (port, image_check.BOOT_HINT), port,
                           esptool_said(done.stderr))
        return self.parse(done.stdout)

    @staticmethod
    def parse(text):
        """The Reading in esptool's output. The chip is the last `Detecting chip type...` line, as the record writes it."""
        def found(pattern):
            return re.findall(pattern, text, re.MULTILINE)

        chips = found(r"^Detecting chip type\.\.\. (ESP32(?:-\w+)?)\s*$")
        flash = found(r"^Detected flash size: (\d+)(MB|KB)\s*$")
        macs = found(r"^BASE MAC:\s+(\S+)") or found(r"^MAC:\s+(\S+)")
        size = None
        if flash:
            size = int(flash[0][0]) / (1024 if flash[0][1] == "KB" else 1)
            size = int(size) if size == int(size) else size
        return Reading(chips[-1].lower().replace("-", "") if chips else None, size, macs[0] if macs else None)


def _flash_same(read, recorded):
    return read in (recorded if isinstance(recorded, list) else [recorded])


#: The fields the look compares: (name, the reading's field, the record's key, how they match). A new field is a row.
FIELDS = (("chip", "chip", "chip", lambda read, recorded: read == recorded),
          ("flash", "flash_mb", "flash_mb", _flash_same))


def compare(reading, record):
    """{field: same | differs | unknown}. A field the board did not say, or the record does not hold, is unknown."""
    result = {}
    for name, read_key, record_key, matches in FIELDS:
        read, recorded = getattr(reading, read_key), record.get(record_key)
        result[name] = "unknown" if read is None or recorded is None else ("same" if matches(read, recorded) else "differs")
    return result


def _recorded(value):
    return " or ".join(str(each) for each in (value if isinstance(value, list) else [value]))


class Report:
    """What the look found. `stops` and `warnings` are sentences, `unknown` maps a field to why; the verdict is match,
    warning or stop."""

    def __init__(self, port, reading, record, image, image_why):
        self.port, self.reading, self.record = port, reading, record
        self.image, self.image_why = image, image_why  # the image Path or None; why no passed run names it, or None
        self.fields = compare(reading, record)
        self.stops, self.warnings = [], []
        if self.fields["chip"] == "differs":
            self.stops.append("this board is an %s, the project is for an %s" % (reading.chip, record["chip"]))
        if image and reading.flash_mb is not None and reading.flash_mb * MB < image.stat().st_size:  # whatever compare said
            self.stops.append("the flash is %s MB, the image needs %d MB" % (reading.flash_mb, -(-image.stat().st_size // MB)))
        elif self.fields["flash"] == "differs":
            self.warnings.append("the flash differs: %s MB, the record says %s" % (reading.flash_mb, _recorded(record["flash_mb"])))
        self.unknown = {name: "the board did not say" if getattr(reading, read_key) is None else "the record does not hold it"
                        for name, read_key, _, _ in FIELDS if self.fields[name] == "unknown"}
        self.verdict = "stop" if self.stops else "warning" if self.warnings or self.unknown else "match"

    @property
    def status(self):
        """The one outcome. A stop is a problem even when every field is `same` (the image does not fit a flash the
        record lists), and a look with no token went unchecked, since deploy.py cannot go on without one."""
        return outcomes.status_of([n for n, s in self.fields.items() if s == "differs"] + self.stops,
                                  list(self.unknown) + (["token"] if self.no_token_reason() else []))

    def exit_code(self):
        """What the shell sees: the exit for `status`."""
        return outcomes.EXIT_FOR[self.status]

    def no_token_reason(self):
        """Why there is no token, or None when there is one."""
        if self.verdict == "stop":
            return "the look found a stop"
        if not self.reading.mac:
            return "the board's MAC could not be read"
        return self.image_why

    def token(self):
        """4 hex of sha256(MAC), a dash, 4 hex of sha256(image): this board, this image. None when there is no_token_reason."""
        if self.no_token_reason():
            return None
        return "%s-%s" % (board_token(self.reading.mac), hashlib.sha256(self.image.read_bytes()).hexdigest()[:4])


class Look:
    """The look at one project: its record, the port, the reading."""

    def __init__(self, finder, reader):
        self.finder, self.reader = finder, reader

    def run(self, project, port=None, ignore_older_runs=False):
        """A Report. LookStop says why not: no record, no board, two boards without a port, a read that failed."""
        record = self.record_of(project)
        port = port or self.only_port()
        reading = self.reader.read(port)
        image, why = None, None
        try:
            image = image_check.image_of(project)
            runs = project / "sim" / "runs"
            why = image_check.untested(image, runs) or (None if ignore_older_runs else image_check.tested_another(image, runs))
        except image_check.DeployProblem as cannot:
            why = str(cannot)  # image stays set when only the logs could not be read: the fit check needs it
        return Report(port, reading, record, image, why)

    @staticmethod
    def record_of(project):
        """The board record requirements.json names, or a LookStop pointing to P230 (D36: two records only)."""
        try:
            name = json.loads((project / "requirements.json").read_text()).get("board")
        except (OSError, ValueError, AttributeError):
            name = None
        if not name:
            raise LookStop("requirements.json names no board")
        try:
            return boards.load(project, name)
        except boards.BoardError:
            raise LookStop("no board record for %s: P230 will research one." % name)

    def only_port(self):
        return self.finder.require_one_port("look.py")


def looker(project, run=subprocess.run):
    """A Look with mpremote and esptool as the project's tools list finds them. tools.ToolProblem becomes a LookStop."""
    try:
        return Look(PortFinder(tools.find("board-shell", project), run), EsptoolReader(tools.find("flasher", project), run))
    except tools.ToolProblem as cannot:
        raise LookStop(str(cannot))
