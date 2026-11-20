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
import os
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
from spark.breadboard.tabbed_page import SvgExportResult  # noqa: E402
from spark.build.stages import Stage  # noqa: E402
from spark.core.outcomes import COULD_NOT_RUN, OK, SKIPPED  # noqa: E402
from spark.breadboard import sheet  # noqa: E402
from spark.flow.flow_page import FlowHtmlPage, FlowPage, PageWiring, Picture, TICK, shown_phase, word_of  # noqa: E402
from spark.flow.phase_readers import MARKS, Offer, Phase  # noqa: E402
from spark.flow.show_flow import read_flow  # noqa: E402
from spark.flow.write_flow_page import FlowPageStore, PageParts, write_kept_page, WriteFlowPage, kept_pictures, kept_wiring, write_page  # noqa: E402

#: The built fixture test_flow.py builds its projects from.
BUILT = ROOT / "tests" / "data" / "breadboard" / "button-light-xiao"
#: The base64 of the synthetic JPEG in tests/data/pictures (P946): one colour, made by Pillow, no photo.
SYNTHETIC_JPEG = re.search(r'href="data:image/jpeg;base64,([^"]+)"',
                           (ROOT / "tests" / "data" / "pictures" / "epaper-synthetic.svg").read_text()).group(1)
UNKNOWN_CODE = "a-new-code"
#: The nine phases of a real flow, the words of the page and its codes, as the card says them: literals, not the code's own.
NINE = ["idea", "needs", "parts", "requirements", "build", "breadboard", "firmware", "simulate", "deploy"]
NOT_CHECKED = "not checked by spark"
BENCH = "This page reads the project's files. It does not know whether the board is wired or flashed."
NOT_WRITTEN = "page_not_written"
NOT_DRAWN_HERE = "Not drawn here. The build draws it: run /spark:build --keep."
NO_BREADBOARD_FILE = "Not drawn: breadboard.svg is not in the project yet. The build with --keep writes it."


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


def parts_of(pictures, wiring=None):
    """The swap point of write_page: a function that gives these pictures and this wiring, whatever the project."""
    return lambda _project: PageParts(pictures, wiring)


def readers_of(*phases):
    return [FakeReader(phase) for phase in phases]


def page_of(*phases, project="project", pictures=()):
    """The text of the page of `phases`, through write_page and a fake store."""
    store = FakeStore()
    write_page(Path(tempfile.mkdtemp()) / project, readers_of(*phases), parts_of(list(pictures)), store=store)
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
        names = NINE + ["bench-test"]
        parsed = Parsed(page_of(*[a_phase(name) for name in names]))
        self.assertEqual([attrs["data-phase"] for attrs, _ in parsed.rail], names)
        self.assertEqual([attrs["data-phase"] for attrs, _ in parsed.sections], names)

    def test_a_flow_of_one_phase_gives_one(self):
        parsed = Parsed(page_of(a_phase("only")))
        self.assertEqual(([attrs["data-phase"] for attrs, _ in parsed.rail], len(parsed.sections)), (["only"], 1))

    def test_the_page_holds_no_phase_name_the_flow_did_not_give(self):
        text = page_of(a_phase("alpha"), a_phase("beta")).lower()
        for name in NINE:
            self.assertNotIn(name, text)

    def test_show_and_page_read_the_same_phases(self):
        phases = readers_of(a_phase("one", "stale"), a_phase("two", None))
        shown, shown_at = read_flow("project", phases)
        written = write_page("project", phases, parts_of([]), store=FakeStore())
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
        self.assertEqual(word_of(OK), "ok")
        self.assertEqual(word_of(None), NOT_CHECKED)
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
        self.assertEqual(shown_phase(a_phase("one", None).to_dict()).word, NOT_CHECKED)

    def test_every_mark_is_hidden_from_a_screen_reader(self):
        parsed = Parsed(page_of(*[a_phase("p%d" % number, status) for number, status in enumerate(MARKS)]))
        self.assertTrue(parsed.marks)
        for attrs, _said in parsed.marks:
            self.assertEqual(attrs.get("aria-hidden"), "true")

    def test_the_legend_lists_every_mark_with_its_word(self):
        legend = Parsed(page_of(a_phase("one"))).legend
        for status, (_word, glyph) in MARKS.items():
            self.assertIn("%s %s" % (glyph, word_of(status)), legend)
        self.assertIn("does not judge this phase", legend)

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
        text = page_of(a_phase("one", says=["<b>bold</b> & more"], offers=[Offer("a<b", "<i>x</i>")]), project="<p>")
        self.assertNotIn("<b>", text)
        self.assertNotIn("<i>", text)
        self.assertIn("&lt;b&gt;bold&lt;/b&gt; &amp; more", text)
        self.assertIn("a&lt;b", text)

    def test_the_same_flow_gives_the_same_bytes(self):
        phases = [a_phase("one"), a_phase("two", None)]
        self.assertEqual(page_of(*phases), page_of(*phases))

    def test_an_offer_is_plain_text_with_no_button(self):
        text = page_of(a_phase("one", offers=[Offer("build", "builds the board")]))
        self.assertIn("<code>build</code>: builds the board", text)
        self.assertNotIn("<button", text)

    def test_the_pictures_stand_together_after_the_phases_and_before_the_legend_with_a_link_in_the_rail(self):
        pictures = [Picture("Breadboard", "<svg/>", None), Picture("Schematic", None, "Not drawn, because no tsci.")]
        text = page_of(a_phase("one"), pictures=pictures)
        self.assertEqual(text.count('<section id="pictures">'), 1)
        order = [text.index(mark) for mark in ('id="phase-one"', '<section id="pictures">', "<h3>Breadboard</h3>", "<h3>Schematic</h3>",
                                                '<section class="legend">')]
        self.assertEqual(order, sorted(order))
        self.assertIn("Not drawn, because no tsci.", text)
        parsed = Parsed(text)
        self.assertIn("#pictures", parsed.hrefs)
        self.assertEqual(len(parsed.rail), 1)
        self.assertLess(text.index('</ol><a href="#pictures">Pictures</a></nav>'), text.index('id="phase-one"'))

    def test_a_page_with_no_pictures_has_no_pictures_section_and_no_link(self):
        text = page_of(a_phase("one"))
        self.assertNotIn("pictures", text)


