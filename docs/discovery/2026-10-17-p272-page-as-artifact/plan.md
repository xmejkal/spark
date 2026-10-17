# P272 plan: the same page as an Artifact (#308)

Card: "Step 4: the same page as an Artifact. Done when: the same bundled file opens as an Artifact." The PO, 2026-10-16:
"ideally if reusable for the artifact and later even some electron version". Brief D5 (Mac page, then Artifact) and D8
(order). The page is P271's `page.html`.

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

(Round 2 is filled below when it finishes.)

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

This builder publishes nothing.

## Out of scope

Publishing by a script or an MCP server, sharing links, Artifact capabilities (database, comments), editing in the
page (step 5), an Electron shell, a theme switch inside the page, any change to the three pictures.
