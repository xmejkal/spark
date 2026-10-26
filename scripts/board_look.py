"""
Read the board on USB without changing it, and compare it with the project's board record (P219, #201).

A library: look.py only parses arguments, calls `looker(project).run(project, port, evidence)` and prints `report_lines(report)`.
deploy.py calls `looker` and `report_lines` too. It reads the image checks from project_image.py and never imports deploy.py.
The seams are the readers: `BoardReader` is how a board is read, and `EsptoolReader` is the one reader today.

    PortFinder     the boards on USB, from mpremote's list. It never opens a port.
    EsptoolReader  one board's chip, flash size and MAC, from `esptool flash_id`.
    compare        each field of the reading against the record: same, differs or unknown.
    LookService    the project's record, the port, the reading, the LookReport.
    LookReport     the verdict (match, warning or stop), the exit status and the token, as a dict too.
    report_lines   the lines a person reads, for a LookReport.

A board restarts when esptool reads it. Nothing is erased or written.
"""

import hashlib
import json
import re
import subprocess
from collections import namedtuple

import board_facts
import boards
import flasher
import outcomes
import project_image
import tools

#: mpremote devs lists these for Bluetooth and the debug console, and they are no board.
NOT_A_BOARD = "0000:0000"
#: What mpremote devs prints in the serial column of a board that reports no USB serial.
NO_SERIAL = "None"
#: The look's port line when the board shows on more than one node (P333).
ALSO_ON = "  (one board on more nodes, also %s: the same USB serial. If these are two boards, unplug one)"
Port = namedtuple("Port", "device serial usb product also_on", defaults=((),))
#: What esptool said, each field None when it could not be parsed. flash_mb is a number of MB.
BoardReading = namedtuple("BoardReading", "chip flash_mb mac")
MB = 1024 * 1024
#: How long a subprocess may take, in seconds: mpremote only lists, esptool connects to a board and may wait for it.
LIST_TIMEOUT_S, READ_TIMEOUT_S = 15, 60

RESTART_NOTICE = "the board restarts while it is read: a running program stops and starts again. Nothing is erased or written."
TOKEN_LINE = "token  %s  for deploy.py --token. It is not your yes: deploy.py asks for that."


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
        self.command, self.run = tools.command_for(shell) + ["devs"], run

    def nodes(self):
        try:
            done = self.run(self.command, capture_output=True, text=True, timeout=LIST_TIMEOUT_S)
        except OSError as cannot:
            raise LookStop("could not list the boards on USB: %s" % cannot)
        except subprocess.TimeoutExpired:
            raise LookStop("could not list the boards on USB: mpremote took more than %d s. %s"
                           % (LIST_TIMEOUT_S, flasher.EsptoolFlasher.boot_hint_for(boards.ButtonPlaces.EMPTY)))
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
        found = self.nodes()
        if port:
            named = [each for each in found if each.device == port]
            if not named:
                raise LookStop("no board on %s: mpremote devs does not list it." % port)
            return named[0]
        on_usb = boards_of(found)
        if not on_usb:
            raise LookStop("no board found. Plug it straight into the computer with a data cable, not a hub that gives power only. "
                           "If the plug is USB-C, turn it around, or use a USB-A to USB-C cable.")
        if len(on_usb) > 1:
            lines = [_listed(board) for board in on_usb]
            raise LookStop("%d boards on USB:\n%s\n%s --port %s  (unplug one to tell them apart)"
                           % (len(on_usb), "\n".join(lines), script, port_of(on_usb[0]).device))
        return port_of(on_usb[0])


def boards_of(ports):
    """The boards behind `ports`, each a list of its Port rows, in the order listed (P333). Rows with one USB serial, USB
    id and product are one board only when one of them is named by that serial: macOS shows a CP2104 as
    /dev/cu.SLAB_USBtoUART and /dev/cu.usbserial-<serial>. Every other row is a board of its own, so two clones that share
    a serial (/dev/ttyUSB0 and /dev/ttyUSB1, both `0001`) still stop as two boards, and so do rows with no serial
    (mpremote prints `None`)."""
    grouped = {}
    for port in ports:
        known = port.serial not in ("", NO_SERIAL)
        grouped.setdefault((port.serial, port.usb, port.product) if known else ("device", port.device), []).append(port)
    return [board for rows in grouped.values() for board in ([rows] if len(rows) > 1 and _named_by_serial(rows) else [[row] for row in rows])]


