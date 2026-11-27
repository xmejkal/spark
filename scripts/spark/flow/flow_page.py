"""
The page of a project (P827, #1185): the flow's phases as one plain HTML file, `page.html`, each with a status word and a
mark, readable from disk. `FlowPage` is the Value a renderer takes; `FlowHtmlPage` is the Renderer that draws it, as an
ordered table of sections (`SECTIONS`, P1123, whose Renderers live in `page_sections`, P1128) in the slice 1 order
(P1062): the freshness line, the station line (P1119), the NOW box, the Parts, Wiring and Pictures folds, the bench note,
and the developer fold, always closed. The page adds no tick of its own: a phase whose status is not ok never shows one (`shown_phase`). It
writes the same bytes for the same flow. It loads the font's stylesheet from fonts.googleapis.com (P1120), which then
loads the font files from fonts.gstatic.com; Google gets each visitor's IP address and browser string (User-Agent), and
from a published page its origin. With no network the page uses the system fonts. Its one script (P829 PR 3) does
nothing from disk; `page_words` writes its words. The breadboard stands in it as plain shapes (`SvgInliner`, P949) with
its keys for a player and a legend of its pads; every other picture is an <img>.
"""

import json
from collections import namedtuple
from pathlib import Path

from spark.breadboard.tabbed_page import token_styles
from spark.flow import flow_codes, request_codes
from spark.flow.fingerprint import SHORT
from spark.flow.page_sections import (WIRING, DeveloperHtmlFold, FreshHtmlLine, GuideHtmlSection, IntroHtmlLine, NotesHtmlSection,
                                      PartsHtmlFold, PicturesHtmlFold, StandsAtHtmlLine, StationsHtmlLine, TitleHtmlHeading,
                                      WiringHtmlFold, _text)
from spark.flow.flow_codes import effect_lines, quoted
from spark.flow.phase_readers import MARKS, pick_need
from spark.core.outcomes import COULD_NOT_RUN, OK, PROBLEMS
from spark.core.zone_time import MONTHS

# --- MVP ---
#: Value: one picture of the project: its title, its SVG text or None, and why there is none. The page keeps no renderer's
#: type, so whoever has another kind of picture (a tab) converts it.
Picture = namedtuple("Picture", "title svg why_missing")
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

#: The page's one script (P829 PR 3): it adds the buttons only in a published page with the Artifact database, and does
#: nothing from disk. Its words stand beside it in an inert JSON block with WORDS_ID.
PAGE_SCRIPT = Path(__file__).resolve().with_name("page_script.js")
WORDS_ID = "spark-words"
#: The page's font (P1120, the PO's choice): Instrument Sans, the canvas's, in its two weights. `display=swap` shows the
#: system's fonts at once and with no network. The address holds nothing of the project.
FONT_STYLESHEET = "https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;600&display=swap"


