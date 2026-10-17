# P272 plan: the same page as an Artifact (#308)

Card: "Step 4: the same page as an Artifact. Done when: the same bundled file opens as an Artifact." The PO, 2026-10-16:
"ideally if reusable for the artifact and later even some electron version". Brief D5 (Mac page, then Artifact) and D8
(order). The page is P271's `page.html`.

> **TL;DR.** `page.html` gets Artifact-ready CSS (color tokens, a dark mode, a 16 px gutter, a 2 to 4 word title) so the
> same file serves the browser, the Artifact and a later Electron window. The docs tell Claude how to publish it, with
> the person's yes. The builder publishes nothing; one private publish by Claude, after the PO's yes, closes the card.

The page gets plain Artifact CSS in `TabbedHtmlPage` and a `page_title` function. No new file, no script, no flag. The tests
prove the page obeys the rules; only the private publish proves the host opens it.

## Context

Spark's scripts cannot publish an Artifact. Claude publishes one with its Artifact tool, from a file. So the work has
two parts: make `page.html` obey the Artifact page rules, and tell Claude how to publish it. One file must serve the Mac
browser, the Artifact and a later Electron window. Electron loads a plain HTML file with no script, so the answer is a
page that is plain, self-contained and follows the Artifact rules everywhere. No second file, no flag.

## Council

