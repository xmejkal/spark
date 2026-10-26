"""
The page (P271, #307): page.html, the breadboard, schematic and PCB in three tabs, each picture in its own <img>.

    python3 -m unittest tests.test_tabbed_page
"""

import base64
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401
from suite_runs import slow  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import tabbed_page  # noqa: E402
from tabbed_page import SvgExportResult, Tab, TabbedHtmlPage, TscircuitExport  # noqa: E402

SVG = '<svg xmlns="http://www.w3.org/2000/svg"><style>.boundary{fill:beige}</style><rect class="boundary"/></svg>'
CIRCUIT = ROOT / "tests" / "data" / "breadboard" / "button-light-xiao" / "dist" / "board" / "circuit.json"


def three_tabs(schematic=SVG):
    return [Tab("Breadboard", SVG, None), Tab("Schematic", schematic, None), Tab("PCB", SVG, None)]


def pictures(page):
    return [base64.b64decode(data).decode("utf-8") for data in re.findall(r'data:image/svg\+xml;base64,([^"]+)', page)]


class TabbedHtmlPageTest(unittest.TestCase):
    def test_three_tabs_give_one_page_with_three_pictures(self):
        page = TabbedHtmlPage().text(three_tabs())
        self.assertEqual(3, page.count('type="radio"'))
        self.assertEqual(["Breadboard", "Schematic", "PCB"], re.findall(r'<label for="tab\d">([^<]+)</label>', page))
        self.assertEqual([SVG] * 3, pictures(page))
        self.assertIn('<meta charset="utf-8">', page)

    def test_no_svg_is_pasted_inline_so_its_styles_stay_in_its_picture(self):
        page = TabbedHtmlPage().text(three_tabs())
        self.assertNotIn("<svg", page)
        self.assertNotIn(".boundary", page)
        self.assertTrue(all('xmlns="http://www.w3.org/2000/svg"' in svg for svg in pictures(page)))

    def test_the_page_loads_nothing_and_runs_nothing(self):
        page = TabbedHtmlPage().text(three_tabs())
        self.assertNotIn("<script", page)
        self.assertNotIn("http", page.replace('xmlns="http://www.w3.org/2000/svg"', ""))

    def test_a_missing_tab_says_why_escaped(self):
        page = TabbedHtmlPage().text(three_tabs(schematic=None)[:1] + [Tab("Schematic", None, "tsci said <b>no</b>")])
        self.assertIn("<p>Schematic: not drawn, because tsci said &lt;b&gt;no&lt;/b&gt;.</p>", page)
        self.assertEqual(1, len(pictures(page)))

    def test_the_same_tabs_give_the_same_bytes(self):
        self.assertEqual(TabbedHtmlPage().text(three_tabs()), TabbedHtmlPage().text(three_tabs()))


