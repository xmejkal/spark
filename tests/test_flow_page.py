"""
The page of a project (P827, #1185): page.html shows each phase of the flow with a status word and a mark, and never a
tick for a phase that is not ok. The page is built from the phases a flow gives it, so ten fake phases give ten entries.
The card's own proof writes the page of a built project to disk, reads the file back and compares it with `flow.py show`.
It covers `flow_page`, `write_flow_page`, `show_flow.read_flow` and the keep step's flow page.

    python3 -m unittest tests.test_flow_page
"""

import contextlib
import html
import html.parser
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import flow  # noqa: E402
from fakes import FakeClock, FakeTscircuitExport  # noqa: E402
from spark.build import kept_files  # noqa: E402
from spark.build.build_record import BuildRecordStore, sha256_of  # noqa: E402
from spark.build.stages import Stage  # noqa: E402
from spark.core.outcomes import COULD_NOT_RUN, OK, SKIPPED  # noqa: E402
from spark.flow import flow_codes  # noqa: E402
from spark.flow.flow_page import FlowHtmlPage, FlowPage, Picture, TICK, shown_phase, word_of  # noqa: E402
from spark.flow.phase_readers import MARKS, Phase  # noqa: E402
from spark.flow.show_flow import read_flow  # noqa: E402
from spark.flow.write_flow_page import FlowPageStore, KeptFlowPage, WriteFlowPage, kept_pictures, write_page  # noqa: E402

#: The built fixture test_flow.py builds its projects from.
BUILT = ROOT / "tests" / "data" / "breadboard" / "button-light-xiao"
UNKNOWN_CODE = "a-new-code"


class FakeReader:
    """Fake: a PhaseReader that answers the Phase it was given, whatever the project is."""

    def __init__(self, phase):
        self.phase = phase

    def answer(self, project):
        return self.phase


class FakeStore:
    """Fake: stands in for FlowPageStore and keeps what it was asked to write."""

    def __init__(self):
        self.written = []

    def write(self, project, file_name, text):
        self.written.append((Path(project), file_name, text))
        return Path(project) / file_name


def a_phase(name, status=OK, mark=None, says=("said",), offers=()):
    """A Phase of `name`. Its mark is the flow's own for `status`, unless a test gives one that lies."""
    glyph = MARKS[status][1] if status in MARKS else "?"
    return Phase(name, status, mark or glyph, "you", list(says), list(offers))


def readers_of(*phases):
    return [FakeReader(phase) for phase in phases]


def page_of(*phases, project="project", pictures=()):
    """The text of the page of `phases`, through write_page and a fake store."""
    store = FakeStore()
    write_page(Path(tempfile.mkdtemp()) / project, readers_of(*phases), lambda _project: list(pictures), store=store)
    return store.written[0][2]


class Parsed(html.parser.HTMLParser):
    """The parts of a page the tests read: the rail's entries, the sections, the headings, the hrefs and ids, each element's
    text, and the marks (the spans whose text is a glyph)."""

    def __init__(self, text):
        super().__init__()
        self.rail, self.sections, self.levels, self.hrefs, self.ids, self.marks = [], [], [], [], [], []
        self.style, self.nav, self.legend = "", None, ""
        self._open = []  # the stack of (tag, attrs, [text])
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.ids += [attrs["id"]] if "id" in attrs else []
        self.hrefs += [attrs["href"]] if "href" in attrs else []
        self.levels += [int(tag[1])] if re.fullmatch(r"h[1-6]", tag) else []
        self.nav = attrs if tag == "nav" else self.nav
        self._open.append((tag, attrs, []))

    def handle_data(self, data):
        for _tag, _attrs, text in self._open:
            text.append(data)

    def handle_endtag(self, tag):
        opened, attrs, text = self._open.pop()
        said = "".join(text)
        if tag == "style":
            self.style = said
        elif tag == "li" and "data-phase" in attrs:
            self.rail.append((attrs, said))
        elif tag == "section" and attrs.get("class") == "phase":
            self.sections.append((attrs, said))
        elif tag == "section" and attrs.get("class") == "legend":
            self.legend = said
        elif tag == "span" and said in {glyph for _word, glyph in MARKS.values()}:
            self.marks.append((attrs, said))


