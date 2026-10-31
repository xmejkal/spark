#!/usr/bin/env python3
"""
A flash image with MicroPython AND the project's files, for a headless simulation.

    flash_image.py --files firmware -o sim/flash-with-firmware.bin    # the build the project's board names
    flash_image.py --micropython sim/micropython-esp32s3.bin --files firmware -o sim/flash-with-firmware.bin
    flash_image.py ... --config '{"THRESHOLD_PCT": 40}'      # also writes /config.json into the image

Wokwi's CLI simulates a flash image, and MicroPython's download is only the interpreter. On real
hardware you copy your .py files over USB afterwards; a headless simulator has no afterwards, so
the files have to be in the image. MicroPython's ESP32 partition table ends after `factory` and
the rest of a 4 MB flash is the user filesystem, from 0x200000: this writes a littlefs image of
the files there and puts the interpreter where its tools list entry says it starts (`flash_offset`:
0x1000 on the original ESP32, 0x0 when the entry says nothing, P335), 0xff between. The littlefs parameters are the ESP32 port's own; if
they are wrong the simulated board boots to a bare REPL with no main.py, which is the symptom.

Written for the smart bin (its tools/build-flash-image.py) and made general here for backlog
P31: any project, any file tree. The board's record names its MicroPython build (`micropython_port`), and the tools
list's entry with that build is the interpreter (P229).
"""

import argparse
import hashlib
import json
import struct
import sys
from collections import namedtuple
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.core.outcomes import EXIT_OK, EXIT_COULD_NOT_RUN
import boards
import tools

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

# --- MVP ---
class PartitionTable(namedtuple("PartitionTable", "entries")):
    """
    Value: the partition table inside an interpreter, as (label, type, subtype, offset, size, flags) entries. The
    format is ESP-IDF's (v5.5.2, components/partition_table/gen_esp32part.py); the "vfs" label and its size are
    MicroPython's. MicroPython mounts the "vfs" partition, and only when the table holds none and no "ffat" does it
    register the rest of the physical flash as one, which on a 16 MB board is not the 2 MB spark wrote (P461).
    """
    TABLE_OFFSET = 0x8000   # where the bootloader reads the table in the flash
    SIZE = 0xC00            # the table's length: the entries, the MD5 entry and 0xff
    ENTRY = struct.Struct("<2sBBLL16sL")
    ENTRY_MAGIC = b"\xaa\x50"
    MD5_MAGIC = b"\xeb\xeb" + b"\xff" * 14
    FILESYSTEM = ("vfs", 0x01, 0x81, FILESYSTEM_OFFSET, FLASH_SIZE - FILESYSTEM_OFFSET, 0)   # data, fat

    @classmethod
    def read(cls, interpreter, offset):
        """The table in the interpreter that starts at `offset` in the flash. ValueError: no table, or not one spark can use."""
        start = cls.TABLE_OFFSET - offset
        if start < 0:
            raise ValueError("MicroPython at %#x starts past the partition table at %#x, so the image cannot say where its "
                             "file system is: use the build for the board's chip from micropython.org/download"
                             % (offset, cls.TABLE_OFFSET))
        table = interpreter[start:start + cls.SIZE]
        if len(table) < cls.SIZE:
            raise ValueError("MicroPython is %d bytes, too short to hold a partition table at %#x, so the image cannot say "
                             "where its file system is: use the build for the board's chip from micropython.org/download"
                             % (len(interpreter), cls.TABLE_OFFSET))
        entries = []
        for position in range(0, cls.SIZE, cls.ENTRY.size):
            chunk = table[position:position + cls.ENTRY.size]
            if chunk[:2] == cls.ENTRY_MAGIC:
                _, kind, subtype, where, size, label, flags = cls.ENTRY.unpack(chunk)
                entries.append((label.rstrip(b"\x00").decode(), kind, subtype, where, size, flags))
                continue
            if chunk[:16] == cls.MD5_MAGIC and chunk[16:] != hashlib.md5(table[:position]).digest():
                raise ValueError("the partition table's MD5 does not match its entries, so the interpreter is damaged: "
                                 "download the build again from micropython.org/download")
            break
        if not entries:
            raise ValueError("the MicroPython interpreter holds no partition table at %#x, so the image cannot say where its "
                             "file system is: use a build from micropython.org/download for the board's chip" % cls.TABLE_OFFSET)
        return cls(tuple(entries))

    def with_filesystem(self):
        """This table with the "vfs" entry that spark's file system fills. ValueError: a partition is in its way."""
        for entry in self.entries:
            label, where, size = entry[0], entry[3], entry[4]
            if label in ("vfs", "ffat") and entry != self.FILESYSTEM:
                raise ValueError('the partition table holds a "%s" entry other than the 2 MB "vfs" at %#x that spark writes: '
                                 "use the build for the board's chip from micropython.org/download" % (label, FILESYSTEM_OFFSET))
            if label != "vfs" and where + size > FILESYSTEM_OFFSET:
                raise ValueError('the partition "%s" ends at %#x, past %#x where the file system starts: use the build for '
                                 "the board's chip from micropython.org/download" % (label, where + size, FILESYSTEM_OFFSET))
        return PartitionTable(tuple(entry for entry in self.entries if entry != self.FILESYSTEM) + (self.FILESYSTEM,))

    def placed_in(self, interpreter, offset):
        """The interpreter's bytes with this table, and a new MD5 entry, in place of its own."""
        body = b"".join(self.ENTRY.pack(self.ENTRY_MAGIC, kind, subtype, where, size, label.encode(), flags)
                        for label, kind, subtype, where, size, flags in self.entries)
        table = (body + self.MD5_MAGIC + hashlib.md5(body).digest()).ljust(self.SIZE, b"\xff")
        start = self.TABLE_OFFSET - offset
        return interpreter[:start] + table + interpreter[start + self.SIZE:]
