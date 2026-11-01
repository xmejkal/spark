"""
Every board tool of the bench (P239 PR 8, P475): the flasher, the board shell, the port finder, the board reader, the
connection to the board, the ready check and the console probe. `FirmwarePlatform` is the base. `MicroPythonPlatform` is
the one platform spark has today. A platform for another language (Arduino, PlatformIO) would be another subclass, and a
test gives a Fake (tests/fakes.py) in its place. The five bench CLIs and `deploy_service.DeployService` take a platform,
so a test swaps the board tools without a patch.
"""

import json

import board_connection
import board_console
import board_look
import boards
import flasher
import ready_check
import tools
import board_codes
from project_image import DeployError


def board_of(project):
    """The project's board type, requirements.json's `board` (D35)."""
    return json.loads((project / "requirements.json").read_text()).get("board")


def record_of(project):
    """The board record requirements.json names (P192: no chip table). DeployError says why it cannot be read."""
    requirements = project / "requirements.json"
    try:
        return boards.load(project, board_of(project))
    except (OSError, ValueError, AttributeError, boards.BoardError) as cannot:
        raise DeployError("the board's chip cannot be read from %s: %s" % (requirements, cannot), reason=board_codes.CHIP_UNKNOWN)


# --- MVP --- the platform seam (P475): every board tool and the doctor's tool lookup come from one object
class FirmwarePlatform:
    """Strategy: the factories for a project's board tools. A subclass supplies each `make_` method, and `find_tool` for the
    role-to-Tool lookup the board doctor reads. Not a Value: its parts act."""

    def __init__(self, project):
        self.project = project

    def find_tool(self, role):
        """The tools.Tool for `role` (`flasher` or `board-shell`). tools.ToolProblem says why it is not installed."""
        raise NotImplementedError

    def make_flasher(self):
        """The Flasher for this project's chip. DeployError says why the chip cannot be read; tools.ToolProblem, the tool."""
        raise NotImplementedError

    def make_shell_command(self):
        """The board shell's command, as an argv list. tools.ToolProblem says why it is not installed."""
        raise NotImplementedError

    def make_port_finder(self, run):
        """The board_look.PortFinder over the board shell: it lists the boards on USB and opens no port."""
        raise NotImplementedError

    def make_board_reader(self, run, hint):
        """The board_look.BoardReader that reads the board on a port with the flasher's tool. `hint` is what to try when it
        cannot reach the board."""
        raise NotImplementedError

    def make_connection(self, command, port, run):
        """The connection to the board on `port`, through the shell's `command`."""
        raise NotImplementedError

    def make_ready_check(self, connection):
        """The ReadyCheck that reads the board through `connection`."""
        raise NotImplementedError

    def make_console_probe(self, port, run):
        """The probe that reads what the board's console says, or None when the shell cannot read a port."""
        raise NotImplementedError

    def board_of(self):
        """The project's board type, requirements.json's `board` (D35)."""
        return board_of(self.project)


class MicroPythonPlatform(FirmwarePlatform):
    """Strategy: MicroPython on an ESP32. esptool writes the image and reads the board, mpremote talks to it. Each tool is
    found when a step needs it, so a missing tool shows then and not before. `find_tool` is a (role -> tools.Tool) function:
    the project's tools list when None."""

    def __init__(self, project, find_tool=None):
        super().__init__(project)
        self._find_tool = find_tool or (lambda role: tools.find(role, project))

    def find_tool(self, role):
        return self._find_tool(role)

    def make_flasher(self):
        record = record_of(self.project)  # first: a record problem shows before a missing tool
        return flasher.EsptoolFlasher(self.find_tool("flasher"), record["chip"], boards.ButtonPlaces.from_record(record))

    def make_shell_command(self):
        return tools.command_for(self.find_tool("board-shell"))

    def make_port_finder(self, run):
        return board_look.PortFinder(self.find_tool("board-shell"), run)

    def make_board_reader(self, run, hint):
        return board_look.EsptoolReader(self.find_tool("flasher"), run, hint)

    def make_connection(self, command, port, run):
        return board_connection.BoardConnection(command, port, run)

    def make_ready_check(self, connection):
        return ready_check.ReadyCheck(connection)

    def make_console_probe(self, port, run):
        return board_console.ConsoleProbe.for_tool(self.find_tool("board-shell"), port, run)
# --- end MVP ---
