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

    def test_an_npm_tool_is_found_in_the_project_before_the_path(self):
        root = Path(tempfile.mkdtemp())
        (root / "node_modules" / ".bin").mkdir(parents=True)
        (root / "node_modules" / ".bin" / "tsci").write_text("#!/bin/sh\n")
        personal = layer({"tscircuit": {"kind": "npm", "exe": "tsci"}})
        with mock.patch.object(tools.shutil, "which", return_value="/global/tsci"):
            found = tools.find("tscircuit", root, personal)
        self.assertEqual(found.command, [str(root / "node_modules" / ".bin" / "tsci")])



class SparkSDefaultsHoldTogetherTest(unittest.TestCase):
    """The shipped data/tools.json, read as it is: every role names a tool that meets the role's contract."""

    def test_every_role_s_tool_exists_and_meets_its_contract(self):
        lists = tools.merged(None, Path(tempfile.mkdtemp()) / "absent.json")
        broken = [(role, name) for role, name in lists["roles"].items()
                  if name not in lists["tools"]
                  or (lists["contracts"].get(role) and lists["contracts"][role] not in (lists["tools"][name].get("meets") or []))]
        self.assertEqual(broken, [], "a role in spark's own defaults points at a tool that cannot do its job")

if __name__ == "__main__":
    unittest.main()
