"""
The page of a project (P827, #1185): the flow's phases as one plain HTML file, `page.html`, each with a status word and a
mark, readable from disk. `FlowPage` is the Value a renderer takes; `FlowHtmlPage` is the Renderer that draws it. The page
adds no tick of its own: a phase whose status is not ok never shows one (`shown_phase`). It has no script, loads nothing
from the web and is the same bytes for the same flow. The breadboard stands in it as plain shapes (`SvgInliner`, P949),
with its keys for a player and a legend of its pads; every other picture is an <img>.
"""

import base64
import html
import xml.etree.ElementTree as ElementTree
from collections import namedtuple

from spark.breadboard import before_power, part_pictures, picture_check
from spark.breadboard.svg_diagram import PAD_MARKS
from spark.breadboard.tabbed_page import token_styles
from spark.flow import flow_codes
from spark.flow.fingerprint import SHORT
from spark.flow.phase_readers import MARKS
from spark.core.outcomes import COULD_NOT_RUN, OK

# --- MVP ---
#: Value: one picture of the project: its title, its SVG text or None, and why there is none. The page keeps no renderer's
#: type, so whoever has another kind of picture (a tab) converts it.
Picture = namedtuple("Picture", "title svg why_missing")
#: Value: what the page shows of a phase: its mark and its status word.
ShownPhase = namedtuple("ShownPhase", "mark word")
#: Value: the wiring of a build as plain values, so that one call of the project's mask covers it: `steps` are (number, words),
#: `before_power` the dicts of a BeforePowerItem's fields, `records` the record ids, and `why_missing` says why there is no
#: wiring to show (None when there is).
PageWiring = namedtuple("PageWiring", "steps before_power records why_missing")
#: Value: what a page holds. `phases` are the Phase dicts of the flow, `stands_at` the first open phase or None, `pictures`
#: Pictures, `notes` fixed lines and `wiring` a PageWiring or None (no section). `fingerprint` is the flow's
#: (`fingerprint.fingerprint_of`, P829) and `written` the newest change time of its files, both None when not known. A page
#: is masked before it is rendered.
FlowPage = namedtuple("FlowPage", "title phases stands_at pictures notes wiring fingerprint written", defaults=(None, None, None))

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


def _mark(shown):
    return '<span aria-hidden="true">%s</span>' % _text(shown.mark)


class WiringHtmlSection:
    """
    Renderer: the wiring of a page (P828) as one `<section id="wiring">`: the lines before power in a list of their own, then
    the steps in `<ol id="steps">`. One at a time is the URL's fragment: the style hides every step but the target, and a
    browser without `:has()` shows them all. It decides nothing: the steps and the lines are given.
    """

    STYLE = ("#steps>li .nav{display:none}#steps>li:target .nav{display:block}"
             "#steps:has(>li:target)>li:not(:target){display:none}"
             "@media print{#steps>li{display:list-item!important}#steps .nav{display:none!important}}")

    def __init__(self):
        self.before_power = before_power.BeforePowerHtmlList()

    def text(self, wiring, with_picture):
        """The section: its heading, then the reason there is nothing to show, or the sentence, the lines and the steps."""
        lines = ['<section id="wiring">', "<h2>%s</h2>" % _text(flow_codes.WIRING_HEADING)]
        if wiring.why_missing:
            return "\n".join(lines + ["<p>%s</p>" % _text(wiring.why_missing), "</section>"])
        intro = flow_codes.WIRING_INTRO + (" " + flow_codes.WIRING_PICTURE_INTRO if with_picture else "")
        lines.append("<p>%s</p>" % _text(intro))
        lines += self._before_power(wiring) + self._steps(wiring.steps, with_picture)
        return "\n".join(lines + ["</section>"])

    def _before_power(self, wiring):
        if not wiring.before_power:
            return []
        return (["<h3>%s</h3>" % _text(before_power.HEADING), "<ul>"] + self.before_power.items(wiring.before_power) + ["</ul>"]
                + [self.before_power.records_line(wiring.records)])

    def _steps(self, steps, with_picture):
        if not steps:
            return []
        start = '<p><a href="#step-%d">%s</a></p>' % (steps[0][0], _text(flow_codes.ONE_AT_A_TIME))
        return [start, '<ol id="steps">'] + [self._step(each, steps, with_picture) for each in steps] + ["</ol>"]

    def _step(self, step, steps, with_picture):
        number, words = step
        return '<li id="step-%d" value="%d" tabindex="-1">%s%s</li>' % (number, number, _text(words), self._nav(step, steps, with_picture))

    @staticmethod
    def _nav(step, steps, with_picture):
        """The nav line of one step: where it stands, Back and Next (not on the first and the last), the list and the pictures."""
        numbers = [number for number, _words in steps]
        at = numbers.index(step[0])
        links = []
        if at > 0:
            links.append('<a href="#step-%d" aria-label="%s">%s</a>' % (numbers[at - 1], flow_codes.BACK_LABEL % numbers[at - 1], flow_codes.BACK))
        if at < len(numbers) - 1:
            links.append('<a href="#step-%d" aria-label="%s">%s</a>' % (numbers[at + 1], flow_codes.NEXT_LABEL % numbers[at + 1], flow_codes.NEXT))
        links.append('<a href="#wiring">%s</a>' % _text(flow_codes.ALL_STEPS))
        links += ['<a href="#pictures">%s</a>' % _text(flow_codes.PICTURE)] if with_picture else []
        return '<div class="nav">%s %s</div>' % (_text(flow_codes.STEP_OF % (at + 1, len(numbers))), " ".join(links))


