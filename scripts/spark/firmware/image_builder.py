"""
The flash image of MicroPython and a project's files, for a headless simulation (moved from flash_image.py, P685).

Wokwi's CLI simulates a flash image, and MicroPython's download is only the interpreter. On real
hardware you copy your .py files over USB afterwards; a headless simulator has no afterwards, so
the files have to be in the image. MicroPython's ESP32 partition table ends after `factory`, and
the file system is whatever follows it: this adds a 2 MB "vfs" entry at 0x200000 to the interpreter's table
(P461), so every flash size mounts the same 2 MB, and writes a littlefs image of the files there. It puts the
interpreter where its tools list entry says it starts (`flash_offset`:
0x1000 on the original ESP32, 0x0 when the entry says nothing, P335), 0xff between. The littlefs parameters are the ESP32 port's own; if
they are wrong the simulated board boots to a bare REPL with no main.py, which is the symptom.

Written for the smart bin (its tools/build-flash-image.py) and made general here for backlog
P31: any project, any file tree. The board's record names its MicroPython build (`micropython_port`), and the tools
list's entry with that build is the interpreter (P229).
"""

import hashlib
import json
import struct
from collections import namedtuple
from pathlib import Path

import boards
from spark.core.result import Refusal
from spark.firmware import firmware_codes
from spark.records import store
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
class InterpreterError(ValueError):
    """Error: the MicroPython build cannot make an image: it is damaged, too large, or not the build for the board's chip.
    The message is the whole sentence, and `code` names it (P684)."""
    code = firmware_codes.INTERPRETER_UNUSABLE