def page_words(phases):
    """
    Every word the page's script shows (P829 PR 3, the plan's section 9), as one dict: per sendable offer its label (the
    button and the confirm's title) and the confirm's lines (its effect, the phases it may make out of date, the wait),
    the fixed words of the buttons and the status line, and the words of each answer. A refusal's words are keyed by
    its code's meaning, the `line` that `flow.py run-request` answers. The script fills in a time, a label or a line.
    `intro` is the published page's intro, `last_request` the line of the last request, `months` the month words of its
    time, and `request_kinds` and `request_other` its words when its offer left the page (P1062). `copied` is what Copy says
    once it copied a chat offer's tell (P1122). A pick's words also hold its `need`, and the words of several picks in one
    Send are the ones with `picks` in their name (P1067). A pick's confirm lines are its effect's (`effect_lines`, P1135),
    so the sentences every pick of the project says stand apart and once in a Send of several. `keep` names the first radio
    of each picked need: its picks.
    """
    offers = {}
    for offer in (offer for phase in phases for offer in phase["offers"] if flow_codes.is_sendable(offer["key"])):
        stale = [flow_codes.CONFIRM_STALE % ", ".join(offer["makes_stale"])] if offer["makes_stale"] else []
        need = pick_need(offer["key"])
        words = {"label": offer["label"], "says": (effect_lines(offer["effect"]) if need else [offer["effect"]]) + stale}
        offers[offer["key"]] = dict(words, need=need) if need else words
    keep = {need["need"]: flow_codes.KEEP_PICK % quoted(need["picked"]) for phase in phases for need in phase.get("needs") or []
            if need["picked"]}
    meanings = {str(code): meaning for code, meaning in request_codes.CODES.items()}
    marks = {status: MARKS[status][1] for status in (OK, PROBLEMS, COULD_NOT_RUN)}
    return {"offers": offers, "keep": keep, "send": flow_codes.SEND, "cancel": flow_codes.CANCEL, "copy": flow_codes.COPY, "copied": flow_codes.COPIED_SAYS,
            "withdraw": flow_codes.WITHDRAW, "command": flow_codes.PAGE_COMMAND, "waiting": flow_codes.WAITING_SAYS,
            "now_button": flow_codes.NOW_BUTTON,
            "withdrawn": flow_codes.WITHDRAWN_SAYS, "waiting_for": flow_codes.WAITING_FOR, "last_request": flow_codes.LAST_REQUEST_SAYS,
            "not_sent": flow_codes.NOT_SENT_SAYS, "not_withdrawn": flow_codes.NOT_WITHDRAWN_SAYS,
            "intro": flow_codes.PUBLISHED_INTRO, "months": list(MONTHS),
            "request_kinds": dict(flow_codes.LAST_REQUEST_KINDS), "request_other": flow_codes.LAST_REQUEST_OTHER,
            "ok": dict(flow_codes.RAN_OK_SAYS), "ran": flow_codes.RAN_OTHER_SAYS, "note": flow_codes.RAN_NOTE_SAYS, "problems": flow_codes.RAN_PROBLEMS_SAYS,
            "could_not_run": flow_codes.COULD_NOT_RUN_SAYS,
            "refused": {meanings[name]: said for name, said in flow_codes.REFUSED_SAYS.items()},
            "refused_picks": {meanings[name]: said for name, said in flow_codes.REFUSED_PICKS.items()},
            "not_now": flow_codes.NOT_NOW, "picks_said": list(flow_codes.PICKS_SAID), "send_picks": flow_codes.SEND_PICKS,
            "choose_first": flow_codes.CHOOSE_FIRST, "picks_together": flow_codes.PICKS_TOGETHER_MESSAGE,
            "waiting_picks": flow_codes.WAITING_PICKS_SAYS, "ok_picks": flow_codes.RAN_OK_PICKS_SAYS,
            "last_request_picks": flow_codes.LAST_REQUEST_PICKS, "needs_join": flow_codes.NEEDS_JOIN, "label_join": flow_codes.LABEL_JOIN,
            "no_pick_saved": flow_codes.NO_PICK_SAVED_SAYS,
            "marks": dict(marks, **{"not-run": flow_codes.NOT_RUN_MARK})}


