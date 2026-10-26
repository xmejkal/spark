"""P31: a flash image with MicroPython and the project's files, for the headless simulator."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import flash_image  # noqa: E402

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


def mounted(flash):
    """The image's filesystem, mounted the way MicroPython mounts it, where MicroPython looks."""
    from littlefs import LittleFS
    fs = LittleFS(block_count=(MICROPYTHON_FLASH_SIZE - MICROPYTHON_VFS_OFFSET) // 4096, mount=False, **MICROPYTHON_LITTLEFS)
    fs.context.buffer = bytearray(flash[MICROPYTHON_VFS_OFFSET:])
    fs.mount()
    return fs


class TheImageTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "fw" / "lib").mkdir(parents=True)
        (self.root / "fw" / "main.py").write_text("print('hi')\n")
        (self.root / "fw" / "lib" / "rtc.py").write_text("x = 1\n")
        (self.root / "micropython.bin").write_bytes(b"\xe9" + b"\x00" * 999)

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

    def test_the_original_esp32_s_interpreter_sits_at_0x1000_with_0xff_before_it(self):
        interpreter = (self.root / "micropython.bin").read_bytes()
        flash = flash_image.image(interpreter, flash_image.files_under(self.root / "fw"), offset=ESP32_INTERPRETER_OFFSET)
        self.assertEqual(len(flash), MICROPYTHON_FLASH_SIZE)
        self.assertEqual(flash[:ESP32_INTERPRETER_OFFSET], b"\xff" * ESP32_INTERPRETER_OFFSET)
        self.assertEqual(flash[ESP32_INTERPRETER_OFFSET:ESP32_INTERPRETER_OFFSET + len(interpreter)], interpreter)
        with mounted(flash).open("/main.py", "rb") as handle:
            self.assertEqual(handle.read(), b"print('hi')\n")

    def test_an_interpreter_that_ends_where_the_filesystem_starts_fits_and_one_byte_more_is_refused(self):
        fits = b"\xe9" * (MICROPYTHON_VFS_OFFSET - ESP32_INTERPRETER_OFFSET)
        self.assertEqual(len(flash_image.image(fits, [], offset=ESP32_INTERPRETER_OFFSET)), MICROPYTHON_FLASH_SIZE)
        with self.assertRaises(ValueError) as refused:
            flash_image.image(fits + b"\x00", [], offset=ESP32_INTERPRETER_OFFSET)
        self.assertIn("MicroPython at 0x1000 is %d bytes and would pass 0x200000" % (len(fits) + 1), str(refused.exception))

    def test_the_chosen_interpreter_builds_its_image_at_its_offset(self):
        chosen = flash_image.Interpreter(self.root / "micropython.bin", ESP32_INTERPRETER_OFFSET)
        flash = chosen.image(flash_image.files_under(self.root / "fw"), {"T": 40})
        self.assertEqual(flash[ESP32_INTERPRETER_OFFSET:ESP32_INTERPRETER_OFFSET + 1], b"\xe9")
        with mounted(flash).open("/config.json", "rb") as handle:
            self.assertEqual(json.loads(handle.read()), {"T": 40})

    def test_an_interpreter_too_large_for_its_slot_is_refused(self):
        with self.assertRaises(ValueError):
            flash_image.image(b"\x00" * (MICROPYTHON_VFS_OFFSET + 1), [])

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

    def test_a_missing_interpreter_is_could_not_run_with_where_to_get_one(self):
        import contextlib
        import io
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = flash_image.main(["--micropython", str(self.root / "nope.bin"), "--files", str(self.root / "fw"), "-o", str(self.root / "f.bin")])
        self.assertEqual(code, 2)
        self.assertIn("micropython.org", err.getvalue())



class TheInterpreterComesFromTheToolsListTest(unittest.TestCase):
    """P82: littlefs and the MicroPython build are tools on the list, not a traceback and a path to type."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "fw").mkdir()
        (self.root / "fw" / "main.py").write_text("print('hi')\n")
        (self.root / "micropython.bin").write_bytes(b"\xe9" + b"\x00" * 999)

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
        c6.write_bytes(b"\xe9C6" + b"\x00" * 997)
        s3.write_bytes(b"\xe9S3" + b"\x00" * 997)
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

    def test_the_command_takes_the_build_of_the_project_it_is_given(self):
        project = self.project_on("xiao-esp32-c6")
        self.assertEqual(self.image_from_main(project, ["--project", str(project)]), (0, b"\xe9C6"))

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

    def test_the_command_says_where_the_interpreter_starts_and_ends(self):
        import contextlib
        import io
        esp32 = ("ESP32_GENERIC", ("micropython-esp32", self.with_the_esp32()["tools"]["micropython-esp32"]))
        for held, span in ((esp32, "MicroPython at 0x1000-0x13e8"), (("ESP32_GENERIC_C3", None), "MicroPython at 0x0-0x3e8")):
            out = io.StringIO()
            with self.subTest(build=held[0]), mock.patch.object(flash_image, "build_entry", return_value=held), \
                    contextlib.redirect_stdout(out):
                code = flash_image.main(["--micropython", str(self.root / "micropython.bin"), "--project", str(self.root),
                                         "--files", str(self.root / "fw"), "-o", str(self.root / "out.bin")])
                self.assertEqual(code, flash_image.EXIT_OK)
                self.assertIn(span + ", filesystem at 0x200000", out.getvalue())

    def test_the_command_writes_the_original_esp32_s_interpreter_at_0x1000(self):
        import contextlib
        import io
        esp32 = ("ESP32_GENERIC", ("micropython-esp32", self.with_the_esp32()["tools"]["micropython-esp32"]))
        with mock.patch.object(flash_image, "build_entry", return_value=esp32), contextlib.redirect_stdout(io.StringIO()):
            code = flash_image.main(["--micropython", str(self.root / "micropython.bin"), "--project", str(self.root),
                                     "--files", str(self.root / "fw"), "-o", str(self.root / "out.bin")])
        self.assertEqual(code, flash_image.EXIT_OK)
        written, interpreter = (self.root / "out.bin").read_bytes(), (self.root / "micropython.bin").read_bytes()
        self.assertEqual(written[:ESP32_INTERPRETER_OFFSET], b"\xff" * ESP32_INTERPRETER_OFFSET)
        self.assertEqual(written[ESP32_INTERPRETER_OFFSET:ESP32_INTERPRETER_OFFSET + len(interpreter)], interpreter)

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

    def test_no_build_given_and_none_downloaded_says_how_to_get_it(self):
        code, said = self.run_main([], failing="firmware-image")
        self.assertEqual(code, flash_image.EXIT_COULD_NOT_RUN)
        self.assertIn("/spark:setup add micropython-esp32s3", said)

    def test_with_no_build_given_the_download_goes_into_the_image(self):
        import tools
        found = tools.Tool("micropython-esp32s3", "firmware-image", {}, [str(self.root / "micropython.bin")])
        real = tools.find
        with mock.patch.object(tools, "find", side_effect=lambda name, *rest: found if name == "firmware-image" else real(name, *rest)):
            code, said = self.run_main([], failing=None)
        self.assertEqual(code, flash_image.EXIT_OK, said)
        self.assertEqual((self.root / "out.bin").read_bytes()[:1000], (self.root / "micropython.bin").read_bytes())

if __name__ == "__main__":
    unittest.main()
