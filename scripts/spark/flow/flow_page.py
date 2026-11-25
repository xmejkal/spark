"""
The page of a project (P827, #1185): the flow's phases as one plain HTML file, `page.html`, each with a status word and a
mark, readable from disk. `FlowPage` is the Value a renderer takes; `FlowHtmlPage` is the Renderer that draws it, as its
ordered table of sections (`SECTIONS`, P1123), in the slice 1 order (P1062): the freshness line, the NOW box, the Parts, Wiring and Pictures folds, the bench note, and the
developer fold, always closed. The page adds no tick of its own: a phase whose status is not ok never shows one
(`shown_phase`). It loads nothing from the web and is
the same bytes for the same flow. Its one script (P829 PR 3) does nothing from disk: `page_words` writes every word it
shows. The breadboard stands in it as plain shapes (`SvgInliner`, P949),
with its keys for a player and a legend of its pads; every other picture is an <img>.
"""

import base64
import html
import json
import xml.etree.ElementTree as ElementTree
from collections import namedtuple
from pathlib import Path

from spark.breadboard import before_power, part_pictures, picture_check
from spark.breadboard.svg_diagram import PAD_MARKS
from spark.breadboard.tabbed_page import token_styles
from spark.flow import flow_codes, request_codes
from spark.flow.fingerprint import SHORT
from spark.flow.phase_readers import MARKS, pick_need
from spark.core.outcomes import COULD_NOT_RUN, OK, PROBLEMS
from spark.core.zone_time import MONTHS, day_and_time

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
#: Value: what a page holds. `phases` are the Phase dicts of the flow, `stands_at` the guide's now phase or None, `pictures`
#: Pictures, `notes` fixed lines and `wiring` a PageWiring or None (no section). `fingerprint` is the flow's
#: (`fingerprint.fingerprint_of`, P829) and `written` the newest change time of its files, both None when not known. A page
#: is masked before it is rendered.
#: `guide` is the flow's guide (`guide.guide_of`, P977), a dict, or None for a page from a caller that has none: then the page
#: says where the project stands in one line.
#: `deployed` is ON THE BOARD's sentence (`deploy_reading.deployed_line`, P1062), or None before any deploy.
FlowPage = namedtuple("FlowPage", "title phases stands_at pictures notes wiring fingerprint written guide deployed",
                      defaults=(None, None, None, None, None))

TICK = MARKS[OK][1]
#: The page's one script (P829 PR 3): it adds the buttons only in a published page with the Artifact database, and does
#: nothing from disk. Its words stand beside it in an inert JSON block with WORDS_ID.
PAGE_SCRIPT = Path(__file__).resolve().with_name("page_script.js")
WORDS_ID = "spark-words"


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


def is_sendable(offer):
    """True when the page sends the offer dict `offer` from a button (P829): a pick, the parts list or the build."""
    return offer["key"].split(":", 1)[0] in flow_codes.SENDABLE


def _makes_stale(offer):
    """The attribute a sendable offer carries for the script and an agent: the phases it can make out of date, space
    apart. Nothing for an offer the page does not send."""
    return ' data-makes-stale="%s"' % _text(" ".join(offer["makes_stale"])) if is_sendable(offer) else ""


def sendable_now(page):
    """The offer dict the guide's now names (`now.offer`, P1030) when it is sendable, from any phase, else None: the NOW
    box's NEXT line then carries its key, and the script puts its button there, and nowhere else (P1062). The CLI's `next`
    holds the same offer's step."""
    now = (page.guide or {}).get("now")
    offers = [offer for phase in page.phases for offer in phase["offers"] if now and offer["key"] == now.get("offer") and is_sendable(offer)]
    return offers[0] if offers else None


