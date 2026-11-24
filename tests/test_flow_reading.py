"""
One reading feeds `flow.py show` and the page (P1060, #1558, D22 of the P1038 design): `show_flow.reading_of` reads the
flow once as a `FlowReading`, `flow.py show --json` prints it, and `write_flow_page.compose_page` draws the page from it
and reads no file. The first tests run both verbs on three projects and find every sentence and time of `show` on the
page; the PO reads their `-v` output. The others pin the route by construction and `data.artifact`.

    python3 -m unittest -v tests.test_flow_reading
"""

import ast
import contextlib
import html
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import flow  # noqa: E402
from golden_checks import FIXTURE  # noqa: E402
from test_flow import FlowTest, show, with_needs  # noqa: E402
from test_flow_page import without_script  # noqa: E402
from spark.breadboard.tabbed_page import page_title  # noqa: E402
from spark.core.operation import READS  # noqa: E402
from spark.flow.show_flow import ShowFlow, reading_of  # noqa: E402

#: A board log in the real layout (P1043), for the deploy of the button-light fixture (A16).
BOARD_LOG = ROOT / "tests" / "data" / "board_log" / "2026-11-23T14-09-49.log"
WRITE_FLOW_PAGE = ROOT / "scripts" / "spark" / "flow" / "write_flow_page.py"
#: The keys whose leaves the page does not show (the design's exemptions): the fingerprint is the page's data-fingerprint,
#: its first 12 hex digits only, and the Artifact's id is no fact of the project.
EXEMPT = ("data.fingerprint", "data.artifact")
#: The leaves the page says in other words, each by name with the reason (A7). `data.deploy.verdict` is the board log's
#: verdict word (`ready unknown`), which the deploy phase's sentence says in words: "nothing read back, start not seen".
SAID_IN_WORDS = {"data.deploy.verdict"}
#: A time as `zone_time.stamp` writes it: ISO 8601 to the second, with the zone.
STAMP = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d")
#: An Artifact id as `publish_files` answers it.
ARTIFACT = "0f1e2d3c-4b5a-6978-8a9b-0c1d2e3f4a5b"
#: What compose_page's body never calls: it reads no file.
FILE_CALLS = {"Path", "open", "read_text", "read_bytes", "stat", "is_file", "exists"}