class PartitionTable(namedtuple("PartitionTable", "entries")):
    """
    Value: the partition table inside an interpreter, as (label, type, subtype, offset, size, flags) entries. The
    format is ESP-IDF's (v5.5.2, components/partition_table/gen_esp32part.py); the "vfs" label and its size are
    MicroPython's. MicroPython mounts the "vfs" partition, and only when the table holds none and no "ffat" does it
    register the rest of the physical flash as one, which on a 16 MB board is not the 2 MB spark wrote (P461).
    """
    TABLE_OFFSET = 0x8000   # where the bootloader reads the table in the flash
    TABLE_SIZE = 0xC00            # the table's length: the entries, the MD5 entry and 0xff
    ENTRY_FORMAT = struct.Struct("<2sBBLL16sL")
    ENTRY_MAGIC = b"\xaa\x50"
    MD5_MAGIC = b"\xeb\xeb" + b"\xff" * 14
    FILESYSTEM = ("vfs", 0x01, 0x81, FILESYSTEM_OFFSET, FLASH_SIZE - FILESYSTEM_OFFSET, 0)   # data, fat

    @classmethod
    def read(cls, interpreter, offset):
        """The table in the interpreter that starts at `offset` in the flash. InterpreterError: no table, or not one spark can use."""
        start = cls.TABLE_OFFSET - offset
        if start < 0:
            raise InterpreterError("MicroPython at %#x starts past the partition table at %#x, so the image cannot say where its "
                             "file system is: use the build for the board's chip from micropython.org/download"
                             % (offset, cls.TABLE_OFFSET))
        table = interpreter[start:start + cls.TABLE_SIZE]
        if len(table) < cls.TABLE_SIZE:
            raise InterpreterError("MicroPython is %d bytes, too short to hold a partition table at %#x, so the image cannot say "
                             "where its file system is: use the build for the board's chip from micropython.org/download"
                             % (len(interpreter), cls.TABLE_OFFSET))
        entries = []
        for position in range(0, cls.TABLE_SIZE, cls.ENTRY_FORMAT.size):
            chunk = table[position:position + cls.ENTRY_FORMAT.size]
            if chunk[:2] == cls.ENTRY_MAGIC:
                _, kind, subtype, where, size, label, flags = cls.ENTRY_FORMAT.unpack(chunk)
                try:
                    entries.append((label.rstrip(b"\x00").decode(), kind, subtype, where, size, flags))
                except UnicodeDecodeError:
                    raise InterpreterError("a partition label in the interpreter's table is not text, so the interpreter is damaged: "
                                     "download the build again from micropython.org/download")
                continue
            if chunk[:16] == cls.MD5_MAGIC and chunk[16:] != hashlib.md5(table[:position]).digest():
                raise InterpreterError("the partition table's MD5 does not match its entries, so the interpreter is damaged: "
                                 "download the build again from micropython.org/download")
            break
        if not entries:
            raise InterpreterError("the MicroPython interpreter holds no partition table at %#x, so the image cannot say where its "
                             "file system is: use a build from micropython.org/download for the board's chip" % cls.TABLE_OFFSET)
        return cls(tuple(entries))

    def with_filesystem(self):
        """This table with the "vfs" entry that spark's file system fills. InterpreterError: a partition is in its way."""
        for entry in self.entries:
            label, where, size = entry[0], entry[3], entry[4]
            if label in ("vfs", "ffat") and entry != self.FILESYSTEM:
                raise InterpreterError('the partition table holds a "%s" entry other than the 2 MB "vfs" at %#x that spark writes: '
                                 "use the build for the board's chip from micropython.org/download" % (label, FILESYSTEM_OFFSET))
            if label != "vfs" and where + size > FILESYSTEM_OFFSET:
                raise InterpreterError('the partition "%s" ends at %#x, past %#x where the file system starts: use the build for '
                                 "the board's chip from micropython.org/download" % (label, where + size, FILESYSTEM_OFFSET))
        entries = tuple(entry for entry in self.entries if entry != self.FILESYSTEM) + (self.FILESYSTEM,)
        if (len(entries) + 1) * self.ENTRY_FORMAT.size >= self.TABLE_SIZE:  # the MD5 entry too, and ESP-IDF refuses a full table
            raise InterpreterError("the partition table has no room for the vfs entry and an MD5 entry: use the build for the "
                             "board's chip from micropython.org/download")
        return PartitionTable(entries)

    def placed_in(self, interpreter, offset):
        """The interpreter's bytes with this table, and a new MD5 entry, in place of its own."""
        body = b"".join(self.ENTRY_FORMAT.pack(self.ENTRY_MAGIC, kind, subtype, where, size, label.encode(), flags)
                        for label, kind, subtype, where, size, flags in self.entries)
        table = (body + self.MD5_MAGIC + hashlib.md5(body).digest()).ljust(self.TABLE_SIZE, b"\xff")
        start = self.TABLE_OFFSET - offset
        return interpreter[:start] + table + interpreter[start + self.TABLE_SIZE:]
# --- end MVP ---