Rebased on main after P273 (#339); line numbers re-read (`check_spine.py:835` is the only one that moved).

### Round 1 (tech lead on sonnet, refuter on opus)

Changes made to the plan:

- The nested skeleton is decided now. The host wraps the file in its own doctype/html/head/body, and the refuter saw two
  `<title>` elements, the host's first. Decision: keep the full document, no flag. A plain browser and Electron need
  the doctype, and the styles, radio tabs and tokens still work when nested. If the private publish shows a harm, the
  fallback is a fragment variant (`<meta>`, `<title>`, `<style>`, then the content), named here, not built.
- `page_title` becomes a module function beside `exported_tab`, not a static method: a Renderer decides nothing.
  Rules: split on `-`, `_`, `.`; drop empty words; first three words; cap each word at 20 characters; no words gives
  "spark circuit". Tests: `---`, `__`, a 300-character word, `Světlo-tlačítko`, `2026-10-17`, `keep`.
- Gutter: name the rules: `nav{padding:0 16px}` and `.panel{padding:12px 16px}`; tested by regex, not by finding
  "16px" anywhere.
- Horizontal scroll: a missing tab's reason can be a long path with no break point (788 px wide at 400 px). Add
  `p{overflow-wrap:anywhere}`. Add `max-width:100%` to `.panel img`. Both tested.
- Colors: the picture ground is the token `--backdrop`, white in both sets. The "no hard-coded color" test looks for
  hex, `rgb(`, `hsl(` and color names outside the token blocks. Every `var(--x)` used must be defined on bare `:root`,
  and the dark set has the same keys as the light set.
- The tab underline uses `var(--accent)`. The two dark blocks come from one dict, so they hold the same values.
- The 5 MB size test is dropped: no code enforces a limit, and the test always passes.
- Docs: the publish step says what to do on failure (report it, never retry in a loop) and that `icon` is for the
  first publish only. Tests and docs that quote `PURPOSE_MESSAGE` are grepped.
- Mutation table entries: the guard removed, the dark block left out of the media query, the word cut, the empty
  fallback, the gutter 16 to 12, `--paper` unused by body, the `overflow-wrap` rule.
- `--keep .` is the documented use, so the title comes from the project folder's name. The plan keeps that source.

Rejected: the doubt about the white backdrop in dark mode (it works; side bands from `object-fit` are checked by eye).

### Round 2 (tech lead and PO assistant, both sonnet)

- TL;DR and a three-sentence summary now open the plan (the PO's reply layers).
- The done line is split. The PR proves "the page obeys the Artifact rules", by tests. "It opens as an Artifact" is
  proved only by one private publish, by Claude after the PO's yes. Until then the card stays open at "partly", and
  no README row or journey picture changes status. The PR says so. A third host question asks for that publish.
- `page_title` splits on `re.split(r"[\s\-_.]+", name)`, drops empty words, keeps the first three, cuts each to 20
  characters, and adds "circuit"; no words gives "spark circuit". Examples, each an `assertEqual`:
  `button-light-xiao` gives "button light xiao circuit"; `keep` gives "keep circuit"; `2026-10-17` gives
  "2026 10 17 circuit"; `a-b-c-d` gives "a b c circuit"; `my cool robot project` gives "my cool robot circuit";
  `---`, `__` and "" give "spark circuit"; 300 letters give the first 20 plus " circuit"; `Světlo-tlačítko` gives
  "Světlo tlačítko circuit".
- The call site is `tabbed_page.page_title(Path(destination).resolve().name)` in `check_spine.keep_tabbed_page`.
  `text(tabs, title="spark")` keeps its default.
- The tab underline color is set in the `shown` loop (`border-color:#c33`), not in STYLE. It becomes
  `border-color:var(--accent)`, and a test asserts no `#c33`.
- Gutter rules to add or change: `nav{padding:0 16px}` (new) and `.panel{display:none;padding:12px 16px}`. Tests use the
  regexes `nav\{[^}]*padding:0 16px` and `\.panel\{[^}]*padding:12px 16px`.
- The color test strips `data:` URIs and reads only the `<style>` text outside the `:root` blocks, so base64 and a
  missing-tab reason cannot match a color name.
- Add a test that reads `<title>` from `text(..., title=...)` and from the kept page (`test_check_spine.py`).
- Mutation entries each use one unique anchor (`tools/mutate.py` refuses a `find` that matches twice), and the table
  is `tests/mutations/p272-page-as-artifact.json`. The dark values are written once, so the "printed twice" entry
  anchors on the media-query guard string. Cut to what the mutation-tester runs: guard, dark block, word cut, empty
  fallback, gutter, `--paper` in body, `overflow-wrap`.
- Docs: nothing quotes `PURPOSE_MESSAGE` text, so the append breaks no test. Update `--help` at `check_spine.py:643`,
  `agents.md`, `commands/build.md`, `journey.md:470`. The README line 56 and `tools/journey.py` stay, since no
  step status changes.

Rejected: none. Two points kept as they were: the dark-mode machinery and the 7-entry table, because each serves a
stated Artifact rule.

## Gaps found

I built `tests/data/breadboard/button-light-xiao` with `check_spine.py --keep` in a scratch folder (311 KB page).

| Artifact rule | Today | Gap |
|---|---|---|
| One HTML file | `page.html`, pictures as data URIs | none |
| `<title>` of 2 to 4 words | the folder name, here `keep` (`check_spine.py:835`, `tabbed_page.py:95`) | yes: one word, or a hyphen slug |
| Color tokens on `:root` | hard-coded `#f6f3ee`, `#222`, `#fff`, `#c33` (`tabbed_page.py:79-83,92`) | yes |
| Dark mode, two blocks (`prefers-color-scheme` guarded by `:root:not([data-theme="light"])`, and `:root[data-theme="dark"]`) | none | yes |
| Explicit body background | set, `tabbed_page.py:79` | none (moves to a token) |
| Scripts only from the five hosts | no `<script>`, no `http` (grep count 0) | none |
| Stylesheets only from Google Fonts | none, font is `system-ui` | none |
| Phone width, 16px side gutter, no sideways scroll | viewport meta is set (`:94`); the panel gutter is 12px (`:82`); the tab labels wrap | gutter is 12px, not 16px |
| At most 16 MB | 311 KB | none |
| Unknown: the host may block `data:` images | not known | test at the private publish |
| The host wraps the page in its own skeleton (the contract says so) | ours nests; a second `<title>` lands in the body, the host's first | decided in round 1: keep the full document; host question for the PO below |

## Design

Smallest change: `TabbedHtmlPage` writes Artifact-ready CSS and a 2 to 4 word title, always. A browser needs nothing
more, and `data-theme` is simply unused outside the host.

```
TabbedHtmlPage            (scripts/tabbed_page.py, existing)
  FILE_NAME, NOUN, PURPOSE_MESSAGE
  TOKENS_LIGHT / TOKENS_DARK   <- new: one dict of color tokens per scheme
  STYLE                         <- uses var(--paper) and so on, gutter 16px
  text(tabs, title)             <- emits the token blocks, then STYLE
  page_title(name)  (module function beside exported_tab) <- new: "<name> circuit", 2 to 4 words
check_spine.keep_tabbed_page  -> TabbedHtmlPage.page_title(folder name)
```

- Tokens: `--paper` (body), `--ink` (text), `--backdrop` (picture ground), `--accent` (active tab). The dark set is
  written once and printed twice: in the media query with the `:root:not([data-theme="light"])` guard, and under
  `:root[data-theme="dark"]`. The picture backdrop stays white in both schemes, because tscircuit's SVGs and spark's
  breadboard assume a light ground (to confirm by eye).
- `page_title`: the folder name with `-` and `_` read as spaces, cut to the first three words, plus "circuit". An empty
  name gives "spark circuit". The result has 2 to 4 words.
- Gutter: `.panel` and `nav` get 16px left and right.
- `PURPOSE_MESSAGE` adds ", and Claude can publish it as an Artifact". One list, one place.
- No script, no web fetch, no new file, no new class. Electron later loads the same file.

## How Claude publishes it (docs)

A short step for `docs/guide/agents.md` and `commands/build.md`, under the `page.html` text:

1. Ask the person first: "Publish this page as an Artifact?" Publishing is the person's choice. Spark never does it.
2. Call the Artifact tool with `file_path` set to the full path of `page.html` and `icon` set to `circuit`. The page is
   private by default. Give the person the link.
3. To update, call it again with the same `file_path` after a rebuild.

The step names no new command. An agent without the Artifact tool skips it and opens the file.

## Tests, written first

In `tests/test_tabbed_page.py`, each fails before the code:

- the page has `:root{` with the four tokens, and the body uses `var(--paper)`;
- the dark tokens appear twice: under `@media (prefers-color-scheme: dark)` with `:root:not([data-theme="light"])`,
  and under `:root[data-theme="dark"]`, with the same values;
- no hard-coded color outside the token blocks;
- no `<script`, and no `http` in `href`, `src` or `@import`;
- `page_title("button-light-xiao")` has 2 to 4 words; the empty name and a long name hold too;
- the panel gutter is 16px;

In `tests/test_check_spine.py`: the kept page's title has 2 to 4 words. Run a mutation check on the title and the dark
block. `tests/test_journey.py` stays green: the README row for this step moves in the same PR.

## Docs

`docs/guide/agents.md` and `commands/build.md` (the publish step), the README "What works today" row and
`tools/journey.py` (step 4), and the `--help` line of `check_spine.py` if it names the page. Plain English, short.

## Verification

1. The new tests fail, then pass. The full suite passes.
2. Rebuild button-light-xiao with `--keep` and a scratch `SPARK_HOME`. Open it in a browser in light and dark mode, and
   at 390 px width: no sideways scroll, all three tabs switch.
3. One private test publish, by hand at the end, by Claude, not by a script: the Artifact tool with the kept
   `page.html`. Check that the three pictures show (the `data:` risk), the tabs switch, dark mode follows the host, and
   the phone width works. Record the result in the PR. If the host blocks `data:` images, the card stops and the PO
   decides.
4. Delete the test Artifact afterwards, with the PO's yes.

## Open host questions (go into the PR, for the PO's private publish)

1. Does the host show the `data:` images? If not, the card stops and the PO decides.
2. Which `<title>` does the host use when our nested document brings its own, and do the tabs and tokens still work?
   If it harms, build the fragment variant named in round 1.

3. Does the PO approve one private test publish of the kept `page.html` by Claude, and who deletes it afterwards?

This builder publishes nothing.

## Out of scope

Publishing by a script or an MCP server, sharing links, Artifact capabilities (database, comments), editing in the
page (step 5), an Electron shell, a theme switch inside the page, any change to the three pictures.