def page_words(phases):
    """
    Every word the page's script shows (P829 PR 3, the plan's section 9), as one dict: per sendable offer its label (the
    button and the confirm's title) and the confirm's lines (its effect, the phases it may make out of date, the wait),
    the fixed words of the buttons and the status line, and the words of each answer. A refusal's words are keyed by
    its code's meaning, the `line` that `flow.py run-request` answers. The script fills in a time, a label or a line.
    `intro` is the published page's intro, `last_request` the line of the last request, `months` the month words of its
    time, and `request_kinds` and `request_other` its words when its offer left the page (P1062).
    """
    offers = {}
    for offer in (offer for phase in phases for offer in phase["offers"] if is_sendable(offer)):
        stale = [flow_codes.CONFIRM_STALE % ", ".join(offer["makes_stale"])] if offer["makes_stale"] else []
        offers[offer["key"]] = {"label": offer["label"], "says": [offer["effect"]] + stale}
    meanings = {str(code): meaning for code, meaning in request_codes.CODES.items()}
    marks = {status: MARKS[status][1] for status in (OK, PROBLEMS, COULD_NOT_RUN)}
    return {"offers": offers, "send": flow_codes.SEND, "cancel": flow_codes.CANCEL, "copy": flow_codes.COPY,
            "withdraw": flow_codes.WITHDRAW, "command": flow_codes.PAGE_COMMAND, "waiting": flow_codes.WAITING_SAYS,
            "now_button": flow_codes.NOW_BUTTON,
            "withdrawn": flow_codes.WITHDRAWN_SAYS, "waiting_for": flow_codes.WAITING_FOR, "last_request": flow_codes.LAST_REQUEST_SAYS,
            "not_sent": flow_codes.NOT_SENT_SAYS, "not_withdrawn": flow_codes.NOT_WITHDRAWN_SAYS,
            "intro": flow_codes.PUBLISHED_INTRO, "months": list(MONTHS),
            "request_kinds": dict(flow_codes.LAST_REQUEST_KINDS), "request_other": flow_codes.LAST_REQUEST_OTHER,
            "ok": dict(flow_codes.RAN_OK_SAYS), "ran": flow_codes.RAN_OTHER_SAYS, "note": flow_codes.RAN_NOTE_SAYS, "problems": flow_codes.RAN_PROBLEMS_SAYS,
            "could_not_run": flow_codes.COULD_NOT_RUN_SAYS,
            "refused": {meanings[name]: said for name, said in flow_codes.REFUSED_SAYS.items()},
            "marks": dict(marks, **{"not-run": flow_codes.NOT_RUN_MARK})}


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
        """The section: the reason there is nothing to show, or the sentence, the lines and the steps. Its heading is its
        fold's (P1062)."""
        lines = ['<section id="wiring">']
        if wiring.why_missing:
            return "\n".join(lines + ["<p>%s</p>" % _text(wiring.why_missing), "</section>"])
        intro = flow_codes.WIRING_INTRO + (" " + flow_codes.WIRING_PICTURE_INTRO if with_picture else "")
        lines.append("<p>%s</p>" % _text(intro))
        lines += self._before_power(wiring) + self._steps(wiring.steps, with_picture)
        return "\n".join(lines + ["</section>"])

    def _before_power(self, wiring):
        if not wiring.before_power:
            return []
        return ["<h3>%s</h3>" % _text(before_power.HEADING), "<ul>"] + self.before_power.items(wiring.before_power) + ["</ul>"]

    def _steps(self, steps, with_picture):
        if not steps:
            return []
        start = '<p><a href="#step-%d">%s</a></p>' % (steps[0][0], _text(flow_codes.ONE_AT_A_TIME % steps[0][0]))
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


def _data(phase):
    return 'data-phase="%s" data-status="%s"' % (_text(phase["phase"]), _text("none" if phase["status"] is None else phase["status"]))


def _fold(name, summary, body, is_open):
    """One fold (P1062): a `<details>` whose one-line summary holds the heading `summary` (markup), open when `is_open`."""
    return "\n".join(['<details class="fold" data-fold="%s"%s><summary><h2>%s</h2></summary>' % (
        name, " open" if is_open else "", summary)] + body + ["</details>"])


def _wiring_open(page):
    """True when the guide's now holds the wiring (`now.with_wiring`, `guide.with_wiring`): the page reads the fact."""
    return bool((((page.guide or {}).get("now")) or {}).get("with_wiring"))


#: The one wiring Renderer: the page's style, the wiring fold and the developer fold's records line use it.
WIRING = WiringHtmlSection()
#: The design-basis keys of the offers the page sends from a button (`flow_codes.SENDABLE`).
SENDABLE_KEYS = tuple("offer:" + kind for kind in flow_codes.SENDABLE)


class TitleHtmlHeading:
    """Renderer: the page's title as its one `<h1>`."""

    NAME = "title"
    KEYS = ()

    def text(self, page):
        return "<h1>%s</h1>" % _text(page.title)


class FreshHtmlLine:
    """Renderer: the freshness line (P1062) as one `<p>`."""

    NAME = "fresh"
    KEYS = ()

    def text(self, page):
        """The freshness line (P1062): the newest change of the project's files, read in the machine's zone, or the line of
        a page that knows no time. `data-written` keeps the stored time with its zone."""
        said = flow_codes.FRESH_LINE % day_and_time(page.written) if page.written else flow_codes.FRESH_NONE
        return '<p class="fresh">%s</p>' % _text(said)