def _named_by_serial(rows):
    return any(row.device.endswith(row.serial) for row in rows)


def port_of(board):
    """The Port a board is used on: the node named by its serial (the one the T-Display was read on), or the board's only
    node. Its `also_on` names the board's other nodes."""
    chosen = next((port for port in board if len(board) > 1 and port.device.endswith(port.serial)), board[0])
    return chosen._replace(also_on=tuple(port.device for port in board if port is not chosen))


def _listed(board):
    port = port_of(board)
    return "  %s  %s  %s%s" % (port.device, port.serial, port.product, "  (also %s)" % ", ".join(port.also_on) if port.also_on else "")


class BoardReader:
    """How a board is read. `read(port)` returns a BoardReading, or raises LookStop when the board cannot be read."""

    def read(self, port):
        raise NotImplementedError


class EsptoolReader(BoardReader):
    """esptool 5.5.0's `flash_id` output, parsed with anchored lines. A field that does not parse is None."""

    def __init__(self, flasher_tool, run=subprocess.run, boot_hint=flasher.EsptoolFlasher.boot_hint_for(boards.ButtonPlaces.EMPTY)):
        self.flasher_tool, self.run, self.boot_hint = flasher_tool, run, boot_hint

    def read(self, port):
        if self.flasher_tool.name != "esptool":
            raise LookStop("could not read: the look reads only esptool, and the flasher is %s" % self.flasher_tool.name)
        command = flasher.build_esptool_prefix(self.flasher_tool, port) + ["flash_id"]
        try:
            done = self.run(command, capture_output=True, text=True, timeout=READ_TIMEOUT_S)
        except OSError as cannot:
            raise LookStop("could not read the board on %s: %s" % (port, cannot), port)
        except subprocess.TimeoutExpired:
            raise LookStop("could not read the board on %s: esptool took more than %d s. %s"
                           % (port, READ_TIMEOUT_S, self.boot_hint), port)
        if done.returncode:
            raise LookStop("could not read the board on %s. %s" % (port, self.boot_hint), port,
                           esptool_said(done.stderr))
        return self.parse(done.stdout)

    @staticmethod
    def parse(text):
        """The BoardReading in esptool's output. The chip is the last `Detecting chip type...` line, as the record writes it."""
        def found(pattern):
            return re.findall(pattern, text, re.MULTILINE)

        chips = found(r"^Detecting chip type\.\.\. (ESP32(?:-\w+)?)\s*$")
        flash = found(r"^Detected flash size: (\d+)(MB|KB)\s*$")
        macs = found(r"^BASE MAC:\s+(\S+)") or found(r"^MAC:\s+(\S+)")
        size = None
        if flash:
            size = int(flash[0][0]) / (1024 if flash[0][1] == "KB" else 1)
            size = int(size) if size == int(size) else size
        return BoardReading(chips[-1].lower().replace("-", "") if chips else None, size, macs[0] if macs else None)


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


#: The look's verdicts: a stop refuses, a warning or an unknown field asks the person, a match asks nothing more.
VERDICT_STOP, VERDICT_WARNING, VERDICT_MATCH = "stop", "warning", "match"