def leaves(value, at="data"):
    """Each string leaf of `value` as (its JSON path, its text)."""
    if isinstance(value, dict):
        for key, item in value.items():
            yield from leaves(item, "%s.%s" % (at, key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from leaves(item, "%s[%d]" % (at, index))
    elif isinstance(value, str):
        yield at, value


def counted(data):
    """The leaves of `data` the page must show: a sentence or a title (it holds a space) or a time, out of EXEMPT."""
    return [(at, text) for at, text in leaves(data)
            if not at.startswith(EXEMPT) and at not in SAID_IN_WORDS and (" " in text or STAMP.fullmatch(text))]


def show_and_page(project, name):
    """(`flow.py show --project <name> --json`'s data, the page `flow.py page --project <name>` wrote), both through
    `flow.main`, so the real Privacy runs. `name` is how the project is named on the command line."""
    said, _code = show(name)
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        code = flow.main(["page", "--project", str(name)])
    assert code == 0, code
    return said["data"], (project / "page.html").read_text(encoding="utf-8")


def paths_in(value):
    """Each Path that `value` holds, however deep: in a namedtuple, a list, a tuple or a dict."""
    if isinstance(value, Path):
        return [value]
    if isinstance(value, dict):
        value = list(value.values())
    return [found for item in value for found in paths_in(item)] if isinstance(value, (list, tuple)) else []


class FromShowToThePageTest(FlowTest):
    """D22: every sentence, title and time of `flow.py show --json` stands in the page `flow.py page` writes, with the
    title of `data.name` and `data.stamp.newest` as data-written. A miss names its JSON path."""

    def assert_the_page_shows(self, project, name=None):
        data, page = show_and_page(project, name or project)
        text = html.unescape(without_script(page))
        missed = [at for at, said in counted(data) if said not in text]
        self.assertEqual(missed, [], "show's leaves the page does not show")
        self.assertEqual(data["name"], project.resolve().name)
        self.assertEqual(data["title"], page_title(data["name"]))  # A15: Claude takes the Artifact's title from show
        self.assertIn("<title>%s</title>" % data["title"], page)
        self.assertIn('data-written="%s"' % (data["stamp"]["newest"] or "none"), page)  # the page's word for no time
        return data

    def test_fixture_1_an_empty_project(self):
        project = Path(tempfile.mkdtemp()) / "plant-alarm"
        project.mkdir()
        data = self.assert_the_page_shows(project)
        self.assertIsNone(data["stamp"]["newest"])

    def test_fixture_2_the_button_light_project_of_the_golden_named_dot(self):
        # A4: `--project .` from the project's folder: the name is the folder's, so the title is not "spark circuit"
        project = Path(tempfile.mkdtemp()) / "button-light"
        shutil.copytree(FIXTURE, project)
        (project / "sim" / "runs" / "board").mkdir(parents=True)  # A16: a board log, so data.deploy is compared too
        shutil.copy(BOARD_LOG, project / "sim" / "runs" / "board")
        here = Path.cwd()
        os.chdir(project)
        self.addCleanup(os.chdir, here)
        data = self.assert_the_page_shows(project, ".")
        self.assertEqual(data["name"], "button-light")
        self.assertTrue(STAMP.fullmatch(data["stamp"]["newest"]), data["stamp"])
        self.assertTrue([at for at, _text in counted(data) if at.startswith("data.deploy")], "the fixture counts the deploy's leaves")  # row 4's catcher: the newest time is there

    def test_fixture_3_a_project_with_needs_and_a_pick(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-many"}]},
            {"id": "wet", "does": "sense", "what": "soil-moisture"}])
        data = self.assert_the_page_shows(project)
        self.assertTrue([at for at, _text in counted(data) if ".offers[" in at], "the fixture counts the offers' sentences")


class ByConstructionTest(unittest.TestCase):
    """D22 by construction: `compose_page` takes the reading and the parts only and reads no file, `write_flow_page`
    imports none of the flow's readers, and the reading holds no path."""

    def tree(self):
        return ast.parse(WRITE_FLOW_PAGE.read_text(encoding="utf-8"))

    def test_compose_page_takes_the_reading_and_the_parts_and_calls_no_file(self):
        compose = next(node for node in ast.walk(self.tree()) if isinstance(node, ast.FunctionDef) and node.name == "compose_page")
        self.assertEqual([arg.arg for arg in compose.args.args], ["reading", "parts"])
        called = {call.func.id if isinstance(call.func, ast.Name) else getattr(call.func, "attr", None)
                  for call in ast.walk(compose) if isinstance(call, ast.Call)}
        self.assertEqual(called & FILE_CALLS, set())

    def test_write_flow_page_imports_none_of_the_flow_s_readers(self):
        imported = {alias.name for node in ast.walk(self.tree()) if isinstance(node, ast.ImportFrom) for alias in node.names}
        self.assertEqual(imported & {"flow_and_guide", "phases_of", "fingerprint_of"}, set())

    def test_no_field_of_the_reading_holds_a_path(self):
        project = Path(tempfile.mkdtemp()) / "plant-alarm"
        project.mkdir()
        self.assertEqual(paths_in(tuple(reading_of(project))), [])


class ShowAnswersTheArtifactTest(FlowTest):
    """`flow.py show` answers the Artifact the page is published as, as `data.artifact`, and still writes nothing."""

    def project(self, held=None):
        project = Path(tempfile.mkdtemp()) / "plant-alarm"
        project.mkdir()
        if held is not None:
            (project / ".spark").mkdir()
            (project / ".spark" / "page.json").write_text(json.dumps({"artifact": held}))
        return project

    @staticmethod
    def files(project):
        return sorted((str(path.relative_to(project)), path.stat().st_mtime_ns) for path in project.rglob("*"))

    def test_a_kept_id_is_data_artifact_and_show_writes_nothing(self):
        project = self.project(ARTIFACT)
        before = self.files(project)
        self.assertEqual(show(project)[0]["data"]["artifact"], ARTIFACT)
        self.assertEqual(self.files(project), before)
        self.assertEqual(ShowFlow.effects, (READS,))

    def test_no_record_is_null(self):
        self.assertIsNone(show(self.project())[0]["data"]["artifact"])

    def test_an_id_that_is_no_artifact_id_is_null_not_the_raw_text(self):
        # A9: spark answers no id it cannot use
        self.assertIsNone(show(self.project("not-an-id\n"))[0]["data"]["artifact"])


if __name__ == "__main__":
    unittest.main()