class TheBenchLineTest(unittest.TestCase):
    def test_the_bench_line_is_there_and_wired_and_flashed_appear_only_in_it(self):
        text = page_of(a_phase("deploy", "not-started"))
        bench = html.escape(BENCH)
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
        with mock.patch.dict(os.environ, {"HOME": str(home), "SPARK_HOME": str(home / "store")}):
            write_page(project, readers_of(phase), parts_of([picture]), store=store)
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
        self.assertEqual([item["code"] for item in envelope["unchecked"]], [NOT_WRITTEN])

    def test_a_page_that_cannot_be_written_says_why_in_text_mode_too(self):
        project = Path(tempfile.mkdtemp())
        (project / "page.html").mkdir()
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
            code = flow.main(["page", "--project", str(project)])
        self.assertEqual(code, 2)
        self.assertIn("page.html was not written", out.getvalue() + err.getvalue())

    def test_a_page_that_a_store_refuses_is_one_could_not_run_finding(self):
        class Refusing:
            def write(self, project, file_name, text):
                raise PermissionError("read-only")
        result = WriteFlowPage(readers=readers_of(a_phase("one")), parts=parts_of([]), store=Refusing()).run(Path("."), outside=None)
        self.assertEqual([(finding.severity, finding.code) for finding in result.findings], [(COULD_NOT_RUN, NOT_WRITTEN)])

    def test_page_on_a_record_whose_stages_is_no_list_writes_the_page_with_the_sentence(self):
        project = a_built_project()
        (project / ".spark" / "build.json").write_text('{"status": "ok", "stages": 5}')
        envelope, code = run_flow("page", "--project", str(project), "--json")
        self.assertEqual((code, envelope["data"]["did"]), (0, "wrote"))
        self.assertEqual({phase["phase"]: phase["status"] for phase in envelope["data"]["phases"]}["build"], COULD_NOT_RUN)
        self.assertIn("is no build record", (project / "page.html").read_text(encoding="utf-8"))

    def test_a_record_with_a_lone_surrogate_is_a_page_that_cannot_be_written_and_no_traceback(self):
        project = a_built_project()
        (project / ".spark" / "build.json").write_text('{"status": "ok", "at": "\\ud800"}')
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
            code = flow.main(["page", "--project", str(project)])
        self.assertEqual(code, 2)
        self.assertNotIn("Traceback", out.getvalue() + err.getvalue())
        self.assertIn("page.html was not written", out.getvalue() + err.getvalue())

    def test_a_phase_that_holds_problems_does_not_change_the_page_s_status(self):
        result = WriteFlowPage(readers=readers_of(a_phase("one", "problems")), parts=parts_of([]), store=FakeStore()).run(
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
            self.assertEqual((picture.svg, picture.why_missing), (None, NOT_DRAWN_HERE))

    @unittest.skipIf(os.geteuid() == 0, "root reads any file")
    def test_a_breadboard_file_that_cannot_be_read_says_so(self):
        project = Path(tempfile.mkdtemp())
        picture = project / "breadboard.svg"
        picture.write_text("<svg/>")
        picture.chmod(0)
        self.addCleanup(picture.chmod, 0o644)
        breadboard = kept_pictures(project)[0]
        self.assertIsNone(breadboard.svg)
        self.assertIn("cannot be read", breadboard.why_missing)

    def test_a_breadboard_file_that_is_missing_is_not_drawn_and_says_why(self):
        breadboard = kept_pictures(Path(tempfile.mkdtemp()))[0]
        self.assertEqual((breadboard.svg, breadboard.why_missing), (None, NO_BREADBOARD_FILE))


class ParsedWiring(html.parser.HTMLParser):
    """The wiring section of a page: its headings, the before-power lines (the `<li>`s outside the steps), the steps (each
    `<li>` of `<ol id="steps">`: its attributes, its words and its nav line) and every link and control in it."""

    def __init__(self, text):
        super().__init__()
        self.headings, self.before, self.steps, self.links, self.controls = [], [], [], [], []
        self.ordered_lists = 0
        self._stack, self._step = [], None
        start = text.find('<section id="wiring">')
        self.present = start >= 0
        self.feed(text[start:text.index("</section>", start) + len("</section>")] if self.present else "")

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.ordered_lists += tag == "ol"
        if tag == "a":
            self.links.append((attrs.get("href"), attrs.get("aria-label")))
        if tag in ("button", "input", "script"):
            self.controls.append(tag)
        if tag == "li" and ("ol", "steps") in self._stack:
            self._step = {"attrs": attrs, "words": [], "nav": []}
            self.steps.append(self._step)
        if tag == "li" and self._step is None:
            self.before.append("")
        self._stack.append((tag, attrs.get("id") if tag == "ol" else attrs.get("class")))

    def handle_data(self, data):
        if self._step is not None:
            self._step["nav" if ("div", "nav") in self._stack else "words"].append(data)
            return
        heading = [tag for tag, _mark in self._stack if tag in ("h2", "h3")]
        if heading:
            self.headings.append((heading[-1], data))
        elif ("ul", None) in self._stack and ("li", None) in self._stack:
            self.before[-1] += data

    def handle_endtag(self, tag):
        self._step = None if tag == "li" else self._step
        self._stack.pop()


def page_of_wiring(wiring, pictures=()):
    """The text of a page whose wiring is `wiring`, on one fake phase."""
    store = FakeStore()
    write_page(Path(tempfile.mkdtemp()) / "project", readers_of(a_phase("one")), parts_of(list(pictures), wiring), store=store)
    return store.written[0][2]


def wiring_page(steps, before=(), records=(), why=None, pictures=()):
    return page_of_wiring(PageWiring(list(steps), list(before), list(records), why), pictures)


def an_item(kind="conflict", **fields):
    """A before-power item as the page holds it, a plain dict."""
    return dict({"kind": kind, "subject": "PartA", "pin": "P1", "record": "rec", "said": "keep it low", "users": ()}, **fields)


THREE = [(1, "Put the board in."), (2, "Run a jumper from A to B."), (3, "Run a jumper from C to D.")]
THREE_PICTURES = [Picture(title, "<svg/>", None) for title in ("Breadboard", "Schematic", "PCB")]


def a_project_with_circuit(circuit_text=None, requirements_edit=None):
    """A built project copy; its circuit.json replaced by `circuit_text`, its requirements changed by `requirements_edit`."""
    project = a_built_project()
    if circuit_text is not None:
        (project / "dist" / "board" / "circuit.json").write_text(circuit_text)
    if requirements_edit is not None:
        requirements = json.loads((project / "requirements.json").read_text())
        requirements_edit(requirements)
        (project / "requirements.json").write_text(json.dumps(requirements))
    return project


def wiring_text_of(project):
    """The page of `project` as write_page writes it, in a scratch store, read back."""
    with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
        return page_of_project(project)


def wiring_section(text):
    """The wiring section of a page, tags and all."""
    return text.split('<section id="wiring">')[1].split("</section>")[0]


class TheWiringTest(unittest.TestCase):
    """The wiring section (P828, #1186): the lines before power, then the steps, as a page of the built fixture shows them."""

    @classmethod
    def setUpClass(cls):
        cls.project = a_built_project()
        cls.text = wiring_text_of(cls.project)
        cls.parsed = ParsedWiring(cls.text)
        with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
            cls.data = sheet.wiring_data(cls.project / "requirements.json")

    def test_the_page_shows_exactly_the_steps_the_data_holds_in_order(self):
        self.assertTrue(self.data.steps)
        self.assertEqual([(int(step["attrs"]["value"]), "".join(step["words"])) for step in self.parsed.steps],
                         [(step.number, step.words) for step in self.data.steps])

    def test_the_before_power_heading_and_lines_come_before_the_first_step(self):
        self.assertIn(("h3", "Before you power it"), self.parsed.headings)
        self.assertEqual(len(self.parsed.before), len(self.data.before_power.items))
        self.assertTrue(self.data.before_power.items)
        first = self.text.index('id="step-1"')
        self.assertLess(self.text.index("<h3>Before you power it</h3>"), first)
        self.assertLess(self.text.index("</ul>"), first)

    def test_every_step_has_an_id_of_its_number_and_no_before_power_line_is_among_them(self):
        self.assertEqual([step["attrs"]["id"] for step in self.parsed.steps], ["step-%d" % step.number for step in self.data.steps])
        steps = self.text.split('<ol id="steps">')[1].split("</ol>")[0]
        self.assertEqual(steps.count("<li "), len(self.data.steps))
        self.assertNotIn("<li>", steps)
        self.assertNotIn("Before you power it", steps)

    def test_the_section_stands_between_the_last_phase_and_the_pictures_with_a_link_in_the_rail(self):
        text = page_of_wiring(PageWiring(THREE, [], [], None), THREE_PICTURES)
        order = [text.index(mark) for mark in ('id="phase-one"', '<section id="wiring">', '<section id="pictures">')]
        self.assertEqual(order, sorted(order))
        self.assertIn('</ol><a href="#wiring">Wiring</a> <a href="#pictures">Pictures</a></nav>', text)
        self.assertEqual(len(Parsed(text).rail), 1)

    def test_the_section_holds_its_heading_the_fixed_sentence_the_lines_the_link_and_the_steps_in_that_order(self):
        text = page_of_wiring(PageWiring(THREE, [an_item()], ["rec"], None), THREE_PICTURES)
        marks = ["<h2>Wiring</h2>", "<p>Read the lines before power first. In the Breadboard picture below, each jumper has its "
                 "step&#x27;s number and the color of what it carries: find the holes there.</p>",
                 "<h3>Before you power it</h3>", "<ul>", "</ul>",
                 "Each record whole", "One at a time: start at step 1", '<ol id="steps">']
        order = [text.index(mark) for mark in marks]
        self.assertEqual(order, sorted(order))

    def test_the_picture_sentence_and_the_picture_links_need_a_drawn_breadboard(self):
        undrawn = [Picture("Breadboard", None, "Not drawn"), Picture("Schematic", "<svg/>", None)]
        for pictures, drawn in ((THREE_PICTURES, True), (undrawn, False), ([], False)):
            with self.subTest(drawn=drawn, pictures=len(pictures)):
                text = wiring_page(THREE, pictures=pictures)
                section = wiring_section(text)
                self.assertEqual("Breadboard picture below" in section, drawn)
                self.assertEqual(">Picture</a>" in section, drawn)
                self.assertIn("<p>Read the lines before power first.", section)
                self.assertNotIn("Breadboard picture" if not drawn else "colour", section)

    def test_a_project_with_no_requirements_has_no_wiring_section_and_no_link(self):
        text = wiring_text_of(Path(tempfile.mkdtemp()))
        self.assertNotIn('id="wiring"', text)
        self.assertNotIn('href="#wiring"', text)

    def test_zero_one_and_many_steps_give_a_valid_page(self):
        for steps in ([], THREE[:1], THREE):
            with self.subTest(steps=len(steps)):
                text = wiring_page(steps, [an_item()], ["rec"])
                parsed = ParsedWiring(text)
                self.assertEqual((len(parsed.steps), parsed.ordered_lists), (len(steps), 1 if steps else 0))
                self.assertNotIn('<ol id="steps"></ol>', text)
                self.assertEqual(len(Parsed(text).ids), len(set(Parsed(text).ids)))
                for number, step in enumerate(parsed.steps, 1):
                    self.assertEqual((step["attrs"]["value"], step["attrs"]["id"]), (str(number), "step-%d" % number))
                    self.assertIn("Step %d of %d" % (number, len(steps)), "".join(step["nav"]))
                labels = [label for _href, label in parsed.links if label]
                self.assertEqual(sum(label.startswith("Back") for label in labels), max(len(steps) - 1, 0))
                self.assertEqual(sum(label.startswith("Next") for label in labels), max(len(steps) - 1, 0))

    def test_the_first_step_has_no_back_and_the_last_no_next_and_next_points_to_the_next_number(self):
        parsed = ParsedWiring(wiring_page(THREE))
        self.assertEqual([(href, label) for href, label in parsed.links if label],
                         [("#step-2", "Next: step 2"), ("#step-1", "Back to step 1"), ("#step-3", "Next: step 3"),
                          ("#step-2", "Back to step 2")])

    def test_every_link_of_the_section_points_to_an_id_that_exists_and_each_control_is_a_link(self):
        for pictures in ([], THREE_PICTURES):
            with self.subTest(pictures=len(pictures)):
                text = wiring_page(THREE, [an_item()], ["rec"], pictures=pictures)
                parsed = ParsedWiring(text)
                for href, _label in parsed.links:
                    self.assertTrue(href.startswith("#"), href)
                    self.assertIn(href[1:], Parsed(text).ids)
                self.assertEqual(parsed.controls, [])
                self.assertEqual("#pictures" in [href for href, _label in parsed.links], bool(pictures))

    def test_the_style_hides_other_steps_only_inside_the_steps_list(self):
        style = Parsed(wiring_page(THREE)).style
        self.assertIn("#steps:has(>li:target)>li:not(:target){display:none}", style)
        self.assertIn("#steps>li:target .nav{display:block}", style)
        hiding = re.findall(r"([^{}@]+)\{[^{}]*display:none[^{}]*\}", style)
        self.assertTrue(hiding)
        for selector in hiding:
            self.assertTrue(selector.startswith("#steps"), selector)

    def test_the_print_rule_shows_every_step_and_hides_the_nav_lines(self):
        style = Parsed(wiring_page(THREE)).style
        self.assertIn("@media print{#steps>li{display:list-item!important}#steps .nav{display:none!important}}", style)

    def test_a_page_with_no_wiring_has_none_of_its_style(self):
        self.assertNotIn("#steps", Parsed(page_of(a_phase("one"))).style)


class TheMissingWiringTest(unittest.TestCase):
    """No steps to show: the section says why, in the refusal's words, with no list and no home path."""

    def says_why(self, project, *words):
        text = wiring_text_of(project)
        parsed = ParsedWiring(text)
        self.assertTrue(parsed.present)
        self.assertEqual((parsed.steps, parsed.before, parsed.ordered_lists), ([], [], 0))
        said = wiring_section(text)
        for word in ("<ul>", "<ol", "<li"):
            self.assertNotIn(word, said)
        for word in words:
            self.assertIn(word, said)
        return text

    def test_a_project_with_no_build_shows_no_steps_and_says_why(self):
        project = a_built_project()
        shutil.rmtree(project / "dist")
        self.says_why(project, "nothing is built", "yet")

    def test_requirements_changed_after_the_build_shows_no_steps_and_says_why(self):
        project = a_project_with_circuit(requirements_edit=lambda requirements: requirements.update(note="changed"))
        self.says_why(project, "other requirements")

    def test_a_circuit_json_that_is_malformed_never_stops_the_page(self):
        for broken in ('[{"type": "source_component", "ftype": "simple_chip"}]', '[{"type": 5}]', "{}", "not json"):
            with self.subTest(circuit=broken):
                text = self.says_why(a_project_with_circuit(broken))
                self.assertIn('id="phase-build"', text)

    def test_a_reason_that_is_not_the_sheet_s_is_one_fixed_sentence(self):
        sentence = "The wiring could not be read from the build&#x27;s files. Run the build again with --keep."
        for broken in ('[{"type": 5}]', '[{"type": "source_component", "ftype": "simple_chip"}]'):
            with self.subTest(circuit=broken):
                said = wiring_section(self.says_why(a_project_with_circuit(broken), sentence))
                self.assertNotIn("expected string", said)
                self.assertNotIn("&#x27;name&#x27;", said)

    def test_a_refusal_of_the_sheet_keeps_its_own_words(self):
        self.says_why(a_project_with_circuit("{}"), "is not a built circuit")

    def test_a_circuit_json_nested_beyond_the_recursion_limit_never_stops_the_page(self):
        text = self.says_why(a_project_with_circuit("[" * 100000 + "]" * 100000), "Run the build again with --keep.")
        self.assertIn('id="phase-build"', text)

    def test_the_why_holds_no_absolute_path_of_the_project(self):
        project = a_built_project()
        shutil.rmtree(project / "dist")
        with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}), self.assertRaises(sheet.NotBuiltError) as raised:
            sheet.wiring_data(project / "requirements.json")
        self.assertIn(str(project.resolve()), str(raised.exception))  # the unmasked message holds it, so the test can fail
        text = wiring_text_of(project)
        self.assertNotIn(str(project.resolve()), text)
        self.assertIn("nothing is built at dist/board/circuit.json yet", wiring_section(text))


