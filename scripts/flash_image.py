#!/usr/bin/env python3
"""
A flash image with MicroPython AND the project's files, for a headless simulation.

    flash_image.py --micropython sim/micropython-esp32s3.bin --files firmware -o sim/flash-with-firmware.bin
    flash_image.py ... --config '{"THRESHOLD_PCT": 40}'      # also writes /config.json into the image

Wokwi's CLI simulates a flash image, and MicroPython's download is only the interpreter. On real
hardware you copy your .py files over USB afterwards; a headless simulator has no afterwards, so
the files have to be in the image. MicroPython's ESP32 partition table ends after `factory` and
the rest of a 4 MB flash is the user filesystem, from 0x200000: this writes a littlefs image of
the files there and concatenates the two. The littlefs parameters are the ESP32 port's own; if
they are wrong the simulated board boots to a bare REPL with no main.py, which is the symptom.

Written for the smart bin (its tools/build-flash-image.py) and made general here for backlog
P31: any project, any file tree, the board's chip named on the command line by the image.
"""

import argparse
import json
import sys
from pathlib import Path

from outcomes import EXIT_OK, EXIT_COULD_NOT_RUN

FLASH_SIZE = 4 * 1024 * 1024
FILESYSTEM_OFFSET = 0x200000
BLOCK_SIZE = 4096
LITTLEFS_SETTINGS = dict(block_size=BLOCK_SIZE, read_size=32, prog_size=32, cache_size=4 * 32,
                         lookahead_size=32, block_cycles=100, disk_version=0x00020000)


def files_under(root):
    """Every file under the tree, as (path inside the image, bytes), sorted."""
    root = Path(root)
    return [("/" + str(path.relative_to(root)), path.read_bytes())
            for path in sorted(root.rglob("*")) if path.is_file() and "__pycache__" not in path.parts]


def filesystem(files, overrides=None):
    """A littlefs image holding the files (and /config.json from `overrides`), as bytes."""
    from littlefs import LittleFS  # imported here so --help works without it
    block_count = (FLASH_SIZE - FILESYSTEM_OFFSET) // BLOCK_SIZE
    fs = LittleFS(block_count=block_count, **LITTLEFS_SETTINGS)
    if overrides:
        files = list(files) + [("/config.json", json.dumps(overrides).encode())]
    for destination, content in files:
        parent = destination.rsplit("/", 1)[0]
        if parent and parent not in ("", "/"):
            try:
                fs.makedirs(parent, exist_ok=True)
            except (AttributeError, TypeError):
                fs.mkdir(parent)
        with fs.open(destination, "wb") as handle:
            handle.write(content)
    return bytes(fs.context.buffer)


def image(interpreter, files, overrides=None):
    """The whole flash: the interpreter at 0, the filesystem at FILESYSTEM_OFFSET, 0xff between."""
    if len(interpreter) > FILESYSTEM_OFFSET:
        raise ValueError("the MicroPython image is larger than %#x and would overwrite the filesystem" % FILESYSTEM_OFFSET)
    flash = bytearray(b"\xff" * FLASH_SIZE)
    flash[:len(interpreter)] = interpreter
    fs = filesystem(files, overrides)
    flash[FILESYSTEM_OFFSET:FILESYSTEM_OFFSET + len(fs)] = fs
    return bytes(flash)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="flash_image.py", description=__doc__.split("\n\n")[0])
    parser.add_argument("--micropython", required=True, type=Path, help="the interpreter .bin from micropython.org for the board's chip")
    parser.add_argument("--files", required=True, type=Path, help="the directory whose files go into the image, as they are")
    parser.add_argument("--config", help="JSON written as /config.json into the image")
    parser.add_argument("-o", "--output", required=True, type=Path)
    args = parser.parse_args(argv)
    if not args.micropython.is_file():
        print("flash_image.py: no interpreter at %s — download a build from micropython.org/download for the board's chip" % args.micropython, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    if not args.files.is_dir():
        print("flash_image.py: %s is not a directory" % args.files, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    files = files_under(args.files)
    try:
        flash = image(args.micropython.read_bytes(), files, json.loads(args.config) if args.config else None)
    except ValueError as broken:
        print("flash_image.py: %s" % broken, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    args.output.write_bytes(flash)
    for destination, content in files:
        print("  %-28s %6d bytes" % (destination, len(content)))
    print("wrote %s: %d KB (MicroPython to %#x, filesystem at %#x)" % (args.output, len(flash) // 1024, len(args.micropython.read_bytes()), FILESYSTEM_OFFSET))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