class FlowOfNPhasesTest(unittest.TestCase):
    """The page has one entry and one section for each phase the flow gives it, in the flow's order, and no other."""

    def test_a_flow_of_ten_phases_gives_ten_rail_entries_and_ten_sections_in_order(self):
        names = list(flow_codes.PHASES) + ["bench-test"]
        parsed = Parsed(page_of(*[a_phase(name) for name in names]))
        self.assertEqual([attrs["data-phase"] for attrs, _ in parsed.rail], names)
        self.assertEqual([attrs["data-phase"] for attrs, _ in parsed.sections], names)

    def test_a_flow_of_one_phase_gives_one(self):
        parsed = Parsed(page_of(a_phase("only")))
        self.assertEqual(([attrs["data-phase"] for attrs, _ in parsed.rail], len(parsed.sections)), (["only"], 1))

    def test_the_page_holds_no_phase_name_the_flow_did_not_give(self):
        text = page_of(a_phase("alpha"), a_phase("beta")).lower()
        for name in flow_codes.PHASES:
            self.assertNotIn(name, text)

    def test_show_and_page_read_the_same_phases(self):
        phases = readers_of(a_phase("one", flow_codes.STALE), a_phase("two", None))
        shown, shown_at = read_flow("project", phases)
        written = write_page("project", phases, lambda _project: [], store=FakeStore())
        self.assertEqual([(phase.phase, phase.status) for phase in shown], [(phase["phase"], phase["status"]) for phase in written.phases])
        self.assertEqual(shown_at, written.stands_at)


class TheMarkTest(unittest.TestCase):
    """The mark and the word of a phase: the flow's own, and never a tick for a status that is not ok."""

    #: Every code the flow has but ok, one it does not know, and None.
    NOT_OK = [status for status in MARKS if status != OK] + [UNKNOWN_CODE]

    def test_no_status_but_ok_shows_the_tick(self):
        for status in self.NOT_OK:
            with self.subTest(status=status):
                parsed = Parsed(page_of(a_phase("liar", status, mark=TICK)))
                self.assertNotIn(TICK, parsed.rail[0][1])
                self.assertNotIn(TICK, parsed.sections[0][1])
                self.assertIn(MARKS[COULD_NOT_RUN][1], parsed.rail[0][1])

    def test_ok_shows_the_tick(self):
        parsed = Parsed(page_of(a_phase("fine", OK)))
        self.assertIn(TICK, parsed.rail[0][1])
        self.assertIn(TICK, parsed.sections[0][1])

    def test_the_word_of_each_status(self):
        self.assertEqual(word_of(OK), flow_codes.OK_WORD)
        self.assertEqual(word_of(None), flow_codes.NOT_CHECKED_WORD)
        self.assertEqual(word_of(UNKNOWN_CODE), UNKNOWN_CODE)
        for status, (word, _glyph) in MARKS.items():
            if status not in (OK, None):
                self.assertEqual(word_of(status), word)

    def test_a_phase_shows_its_word_beside_its_mark(self):
        for status in MARKS.keys() | {UNKNOWN_CODE}:
            with self.subTest(status=status):
                parsed = Parsed(page_of(a_phase("one", status)))
                for _attrs, said in (parsed.rail[0], parsed.sections[0]):
                    self.assertIn(word_of(status), said)
        self.assertEqual(shown_phase(a_phase("one", None).to_dict()).word, flow_codes.NOT_CHECKED_WORD)

    def test_every_mark_is_hidden_from_a_screen_reader(self):
        parsed = Parsed(page_of(*[a_phase("p%d" % number, status) for number, status in enumerate(MARKS)]))
        self.assertTrue(parsed.marks)
        for attrs, _said in parsed.marks:
            self.assertEqual(attrs.get("aria-hidden"), "true")

    def test_the_legend_lists_every_mark_with_its_word(self):
        legend = Parsed(page_of(a_phase("one"))).legend
        for status, (_word, glyph) in MARKS.items():
            self.assertIn("%s %s" % (glyph, word_of(status)), legend)
        self.assertIn(flow_codes.NOT_CHECKED_LEGEND, legend)

    def test_the_style_names_no_status_code(self):
        style = Parsed(page_of(a_phase("one"))).style
        self.assertTrue(style)
        for status in MARKS:
            if status is not None:
                self.assertIsNone(re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(status), style), status)
        self.assertNotIn("data-status", style)