class TheWiringWordsTest(unittest.TestCase):
    """The fixed words of the section never say the board is wired, done or flashed, and a page with wiring runs nothing."""

    ITEMS = [an_item(kind, said="a neutral note") for kind in
             ("off-board-supply", "conflict", "firmware-pull", "unused-pin", "own-socket", "own-socket-unverified", "host-requirement")]

    def test_no_fixed_word_of_the_wiring_says_wired_done_or_flashed(self):
        text = page_of_wiring(PageWiring(THREE, self.ITEMS, ["rec"], None), THREE_PICTURES)
        rail = text.split("</ol>")[1].split("</nav>")[0]
        for word in ("wired", "done", "flashed"):
            self.assertNotIn(word, wiring_section(text).lower())
            self.assertNotIn(word, rail.lower())

    def test_the_page_still_runs_nothing_and_loads_nothing_with_wiring_and_three_pictures(self):
        text = page_of_wiring(PageWiring(THREE, self.ITEMS, ["rec"], None), THREE_PICTURES).lower()
        for word in ("<script", "<iframe", "http", "<button", "<input", "onclick"):
            self.assertNotIn(word, text)

    def test_a_record_s_marks_and_signs_come_out_as_text_in_a_line_before_power(self):
        item = an_item(said="2**8 or 2**9, a ` tick, a & b and x <= y")
        text = page_of_wiring(PageWiring(THREE, [item], ["rec"], None))
        self.assertIn("2**8 or 2**9, a ` tick, a &amp; b and x &lt;= y</li>", text)


