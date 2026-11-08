#!/usr/bin/env python3
"""
A flash image with MicroPython AND the project's files, for a headless simulation.

    flash_image.py --files firmware -o sim/flash-with-firmware.bin    # the build the project's board names
    flash_image.py --micropython sim/micropython-esp32s3.bin --files firmware -o sim/flash-with-firmware.bin
    flash_image.py ... --config '{"THRESHOLD_PCT": 40}'      # also writes /config.json into the image
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.core.outcomes import EXIT_OK, EXIT_COULD_NOT_RUN
import boards
from spark.firmware.image_builder import FILESYSTEM_OFFSET, make_image


def project_here():
    """The project this runs in: the nearest folder up with boards/active.json or .spark/, else the current folder."""
    try:
        return boards.project_root()
    except boards.BoardError:
        return Path(".")


#: What --micropython says in --help.
MICROPYTHON_HELP = ("the interpreter .bin from micropython.org for the board's chip; omitted, the tools list's download for "
                    "the build the project's board names. It starts where that build's entry says (flash_offset, 0x1000 on "
                    "the original ESP32), else at 0x0. A board whose record names no build stops a given file too, since its "
                    "start is not known. look.py --no-simulation rebuilds the image with the build in the tools list, not "
                    "with this file, so to use your own build, name it there")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="flash_image.py", description=__doc__.split("\n\n")[0])
    parser.add_argument("--micropython", type=Path, help=MICROPYTHON_HELP)
    parser.add_argument("--project", type=Path,
                        help="the project whose requirements.json names the board (default: the nearest folder up from "
                        "here with boards/active.json or .spark/, else here); with no board, the tools list's "
                        "firmware-image download")
    parser.add_argument("--files", required=True, type=Path, help="the directory whose files go into the image, as they are")
    parser.add_argument("--config", help="JSON written as /config.json into the image")
    parser.add_argument("-o", "--output", required=True, type=Path)
    args = parser.parse_args(argv)
    made, refusal = make_image(args.micropython, args.project or project_here(), args.files, args.config)
    if refusal:
        print("flash_image.py: %s" % refusal, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    interpreter, micropython, files, flash = made
    args.output.write_bytes(flash)
    for destination, content in files:
        print("  %-28s %6d bytes" % (destination, len(content)))
    print("wrote %s: %d KB (MicroPython at %#x-%#x, filesystem at %#x, the \"vfs\" partition of its table)"
          % (args.output, len(flash) // 1024, interpreter.offset, interpreter.offset + len(micropython), FILESYSTEM_OFFSET))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
