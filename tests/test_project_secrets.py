"""P1060 (#1558): `ProjectSecrets` reads the values of a project's secrets files, which the page and `flow.py` mask. The
rule names a file directly in `firmware/` whose lower-case name matches `*secret*.py` (D3). The read parses the file
with `ast` and never imports it, takes values only (A3), and never raises (A2): a file it cannot read or parse is named,
and nothing of its text reaches the result."""

import sys
import tempfile
import unittest
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.core.privacy import MIN_SECRET  # noqa: E402
from spark.firmware.project_secrets import ProjectSecrets, is_secret_file  # noqa: E402

WIFI_PASSWORD = "wifi-password-1234"
TOKEN = "api-token-56789"
NESTED = "nested-network-pass"
LISTED = "listed-in-a-tuple-99"
DICT_KEY = "network_password_key"
DOCSTRING = "a docstring that is no secret"
SHORT = "seven77"
HALF_TYPED = "hunter2hunter2"
NUL_VALUE = "nul-byte-secret"


def project_with(files):
    """A project folder holding `files`, a map of relative name to text or bytes."""
    project = Path(tempfile.mkdtemp(prefix="spark-tests-secrets-"))
    for name, content in files.items():
        file = project / name
        file.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            file.write_bytes(content)
        else:
            file.write_text(content)
    return project


class TheRuleTest(unittest.TestCase):
    """D3: the files the rule names, and the files it does not."""

    def test_the_secrets_files_in_firmware_are_named_and_no_other(self):
        project = project_with({"firmware/wifi_secrets.py": 'WIFI = "%s"\n' % WIFI_PASSWORD,
                                "firmware/secrets.py": 'TOKEN = "%s"\n' % TOKEN,
                                "firmware/main.py": 'MAIN = "main-module-value"\n',
                                "secrets.py": 'TOP = "top-folder-value"\n',
                                "firmware/lib/x_secret.py": 'LIB = "nested-folder-value"\n'})
        self.assertEqual([file.name for file in ProjectSecrets.files(project)], ["secrets.py", "wifi_secrets.py"])
        reading = ProjectSecrets.read(project)
        self.assertEqual(sorted(reading.values), sorted([WIFI_PASSWORD, TOKEN]))
        self.assertEqual(reading.unreadable, ())

    def test_the_name_is_matched_in_lower_case(self):
        self.assertTrue(is_secret_file("WiFi_SECRETS.py"))
        self.assertFalse(is_secret_file("secrets.txt"))
        self.assertFalse(is_secret_file("main.py"))

    def test_a_project_with_no_firmware_folder_gives_no_values(self):
        reading = ProjectSecrets.read(project_with({"secrets.py": 'TOP = "%s"\n' % TOKEN}))
        self.assertEqual((reading.values, reading.unreadable), ((), ()))


class TheValuesTest(unittest.TestCase):
    """A3: values only, walked down: the right side of an assignment, dict values, list and tuple items."""

    def setUp(self):
        self.reading = ProjectSecrets.read(project_with({"firmware/wifi_secrets.py": '''"""%s"""
NETWORKS = {"%s": {"ssid": "home", "password": "%s"}}
OTHERS = [("guest", "%s")]
SHORT = "%s"
EMPTY = ""
'''  % (DOCSTRING, DICT_KEY, NESTED, LISTED, SHORT)}))

    def test_a_value_nested_in_a_dict_or_a_tuple_is_found(self):
        self.assertIn(NESTED, self.reading.values)
        self.assertIn(LISTED, self.reading.values)

    def test_a_dict_key_and_a_docstring_are_not_taken(self):
        self.assertGreaterEqual(len(DICT_KEY), MIN_SECRET)
        self.assertNotIn(DICT_KEY, self.reading.values)
        self.assertNotIn(DOCSTRING, self.reading.values)

    def test_a_value_shorter_than_min_secret_is_dropped(self):
        self.assertTrue(0 < len(SHORT) < MIN_SECRET)
        self.assertEqual(sorted(self.reading.values), sorted([NESTED, LISTED]))


class TheReadTest(unittest.TestCase):
    """The read never imports a file and never raises (A2)."""

    def test_the_file_is_never_imported(self):
        marker = Path(tempfile.mkdtemp(prefix="spark-tests-secrets-")) / "imported"
        project = project_with({"firmware/secrets.py": 'from pathlib import Path\nPath(%r).write_text("x")\nTOKEN = "%s"\n'
                                % (str(marker), TOKEN)})
        self.assertEqual(ProjectSecrets.read(project).values, (TOKEN,))
        self.assertFalse(marker.exists())

    def test_a_file_that_does_not_parse_is_named_and_shows_none_of_its_text(self):
        for name, content in (("half_typed_secret.py", 'PASSWORD = "%s\n' % HALF_TYPED),
                              ("nul_secret.py", b'TOKEN = "' + NUL_VALUE.encode() + b'"\x00\n')):
            with self.subTest(name=name):
                project = project_with({"firmware/" + name: content, "firmware/wifi_secrets.py": 'WIFI = "%s"\n' % WIFI_PASSWORD})
                reading = ProjectSecrets.read(project)
                self.assertEqual(reading.values, (WIFI_PASSWORD,))
                self.assertEqual(reading.unreadable, (name,))
                self.assertNotIn(HALF_TYPED, repr(reading))
                self.assertNotIn(NUL_VALUE, repr(reading))

    def test_the_parse_gives_no_warning_that_could_show_a_line(self):
        project = project_with({"firmware/secrets.py": 'TOKEN = "abc\\d-%s"\n' % TOKEN})
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            reading = ProjectSecrets.read(project)
        self.assertEqual([str(warning.message) for warning in caught], [])
        self.assertEqual(reading.values, ("abc\\d-" + TOKEN,))


if __name__ == "__main__":
    unittest.main()