class TheDocumentTest(unittest.TestCase):
    """What a reader, a screen reader and a browser need of the document."""

    def setUp(self):
        self.text = page_of(*[a_phase(name, status) for name, status in zip("abcdefg", list(MARKS))])
        self.parsed = Parsed(self.text)

    def test_one_h1_then_h2_and_no_level_is_skipped(self):
        self.assertEqual(self.parsed.levels[0], 1)
        self.assertEqual(set(self.parsed.levels[1:]), {2})

    def test_the_page_says_its_language(self):
        self.assertIn('<html lang="en">', self.text)

    def test_the_rail_is_a_named_nav(self):
        self.assertTrue(self.parsed.nav.get("aria-label"))

    def test_every_rail_link_points_to_an_id_that_exists(self):
        links = [href for href in self.parsed.hrefs if href.startswith("#")]
        self.assertEqual(len(links), 7)
        for href in links:
            self.assertIn(href[1:], self.parsed.ids)

    def test_each_section_s_data_status_is_the_flow_s_status(self):
        for (attrs, _said), status in zip(self.parsed.sections, MARKS):
            self.assertEqual(attrs["data-status"], "none" if status is None else status)
        for (rail, _), (section, _) in zip(self.parsed.rail, self.parsed.sections):
            self.assertEqual(rail["data-status"], section["data-status"])

    def test_the_page_runs_nothing_and_loads_nothing(self):
        for text in (self.text, page_of(a_phase("one"), pictures=[Picture("Breadboard", "<svg/>", None)])):
            self.assertNotIn("<script", text.lower())
            self.assertNotIn("<iframe", text.lower())
            self.assertNotIn("http", text.lower())

    def test_a_sentence_with_an_angle_bracket_is_escaped(self):
        text = page_of(a_phase("one", says=["<b>bold</b> & more"], offers=[flow_codes_offer("a<b", "<i>x</i>")]), project="<p>")
        self.assertNotIn("<b>", text)
        self.assertNotIn("<i>", text)
        self.assertIn("&lt;b&gt;bold&lt;/b&gt; &amp; more", text)
        self.assertIn("a&lt;b", text)

    def test_the_same_flow_gives_the_same_bytes(self):
        phases = [a_phase("one"), a_phase("two", None)]
        self.assertEqual(page_of(*phases), page_of(*phases))

    def test_an_offer_is_plain_text_with_no_button(self):
        text = page_of(a_phase("one", offers=[flow_codes_offer("build", "builds the board")]))
        self.assertIn("<code>build</code>: builds the board", text)
        self.assertNotIn("<button", text)

    def test_the_first_picture_comes_before_the_phases_and_the_rest_after(self):
        pictures = [Picture("Breadboard", "<svg/>", None), Picture("Schematic", None, "no tsci")]
        text = page_of(a_phase("one"), pictures=pictures)
        self.assertLess(text.index("<h2>Breadboard</h2>"), text.index('id="phase-one"'))
        self.assertLess(text.index('id="phase-one"'), text.index("<h2>Schematic</h2>"))
        self.assertIn("Not drawn, because no tsci.", text)


def flow_codes_offer(key, effect):
    from spark.flow.phase_readers import Offer
    return Offer(key, effect)


class TheBenchLineTest(unittest.TestCase):
    def test_the_bench_line_is_there_and_wired_and_flashed_appear_only_in_it(self):
        text = page_of(a_phase("deploy", flow_codes.NOT_STARTED))
        bench = html.escape(flow_codes.BENCH_NOTE)
        self.assertEqual(text.count(bench), 1)
        rest = text.replace(bench, "")
        for word in ("wired", "flashed", "none recorded"):
            self.assertNotIn(word, rest)

    def test_the_real_flow_of_a_project_adds_no_word_about_the_board(self):
        project = a_built_project()
        FlowPageStore().write(project, "page.html", FlowHtmlPage().text(
            FlowPage("t", [phase.to_dict() for phase in read_flow(project)[0]], None, [], [])))
        text = (project / "page.html").read_text()
        for word in ("wired", "flashed"):
            self.assertNotIn(word, text)


