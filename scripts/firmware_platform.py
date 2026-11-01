"""
The parts of a deploy that depend on the firmware's language (P239 PR 8): the flasher, the connection to the board, the
ready check and the console probe. `FirmwarePlatform.micropython` builds the one platform spark has today. A platform for
another language (Arduino, PlatformIO) would be another builder beside it, with its own parts. deploy.py builds it
and hands it to `deploy_service.DeployService`.
"""

import json
import subprocess

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


def _esptool_flasher(project):
    """The EsptoolFlasher for the project's chip and button places. The record is read first, so a record problem shows
    before a missing tool."""
    record = record_of(project)
    return flasher.EsptoolFlasher(tools.find("flasher", project), record["chip"], boards.ButtonPlaces.from_record(record))


class FirmwarePlatform:
    """The factories for a project's flasher, board connection, ready check and console probe. Not a Value: its parts act.
    `make_flasher`, `make_shell_command` and `make_console_probe` call `tools.find` when they are called, so a missing
    tool shows when the step needs it, not before."""

    def __init__(self, project, make_flasher, make_shell_command, make_connection, make_ready_check, make_console_probe):
        self.project = project
        self._make_flasher, self._make_shell_command = make_flasher, make_shell_command
        self._make_connection, self._make_ready_check = make_connection, make_ready_check
        self._make_console_probe = make_console_probe

    @classmethod
    def micropython(cls, project):
        """The platform for MicroPython on an ESP32: esptool writes the image, mpremote talks to the board."""
        return cls(project,
                   lambda: _esptool_flasher(project),
                   lambda: tools.command_for(tools.find("board-shell", project)),
                   board_connection.BoardConnection,
                   ready_check.ReadyCheck,
                   lambda port, run: board_console.ConsoleProbe.for_tool(tools.find("board-shell", project), port, run))

    def make_flasher(self):
        """The Flasher for this project's chip. DeployError says why the chip cannot be read; tools.ToolProblem, the tool."""
        return self._make_flasher()

    def make_shell_command(self):
        """The board shell's command, as an argv list. tools.ToolProblem says why it is not installed."""
        return self._make_shell_command()

    def make_port_finder(self, run):
        """The board_look.PortFinder over the board shell: it lists the boards on USB and opens no port."""
        return board_look.PortFinder(tools.find("board-shell", self.project), run)

    def make_connection(self, command, port, run=subprocess.run):
        """The connection to the board on `port`, through the shell's `command`."""
        return self._make_connection(command, port, run)

    def make_ready_check(self, connection):
        """The ReadyCheck that reads the board through `connection`."""
        return self._make_ready_check(connection)

    def make_console_probe(self, port, run=subprocess.run):
        """The probe that reads what the board's console says, or None when the shell cannot read a port."""
        return self._make_console_probe(port, run)

    def board_of(self):
        """The project's board type, requirements.json's `board` (D35)."""
        return board_of(self.project)