class IntroHtmlLine:
    """Renderer: what the page is and how to act on it, as one `<p>`."""

    NAME = "intro"
    KEYS = ()

    def text(self, page):
        """What the page is and how to act on it (P828 step 2). The script puts the owner's sentence in its place."""
        return '<p class="intro">%s</p>' % _text(flow_codes.PAGE_INTRO)


class GuideHtmlSection:
    """Renderer: the guide (P977, P1062) as one `<section id="guide">`: the NOW box and the muted lines under it."""

    NAME = "guide"
    KEYS = ("phase:*", "by:*") + SENDABLE_KEYS

    def text(self, page):
        """The guide (P977 PR 2, P1062) in `<section id="guide">`, under the intro: the NOW box, then, muted, DONE, LATER (with
        the line on why there is no simulation) and SET ASIDE. A list with no item draws no line. Nothing with no guide, or a
        guide with no line. The script puts its panel last in it."""
        guide = page.guide
        if guide is None:
            return ""
        lines = [self._now(page),
                 self._muted(flow_codes.GUIDE_DONE, guide["done"]),
                 self._muted(flow_codes.GUIDE_LATER, guide["later"]),
                 '<p class="muted">%s</p>' % _text(guide["no_simulation"]) if guide["no_simulation"] else "",
                 self._muted(flow_codes.GUIDE_SET_ASIDE, guide["set_aside"])]
        lines = [line for line in lines if line]
        return "\n".join(['<section id="guide">'] + lines + ["</section>"]) if lines else ""

    def _now(self, page):
        """The NOW box (P1062): its phase and who acts, ON THE BOARD (`page.deployed`, only after a deploy), and NEXT, the
        guide's sentence, with the step link and the hooks of the sendable offer the now names (`sendable_now`). With no now,
        the line that says nothing is open (P1043, read with `.get`), or nothing."""
        now = page.guide["now"]
        if not now:
            said = page.guide.get("no_open_phase")
            return '<div class="now">\n<p>%s</p>\n</div>' % _text(said) if said else ""
        lines = ["<p><strong>%s</strong></p>" % _text(flow_codes.NOW_BY % (now["phase"], flow_codes.NOW_BY_JOIN.join(now["by"])))]
        if page.deployed:
            lines.append('<p class="board"><strong>%s</strong> %s</p>' % (_text(flow_codes.ON_BOARD_LABEL), _text(page.deployed)))
        offer = sendable_now(page)
        hooks = ' data-key="%s"%s' % (_text(offer["key"]), _makes_stale(offer)) if offer else ""
        lines.append('<p class="next"%s><strong>%s</strong> %s%s</p>' % (
            hooks, _text(flow_codes.NEXT_ACT_LABEL), _text(now["says"]), self._step_link(page)))
        return "\n".join(['<div class="now">'] + lines + ["</div>"])

    @staticmethod
    def _step_link(page):
        """The link to the first wiring step, when the guide's now holds the wiring and the page holds steps."""
        now, wiring = page.guide["now"], page.wiring
        if now.get("steps") and wiring and not wiring.why_missing and wiring.steps:
            first = wiring.steps[0][0]
            return ' <a href="#step-%d">%s</a>' % (first, _text(flow_codes.ONE_AT_A_TIME % first))
        return ""

    @staticmethod
    def _muted(label, items):
        """One muted line under the NOW box: its label in `<strong>` and its items, comma apart, or nothing with none."""
        return '<p class="muted"><strong>%s</strong> %s</p>' % (_text(label), _text(", ".join(items))) if items else ""


class StandsAtHtmlLine:
    """Renderer: where the project stands, as one `<p>`, for a page with no guide."""

    NAME = "stands-at"
    KEYS = ("phase:*",)

    def text(self, page):
        if page.guide is not None:  # the guide says where the project stands (P977)
            return ""
        return "<p>%s</p>" % _text(flow_codes.STANDS_AT_LINE % page.stands_at if page.stands_at else flow_codes.NOTHING_OPEN_LINE)