#: The station line's style (P1119): twelve equal cells in a row. Each cell's `::before` is the 2px segment that leads to it,
#: solid ink up to now and dashed muted after it, dotted for an unbuilt step after a thin divider; the first has none. A
#: note's words stand small and muted under the name (the PO's "Visible note"). A mark
#: stands on the ground over its segment, and each now station's mark has a 2px ink ring. Only ink and muted: no teal. On a
#: phone the names and notes are clipped (a screen reader still reads them), the marks are 14px and the caption, of no height
#: elsewhere, names the now stations on one line.
STATIONS_STYLE = (".stations{display:flex;list-style:none;padding:0;margin:var(--space-l) 0 var(--space-s)}"
                  ".stations>li{flex:1 1 0;min-width:0;position:relative;text-align:center;overflow-wrap:normal}"
                  ".stations>li::before{content:\"\";position:absolute;top:13px;left:-50%;width:100%;border-top:2px solid var(--ink)}"
                  ".stations>li:first-child::before{content:none}"
                  ".stations>[data-place=\"later\"]::before{border-top:2px dashed var(--muted)}"
                  ".stations>.unbuilt::before{border-top:2px dotted var(--muted)}"
                  ".stations>li:not(.unbuilt)+.unbuilt{border-left:1px solid var(--muted)}"
                  ".stations .mark{position:relative;display:inline-block;box-sizing:border-box;width:28px;height:28px;"
                  "line-height:24px;border:2px solid transparent;border-radius:50%;background:var(--bg)}"
                  ".stations [aria-current] .mark{border-color:var(--ink)}"
                  ".stations .unbuilt .mark{border:2px dotted var(--muted)}"
                  ".stations .name{display:block}.stations .note{display:block;font-size:13px;line-height:1.3;color:var(--muted)}"
                  ".unbuilt{color:var(--muted)}"
                  ".clip{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}"
                  ".stations-now{max-height:0;overflow:hidden;white-space:nowrap;margin:0}"
                  "@media (max-width: 600px){.stations .name,.stations .note{position:absolute;width:1px;height:1px;overflow:hidden;"
                  "clip:rect(0 0 0 0);white-space:nowrap}.stations .mark{width:14px;height:14px;line-height:10px;font-size:10px}"
                  ".stations>li::before{top:6px}.stations-now{max-height:none;margin:0 0 var(--space-s)}}")