class LookReport:
    """Value. What the look found. `stops` and `warnings` are sentences, `unknown` maps a field to why; the verdict is match,
    warning or stop. `simulation` and `caveats` are what the evidence says of the image, or None and [] when it refused the image.
    `last_deploy` is the board_facts.LastDeploy of the board's MAC, whatever the evidence said."""

    def __init__(self, port, reading, record, image, image_why, simulation, caveats, last_deploy, also_on=None):
        self.port, self.reading, self.record = port, reading, record
        self.also_on = None if also_on is None else tuple(also_on)  # None: a --port was named, so no node list was read
        self.image, self.image_why = image, image_why  # the image Path or None; why the evidence refuses it, or None
        self.simulation, self.caveats = simulation, list(caveats)
        self.last_deploy = last_deploy
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
        self.verdict = (VERDICT_STOP if self.stops else
                        VERDICT_WARNING if self.warnings or self.unknown else VERDICT_MATCH)

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
        if self.verdict == VERDICT_STOP:
            return "the look found a stop"
        if not self.reading.mac:
            return "the board's MAC could not be read"
        return self.image_why

    def token(self):
        """4 hex of sha256(MAC), a dash, 4 hex of sha256(image): this board, this image. None when there is no_token_reason."""
        if self.no_token_reason():
            return None
        return "%s-%s" % (board_token(self.reading.mac), hashlib.sha256(self.image.read_bytes()).hexdigest()[:4])

    def to_dict(self):
        """The facts of the look as plain JSON values, for `--json` (P213). `board` is the record's id; the image is not in it."""
        return {"port": self.port, "also_on": None if self.also_on is None else list(self.also_on), "chip": self.reading.chip, "flash_mb": self.reading.flash_mb, "mac": self.reading.mac,
                "board": self.record["id"], "fields": dict(self.fields), "stops": list(self.stops),
                "warnings": list(self.warnings), "unknown": dict(self.unknown), "verdict": self.verdict,
                "status": self.status, "token": self.token(), "no_token_reason": self.no_token_reason(),
                "simulation": self.simulation, "caveats": list(self.caveats), "last_deploy": self.last_deploy.to_dict()}


def report_lines(report, token=True):
    """The lines a person reads, for a LookReport. deploy.py prints them without the token line."""
    reading, name = report.reading, report.record["id"]
    shown = {"chip": reading.chip, "flash": "%s MB" % reading.flash_mb if reading.flash_mb is not None else None}
    out = [RESTART_NOTICE, "port   %s%s" % (report.port, ALSO_ON % ", ".join(report.also_on) if report.also_on else ""), "mac    %s" % (reading.mac or "not read"),
           report.last_deploy.line()]
    out += ["%-6s %-9s %s" % (field, report.fields[field], shown[field] or "not read") for field in shown]
    out += ["%s: deploy.py will refuse." % stop for stop in report.stops]
    out += ["%s. deploy.py will ask you to accept it." % warning for warning in report.warnings]
    if report.unknown:
        out.append("%d field%s unknown (%s): deploy.py will ask you to accept it."
                   % (len(report.unknown), "" if len(report.unknown) == 1 else "s",
                      ", ".join("%s: %s" % each for each in report.unknown.items())))
    if report.simulation:
        out.append("simulation: %s" % report.simulation)
    out += report.caveats
    if report.verdict == VERDICT_MATCH:
        out.append("all fields match the board record %s." % name)
    if token:
        mine = report.token()
        out.append(TOKEN_LINE % mine if mine else "no token: %s" % report.no_token_reason())
    return ["  " + line for line in out]


class LookService:
    """The look at one project: its record, the port, the reading."""

    def __init__(self, finder, reader):
        self.finder, self.reader = finder, reader

    def run(self, project, port, evidence):
        """A LookReport. LookStop says why not: no record, no board, two boards without a port, a read that failed."""
        record = self.record_of(project)
        listed = None if port else self.finder.require_one_board("look.py")
        port = port or listed.device
        reading = self.reader.read(port)
        image, why, simulation, caveats = None, None, None, []
        try:
            found = project_image.ProjectImage(project)
            image = found.path
            why = evidence.why_not_ready(found)
            # --- MVP ---
            if why is None:  # what tested an image is stated only for one the evidence passes
                simulation, caveats = evidence.simulation, evidence.caveats(found)
        except project_image.DeployError as cannot:
            why = str(cannot)  # image stays set when only the logs could not be read: the fit check needs it
        # --- MVP --- an erase follows any evidence, so the last deploy is read whatever the evidence said
        return LookReport(port, reading, record, image, why, simulation, caveats, board_facts.read_last_deploy(reading.mac),
                          listed.also_on if listed else None)

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


def looker(project, run=subprocess.run):
    """A LookService with mpremote and esptool as the project's tools list finds them. tools.ToolProblem becomes a LookStop."""
    try:
        hint = flasher.EsptoolFlasher.boot_hint_for(boards.ButtonPlaces.of_project(project))
        return LookService(PortFinder(tools.find("board-shell", project), run),
                           EsptoolReader(tools.find("flasher", project), run, hint))
    except tools.ToolProblem as cannot:
        raise LookStop(str(cannot))