class TheMaskTest(unittest.TestCase):
    """No home path reaches page.html: the whole page is masked, a phase's sentence and a picture's reason too."""

    def test_no_home_path_reaches_the_page(self):
        home = Path(tempfile.mkdtemp()).resolve()
        project = Path(tempfile.mkdtemp()).resolve() / "project"
        sentence = "read %s/secret/notes" % home
        phase = a_phase("one", says=[sentence])
        picture = Picture("Breadboard", None, "no file in %s/drawings" % home)
        store = FakeStore()
        with mock.patch.dict("os.environ", {"HOME": str(home), "SPARK_HOME": str(home / "store")}):
            write_page(project, readers_of(phase), lambda _project: [picture], store=store)
        text = store.written[0][2]
        self.assertNotIn(str(home), text)
        self.assertIn("~/secret/notes", text)
        self.assertIn("~/drawings", text)
        # The test can fail: the same page, rendered without the mask, holds the home path.
        unmasked = FlowHtmlPage().text(FlowPage("t", [phase.to_dict()], None, [picture], []))
        self.assertIn(str(home), unmasked)


def a_built_project(status=OK, stage_status=OK):
    """A copy of the built fixture, with the record of a build that ended in `status`, every stage `stage_status`."""
    project = Path(tempfile.mkdtemp()) / "xiao"
    shutil.copytree(BUILT, project)
    (project / "breadboard.md").write_text("# the sheet\n")
    stages = [{"name": name, "status": stage_status} for name in ("board", "parts", "build", "simulation")]
    BuildRecordStore(project, clock=FakeClock()).write({"status": status, "stages": stages, "missing_facts": [],
                                                       "requirements": "requirements.json",
                                                       "requirements_sha256": sha256_of(project / "requirements.json")})
    return project


def run_flow(*argv):
    """`flow.py <argv>`: (the envelope, the exit code)."""
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
        code = flow.main(list(argv))
    return json.loads(out.getvalue()), code


class TheCommandTest(unittest.TestCase):
    def test_page_writes_the_file_and_answers_its_keys(self):
        project = a_built_project()
        envelope, code = run_flow("page", "--project", str(project), "--json")
        self.assertEqual((code, envelope["op"], envelope["status"]), (0, "write-flow-page", OK))
        self.assertEqual(sorted(envelope["data"]), ["did", "file", "phases", "stands_at"])
        self.assertEqual((envelope["data"]["file"], envelope["data"]["did"]), ("page.html", "wrote"))
        self.assertTrue((project / "page.html").is_file())
        for phase in envelope["data"]["phases"]:
            self.assertEqual(sorted(phase), ["phase", "status"])

    def test_a_folder_it_cannot_write_is_could_not_run_and_exit_2(self):
        not_a_folder = Path(tempfile.mkdtemp()) / "a-file"
        not_a_folder.write_text("x")
        envelope, code = run_flow("page", "--project", str(not_a_folder), "--json")
        self.assertEqual((code, envelope["status"]), (2, COULD_NOT_RUN))
        self.assertEqual([item["code"] for item in envelope["unchecked"]], [flow_codes.PAGE_NOT_WRITTEN])

    def test_a_page_that_a_store_refuses_is_one_could_not_run_finding(self):
        class Refusing:
            def write(self, project, file_name, text):
                raise PermissionError("read-only")
        result = WriteFlowPage(readers=readers_of(a_phase("one")), pictures=lambda _project: [], store=Refusing()).run(Path("."), outside=None)
        self.assertEqual([(finding.severity, finding.code) for finding in result.findings], [(COULD_NOT_RUN, flow_codes.PAGE_NOT_WRITTEN)])

    def test_a_phase_that_holds_problems_does_not_change_the_page_s_status(self):
        result = WriteFlowPage(readers=readers_of(a_phase("one", "problems")), pictures=lambda _project: [], store=FakeStore()).run(
            Path("."), outside=None)
        self.assertEqual(list(result.findings), [])

    def test_the_page_of_a_project_is_the_flow_s_phases_written_to_disk(self):
        # The card's proof: the file on disk, read back, shows each phase `flow.py show` gives, and no tick for a non-ok one.
        project = a_built_project(OK, SKIPPED)
        shown, _ = run_flow("show", "--project", str(project), "--json")
        run_flow("page", "--project", str(project), "--json")
        parsed = Parsed((project / "page.html").read_text(encoding="utf-8"))
        phases = shown["data"]["phases"]
        self.assertEqual([attrs["data-phase"] for attrs, _ in parsed.sections], [phase["phase"] for phase in phases])
        self.assertEqual([attrs["data-phase"] for attrs, _ in parsed.rail], [phase["phase"] for phase in phases])
        for phase, (attrs, said) in zip(phases, parsed.sections):
            self.assertEqual(attrs["data-status"], "none" if phase["status"] is None else phase["status"])
            self.assertEqual(TICK in said, phase["status"] == OK, phase["phase"])
        ok = [phase for phase in phases if phase["status"] == OK]
        self.assertEqual(sum(TICK in said for _attrs, said in parsed.rail), len(ok))
        self.assertEqual(sum(TICK in said for _attrs, said in parsed.sections), len(ok))

    def test_a_build_record_that_is_ok_with_every_stage_skipped_gets_a_tick_only_where_the_flow_says_ok(self):
        project = a_built_project(OK, SKIPPED)
        phases, _ = read_flow(project)
        parsed = Parsed(page_of_project(project))
        self.assertEqual(sum(TICK in said for _attrs, said in parsed.rail), sum(phase.status == OK for phase in phases))


