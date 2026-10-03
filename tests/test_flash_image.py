"""P31: a flash image with MicroPython and the project's files, for the headless simulator."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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
            self.assertEqual(flash_image.interpreter_path(None), Path("/downloads/mp.bin"))
        self.assertEqual(asked.call_args[0][0], "firmware-image")

    def test_a_given_build_is_used_as_given(self):
        self.assertEqual(flash_image.interpreter_path(self.root / "micropython.bin"), self.root / "micropython.bin")

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