@slow("the tsci export of a circuit, 7 tests, 2.1 s on 2026-10-26")
class TscircuitExportTest(unittest.TestCase):
    def run_with(self, returncode=0, writes="<svg/>", stderr="", side_effect=None):
        def fake_run(command, **kwargs):
            if side_effect:
                raise side_effect
            out = Path(command[command.index("-o") + 1])
            if writes is not None:
                out.write_text(writes, encoding="utf-8")
            self.command, self.timeout = command, kwargs["timeout"]
            return subprocess.CompletedProcess(command, returncode, "", stderr)
        with mock.patch.object(tabbed_page.subprocess, "run", fake_run):
            return TscircuitExport("/bin/tsci").export_svg("circuit.json", "pcb-svg")

    def test_it_returns_the_svg_and_passes_an_absolute_path_and_its_own_timeout(self):
        self.assertEqual(SvgExportResult("<svg/>", None), self.run_with())
        self.assertTrue(Path(self.command[2]).is_absolute())
        self.assertEqual(["-f", "pcb-svg"], self.command[3:5])
        self.assertEqual(60, self.timeout)

    def test_no_tsci_says_so(self):
        self.assertEqual(SvgExportResult(None, "tsci is not installed"),
                         TscircuitExport(None).export_svg("circuit.json", "pcb-svg"))

    def test_a_failed_export_says_its_exit_code_and_last_line(self):
        self.assertEqual("tsci export -f pcb-svg exited 1: Element type is invalid",
                         self.run_with(returncode=1, writes=None, stderr="trace\nElement type is invalid\n").why_missing)

    def test_an_empty_output_is_a_failure_even_with_exit_0(self):
        self.assertEqual("tsci export -f pcb-svg wrote nothing", self.run_with(writes="  \n").why_missing)
        self.assertEqual("tsci export -f pcb-svg wrote nothing", self.run_with(writes=None).why_missing)

    def test_an_output_that_is_not_utf8_says_why(self):
        def fake_run(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_bytes(b"<svg>\xff</svg>")
            return subprocess.CompletedProcess(command, 0, "", "")
        with mock.patch.object(tabbed_page.subprocess, "run", fake_run):
            result = TscircuitExport("/bin/tsci").export_svg("circuit.json", "pcb-svg")
        self.assertTrue(result.why_missing.startswith("tsci export -f pcb-svg wrote a file spark cannot read"))

    def test_a_timeout_says_so(self):
        result = self.run_with(side_effect=subprocess.TimeoutExpired("tsci", 60))
        self.assertEqual("tsci export -f pcb-svg took over 60 s", result.why_missing)

    @unittest.skipUnless(shutil.which("tsci"), "tsci is not installed")
    def test_the_real_tsci_exports_a_circuit(self):
        with tempfile.TemporaryDirectory() as scratch:
            circuit = Path(scratch) / "circuit.json"
            shutil.copy(CIRCUIT, circuit)
            for form in ("schematic-svg", "pcb-svg"):
                result = TscircuitExport(shutil.which("tsci")).export_svg(circuit, form)
                self.assertIsNone(result.why_missing, form)
                self.assertIn("<svg", result.svg)


def style_of(page):
    return re.search(r"<style>(.*?)</style>", page, re.S).group(1)


def root_blocks(style):
    """The token blocks: bare :root, the dark media query, and :root[data-theme="dark"]."""
    light = re.search(r"(?:^|\})\s*:root\{([^}]*)\}", style).group(1)
    media = re.search(r'@media \(prefers-color-scheme: dark\)\{:root:not\(\[data-theme="light"\]\)\{([^}]*)\}\}', style)
    forced = re.search(r':root\[data-theme="dark"\]\{([^}]*)\}', style)
    return light, media and media.group(1), forced and forced.group(1)


def tokens(block):
    return dict(re.findall(r"(--[a-z]+):([^;]+)", block))


class ArtifactPageTest(unittest.TestCase):
    """P272 (#308): the page follows the Artifact page rules, so one file serves a browser and an Artifact."""

    def setUp(self):
        self.page = TabbedHtmlPage().text(three_tabs(), title="button light xiao circuit")
        self.style = style_of(self.page)

    def test_every_token_is_first_defined_on_bare_root(self):
        light, _, _ = root_blocks(self.style)
        self.assertEqual({"--paper", "--ink", "--backdrop", "--accent"}, set(tokens(light)))
        used = set(re.findall(r"var\((--[a-z]+)\)", self.style))
        self.assertEqual(used, set(tokens(light)))

    def test_the_dark_values_are_written_twice_and_are_the_same(self):
        light, media, forced = root_blocks(self.style)
        self.assertIsNotNone(media, "the media query with the light guard is missing")
        self.assertIsNotNone(forced, ':root[data-theme="dark"] is missing')
        self.assertEqual(tokens(media), tokens(forced))
        self.assertEqual(set(tokens(light)), set(tokens(media)))
        for name in ("--paper", "--ink", "--accent"):
            self.assertNotEqual(tokens(light)[name], tokens(media)[name], name)
        self.assertTrue(light.endswith("color-scheme:light"))
        self.assertIn("color-scheme:dark", media)
        self.assertIn("color-scheme:dark", forced)

    def test_the_body_has_an_explicit_background_from_a_token(self):
        self.assertRegex(self.style, r"body\{[^}]*background:var\(--paper\)")
        self.assertRegex(self.style, r"body\{[^}]*color:var\(--ink\)")

    def test_no_color_is_written_outside_the_token_blocks(self):
        outside = re.sub(r"\{[^{}]*--paper:[^{}]*\}", "{}", self.style)
        self.assertEqual(3, len(re.findall(r"--paper:", self.style)))
        self.assertNotRegex(outside, r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(")
        self.assertNotRegex(outside, r"(?:color|background|border-color):\s*(?!var\(|transparent|inherit)[a-z]+")
        self.assertNotIn("border-color:#c33", self.page)

    def test_every_selected_tab_uses_the_accent_token(self):
        for number in (1, 2, 3):
            self.assertIn("#tab%d:checked~nav label[for=tab%d]{border-color:var(--accent)}" % (number, number),
                          self.style)

    def test_the_page_says_its_language(self):
        self.assertIn('<html lang="en">', self.page)

    def test_the_side_gutter_is_16px(self):
        self.assertRegex(self.style, r"nav\{[^}]*padding:0 16px")
        self.assertRegex(self.style, r"\.panel\{[^}]*padding:12px 16px")

    def test_nothing_can_push_the_page_sideways(self):
        self.assertRegex(self.style, r"\.panel img\{[^}]*max-width:100%")
        self.assertRegex(self.style, r"p\{[^}]*overflow-wrap:anywhere")

    def test_nothing_makes_a_panel_wider_than_the_screen(self):
        for rule in ("min-width", "nowrap", "overflow-x"):
            self.assertNotIn(rule, self.style)

    def test_the_title_is_written_from_the_title_argument(self):
        self.assertIn("<title>button light xiao circuit</title>", self.page)

    def test_the_page_stays_a_whole_document_for_a_browser(self):
        self.assertTrue(self.page.startswith("<!doctype html>"))
        self.assertIn('<meta name="viewport" content="width=device-width, initial-scale=1">', self.page)


class PageTitleTest(unittest.TestCase):
    def test_the_title_has_two_to_four_words(self):
        for name, title in [("button-light-xiao", "button light xiao circuit"),
                            ("keep", "keep circuit"),
                            ("2026-10-17", "2026 10 17 circuit"),
                            ("a-b-c-d", "a b c circuit"),
                            ("my cool robot project", "my cool robot circuit"),
                            ("board.v2", "board v2 circuit"),
                            ("---", "spark circuit"),
                            ("__", "spark circuit"),
                            ("", "spark circuit"),
                            ("x" * 300, "x" * 20 + " circuit"),
                            ("Světlo-tlačítko", "Světlo tlačítko circuit")]:
            with self.subTest(name=name[:12]):
                self.assertEqual(title, tabbed_page.page_title(name))
                self.assertIn(len(title.split()), (2, 3, 4))


if __name__ == "__main__":
    unittest.main()
