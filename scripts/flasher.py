"""
How a flash image goes onto a board (P239 PR 7): the seam that another platform's flasher plugs into.

`Flasher` is the base. `EsptoolFlasher` erases the whole flash with esptool and writes one image at 0x0, where the
simulator loaded it. Only the commands are built here: deploy.py runs them, and nothing here touches USB.
"""

import boards
import tools


def build_esptool_prefix(tool, port=None, chip=None):
    """The start of an esptool command line: the tool, then `--chip`, then `--port`, each when given. The order is the
    one deploy.py has always printed. `EsptoolFlasher` and board_look.EsptoolReader both begin their lines with it."""
    return tools.command_for(tool) + (["--chip", chip] if chip else []) + (["--port", port] if port else [])


class Flasher:
    """Strategy: how an image goes onto a board. A subclass supplies `build_commands` and may set `boot_hint` and the
    retry of its first command: `RETRY_EXIT_CODE`, `RETRY_WAIT_S` and `RETRY_LINE`."""

    #: What to try when the flasher cannot connect to the board. A sentence; empty when a flasher has none.
    boot_hint = ""
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
    #: esptool's commands with hyphens: esptool 5.0 is the first that knows them (esptool/__init__.py of esptool-5.0.0, sha256
    #: cee2259c868a91c99962b557b463398d024c3610ff721ac1058cb13144686ead), and 5.5.0 prints a deprecation line for the
    #: underscore names. The esptool entry's `oldest_version` makes the tools list refuse an older one.
    ERASE, WRITE = "erase-flash", "write-flash"
    #: How esptool restarts the chip after the write (P462). Its default, hard-reset, leaves a chip that was entered with the
    #: BOOT button in download mode (esptool troubleshooting, "Leaving Download Mode in USB-Serial/JTAG Mode"), as the
    #: FireBeetle 2 stayed in boot:0x23. The watchdog resets the whole system and samples the boot pin again on the S3
    #: (esptool-5.5.0 targets/esp32s3.py:337-345). The C6 and the classic ESP32 have no watchdog reset of their own and fall
    #: back to a hard reset (loader.py:2218-2223), as before. Run on the S3 only after a software entry, not after a BOOT
    #: entry: the bench started MicroPython after a watchdog reset at 23:29:16 (P472 bench.log).
    AFTER = ["--after", "watchdog-reset"]
    #: What to try when esptool cannot reach the board, with `%(boot)s`, `%(reset)s` and `%(orientation)s` from the
    #: ButtonPlaces. The sentence has no period: `orientation` brings its own, or nothing.
    BOOT_HINT_TEMPLATE = ("if esptool could not connect, hold the board's %(boot)s, press and release %(reset)s, "
                          "release BOOT, and run it again%(orientation)s")
    #: esptool 5.5.0 exits with 2 for every FatalError (esptool/__init__.py:1374), and a failed connect is one
    #: (esptool/loader.py:916). A second erase does what the first would have done. The wait is one bench observation:
    #: the PO's erase right after the look failed to connect, and the same command 5 s later connected (2026-10-18, P290).
    RETRY_EXIT_CODE = 2
    RETRY_WAIT_S = 5
    RETRY_LINE = "retry in %(wait)d s: %(command)s stopped with exit %(code)d (esptool's exit for any stop, a failed connect among them)"

    def __init__(self, tool, chip, places=boards.ButtonPlaces.EMPTY):
        self.tool, self.chip = tool, chip
        self.boot_hint = self.boot_hint_for(places)  # read by deploy.py through its plan's flasher

    @classmethod
    def boot_hint_for(cls, places):
        """The sentence to try when esptool cannot reach the board, naming the buttons as `places` (ButtonPlaces) does."""
        return cls.BOOT_HINT_TEMPLATE % {"boot": places.boot, "reset": places.reset, "orientation": places.orientation}

    def build_commands(self, image, port=None):
        base = build_esptool_prefix(self.tool, port, self.chip)
        return [base + [self.ERASE], base + self.AFTER + [self.WRITE, self.IMAGE_OFFSET, str(image)]]