# --- end MVP ---


# --- MVP ---
def image(interpreter, files, overrides=None, offset=0):
    """The whole flash: the interpreter at `offset`, the filesystem at FILESYSTEM_OFFSET, 0xff between."""
    if offset + len(interpreter) > FILESYSTEM_OFFSET:
        raise ValueError("MicroPython at %#x is %d bytes and would pass %#x, where the filesystem starts"
                         % (offset, len(interpreter), FILESYSTEM_OFFSET))
    interpreter = PartitionTable.read(interpreter, offset).with_filesystem().placed_in(interpreter, offset)
    flash = bytearray(b"\xff" * FLASH_SIZE)
    flash[offset:offset + len(interpreter)] = interpreter
    fs = filesystem(files, overrides)
    flash[FILESYSTEM_OFFSET:FILESYSTEM_OFFSET + len(fs)] = fs
    return bytes(flash)


def board_build(project):
    """
    The MicroPython build the project's board names (its record's `micropython_port`), or None when the project names
    no board. A named board whose record cannot give its build is a ToolProblem, never the default build.
    """
    requirements = Path(project) / "requirements.json"
    if not requirements.is_file():
        return None
    try:
        board = json.loads(requirements.read_text()).get("board")
    except (OSError, ValueError, AttributeError) as cannot:
        raise tools.ToolProblem("%s cannot be read, so its board's MicroPython build is not known: %s", requirements, cannot)
    if not board:
        return None
    try:
        return boards.get(Path(project), "micropython_port", board)
    except boards.BoardError as cannot:
        first, *rest = str(cannot).split("\n")  # the problem's own lines stay lines; the board's name is a value
        raise tools.ToolProblem.of_lines(["the board %s names no MicroPython build that can be read: %s" % (board, first)] + rest)


def project_here():
    """The project this runs in: the nearest folder up with boards/active.json or .spark/, else the current folder."""
    try:
        return boards.project_root()
    except boards.BoardError:
        return Path(".")


