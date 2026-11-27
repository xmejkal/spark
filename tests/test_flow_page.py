"""
The page of a project (P827, #1185): page.html shows each phase of the flow with a status word and a mark, and never a
tick for a phase that is not ok. The page is built from the phases a flow gives it, so ten fake phases give ten entries.
The card's own proof writes the page of a built project to disk, reads the file back and compares it with `flow.py show`.
It covers `flow_page`, `write_flow_page`, `show_flow.read_flow` and the keep step's flow page.

    python3 -m unittest tests.test_flow_page
"""

import contextlib
import datetime
import html
import html.parser
import io
import itertools
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
from spark.breadboard import before_power, sheet  # noqa: E402
from spark.flow.flow_page import FlowHtmlPage, FlowPage, PageWiring, Picture, page_words  # noqa: E402
from spark.flow.page_sections import TICK, shown_phase, word_of  # noqa: E402
from spark.flow.offer_steps import build_step  # noqa: E402
from spark.flow.phase_readers import MARKS, Offer, Phase  # noqa: E402
from spark.flow.show_flow import read_flow  # noqa: E402
from spark.flow.flow_codes import WIRED_BUILD_MESSAGE, WIRED_SHEET_MESSAGE, WIRED_STEP_MESSAGE  # noqa: E402
from spark.flow.wired_board import day_of  # noqa: E402
from spark.flow.fingerprint import FILES, fingerprint_of  # noqa: E402
from spark.core import zone_time  # noqa: E402
from test_flow import MAY_NOTE, SHARED, SOIL, WIRED_PICK, FlowTest, in_prague, with_needs  # noqa: E402
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
#: The bench note (P1043-D10, the review of #1579); before it: "This page reads the project's files. It does not know whether the
#: board is wired or flashed."
BENCH = "This page reads the project's files and its board logs. It cannot see your wiring or what the board shows now."
NOT_WRITTEN = "page_not_written"
NOT_DRAWN_HERE = "Not drawn here. The build draws it: run /spark:build --keep."
NO_BREADBOARD_FILE = "Not drawn: breadboard.svg is not in the project yet. The build with --keep writes it."
#: The page's script (P829 PR 3), as the page holds it, and its block: the inert words, then the script, before </body>.
PAGE_SCRIPT = (ROOT / "scripts" / "spark" / "flow" / "page_script.js").read_text(encoding="utf-8")
SCRIPT_BLOCK = re.compile(r'<script type="application/json" id="spark-words">.*?</script>\n<script>.*?</script>\n', re.S)
#: A page with an offer of each kind and today's page of it, written by the renderer before the script (P829 PR 3).
SAMPLE = ROOT / "tests" / "data" / "flow-page"
#: The one web address the page loads (P1120): the font's stylesheet, written here, never imported from the code.
FONT_URL = "https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;600&display=swap"
#: The system's fonts, last in the page's font stack: the page's fonts with no network.
SYSTEM_FONTS = 'system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif'


def without_script(text):
    """`text` without the script block and the script's hooks (data-makes-stale on a sendable offer, data-key with it on the
    NOW box's NEXT line, P1062, and data-need on a need's row, P1067): the page as it was before the script."""
    text = re.sub(r'<p class="next" data-key="[^"]*" data-makes-stale="[^"]*">', '<p class="next">', SCRIPT_BLOCK.sub("", text, count=1))
    return re.sub(r' data-(makes-stale|need)="[^"]*"', "", text)


def scripts_of(text):
    """Each <script> of `text`, as (its attributes, its text)."""
    return [(dict(re.findall(r'([a-z-]+)="([^"]*)"', attributes)), body)
            for attributes, body in re.findall(r"<script([^>]*)>(.*?)</script>", text, re.S)]


def assert_only_the_font_is_loaded(test, text):
    """The page loads one thing from the web (P1120): the font's stylesheet, by one `<link>` in `<head>` to the literal
    FONT_URL. With that link gone, no web address is left."""
    link = '<link rel="stylesheet" href="%s">' % html.escape(FONT_URL)
    test.assertEqual((text[:text.index("</head>")].count(link), text.count(link)), (1, 1))
    test.assertNotIn("http", text.replace(link, "").lower())


def assert_spark_s_script_only(test, text):
    """The page runs spark's script only (P829 PR 3, D7): one script with no src and no type, whose text is page_script.js,
    beside the inert words block, and no frame, control in the markup or handler. Its one web address is the font's
    stylesheet (P1120)."""
    scripts = scripts_of(text)
    test.assertEqual([attributes for attributes, _body in scripts], [{"type": "application/json", "id": "spark-words"}, {}])
    test.assertEqual(scripts[1][1], PAGE_SCRIPT)
    test.assertEqual(text.lower().count("<script"), 2)
    for word in ("<iframe", "<button", "<input", "onclick"):
        test.assertNotIn(word, text.lower())
    assert_only_the_font_is_loaded(test, text)


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

    def test_a_flow_of_ten_phases_gives_ten_sections_in_order_in_the_developer_fold(self):
        names = NINE + ["bench-test"]
        text = page_of(*[a_phase(name) for name in names])
        self.assertEqual([attrs["data-phase"] for attrs, _ in Parsed(text).sections], names)
        self.assertEqual([attrs["data-phase"] for attrs, _ in Parsed(developer(text)).sections], names)

    def test_a_flow_of_one_phase_gives_one(self):
        parsed = Parsed(page_of(a_phase("only")))
        self.assertEqual(([attrs["data-phase"] for attrs, _ in parsed.sections], len(parsed.sections)), (["only"], 1))

    def test_the_page_holds_no_phase_name_the_flow_did_not_give(self):
        # P1062: as a word, so the freshness line's "deployed" is no phase name
        text = without_script(page_of(a_phase("alpha"), a_phase("beta"))).lower()
        for name in NINE:
            self.assertIsNone(re.search(r"\b%s\b" % name, text), name)

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
                self.assertNotIn(TICK, parsed.sections[0][1])
                self.assertIn(MARKS[COULD_NOT_RUN][1], parsed.sections[0][1])

    def test_ok_shows_the_tick(self):
        parsed = Parsed(page_of(a_phase("fine", OK)))
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
                self.assertIn(word_of(status), parsed.sections[0][1])
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

    def test_there_is_no_rail_and_the_phases_stand_in_the_closed_developer_fold(self):
        # P1062: the rail is gone; the developer fold's phase sections, each one closed line with its mark, are the same list
        self.assertIsNone(self.parsed.nav)
        self.assertNotIn(" open", fold(self.text, "developer"))
        self.assertEqual(len(Parsed(developer(self.text)).sections), 7)

    def test_every_link_points_to_an_id_that_exists(self):
        text = order_page(guide=a_guide(now=dict(a_guide()["now"], steps=3)))
        parsed = Parsed(text)
        links = [href for href in parsed.hrefs if href.startswith("#")]
        self.assertGreater(len(links), 7)
        for href in links:
            self.assertIn(href[1:], parsed.ids)

    def test_each_section_s_data_status_is_the_flow_s_status(self):
        self.assertEqual(len(self.parsed.sections), 7)
        for (attrs, _said), status in zip(self.parsed.sections, MARKS):
            self.assertEqual(attrs["data-status"], "none" if status is None else status)

    def test_the_page_runs_nothing_and_loads_only_the_font(self):
        for text in (self.text, page_of(a_phase("one"), pictures=[Picture("Breadboard", "<svg/>", None)])):
            assert_spark_s_script_only(self, text)

    def test_a_sentence_with_an_angle_bracket_is_escaped(self):
        text = page_of(a_phase("one", says=["<b>bold</b> & more"], offers=[Offer("a<b", "<i>x</i>", "<i>y</i>", (), build_step("project"))]), project="<p>")
        self.assertNotIn("<b>", text)
        self.assertNotIn("<i>", text)
        self.assertIn("<code>a&lt;b</code>", text)
        self.assertIn("&lt;b&gt;bold&lt;/b&gt; &amp; more", text)
        self.assertIn("a&lt;b", text)

    def test_the_same_flow_gives_the_same_bytes(self):
        phases = [a_phase("one"), a_phase("two", None)]
        self.assertEqual(page_of(*phases), page_of(*phases))

    def test_an_offer_shows_its_label_and_keeps_its_key_in_data_key(self):
        # P1062: the sendable row stands once, in the parts fold; the developer fold shows its key as text, with no hook.
        # P1135: the row holds its label alone; its effect stands in its Send box and in the developer fold
        text = page_of(a_phase("one", offers=[Offer("build", "Build the board", "Builds the board.", (), build_step("project"))]))
        self.assertEqual(text.count('<li data-key="build" data-makes-stale="">Build the board</li>'), 1)
        self.assertLess(text.index('<li data-key="build"'), text.index(fold(text, "developer")))
        self.assertIn("<li><code>build</code> Build the board: Builds the board.</li>", developer(text))
        self.assertEqual(without_script(text).count(">build<"), 1)
        self.assertNotIn("<button", text)

    def test_the_pictures_stand_together_in_their_fold_before_the_developer_fold_s_phases_and_legend(self):
        # P1062: the pictures fold comes before the developer fold, which holds the phases and the legend
        pictures = [Picture("Breadboard", "<svg/>", None), Picture("Schematic", None, "Not drawn, because no tsci.")]
        text = page_of(a_phase("one"), pictures=pictures)
        self.assertEqual(text.count('<section id="pictures">'), 1)
        order = [text.index(mark) for mark in (fold(text, "pictures"), '<section id="pictures">', "<h3>Breadboard</h3>",
                                                "<h3>Schematic</h3>", fold(text, "developer"), 'id="phase-one"', '<section class="legend">')]
        self.assertEqual(order, sorted(order))
        self.assertIn("Not drawn, because no tsci.", text)
        self.assertIn('data-fold="pictures"><summary><h2>Pictures</h2></summary>', text)

    def test_a_page_with_no_pictures_has_no_pictures_section_and_no_link(self):
        text = page_of(a_phase("one"))
        self.assertNotIn("pictures", text)


class TheBenchLineTest(unittest.TestCase):
    def test_the_bench_line_is_there_and_wired_and_flashed_appear_only_in_it(self):
        text = page_of(a_phase("deploy", "not-started"))
        bench = html.escape(BENCH)
        self.assertEqual(text.count(bench), 1)
        # P977 PR 2: the guide's deploy sentence asks "When the breadboard is wired, ...", a condition for the person and no claim
        # that the board is wired, so only that sentence stands outside this check; the rest of the guide and the page do not.
        deploy = html.escape("When the breadboard is wired, plug the board into USB. Ask Claude to look at it first, then run the deploy in your terminal.")
        rest = without_script(text).replace(bench, "").replace(deploy, "")
        for word in ("wired", "flashed", "none recorded"):
            self.assertNotIn(word, rest)

    def test_the_real_flow_of_a_project_adds_no_word_about_the_board(self):
        project = a_built_project()
        FlowPageStore().write(project, "page.html", FlowHtmlPage().text(
            FlowPage("t", [phase.to_dict() for phase in read_flow(project)[0]], None, [], [])))
        text = without_script((project / "page.html").read_text())
        # P1044: the fixture keeps a sheet. Like P977's deploy sentence, the wired sentences are each a condition for the
        # person ("If you wired the board", "whether you wired from it"), never a claim, so only they stand outside this check.
        sheet_day = day_of(zone_time.stamp(datetime.datetime.fromtimestamp((project / "breadboard.md").stat().st_mtime)))
        for sentence in (WIRED_SHEET_MESSAGE % sheet_day, WIRED_STEP_MESSAGE, WIRED_BUILD_MESSAGE):
            self.assertIn(html.escape(sentence), text)  # the review of #1609, lens 4: each is there, so the rest is checked
            text = text.replace(html.escape(sentence), "")
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


#: A value of the project's secrets file (P1060), MIN_SECRET characters or more, and one that the page never shows.
SECRET, OTHER_SECRET = "wifi-pass-4711", "never-on-the-page-0815"
#: A secrets file that does not parse: its value holds no closing quote. No answer may show its text (D5).
HALF_TYPED = "half-typed-value-31337"


def a_project_with_secrets(text):
    """A project folder whose firmware/wifi_secrets.py holds `text`."""
    project = Path(tempfile.mkdtemp()) / "project"
    (project / "firmware").mkdir(parents=True)
    (project / "firmware" / "wifi_secrets.py").write_text(text, encoding="utf-8")
    return project


def a_secrets_line(value):
    return 'WIFI_PASSWORD = "%s"\n' % value