class ThePictureFilesTest(unittest.TestCase):
    """The schematic a build kept is a file: `flow.py page` alone shows it."""

    def test_page_alone_shows_the_schematic_a_build_kept(self):
        project = a_built_project()
        (project / "breadboard.svg").write_text("<svg><title>bb</title></svg>")
        (project / "dist" / "board" / "schematic.svg").write_text("<svg><title>kept schematic</title></svg>")
        pictures = kept_pictures(project)
        self.assertEqual([(picture.title, picture.svg is not None) for picture in pictures],
                         [("Breadboard", True), ("Schematic", True), ("PCB", False)])
        self.assertEqual(pictures[1].svg, "<svg><title>kept schematic</title></svg>")
        self.assertEqual(pictures[2].why_missing, NOT_DRAWN_HERE)
        run_flow("page", "--project", str(project), "--json")
        # the schematic is an <img>, and the breadboard stands in the page (P949)
        text = (project / "page.html").read_text()
        self.assertEqual(text.count("data:image/svg+xml;base64,"), 1)
        self.assertEqual(text.count(FIGURE), 1)
        self.assertIn("<svg><title>bb</title></svg></figure>", text)


def a_drawn_project():
    """A built XIAO project with the breadboard.svg the sheet draws, as a build with --keep leaves it."""
    project = a_built_project()
    with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
        sheet.write(project / "requirements.json", project / "breadboard.md")
    return project