#: Value: a picture made fit to stand in the page: its markup, and the pad states its dots draw, in PAD_MARKS's order.
InlineSvg = namedtuple("InlineSvg", "markup pads")


class SvgInliner:
    """
    Renderer: an SVG as markup that stands in the page (P949), or None. Inline, an SVG runs its scripts and its handlers,
    and an <img> does not, so it inlines only an SVG that parses and holds no DOCTYPE, whose elements are all
    `part_pictures.PLAIN_SHAPES` and whose attributes are all `PLAIN_ATTRIBUTES` (its name lowercased, as HTML reads
    it, with no namespace), and no value of which, read after the parse and lowercased, holds an `UNPLAIN_VALUES` word.
    One more element stands (P946): an `image` of `IMAGE_ATTRIBUTES` whose href is a JPEG embedded as base64, by
    `picture_check.is_embedded_jpeg`, the rule a kept picture passed. No element may stand inside a `title`. It works on its own parse: every tag loses its namespace, so the root has no xmlns and the file keeps its own, the
    comments are gone and every text stays escaped. The same SVG gives the same bytes.
    """

    def inline(self, svg):
        if "<!doctype" in svg.lower():
            return None
        try:
            root = ElementTree.fromstring(svg)
            if not all(self._plain(element) for element in root.iter()) or any(
                    len(element) for element in root.iter() if element.tag == "title"):
                return None
            markup = ElementTree.tostring(root, encoding="unicode")
        except Exception:  # noqa: BLE001  a hand-edited file can hold anything: whatever it raises, the page shows an <img>
            return None
        drawn = {element.get("data-pad") for element in root.iter()}
        return InlineSvg(markup, [state for state in PAD_MARKS if state in drawn])

    @staticmethod
    def _plain(element):
        """True when `element` is a plain shape whose every attribute is allowed and holds no unplain word; it drops the
        tag's namespace on the way."""
        element.tag = _local(element.tag)
        if picture_check.repeated_names(element.attrib):  # HTML keeps the first of two names that are one lowercased
            return False
        if element.tag == "image":  # P946: a kept photo, whose one href is a JPEG embedded as base64
            others = {name: value for name, value in element.attrib.items() if not picture_check.is_href(name)}
            names = all(name.lower() in part_pictures.IMAGE_ATTRIBUTES for name in others)
            return picture_check.is_embedded_jpeg(element.get("href")) and names and _plain_values(others)
        names = all(name.lower() in part_pictures.PLAIN_ATTRIBUTES for name in element.attrib)
        return element.tag in part_pictures.PLAIN_SHAPES and names and _plain_values(element.attrib)


def _plain_values(attributes):
    """True when no value, lowercased, holds an `UNPLAIN_VALUES` word."""
    return not any(word in value.lower() for value in attributes.values() for word in part_pictures.UNPLAIN_VALUES)


