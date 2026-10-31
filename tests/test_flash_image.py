"""P31: a flash image with MicroPython and the project's files, for the headless simulator."""

import hashlib
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit
from suite_runs import needs_littlefs  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import flash_image  # noqa: E402
from flat_message import NASTY, assert_flat  # noqa: E402
from micropython_fakes import MICROPYTHON_TABLE, fake_interpreter, table_bytes  # noqa: E402

#: MicroPython v1.29.0's own numbers for ESP32_GENERIC_S3, which the image has to match. Literals
#: from its source, never read back from `flash_image`: the test used the module's constants to
#: find the filesystem, so a wrong offset moved the module and the test together and nothing
#: noticed (P54). Each was read at the tag on 2026-10-01.
MICROPYTHON_FLASH_SIZE = 4 * 1024 * 1024   # ports/esp32/boards/sdkconfig.base: CONFIG_ESPTOOLPY_FLASHSIZE_4MB=y
MICROPYTHON_VFS_OFFSET = 0x200000          # ports/esp32/partitions-4MiBplus.csv: factory ends at 0x10000 + 0x1F0000; "The remaining flash is for the user filesystem(s)"
MICROPYTHON_LITTLEFS = dict(               # how MicroPython itself mounts that partition:
    block_size=4096,                       # ports/esp32/esp32_partition.c: NATIVE_BLOCK_SIZE_BYTES (4096)
    read_size=32, prog_size=32, lookahead_size=32,   # extmod/vfs_lfs.c: readsize/progsize/lookahead default 32
    cache_size=128, block_cycles=100)      # extmod/vfs_lfsx.c: MIN(block, 4 * MAX(read, prog)); block_cycles = 100
#: Where the original ESP32's interpreter starts (P335): micropython.org/download/ESP32_GENERIC/ says
#: "Then deploy the firmware to the board, starting at address 0x1000", read on 2026-10-26.
ESP32_INTERPRETER_OFFSET = 0x1000
#: P461: the partition table MicroPython finds its file system by. The format is ESP-IDF's, read at tag v5.5.2 (the
#: version string in the three v1.29.0 interpreters; ports/esp32/README.md:55 of MicroPython recommends it) on 2026-10-31.
BOOTLOADER_TABLE_OFFSET = 0x8000           # components/partition_table/Kconfig.projbuild:153-155 PARTITION_TABLE_OFFSET, default 0x8000
TABLE_SIZE = 0xC00                         # components/partition_table/gen_esp32part.py:22 MAX_PARTITION_LENGTH; esp_flash_partitions.h:63
ENTRY_SIZE = 32                            # gen_esp32part.py:607 STRUCT_FORMAT b'<2sBBLL16sL' (2+1+1+4+4+16+4)
ENTRY_MAGIC = b"\xaa\x50"                  # gen_esp32part.py:424 MAGIC_BYTES; esp_flash_partitions.h:16 ESP_PARTITION_MAGIC 0x50AA, little endian
MD5_MAGIC = b"\xeb\xeb"                    # gen_esp32part.py:23 MD5_PARTITION_BEGIN (then 14 x 0xff, then the digest); esp_flash_partitions.h:17
DATA_TYPE = 0x01                           # gen_esp32part.py:38 DATA_TYPE; esp_partition.h:52 ESP_PARTITION_TYPE_DATA
FAT_SUBTYPE = 0x81                         # gen_esp32part.py:87 'fat'; esp_partition.h:112 ESP_PARTITION_SUBTYPE_DATA_FAT
VFS_LABEL = b"vfs"                         # MicroPython ports/esp32/modules/flashbdev.py:4 Partition.find(TYPE_DATA, label="vfs")
#: The first 128 bytes of the table in ESP32_GENERIC_S3-20260824-v1.29.0.bin (sha256 1dd9dcd27ba2d6a1cb7f7b49a063f46d3d807d68b0151161233920228285e300),
#: read from flash offset 0x8000 on 2026-10-31: nvs, phy_init, factory, then the MD5 entry. The other two v1.29.0 builds hold the same bytes.
S3_TABLE = bytes.fromhex("aa50010200900000006000006e76730000000000000000000000000000000000aa50010100f00000001000007068795f696e6974000000000000000000000000aa5000000000010000001f00666163746f727900000000000000000000000000ebebffffffffffffffffffffffffffff8405a9bb5ce0b84c4f2ca5de9a76b050")
VFS_SIZE = 0x200000                        # the 2 MB spark's littlefs fills: 512 blocks of 4096
WRONG_BLOCK_COUNT = 3584                   # what MicroPython registers itself on a 16 MB flash: 14 MB / 4096 (main.c:255-275)