# --- MVP ---
def image(interpreter, files, overrides=None, offset=0):
    """The whole flash: the interpreter at `offset`, the filesystem at FILESYSTEM_OFFSET, 0xff between."""
    if offset + len(interpreter) > FILESYSTEM_OFFSET:
        raise InterpreterError("MicroPython at %#x is %d bytes and would pass %#x, where the filesystem starts"
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
        raise tools.ToolProblem("%s cannot be read, so its board's MicroPython build is not known: %s", requirements, cannot, code=firmware_codes.TOOL_MISSING)
    if not board:
        return None
    try:
        return boards.get(Path(project), "micropython_port", board)
    except boards.BoardError as cannot:
        first, *rest = str(cannot).split("\n")  # the problem's own lines stay lines; the board's name is a value
        raise tools.ToolProblem.of_lines(["the board %s names no MicroPython build that can be read: %s" % (board, first)] + rest, code=cannot.code)


class Interpreter(namedtuple("Interpreter", "path offset")):
    """Value: the MicroPython build chosen for a project, and where it starts in the flash (P335)."""

    def image(self, files, overrides=None):
        """The whole flash with this build at its offset."""
        return image(self.path.read_bytes(), files, overrides, self.offset)


def offset_of(entry):
    """Where an entry's build starts in the flash: its `flash_offset`, else 0. A broken one is a ToolProblem."""
    problem = tools.flash_offset_problem(entry)
    if problem:
        raise tools.ToolProblem("the MicroPython build's tools list entry is broken: %s", problem, code=firmware_codes.TOOL_MISSING)
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


#: The CLI a person runs to build the image, two folders up from this module (P685): the build command names it.
FLASH_IMAGE_SCRIPT = Path(__file__).resolve().parents[2] / "flash_image.py"
#: P463: how a person names their own MicroPython build in the project's tools list: the two tools.py lines, then the build again.
OWN_BUILD_HINT = "to use another MicroPython build, name it in this project's tools list: %s, then %s, then %s"
BUILD_AGAIN = "build the image again"


def build_command(project, image):
    """The line that builds the image of the project's firmware/ (P463): whole paths, quoted, led by the store, so it runs
    from any folder in a new terminal window."""
    project = Path(project).resolve()
    return store.format_rerun_line(FLASH_IMAGE_SCRIPT, ["--project", project, "--files", project / "firmware", "-o", Path(image).resolve()])


def own_build_hint_for(project, build, name, image=None):
    """
    How to name another MicroPython build for the board whose build is `build`, as a sentence; "" with no build. The
    lines are tools.py's, as a person runs them, then `image`'s build command (else the words to build again).
    `name` is the tools list's entry that holds the build: the new entry takes the same name, and the merge keeps its
    other fields. With no such entry (None), the new one is `<name>` and carries the build and the contract.
    """
    if not build:
        return ""
    entry = {"kind": "download", "file": "<file>", "url": "<url>", "sha256": "<sha256>"}
    if not name:
        entry.update(micropython_port=build, meets=["micropython-esp32-bin"])
    tools_py, where, name = Path(tools.__file__), ["--project", Path(project).resolve()], name or "<name>"
    return OWN_BUILD_HINT % (store.format_rerun_line(tools_py, where + ["--new", "%s=%s" % (name, json.dumps(entry))]),
                             store.format_rerun_line(tools_py, where + ["--install", name]),
                             build_command(project, image) if image else BUILD_AGAIN)


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
                                "one from https://micropython.org/download/%s/; or %s", build, build,
                                own_build_hint_for(project, build, None), code=firmware_codes.NO_INTERPRETER)
    found = find_tool("firmware-image")
    return Interpreter(Path(found.command[0]), offset_of(found.entry))


# --- MVP ---
def make_image(given, project, folder, config_text=None):
    """
    The image of the files under `folder`, with the MicroPython build `given` or the project's (P684): ((the
    interpreter, its bytes, the files, the flash), None), or (None, a Refusal) whose code names why not. `config_text`
    is the JSON written as /config.json. A bad --config is said before a bad build, as when one except caught both.
    """
    try:
        tools.find("littlefs", project)  # P457: a project's tools file that turns it off is named
        interpreter = interpreter_for(given, project)
    except tools.ToolProblem as missing:
        return None, Refusal(str(missing), firmware_codes.TOOL_MISSING)
    if not interpreter.path.is_file():
        return None, Refusal("no interpreter at %s — download a build from micropython.org/download for the board's chip"
                             % interpreter.path, firmware_codes.NO_INTERPRETER)
    if not Path(folder).is_dir():
        return None, Refusal("%s is not a directory" % folder, firmware_codes.FILES_NOT_FOLDER)
    files, micropython = files_under(folder), interpreter.path.read_bytes()
    try:
        config = json.loads(config_text) if config_text else None
    except ValueError as broken:
        return None, Refusal(str(broken), firmware_codes.CONFIG_NOT_JSON)
    try:
        return (interpreter, micropython, files, image(micropython, files, config, interpreter.offset)), None
    except ValueError as broken:  # an InterpreterError; another keeps its text and this code, as one except gave it
        return None, Refusal(str(broken), firmware_codes.INTERPRETER_UNUSABLE)
# --- end MVP ---