def _local(name):
    """A tag or attribute name without its namespace."""
    return name.rsplit("}", 1)[-1]


class FlowHtmlPage:
    """
    Renderer: a FlowPage as one HTML document, the same bytes for the same page. It loops over the page's phases and holds
    no phase name and no count. The colors are the praised page's tokens (P949), light and dark, with the system's fonts,
    and no color says a status: the mark and the word do. Under an inline breadboard a legend names each pad state its
    dots draw, and only those.
    """

    FILE_NAME = "page.html"
    NOUN = "page"
    PURPOSE_MESSAGE = "where the project stands, phase by phase, with its pictures: open it in a browser"

    #: The praised page's colors by token, light and dark. The picture ground stays white in both, as the tabbed page's:
    #: the pictures are drawn for a light ground. The fonts are the system's, so the page loads nothing.
    TOKENS_LIGHT = {"--bg": "#eef1f3", "--ink": "#1c262e", "--muted": "#566570", "--line": "#c3ccd3", "--signal": "#c8500f",
                    "--backdrop": "#fff", "--display": "ui-serif,Georgia,serif",
                    "--body": 'system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif'}
    TOKENS_DARK = {"--bg": "#141b21", "--ink": "#e4eaee", "--muted": "#9aa9b4", "--line": "#3a4955", "--signal": "#f08a48",
                   "--backdrop": "#fff"}
    STYLE = ("body{max-width:1180px;margin:0 auto;padding:12px 16px;font:16px/1.55 var(--body);background:var(--bg);"
             "color:var(--ink)}"
             "h1,h2{font-family:var(--display);line-height:1.2}"
             "nav ol{display:flex;flex-wrap:wrap;gap:4px 16px;list-style:none;margin:0;padding:0}"
             "a{color:var(--ink)}a:focus-visible{outline:2px solid var(--signal)}"
             ".phase{border-top:1px solid var(--line);padding:4px 0}"
             "summary{cursor:pointer}summary h2{display:inline}"
             "p,li{overflow-wrap:anywhere}"
             "img{width:100%;max-width:100%;height:auto;max-height:88vh;object-fit:contain;background:var(--backdrop)}"
             ".fig{margin:0;overflow-x:auto;background:var(--backdrop);border:1px solid var(--line);border-radius:6px}"
             ".fig svg{display:block;width:100%;height:auto}"
             ".pads{display:flex;flex-wrap:wrap;gap:4px 18px;list-style:none;padding:0;color:var(--muted)}"
             ".sw{display:inline-block;width:14px;height:14px;border-radius:50%;margin-right:7px;vertical-align:-2px;"
             "border:1px solid var(--line)}")
    WIRING = WiringHtmlSection()
    INLINER = SvgInliner()

    def text(self, page):
        head = [self._open(page), "<h1>%s</h1>" % _text(page.title), self._intro(page), self._rail(page), self._stands_at(page)]
        return "\n".join(head + [part for part in self._body(page) if part] + ["</body>", "</html>"]) + "\n"

    @staticmethod
    def _sheet(page):
        """True when the page holds a wiring sheet to wire from."""
        return bool(page.wiring) and not page.wiring.why_missing

    def _intro(self, page):
        """What the page is and how to act on it, and, with a sheet, that the wiring comes first (P828 step 2)."""
        said = [flow_codes.PAGE_INTRO] + ([flow_codes.WIRING_FIRST] if self._sheet(page) else [])
        return '<p class="intro">%s</p>' % _text(" ".join(said))

    def _body(self, page):
        """With a sheet, the wiring, its pictures and the marks come first and the folded phases after them (P828 step 2):
        the person at the bench finds step 1 at once. Else the phases come first, as before."""
        phases = [self._phase(phase) for phase in page.phases]
        shown = [self._wiring(page), self._pictures(page.pictures), self._legend()]
        return (shown + phases if self._sheet(page) else phases + shown) + [self._notes(page.notes)]

    def _open(self, page):
        style = token_styles(self.TOKENS_LIGHT, self.TOKENS_DARK) + self.STYLE + (self.WIRING.STYLE if page.wiring else "")
        return "\n".join(['<!doctype html>', '<html lang="en">', '<head>', '<meta charset="utf-8">',
                          '<meta name="viewport" content="width=device-width, initial-scale=1">',
                          '<title>%s</title>' % _text(page.title), '<style>%s</style>' % style, '</head>',
                          '<body data-stands-at="%s" data-fingerprint="%s" data-written="%s">' % (
                              _text(page.stands_at or "none"), _text((page.fingerprint or "none")[:SHORT]), _text(page.written or "none"))])

    @staticmethod
    def _stands_at(page):
        return "<p>%s</p>" % _text(flow_codes.STANDS_AT_LINE % page.stands_at if page.stands_at else flow_codes.NOTHING_OPEN_LINE)

    @staticmethod
    def _data(phase):
        return 'data-phase="%s" data-status="%s"' % (_text(phase["phase"]), _text("none" if phase["status"] is None else phase["status"]))

    def _rail(self, page):
        entries = []
        for phase in page.phases:
            shown = shown_phase(phase)
            entries.append('<li %s><a href="#phase-%s">%s %s <span>%s</span></a></li>' % (
                self._data(phase), _text(phase["phase"]), _mark(shown), _text(phase["phase"]), _text(shown.word)))
        links = ['<a href="#wiring">%s</a>' % _text(flow_codes.WIRING_HEADING)] if page.wiring else []
        links += ['<a href="#pictures">Pictures</a>'] if page.pictures else []
        return '<nav aria-label="Phases"><ol>\n%s\n</ol>%s</nav>' % ("\n".join(entries), " ".join(links))

    def _phase(self, phase):
        shown = shown_phase(phase)
        lines = ['<section class="phase" id="phase-%s" %s>' % (_text(phase["phase"]), self._data(phase)),
                 "<details><summary><h2>%s %s <span>%s</span></h2></summary>" % (_mark(shown), _text(phase["phase"]), _text(shown.word)),
                 "<p>Done by: %s</p>" % _text(phase["by"])]
        lines += ["<p>%s</p>" % _text(said) for said in phase["says"]]
        offers = ['<li data-key="%s">%s: %s</li>' % (_text(offer["key"]), _text(offer["label"]), _text(offer["effect"]))
                  for offer in phase["offers"]]
        return "\n".join(lines + (["<ul>%s</ul>" % "".join(offers)] if offers else []) + ["</details>", "</section>"])

    def _wiring(self, page):
        drawn = any(each.title == flow_codes.BREADBOARD_TITLE and each.svg for each in page.pictures)
        return self.WIRING.text(page.wiring, drawn) if page.wiring else ""

    def _pictures(self, pictures):
        """All the pictures in one section, in the order the page was given them, or nothing when there are none."""
        if not pictures:
            return ""
        return '<section id="pictures"><h2>Pictures</h2>\n%s\n</section>' % "\n".join(self._picture(each) for each in pictures)

    def _picture(self, picture):
        """The breadboard stands in the page when the inliner takes it, so a player finds its keys. Any other picture, and
        a breadboard it refuses, is an <img>: one SVG's <style> cannot reach another, and no script in it runs."""
        title = _text(picture.title)
        if picture.svg is None:
            return '<div class="picture"><h3>%s</h3><p>%s</p></div>' % (title, _text(picture.why_missing))
        inline = self.INLINER.inline(picture.svg) if picture.title == flow_codes.BREADBOARD_TITLE else None
        if inline:
            return '<div class="picture"><h3>%s</h3><figure class="fig" aria-label="%s">%s</figure>%s</div>' % (
                title, title, inline.markup, self._pads(inline.pads))
        data = base64.b64encode(picture.svg.encode("utf-8")).decode("ascii")
        return '<div class="picture"><h3>%s</h3><img src="data:image/svg+xml;base64,%s" alt="%s"></div>' % (title, data, title)

    @staticmethod
    def _pads(pads):
        """The legend under an inline breadboard: one line per pad state its dots draw, after the figure, so its words
        stand on the page's own ground in both themes. Nothing when it draws none."""
        if not pads:
            return ""
        return '<ul class="pads">%s</ul>' % "".join('<li><span class="sw" style="background:%s"></span>%s</li>' % (
            PAD_MARKS[state].fill, _text(PAD_MARKS[state].words)) for state in pads)

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