class PartsHtmlFold:
    """Renderer: the parts fold (P1062) as one `<details>`: the parts phase's lines and a row per sendable offer."""

    NAME = "parts"
    KEYS = ("phase:parts", "status:*") + SENDABLE_KEYS

    def text(self, page):
        """The parts fold (P1062): the parts phase's says in order (P1044's wired line first), one row per need with its
        picks in the reading's order (`pick_need`), then the other sendable offers, the parts list and the build. Each is a
        hooked row, but the one on the NOW line. Open while the parts are NOW. Nothing with no parts phase and no row."""
        phase = next((each for each in page.phases if each["phase"] == flow_codes.PARTS), None)
        on_now = (sendable_now(page) or {}).get("key")
        needs = {}
        for offer in (offer for each in page.phases for offer in each["offers"] if is_sendable(offer) and offer["key"] != on_now):
            needs.setdefault(pick_need(offer["key"]), []).append(offer)
        if phase is None and not needs:
            return ""
        rows = ['<li class="need"><strong>%s</strong><ul>%s</ul></li>' % (_text(need), "".join(self._hooked(offer) for offer in offers))
                for need, offers in needs.items() if need is not None]
        rows += [self._hooked(offer) for offer in needs.get(None, [])]
        said = list(dict.fromkeys(phase["says"])) if phase else []  # a line the phase says for every need stands once
        body = ["<p>%s</p>" % _text(line) for line in said] + (["<ul>%s</ul>" % "\n".join(rows)] if rows else [])
        summary = _text(flow_codes.PARTS_HEADING)
        if phase:
            shown = shown_phase(phase)
            summary = "%s %s <span>%s</span>" % (_mark(shown), summary, _text(shown.word))
        return _fold("parts", summary, body, ((page.guide or {}).get("now") or {}).get("phase") == flow_codes.PARTS)

    @staticmethod
    def _hooked(offer):
        """A sendable offer's row: its key and `data-makes-stale` for the script, its label and its effect."""
        return '<li data-key="%s"%s>%s: %s</li>' % (_text(offer["key"]), _makes_stale(offer), _text(offer["label"]), _text(offer["effect"]))


class WiringHtmlFold:
    """Renderer: the wiring fold as one `<details>` that holds the wiring's `<section>` (`WiringHtmlSection`)."""

    NAME = "wiring"
    KEYS = ("phase:breadboard",)

    def text(self, page):
        """The wiring fold: its summary counts the steps, and it holds the wiring section. Open while the now holds the
        wiring (`_wiring_open`)."""
        if not page.wiring:
            return ""
        drawn = any(each.title == flow_codes.BREADBOARD_TITLE and each.svg for each in page.pictures)
        steps = [] if page.wiring.why_missing else page.wiring.steps
        summary = flow_codes.WIRING_STEPS[len(steps) != 1] % len(steps) if steps else flow_codes.WIRING_HEADING
        return _fold("wiring", _text(summary), [WIRING.text(page.wiring, drawn)], _wiring_open(page))


class PicturesHtmlFold:
    """Renderer: the pictures fold as one `<details>`: every picture of the page, in the order it was given them."""

    NAME = "pictures"
    KEYS = ()
    INLINER = SvgInliner()

    def text(self, page):
        """All the pictures in one fold, in the order the page was given them, or nothing when there are none. Open while
        the now holds the wiring (`_wiring_open`)."""
        if not page.pictures:
            return ""
        return _fold("pictures", _text(flow_codes.PICTURES_HEADING),
                     ['<section id="pictures">\n%s\n</section>' % "\n".join(self._picture(each) for each in page.pictures)],
                     _wiring_open(page))

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


class NotesHtmlSection:
    """Renderer: the page's fixed notes, the bench note among them, as one `<section class="notes">`."""

    NAME = "notes"
    KEYS = ()

    def text(self, page):
        return '<section class="notes"><h2>Notes</h2>%s</section>' % "".join("<p>%s</p>" % _text(note) for note in page.notes)


class DeveloperHtmlFold:
    """Renderer: the developer fold (P1062) as one `<details>`, always closed and last: each phase, the marks and the records."""

    NAME = "developer"
    KEYS = ("phase:*", "status:*", "by:*", "offer:*")

    def text(self, page):
        """The developer fold (P1062), always closed and last: each phase, closed, with its offers' keys and effects and no
        hook, the marks, and the line that names each record whole."""
        body = ['<section id="developer">'] + [self._phase(phase) for phase in page.phases] + [self._legend()]
        if page.wiring and page.wiring.before_power:
            body.append(WIRING.before_power.records_line(page.wiring.records))
        return _fold("developer", _text(flow_codes.DEVELOPER_HEADING), body + ["</section>"], False)

    def _phase(self, phase):
        """A phase's section in the developer fold: its heading in a `<summary>`, its text in a `<div>`, always closed. An offer
        shows its key in `<code>`, its label and its effect, with no hook: the page's buttons stand on NOW and in the folds."""
        shown = shown_phase(phase)
        lines = ['<section class="phase" %s>' % _data(phase),
                 "<details><summary><h2>%s %s <span>%s</span></h2></summary>" % (_mark(shown), _text(phase["phase"]), _text(shown.word)),
                 '<div id="phase-%s">' % _text(phase["phase"]), "<p>Done by: %s</p>" % _text(phase["by"])]
        lines += ["<p>%s</p>" % _text(said) for said in phase["says"]]
        offers = ["<li><code>%s</code> %s: %s</li>" % (_text(offer["key"]), _text(offer["label"]), _text(offer["effect"]))
                  for offer in phase["offers"]]
        return "\n".join(lines + (["<ul>%s</ul>" % "".join(offers)] if offers else []) + ["</div>", "</details>", "</section>"])

    @staticmethod
    def _legend():
        items = []
        for status, (_word, glyph) in MARKS.items():
            more = ": " + flow_codes.NOT_CHECKED_LEGEND if status is None else ""
            items.append("<li>%s %s%s</li>" % (_mark(ShownPhase(glyph, word_of(status))), _text(word_of(status)), _text(more)))
        return '<section class="legend"><h2>Marks</h2><ul>%s</ul></section>' % "".join(items)