#: A picture as tsci writes one, with its namespace.
NAMESPACED = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><title>%s</title></svg>'
FIGURE = '<figure class="fig"'


class TheInlinePictureTest(unittest.TestCase):
    """P949: the breadboard stands in the page as plain shapes, with its keys for a player; any other SVG stays an <img>,
    and so do the schematic and the PCB."""

    @classmethod
    def setUpClass(cls):
        cls.project = a_drawn_project()
        cls.svg = (cls.project / "breadboard.svg").read_text()

    def test_the_breadboard_is_inline_with_no_namespace_and_the_schematic_and_pcb_stay_img(self):
        pictures = [Picture("Breadboard", self.svg, None), Picture("Schematic", NAMESPACED % "schematic", None),
                    Picture("PCB", NAMESPACED % "pcb", None)]
        text = page_of(a_phase("one"), pictures=pictures)
        self.assertIn('xmlns="http://www.w3.org/2000/svg"', self.svg)  # the file keeps it, so the test can fail
        self.assertEqual(text.count(FIGURE), 1)
        self.assertEqual(text.count("data:image/svg+xml;base64,"), 2)
        figure = text.split(FIGURE, 1)[1].split("</figure>", 1)[0]
        self.assertIn("<svg ", figure)
        self.assertIn('data-step="5"', figure)
        for word in ("xmlns", "ns0:", "http"):
            self.assertNotIn(word, text.lower())
        order = [text.index(mark) for mark in ("<h3>Breadboard</h3>", FIGURE, "</figure>", "<h3>Schematic</h3>")]
        self.assertEqual(order, sorted(order))

    def test_each_jumper_step_and_each_part_of_the_built_fixture_is_in_the_page(self):
        text = page_of_project(self.project)
        # the fixture's steps 5 to 8 run a jumper; steps 1 to 4 place a part and carry no step key
        for step in (5, 6, 7, 8):
            self.assertEqual(text.count('data-step="%d"' % step), 1, step)
        self.assertEqual(text.count("data-step="), 4)
        self.assertEqual(sorted(re.findall(r'data-part="([^"]*)"', text)), ["LedRed5mm", "R1", "TactileButton", "board"])

    def test_an_svg_with_anything_but_plain_shapes_stays_an_img(self):
        guards = {
            "script": '<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>',
            "foreignObject": '<svg xmlns="http://www.w3.org/2000/svg"><foreignObject><p>x</p></foreignObject></svg>',
            "style": "<svg><style>rect{fill:red}</style><rect/></svg>",
            "image href": '<svg><image href="x.png"/></svg>',
            "a href": '<svg><a href="#x"><rect/></a></svg>',
            "onload": '<svg onload="alert(1)"><rect/></svg>',
            "xlink:href": '<svg xmlns:xlink="http://www.w3.org/1999/xlink"><rect xlink:href="#x"/></svg>',
            "url(": '<svg><rect style="fill:url(#a)"/></svg>',
            "DOCTYPE": '<!DOCTYPE svg [<!ENTITY a "b">]><svg><text>&a;</text></svg>',
            "a masked path that is no XML": "<svg><text>read <project>/notes</text></svg>",
            "nested beyond the recursion limit": "<svg>" + "<g>" * 100000 + "</g>" * 100000 + "</svg>",
            # the review's refuter ran each of these in headless Chrome: HTML lowercases an attribute's name, and CSS
            # reads an escaped or uppercase url( and image-set
            "ONLOAD": "<svg ONLOAD=\"document.title='SCRIPT-RAN'\"><rect/></svg>",
            "OnClick": '<svg><rect OnClick="alert(1)"/></svg>',
            "HREF": '<svg><rect HREF="#x"/></svg>',
            "URL(": '<svg><rect fill="URL(#a)"/></svg>',
            "&#117;rl(": '<svg><rect fill="&#117;rl(http://x/a)"/></svg>',
            "&#x55;RL(": '<svg><rect fill="&#x55;RL(http://x/a)"/></svg>',
            "a CSS escape": '<svg><rect fill="\\75 rl(http://x/a)"/></svg>',
            "image-set": "<svg><rect fill=\"image-set('http://x/a.png' 1x)\"/></svg>",
            "a style attribute": '<svg><rect style="fill:red"/></svg>',
            "javascript:": '<svg><rect class="javascript:alert(1)"/></svg>',
            "a namespaced attribute": '<svg xmlns:a="http://a.example"><rect a:fill="red"/></svg>',
        }
        for name, svg in guards.items():
            with self.subTest(name):
                text = page_of(a_phase("one"), pictures=[Picture("Breadboard", svg, None)])
                self.assertNotIn(FIGURE, text)
                self.assertEqual(text.count("data:image/svg+xml;base64,"), 1)
                self.assertNotIn("<script", text.lower())
                self.assertNotIn("onload", text.lower())
        # the control: plain shapes, an attribute that starts with "o" and a text that says "on" stand in the page
        text = page_of(a_phase("one"), pictures=[Picture("Breadboard", '<svg><rect opacity="1"/><text>on</text></svg>', None)])
        self.assertEqual((text.count(FIGURE), text.count("data:image/svg+xml;base64,")), (1, 0))

    def test_a_breadboard_with_an_embedded_jpeg_stays_inline(self):
        # P946: a kept photo of a part is an <image> whose one href is a JPEG embedded as base64, by picture_check's rule
        svg = ('<svg xmlns="http://www.w3.org/2000/svg"><g data-part="Epaper"><image x="0" y="0" width="85" height="44" '
               'preserveAspectRatio="none" href="data:image/jpeg;base64,%s"/></g><g class="wire" data-step="1"><path d="M0 0"/>'
               '</g></svg>' % SYNTHETIC_JPEG)
        text = page_of(a_phase("one"), pictures=[Picture("Breadboard", svg, None)])
        self.assertEqual((text.count(FIGURE), text.count("data:image/svg+xml;base64,")), (1, 0))
        self.assertEqual(text.count("data:image/jpeg;base64,%s" % SYNTHETIC_JPEG), 1)
        self.assertEqual(text.count('data-step="1"'), 1)

    def test_an_image_with_any_other_href_or_a_title_inside_a_title_stays_an_img(self):
        guards = {
            "http": '<svg><image href="http://example.org/a.jpg"/></svg>',
            "data:image/png": '<svg><image href="data:image/png;base64,%s"/></svg>' % SYNTHETIC_JPEG,
            "data:image/svg+xml": '<svg><image href="data:image/svg+xml;base64,%s"/></svg>' % SYNTHETIC_JPEG,
            "xlink:href": ('<svg xmlns:xlink="http://www.w3.org/1999/xlink"><image xlink:href="data:image/jpeg;base64,%s"/>'
                           '</svg>' % SYNTHETIC_JPEG),
            "an image with a style": '<svg><image style="a" href="data:image/jpeg;base64,%s"/></svg>' % SYNTHETIC_JPEG,
            "a JPEG href on a rect": '<svg><rect href="data:image/jpeg;base64,%s"/></svg>' % SYNTHETIC_JPEG,
            "a title inside a title": "<svg><title>a<title>b</title></title><rect/></svg>",
            # the review's refuter: HTML lowercases a name and keeps the first of two, so this loaded from the web
            "HREF before href": '<svg><image HREF="//example.com/x.jpg" href="data:image/jpeg;base64,%s"/></svg>' % SYNTHETIC_JPEG,
            "HREF of a PNG": '<svg><image HREF="data:image/png;base64,%s"/></svg>' % SYNTHETIC_JPEG,
            "a name repeated once lowercased": '<svg><rect fill="red" FILL="blue"/></svg>',
        }
        for name, svg in guards.items():
            with self.subTest(name):
                text = page_of(a_phase("one"), pictures=[Picture("Breadboard", svg, None)])
                self.assertNotIn(FIGURE, text)
                self.assertEqual(text.count("data:image/svg+xml;base64,"), 1)

    def test_spark_s_own_breadboard_and_every_pictogram_stand_in_the_page(self):
        pictograms = sorted((ROOT / "data" / "pictograms").glob("*.svg"))
        self.assertGreaterEqual(len(pictograms), 5)
        for name, svg in [("breadboard.svg", self.svg)] + [(each.name, each.read_text()) for each in pictograms]:
            with self.subTest(name):
                text = page_of(a_phase("one"), pictures=[Picture("Breadboard", svg, None)])
                self.assertEqual((text.count(FIGURE), text.count("data:image/svg+xml;base64,")), (1, 0))

    def test_the_mask_covers_the_inline_picture(self):
        home = Path(tempfile.mkdtemp()).resolve()
        picture = Picture("Breadboard", '<svg xmlns="http://www.w3.org/2000/svg"><text>%s/notes</text></svg>' % home, None)
        store = FakeStore()
        with mock.patch.dict(os.environ, {"HOME": str(home), "SPARK_HOME": str(home / "store")}):
            write_page(Path(tempfile.mkdtemp()).resolve() / "project", readers_of(a_phase("one")), parts_of([picture]),
                       store=store)
        text = store.written[0][2]
        self.assertNotIn(str(home), text)
        self.assertIn("<text>~/notes</text>", text)
        # the test can fail: the same page, rendered without the mask, holds the home path
        unmasked = FlowHtmlPage().text(FlowPage("t", [a_phase("one").to_dict()], None, [picture], []))
        self.assertIn(str(home), unmasked)

    def test_the_mask_covers_a_home_path_written_as_character_references(self):
        # the review: the mask reads the raw text, and the parse turns &#47; into the / of the home path
        home = Path(tempfile.mkdtemp()).resolve()
        encoded = str(home).replace("/", "&#47;")
        picture = Picture("Breadboard", '<svg xmlns="http://www.w3.org/2000/svg"><text>%s&#47;notes</text></svg>' % encoded, None)
        store = FakeStore()
        with mock.patch.dict(os.environ, {"HOME": str(home), "SPARK_HOME": str(home / "store")}):
            write_page(Path(tempfile.mkdtemp()).resolve() / "project", readers_of(a_phase("one")), parts_of([picture]),
                       store=store)
        text = store.written[0][2]
        self.assertNotIn(str(home), text)
        self.assertIn("<text>~/notes</text>", text)
        # the test can fail: the same page, rendered without the mask, holds the decoded home path inline
        self.assertIn(str(home), FlowHtmlPage().text(FlowPage("t", [a_phase("one").to_dict()], None, [picture], [])))