class FlowHtmlPage:
    """
    Renderer: a FlowPage as one HTML document, the same bytes for the same page. Between its head and its script it writes
    its `SECTIONS` in order (P1123), each a small Renderer with a `NAME`, the design-basis `KEYS` it shows and `text(page)`;
    a section with nothing to show writes nothing. It names only the parts phase, for its fold (P1062), and no count. Its
    colors are tokens (P1120), light and dark, with the linked font then the system's. Teal is only a button's fill, the confirm frame's
    edge or the focus ring. The Now box is an ink plane whose dot's halo is a `::before` border, as the page has no shadow.
    No color says a status: the mark and the word do. Under an inline breadboard a legend names each pad state its dots
    draw, and only those.
    """

    FILE_NAME = "page.html"
    NOUN = "page"
    PURPOSE_MESSAGE = "where the project stands, phase by phase, with its pictures: open it in a browser"

    #: The colors by token, light and dark (P1120: the P1113 council's light set, the PO's dark set of 2026-11-25); the shape
    #: and font tokens are light's only. The picture ground stays white in both, as the tabbed page's: the pictures are drawn
    #: for a light ground. The font is the linked one (`FONT_STYLESHEET`), then the system's, which draw it with no network.
    TOKENS_LIGHT = {"--bg": "#f6f5f1", "--surface": "#ffffff", "--ink": "#15181d", "--muted": "#5b6270", "--line": "#e4e1d8",
                    "--accent": "#0f766e", "--accent-hover": "#0b5c56", "--on-accent": "#ffffff", "--accent-edge": "#0f766e",
                    "--focus": "#0f766e", "--now-bg": "#15181d", "--now-ink": "#f6f5f1", "--now-halo": "#5eead4",
                    "--amber-ink": "#92400e", "--amber-plane": "#fef3c7", "--red-ink": "#b42318", "--red-plane": "#fee4e2",
                    "--backdrop": "#fff", "--radius-button": "8px", "--radius-frame": "12px", "--button-height": "44px",
                    "--size-text": "16px", "--size-heading": "20px", "--size-title": "40px", "--space-s": "8px",
                    "--space-m": "12px", "--space-l": "16px",
                    "--body": '"Instrument Sans",system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif'}
    TOKENS_DARK = {"--bg": "#121417", "--surface": "#1b1e24", "--ink": "#eceae4", "--muted": "#a3a9b5", "--line": "#2e333b",
                   "--accent": "#0f766e", "--accent-hover": "#0b5c56", "--on-accent": "#ffffff", "--accent-edge": "#5eead4",
                   "--focus": "#5eead4", "--now-bg": "#23272f", "--now-ink": "#eceae4", "--now-halo": "#5eead4",
                   "--amber-ink": "#fcd34d", "--amber-plane": "#3a2a0b", "--red-ink": "#fca5a5", "--red-plane": "#3b1214",
                   "--backdrop": "#fff"}
    #: Kind 1, teal, is spark's step: a sendable offer's button and Send (the confirm's first), never a disabled one; kind 2, an
    #: outline, is every other. Until P1115 the selectors read where the script puts a button. While the confirm shows, the
    #: offer's own button is an outline again, so Send is the one teal button. A disabled offer on the Now plane keeps its halo
    #: edge, since without it the dark edge is 1.18:1 against the plane; the grey fill still says disabled.
    #: A part chosen in a need's row (P1135) gets a teal edge on the pale ground, as the canvas draws it, not a ring.
    STYLE = ("body{max-width:1180px;margin:0 auto;padding:var(--space-m) var(--space-l);"
             "font:var(--size-text)/1.55 var(--body);background:var(--bg);color:var(--ink)}h1,h2{font-weight:600;"
             "line-height:1.2;letter-spacing:-0.02em}h1{font-size:var(--size-title);line-height:1.1}"
             "h2{font-size:var(--size-heading)}strong{font-weight:600}a{color:var(--ink)}.now a{color:var(--now-ink)}a:focus-visible,"
             "button:focus-visible,summary:focus-visible{outline:2px solid var(--focus);outline-offset:2px}"
             "button{min-height:var(--button-height);padding:0 var(--space-l);border:1px solid var(--ink);"
             "border-radius:var(--radius-button);background:var(--surface);color:var(--ink);"
             "font:600 var(--size-text)/1 var(--body);cursor:pointer}button+button{margin-left:var(--space-s)}"
             "[data-makes-stale]>button:not(:disabled),"
             "[data-makes-stale] [role=group]>button:first-of-type:not(:disabled){background:var(--accent);"
             "border-color:var(--accent);color:var(--on-accent)}[data-makes-stale]>button:hover:not(:disabled),"
             "[data-makes-stale] [role=group]>button:first-of-type:hover:not(:disabled){background:var(--accent-hover);"
             "border-color:var(--accent-hover)}[data-makes-stale]:has(>[role=group])>button:not(:disabled),"
             "[data-makes-stale]:has(>[role=group])>button:hover:not(:disabled){background:var(--surface);border-color:var(--ink);"
             "color:var(--ink)}.now [data-makes-stale]>button,"
             ".now [data-makes-stale]>button:hover{border-color:var(--now-halo)}"
             "button:disabled{background:var(--line);border-color:var(--line);color:var(--muted);cursor:not-allowed}"
             "#guide,.fold,[role=group]{border:1px solid var(--line);border-radius:var(--radius-frame);"
             "background:var(--surface);padding:var(--space-s) var(--space-l);margin:var(--space-s) 0}"
             "[role=group]{color:var(--ink);font-size:var(--size-text)}"
             "[data-makes-stale] [role=group]{border-color:var(--accent-edge)}"
             "[data-need] label{border:2px solid transparent;border-radius:var(--radius-button);padding:0 var(--space-s)}"
             "[data-need] label:has(:checked:not([value=\"\"]):not(:disabled)){background:var(--bg);"
             "border-color:var(--accent-edge)}"
             "#guide p{margin:var(--space-s) 0}.now{background:var(--now-bg);color:var(--now-ink);"
             "border-radius:var(--radius-frame);padding:var(--space-s) var(--space-l);margin:var(--space-s) 0}"
             ".now>p:first-child::before{content:\"\";display:inline-block;width:8px;height:8px;"
             "margin-right:var(--space-s);border:2px solid var(--now-halo);border-radius:50%;vertical-align:1px}"
             ".next{font-size:var(--size-heading)}.muted,#request{color:var(--muted)}"
             ".ask code{display:block;margin:var(--space-s) 0;padding:var(--space-s) var(--space-m);background:var(--bg);"
             "color:var(--ink);border:1px solid var(--line);border-radius:var(--radius-button);overflow-wrap:anywhere}"
             ".plane-amber{color:var(--amber-ink);background:var(--amber-plane);"
             "border-left:3px solid var(--amber-ink);padding:0 var(--space-s)}.plane-red{color:var(--red-ink);"
             "background:var(--red-plane);border-left:3px solid var(--red-ink);padding:0 var(--space-s)}"
             ".phase{border-top:1px solid var(--line);padding:4px 0}summary{cursor:pointer}summary h2{display:inline}"
             "p,li{overflow-wrap:anywhere}img{width:100%;max-width:100%;height:auto;max-height:88vh;"
             "object-fit:contain;background:var(--backdrop)}.fig{margin:0;overflow-x:auto;background:var(--backdrop);"
             "border:1px solid var(--line);border-radius:var(--radius-frame)}.fig svg{display:block;width:100%;"
             "height:auto}.pads{display:flex;flex-wrap:wrap;gap:4px 18px;list-style:none;padding:0;"
             "color:var(--muted)}.sw{display:inline-block;width:14px;height:14px;border-radius:50%;margin-right:7px;"
             "vertical-align:-2px;border:1px solid var(--line)}" + STATIONS_STYLE)
    #: The page's sections, in the order it stands (P1062, P1123): a new part of the page is one more entry here.
    SECTIONS = (TitleHtmlHeading(), FreshHtmlLine(), IntroHtmlLine(), StationsHtmlLine(), GuideHtmlSection(), StandsAtHtmlLine(),
                PartsHtmlFold(), WiringHtmlFold(), PicturesHtmlFold(), NotesHtmlSection(), DeveloperHtmlFold())

    def text(self, page):
        shown = [part for part in (section.text(page) for section in self.SECTIONS) if part]
        return "\n".join([self._open(page)] + shown + [self._script(page), "</body>", "</html>"]) + "\n"

    def _script(self, page):
        """The page's words (`page_words`) as an inert JSON block, then its one script (P829 PR 3), as one block before
        `</body>`: without it the page is the page with no script, byte for byte, but the script's hooks (`data-makes-stale` on
        a sendable offer, `data-key` with it on the NOW box's NEXT line, `sendable_now`, and `data-need` on a need's row, P1067).
        A `<` in the words is written `\\u003c`, so no text closes the block."""
        words = json.dumps(page_words(page.phases), ensure_ascii=False, sort_keys=True).replace("<", "\\u003c")
        return '<script type="application/json" id="%s">%s</script>\n<script>%s</script>' % (
            WORDS_ID, words, PAGE_SCRIPT.read_text(encoding="utf-8"))

    def _open(self, page):
        style = token_styles(self.TOKENS_LIGHT, self.TOKENS_DARK) + self.STYLE + (WIRING.STYLE if page.wiring else "")
        return "\n".join(['<!doctype html>', '<html lang="en">', '<head>', '<meta charset="utf-8">',
                          '<meta name="viewport" content="width=device-width, initial-scale=1">',
                          '<title>%s</title>' % _text(page.title), '<link rel="stylesheet" href="%s">' % _text(FONT_STYLESHEET),
                          '<style>%s</style>' % style, '</head>',
                          '<body data-stands-at="%s" data-fingerprint="%s" data-written="%s">' % (
                              _text(page.stands_at or "none"), _text((page.fingerprint or "none")[:SHORT]), _text(page.written or "none"))])
# --- end MVP ---