def table_of(flash, offset=0):
    """The image's partition table, read apart from the module: (label, type, subtype, offset, size) of each entry,
    and the MD5 entry's digest and the bytes it covers."""
    table = flash[BOOTLOADER_TABLE_OFFSET:BOOTLOADER_TABLE_OFFSET + TABLE_SIZE]
    entries, covered = [], 0
    while table[covered:covered + 2] == ENTRY_MAGIC:
        kind, subtype, start, size, label, _flags = struct.unpack("<BBLL16sL", table[covered + 2:covered + ENTRY_SIZE])
        entries.append((label.rstrip(b"\x00").decode(), kind, subtype, start, size))
        covered += ENTRY_SIZE
    digest = table[covered + 16:covered + 32] if table[covered:covered + 2] == MD5_MAGIC else None
    return entries, digest, table[:covered], table[covered:]


def mounted(flash, blocks=None):
    """The image's filesystem, mounted the way MicroPython mounts it, where MicroPython looks: `blocks` blocks
    (default, the image's own "vfs" partition)."""
    from littlefs import LittleFS
    if blocks is None:
        blocks = dict((label, size) for label, _, _, _, size in table_of(flash)[0])["vfs"] // 4096
    fs = LittleFS(block_count=blocks, mount=False, **MICROPYTHON_LITTLEFS)
    fs.context.buffer = bytearray(flash[MICROPYTHON_VFS_OFFSET:MICROPYTHON_VFS_OFFSET + blocks * 4096].ljust(blocks * 4096, b"\xff"))
    fs.mount()
    return fs


class TheImageTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "fw" / "lib").mkdir(parents=True)
        (self.root / "fw" / "main.py").write_text("print('hi')\n")
        (self.root / "fw" / "lib" / "rtc.py").write_text("x = 1\n")
        (self.root / "micropython.bin").write_bytes(fake_interpreter())

    @needs_littlefs
    def test_the_interpreter_sits_at_zero_and_the_files_at_the_filesystem_offset(self):
        from littlefs import LittleFS
        files = flash_image.files_under(self.root / "fw")
        self.assertEqual([name for name, _ in files], ["/lib/rtc.py", "/main.py"])
        flash = flash_image.image((self.root / "micropython.bin").read_bytes(), files, {"T": 40})
        self.assertEqual(len(flash), MICROPYTHON_FLASH_SIZE)
        self.assertEqual(flash[:1], b"\xe9")
        # Mounted the way MicroPython mounts it, where MicroPython looks — not where the module says.
        fs = LittleFS(block_count=(MICROPYTHON_FLASH_SIZE - MICROPYTHON_VFS_OFFSET) // 4096,
                      mount=False, **MICROPYTHON_LITTLEFS)
        fs.context.buffer = bytearray(flash[MICROPYTHON_VFS_OFFSET:])
        fs.mount()
        with fs.open("/main.py", "rb") as handle:
            self.assertEqual(handle.read(), b"print('hi')\n")
        with fs.open("/lib/rtc.py", "rb") as handle:
            self.assertEqual(handle.read(), b"x = 1\n")
        with fs.open("/config.json", "rb") as handle:
            self.assertEqual(json.loads(handle.read()), {"T": 40})

    @needs_littlefs
    def test_the_original_esp32_s_interpreter_sits_at_0x1000_with_0xff_before_it(self):
        interpreter = fake_interpreter(offset=ESP32_INTERPRETER_OFFSET)
        flash = flash_image.image(interpreter, flash_image.files_under(self.root / "fw"), offset=ESP32_INTERPRETER_OFFSET)
        self.assertEqual(len(flash), MICROPYTHON_FLASH_SIZE)
        self.assertEqual(flash[:ESP32_INTERPRETER_OFFSET], b"\xff" * ESP32_INTERPRETER_OFFSET)
        self.assertEqual(flash[ESP32_INTERPRETER_OFFSET:BOOTLOADER_TABLE_OFFSET], interpreter[:BOOTLOADER_TABLE_OFFSET - ESP32_INTERPRETER_OFFSET])
        with mounted(flash).open("/main.py", "rb") as handle:
            self.assertEqual(handle.read(), b"print('hi')\n")

    @needs_littlefs
    def test_an_interpreter_that_ends_where_the_filesystem_starts_fits_and_one_byte_more_is_refused(self):
        size = MICROPYTHON_VFS_OFFSET - ESP32_INTERPRETER_OFFSET
        fits = fake_interpreter(size=size, offset=ESP32_INTERPRETER_OFFSET)
        self.assertEqual(len(flash_image.image(fits, [], offset=ESP32_INTERPRETER_OFFSET)), MICROPYTHON_FLASH_SIZE)
        with self.assertRaises(ValueError) as refused:
            flash_image.image(fake_interpreter(size=size + 1, offset=ESP32_INTERPRETER_OFFSET), [], offset=ESP32_INTERPRETER_OFFSET)
        self.assertIn("MicroPython at 0x1000 is %d bytes and would pass 0x200000" % (size + 1), str(refused.exception))

    @needs_littlefs
    def test_the_chosen_interpreter_builds_its_image_at_its_offset(self):
        (self.root / "micropython.bin").write_bytes(fake_interpreter(offset=ESP32_INTERPRETER_OFFSET))
        chosen = flash_image.Interpreter(self.root / "micropython.bin", ESP32_INTERPRETER_OFFSET)
        flash = chosen.image(flash_image.files_under(self.root / "fw"), {"T": 40})
        self.assertEqual(flash[ESP32_INTERPRETER_OFFSET:ESP32_INTERPRETER_OFFSET + 1], b"\xe9")
        with mounted(flash).open("/config.json", "rb") as handle:
            self.assertEqual(json.loads(handle.read()), {"T": 40})

    def test_an_interpreter_too_large_for_its_slot_is_refused(self):
        with self.assertRaises(ValueError):
            flash_image.image(b"\x00" * (MICROPYTHON_VFS_OFFSET + 1), [])

    @needs_littlefs
    def test_the_command_writes_the_image_and_names_what_went_in(self):
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = flash_image.main(["--micropython", str(self.root / "micropython.bin"), "--files", str(self.root / "fw"),
                                     "-o", str(self.root / "flash.bin")])
        self.assertEqual(code, 0, out.getvalue())
        self.assertEqual((self.root / "flash.bin").stat().st_size, MICROPYTHON_FLASH_SIZE)
        self.assertIn("/main.py", out.getvalue())

    @needs_littlefs
    def test_a_missing_interpreter_is_could_not_run_with_where_to_get_one(self):
        import contextlib
        import io
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = flash_image.main(["--micropython", str(self.root / "nope.bin"), "--files", str(self.root / "fw"), "-o", str(self.root / "f.bin")])
        self.assertEqual(code, 2)
        self.assertIn("micropython.org", err.getvalue())