def pad_legend(text):
    """(swatch colour, words) of each line of the page's pad legend."""
    legend = text.split('<ul class="pads">', 1)[1].split("</ul>", 1)[0]
    return re.findall(r'<li><span class="sw" style="background:(#[0-9a-f]{6})"></span>([^<]*)</li>', legend)


def token_block(pattern, style):
    return dict(re.findall(r"(--[a-z]+):([^;]+)", re.search(pattern, style).group(1)))


class TheLookTest(unittest.TestCase):
    """P949: the praised page's colours, light and dark, with system fonts and nothing loaded, and a legend of the pads
    under the breadboard that says only what the picture draws."""

    def test_the_pad_legend_follows_an_inline_breadboard_only(self):
        svg = (a_drawn_project() / "breadboard.svg").read_text()
        text = page_of(a_phase("one"), pictures=[Picture("Breadboard", svg, None)])
        self.assertEqual(pad_legend(text), [("#ffd34d", "pad in use"), ("#c9a24b", "pad free")])
        self.assertLess(text.index("</figure>"), text.index('<ul class="pads">'))
        held = '<svg><circle r="2" fill="#5bc0eb" data-pad="held"/></svg>'
        text = page_of(a_phase("one"), pictures=[Picture("Breadboard", held, None)])
        self.assertEqual(pad_legend(text), [("#5bc0eb", "pad held: do not use")])
        for name, pictures in {"no picture": [], "not drawn": [Picture("Breadboard", None, "not drawn")],
                               "refused": [Picture("Breadboard", "<svg><script/></svg>", None)],
                               "no pad": [Picture("Breadboard", "<svg><rect/></svg>", None)],
                               "the schematic": [Picture("Schematic", svg, None)]}.items():
            with self.subTest(name):
                self.assertNotIn('class="pads"', page_of(a_phase("one"), pictures=pictures))

    def test_every_token_is_defined_light_and_dark_and_the_style_uses_only_them(self):
        page = page_of_wiring(PageWiring(THREE, [], ["rec"], None), THREE_PICTURES)
        style = re.search(r"<style>(.*?)</style>", page, re.S).group(1)
        light = token_block(r"^:root\{([^}]*)\}", style)
        dark = token_block(r'@media \(prefers-color-scheme: dark\)\{:root:not\(\[data-theme="light"\]\)\{([^}]*)\}\}', style)
        self.assertEqual(dark, token_block(r':root\[data-theme="dark"\]\{([^}]*)\}', style))
        colours = {"--bg", "--ink", "--muted", "--line", "--signal", "--backdrop"}
        self.assertEqual((set(light), set(dark)), (colours | {"--display", "--body"}, colours))
        for name in colours - {"--backdrop"}:
            self.assertNotEqual(light[name], dark[name], name)
        # the praised page's ground, and a white ground under the pictures in both, which are drawn for a light one
        self.assertEqual((light["--bg"], dark["--bg"], light["--backdrop"], dark["--backdrop"]),
                         ("#eef1f3", "#141b21", "#fff", "#fff"))
        self.assertEqual(set(re.findall(r"var\((--[a-z]+)\)", style)), set(light))
        self.assertTrue(light["--body"].startswith("system-ui"), light["--body"])
        outside = re.sub(r"\{[^{}]*--bg:[^{}]*\}", "{}", style)
        self.assertEqual(style.count("--bg:"), 3)
        self.assertNotRegex(outside, r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(")
        self.assertNotRegex(outside, r"(?:color|background|border-color):\s*(?!var\(|transparent|inherit)[a-z]+")
        for word in ("url(", "@import", "@font-face"):
            self.assertNotIn(word, page)


class TheBudgetTest(unittest.TestCase):
    """P949: with the walk's e-paper breadboard inline, its wiring and two tsci pictures of the walk's sizes (schematic.svg
    96 KB, pcb.svg 331 KB), the page stays under 3 MiB."""

    BUDGET = 3 * 1024 * 1024

    @classmethod
    def setUpClass(cls):
        cls.project = Path(tempfile.mkdtemp()) / "epaper"
        shutil.copytree(ROOT / "tests" / "data" / "breadboard" / "epaper", cls.project)
        with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
            sheet.write(cls.project / "requirements.json", cls.project / "breadboard.md")
            cls.wiring = kept_wiring(cls.project)

    def page(self, pcb_bytes):
        def tsci(size):
            return NAMESPACED % ("x" * size)
        pictures = [Picture("Breadboard", (self.project / "breadboard.svg").read_text(), None),
                    Picture("Schematic", tsci(96 * 1000), None), Picture("PCB", tsci(pcb_bytes), None)]
        return page_of_wiring(self.wiring, pictures)

    def test_the_page_stays_within_its_budget(self):
        text = self.page(331 * 1000)
        self.assertEqual((text.count(FIGURE), text.count("data-step="), len(self.wiring.steps)), (1, 8, 10))
        self.assertLess(len(text.encode("utf-8")), self.BUDGET)

    def test_a_pcb_picture_of_3_mib_goes_over(self):
        # the twin, so the budget test can fail
        self.assertGreater(len(self.page(self.BUDGET).encode("utf-8")), self.BUDGET)


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
        return kept_files.keep_tabbed_page(self.project, [Stage("build", OK)], self.kept, FakeTscircuitExport(), write_kept_page)

    def test_in_a_project_the_page_is_the_flow_page_with_three_pictures(self):
        (self.project / ".spark").mkdir()
        entry = self.keep()
        self.assertEqual((entry["did"], entry["why"]), ("wrote", FlowHtmlPage.PURPOSE_MESSAGE))
        text = self.page.read_text()
        # the schematic and the PCB are <img>s, and the breadboard stands in the page with no namespace (P949)
        self.assertEqual(2, text.count("data:image/svg+xml;base64,"))
        self.assertEqual(text.count(FIGURE), 1)
        self.assertNotIn("http", text.lower())
        self.assertEqual(len(Parsed(text).sections), 9)

    def test_a_flow_page_that_raises_is_one_no_page_entry(self):
        # A pin: whatever the flow page raises, the keep step answers one "not written" entry and the build goes on.
        def raising(project, tabs):
            raise TypeError("a record of a shape nobody foresaw")
        (self.project / ".spark").mkdir()
        entry = kept_files.keep_tabbed_page(self.project, [Stage("build", OK)], self.kept, FakeTscircuitExport(), raising)
        self.assertEqual((entry["did"], entry["why"]), ("not written", "the flow page could not be written (TypeError)"))

    def test_the_keep_step_writes_the_schematic_and_pcb_files(self):
        (self.project / ".spark").mkdir()
        self.keep()
        board = self.project / "dist" / "board"
        self.assertEqual((board / "schematic.svg").read_text(), FakeTscircuitExport().export_svg("c", "schematic-svg").svg)
        self.assertEqual((board / "pcb.svg").read_text(), FakeTscircuitExport().export_svg("c", "pcb-svg").svg)
        self.assertNotEqual((board / "schematic.svg").read_text(), (board / "pcb.svg").read_text())

    def test_an_export_that_gave_nothing_removes_the_earlier_file(self):
        (self.project / ".spark").mkdir()
        board = self.project / "dist" / "board"
        board.mkdir(parents=True)
        (board / "schematic.svg").write_text("<svg>of an earlier design</svg>")
        (board / "pcb.svg").write_text("<svg>of an earlier design</svg>")
        nothing = SvgExportResult(None, "tsci is not installed")
        exporter = FakeTscircuitExport({"schematic-svg": nothing})
        kept_files.keep_tabbed_page(self.project, [Stage("build", OK)], self.kept, exporter, write_kept_page)
        self.assertFalse((board / "schematic.svg").exists())
        self.assertIn("fake pcb-svg", (board / "pcb.svg").read_text())

    def test_a_build_that_did_not_finish_removes_both_files(self):
        (self.project / ".spark").mkdir()
        board = self.project / "dist" / "board"
        board.mkdir(parents=True)
        for name in ("schematic.svg", "pcb.svg"):
            (board / name).write_text("<svg>of an earlier design</svg>")
        kept_files.keep_tabbed_page(self.project, [Stage("build", COULD_NOT_RUN)], self.kept, FakeTscircuitExport(), write_kept_page)
        self.assertEqual(sorted(path.name for path in board.iterdir()), [])

    def test_a_picture_file_that_cannot_be_removed_never_stops_the_build(self):
        board = self.project / "dist" / "board"
        board.mkdir(parents=True)
        (board / "schematic.svg").write_text("<svg>of an earlier design</svg>")
        (self.project / ".spark").mkdir()
        board.chmod(0o555)
        self.addCleanup(board.chmod, 0o755)
        entry = kept_files.keep_tabbed_page(self.project, [Stage("build", COULD_NOT_RUN)], self.kept, FakeTscircuitExport(), write_kept_page)
        self.assertIn("did not finish", entry["why"])
        problem = [each for each in self.kept if each["file"] == str(board / "schematic.svg")]
        self.assertEqual([each["did"] for each in problem], ["not kept"])
        self.assertIn("cannot be kept", problem[0]["line"])

    def test_a_picture_file_that_cannot_be_written_never_blocks_the_page(self):
        board = self.project / "dist" / "board"
        (board / "schematic.svg").mkdir(parents=True)
        (self.project / ".spark").mkdir()
        entry = self.keep()
        self.assertEqual(entry["did"], "wrote")
        text = self.page.read_text()
        # the PCB is an <img>, and the breadboard stands in the page (P949)
        self.assertEqual(text.count("data:image/svg+xml;base64,"), 1)
        self.assertEqual(text.count(FIGURE), 1)
        self.assertIn("its file cannot be kept", text)
        self.assertEqual([each["did"] for each in self.kept if each["file"] == str(board / "schematic.svg")], ["not kept"])
        self.assertIn("fake pcb-svg", (board / "pcb.svg").read_text())

    def test_a_folder_that_is_no_project_keeps_no_picture_file_and_removes_none(self):
        board = self.project / "dist" / "board"
        board.mkdir(parents=True)
        (board / "pcb.svg").write_text("<svg>of an earlier design</svg>")
        self.keep()
        kept_files.keep_tabbed_page(self.project, [Stage("build", COULD_NOT_RUN)], self.kept, FakeTscircuitExport(), write_kept_page)
        self.assertEqual(sorted(path.name for path in board.iterdir()), ["pcb.svg"])
        self.assertEqual((board / "pcb.svg").read_text(), "<svg>of an earlier design</svg>")

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
        entries = kept_files.keep_all([Stage("build", OK)], workdir, asked, FakeTscircuitExport(), write_kept_page)
        files = [Path(entry["file"]).name for entry in entries]
        self.assertGreater(files.index("page.html"), files.index("sim"))

    def test_an_unreadable_record_still_gets_its_page_from_the_build(self):
        # The refuter's case: a build record whose stages is no list, in a read-only .spark, so the record is not kept and the
        # flow page reads the malformed one. The build still ends as it ends, with the page written and no traceback.
        import argparse
        from fakes import run_build_board
        project = Path(tempfile.mkdtemp()) / "project"
        (project / ".spark").mkdir(parents=True)
        shutil.copy(BUILT / "requirements.json", project / "requirements.json")
        record = project / ".spark" / "build.json"
        record.write_text('{"status": "ok", "stages": 5}')
        work = Path(tempfile.mkdtemp())
        (work / "dist" / "board").mkdir(parents=True)
        (work / "dist" / "board" / "circuit.json").write_text("[]")
        record.chmod(0o444)
        (project / ".spark").chmod(0o555)
        self.addCleanup((project / ".spark").chmod, 0o755)
        args = argparse.Namespace(json=False, keep=project, requirements=project / "requirements.json")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            code = run_build_board([Stage("build", OK, "fine")], args, work)
        self.assertEqual(code, 0)
        self.assertNotIn("Traceback", err.getvalue())
        self.assertIn("not kept: ", err.getvalue())
        self.assertEqual(err.getvalue().count("no page: the flow page could not be written (TypeError)"), 0)
        self.assertIn("wrote " + str(project / "page.html"), err.getvalue())
        self.assertIn("is no build record", (project / "page.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