def page_of_project(project):
    write_page(project, store=FlowPageStore())
    return (Path(project) / "page.html").read_text(encoding="utf-8")


class ThePicturesTest(unittest.TestCase):
    def test_the_breadboard_is_the_kept_drawing_and_the_other_two_say_how_to_get_them(self):
        project = Path(tempfile.mkdtemp())
        (project / "breadboard.svg").write_text("<svg/>")
        breadboard, schematic, pcb = kept_pictures(project)
        self.assertEqual((breadboard.title, breadboard.svg, breadboard.why_missing), ("Breadboard", "<svg/>", None))
        for picture in (schematic, pcb):
            self.assertEqual((picture.svg, picture.why_missing), (None, flow_codes.NOT_DRAWN_HERE))

    def test_a_breadboard_file_that_is_missing_is_not_drawn_and_says_why(self):
        breadboard = kept_pictures(Path(tempfile.mkdtemp()))[0]
        self.assertEqual((breadboard.svg, breadboard.why_missing), (None, flow_codes.NO_PICTURE_FILE % "breadboard.svg"))


class TheKeepStepTest(unittest.TestCase):
    """The keep step: in a project the page is the flow page with the three pictures the build drew, and it is written after
    the simulation folder is kept. In a folder that is no project, today's tabbed page stays."""

    def setUp(self):
        self.project = Path(tempfile.mkdtemp())
        self.picture = self.project / "breadboard.svg"
        self.picture.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        self.kept = [{"file": str(self.project / "dist"), "did": "wrote"}, {"file": str(self.picture), "did": "wrote", "why": "a picture"}]
        self.page = self.project / "page.html"

    def keep(self):
        return kept_files.keep_tabbed_page(self.project, [Stage("build", OK)], self.kept, FakeTscircuitExport(), KeptFlowPage())

    def test_in_a_project_the_page_is_the_flow_page_with_three_pictures(self):
        (self.project / ".spark").mkdir()
        entry = self.keep()
        self.assertEqual((entry["did"], entry["why"]), ("wrote", FlowHtmlPage.PURPOSE_MESSAGE))
        text = self.page.read_text()
        self.assertEqual(3, text.count("data:image/svg+xml;base64,"))
        self.assertEqual(len(Parsed(text).sections), 9)

    def test_in_a_folder_that_is_no_project_the_page_stays_the_tabbed_one(self):
        entry = self.keep()
        self.assertEqual(entry["did"], "wrote")
        self.assertIn('<div class="panel panel1">', self.page.read_text())
        self.assertEqual(Parsed(self.page.read_text()).sections, [])

    def test_the_page_is_written_after_the_simulation_folder_is_kept(self):
        (self.project / ".spark").mkdir()
        workdir = Path(tempfile.mkdtemp())
        (workdir / "sim").mkdir()
        (workdir / "sim" / "wokwi.toml").write_text("[wokwi]\nversion = 1\n")
        asked = kept_files.KeepAsked(str(self.project / "requirements.json"), self.project, None)
        (self.project / "requirements.json").write_text(json.dumps({"board": "x", "parts": []}))
        entries = kept_files.keep_all([Stage("build", OK)], workdir, asked, FakeTscircuitExport(), KeptFlowPage())
        files = [Path(entry["file"]).name for entry in entries]
        self.assertGreater(files.index("page.html"), files.index("sim"))


if __name__ == "__main__":
    unittest.main()