class TheSecretMaskTest(unittest.TestCase):
    """P1060 (#1558): the values of the project's secrets file are masked in the page's texts, and a picture's SVG takes
    the paths-only mask (A12): masking a value inside a drawing would break it, as the design's short-secret test says."""

    def test_a_secret_is_masked_in_a_phase_sentence_and_kept_in_the_svg(self):
        project = a_project_with_secrets(a_secrets_line(SECRET))
        phase = a_phase("one", says=["joins the network %s" % SECRET])
        drawn = Picture("Breadboard", '<svg xmlns="http://www.w3.org/2000/svg"><text>%s</text></svg>' % SECRET, None)
        missing = Picture("Schematic", None, "not drawn for %s" % SECRET)
        store = FakeStore()
        write_page(project, readers_of(phase), parts_of([drawn, missing]), store=store)
        text = without_script(store.written[0][2])
        self.assertIn("joins the network ***", text)
        self.assertIn("not drawn for ***", text)
        self.assertEqual(text.count(SECRET), 1)
        self.assertIn("<text>%s</text>" % SECRET, text)

    def test_the_bytes_change_only_where_a_secret_was(self):
        # A10: the SVG holds no secret here, so the page with the mask is the page without it, each secret made ***
        phase = a_phase("one", says=["joins the network %s" % SECRET])
        drawn = Picture("Breadboard", '<svg xmlns="http://www.w3.org/2000/svg"><text>a drawing</text></svg>', None)
        project = a_project_with_secrets(a_secrets_line(OTHER_SECRET))
        pages = []
        for value in (OTHER_SECRET, SECRET):
            (project / "firmware" / "wifi_secrets.py").write_text(a_secrets_line(value), encoding="utf-8")
            store = FakeStore()
            write_page(project, readers_of(phase), parts_of([drawn]), store=store)
            pages.append(store.written[0][2])
        without_mask, with_mask = pages
        self.assertIn(SECRET, without_mask)
        self.assertEqual(with_mask, without_mask.replace(SECRET, "***"))


