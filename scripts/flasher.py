"""
How a flash image goes onto a board (P239 PR 7): the seam that another platform's flasher plugs into.

`Flasher` is the base. `EsptoolFlasher` erases the whole flash with esptool and writes one image at 0x0, where the
simulator loaded it. Only the commands are built here: deploy.py runs them, and nothing here touches USB.
"""

import tools


def build_esptool_prefix(tool, port=None, chip=None):
    """The start of an esptool command line: the tool, then `--chip`, then `--port`, each when given. The order is the
    one deploy.py has always printed. `EsptoolFlasher` and board_look.EsptoolReader both begin their lines with it."""
    return tools.command_for(tool) + (["--chip", chip] if chip else []) + (["--port", port] if port else [])


class Flasher:
    """Strategy: how an image goes onto a board. A subclass supplies `build_commands` and may set `BOOT_HINT` and the
    retry of its first command: `RETRY_EXIT_CODE`, `RETRY_WAIT_S` and `RETRY_LINE`."""

    #: What to try when the flasher cannot connect to the board. A sentence; empty when a flasher has none.
    BOOT_HINT = ""
    #: The exit code on which the first command runs once more, after RETRY_WAIT_S seconds. None: never retry.
    RETRY_EXIT_CODE = None
    RETRY_WAIT_S = 0
    #: The line that names the retry, formatted with `wait`, `command` and `code`.
    RETRY_LINE = ""

    def build_commands(self, image, port=None):
        """The commands that put `image` on the board, in order, each an argv list. `port` is None when the tool finds the board."""
        raise NotImplementedError


class EsptoolFlasher(Flasher):
    """esptool: erase the whole flash, then write one image at IMAGE_OFFSET. `tool` is the tools.Tool for the `flasher`
    role, `chip` the chip as esptool names it."""

    #: Where the image goes: it is the whole flash from its first byte, as the simulator loaded it.
    IMAGE_OFFSET = "0x0"
    #: esptool's commands with underscores: esptool 3 and 4 know only these, and 5.x still accepts them with a deprecation
    #: line (esptool 5.5.0's cli_util.py, read 2026-10-12). The tools list finds any installed esptool, not only its pin.
    ERASE, WRITE = "erase_flash", "write_flash"
    #: What to try when esptool cannot reach the board. Read by the look, and by deploy.py through its plan's flasher.
    BOOT_HINT = ("if esptool could not connect, hold the board's BOOT button, press and release RESET, release BOOT, "
                 "and run it again")
    #: esptool 5.5.0 exits with 2 for every FatalError (esptool/__init__.py:1374), and a failed connect is one
    #: (esptool/loader.py:916). A second erase does what the first would have done. The wait is one bench observation:
    #: the PO's erase right after the look failed to connect, and the same command 5 s later connected (2026-10-18, P290).
    RETRY_EXIT_CODE = 2
    RETRY_WAIT_S = 5
    RETRY_LINE = "retry in %(wait)d s: %(command)s stopped with exit %(code)d (esptool's exit for any stop, a failed connect among them)"

    def __init__(self, tool, chip):
        self.tool, self.chip = tool, chip

    def build_commands(self, image, port=None):
        base = build_esptool_prefix(self.tool, port, self.chip)
        return [base + [self.ERASE], base + [self.WRITE, self.IMAGE_OFFSET, str(image)]]