class FlowHtmlPage:
    """
    Renderer: a FlowPage as one HTML document, the same bytes for the same page. Between its head and its script it writes
    its `SECTIONS` in order (P1123), each a small Renderer with a `NAME`, the design-basis `KEYS` it shows and `text(page)`;
    a section with nothing to show writes nothing. It names only the parts phase, for its fold (P1062), and no count. The
    colors are the praised page's tokens (P949), light and dark, with the system's fonts,
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
             "a{color:var(--ink)}a:focus-visible{outline:2px solid var(--signal)}"
             "#guide{border:1px solid var(--line);border-radius:6px;padding:2px 12px;margin:8px 0}"
             "#guide p{margin:6px 0}"
             ".now{border:1px solid var(--line);border-radius:6px;padding:2px 12px;margin:8px 0}.next{font-size:1.4em}"
             ".muted,#request{color:var(--muted)}"
             ".fold,.phase{border-top:1px solid var(--line);padding:4px 0}"
             "summary{cursor:pointer}summary h2{display:inline}"
             "p,li{overflow-wrap:anywhere}"
             "img{width:100%;max-width:100%;height:auto;max-height:88vh;object-fit:contain;background:var(--backdrop)}"
             ".fig{margin:0;overflow-x:auto;background:var(--backdrop);border:1px solid var(--line);border-radius:6px}"
             ".fig svg{display:block;width:100%;height:auto}"
             ".pads{display:flex;flex-wrap:wrap;gap:4px 18px;list-style:none;padding:0;color:var(--muted)}"
             ".sw{display:inline-block;width:14px;height:14px;border-radius:50%;margin-right:7px;vertical-align:-2px;"
             "border:1px solid var(--line)}")
    #: The page's sections, in the order it stands (P1062, P1123): a new part of the page is one more entry here.
    SECTIONS = (TitleHtmlHeading(), FreshHtmlLine(), IntroHtmlLine(), GuideHtmlSection(), StandsAtHtmlLine(),
                PartsHtmlFold(), WiringHtmlFold(), PicturesHtmlFold(), NotesHtmlSection(), DeveloperHtmlFold())

    def text(self, page):
        shown = [part for part in (section.text(page) for section in self.SECTIONS) if part]
        return "\n".join([self._open(page)] + shown + [self._script(page), "</body>", "</html>"]) + "\n"

    def _script(self, page):
        """The page's words (`page_words`) as an inert JSON block, then its one script (P829 PR 3), as one block before
        `</body>`: without it the page is the page with no script, byte for byte, but the script's hooks (`data-makes-stale` on
        a sendable offer, and `data-key` with it on the NOW box's NEXT line, `sendable_now`).
        A `<` in the words is written `\\u003c`, so no text closes the block."""
        words = json.dumps(page_words(page.phases), ensure_ascii=False, sort_keys=True).replace("<", "\\u003c")
        return '<script type="application/json" id="%s">%s</script>\n<script>%s</script>' % (
            WORDS_ID, words, PAGE_SCRIPT.read_text(encoding="utf-8"))

    def _open(self, page):
        style = token_styles(self.TOKENS_LIGHT, self.TOKENS_DARK) + self.STYLE + (WIRING.STYLE if page.wiring else "")
        return "\n".join(['<!doctype html>', '<html lang="en">', '<head>', '<meta charset="utf-8">',
                          '<meta name="viewport" content="width=device-width, initial-scale=1">',
                          '<title>%s</title>' % _text(page.title), '<style>%s</style>' % style, '</head>',
                          '<body data-stands-at="%s" data-fingerprint="%s" data-written="%s">' % (
                              _text(page.stands_at or "none"), _text((page.fingerprint or "none")[:SHORT]), _text(page.written or "none"))])
# --- end MVP ---