class TheUnreadableSecretsTest(unittest.TestCase):
    """P1060 D5 (the delegated council, the PO's to change): what reaches the published Artifact fails closed. When a
    secrets file cannot be read or parsed, write_page writes nothing, and each writer says so in its own words, naming the
    file only: the text of a parse error holds the line, and the line holds the secret."""

    def test_flow_page_writes_nothing_and_says_the_page_on_disk_is_the_old_one(self):
        from spark.flow.write_flow_page import SECRETS_FIX
        project = a_project_with_secrets('WIFI_PASSWORD = "%s\n' % HALF_TYPED)
        (project / "page.html").write_text("an old page", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
            code = flow.main(["page", "--project", str(project), "--json"])
        envelope = json.loads(out.getvalue())
        self.assertEqual((code, envelope["status"]), (2, COULD_NOT_RUN))
        [item] = envelope["unchecked"]
        self.assertEqual((item["code"], item["fix"]), (NOT_WRITTEN, SECRETS_FIX))
        self.assertEqual(item["sentence"], "page.html was not written: firmware/wifi_secrets.py cannot be read or parsed, so spark "
                                           "cannot mask the values of the project's secrets. The page on disk is the old one")
        self.assertEqual((project / "page.html").read_text(encoding="utf-8"), "an old page")
        self.assertNotIn(HALF_TYPED, out.getvalue() + err.getvalue())

    def test_the_build_s_kept_page_is_not_written_and_names_the_file(self):
        project = a_project_with_secrets('WIFI_PASSWORD = "%s\n' % HALF_TYPED)
        (project / ".spark").mkdir()
        (project / "breadboard.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        kept = [{"file": str(project / "dist"), "did": "wrote"}, {"file": str(project / "breadboard.svg"), "did": "wrote", "why": "a picture"}]
        entry = kept_files.keep_tabbed_page(project, [Stage("build", OK)], kept, FakeTscircuitExport(), write_kept_page)
        self.assertEqual(entry["did"], "not written")
        self.assertIn("firmware/wifi_secrets.py cannot be read or parsed", entry["why"])
        self.assertNotIn(HALF_TYPED, repr(entry))
        self.assertFalse((project / "page.html").exists())


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
        # P977: the page answers the guide too
        # P829 PR 4: and the artifact the page is published as, null until /spark:page publishes it
        self.assertEqual(sorted(envelope["data"]), ["artifact", "did", "file", "fingerprint", "guide", "phases", "stands_at"])
        self.assertEqual(envelope["data"]["guide"], run_flow("show", "--project", str(project), "--json")[0]["data"]["guide"])
        self.assertEqual(envelope["data"]["guide"]["now"]["phase"], "firmware")
        self.assertEqual(envelope["data"]["fingerprint"], fingerprint_of(project, read_flow(project)[0]))
        body = re.search(r'<body data-stands-at="[^"]*" data-fingerprint="([0-9a-f]{12})" data-written="([^"]*)">',
                         (project / "page.html").read_text(encoding="utf-8"))
        self.assertEqual(body.group(1), envelope["data"]["fingerprint"][:12])
        written = max((project / name).stat().st_mtime for name in FILES if (project / name).is_file())
        self.assertEqual(body.group(2), zone_time.stamp(datetime.datetime.fromtimestamp(written)))
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

    def test_a_pick_that_owes_a_fact_gives_no_parts_list_button_and_shows_what_it_owes(self):
        # P993: the parts list would refuse and write nothing, so the page offers no button and says the blocker
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        (home / "catalog" / "x-probe.json").write_text(json.dumps({"schema": 1, "id": "x-probe", "name": "A soil probe", "kind": "sensor",
                                                                   "function": [{"does": "sense", "what": "soil-moisture"}]}))
        project = Path(tempfile.mkdtemp()) / "plant-alarm"
        (project / ".spark").mkdir(parents=True)
        (project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [
            {"id": "board", "does": "compute", "what": "microcontroller", "pick": [{"board": "xiao-esp32-c6"}]},
            {"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"part": "x-probe"}]}]}))
        with mock.patch.dict(os.environ, {"SPARK_HOME": str(home)}):
            _, code = run_flow("page", "--project", str(project), "--json")
        text = (project / "page.html").read_text(encoding="utf-8")
        self.assertEqual(code, 0)
        self.assertNotIn('data-key="requirements"', text)
        self.assertIn("“A soil probe” for soil still lacks what spark needs: needs, footprint, pin_order, pin_order_proof. "
                      "Ask Claude how to fill it in.", html.unescape(text))

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
        text = (project / "page.html").read_text(encoding="utf-8")
        self.assertEqual([attrs["data-phase"] for attrs, _ in Parsed(developer(text)).sections], [phase["phase"] for phase in phases])
        for phase, (attrs, said) in zip(phases, parsed.sections):
            self.assertEqual(attrs["data-status"], "none" if phase["status"] is None else phase["status"])
            self.assertEqual(TICK in said, phase["status"] == OK, phase["phase"])
        ok = [phase for phase in phases if phase["status"] == OK]
        self.assertEqual(sum(TICK in said for _attrs, said in parsed.sections), len(ok))
        outside = re.sub(r'<section class="legend">.*?</section>', "", without_script(text))
        parts_ok = [phase for phase in ok if phase["phase"] == "parts"]  # the parts fold's summary shows the parts phase's mark
        self.assertEqual(outside.count(TICK), len(ok) + len(parts_ok))

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


#: P828 step 2: the line under the title, and its second sentence when the page holds wiring steps, as the PO reads them.
PAGE_INTRO = "Where this project stands. This page only shows it. To change anything, tell Claude in the chat."
# P977 PR 2 review: a layout sentence, no longer an order that competes with the guide's NOW.
WIRING_FIRST = "Below: the wiring and its pictures, then each phase, folded: click one to read it."


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
        items = self.data.before_power.items
        # P828 step 2: a part's host requirements stand under its name, given once as a line of its own.
        heads = [line for line in self.parsed.before if line in {item.subject for item in items}]
        self.assertEqual(len(self.parsed.before) - len(heads), len(items))
        runs = [len(list(run)) for _key, run in itertools.groupby(
            items, key=lambda item: (item.record, item.subject) if item.kind == "host-requirement" else id(item))]
        self.assertEqual(len(heads), sum(1 for size in runs if size > 1), "one name line for each run of two or more")
        self.assertTrue(items)
        first = self.text.index('id="step-1"')
        self.assertLess(self.text.index("<h3>Before you power it</h3>"), first)
        self.assertLess(self.text.index("</ul>"), first)

    def test_every_step_has_an_id_of_its_number_and_no_before_power_line_is_among_them(self):
        self.assertEqual([step["attrs"]["id"] for step in self.parsed.steps], ["step-%d" % step.number for step in self.data.steps])
        steps = self.text.split('<ol id="steps">')[1].split("</ol>")[0]
        self.assertEqual(steps.count("<li "), len(self.data.steps))
        self.assertNotIn("<li>", steps)
        self.assertNotIn("Before you power it", steps)

    def test_a_page_with_a_sheet_shows_the_wiring_then_the_pictures_then_the_bench_note_then_the_phases(self):
        # P828 step 2, P1062: the wiring and its pictures come before the phases, which stand in the developer fold, last
        text = page_of_wiring(PageWiring(THREE, [], [], None), THREE_PICTURES)
        order = [text.index(mark) for mark in ('<section id="wiring">', '<section id="pictures">', '<section class="notes">',
                                                'id="phase-one"', '<section class="legend">')]
        self.assertEqual(order, sorted(order))
        self.assertNotIn("<nav", text)

    def test_the_section_holds_its_heading_the_fixed_sentence_the_lines_the_link_and_the_steps_in_that_order(self):
        text = page_of_wiring(PageWiring(THREE, [an_item()], ["rec"], None), THREE_PICTURES)
        # P1062: the heading is the fold's summary, and the records line stands in the developer fold, after the steps
        marks = ["<h2>Wiring: 3 steps</h2>", "<p>Read the lines before power first. In the Breadboard picture below, each jumper "
                 "carries a pill with its step&#x27;s number and the two pads it joins: find the holes there.</p>",
                 "<h3>Before you power it</h3>", "<ul>", "</ul>",
                 "One at a time: start at step 1", '<ol id="steps">', fold(text, "developer"), "Each record whole"]
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
        # P1062: the rail is gone; the wiring fold's summary is its one other fixed line
        summary = text.split(fold(text, "wiring"))[1].split("</summary>")[0]
        for word in ("wired", "done", "flashed"):
            self.assertNotIn(word, wiring_section(text).lower())
            self.assertNotIn(word, summary.lower())

    def test_the_page_still_runs_nothing_and_loads_only_the_font_with_wiring_and_three_pictures(self):
        assert_spark_s_script_only(self, page_of_wiring(PageWiring(THREE, self.ITEMS, ["rec"], None), THREE_PICTURES))

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
        for word in ("xmlns", "ns0:"):
            self.assertNotIn(word, text.lower())
        assert_only_the_font_is_loaded(self, text)  # P1120: no web address but the font's link, so no namespace's either
        order = [text.index(mark) for mark in ("<h3>Breadboard</h3>", FIGURE, "</figure>", "<h3>Schematic</h3>")]
        self.assertEqual(order, sorted(order))

    def test_each_jumper_step_and_each_part_of_the_built_fixture_is_in_the_page(self):
        text = page_of_project(self.project)
        # the fixture's steps 5 to 9 run a jumper (7 to 9 join GND through a - rail, P953); steps 1 to 4 and 10 place
        # a part and carry no step key
        for step in (5, 6, 7, 8, 9):
            self.assertEqual(text.count('data-step="%d"' % step), 1, step)
        self.assertEqual(text.count("data-step="), 5)
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
                self.assertNotIn("alert(1)", text)
                self.assertEqual([body for _attributes, body in scripts_of(text)][1:], [PAGE_SCRIPT], "the only script is spark's")
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
    return dict(re.findall(r"(--[a-z-]+):([^;]+)", re.search(pattern, style).group(1)))


#: The page's colour tokens (P1120), by name: each stands in light and in dark. The tests check rules, never the values.
COLOUR_TOKENS = {"--bg", "--surface", "--ink", "--muted", "--line", "--accent", "--accent-hover", "--on-accent", "--accent-edge",
                 "--focus", "--now-bg", "--now-ink", "--now-halo", "--amber-ink", "--amber-plane", "--red-ink", "--red-plane",
                 "--backdrop"}
#: The shape and font tokens, in light's :root only: they do not change with the scheme.
SHAPE_TOKENS = {"--radius-button", "--radius-frame", "--button-height", "--size-text", "--size-heading", "--size-title",
                "--space-s", "--space-m", "--space-l", "--body"}
#: Teal (the P1113 council's accent) and the tokens of its family, by name.
TEAL = "#0f766e"
TEAL_FAMILY = {"--accent", "--accent-hover", "--accent-edge", "--focus", "--now-halo"}
#: Where a teal token may stand, as (selector, property): a kind-1 button's fill and edge (the offer's own button and Send),
#: the confirm frame's edge, the focus ring, and the Now plane's halo (its dot and the edge of its offer button). Never a
#: text colour, a fill or a stroke.
TEAL_ROLES = {(selector, prop) for selector in ("[data-makes-stale]>button:not(:disabled)",
                                                "[data-makes-stale] [role=group]>button:first-of-type:not(:disabled)",
                                                "[data-makes-stale]>button:hover:not(:disabled)",
                                                "[data-makes-stale] [role=group]>button:first-of-type:hover:not(:disabled)")
              for prop in ("background", "border-color")} | {
    ("[data-makes-stale] [role=group]", "border-color"), ("a:focus-visible", "outline"), ("button:focus-visible", "outline"),
    ("summary:focus-visible", "outline"), (".now [data-makes-stale]>button", "border-color"),
    (".now [data-makes-stale]>button:hover", "border-color"), (".now>p:first-child::before", "border"),
    ('[data-need] label:has(:checked:not([value=""]):not(:disabled))', "border-color")}
#: (text, ground) pairs that a person reads: 4.5:1 in both themes. The outline button and the confirm box are ink on the
#: surface, the disabled label is muted on the line, and the Now link is the Now ink on the Now plane.
TEXT_PAIRS = [("--ink", "--bg"), ("--ink", "--surface"), ("--muted", "--bg"), ("--muted", "--surface"), ("--muted", "--line"),
              ("--on-accent", "--accent"), ("--on-accent", "--accent-hover"), ("--now-ink", "--now-bg"),
              ("--amber-ink", "--amber-plane"), ("--red-ink", "--red-plane")]
#: (edge, ground) pairs of a control or a ring: 3:1 in both themes. The kind-1 fill and Send on a frame or the ground, the
#: outline, the focus ring on each ground it can stand on, the Now dot and the Now button's edge, and the confirm frame.
EDGE_PAIRS = [("--accent", "--surface"), ("--accent", "--bg"), ("--ink", "--surface"), ("--focus", "--bg"), ("--focus", "--surface"),
              ("--focus", "--now-bg"), ("--now-halo", "--now-bg"), ("--accent-edge", "--surface"), ("--accent-edge", "--now-bg"),
              ("--accent-edge", "--bg")]  # P1135: the chosen pick's edge stands on its pale fill


def page_style(page):
    return re.search(r"<style>(.*?)</style>", page, re.S).group(1)


def themes(style):
    """The light tokens, and the dark ones: the light :root with the dark block over it, as a browser reads them."""
    light = token_block(r"^:root\{([^}]*)\}", style)
    return light, dict(light, **token_block(r':root\[data-theme="dark"\]\{([^}]*)\}', style))


def declarations(style):
    """(selector, property, value) of each declaration of the style outside the token blocks, once per selector of a list."""
    found = []
    for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", style):
        if selectors.startswith(":root"):
            continue
        for declaration in filter(None, body.split(";")):
            prop, _colon, value = declaration.partition(":")
            found += [(selector.strip(), prop.strip(), value.strip()) for selector in selectors.split(",")]
    return found


def luminance(colour):
    """The WCAG 2 relative luminance of a #rgb or #rrggbb colour."""
    value = colour.strip().lstrip("#")
    value = "".join(each * 2 for each in value) if len(value) == 3 else value
    channels = [int(value[at:at + 2], 16) / 255 for at in (0, 2, 4)]
    red, green, blue = [each / 12.92 if each <= 0.04045 else ((each + 0.055) / 1.055) ** 2.4 for each in channels]
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast(one, other):
    high, low = sorted((luminance(one), luminance(other)), reverse=True)
    return (high + 0.05) / (low + 0.05)


class TheLookTest(unittest.TestCase):
    """P949, P1120: the page's tokens, light and dark, with teal only on a button's fill, a frame's edge or a ring, no shadow,
    radii from their tokens, every pair readable, the linked font then the system's, nothing loaded by the style, and a
    legend of the pads under the breadboard that says only what the picture draws."""

    def setUp(self):
        self.page = page_of_wiring(PageWiring(THREE, [], ["rec"], None), THREE_PICTURES)
        self.style = page_style(self.page)

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
        page, style = self.page, self.style
        light = token_block(r"^:root\{([^}]*)\}", style)
        dark = token_block(r'@media \(prefers-color-scheme: dark\)\{:root:not\(\[data-theme="light"\]\)\{([^}]*)\}\}', style)
        self.assertEqual(dark, token_block(r':root\[data-theme="dark"\]\{([^}]*)\}', style))
        self.assertEqual((set(light), set(dark)), (COLOUR_TOKENS | SHAPE_TOKENS, COLOUR_TOKENS))
        self.assertIn("--radius-button", light)  # a name with a hyphen is read whole
        for name in ("--bg", "--surface", "--ink", "--muted", "--line"):
            self.assertNotEqual(light[name], dark[name], name)
        # the dark ground is the darker one, and a white ground under the pictures in both, which are drawn for a light one
        self.assertLess(luminance(dark["--bg"]), luminance(light["--bg"]))
        self.assertEqual((light["--backdrop"], dark["--backdrop"]), ("#fff", "#fff"))
        self.assertEqual(set(re.findall(r"var\((--[a-z-]+)\)", style)), set(light))
        outside = re.sub(r"\{[^{}]*--bg:[^{}]*\}", "{}", style)
        self.assertEqual(style.count("--bg:"), 3)
        self.assertNotRegex(outside, r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(")
        self.assertNotRegex(outside, r"(?:color|background|border-color):\s*(?!var\(|transparent|inherit)[a-z]+")
        for word in ("url(", "@import", "@font-face"):
            self.assertNotIn(word, page)

    def test_teal_is_only_a_button_fill_a_frame_edge_or_a_focus_ring(self):
        light, dark = themes(self.style)
        teal = TEAL_FAMILY | {name for theme in (light, dark) for name, value in theme.items() if value.strip().lower() == TEAL}
        self.assertEqual(teal, TEAL_FAMILY)  # a token that holds teal is one of the family, whatever its name
        used = [(selector, prop, value) for selector, prop, value in declarations(self.style)
                if any("var(%s)" % name in value for name in teal)]
        self.assertTrue(used)
        for selector, prop, value in used:
            self.assertNotIn(prop, ("color", "fill", "stroke"), selector)
            self.assertIn((selector, prop), TEAL_ROLES, "%s{%s:%s}" % (selector, prop, value))
            self.assertEqual(prop == "outline", "var(--focus)" in value, selector)  # the ring is --focus, and --focus only a ring

    def test_no_accent_fill_reaches_a_disabled_button_or_cancel(self):
        found = declarations(self.style)
        fills = [selector for selector, prop, value in found if prop == "background" and "var(--accent" in value]
        self.assertTrue(fills)
        for selector in fills:
            self.assertIn(":not(:disabled)", selector)
            if "[role=group]" in selector:  # Send is the confirm's first button; Cancel, the second, keeps the outline
                self.assertIn(">button:first-of-type", selector)
        rule = {(selector, prop): value for selector, prop, value in found}
        self.assertEqual((rule[("button:disabled", "background")], rule[("button:disabled", "color")]), ("var(--line)", "var(--muted)"))
        # while the confirm shows, the offer's own button is an outline again, so Send is the one teal button
        fallback = ("[data-makes-stale]:has(>[role=group])>button:not(:disabled)",
                    "[data-makes-stale]:has(>[role=group])>button:hover:not(:disabled)")
        for selector in fallback:
            self.assertEqual(rule[(selector, "background")], "var(--surface)", selector)
        self.assertEqual(rule[("button", "background")], "var(--surface)")

    def test_the_confirm_open_outline_never_styles_a_disabled_offer_and_stands_after_the_teal_rule(self):
        style = self.style
        found = declarations(style)
        # a disabled offer keeps the grey fill, whether or not the confirm is open: the fallback is for a button that can send
        for selector, prop, value in found:
            if ":has(" in selector and prop in ("background", "border-color", "color"):
                self.assertIn(":not(:disabled)", selector, selector)
        # the fill is the disabled rule's, and no Now rule paints a fill over it (the Now edge stays: see the style's comment)
        self.assertEqual([selector for selector, prop, _value in found if prop == "background" and ".now" in selector], [".now"])
        # the fallback outranks the teal rule by its place as well as by its weight, so the offer stays an outline
        self.assertGreater(style.index("[data-makes-stale]:has(>[role=group])>button:not(:disabled)"),
                           style.index("[data-makes-stale]>button:not(:disabled)"))
        self.assertGreater(style.index("[data-makes-stale]:has(>[role=group])>button:hover:not(:disabled)"),
                           style.index("[data-makes-stale]>button:hover:not(:disabled)"))
        rule = {(selector, prop): value for selector, prop, value in found}
        self.assertEqual((rule[("[role=group]", "color")], rule[("[role=group]", "background")]), ("var(--ink)", "var(--surface)"))

    def test_no_shadow_no_gradient_and_each_radius_is_a_token(self):
        found = declarations(self.style)
        for word in ("shadow", "gradient"):  # in a property or a value: box-shadow, filter:drop-shadow(...), a gradient
            self.assertEqual([(selector, prop) for selector, prop, value in found if word in prop or word in value], [])
        radii = [value for _selector, prop, value in found if "radius" in prop]
        self.assertTrue(radii)
        self.assertEqual({prop for _selector, prop, _value in found if "radius" in prop}, {"border-radius"})
        for value in radii:
            self.assertIn(value, ("var(--radius-button)", "var(--radius-frame)", "50%"))
        button = {prop: value for selector, prop, value in found if selector == "button"}
        self.assertEqual((button["border-radius"], button["min-height"]), ("var(--radius-button)", "var(--button-height)"))
        light, _dark = themes(self.style)
        self.assertGreaterEqual(int(light["--button-height"].rstrip("px")), 44)  # a finger's target
        self.assertLess(int(light["--radius-button"].rstrip("px")), int(light["--radius-frame"].rstrip("px")))

    def test_each_text_pair_meets_its_contrast_in_both_themes(self):
        for name, theme in zip(("light", "dark"), themes(self.style)):
            for pairs, floor in ((TEXT_PAIRS, 4.5), (EDGE_PAIRS, 3.0)):
                for one, other in pairs:
                    with self.subTest(theme=name, pair=(one, other)):
                        self.assertGreaterEqual(contrast(theme[one], theme[other]), floor)
        # the rules that set those pairs: the Now plane and its link, the confirm box, the Now button's edge
        rule = {(selector, prop): value for selector, prop, value in declarations(self.style)}
        for selector, prop, value in ((".now", "background", "var(--now-bg)"), (".now", "color", "var(--now-ink)"),
                                      (".now a", "color", "var(--now-ink)"), ("[role=group]", "color", "var(--ink)"),
                                      ("[role=group]", "background", "var(--surface)"),
                                      (".now [data-makes-stale]>button", "border-color", "var(--now-halo)")):
            self.assertEqual(rule.get((selector, prop)), value, selector)

    def test_nothing_inside_the_now_plane_is_muted_or_off_its_ink(self):
        box = re.search(r'<div class="now">(.*?)</div>', guide_page(a_guide()), re.S).group(1)
        inside = set(re.findall(r'class="([^"]+)"', box)) | {"now"}  # the classes the plane holds, and its own
        self.assertIn("next", inside)
        for selector, prop, value in declarations(self.style):
            if set(re.findall(r"\.([a-z-]+)", selector)) & inside:
                self.assertNotIn("var(--muted)", value, selector)  # --muted is for a light ground: 2.9:1 on the Now plane
                if prop == "color":
                    self.assertEqual(value, "var(--now-ink)", selector)

    def test_a_stale_or_problems_word_stands_on_its_plane_and_no_other_status_has_one(self):
        hues = {"stale": "amber", "problems": "red"}  # by hue, so the style names no status code
        rule = {(selector, prop): value for selector, prop, value in declarations(self.style)}
        for hue in hues.values():
            self.assertEqual((rule[(".plane-%s" % hue, "color")], rule[(".plane-%s" % hue, "background")]),
                             ("var(--%s-ink)" % hue, "var(--%s-plane)" % hue))
        for status in MARKS.keys() | {UNKNOWN_CODE}:
            with self.subTest(status=status):
                text = page_of(a_phase("parts", status))
                word = html.escape(word_of(status))
                spans = re.findall(r'<span(?: class="plane-([a-z]+)")?>%s</span>' % re.escape(word), text)
                self.assertEqual(spans, [hues.get(status, "")] * 2)  # the parts fold's summary and the developer fold's heading
                self.assertEqual(text.count('class="plane-'), 2 if status in hues else 0)
                self.assertIn('<span aria-hidden="true">%s</span>' % html.escape(shown_phase(a_phase("parts", status).to_dict()).mark), text)

    def test_the_confirm_reads_at_the_text_size_wherever_it_stands(self):
        # the confirm opens inside its offer's element, and on the NOW box's NEXT line it would take the line's larger size
        rule = {(selector, prop): value for selector, prop, value in declarations(self.style)}
        self.assertEqual(rule[(".next", "font-size")], "var(--size-heading)")
        self.assertEqual(rule[("[role=group]", "font-size")], "var(--size-text)")

    def test_the_font_is_the_linked_family_then_the_system_s(self):
        light, _dark = themes(self.style)
        family = re.search(r"family=([^:&]+)", FONT_URL).group(1).replace("+", " ")
        self.assertEqual(light["--body"], '"%s",%s' % (family, SYSTEM_FONTS))
        self.assertIn("display=swap", FONT_URL)  # with no network the system's fonts show at once
        self.assertEqual(self.page.count(html.escape(FONT_URL)), 1)
        rule = {(selector, prop): value for selector, prop, value in declarations(self.style)}
        self.assertEqual(rule[("strong", "font-weight")], "600")  # a weight the link loads, so none is made up

    def test_the_orange_signal_is_gone(self):
        self.assertNotIn("--signal", self.page)
        self.assertNotIn("#c8500f", self.page.lower())


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
        # power and ground go through the rails (P953): 12 steps, 10 of them jumpers
        self.assertEqual((text.count(FIGURE), text.count("data-step="), len(self.wiring.steps)), (1, 10, 12))
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
        assert_only_the_font_is_loaded(self, text)
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


class TheGuidingOrderTest(unittest.TestCase):
    """P828 step 2: the line under the title, the order with no sheet, the folded phases and the grouped lines before power."""

    def test_with_no_wiring_steps_the_phases_stay_folded_and_no_wiring_line_is_said(self):
        # P1062: with or without a sheet the phases stand closed in the developer fold, and the intro says no order
        for wiring in (PageWiring([], [], [], "no sheet yet"), None):
            text = page_of_wiring(wiring, THREE_PICTURES)
            self.assertNotIn("<details open><summary><h2>", developer(text))
            self.assertLess(text.index('<section id="pictures">'), text.index('id="phase-one"'))
            self.assertIn('<p class="intro">%s</p>' % html.escape(PAGE_INTRO), text)

    def test_a_link_to_the_wiring_or_the_pictures_targets_the_text_inside_its_fold_so_the_browser_opens_it(self):
        # A fragment inside a closed <details> (not its summary) opens it, with no script (HTML's ancestor revealing).
        text = page_of_wiring(PageWiring(THREE, [], [], None), THREE_PICTURES)
        for name in ("wiring", "pictures"):
            inside = text.split(fold(text, name))[1]
            self.assertLess(inside.index("</summary>"), inside.index('<section id="%s">' % name))
            self.assertLess(inside.index('<section id="%s">' % name), inside.index("</details>"))
        self.assertIn('<a href="#wiring">', text)
        self.assertIn('<a href="#pictures">', text)

    def test_the_intro_stands_under_the_freshness_line_and_above_the_folds(self):
        text = page_of_wiring(None, THREE_PICTURES)
        self.assertLess(text.index("</h1>"), text.index('class="fresh"'))
        self.assertLess(text.index('class="fresh"'), text.index(PAGE_INTRO))
        self.assertLess(text.index(PAGE_INTRO), text.index(fold(text, "pictures")))

    def test_every_phase_is_folded_closed_under_a_summary_that_holds_its_heading(self):
        text = page_of_wiring(PageWiring(THREE, [], [], None), THREE_PICTURES)
        sections = text.split('<section class="phase"')[1:]
        self.assertTrue(sections)
        for section in sections:
            body = section.split("</section>")[0]
            self.assertEqual(body.count("<details>"), 1)
            self.assertNotIn("<details open", body)
            self.assertLess(body.index("<details><summary><h2>"), body.index("</h2></summary>"))
            self.assertLess(body.index("</h2></summary>"), body.index("Done by:"))

    def test_host_requirements_of_one_part_stand_under_its_name_once_and_a_conflict_stands_alone(self):
        html_list = before_power.BeforePowerHtmlList()
        def item(kind, subject, said):
            return {"kind": kind, "subject": subject, "pin": "GPIO4", "record": "r", "said": said, "users": []}
        host, conflict = "host-requirement", "conflict"
        lines = html_list.items([item(host, "Panel", "one"), item(host, "Panel", "two"), item(conflict, "Panel", "short"),
                                 item(host, "Panel", "three"), item(host, "Other", "four")])
        self.assertEqual(lines[0], "<li><strong>Panel</strong><ul><li>one</li><li>two</li></ul></li>")
        signs = html_list.items([item(host, "A&B", "x < y"), item(host, "A&B", "z")])
        self.assertEqual(signs, ["<li><strong>A&amp;B</strong><ul><li>x &lt; y</li><li>z</li></ul></li>"])
        two_records = [dict(item(host, "Panel", "one"), record="a"), dict(item(host, "Panel", "two"), record="b")]
        self.assertEqual(html_list.items(two_records), ["<li>Panel: one</li>", "<li>Panel: two</li>"])
        self.assertIn("CONFLICT", lines[1])
        self.assertEqual(lines[2:], ["<li>Panel: three</li>", "<li>Other: four</li>"])


def a_guide(**changes):
    """A guide as `data.guide` holds it: a now with its sentence and no wiring steps, and the lists beside it."""
    guide = {"now": {"phase": "build", "by": ["claude"], "says": "Ask Claude to build the board.", "offer": "build", "needs": [],
                     "steps": None},
             "done": ["idea", "needs"], "later": ["firmware", "deploy"], "set_aside": ["stick"], "no_simulation": None}
    return dict(guide, **changes)


def guide_page(guide, wiring=None, phases=("one",)):
    """The text of FlowHtmlPage's page of these phases, with `guide` (P977 PR 2)."""
    page = FlowPage("t", [a_phase(name).to_dict() for name in phases], phases[0], [], [], wiring, None, None, guide)
    return FlowHtmlPage().text(page)


def guide_lines(text):
    """(the labelled lines of the page's guide section as (label, the rest of the line), the section's markup)."""
    section = text.split('<section id="guide">')[1].split("</section>")[0]
    return re.findall(r"<p[^>]*><strong>([^<]*)</strong> ?(.*?)</p>", section), section


class TheGuideSectionTest(unittest.TestCase):
    """P977 PR 2: the page draws data.guide under the intro and above the rail."""

    def test_the_guide_stands_between_the_intro_and_the_folds_with_the_hook_id(self):
        text = guide_page(a_guide())
        self.assertEqual(text.count('<section id="guide">'), 1)
        order = [text.index(mark) for mark in ('class="intro"', '<section id="guide">', '<section class="notes">', fold(text, "developer"))]
        self.assertEqual(order, sorted(order))

    def test_each_line_shows_its_items_in_order_and_an_empty_list_shows_no_line(self):
        # P1062: the NOW box (who acts, then NEXT), then the muted lines. P1119: the station line says what is done and
        # later, so the page draws no DONE or LATER line; SET ASIDE stays
        lines, _section = guide_lines(guide_page(a_guide()))
        self.assertEqual(lines, [("NOW (build), by claude", ""), ("NEXT", "Ask Claude to build the board."), ("SET ASIDE", "stick")])
        lines, _section = guide_lines(guide_page(a_guide(done=[], set_aside=[])))
        self.assertEqual([label for label, _rest in lines], ["NOW (build), by claude", "NEXT"])
        lines, _section = guide_lines(guide_page(a_guide(later=[])))
        self.assertEqual([label for label, _rest in lines], ["NOW (build), by claude", "NEXT", "SET ASIDE"])
        for gone in ("<strong>DONE</strong>", "<strong>LATER</strong>", "idea, needs", "firmware, deploy"):
            self.assertNotIn(gone, before_developer(guide_page(a_guide())))  # the developer fold holds them (P1119, D22)

    def test_no_simulation_is_its_own_line_under_later(self):
        text = guide_page(a_guide(simulation={"line": "No simulation: Wokwi has no model of this board.", "grey": True, "check": None}))
        _lines, section = guide_lines(text)
        self.assertIn('<p class="muted">No simulation: Wokwi has no model of this board.</p>', section)
        self.assertLess(section.index('<p class="next"'), section.index("No simulation: Wokwi"))  # P1119: LATER is gone
        self.assertLess(section.index("No simulation: Wokwi"), section.index("SET ASIDE"))
        self.assertNotIn("No simulation", guide_page(a_guide()))

    def test_the_simulation_line_is_grey_only_where_nothing_more_runs(self):
        """P1209 (D5): the page decides nothing: `grey` comes from the reading."""
        line = "Free checks, 27 Nov 2026, 02:10: imports: 6 of 6 imported."
        _lines, grey = guide_lines(guide_page(a_guide(simulation={"line": line, "grey": True, "check": None})))
        _lines, plain = guide_lines(guide_page(a_guide(simulation={"line": line, "grey": False, "check": None})))
        self.assertIn('<p class="muted">%s</p>' % line, grey)
        self.assertIn('<p class="simulation">%s</p>' % line, plain)
        self.assertNotIn('<p class="muted">Free checks', plain)
        self.assertLess(plain.index('<p class="next"'), plain.index(line))
        self.assertLess(plain.index(line), plain.index("SET ASIDE"))
        _lines, none = guide_lines(guide_page(a_guide(simulation={"line": None, "grey": False, "check": None})))
        self.assertNotIn('class="simulation"', none)

    def test_an_older_guide_with_no_simulation_key_draws_no_line(self):
        """An older page value (tests/data/flow-page/sample-page.json) has no `simulation` key: no line, no error."""
        text = guide_page(a_guide(no_simulation="No simulation: Wokwi has no model of this board."))
        self.assertNotIn("No simulation", text)
        self.assertNotIn('class="simulation"', text)

    def test_a_null_now_draws_no_now_line(self):
        lines, _section = guide_lines(guide_page(a_guide(now=None)))
        self.assertEqual([label for label, _rest in lines], ["SET ASIDE"])  # P1119: no DONE or LATER line
        self.assertNotIn("NOW", without_script(guide_page(a_guide(now=None))))
        self.assertNotIn('<div class="now">', guide_page(a_guide(now=None)))

    def test_the_step_link_shows_with_steps_in_now_and_wiring_steps_on_the_page(self):
        now = dict(a_guide()["now"], steps=3)
        wiring = PageWiring([(1, "Put the board in."), (2, "Run a jumper."), (3, "Run another.")], [], [], None)
        lines, section = guide_lines(guide_page(a_guide(now=now), wiring))
        self.assertEqual(lines[1], ("NEXT", 'Ask Claude to build the board. <a href="#step-1">One at a time: start at step 1</a>'))

    def test_the_step_link_goes_to_the_first_step_s_own_number(self):
        now = dict(a_guide()["now"], steps=2)
        wiring = PageWiring([(5, "Put the board in."), (6, "Run a jumper.")], [], [], None)
        self.assertIn('<a href="#step-5">One at a time: start at step 5</a>', guide_lines(guide_page(a_guide(now=now), wiring))[1])

    def test_no_step_link_without_steps_in_now_or_without_wiring_steps_on_the_page(self):
        wiring = PageWiring([(1, "Put the board in.")], [], [], None)
        for guide, shown in ((a_guide(), wiring), (a_guide(now=dict(a_guide()["now"], steps=4)), None),
                             (a_guide(now=dict(a_guide()["now"], steps=4)), PageWiring([], [], [], "no sheet yet"))):
            self.assertNotIn("One at a time", guide_lines(guide_page(guide, shown))[1])  # the wiring section has its own link

    def test_with_a_guide_the_stands_at_line_goes_and_without_one_it_stays(self):
        self.assertNotIn("The project stands at", guide_page(a_guide()))
        self.assertNotIn("No phase is open", guide_page(a_guide()))
        plain = guide_page(None)
        self.assertIn("<p>The project stands at: one.</p>", plain)
        self.assertNotIn('id="guide"', plain)

    def test_a_text_with_an_angle_bracket_or_an_ampersand_is_escaped(self):
        now = dict(a_guide()["now"], says="<b>go</b> & wait")
        # P1119: the page draws done and later as the station line, so the two words stand there as phases
        text = guide_page(a_guide(now=now, done=["<i>idea</i>"], later=["a&b"], set_aside=["<u>x</u>"], simulation={"line": "<s>none</s>", "grey": True, "check": None},
                                  stations=stations(("<i>idea</i>", "done", None), ("a&b", "later", None))))
        for raw in ("<b>go", "<i>idea", "<u>x", "<s>none", "a&b"):
            self.assertNotIn(raw, text)
        for escaped in ("&lt;b&gt;go&lt;/b&gt; &amp; wait", "&lt;i&gt;idea&lt;/i&gt;", "a&amp;b", "&lt;u&gt;x&lt;/u&gt;", "&lt;s&gt;none&lt;/s&gt;"):
            self.assertIn(escaped, text)
        # the PR review (lens 4): DONE and LATER stand in the developer fold, escaped there too
        self.assertIn("<strong>DONE</strong> &lt;i&gt;idea&lt;/i&gt;</p>", developer(text))
        self.assertIn("<strong>LATER</strong> a&amp;b</p>", developer(text))

    def test_a_chat_offer_in_now_draws_its_block_under_next_with_the_head_and_the_tell(self):
        # P1122 (D7): the head is bold text and the tell a code box, with the key for the owner's Copy and no hook that sends
        now = dict(a_guide()["now"], phase="deploy", offer=None, chat_offer="look-at-board")
        section = guide_lines(guide_page(a_guide(now=now)))[1]
        block = '<div class="ask" data-key="look-at-board"><strong>Ask Claude</strong> <code>Look at this project&#x27;s board with me.</code></div>'
        self.assertEqual(section.count('class="ask"'), 1)
        self.assertIn(block, section)
        self.assertLess(section.index('<p class="next"'), section.index(block))
        self.assertLess(section.index(block), section.index("</div>", section.index(block) + len(block)))
        self.assertNotIn("data-makes-stale", section)

    def test_no_chat_offer_or_no_key_for_it_draws_no_block(self):
        for now in (a_guide()["now"], dict(a_guide()["now"], chat_offer=None), dict(a_guide()["now"], chat_offer="needs-drop")):
            with self.subTest(now=now.get("chat_offer", "no key")):
                self.assertNotIn('class="ask"', guide_page(a_guide(now=now)))

    def test_the_guide_adds_no_script_and_loads_only_the_font(self):
        assert_spark_s_script_only(self, guide_page(a_guide(), PageWiring([(1, "x")], [], [], None)))


class TheGuideThroughWritePageTest(unittest.TestCase):
    """The guide is computed once in write_page, masked, drawn, and answered as Written.guide."""

    def test_a_phase_after_now_that_is_ok_says_it_may_change(self):
        # P977 PR 2 review: the rail says ok, so LATER must not list it as work still to do; a phase not ok has no suffix.
        store = FakeStore()
        written = write_page(Path(tempfile.mkdtemp()) / "project", readers_of(a_phase("one", "not-started"), a_phase("two", OK),
                                                                            a_phase("three", "not-started")), parts_of([]), store=store)
        self.assertEqual(written.guide["later"], ["two (done, may change)", "three"])
        # P1119: the page draws the station line, where two is later with its own tick and its note, and no LATER line
        self.assertIn('<li data-phase="two" data-place="later"><span class="mark" aria-hidden="true">✓</span><span class="name">two</span>'
                      '<span class="clip">: later, ok</span><span class="note">done, may change</span></li>', store.written[0][2])
        self.assertNotIn("<strong>LATER</strong>", before_developer(store.written[0][2]))  # the developer fold holds it (D22)

    def test_write_page_draws_the_guide_it_answers(self):
        store = FakeStore()
        written = write_page(Path(tempfile.mkdtemp()) / "project", readers_of(a_phase("one", OK), a_phase("two", "not-started")),
                             parts_of([]), store=store)
        text = store.written[0][2]
        self.assertEqual(text.count('<section id="guide">'), 1)
        self.assertEqual(written.guide["done"], ["one"])
        self.assertIn('<li data-phase="one" data-place="done">', text)  # P1119: the station line, no DONE line
        self.assertNotIn("<strong>DONE</strong>", before_developer(text))  # the developer fold holds it (D22)
        self.assertNotIn("The project stands at", text)

    def test_no_home_path_reaches_the_guide_on_the_page_or_in_what_is_answered(self):
        home = Path(tempfile.mkdtemp()).resolve()
        store = FakeStore()  # a phase's name reaches the guide's station line (P1119)
        with mock.patch.dict(os.environ, {"HOME": str(home), "SPARK_HOME": str(home / "store")}):
            written = write_page(Path(tempfile.mkdtemp()).resolve() / "project", readers_of(a_phase("read %s/secret" % home)),
                                 parts_of([]), store=store)
        self.assertNotIn(str(home), store.written[0][2])
        self.assertIn('<span class="name">read ~/secret</span>', store.written[0][2])
        self.assertEqual(written.guide["done"], ["read ~/secret"])


def stations(*rows):
    """The guide's `stations` (P1119) from (phase, place, note) rows."""
    return [{"phase": phase, "place": place, "note": note} for phase, place, note in rows]


def line_of(text):
    """The station line: its `<ol>` and the caption under it, or None with no line."""
    found = re.search(r'<ol class="stations".*?</ol>(?:\n<p class="stations-now"[^>]*>[^<]*</p>)?', text, re.S)
    return found.group(0) if found else None


def station_page(rows, phases=None, **changes):
    """The page of `phases` (Phase dicts; by default one per row, each not started) with a guide whose stations are `rows`."""
    phases = phases or [a_phase(phase, "not-started").to_dict() for phase, _place, _note in rows]
    page = FlowPage("t", phases, phases[0]["phase"], [], [], None, None, None, a_guide(stations=stations(*rows), **changes))
    return FlowHtmlPage().text(page)


#: The rows of the two jobs beside the firmware (P1119): the breadboard is now with the firmware, with no note.
TWO_JOBS = (("idea", "done", None), ("needs", "done", None), ("parts", "done", None), ("requirements", "done", None),
            ("build", "done", None), ("breadboard", "now", None), ("firmware", "now", None), ("simulate", "later", None),
            ("deploy", "later", None))


class TheStationLineTest(unittest.TestCase):
    """P1119: above the guide, one line of the stations the guide gives, as given: a mark and a plain name each, a ring on
    each now station, then spark's three unbuilt steps greyed. It uses only ink and muted, and on a phone the names hide."""

    def test_the_line_stands_after_the_intro_and_before_the_guide(self):
        text = station_page(TWO_JOBS)
        order = [text.index(mark) for mark in ('class="intro"', '<ol class="stations" aria-label="Where the project stands">',
                                               '<section id="guide">')]
        self.assertEqual(order, sorted(order))
        self.assertEqual(text.count('<ol class="stations"'), 1)

    def test_each_station_in_the_guide_s_order_with_its_place_mark_and_plain_name_then_the_three_unbuilt(self):
        parsed = Parsed(line_of(station_page(TWO_JOBS)))
        self.assertEqual([(attrs["data-phase"], attrs["data-place"]) for attrs, _said in parsed.rail],
                         [(phase, place) for phase, place, _note in TWO_JOBS])
        self.assertEqual([said for _attrs, said in parsed.rail],
                         ["○Idea: done, not started", "○Needs: done, not started", "○Parts: done, not started",
                          "○Parts list: done, not started", "○Board files: done, not started", "○Wiring: now, not started",
                          "○Firmware: now, not started", "○Simulation: later, not started", "○On the board: later, not started"])
        cells = re.findall(r'<li class="unbuilt" data-unbuilt="([a-z]+)">(.*?)</li>', line_of(station_page(TWO_JOBS)))
        self.assertEqual([(key, re.sub("<[^>]+>", "", inner)) for key, inner in cells],
                         [("perfboard", "Perfboard not built"), ("pcb", "PCB not built"), ("case", "Case not built")])
        line = line_of(station_page(TWO_JOBS))
        self.assertLess(line.index('data-phase="deploy"'), line.index('data-unbuilt="perfboard"'))

    def test_each_station_says_its_place_and_its_status_word_to_a_screen_reader_only(self):
        # the PR review (lens 1): the mark is hidden from a screen reader, so a clipped span says the place and the status
        phases = [a_phase("idea", OK).to_dict(), a_phase("needs", None).to_dict(), a_phase("parts", "stale").to_dict()]
        line = line_of(station_page((("idea", "done", None), ("needs", "now", None), ("parts", "later", None), ("ghost", "later", None)),
                                    phases=phases))
        said = dict(re.findall(r'<li data-phase="([a-z]+)"[^>]*>.*?<span class="clip">([^<]*)</span>', line))
        self.assertEqual(said, {"idea": ": done, ok", "needs": ": now, not checked by spark", "parts": ": later, out of date",
                                "ghost": ": later"})  # a station the page holds no phase of says its place only
        for _key, inner in re.findall(r'<li class="unbuilt" data-unbuilt="([a-z]+)">(.*?)</li>', line):
            self.assertEqual(re.findall(r'<span class="clip">([^<]*)</span>', inner), [" not built"])

    def test_an_unbuilt_cell_has_no_status_mark_and_says_not_built_to_a_screen_reader_only(self):
        for _key, inner in re.findall(r'<li class="unbuilt" data-unbuilt="([a-z]+)">(.*?)</li>', line_of(station_page(TWO_JOBS))):
            self.assertIn('<span class="mark"></span>', inner)
            self.assertIn('<span class="clip"> not built</span>', inner)
            self.assertFalse(set(inner) & {glyph for _word, glyph in MARKS.values()}, inner)

    def test_each_now_station_carries_the_ring_and_the_phone_caption_names_them(self):
        line = line_of(station_page(TWO_JOBS))
        current = re.findall(r'<li data-phase="([a-z]+)" data-place="now" aria-current="step">', line)
        self.assertEqual(current, ["breadboard", "firmware"])
        self.assertEqual(line.count("aria-current"), 2)
        self.assertIn('<p class="stations-now" aria-hidden="true">Wiring, Firmware</p>', line)
        one = line_of(station_page((("idea", "done", None), ("needs", "now", None), ("parts", "later", None))))
        self.assertEqual(re.findall(r'data-phase="([a-z]+)"[^>]*aria-current', one), ["needs"])
        self.assertIn('<p class="stations-now" aria-hidden="true">Needs</p>', one)

    def test_with_no_now_no_station_has_the_ring_and_there_is_no_caption(self):
        line = line_of(station_page((("idea", "done", None), ("simulate", "later", "no-model")), now=None))
        self.assertNotIn("aria-current", line)
        self.assertNotIn("stations-now", line)

    def test_the_mark_keeps_the_tick_guard_and_hides_from_a_screen_reader(self):
        liar = a_phase("idea", "stale", mark=TICK).to_dict()
        line = line_of(station_page((("idea", "done", None),), phases=[liar]))
        self.assertNotIn(TICK, line)
        self.assertIn('<span class="mark" aria-hidden="true">%s</span>' % MARKS[COULD_NOT_RUN][1], line)
        fine = line_of(station_page((("idea", "done", None),), phases=[a_phase("idea", OK).to_dict()]))
        self.assertIn('<span class="mark" aria-hidden="true">%s</span>' % TICK, fine)

    def test_a_phase_with_no_plain_name_shows_its_word_escaped(self):
        line = line_of(station_page((("bench-test", "now", None), ("<b>x</b>", "later", None))))
        self.assertIn('<span class="name">bench-test</span>', line)
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", line)
        self.assertNotIn("<b>x", line)

    def test_no_guide_or_a_guide_with_no_stations_draws_no_line(self):
        self.assertIsNone(line_of(guide_page(None)))
        self.assertIsNone(line_of(guide_page(a_guide())))  # an older page value has no stations
        self.assertIsNone(line_of(guide_page(a_guide(stations=[]))))

    def test_the_line_uses_ink_and_muted_and_no_teal_token(self):
        style = page_style(station_page(TWO_JOBS))
        rules = [(selector, prop, value) for selector, prop, value in declarations(style) if "stations" in selector or "unbuilt" in selector]
        self.assertTrue(rules)
        used = {name for _selector, _prop, value in rules for name in re.findall(r"var\((--[a-z-]+)\)", value)}
        self.assertEqual(used - {"--space-s", "--space-m", "--space-l"}, {"--ink", "--muted", "--bg"})
        self.assertFalse(used & TEAL_FAMILY)
        rule = {(selector, prop): value for selector, prop, value in rules}
        self.assertEqual(rule[(".stations [aria-current] .mark", "border-color")], "var(--ink)")  # the ring, on each now
        self.assertEqual(rule[(".stations>li::before", "border-top")], "2px solid var(--ink)")
        self.assertEqual(rule[('.stations>[data-place="later"]::before', "border-top")], "2px dashed var(--muted)")
        self.assertEqual(rule[(".stations>li:first-child::before", "content")], "none")

    def test_on_a_phone_the_names_are_clipped_the_marks_small_and_the_caption_shown(self):
        style = page_style(station_page(TWO_JOBS))
        phone = re.search(r"@media \(max-width: 600px\)\{((?:[^{}]+\{[^{}]*\})+)\}", style).group(1)
        rule = {(selector, prop): value for selector, prop, value in declarations(phone)}
        self.assertEqual((rule[(".stations .name", "position")], rule[(".stations .name", "clip")]), ("absolute", "rect(0 0 0 0)"))
        self.assertEqual((rule[(".stations .mark", "width")], rule[(".stations .mark", "height")]), ("14px", "14px"))
        self.assertEqual(rule[(".stations-now", "max-height")], "none")
        outside = {(selector, prop): value for selector, prop, value in declarations(style.replace(phone, ""))}
        self.assertEqual((outside[(".stations-now", "max-height")], outside[(".stations-now", "overflow")],
                          outside[(".stations-now", "white-space")]), ("0", "hidden", "nowrap"))

    def test_a_station_with_a_note_shows_its_words_under_its_name_and_a_left_out_note_shows_none(self):
        # the PO's "Visible note" (2026-11-25): the note's words stand on the line, small and muted
        rows = (("needs", "done", "not-done"), ("requirements", "done", "no-picks"), ("build", "done", "no-model"),
                ("breadboard", "done", "unseen"), ("firmware", "now", None), ("simulate", "later", "no-model"),
                ("deploy", "later", "may-change"))
        line = line_of(station_page(rows))
        cells = re.findall(r'<li data-phase="([a-z]+)"[^>]*>(.*?)</li>', line)
        notes = {phase: re.findall(r'<span class="note">([^<]*)</span>', inner) for phase, inner in cells}
        self.assertEqual(notes, {"needs": [], "requirements": ["no needs or picks behind it"], "build": ["no simulation"],
                                 "breadboard": ["spark cannot see it"], "firmware": [], "simulate": ["no Wokwi model of this board"],
                                 "deploy": ["done, may change"]})
        for _phase, inner in cells:  # under the name
            if "note" in inner:
                self.assertLess(inner.index('class="name"'), inner.index('class="note"'))
        self.assertNotIn('class="note"', line_of(station_page((("breadboard", "done", "no-sheet"), ("idea", "now", None)))))

    def test_the_note_is_muted_and_clipped_on_a_phone_with_the_names(self):
        style = page_style(station_page(TWO_JOBS))
        rule = {(selector, prop): value for selector, prop, value in declarations(style)}
        self.assertEqual(rule[(".stations .note", "color")], "var(--muted)")
        phone = re.search(r"@media \(max-width: 600px\)\{((?:[^{}]+\{[^{}]*\})+)\}", style).group(1)
        inside = {(selector, prop): value for selector, prop, value in declarations(phone)}
        for selector in (".stations .name", ".stations .note"):
            self.assertEqual((inside[(selector, "position")], inside[(selector, "clip")]), ("absolute", "rect(0 0 0 0)"), selector)

    def test_the_two_jobs_of_a_real_project_put_the_ring_on_wiring_and_firmware(self):
        from test_flow import a_project_built_with_no_simulation
        project = a_project_built_with_no_simulation()
        run_flow("page", "--project", str(project), "--json")
        line = line_of((project / "page.html").read_text(encoding="utf-8"))
        self.assertEqual(re.findall(r'data-phase="([a-z]+)" data-place="now" aria-current="step"', line), ["breadboard", "firmware"])
        self.assertEqual(re.findall(r'data-phase="([a-z]+)" data-place="later"', line), ["simulate", "deploy"])
        self.assertIn('<p class="stations-now" aria-hidden="true">Wiring, Firmware</p>', line)



class TheDeveloperGuideLinesTest(unittest.TestCase):
    """P1119, the PO's choice for D22: the developer fold writes the guide's DONE and LATER lines as the page wrote them, so
    every label of `flow.py show` stands in the page's text, and they stand nowhere else on the page."""

    def test_the_fold_holds_done_and_later_and_the_page_before_it_does_not(self):
        text = guide_page(a_guide(done=["idea", "requirements (no needs or picks behind it)"], later=["firmware", "deploy"]))
        fold_text = developer(text)
        self.assertIn('<p class="muted"><strong>DONE</strong> idea, requirements (no needs or picks behind it)</p>', fold_text)
        self.assertIn('<p class="muted"><strong>LATER</strong> firmware, deploy</p>', fold_text)
        self.assertLess(fold_text.index("<strong>DONE</strong>"), fold_text.index("<strong>LATER</strong>"))
        for gone in ("<strong>DONE</strong>", "<strong>LATER</strong>"):
            self.assertNotIn(gone, before_developer(text))

    def test_an_empty_list_or_no_guide_writes_no_line_in_the_fold(self):
        self.assertNotIn("<strong>DONE</strong>", developer(guide_page(a_guide(done=[]))))
        self.assertNotIn("<strong>LATER</strong>", developer(guide_page(a_guide(later=[]))))
        self.assertIn("<strong>LATER</strong>", developer(guide_page(a_guide(done=[]))))
        for gone in ("<strong>DONE</strong>", "<strong>LATER</strong>"):
            self.assertNotIn(gone, guide_page(None))

    def test_the_fold_s_lines_are_escaped(self):
        fold_text = developer(guide_page(a_guide(done=["<i>x</i>"], later=["a&b"])))
        self.assertIn("&lt;i&gt;x&lt;/i&gt;", fold_text)
        self.assertIn("a&amp;b", fold_text)
        self.assertNotIn("<i>x", fold_text)


class TheDeployedPageTest(unittest.TestCase):
    """P1043 (test 15): after a deploy that saw ready on the image the project holds now, the page says nothing waits, under
    the bench note. A partial deploy gets no tick. A guide with no `no_open_phase` key draws as before."""

    NOTHING_WAITS = ("Nothing is waiting on you: the last deploy started the image this project holds now. Tell Claude what "
                     "to change next.")

    def page(self, verdict, sentence):
        from test_flow import a_board_log, a_deploy_project
        project = a_board_log(a_deploy_project(), verdict, sentence)
        run_flow("page", "--project", str(project), "--json")
        return (project / "page.html").read_text(encoding="utf-8")

    def test_a_deployed_project_s_page_says_nothing_waits_under_the_bench_note(self):
        from test_flow import SEEN_SENTENCE
        text = self.page("ready seen", SEEN_SENTENCE)
        self.assertIn("<p>%s</p>" % html.escape(self.NOTHING_WAITS), text)
        self.assertEqual(text.count(html.escape(BENCH)), 1)
        self.assertIn('data-stands-at="none"', text)
        self.assertIn('data-phase="deploy" data-status="ok"', text)

    def test_a_partial_deploy_has_no_tick(self):
        from test_flow import FILES_UNREAD_SENTENCE
        text = self.page("ready unknown", FILES_UNREAD_SENTENCE)
        section = re.search(r'<section class="phase" data-phase="deploy" data-status="partial">.*?</section>', text, re.S).group(0)
        box = text.split('<div class="now">')[1].split("</div>")[0]
        self.assertIn('<p class="board"><strong>ON THE BOARD</strong> Last deploy ', box)  # P1062
        self.assertNotIn(TICK, box)
        for shown in (section,):
            self.assertNotIn(TICK, shown)
            self.assertIn("◐", shown)
        self.assertNotIn(self.NOTHING_WAITS, text)

    def test_a_guide_with_no_no_open_phase_key_draws_as_before(self):
        self.assertEqual(guide_page(a_guide(now=None)), guide_page(a_guide(now=None, no_open_phase=None)))
        self.assertIn("<p>said once</p>", guide_page(a_guide(now=None, no_open_phase="said once")))


def a_need_phase(says=("1 of 2 needs picked",), status="partial"):
    """A parts phase dict with two needs of two picks each, and a drop: the picks in the reading's order, and the needs
    (P1135), neither picked."""
    def pick(need, part):
        return {"key": "pick:%s:%s" % (need, part), "label": "Pick %s for %s" % (part, need), "effect": "Saves %s." % part,
                "makes_stale": ["requirements"], "part": part, "have": "in your drawer"}
    offers = [pick("light", "led-red"), pick("button", "tact-6mm"), pick("light", "led-green"), pick("button", "tact-12mm"),
              {"key": "needs-drop:light", "label": "Drop the light need", "effect": "Drops it.", "makes_stale": [], "part": None, "have": None}]
    needs = [{"need": need, "picked": [], "says": []} for need in ("light", "button")]
    return dict(a_phase("parts", status, says=says).to_dict(), offers=offers, needs=needs)


def order_page(guide=None, phases=None, wiring=PageWiring(THREE, [an_item()], ["rec"], None), deployed=None,
               written="2026-11-23T14:18:05+01:00", pictures=tuple(THREE_PICTURES)):
    """The text of FlowHtmlPage's page (P1062): by default the parts are NOW, with two needs and the build's offer."""
    build = {"key": "build", "label": "Build the board", "effect": "Builds it.", "makes_stale": []}
    phases = phases if phases is not None else [a_phase("idea", None).to_dict(), a_need_phase(),
                                                 dict(a_phase("build", "not-started").to_dict(), offers=[build])]
    now = {"phase": "parts", "by": ["you"], "says": "2 needs have no part yet.", "offer": None, "needs": ["light"], "steps": None}
    guide = guide if guide is not None else a_guide(now=now)
    return FlowHtmlPage().text(FlowPage("t", phases, "parts", list(pictures), ["The bench note."], wiring, None, written, guide,
                                        deployed))


def fold(text, name):
    """The `<details>` tag of the fold `name`."""
    return re.search(r'<details class="fold" data-fold="%s"[^>]*>' % name, text).group(0)


def before_developer(text):
    """The page before the developer fold."""
    return text[:text.index(fold(text, "developer"))]


def developer(text):
    """The developer fold, from its tag to the script block."""
    return text[text.index(fold(text, "developer")):text.index("<script")]


class TheSliceOneOrderTest(unittest.TestCase):
    """P1062: the slice 1 order (the P1038 design's mockup): the freshness line, one NOW box with ON THE BOARD and NEXT, the
    muted lines, three folds open only for their NOW, the bench note, and one developer fold, always closed, last."""

    ORDER = ["<h1>", 'class="fresh"', 'class="intro"', '<section id="guide">', '<div class="now">', 'class="muted"',
             'data-fold="parts"', 'data-fold="wiring"', 'data-fold="pictures"', 'class="notes"', 'data-fold="developer"']

    def setUp(self):
        in_prague(self)

    def test_the_order_is_the_same_with_a_sheet_without_one_and_with_no_steps(self):
        for wiring in (PageWiring(THREE, [], [], None), PageWiring([], [], [], "no sheet yet"), None):
            with self.subTest(wiring=wiring):
                text = without_script(order_page(wiring=wiring))
                marks = [mark for mark in self.ORDER if wiring or mark != 'data-fold="wiring"']
                order = [text.index(mark) for mark in marks]
                self.assertEqual(order, sorted(order))
                self.assertNotIn("<nav", text)

    def test_the_freshness_line_says_the_newest_change_in_the_machine_s_zone_and_keeps_the_iso_time(self):
        text = order_page(written="2026-11-23T14:18:05+01:00")
        # the review of #1619: the time the files last changed, so it never reads as the board's time
        self.assertIn('<p class="fresh">This page shows the project as its files last changed, 23 Nov 2026, 14:18. If you changed '
                      'or deployed something after that, type /spark:page in the chat.</p>', text)
        self.assertIn('data-written="2026-11-23T14:18:05+01:00"', text)
        self.assertNotIn("last changed,", order_page(written=None))
        self.assertIn('<p class="fresh">This page does not know when the project last changed.', order_page(written=None))

    def test_the_now_box_says_who_acts_on_the_board_and_next_with_its_hooks(self):
        build = dict(a_guide()["now"], by=["you", "claude"])
        text = order_page(guide=a_guide(now=build), deployed="Last deploy 23 Nov 2026, 14:09. Written by the flasher.")
        box = text.split('<div class="now">')[1].split("</div>")[0]
        lines = re.findall(r"<p[^>]*><strong>([^<]*)</strong> ?(.*?)</p>", box)
        self.assertEqual(lines, [("NOW (build), by you and claude", ""),
                                 ("ON THE BOARD", "Last deploy 23 Nov 2026, 14:09. Written by the flasher."),
                                 ("NEXT", "Ask Claude to build the board.")])
        self.assertIn('<p class="next" data-key="build" data-makes-stale=""><strong>NEXT</strong>', box)
        self.assertNotIn("ON THE BOARD", order_page(guide=a_guide(now=build)))
        nothing = order_page(guide=a_guide(now=None, no_open_phase="Nothing is waiting on you."))
        self.assertIn('<div class="now">\n<p>Nothing is waiting on you.</p>\n</div>', nothing)
        self.assertNotIn('<div class="now">', order_page(guide=a_guide(now=None)))

    def test_the_step_link_stands_on_the_next_line_with_steps_in_now(self):
        now = dict(a_guide()["now"], steps=3)
        box = order_page(guide=a_guide(now=now)).split('<div class="now">')[1].split("</div>")[0]
        self.assertIn('<a href="#step-1">One at a time: start at step 1</a></p>', box)

    def test_the_developer_lines_are_always_folded(self):
        deploy = {"phase": "deploy", "by": ["you"], "says": "Plug it in.", "offer": None, "needs": [], "steps": None}
        steps = dict(deploy, phase="firmware", steps=3, with_wiring=True)
        sheet = [a_phase("breadboard", None).to_dict(), a_need_phase()]
        for guide in (None, a_guide(now=deploy), a_guide(now=steps), a_guide(now=None, no_open_phase="Nothing waits.")):
            with self.subTest(guide=guide and guide["now"]):
                text = order_page(guide=guide, phases=sheet) if guide else order_page()
                self.assertNotIn(" open", fold(text, "developer"))
                inside = developer(text)
                self.assertEqual(re.findall(r"<details[^>]* open", inside), [])
                outside = text[:text.index(fold(text, "developer"))]
                for word in ('class="phase"', '<section class="legend">', "parts.py --show", "Done by:"):
                    self.assertIn(word, inside)
                    self.assertNotIn(word, outside)

    def test_no_tick_outside_the_script_for_a_status_that_is_not_ok(self):
        for status in ("partial", "could-not-run", None):
            with self.subTest(status=status):
                parts = dict(a_need_phase(status=status), mark=TICK)
                text = without_script(order_page(phases=[parts]))
                self.assertNotIn(TICK, re.sub(r'<section class="legend">.*?</section>', "", text))  # the legend names every mark
                self.assertIn(MARKS[COULD_NOT_RUN][1], fold(text, "parts") + text.split(fold(text, "parts"))[1].split("</summary>")[0])
        board = order_page(deployed="Last deploy 23 Nov 2026, 14:09. Written by the flasher.")
        line = re.search(r'<p class="board">.*?</p>', board).group(0)
        for _word, glyph in MARKS.values():
            self.assertNotIn(glyph, line)

    def test_the_parts_fold_opens_only_while_the_parts_are_now(self):
        self.assertIn(" open", fold(order_page(), "parts"))
        other = order_page(guide=a_guide())
        self.assertNotIn(" open", fold(other, "parts"))
        self.assertRegex(other, r'data-fold="parts"><summary><h2>[^\n]*</h2></summary>\n')

    def test_the_wiring_and_pictures_open_only_when_the_guide_s_now_holds_the_wiring(self):
        # the review of #1619: the reading says it (`now.with_wiring`, guide.py, E16); the page reads it and decides nothing
        deploy = dict(a_guide()["now"], phase="deploy", offer=None)
        sheet = [a_phase("breadboard", None).to_dict(), a_phase("deploy", "not-started").to_dict()]
        for guide, phases, shown in ((a_guide(now=dict(deploy, with_wiring=True)), sheet, True),
                                     (a_guide(now=dict(deploy, with_wiring=True)), [], True),
                                     (a_guide(now=dict(deploy, with_wiring=False)), sheet, False),
                                     (a_guide(now=dict(deploy, steps=3)), sheet, False), (a_guide(), sheet, False),
                                     (a_guide(now=None), sheet, False)):
            with self.subTest(now=guide["now"], phases=phases and [phase["status"] for phase in phases]):
                text = order_page(guide=guide, phases=phases)
                for name in ("wiring", "pictures"):
                    self.assertEqual(" open" in fold(text, name), shown, name)
                    self.assertRegex(text, r'data-fold="%s"( open)?><summary><h2>[^\n]*</h2></summary>\n' % name)

    def test_each_need_has_its_own_row_of_picks_in_the_reading_s_order_after_the_wired_line(self):
        wired = "You kept a wiring sheet on 22 Nov 2026. Each pick says what it changes."
        text = without_script(order_page(phases=[a_need_phase(says=(wired, "1 of 2 needs picked"))]))
        start = text.index(fold(text, "parts"))
        parts = text[start:text.index("</details>", start)]
        self.assertLess(parts.index(wired), parts.index("1 of 2 needs picked"))
        rows = re.findall(r'<li class="need"><strong>([^<]*)</strong><ul>(.*?)</ul></li>', parts)
        self.assertEqual([(need, re.findall(r'data-key="([^"]*)"', row)) for need, row in rows],
                         [("light", ["pick:light:led-red", "pick:light:led-green"]),
                          ("button", ["pick:button:tact-6mm", "pick:button:tact-12mm"])])
        self.assertLess(parts.index("1 of 2 needs picked"), parts.index('<li class="need">'))

    def test_a_sentence_the_parts_say_twice_stands_once_above_the_need_rows(self):
        # the review of #1619 (the lens): one refusal said for every need reads once
        said = "Spark can save no new pick: the board is held."
        text = without_script(order_page(phases=[a_need_phase(says=("1 of 2 needs picked", said, said))]))
        start = text.index(fold(text, "parts"))
        parts = text[start:text.index("</details>", start)]
        self.assertEqual(parts.count(said), 1)
        self.assertLess(parts.index(said), parts.index('<li class="need">'))
        self.assertLess(parts.index("1 of 2 needs picked"), parts.index(said))

    def test_each_sendable_button_stands_exactly_once_and_no_hook_stands_in_the_developer_fold(self):
        build = dict(a_guide()["now"], offer="build")
        for guide in (None, a_guide(now=build)):
            with self.subTest(now=guide and guide["now"]["offer"]):
                text = order_page(guide=guide) if guide else order_page()
                for key in ("pick:light:led-red", "pick:light:led-green", "pick:button:tact-6mm", "pick:button:tact-12mm", "build"):
                    self.assertEqual(text.count('data-key="%s"' % key), 1, key)
                self.assertNotIn("data-key", developer(text))
                self.assertNotIn("data-makes-stale", developer(text))
                self.assertNotIn('data-key="needs-drop:light"', text)
                self.assertIn("<code>needs-drop:light</code> Drop the light need: Drops it.", developer(text))
        self.assertIn('<p class="next" data-key="build"', order_page(guide=a_guide(now=build)))
        self.assertIn('<li data-key="build" data-makes-stale="">Build the board</li>', order_page())

    def test_each_need_row_carries_its_need_for_the_script_and_the_developer_fold_none(self):
        """P1067: the script groups a need's picks by the row's `data-need`, so a choice per need needs no rule of its own."""
        text = order_page()
        for need in ("light", "button"):
            self.assertEqual(text.count('<li class="need" data-need="%s"><strong>%s</strong><ul>' % (need, need)), 1, need)
        self.assertNotIn("data-need", developer(text))

    def test_a_pick_offer_s_words_hold_its_need_and_the_other_offers_none(self):
        """P1067: the Send of picks names their needs. P1135: a pick's radio is labelled by its row's text, so its words hold
        no part."""
        phase = a_need_phase()
        offers = page_words([phase, dict(a_phase("build").to_dict(), offers=[{"key": "build", "label": "Build the board",
                                                                              "effect": "Builds it.", "makes_stale": []}])])["offers"]
        self.assertEqual(offers["pick:light:led-red"], {"label": "Pick led-red for light", "says": [
            "Saves led-red.", "These steps may be marked out of date: requirements."], "need": "light"})
        self.assertEqual(offers["pick:button:tact-6mm"]["need"], "button")
        self.assertEqual(offers["build"], {"label": "Build the board", "says": ["Builds it."]})

    def test_the_words_of_several_picks_are_python_s(self):
        """P1067: the words of the radios, the Send of picks, its box, its wait and its answers, written by Python."""
        words = page_words([])
        self.assertEqual({name: words[name] for name in ("not_now", "picks_said", "send_picks", "choose_first", "picks_together",
                                                          "waiting_picks", "ok_picks", "last_request_picks", "needs_join", "label_join",
                                                          "no_pick_saved")},
                         {"not_now": "not now", "picks_said": ["%d pick (%s)", "%d picks (%s)"], "send_picks": "Send %s",
                          "choose_first": "Choose a part first.",
                          "picks_together": "Spark checks the picks together. If one fails, spark saves none.",
                          "waiting_picks": "Sent at %s: %s. Nothing has run yet. To run it, type /spark:page in Claude Code.",
                          "ok_picks": "Saved as the picks. Nothing is built yet. Reload to see the new state.",
                          "last_request_picks": "your picks", "needs_join": ", ", "label_join": ": ",
                          "no_pick_saved": "No pick was saved."})
        not_offered = "the request names a step that spark does not offer now, so nothing ran"
        self.assertEqual(words["refused_picks"], dict(words["refused"], **{
            not_offered: "Nothing ran. Spark no longer offers one of these picks. Reload this page."}))
        self.assertEqual(words["refused"][not_offered], "Nothing ran. This button is no longer offered. Reload the page.")

    def test_the_need_of_a_pick_offer_s_key(self):
        from spark.flow.phase_readers import pick_need
        self.assertEqual(pick_need("pick:light:led-red-5mm"), "light")
        self.assertEqual(pick_need("pick:light:drawer:7"), "light")
        for key in ("build", "needs-drop:light", "requirements", "pick"):
            self.assertIsNone(pick_need(key), key)


def wired_effect(own):
    """A pick's effect on a wired board of an unlisted project, as the parts reader writes it (P1135): its own sentences
    between the three that every pick of the project says."""
    return " ".join([WIRED_PICK, own] + SHARED[1:])


def a_picked_phase():
    """A parts phase dict (P1135): button picked “Tactile 6 mm”, with one more pick and a line of its own, and board not
    picked, with a pick spark has no board file for and one it has."""
    def pick(need, part, name, effect):
        return {"key": "pick:%s:%s" % (need, part), "label": "Pick “%s” for %s" % (name, need), "effect": effect,
                "makes_stale": ["requirements"], "part": name, "have": "in your drawer"}
    offers = [pick("button", "tact-12mm", "Tactile 12 mm", wired_effect("Saves “Tactile 12 mm” as the pick.")),
              pick("board", "beetle", "Beetle", wired_effect("Saves “Beetle” as the pick. Spark cannot build from this pick: it has no board file for “Beetle”.")),
              dict(pick("board", "c6", "XIAO C6", wired_effect("Saves “XIAO C6” as the pick.")), have="to get")]
    needs = [{"need": "button", "picked": ["Tactile 6 mm"], "says": ["Not shown for button: 1 more pick."]},
             {"need": "board", "picked": [], "says": []}]
    return dict(a_phase("parts", "partial", says=("1 of 2 needs picked",)).to_dict(), offers=offers, needs=needs)


def parts_fold(text):
    """The parts fold, from its tag to its end."""
    start = text.index(fold(text, "parts"))
    return text[start:text.index("</details>", start)]


class TheLessTextTest(unittest.TestCase):
    """P1135 (the PO: "its still way too much text"; "clearly see on the page" what is picked): a picked need's row says its
    pick with a tick, each pick's row its part and what you have of it, and a step's effect stands in its Send box and in
    the developer fold only."""

    def setUp(self):
        in_prague(self)
        build = {"key": "build", "label": "Build the board", "effect": "Builds it.", "makes_stale": [], "part": None, "have": None}
        self.text = order_page(phases=[a_picked_phase(), dict(a_phase("build", "not-started").to_dict(), offers=[build])])
        self.parts = parts_fold(self.text)

    def test_a_picked_need_s_row_says_its_pick_before_its_offers_and_its_lines_after_them(self):
        self.assertIn('<li class="need" data-need="button"><strong>button</strong><p class="picked" id="picked-button">'
                      '<span aria-hidden="true">✓</span> picked “Tactile 6 mm”.</p><ul><li data-key="pick:button:tact-12mm" '
                      'data-makes-stale="requirements">Tactile 12 mm (in your drawer)</li></ul><p class="muted">Not shown for button: '
                      '1 more pick.</p></li>', self.parts)
        self.assertIn('<li class="need" data-need="board"><strong>board</strong><ul>', self.parts)
        self.assertNotIn("picked-board", self.text)

    def test_the_fold_s_top_keeps_only_the_phase_s_lines(self):
        top = self.parts[:self.parts.index("<ul>")]
        self.assertEqual(re.findall(r"<p>([^<]*)</p>", top), ["1 of 2 needs picked"])
        self.assertEqual(self.parts.count("Not shown for button"), 1)

    def test_a_pick_s_row_reads_its_part_and_what_you_have_and_keeps_its_board_file_line(self):
        self.assertIn('<li data-key="pick:board:beetle" data-makes-stale="requirements">Beetle (in your drawer)<p class="muted">'
                      'Spark cannot build from this pick: it has no board file for “Beetle”.</p></li>', self.parts)
        self.assertIn('<li data-key="pick:board:c6" data-makes-stale="requirements">XIAO C6 (to get)</li>', self.parts)
        for said in ("Saves “Beetle”", html.escape(WIRED_PICK), MAY_NOTE):
            self.assertNotIn(said, before_developer(self.text))

    def test_the_parts_list_s_and_the_build_s_rows_hold_their_label_alone(self):
        offer = {"key": "requirements", "label": "Write the parts list", "effect": "Writes it.", "makes_stale": ["build"]}
        text = order_page(phases=[dict(a_phase("requirements", "not-started").to_dict(), offers=[offer])], guide=a_guide())
        self.assertIn('<li data-key="requirements" data-makes-stale="build">Write the parts list</li>', text)
        self.assertIn('<li data-key="build" data-makes-stale="">Build the board</li>', self.parts)
        self.assertNotIn("Writes it.", before_developer(text))
        self.assertNotIn("Builds it.", before_developer(self.text))

    def test_the_developer_fold_keeps_every_key_label_and_effect_and_a_pick_s_have(self):
        inside = developer(self.text)
        beetle = a_picked_phase()["offers"][1]
        self.assertIn("<li><code>pick:board:beetle</code> Pick “Beetle” for board (in your drawer): %s</li>" % html.escape(beetle["effect"]),
                      inside)
        self.assertIn("<li><code>build</code> Build the board: Builds it.</li>", inside)

    def test_a_pick_s_send_box_says_the_shared_lines_apart_and_keep_names_a_picked_need_s_part(self):
        words = page_words([a_picked_phase()])
        self.assertEqual(words["offers"]["pick:board:c6"]["says"], [
            WIRED_PICK, "Saves “XIAO C6” as the pick."] + SHARED[1:] + ["These steps may be marked out of date: requirements."])
        self.assertEqual(words["keep"], {"button": "keep “Tactile 6 mm”"})
        self.assertEqual(page_words([a_need_phase()])["keep"], {})


class TheNowBoxAtThePartsTest(FlowTest):
    """P1135 (council P1251: "a line count for NOW is pinned"): at the parts moment the NOW box holds two lines, who acts and
    NEXT, whose sentence is two sentences."""

    def test_the_now_box_holds_two_lines_at_the_parts_moment(self):
        project = with_needs(Path(tempfile.mkdtemp()) / "plant-alarm", SOIL + [{"id": "wet", "does": "sense", "what": "soil-moisture"}])
        run_flow("page", "--project", str(project), "--json")
        text = (project / "page.html").read_text(encoding="utf-8")
        box = text.split('<div class="now">')[1].split("</div>")[0]
        self.assertEqual(len(re.findall(r"<p[ >]", box)), 2, box)
        self.assertIn("2 needs have no part yet: soil, wet. Pick a part for each, or ask Claude to set one aside.", box)


class TheSectionsTest(unittest.TestCase):
    """P1123: page.html is an ordered table of small Renderers, so that a later part of the page is one more section."""

    def test_the_page_s_sections_stand_in_this_order(self):
        # a literal list, the slice 1 order (P1062): a section that moves or goes fails here, whatever SECTIONS holds
        self.assertEqual([section.NAME for section in FlowHtmlPage.SECTIONS],
                         ["title", "fresh", "intro", "stations", "guide", "stands-at", "parts", "wiring", "pictures", "notes",
                          "developer"])


def sample_page():
    """The FlowPage of tests/data/flow-page/sample-page.json: an offer of each kind, a guide, wiring and two pictures."""
    sample = json.loads((SAMPLE / "sample-page.json").read_text(encoding="utf-8"))
    return FlowPage(sample["title"], sample["phases"], sample["stands_at"], [Picture(*each) for each in sample["pictures"]],
                    tuple(sample["notes"]), PageWiring(*sample["wiring"]), sample["fingerprint"], sample["written"], sample["guide"])


def words_of(text):
    """The words block of a page, read as JSON."""
    return json.loads(scripts_of(text)[0][1])


class ThePageScriptTest(unittest.TestCase):
    """P829 PR 3: the page holds one inert words block and one script; without them it is the page before the script."""

    def setUp(self):
        in_prague(self)  # P1062: the freshness line reads the time in the machine's zone
        self.text = FlowHtmlPage().text(sample_page())

    def test_the_page_without_its_script_is_the_page_before_the_script_byte_for_byte(self):
        self.assertEqual(without_script(self.text), (SAMPLE / "before-script.html").read_text(encoding="utf-8"))
        self.assertEqual(self.text.count(PAGE_SCRIPT), 1)
        self.assertLess(self.text.index("<script>"), self.text.index("</body>"))

    def test_only_a_pick_the_parts_list_and_the_build_carry_data_makes_stale(self):
        self.assertIn('<li data-key="pick:light:led-red-5mm" data-makes-stale="requirements">', self.text)
        self.assertIn('<li data-key="requirements" data-makes-stale="build breadboard">', self.text)
        self.assertIn('<li data-key="build" data-makes-stale="">', self.text)
        self.assertIn('<li><code>needs-drop:light</code> Drop the light need: ', self.text)  # P1062: in the developer fold, no hook
        self.assertNotIn('data-key="needs-drop', self.text)

    def test_the_words_block_holds_each_sendable_offer_s_confirm_and_no_drop(self):
        words = words_of(self.text)
        self.assertEqual(sorted(words["offers"]), ["build", "pick:light:led-red-5mm", "requirements"])
        self.assertEqual(words["offers"]["requirements"], {"label": "Write the parts list", "says": [
            "Writes the parts list, requirements.json, from your picks. Parts you wrote there yourself stay.",
            "These steps may be marked out of date: build, breadboard."]})
        self.assertEqual(words["offers"]["build"]["says"], ["Saves its files in this project. Runs no simulation and costs nothing."])
        self.assertEqual(words["offers"]["pick:light:led-red-5mm"]["label"], "Pick “Red LED 5 mm” for light")

    def test_the_words_block_holds_the_plan_s_words_and_never_done_alone(self):
        words = words_of(self.text)
        self.assertEqual(words, page_words(sample_page().phases))
        self.assertEqual(page_words([])["intro"], "Where this project stands. Use a button to ask spark for a step; Claude runs it at your next /spark:page.")
        # P993: where the script adds the NOW button, it puts the step and "Use the button." in place of the sentence
        # that names Claude; the page from disk and `flow.py show` keep that sentence
        self.assertEqual(page_words([])["now_button"], {
            "Ask Claude in the chat to write the parts list from your picks.": "Write the parts list from your picks. Use the button.",
            "Your picks changed. Ask Claude to write the parts list again.": "Your picks changed. Write the parts list again. Use the button.",
            "The parts list was changed by hand. Writing it again keeps its parts and puts back what your picks give. "
            "Ask Claude to write it again, or to change your picks first.":
                "The parts list was changed by hand. Writing it again keeps its parts and puts back what your picks give. Use the button.",
            "The parts list differs from what your picks give. Ask Claude to write it from your picks.":
                "The parts list differs from what your picks give. Write it from your picks. Use the button.",
            "Ask Claude in the chat to build the board. It takes seconds and costs nothing.":
                "Build the board. It takes seconds and costs nothing. Use the button.",
            "The parts list changed since the last build. Ask Claude to build again.":
                "The parts list changed since the last build. Build the board again. Use the button."})
        self.assertEqual(words["waiting"], "Sent at %s. Nothing has run yet. To run it, type /spark:page in Claude Code.")
        self.assertEqual((words["copy"], words["copied"]), ("Copy", "Copied: paste it in Claude Code."))  # P1122: a chat offer's Copy
        self.assertEqual(words["ok"], {
            "pick": "Saved as the pick. Nothing is built yet. Reload to see the new state.",
            "requirements": "The parts list is written. Nothing is built yet. Reload to see the new state.",
            "build": "The board builds. It is not wired, not flashed and not simulated yet. Reload to see the new state."})
        # P1062: no wiring sentence in the intro, and the last request's line with its month words
        self.assertEqual(words["intro"], "Where this project stands. Use a button to ask spark for a step; Claude runs it at your next "
                                         "/spark:page.")
        self.assertEqual((words["last_request"], words["months"][0], words["months"][10], len(words["months"])),
                         ("Your last request, %s: %s.", "Jan", "Nov", 12))
        # the review of #1619: a request whose offer left the page is said by its kind's words, never by a part of its key
        self.assertEqual(words["request_kinds"], {"pick": "a pick", "requirements": "the parts list", "build": "the build"})
        self.assertEqual(words["request_other"], "a step this page no longer offers")
        self.assertNotIn("page_from", words)
        self.assertEqual((words["not_sent"], words["not_withdrawn"]), ("Could not send. Nothing ran.", "Could not withdraw. The request still waits."))
        self.assertEqual(words["refused"], {
            "the project changed after the page was read, so nothing ran":
                "Nothing ran. The project changed after you clicked. Reload this page and click again.",
            "the request names a step that spark does not offer now, so nothing ran":
                "Nothing ran. This button is no longer offered. Reload the page.",
            "the request names a step that is asked in the chat, never from the page, so nothing ran":
                "Nothing ran. This step is asked in the chat: tell Claude.",
            "the request file is missing, is no regular file or no JSON object, holds an id, key or seen that cannot be read, or "
            "could not be deleted, so nothing ran": "Nothing ran. The request could not be read. Reload the page and click again."})
        self.assertEqual(words["marks"], {"ok": "✓", "problems": "✗", "could-not-run": "?", "not-run": "–"})
        said = [words[name] for name in ("send", "cancel", "copy", "withdraw", "withdrawn", "waiting_for", "last_request", "ran",
                                         "problems", "could_not_run")] + list(words["ok"].values()) + list(words["refused"].values())
        self.assertEqual(said[:7], ["Send", "Cancel", "Copy", "Withdraw", "Withdrawn. If Claude had already started it, its answer shows here.",
                                    "Waiting for Claude: %s.", "Your last request, %s: %s."])
        for line in said:
            self.assertNotEqual(line.strip(". ").lower(), "done")
        self.assertNotIn("0123456789ab", json.dumps(words))

    def test_the_now_line_carries_the_key_of_its_phase_s_one_sendable_offer(self):
        page = sample_page()
        # P1030: the page reads the guide's one now offer
        self.text = FlowHtmlPage().text(page._replace(guide=dict(page.guide, now=dict(page.guide["now"], offer="pick:light:led-red-5mm"))))
        # P1062 (E17): the button stands on the NOW box's NEXT line only, so the key stands once
        self.assertIn('<p class="next" data-key="pick:light:led-red-5mm" data-makes-stale="requirements"><strong>NEXT</strong> ', self.text)
        self.assertEqual(self.text.count('data-key="pick:light:led-red-5mm"'), 1)

    def test_the_now_line_carries_no_key_with_two_sendable_offers_or_none(self):
        page = sample_page()
        two = [dict(phase, offers=phase["offers"] + [dict(phase["offers"][0], key="pick:light:led-green")]) if phase["phase"] == "parts"
               else phase for phase in page.phases]
        for phases in (two, [phase for phase in page.phases if phase["phase"] != "parts"]):
            with self.subTest(len(phases)):
                text = FlowHtmlPage().text(page._replace(phases=phases))
                self.assertIn('<p class="next"><strong>NEXT</strong> ', text)

    def test_a_label_with_markup_cannot_close_the_words_block(self):
        phase = a_phase("build", offers=[Offer("build", "</script><script>alert(1)</script>", "x", (), build_step("project"))])
        text = FlowHtmlPage().text(FlowPage("t", [phase.to_dict()], None, [], []))
        self.assertEqual(len(scripts_of(text)), 2)
        self.assertEqual(words_of(text)["offers"]["build"]["label"], "</script><script>alert(1)</script>")
        self.assertIn("\\u003c/script>\\u003cscript>alert(1)", text)


class ThePublishedPageTest(unittest.TestCase):
    """P829 PR 4: `flow.py page --artifact ID` keeps the id of the Artifact the page is published as in .spark/page.json,
    the id only and never a path, and every `flow.py page` reads it back as data.artifact."""

    ARTIFACT = "cd9a5ac3-f053-4a6a-bc9c-ab6f687f4096"

    def page(self, project, *argv):
        with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
            return run_flow("page", "--project", str(project), "--json", *argv)

    def test_the_artifact_is_kept_as_its_id_only_and_read_back(self):
        project = a_built_project()
        envelope, code = self.page(project, "--artifact", self.ARTIFACT)
        self.assertEqual((code, envelope["data"]["artifact"]), (0, self.ARTIFACT))
        text = (project / ".spark" / "page.json").read_text(encoding="utf-8")
        self.assertEqual(json.loads(text), {"artifact": "cd9a5ac3-f053-4a6a-bc9c-ab6f687f4096"})
        self.assertNotIn(str(project.name), text)
        self.assertNotIn("/", text)
        again, code = self.page(project)
        self.assertEqual((code, again["data"]["artifact"]), (0, "cd9a5ac3-f053-4a6a-bc9c-ab6f687f4096"))

    def test_a_page_never_published_answers_no_artifact_and_writes_no_record(self):
        project = a_built_project()
        envelope, code = self.page(project)
        self.assertEqual((code, envelope["data"]["artifact"]), (0, None))
        self.assertEqual(sorted(envelope["data"]), ["artifact", "did", "file", "fingerprint", "guide", "phases", "stands_at"])
        self.assertFalse((project / ".spark" / "page.json").exists())

    def test_an_id_that_is_no_uuid_is_a_bad_argument_and_writes_nothing(self):
        for given in ("../page.html", "/tmp/x/index.html", "CD9A5AC3-F053-4A6A-BC9C-AB6F687F4096", "",
                      "cd9a5ac3-f053-4a6a-bc9c-ab6f687f4096\n"):
            with self.subTest(given=given):
                project = a_built_project()
                envelope, code = self.page(project, "--artifact", given)
                self.assertEqual((code, envelope["status"]), (2, COULD_NOT_RUN))
                self.assertEqual([item["code"] for item in envelope["unchecked"]], ["bad_argument"])
                self.assertFalse((project / ".spark" / "page.json").exists())
                self.assertFalse((project / "page.html").exists())

    def test_a_record_spark_cannot_use_answers_no_artifact(self):
        for held in ("not json", '{"artifact": "/tmp/x"}', '["cd9a5ac3-f053-4a6a-bc9c-ab6f687f4096"]', '{"artifact": 5}',
                     '{"artifact": "cd9a5ac3-f053-4a6a-bc9c-ab6f687f4096\\n"}'):
            with self.subTest(held=held):
                project = a_built_project()
                (project / ".spark" / "page.json").write_text(held, encoding="utf-8")
                envelope, code = self.page(project)
                self.assertEqual((code, envelope["data"]["artifact"]), (0, None))

    def test_a_new_id_replaces_the_old_one(self):
        project = a_built_project()
        self.page(project, "--artifact", self.ARTIFACT)
        self.page(project, "--artifact", "9667a2de-3d30-4c7f-a7fc-9ded96a0e967")
        self.assertEqual(json.loads((project / ".spark" / "page.json").read_text(encoding="utf-8")),
                         {"artifact": "9667a2de-3d30-4c7f-a7fc-9ded96a0e967"})


FAILED_ROW = "A run failed on this image (one.log)."
TESTED_ROW = '<p class="tested"><strong>TESTED BEFORE THE BOARD</strong> %s</p>'


class TheTestedBeforeTheBoardRowTest(unittest.TestCase):
    """P1220: the NOW box prints gate A's row from `guide.gate_a`'s `says`, the same words as `flow.py show`, and decides nothing."""

    def box(self, **changes):
        return order_page(**changes).split('<div class="now">')[1].split("</div>")[0]

    def test_the_now_box_holds_the_row_after_on_the_board_and_before_next(self):
        now = dict(a_guide()["now"], by=["claude"])
        gate_a = {"shut_by": ["run-failed"], "fact": "run-failed", "says": FAILED_ROW}
        box = self.box(guide=a_guide(now=now, gate_a=gate_a), deployed="Last deploy 23 Nov 2026, 14:09. Written by the flasher.")
        self.assertIn(TESTED_ROW % FAILED_ROW, box)
        marks = [box.index(mark) for mark in ('<strong>ON THE BOARD</strong>', "<strong>TESTED BEFORE THE BOARD</strong>", '<strong>NEXT</strong>')]
        self.assertEqual(marks, sorted(marks))

    def test_with_no_now_the_row_stands_after_the_line_that_says_nothing_is_open(self):
        gate_a = {"shut_by": [], "fact": "image-tested", "says": "A run passed on this image."}
        box = self.box(guide=a_guide(now=None, no_open_phase="Nothing is waiting on you.", gate_a=gate_a))
        self.assertEqual(box.split("\n")[1:3], ["<p>Nothing is waiting on you.</p>", TESTED_ROW % "A run passed on this image."])

    def test_a_null_gate_a_and_a_guide_with_no_gate_a_draw_no_row(self):
        for guide in (a_guide(gate_a=None), a_guide(), a_guide(now=None, no_open_phase="Nothing waits.", gate_a=None)):
            with self.subTest(guide=guide["now"]):
                self.assertNotIn("TESTED BEFORE THE BOARD", order_page(guide=guide))

    def test_a_null_shut_by_is_a_row_and_is_printed(self):
        """A null `shut_by` is not a null `gate_a`: spark cannot tell, and the page says so."""
        gate_a = {"shut_by": None, "fact": None, "says": "Spark cannot tell. The simulation phase says why."}
        self.assertIn(TESTED_ROW % "Spark cannot tell. The simulation phase says why.", self.box(guide=a_guide(gate_a=gate_a)))

    def test_the_page_and_show_print_the_same_row(self):
        from test_flow import a_project_at_the_board, lines_of
        project = a_project_at_the_board()
        run_flow("page", "--project", str(project), "--json")
        text = (project / "page.html").read_text(encoding="utf-8")
        self.assertIn(TESTED_ROW % FAILED_ROW, text)
        self.assertIn("  TESTED BEFORE THE BOARD: " + FAILED_ROW, lines_of(project))


if __name__ == "__main__":
    unittest.main()