class TheImageHoldsAVfsPartitionTest(unittest.TestCase):
    """P461: the table in the image names the 2 MB file system spark wrote, so MicroPython does not register its own."""

    def setUp(self):
        self.files = [("/main.py", b"print('hi')\n")]

    def image_of(self, interpreter=None, offset=0):
        return flash_image.image(interpreter or fake_interpreter(offset=offset), self.files, offset=offset)

    def test_the_table_holds_the_vfs_the_littlefs_fills_and_the_entries_it_had(self):
        entries, _, _, _ = table_of(self.image_of())
        self.assertEqual(entries, [("nvs", 1, 2, 0x9000, 0x6000), ("phy_init", 1, 1, 0xf000, 0x1000),
                                   ("factory", 0, 0, 0x10000, 0x1f0000), ("vfs", DATA_TYPE, FAT_SUBTYPE, MICROPYTHON_VFS_OFFSET, VFS_SIZE)])

    def test_an_md5_entry_covers_every_entry_before_it_and_0xff_fills_the_rest(self):
        entries, digest, covered, rest = table_of(self.image_of())
        self.assertEqual(len(covered), len(entries) * ENTRY_SIZE)
        self.assertEqual(digest, hashlib.md5(covered).digest())
        self.assertEqual(rest[:16], MD5_MAGIC + b"\xff" * 14)
        self.assertEqual(rest[32:], b"\xff" * (TABLE_SIZE - len(covered) - 32))

    def test_the_table_is_found_at_0x8000_of_the_flash_and_every_byte_around_it_stays(self):
        for offset in (0, ESP32_INTERPRETER_OFFSET):
            with self.subTest(offset=offset):
                interpreter = fake_interpreter(head=b"\xe9ESP", offset=offset)
                flash = self.image_of(interpreter, offset=offset)
                self.assertEqual(table_of(flash)[0][-1], ("vfs", DATA_TYPE, FAT_SUBTYPE, MICROPYTHON_VFS_OFFSET, VFS_SIZE))
                start = BOOTLOADER_TABLE_OFFSET - offset
                self.assertEqual(flash[offset:BOOTLOADER_TABLE_OFFSET], interpreter[:start])
                self.assertEqual(flash[BOOTLOADER_TABLE_OFFSET + TABLE_SIZE:offset + len(interpreter)], interpreter[start + TABLE_SIZE:])

    def test_the_real_table_of_the_s3_interpreter_is_parsed_and_its_entries_stay_byte_for_byte(self):
        interpreter = fake_interpreter(table=S3_TABLE)
        self.assertEqual(flash_image.PartitionTable.read(interpreter, 0).entries,
                         (("nvs", 1, 2, 0x9000, 0x6000, 0), ("phy_init", 1, 1, 0xf000, 0x1000, 0), ("factory", 0, 0, 0x10000, 0x1f0000, 0)))
        flash = self.image_of(interpreter)
        self.assertEqual(flash[BOOTLOADER_TABLE_OFFSET:BOOTLOADER_TABLE_OFFSET + 3 * ENTRY_SIZE], S3_TABLE[:3 * ENTRY_SIZE])

    @needs_littlefs
    def test_the_littlefs_mounts_with_the_block_count_the_vfs_partition_gives(self):
        flash = self.image_of()
        self.assertEqual(VFS_SIZE // 4096, 512)
        with mounted(flash).open("/main.py", "rb") as handle:  # 512 blocks, read from the image's own table
            self.assertEqual(handle.read(), b"print('hi')\n")

    @needs_littlefs
    def test_the_same_bytes_refuse_to_mount_with_the_blocks_of_a_16_mb_flash(self):
        from littlefs.errors import LittleFSError
        with self.assertRaises(LittleFSError):
            mounted(self.image_of(), blocks=WRONG_BLOCK_COUNT)

    def test_a_table_with_no_md5_entry_is_read_and_gets_one(self):
        bare = fake_interpreter(table=table_bytes(md5=False))
        entries, digest, covered, _ = table_of(self.image_of(bare))
        self.assertEqual((len(entries), digest), (4, hashlib.md5(covered).digest()))

    def test_the_vfs_already_in_the_table_is_kept_once(self):
        vfs = ("vfs", DATA_TYPE, FAT_SUBTYPE, MICROPYTHON_VFS_OFFSET, VFS_SIZE)
        kept = fake_interpreter(table=table_bytes(MICROPYTHON_TABLE + (vfs,)))
        self.assertEqual(table_of(self.image_of(kept))[0], table_of(self.image_of())[0])

    def refused(self, interpreter, offset=0):
        with self.assertRaises(ValueError) as said:
            flash_image.image(interpreter, self.files, offset=offset)
        return str(said.exception)

    def test_an_offset_past_the_table_is_refused_where_a_negative_slice_would_give_wrong_bytes(self):
        for offset in (BOOTLOADER_TABLE_OFFSET + 1, 0x10000):  # a build of 0x20000 bytes: its last 0xC00 are a full, wrong table
            with self.subTest(offset=offset):
                self.assertIn("starts past the partition table", self.refused(fake_interpreter(size=0x20000), offset=offset))

    def test_an_interpreter_too_short_to_hold_the_table_is_refused_with_the_boundary_exact(self):
        size = BOOTLOADER_TABLE_OFFSET + TABLE_SIZE
        self.assertIn("partition table", self.refused(fake_interpreter(size=size - 1)))
        self.assertEqual(table_of(self.image_of(fake_interpreter(size=size)))[0][-1][0], "vfs")

    def test_no_table_magic_is_refused(self):
        self.assertIn("no partition table", self.refused(fake_interpreter(table=b"\xff" * TABLE_SIZE)))

    def test_a_broken_md5_is_refused(self):
        table = bytearray(table_bytes())
        table[3 * ENTRY_SIZE + 16] ^= 0x01
        self.assertIn("MD5", self.refused(fake_interpreter(table=bytes(table))))

    def test_a_partition_that_ends_past_where_the_filesystem_starts_is_refused_and_one_that_ends_there_is_not(self):
        past = MICROPYTHON_TABLE[:2] + (("factory", 0, 0, 0x10000, 0x1f0001),)
        self.assertIn("0x200000", self.refused(fake_interpreter(table=table_bytes(past))))
        self.assertEqual(table_of(self.image_of())[0][2], ("factory", 0, 0, 0x10000, 0x1f0000))  # ends at exactly 0x200000

    def test_an_ffat_inside_the_old_area_is_refused_for_being_an_ffat(self):
        ffat = ("ffat", DATA_TYPE, FAT_SUBTYPE, 0x1f0000, 0x1000)  # ends before 0x200000, so only its label is wrong
        self.assertIn('"ffat" entry', self.refused(fake_interpreter(table=table_bytes(MICROPYTHON_TABLE + (ffat,)))))

    def test_a_label_that_is_not_text_is_refused_with_what_to_do(self):
        table = bytearray(table_bytes())
        table[2 * ENTRY_SIZE + 12] = 0xff  # the first byte of the factory's label (entry offset 12)
        self.assertIn("micropython.org/download", self.refused(fake_interpreter(table=bytes(table))))

    def test_a_table_with_no_room_for_the_end_slot_is_refused_and_one_with_room_is_not(self):
        def table_of_(count):  # the table holds `count` entries before the vfs, all data partitions below 0x200000
            return table_bytes(tuple(("p%d" % index, DATA_TYPE, 2, 0x10000 + index * 0x1000, 0x1000) for index in range(count)))
        # 0xC00 / 32 = 96 slots: n entries and the MD5 entry fill n + 1, and ESP-IDF refuses 96 (gen_esp32part.py:412)
        self.assertEqual(len(table_of(self.image_of(fake_interpreter(table=table_of_(93))))[0]), 94)
        self.assertIn("room", self.refused(fake_interpreter(table=table_of_(94))))

    def test_a_different_vfs_is_refused(self):
        for other in (("vfs", DATA_TYPE, FAT_SUBTYPE, 0x300000, 0x100000), ("vfs", DATA_TYPE, FAT_SUBTYPE, MICROPYTHON_VFS_OFFSET, 0x100000),
                      ("vfs", DATA_TYPE, 0x82, MICROPYTHON_VFS_OFFSET, VFS_SIZE)):
            with self.subTest(other=other):
                self.assertIn(other[0], self.refused(fake_interpreter(table=table_bytes(MICROPYTHON_TABLE + (other,)))))

    def test_an_interpreter_too_large_is_refused_by_the_size_check_before_its_table_is_read(self):
        self.assertIn("would pass 0x200000", self.refused(b"\x00" * (MICROPYTHON_VFS_OFFSET + 1)))


class ANewlineInAValueGivesOneLineTest(unittest.TestCase):
    def test_a_newline_in_the_project_path_gives_one_line_in_a_requirements_file_that_cannot_be_read(self):
        project = Path(tempfile.mkdtemp()) / NASTY
        project.mkdir()
        (project / "requirements.json").write_text("{not json")
        with self.assertRaises(flash_image.tools.ToolProblem) as caught:
            flash_image.board_build(project)
        assert_flat(self, caught.exception)


class TheInterpreterComesFromTheToolsListTest(unittest.TestCase):
    """P82: littlefs and the MicroPython build are tools on the list, not a traceback and a path to type."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "fw").mkdir()
        (self.root / "fw" / "main.py").write_text("print('hi')\n")
        (self.root / "micropython.bin").write_bytes(fake_interpreter())

    def run_main(self, argv, failing):
        import contextlib
        import io
        import tools
        real = tools.find

        def find(name, project=None, personal=None):
            if name == failing:
                raise tools.ToolProblem({"littlefs": "littlefs (littlefs-python) is not installed — install: python3 -m pip install --user littlefs-python",
                                         "firmware-image": "firmware-image (micropython-esp32s3) is not installed — install: /spark:setup add micropython-esp32s3"}[name])
            return real(name, project, personal)
        err = io.StringIO()
        with mock.patch.object(tools, "find", side_effect=find), contextlib.redirect_stderr(err), \
                contextlib.redirect_stdout(io.StringIO()):
            code = flash_image.main(argv + ["--files", str(self.root / "fw"), "-o", str(self.root / "out.bin")])
        return code, err.getvalue()

    def test_without_micropython_the_list_s_download_is_used(self):
        import tools
        found = tools.Tool("micropython-esp32s3", "firmware-image", {}, ["/downloads/mp.bin"])
        with mock.patch.object(tools, "find", return_value=found) as asked:
            self.assertEqual(flash_image.interpreter_for(None), (Path("/downloads/mp.bin"), 0))
        self.assertEqual(asked.call_args[0][0], "firmware-image")

    def project_on(self, board):
        project = Path(tempfile.mkdtemp())
        (project / "requirements.json").write_text(json.dumps({"board": board}))
        return project

    def two_builds(self):
        """A tools list with the S3 and the XIAO C6 builds, each naming the build it holds (P229, D41)."""
        return {"tools": {"micropython-esp32s3": {"micropython_port": "ESP32_GENERIC_S3", "meets": ["micropython-esp32-bin"]},
                          "micropython-xiao-esp32c6": {"micropython_port": "SEEED_XIAO_ESP32C6", "meets": ["micropython-esp32-bin"]}},
                "roles": {"firmware-image": "micropython-esp32s3"}, "contracts": {}}

    def test_the_build_comes_from_the_project_s_board(self):
        import tools
        found = tools.Tool("micropython-xiao-esp32c6", None, {}, ["/downloads/c6.bin"])
        with mock.patch.object(tools, "merged", return_value=self.two_builds()), \
                mock.patch.object(tools, "find", return_value=found) as asked:
            self.assertEqual(flash_image.interpreter_for(None, self.project_on("xiao-esp32-c6")), (Path("/downloads/c6.bin"), 0))
        self.assertEqual(asked.call_args[0][0], "micropython-xiao-esp32c6")

    def test_a_board_whose_build_no_tool_holds_is_refused_by_name(self):
        import tools
        lists = self.two_builds()
        del lists["tools"]["micropython-xiao-esp32c6"]
        with mock.patch.object(tools, "merged", return_value=lists), self.assertRaises(tools.ToolProblem) as said:
            flash_image.interpreter_for(None, self.project_on("xiao-esp32-c6"))
        self.assertIn("SEEED_XIAO_ESP32C6", str(said.exception))

    def test_a_named_board_with_no_build_in_its_record_is_refused_not_given_the_default(self):
        import tools
        with mock.patch.object(tools, "merged", return_value=self.two_builds()), self.assertRaises(tools.ToolProblem) as said:
            flash_image.interpreter_for(None, self.project_on("no-such-board"))
        self.assertIn("no-such-board", str(said.exception))

    def test_the_build_s_tool_is_found_in_the_project_s_lists(self):
        import tools
        project = self.project_on("xiao-esp32-c6")
        found = tools.Tool("micropython-xiao-esp32c6", None, {}, ["/downloads/c6.bin"])
        with mock.patch.object(tools, "merged", return_value=self.two_builds()) as lists, \
                mock.patch.object(tools, "find", return_value=found) as asked:
            flash_image.interpreter_for(None, project)
        self.assertEqual(asked.call_args, mock.call("micropython-xiao-esp32c6", project))
        self.assertEqual(lists.call_args, mock.call(project))

    def test_an_entry_that_does_not_meet_the_contract_is_not_the_build(self):
        import tools
        lists = self.two_builds()
        lists["tools"] = {"a-stray": {"micropython_port": "SEEED_XIAO_ESP32C6"}, **lists["tools"]}
        found = tools.Tool("micropython-xiao-esp32c6", None, {}, ["/downloads/c6.bin"])
        with mock.patch.object(tools, "merged", return_value=lists), \
                mock.patch.object(tools, "find", return_value=found) as asked:
            flash_image.interpreter_for(None, self.project_on("xiao-esp32-c6"))
        self.assertEqual(asked.call_args[0][0], "micropython-xiao-esp32c6")

    def test_a_broken_requirements_file_is_refused_not_given_the_default(self):
        import tools
        project = Path(tempfile.mkdtemp())
        (project / "requirements.json").write_text("{not json")
        with self.assertRaises(tools.ToolProblem) as said:
            flash_image.interpreter_for(None, project)
        self.assertIn("requirements.json", str(said.exception))

    def image_from_main(self, project, argv, cwd=None):
        import contextlib
        import io
        import os
        import tools
        c6, s3 = self.root / "c6.bin", self.root / "s3.bin"
        c6.write_bytes(fake_interpreter(head=b"\xe9C6"))
        s3.write_bytes(fake_interpreter(head=b"\xe9S3"))
        real = tools.find
        builds = {"micropython-xiao-esp32c6": c6, "firmware-image": s3, "micropython-esp32s3": s3}

        def find(name, *rest, **kw):
            return tools.Tool(name, None, {}, [str(builds[name])]) if name in builds else real(name, *rest, **kw)
        here = os.getcwd()
        try:
            os.chdir(cwd or here)
            with mock.patch.object(tools, "find", side_effect=find), contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                code = flash_image.main(argv + ["--files", str(self.root / "fw"), "-o", str(self.root / "out.bin")])
        finally:
            os.chdir(here)
        return code, (self.root / "out.bin").read_bytes()[:3]

    @needs_littlefs
    def test_the_command_takes_the_build_of_the_project_it_is_given(self):
        project = self.project_on("xiao-esp32-c6")
        self.assertEqual(self.image_from_main(project, ["--project", str(project)]), (0, b"\xe9C6"))

    @needs_littlefs
    def test_the_command_finds_its_project_from_a_folder_inside_it(self):
        project = self.project_on("xiao-esp32-c6")
        (project / "boards").mkdir()
        (project / "boards" / "active.json").write_text(json.dumps({"board": "xiao-esp32-c6"}))
        (project / "firmware").mkdir()
        self.assertEqual(self.image_from_main(project, [], cwd=project / "firmware"), (0, b"\xe9C6"))

    def test_a_project_with_no_board_uses_the_firmware_image_role(self):
        import tools
        found = tools.Tool("micropython-esp32s3", "firmware-image", {}, ["/downloads/mp.bin"])
        with mock.patch.object(tools, "find", return_value=found) as asked:
            self.assertEqual(flash_image.interpreter_for(None, Path(tempfile.mkdtemp())), (Path("/downloads/mp.bin"), 0))
        self.assertEqual(asked.call_args[0][0], "firmware-image")

    def with_the_esp32(self):
        """The two builds and the original ESP32's, whose entry says where its interpreter starts (P335)."""
        lists = self.two_builds()
        lists["tools"]["micropython-esp32"] = {"micropython_port": "ESP32_GENERIC", "meets": ["micropython-esp32-bin"],
                                               "kind": "download", "flash_offset": "0x1000"}
        return lists

    def chosen_for(self, build, given=None, find=None):
        import tools
        found = tools.Tool("micropython-esp32", None, {}, ["/downloads/esp32.bin"])
        with mock.patch.object(flash_image, "board_build", return_value=build), \
                mock.patch.object(tools, "merged", return_value=self.with_the_esp32()), \
                mock.patch.object(tools, "find", side_effect=find or (lambda name, *rest: found)):
            return flash_image.interpreter_for(given, Path(tempfile.mkdtemp()))

    def test_an_esp32_board_s_build_starts_at_its_entry_s_offset(self):
        self.assertEqual(self.chosen_for("ESP32_GENERIC"), (Path("/downloads/esp32.bin"), ESP32_INTERPRETER_OFFSET))

    def test_an_s3_board_s_build_starts_at_0(self):
        self.assertEqual(self.chosen_for("ESP32_GENERIC_S3").offset, 0)

    def test_a_given_file_keeps_the_board_s_offset_while_its_download_is_not_in_the_store(self):
        import tools

        def not_installed(name, *rest):
            raise tools.ToolProblem("%s is not installed" % name)
        given = self.root / "micropython.bin"
        self.assertEqual(self.chosen_for("ESP32_GENERIC", given, not_installed), (given, ESP32_INTERPRETER_OFFSET))

    def test_a_given_file_for_a_board_whose_build_no_entry_holds_starts_at_0(self):
        given = self.root / "micropython.bin"
        self.assertEqual(self.chosen_for("ESP32_GENERIC_C3", given), (given, 0))

    def test_a_given_file_for_a_board_whose_record_names_no_build_is_refused(self):
        import tools
        with self.assertRaises(tools.ToolProblem) as said:
            flash_image.interpreter_for(self.root / "micropython.bin", self.project_on("no-such-board"))
        self.assertIn("no-such-board", str(said.exception))

    def test_a_given_file_with_a_broken_requirements_file_is_refused(self):
        import tools
        project = Path(tempfile.mkdtemp())
        (project / "requirements.json").write_text("{not json")
        with self.assertRaises(tools.ToolProblem) as said:
            flash_image.interpreter_for(self.root / "micropython.bin", project)
        self.assertIn("requirements.json", str(said.exception))

    def test_a_project_with_no_board_takes_the_role_entry_s_offset(self):
        import tools
        found = tools.Tool("micropython-esp32", "firmware-image", {"kind": "download", "flash_offset": "0x1000"},
                           ["/downloads/esp32.bin"])
        with mock.patch.object(tools, "find", return_value=found):
            self.assertEqual(flash_image.interpreter_for(None, Path(tempfile.mkdtemp())).offset, ESP32_INTERPRETER_OFFSET)

    def test_a_broken_flash_offset_is_a_tool_problem_on_every_path(self):
        import tools
        for broken in (4096, "-0x10", "zero"):
            with self.subTest(broken=broken):
                with self.assertRaises(tools.ToolProblem) as said:
                    flash_image.offset_of({"kind": "download", "flash_offset": broken})
                self.assertIn("flash_offset", str(said.exception))

    @needs_littlefs
    def test_the_command_says_could_not_run_for_a_broken_flash_offset(self):
        import contextlib
        import io
        import tools
        found = tools.Tool("micropython-esp32", "firmware-image", {"kind": "download", "flash_offset": "zero"},
                           [str(self.root / "micropython.bin")])
        real = tools.find
        err = io.StringIO()
        with mock.patch.object(tools, "find", side_effect=lambda name, *rest: found if name == "firmware-image" else real(name, *rest)), \
                contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            code = flash_image.main(["--project", str(Path(tempfile.mkdtemp())), "--files", str(self.root / "fw"),
                                     "-o", str(self.root / "out.bin")])
        self.assertEqual(code, flash_image.EXIT_COULD_NOT_RUN)
        self.assertIn("flash_offset", err.getvalue())

    @needs_littlefs
    def test_the_command_says_where_the_interpreter_starts_and_ends(self):
        import contextlib
        import io
        esp32 = ("ESP32_GENERIC", ("micropython-esp32", self.with_the_esp32()["tools"]["micropython-esp32"]))
        for held, span in ((esp32, "MicroPython at 0x1000-0xa000"), (("ESP32_GENERIC_C3", None), "MicroPython at 0x0-0x9000")):
            out = io.StringIO()
            (self.root / "micropython.bin").write_bytes(fake_interpreter(offset=0x1000 if held[1] else 0))
            with self.subTest(build=held[0]), mock.patch.object(flash_image, "build_entry", return_value=held), \
                    contextlib.redirect_stdout(out):
                code = flash_image.main(["--micropython", str(self.root / "micropython.bin"), "--project", str(self.root),
                                         "--files", str(self.root / "fw"), "-o", str(self.root / "out.bin")])
                self.assertEqual(code, flash_image.EXIT_OK)
                self.assertIn(span + ', filesystem at 0x200000, the "vfs" partition of its table)', out.getvalue())

    @needs_littlefs
    def test_the_command_writes_the_original_esp32_s_interpreter_at_0x1000(self):
        import contextlib
        import io
        esp32 = ("ESP32_GENERIC", ("micropython-esp32", self.with_the_esp32()["tools"]["micropython-esp32"]))
        (self.root / "micropython.bin").write_bytes(fake_interpreter(offset=ESP32_INTERPRETER_OFFSET))
        with mock.patch.object(flash_image, "build_entry", return_value=esp32), contextlib.redirect_stdout(io.StringIO()):
            code = flash_image.main(["--micropython", str(self.root / "micropython.bin"), "--project", str(self.root),
                                     "--files", str(self.root / "fw"), "-o", str(self.root / "out.bin")])
        self.assertEqual(code, flash_image.EXIT_OK)
        written, interpreter = (self.root / "out.bin").read_bytes(), (self.root / "micropython.bin").read_bytes()
        self.assertEqual(written[:ESP32_INTERPRETER_OFFSET], b"\xff" * ESP32_INTERPRETER_OFFSET)
        self.assertEqual(written[ESP32_INTERPRETER_OFFSET:BOOTLOADER_TABLE_OFFSET], interpreter[:BOOTLOADER_TABLE_OFFSET - ESP32_INTERPRETER_OFFSET])

    def test_the_shipped_list_holds_the_original_esp32_s_build_at_0x1000(self):
        import re
        import tools
        entry = tools.merged()["tools"]["micropython-esp32"]
        self.assertEqual((entry["micropython_port"], int(entry["flash_offset"], 0)), ("ESP32_GENERIC", ESP32_INTERPRETER_OFFSET))
        self.assertIsNone(tools.entry_problem(entry))
        self.assertRegex(entry["sha256"], re.compile(r"^[0-9a-f]{64}$"))

    def test_the_shipped_list_holds_a_build_for_each_shipped_board(self):
        import tools
        held = {entry.get("micropython_port") for entry in tools.merged()["tools"].values()}
        for record in sorted((ROOT / "boards").glob("*.json")):
            port = json.loads(record.read_text()).get("micropython_port")
            if port:
                self.assertIn(port, held, record.name)

    def test_a_given_build_is_used_as_given(self):
        self.assertEqual(flash_image.interpreter_for(self.root / "micropython.bin"), (self.root / "micropython.bin", 0))

    def test_no_littlefs_is_could_not_run_with_its_install(self):
        code, said = self.run_main(["--micropython", str(self.root / "micropython.bin")], failing="littlefs")
        self.assertEqual(code, flash_image.EXIT_COULD_NOT_RUN)
        self.assertIn("pip install --user littlefs-python", said)

    @needs_littlefs
    def test_no_build_given_and_none_downloaded_says_how_to_get_it(self):
        code, said = self.run_main([], failing="firmware-image")
        self.assertEqual(code, flash_image.EXIT_COULD_NOT_RUN)
        self.assertIn("/spark:setup add micropython-esp32s3", said)

    @needs_littlefs
    def test_with_no_build_given_the_download_goes_into_the_image(self):
        import tools
        found = tools.Tool("micropython-esp32s3", "firmware-image", {}, [str(self.root / "micropython.bin")])
        real = tools.find
        with mock.patch.object(tools, "find", side_effect=lambda name, *rest: found if name == "firmware-image" else real(name, *rest)):
            code, said = self.run_main([], failing=None)
        self.assertEqual(code, flash_image.EXIT_OK, said)
        self.assertEqual((self.root / "out.bin").read_bytes()[:BOOTLOADER_TABLE_OFFSET], (self.root / "micropython.bin").read_bytes()[:BOOTLOADER_TABLE_OFFSET])

if __name__ == "__main__":
    unittest.main()