class Interpreter(namedtuple("Interpreter", "path offset")):
    """Value: the MicroPython build chosen for a project, and where it starts in the flash (P335)."""

    def image(self, files, overrides=None):
        """The whole flash with this build at its offset."""
        return image(self.path.read_bytes(), files, overrides, self.offset)


def offset_of(entry):
    """Where an entry's build starts in the flash: its `flash_offset`, else 0. A broken one is a ToolProblem."""
    problem = tools.flash_offset_problem(entry)
    if problem:
        raise tools.ToolProblem("the MicroPython build's tools list entry is broken: %s", problem)
    return int(entry.get("flash_offset", "0"), 0)


def build_entry(project):
    """
    The build the project's board names and the tools list's (name, entry) that holds it: (None, None) with no
    board, (build, None) when no entry holds it.
    """
    build = board_build(project) if project else None
    if not build:
        return None, None
    for name, entry in tools.merged(project)["tools"].items():
        if entry.get("micropython_port") == build and "micropython-esp32-bin" in (entry.get("meets") or []):
            return build, (name, entry)
    return build, None


def interpreter_for(given, project=None, find_tool=None):
    """
    The MicroPython build and its offset: the file given, at the offset of the board's build (0 when no entry
    holds that build), else the tools list's download for the build the project's board names (P229), else the
    firmware-image role's (P82). A board whose build no tool holds is a ToolProblem, never another chip's build.
    `find_tool` (a name -> tools.Tool) finds the download; the project's tools list when None.
    """
    build, held = build_entry(project)
    find_tool = find_tool or (lambda name: tools.find(name, project))
    if given:
        return Interpreter(Path(given), offset_of(held[1]) if held else 0)
    if held:
        name, entry = held
        return Interpreter(Path(find_tool(name).command[0]), offset_of(entry))
    if build:
        raise tools.ToolProblem("no tool on the tools list holds the MicroPython build %s that the board names; add "
                                "one from https://micropython.org/download/%s/", build, build)
    found = find_tool("firmware-image")
    return Interpreter(Path(found.command[0]), offset_of(found.entry))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="flash_image.py", description=__doc__.split("\n\n")[0])
    parser.add_argument("--micropython", type=Path, help="the interpreter .bin from micropython.org for the board's chip; "
                        "omitted, the tools list's download for the build the project's board names. It starts where "
                        "that build's entry says (flash_offset, 0x1000 on the original ESP32), else at 0x0. A board whose record "
                        "names no build stops a given file too, since its start is not known")
    parser.add_argument("--project", type=Path,
                        help="the project whose requirements.json names the board (default: the nearest folder up from "
                        "here with boards/active.json or .spark/, else here); with no board, the tools list's "
                        "firmware-image download")
    parser.add_argument("--files", required=True, type=Path, help="the directory whose files go into the image, as they are")
    parser.add_argument("--config", help="JSON written as /config.json into the image")
    parser.add_argument("-o", "--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        tools.find("littlefs")
        interpreter = interpreter_for(args.micropython, args.project or project_here())
    except tools.ToolProblem as missing:
        print("flash_image.py: %s" % missing, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    if not interpreter.path.is_file():
        print("flash_image.py: no interpreter at %s — download a build from micropython.org/download for the board's chip" % interpreter.path, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    if not args.files.is_dir():
        print("flash_image.py: %s is not a directory" % args.files, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    files = files_under(args.files)
    try:
        micropython = interpreter.path.read_bytes()
        flash = image(micropython, files, json.loads(args.config) if args.config else None, interpreter.offset)
    except ValueError as broken:
        print("flash_image.py: %s" % broken, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    args.output.write_bytes(flash)
    for destination, content in files:
        print("  %-28s %6d bytes" % (destination, len(content)))
    print("wrote %s: %d KB (MicroPython at %#x-%#x, filesystem at %#x)"
          % (args.output, len(flash) // 1024, interpreter.offset, interpreter.offset + len(micropython), FILESYSTEM_OFFSET))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
