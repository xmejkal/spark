"""P31: a flash image with MicroPython and the project's files, for the headless simulator."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import flash_image  # noqa: E402


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
        self.assertEqual(len(flash), flash_image.FLASH_SIZE)
        self.assertEqual(flash[:1], b"\xe9")
        fs = LittleFS(block_count=(flash_image.FLASH_SIZE - flash_image.FILESYSTEM_OFFSET) // flash_image.BLOCK_SIZE,
                      mount=False, **flash_image.LITTLEFS_SETTINGS)
        fs.context.buffer = bytearray(flash[flash_image.FILESYSTEM_OFFSET:])
        fs.mount()
        with fs.open("/main.py", "rb") as handle:
            self.assertEqual(handle.read(), b"print('hi')\n")
        with fs.open("/lib/rtc.py", "rb") as handle:
            self.assertEqual(handle.read(), b"x = 1\n")
        with fs.open("/config.json", "rb") as handle:
            self.assertEqual(json.loads(handle.read()), {"T": 40})

    def test_an_interpreter_too_large_for_its_slot_is_refused(self):
        with self.assertRaises(ValueError):
            flash_image.image(b"\x00" * (flash_image.FILESYSTEM_OFFSET + 1), [])

    def test_the_command_writes_the_image_and_names_what_went_in(self):
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = flash_image.main(["--micropython", str(self.root / "micropython.bin"), "--files", str(self.root / "fw"),
                                     "-o", str(self.root / "flash.bin")])
        self.assertEqual(code, 0, out.getvalue())
        self.assertEqual((self.root / "flash.bin").stat().st_size, flash_image.FLASH_SIZE)
        self.assertIn("/main.py", out.getvalue())

    def test_a_missing_interpreter_is_could_not_run_with_where_to_get_one(self):
        import contextlib
        import io
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = flash_image.main(["--micropython", str(self.root / "nope.bin"), "--files", str(self.root / "fw"), "-o", str(self.root / "f.bin")])
        self.assertEqual(code, 2)
        self.assertIn("micropython.org", err.getvalue())


if __name__ == "__main__":
    unittest.main()
