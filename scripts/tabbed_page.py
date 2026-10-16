"""
The page (P271, #307): one circuit in three tabs, the breadboard, the schematic and the PCB, as one plain HTML file,
`page.html`, beside the sheet. The breadboard is spark's own picture (P268); the schematic and the PCB are tscircuit's,
from `tsci export` on the same kept circuit.json.

    TscircuitExport(toolchain).export_svg(circuit, "schematic-svg")  ->  Tab  ->  TabbedHtmlPage().text(tabs)

Each picture sits in its own <img>, so one SVG's <style> and ids cannot reach another: inline, the schematic's
`.boundary` rule turns the PCB's black background beige (P271's council, round 1). The page has no script and loads
nothing from the web.
"""

import base64
import collections
import html
import subprocess
import tempfile
from pathlib import Path

#: Result: what one `tsci export` gave, its SVG text, or None and why there is none.
SvgExportResult = collections.namedtuple("SvgExportResult", "svg why_missing")

#: Value: one tab of the page, its title, its SVG text or None, and why it is missing.
Tab = collections.namedtuple("Tab", "title svg why_missing")


class TscircuitExport:
    """Adapter: wraps `tsci export`, which draws a built circuit.json as a schematic or a PCB. It is given the
    toolchain, or None when there is no tsci, and it never raises for an export that failed: it says why."""

    #: Seconds one export may take; one takes about 1.2 s on button-light (P271, step 1).
    TIMEOUT_S = 60

    def __init__(self, toolchain):
        self.toolchain = toolchain

    def export_svg(self, circuit_path, form):
        """`form` is a `tsci export -f` format, "schematic-svg" or "pcb-svg"."""
        if self.toolchain is None:
            return SvgExportResult(None, "tsci is not installed")
        with tempfile.TemporaryDirectory() as scratch:
            out = Path(scratch) / "out.svg"
            # tsci 0.0.2600 fails on a bare relative "circuit.json", so the path is always absolute.
            command = [str(self.toolchain), "export", str(Path(circuit_path).resolve()), "-f", form, "-o", str(out)]
            try:
                run = subprocess.run(command, capture_output=True, text=True, timeout=self.TIMEOUT_S)
            except subprocess.TimeoutExpired:
                return SvgExportResult(None, "tsci export -f %s took over %d s" % (form, self.TIMEOUT_S))
            except OSError as refused:
                return SvgExportResult(None, "tsci export -f %s could not run: %s" % (form, refused))
            if run.returncode != 0:
                said = (run.stderr or run.stdout).strip().splitlines()
                return SvgExportResult(None, "tsci export -f %s exited %d%s" % (
                    form, run.returncode, ": " + said[-1] if said else ""))
            svg = out.read_text(encoding="utf-8") if out.is_file() else ""
            if not svg.strip():
                return SvgExportResult(None, "tsci export -f %s wrote nothing" % form)
            return SvgExportResult(svg, None)


class TabbedHtmlPage:
    """
    Renderer: tabs as one self-contained HTML page, each SVG in an <img> as a data URI, the tabs switched by CSS
    alone. A missing tab shows why. The same tabs give the same bytes. It is not in `breadboard.DRAWING_RENDERERS`,
    because those render a layout and this renders tabs; it keeps their `NOUN` and `PURPOSE_MESSAGE` for the lines the
    build prints about the file.
    """

    FILE_NAME = "page.html"
    #: What the build calls the file in a line that says it was not written or was removed.
    NOUN = "page"
    #: What the build says beside the file's path when it wrote it.
    PURPOSE_MESSAGE = "the breadboard, schematic and PCB in three tabs: open it in a browser"

    STYLE = ("body{margin:0;font:15px system-ui,sans-serif;background:#f6f3ee;color:#222}"
             "input{display:none}"
             "label{display:inline-block;padding:10px 18px;cursor:pointer;border-bottom:3px solid transparent}"
             ".panel{display:none;padding:12px}"
             ".panel img{width:100%;height:auto;max-height:88vh;object-fit:contain;background:#fff}")

    def text(self, tabs, title="spark"):
        radios, labels, panels, shown = [], [], [], []
        for number, tab in enumerate(tabs, 1):
            radios.append('<input type="radio" name="tab" id="tab%d"%s>' % (number, " checked" if number == 1 else ""))
            labels.append('<label for="tab%d">%s</label>' % (number, html.escape(tab.title)))
            panels.append('<div class="panel panel%d">%s</div>' % (number, self._picture(tab)))
            shown.append("#tab%d:checked~.panel%d{display:block}"
                         "#tab%d:checked~nav label[for=tab%d]{border-color:#c33}" % (number, number, number, number))
        return "\n".join(['<!doctype html>', '<html lang="en">', '<head>', '<meta charset="utf-8">',
                          '<meta name="viewport" content="width=device-width, initial-scale=1">',
                          '<title>%s</title>' % html.escape(title),
                          '<style>%s</style>' % (self.STYLE + "".join(shown)), '</head>', '<body>']
                         + radios + ['<nav>' + "".join(labels) + '</nav>'] + panels + ['</body>', '</html>']) + "\n"

    @staticmethod
    def _picture(tab):
        if tab.svg is None:
            return "<p>%s: not drawn, because %s.</p>" % (html.escape(tab.title), html.escape(tab.why_missing))
        data = base64.b64encode(tab.svg.encode("utf-8")).decode("ascii")
        return '<img src="data:image/svg+xml;base64,%s" alt="%s">' % (data, html.escape(tab.title, quote=True))


def exported_tab(title, result):
    """A tab from one export's result."""
    return Tab(title, result.svg, result.why_missing)
