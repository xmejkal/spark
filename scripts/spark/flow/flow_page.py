"""
The page of a project (P827, #1185): the flow's phases as one plain HTML file, `page.html`, each with a status word and a
mark, readable from disk. `FlowPage` is the Value a renderer takes; `FlowHtmlPage` is the Renderer that draws it. The page
adds no tick of its own: a phase whose status is not ok never shows one (`shown_phase`). It has no script, loads nothing
from the web and is the same bytes for the same flow.
"""

import base64
import html
from collections import namedtuple

from spark.breadboard.tabbed_page import TabbedHtmlPage
from spark.flow import flow_codes
from spark.flow.phase_readers import MARKS
from spark.core.outcomes import COULD_NOT_RUN, OK

# --- MVP ---
#: Value: one picture of the project: its title, its SVG text or None, and why there is none. The page keeps no renderer's
#: type, so whoever has another kind of picture (a tab) converts it.
Picture = namedtuple("Picture", "title svg why_missing")
#: Value: what the page shows of a phase: its mark and its status word.
ShownPhase = namedtuple("ShownPhase", "mark word")
#: Value: what a page holds. `phases` are the Phase dicts of the flow, `stands_at` the first open phase or None, `pictures`
#: Pictures and `notes` fixed lines. A page is masked before it is rendered.
FlowPage = namedtuple("FlowPage", "title phases stands_at pictures notes")

TICK = MARKS[OK][1]


def word_of(status):
    """The words a person reads for `status`: the flow's own word, `ok` for ok, "not checked by spark" for None, and the
    code itself for one the flow does not know."""
    if status is None:
        return flow_codes.NOT_CHECKED_WORD
    return (MARKS[status][0] or flow_codes.OK_WORD) if status in MARKS else str(status)


def shown_phase(phase):
    """The ShownPhase of one Phase dict. The guard: a phase whose status is not ok never shows the tick, it shows the
    could-not-run mark. It can only remove a tick."""
    mark = phase["mark"]
    if mark == TICK and phase["status"] != OK:
        mark = MARKS[COULD_NOT_RUN][1]
    return ShownPhase(mark, word_of(phase["status"]))


def _text(value):
    return html.escape(str(value))


def _attr(value):
    return html.escape(str(value), quote=True)


def _mark(shown):
    return '<span aria-hidden="true">%s</span>' % _text(shown.mark)


class FlowHtmlPage:
    """
    Renderer: a FlowPage as one HTML document, the same bytes for the same page. It loops over the page's phases and holds
    no phase name and no count. The colors are the tabbed page's tokens, and no color says a status: the mark and the word do.
    """

    FILE_NAME = "page.html"
    NOUN = "page"
    PURPOSE_MESSAGE = "where the project stands, phase by phase, with its pictures: open it in a browser"

    STYLE = ("body{margin:0;padding:12px 16px;font:15px system-ui,sans-serif;background:var(--paper);color:var(--ink)}"
             "nav ol{display:flex;flex-wrap:wrap;gap:4px 16px;list-style:none;margin:0;padding:0}"
             "a{color:var(--ink)}a:focus-visible{outline:2px solid var(--accent)}"
             ".phase{border-top:1px solid var(--ink);padding:4px 0}"
             "p,li{overflow-wrap:anywhere}"
             "img{width:100%;max-width:100%;height:auto;max-height:88vh;object-fit:contain;background:var(--backdrop)}")

    def text(self, page):
        pictures = list(page.pictures)
        head = [self._open(page), "<h1>%s</h1>" % _text(page.title), self._rail(page.phases), self._stands_at(page)]
        body = [self._picture(each) for each in pictures[:1]] + [self._phase(phase) for phase in page.phases]
        body += [self._picture(each) for each in pictures[1:]] + [self._legend(), self._notes(page.notes)]
        return "\n".join(head + body + ["</body>", "</html>"]) + "\n"

    def _open(self, page):
        style = TabbedHtmlPage._token_styles() + self.STYLE
        return "\n".join(['<!doctype html>', '<html lang="en">', '<head>', '<meta charset="utf-8">',
                          '<meta name="viewport" content="width=device-width, initial-scale=1">',
                          '<title>%s</title>' % _text(page.title), '<style>%s</style>' % style, '</head>',
                          '<body data-stands-at="%s">' % _attr(page.stands_at or "none")])

    @staticmethod
    def _stands_at(page):
        return "<p>%s</p>" % _text(flow_codes.STANDS_AT_LINE % page.stands_at if page.stands_at else flow_codes.NOTHING_OPEN_LINE)

    @staticmethod
    def _data(phase):
        return 'data-phase="%s" data-status="%s"' % (_attr(phase["phase"]), _attr("none" if phase["status"] is None else phase["status"]))

    def _rail(self, phases):
        entries = []
        for phase in phases:
            shown = shown_phase(phase)
            entries.append('<li %s><a href="#phase-%s">%s %s <span>%s</span></a></li>' % (
                self._data(phase), _attr(phase["phase"]), _mark(shown), _text(phase["phase"]), _text(shown.word)))
        return '<nav aria-label="Phases"><ol>\n%s\n</ol></nav>' % "\n".join(entries)

    def _phase(self, phase):
        shown = shown_phase(phase)
        lines = ['<section class="phase" id="phase-%s" %s>' % (_attr(phase["phase"]), self._data(phase)),
                 "<h2>%s %s <span>%s</span></h2>" % (_mark(shown), _text(phase["phase"]), _text(shown.word)),
                 "<p>Done by: %s</p>" % _text(phase["by"])]
        lines += ["<p>%s</p>" % _text(said) for said in phase["says"]]
        offers = ["<li><code>%s</code>: %s</li>" % (_text(offer["key"]), _text(offer["effect"])) for offer in phase["offers"]]
        return "\n".join(lines + (["<ul>%s</ul>" % "".join(offers)] if offers else []) + ["</section>"])

    @staticmethod
    def _picture(picture):
        title = _text(picture.title)
        if picture.svg is None:
            return '<section class="picture"><h2>%s</h2><p>Not drawn, because %s.</p></section>' % (title, _text(picture.why_missing))
        data = base64.b64encode(picture.svg.encode("utf-8")).decode("ascii")
        return '<section class="picture"><h2>%s</h2><img src="data:image/svg+xml;base64,%s" alt="%s"></section>' % (
            title, data, _attr(picture.title))

    @staticmethod
    def _legend():
        items = []
        for status, (_word, glyph) in MARKS.items():
            more = ": " + flow_codes.NOT_CHECKED_LEGEND if status is None else ""
            items.append("<li>%s %s%s</li>" % (_mark(ShownPhase(glyph, word_of(status))), _text(word_of(status)), _text(more)))
        return '<section class="legend"><h2>Marks</h2><ul>%s</ul></section>' % "".join(items)

    @staticmethod
    def _notes(notes):
        return '<section class="notes"><h2>Notes</h2>%s</section>' % "".join("<p>%s</p>" % _text(note) for note in notes)
# --- end MVP ---
