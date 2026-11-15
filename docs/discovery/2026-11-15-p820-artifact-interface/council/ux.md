# P820 council: the UX and AI-UX lens
<!-- Tags: E with a pointer, H with its source, D with who and when. — is an unknown. Read-only lens · decides nothing.
Model: Opus. Read 2026-11-15 (Europe/Prague). -->

## Findings

Format: UX-n · claim · tag · pointer · supports only.

### A. What the PO's favourite page actually is

- UX-1 · The page the PO praises ("the breadboard with the nice pictures and the step by step guide") is not the page spark generates. spark's `page.html` is three CSS tabs (Breadboard, Schematic, PCB), each one picture in an `<img>`, with no numbered steps, no text and no script. The numbered steps exist only in `breadboard.md`. The pages with pictures and a step-by-step guide are two Artifacts that Claude wrote by hand on 2026-11-11 in the sound session: "Wire the rotary encoder, step by step" and "FireBeetle 2 Amplifier Wiring". · E · `scripts/spark/breadboard/tabbed_page.py:2-11,107-126`; `spark-walks/t-display/page.html` (labels Breadboard, Schematic, PCB; the Breadboard tab holds only "not drawn, because no Wokwi pin positions for board-esp32-devkit-c-v4"); `list_artifacts`, read 2026-11-15: slugs `d142d2e6-283c-4a39-a44a-60f1379702cb` (version 1794388998-a9a7) and `fae148e7-10c7-417b-9f3e-2c5d2b897923` (version 1794390569-b2bf), both contract 0.0.0 · supports only: "standardize the breadboard look" means turning a hand-made page into a generated one. Which of the two pages he meant is —. That he meant these rather than page.html is H (the dates and titles match his words; he did not name one).
- UX-2 · What the hand-made pages do, element by element, is a ready template. The encoder page: one picture at the top; a card with a progress bar, a colored numbered chip, a step title and one paragraph; Back and Next buttons and the arrow keys; in the picture the wire of the current step draws itself, earlier wires stay solid, later wires are hidden, and a ring pulses around the pads the step is about; the last step hands back to the chat ("Plug the USB-C cable back in. Tell Claude “wired” and the three readings"). The amplifier page adds: a red-bordered warning block ("Unplug USB before you wire"), a wire table with a color swatch and the color's name, a "Which pad belongs to whom" table with a State column ("in place, do not use", "wire now, same as before", "kept free for later", "later"), a guide with two modes ("All at once", "Step by step") and a "Where each fact comes from" list. · E · encoder artifact (its STEPS array, the `.now`, `.done`, `.later` and `.glow` classes, step 8's text); amplifier artifact (its `.warn` section, the tables, the `g-all`, `g-step` buttons, the provenance section), both read 2026-11-15 · supports only: these parts exist and work in one session's pages. Which parts the PO values most is —.
- UX-3 · Both hand-made pages say how sure each fact is, in prose, at the end: "estimated from your photo", "about right, not measured", "Nobody measured whether the gap breaks the rail", "These pins are a proposal, and nothing has tested them yet", "nobody confirmed that each pair is joined. A meter confirms it in one touch", "Peak current: not published · part record, null". This is spark's never-assume rule written per fact, but in free text, with no marker a person can scan and no field Claude can read. · E · amplifier artifact, the display table rows "Peak current" and "Glass outline position" and the "Where each fact comes from" list; encoder artifact, its last card · supports only: the pages already carry the doubt. A scannable, structured form of it does not exist yet.
- UX-4 · The hand-made pages were typed by Claude from spark's files: the encoder page cites "spark's breadboard sheet for P758 (`build/breadboard.md`, steps 5, 7, 23, 28 and 29)" and holds its own copy of the steps in a script array. Nothing ties that copy to the sheet, so a rebuild changes the sheet and not the page. The P269 council already saw the sheet and the picture disagree once (USER-3 there). · E · encoder artifact, the first item of its provenance card and its `STEPS` constant; `docs/discovery/2026-10-16-p269-views-and-editors/council/user.md:12` · supports only: a hand page can go stale. Whether one did is —.
- UX-5 · Generating the page loses what the hand pages took from sources that spark's records do not hold: pad positions read from DFRobot's overview picture, the encoder's place from a bench photo, the warning that RX and TX belong to the serial console until the games start, the 1 kΩ meter threshold. Spark's own sheet has none of these. A generated page will look plainer than the page he praised, unless the records grow those facts (pictures, positions) first. · E for the sources (amplifier artifact's provenance list: "DFRobot's board overview for V1.2", "your bench photo of 2026-11-10"; walk3-rehearsal diary lines 113-129, "spark holds no picture of the board"); H that he will judge the generated page against the hand-made one (P269 USER-26: "He will judge by picture first", `council/user.md:41`) · supports only: the first generated slice risks reading as a step back.
- UX-6 · Rule conflicts between the hand pages and spark's kept page: both hand pages load IBM Plex from fonts.googleapis.com, while the kept page "has no script and loads nothing from the web"; the encoder page's dark palette sits under a bare `@media (prefers-color-scheme:dark){:root{…}}`, with no `:not([data-theme="light"])` guard and no `:root[data-theme="dark"]` block, so a viewer who picks light on a dark system gets dark, and one who picks dark on a light system gets light. The amplifier page and `tabbed_page.py` have both guards. · E · encoder artifact `<style>` head; amplifier artifact `<style>` head; `tabbed_page.py:96-105`; `commands/build.md:160` ("It has no script and loads nothing from the web"); the Artifact design guide (claude-artifacts `guide` topic design, read 2026-11-15: "Redefine the tokens under @media (prefers-color-scheme: dark), guarded as :root:not([data-theme="light"])" and again under `:root[data-theme="dark"]`) · supports only: the standard has to pick one rule for fonts and one theme block shape, and a test can pin it.

### B. Layout options for one page per project

- UX-7 · Option A, a step rail beside one panel, with a next-step panel. A vertical list of the eight steps on the left, each with its state; the chosen step's content in the middle; a fixed panel that names the next action and who does it. It fits a non-linear journey, where a person goes back to change a pick after a build (the build then lists the bench changes, P300). Design systems agree a non-linear stepper lets any step be opened and keeps completed steps marked and reachable; one drops the progress bar for a non-linear stepper because its meaning is unclear. · H (my design reading) · E for the pattern: Morningstar stepper blog (https://designsystem.morningstar.com/whats-new/blog/new-year-new-stepper), Material steppers (https://m1.material.io/components/steppers.html), Toyota CDS stepper (https://dx-playbook.toyota-europe.com/cds/components/forms/stepper/), search results read 2026-11-15, pages not opened; E for the go-back case: `commands/build.md:151-154` (the bench changes after a rebuild) · supports only: a fit by shape. Nobody has used it.

```
+--------------------------------------------------------------------------------+
| button-light · XIAO ESP32-C6          rev 14 · Claude changed R1 at 10:42 CET  |
+----------------+---------------------------------------------------------------+
| 1 Idea      ✓  |  4 Requirements                                    [decided]  |
| 2 Needs     ✓  |  ------------------------------------------------------------ |
| 3 Parts     ✓  |  board  xiao-esp32-c6        yours                            |
|   to get    ●  |  button tactile-button       yours                            |
| 4 Require.  ◉  |  led    led-red-5mm           to get                           |
| 5 Build     ○  |  ! led-red-5mm owes pin_order_proof: not written until filled |
| 6 Breadbrd  ○  |                                                               |
| 7 Firmware  ○  |                                                               |
| 8 Deploy    ○  |                                                               |
+----------------+---------------------------------------------------------------+
| NEXT  Build the board · Claude runs it · about 2 s to 300 s                    |
|       [Ask Claude to build]  [Copy the command]                                |
+--------------------------------------------------------------------------------+
  ✓ done   ◉ open   ○ not yet   ● needs you   (each mark also has its word)
```

- UX-8 · Option B, a tab per step across the top, as today's `page.html` grows from three tabs to eight or more. It reuses the shipped CSS-only tab code and its static, no-script rule. It hides every other step's state behind a label, so "what is not done yet" is not visible at rest. The Artifact rules pass a plain `#name` between the URL and the page, so each tab can be a bookmarkable view (`#needs`, `#breadboard`), except reserved names (`settings`, `sidebar`, `customize`, `upgrade`, `downloads`, `comment-*`). The shipped tabs are radio inputs at `opacity:0` with labels that carry no focus style, so a keyboard user sees no focus. The WAI-ARIA tabs pattern wants one tab in the tab order (roving tabindex), arrow keys between tabs, and Tab into the panel. · E · `tabbed_page.py:87-94,110-114`; Artifact pages guide (topic pages, read 2026-11-15, the `#name` and reserved-names paragraph); APG tabs pattern (https://www.w3.org/WAI/ARIA/apg/patterns/tabs/, search result read 2026-11-15, page not opened) · supports only: the cheapest step from today's code, with a known focus gap.

```
+---------------------------------------------------------------------------+
| Idea | Needs | Parts | Requirements | Build | Breadboard | Firmware | Deploy|
|                        ‾‾‾‾‾‾‾‾‾‾‾‾                                       |
+---------------------------------------------------------------------------+
|  the chosen step only; the other steps' states are not on screen          |
+---------------------------------------------------------------------------+
```

- UX-9 · Option C, one long document, as the amplifier page is: every step is a section in order, with a contents list that sticks to the top and shows each step's state; the open step is expanded, a finished step shrinks to one summary line ("3 picks, 1 to get"), and a later step shows what it waits for. This meets the Artifact rule "Complete at rest: everything meant to be read is visible once the page has loaded", prints whole, and works as a static file with no script. It gets long on a project with twenty wires. · E · amplifier artifact (one scroll, a `#guide` anchor); Artifact design guide, "Complete at rest" (read 2026-11-15) · supports only: the shape the PO already saw on 2026-11-11. That he liked it for its shape rather than its pictures is —.

```
+---------------------------------------------------------------------------+
| Idea ✓ · Needs ✓ · Parts ✓ · Requirements ◉ · Build ○ · Breadboard ○ · …  |  sticky
+---------------------------------------------------------------------------+
| ✓ 1 Idea         "tell me when the button is pressed"          [open ▸]   |
| ✓ 2 Needs        2 needs: press, light                          [open ▸]   |
| ✓ 3 Parts        2 picks, 1 to get                              [open ▸]   |
| ◉ 4 Requirements ------------------------------------------------------   |
|     (the full step, as in UX-12)                                          |
| ○ 5 Build        waits for: requirements.json written                     |
| ○ 6 Breadboard   waits for: a build that finished                         |
+---------------------------------------------------------------------------+
```

- UX-10 · Option D, a page per step (eight Artifacts per project). Each page stays small and each can be published on its own yes, which fits D-e. A person must follow links between pages, and each page is a separate artifact with its own version, so a change in Parts leaves the Breadboard page stale until it is republished. The P297 spike already put the design in files, with the Artifact as one surface, so eight surfaces multiply the places that can go stale. · E · brief.md:18 (D-e); `docs/discovery/2026-10-18-p297-interaction-architecture/finding.md:104-110` ("The Artifact is one place to show the page, not the place the design lives") · H for the staleness risk · supports only: the option exists. It is weakest for "one page" in the PO's words (brief.md:15).

```
[Idea page] → link → [Needs page] → link → [Parts page] → … → [Deploy page]
   v3              v7               v2  ← a pick changed here; the later pages still show v-old
```

- UX-11 · A wizard (Next only, no going back) does not fit: the journey goes back by design. A rebuild after a changed pick lists what to change on the bench, a dropped need releases its holds, a kept `board.tsx` whose traces differ must not be wired. A step that a later change made out of date needs its own state, "stale", which none of A to D shows by itself. · E · `commands/build.md:132-136` (`traces differ`), `:151-154` (bench changes); `commands/idea.md:59` (`--needs-drop`) · supports only: "stale" is a needed state on every option.

### C. The breadboard page as the standard for every step

- UX-12 · One step template, read off the two hand pages and applied to every step: (1) a title and one sentence of what this step decides; (2) a change notice when the step changed since the person last saw it (the encoder page opens with "Since 2026-11-11, GA and GB go to the pads RX and TX"; the sheet has "Changes since the last build"); (3) the picture first, where the step has one; (4) the warning block for anything that can harm a part or the person; (5) numbered items, one card per item, each with a chip, a state and its source; (6) for a step done by hand, the one-at-a-time mode beside the all-at-once view; (7) "Where each fact comes from"; (8) the next-step panel. · E for each element's origin: encoder artifact (its opening paragraph, chips, modes), amplifier artifact (`.warn`, tables, provenance), `spark-walks/t-display/breadboard.md:18-20` ("Changes since the last build") · H for applying it to steps that have no picture · supports only: a template that the PO has seen in parts.

```
+-----------------------------------------------------------------------+
| 3 Parts                                         [needs you: 1 pick]   |
| A part for each need. What you own comes first.                       |
| Since 10:42 CET: Claude added "light" (you asked in the chat).        |  change notice
+-----------------------------------------------------------------------+
| [ picture of the candidate part, or "no picture in the record" ]      |
+-----------------------------------------------------------------------+
| ! led-red-5mm owes pin_order_proof: the requirements wait for it.     |  warning
+-----------------------------------------------------------------------+
| (1) press   ...cards, UX-13...                                        |
| (2) light   ...                                                       |
+-----------------------------------------------------------------------+
| Where each fact comes from  ▸                                         |
+-----------------------------------------------------------------------+
| NEXT  Write the requirements · Claude · [Ask Claude] [Copy command]   |
+-----------------------------------------------------------------------+
```

- UX-13 · A card per need with a pick button fits the Parts step, because spark already shapes `--match` that way: owned candidates first, each with how many are owned and free, "free N, held by <project>", "maybe owned", what it owes (`footprint`, `pin_order`, `pin_order_proof`, `simulation`), and `[other words]` when only the verb matches. The command page asks Claude to show, per need, "the owned option and the simpler one beside it". The reason for a mark is said in the chat and is not written to the project, so a card can show the mark and cannot show why. A pick that another project holds is refused with the holder's name, so a pick button needs a refused state. · E · `commands/idea.md:66-79,133-136` · supports only: the data for the cards exists. The "why" for a mark does not reach a page today.

```
+-- need: light (indicate) ----------------------------------- mark: know --+
|  [pic] Kingbright L-7113ID red LED     to get · owes: nothing    [ Pick ] |
|  [pic] onboard LED (xiao-esp32-c6)     yours  · free 1           [ Pick ] |
|  [pic] ws2812 ring   [other words]     in your drawer · held by  [ — ]   |
|                                        reaction-game (refused)            |
|  Why this mark: said in the chat, not kept (ask Claude)                    |
+---------------------------------------------------------------------------+
```

- UX-14 · "Store options" names two things. In spark the store is the person's local record store (`SPARK_HOME`), and "store first" means records and the drawer; the PO's request lists "the parts, the store options" beside each other, which may mean shops. spark knows no prices ("spark knows no prices"), and the PO's rules name shops (GME, Hadex, LaskaKit, Botland, TME). A page step called "Store" would mean one thing to spark's docs and another to a reader who wants to buy. · E · `commands/idea.md:2,76`; brief.md:15; the PO's rules (`CLAUDE.local.md`, "For parts, prefer Czech and EU shops") · supports only: one word for two things. Which he meant is —.
- UX-15 · The Build step is a pipeline with a state per stage and a list of kept files, both in spark's JSON: `stages` (a board-only design's stage is `skipped`, "which is never `ok`") and `kept` (`did`: `wrote`, `left alone`, `removed`, `not written`, `not kept`, `traces differ`, `traces not compared`, with `why`, and for a drawing `code` and `expected`). A build can run 300 s and stop with "the chain was NOT exercised — this is not a pass", and then the sheet, drawing and page are skipped. So the page needs a running state with its start time and a timed-out state, and must not keep showing the last good page as if it were this build's. · E · `docs/guide/agents/json.md:145-146`; `spark-walks/p581-sound-joystick/p581-rows.md:11` · supports only: the states to draw are defined. How long a typical build takes is —.

```
 Build   started 10:44:07 CET   rev 15
 board ✓ ok · parts ✓ ok · schematic ✓ ok · footprint ✓ ok · build ◌ running 41 s · simulation ○
 kept:  board.tsx  left alone  (yours, not overwritten)   breadboard.md  wrote
        breadboard.svg  not written: not_drawn_yet → wire from the steps below
```

- UX-16 · The Firmware and Deploy steps carry the strongest never-assume text spark has: the look's `data.caveats` ("passed, but it has no set-control step"), `data.limits` (what no simulation can show), `data.unnamed_must` (must lines no scenario named), and after a flash only `ready seen` is a pass. Each needs its own place on the page, above any green mark; "passed" alone must never be the biggest word. · E · `docs/guide/agents/never-assume.md:180-222,167-169` · supports only: these fields exist and are relayed in text today.
- UX-17 · The Deploy step cannot have a working "Flash" button. The flash yes is the person's, typed in their own terminal or given as a deploy grant there; "A yes that another program collected, for example an MCP client's own question, is a relayed yes … and it is neither of the two", and deploy refuses it with `relayed_yes_refused`. A click on an Artifact is such a relayed yes. The page can show the look, the caveats, the limits and the exact line to type, with a Copy button, and a hand step ("press the board's RESET … once") as a numbered card. · E · `never-assume.md:153-167`; Artifact pages guide, clipboard `writeText` only from a click handler (read 2026-11-15) · supports only: the deploy step is display plus a copied line. A button that flashes would break rule 7.

```
+-- 8 Deploy -------------------------------------------- [your terminal] -+
| The look: board XIAO ESP32-C6 on /dev/cu.usbmodem1101 · image passed run 7 |
| ! passed, but it has no set-control step: no button was pressed            |
| ? limits: the LED's brightness, the button's bounce                       |
| Type this in your own terminal (Claude cannot say yes for you):          |
|   python3 …/deploy.py --token 3f…  [Copy]                                 |
| After it: only "ready seen" is a pass.                                    |
+---------------------------------------------------------------------------+
```

- UX-18 · A simulation button must name its cost and wait for a yes: a scenario run spends Wokwi CI minutes, and the PO allows no paid runs. · E · `never-assume.md:105-110`; the PO's memory note "No paid Wokwi runs" (MEMORY.md, 2026-10-31) · supports only: any "Run simulation" control is a gated request, never a one-click act.
- UX-19 · The P269 council's build-mode idea (show step n, grey the rest, tick it off) is what the encoder page built, and the names in the steps (R1, LedRed5mm, board D7) are "the cheapest cross-view link" between the picture and the steps. A standard keeps those names identical across the page, the sheet, the chat and `pins.py`. · E · `docs/discovery/2026-10-16-p269-views-and-editors/council/user.md:35,37`; encoder artifact · supports only: the pattern is proven in one hand page. A tick that persists is — (UX-33).

### D. Decided, guessed, could-not-run, skipped: how a person tells them apart

- UX-20 · spark already has the words a page needs, and the CLI already prints a glyph per kind: `problems` are `-` lines, `unchecked` are `!` lines, `unmeasured` are `?` lines; a result's status is `ok`, `problems`, `could-not-run` or `skipped`; a fact is `verified` or not; a need's mark is `have`, `have-unknown`, `know` or `gap`; a null is unknown. Reusing the same glyph and the same word on the page lets a person who reads the terminal and the page see one language. · E · `docs/guide/agents/json.md:105,120`; `commands/idea.md:77-78`; `never-assume.md:38-40` · supports only: the vocabulary exists. A page legend for it does not.
- UX-21 · Proposed legend, each with a glyph, a word and a shape, never color alone (so a color-blind reader and a screen reader get it): decided (the person chose, with who and a Prague time), from a record (verified), unverified (the record says it, nobody checked), estimated (from a photo), unknown (null: "not known, ask", an empty field, never a default), not checked (`!`), not measured (`?`), skipped (did not run, by design: "never ok"), could-not-run (tried and failed, with the reason), stale (made from an older state). `ok` is drawn only on a result that ran; a step whose checks were all skipped shows "not checked", not a tick. · H (my proposal) · from never-assume.md:5-9 ("A `could-not-run` is not a pass, and neither is a `skipped`"), `json.md:28` ("When every check is skipped, check_all answers could-not-run") · supports only: a proposal to test with the PO.

```
 Legend    ✓ ok     − problem    ! not checked    ? not measured
           ◆ decided (you, 10:42 CET)   ◇ unverified   ~ estimated
           ∅ unknown — ask   ⊘ skipped (never a pass)   ✕ could-not-run: <why>   ⟲ stale
```

- UX-22 · A null shown as an empty field invites a person (or the page's script) to fill a default. The page must render a null as "unknown", with who can answer it, and an edit of it must go through the same command as the CLI (`--fact-set`, a dry run first), never a free text box written to a file. · E · `never-assume.md:38-40` ("A `null` is unknown, never a value to fill in"); `commands/idea.md:55-58` (dry run first) · supports only: the page must not invent values.
- UX-23 · Decisions must name the decider. In spark's records "the PO chose RX and TX on 2026-11-11" is a decision; a pick written by Claude after the person said yes in the chat is the person's decision relayed; a pick made by a click is the person's own. The page should show the actor of each change (you, Claude) and its time in Europe/Prague with the zone, as the PO's rules require. · E · encoder artifact, provenance item 1; `~/.claude/CLAUDE.md` ("When you tell me a time, use my local zone (Europe/Prague)"); P297 decision 3, "Every change carries `rev`, `base_rev` and `actor`" (`finding.md:138`) · supports only: actor and time are needed fields.

### E. How Claude learns what the person clicked and what the page shows

- UX-24 · The Artifact runtime has no "send this to the chat" call. Its capabilities are `artifact`, `assets`, `comments`, `db`, `dictation`, `downloads`, `files`, `mcp`, `room`, `sample`, `tts`, `user`. A click reaches Claude only through what Claude reads later (db rows, comments, a republished page), or through words the person pastes. · E · `describe_capabilities`, contract 0.2.96, read 2026-11-15 · supports only: a page cannot push a click into the conversation.
- UX-25 · `db` is the path for state Claude reads: "shared rows, per-person state, data Claude reads". The page writes rows; Claude reads them with `db_get`, `db_list` or `db_query` and writes with `db_write`, which needs `ifVersion` for an existing document and refuses the whole call on a stale version. This session's Claude Code has those tools. The page hears Claude's writes live through `onSnapshot`. Nothing tells the chat that a row arrived: Claude reads at its next turn. · E · `describe_capabilities db` and the server's note ("Here write_db is db_write, and read_db is db_get, db_list or db_query"); `db_write` tool description; P297 `finding.md:80-81` ("Claude learns of a drag at its next turn") · supports only: db carries clicks both ways, with a turn's delay toward Claude.
- UX-26 · A comment the person sends to Claude wakes the chat, but "Only a cloud session can be woken". So in Claude Code on the PO's Mac a page comment does not start Claude; in a cloud session it does, and `read_comments` shows `claude_may_edit` when the person lets Claude edit and republish for that thread. · E · `watch` and `read_comments` tool descriptions (claude-artifacts server, read 2026-11-15) · supports only: comments are a "tell Claude" path in the cloud only.
- UX-27 · `sample` is a different Claude from the chat's. It is "Memoryless: send instructions+data+format", it can call only tools the page defines in script, and its first call asks consent. It cannot run spark's Python and does not know the conversation. A page "Ask Claude" box built on it answers beside, not inside, the chat; a person who asks the box and then the chat may get two different answers and not know they came from two places. · E · `describe_capabilities sample`, read 2026-11-15 · H for the confusion · supports only: if `sample` is used, its answers must be labelled as the page's helper, not the chat, and be limited to explaining what the page shows.
- UX-28 · `files` lets the page read a Claude Code project's files as the viewer, read only (`list`, `read` with a `revision`, `download`), with a lag of a few seconds for new files. It is declared with a project id (`chan_…`). That would let the page show the kept files themselves (requirements.json, breadboard.md, needs.json) instead of a copy, which matches P297's "files are the truth". Whether a local Claude Code session on the Mac has such an id and whether the page reads the Mac's folder is —. · E · `describe_capabilities files`, read 2026-11-15; P297 `finding.md:133-145` · supports only: a read path that would avoid a second truth, unproven for a local session.
- UX-29 · `artifact.publish(html)` makes the page the record: a click regenerates and republishes the page, and every open view reloads. Its own rules: "`conflict` is routine (every view reloads to the winner, dropping this edit): no retry", and publish only after a viewer acts. So a person's click can vanish when Claude published a second earlier, and the reload clears whatever the person was looking at. · E · `describe_capabilities artifact`, read 2026-11-15 · supports only: a silent drop is built into this path. The page would have to say "your pick was not kept" after the reload, and it cannot know that unless it saved the pick somewhere first.
- UX-30 · A "Copy for the chat" button works on every surface, needs no capability, and keeps the person in charge: the click composes the exact request ("pick light=led-red-5mm for button-light", or the spark command line from `next[].argv`) and the person pastes it. spark's JSON already holds the steps an agent may take, `{op, argv, why, effects, needs_yes}`, so the button's text can come from the core, not from the page. The cost is one paste per action. The encoder page's last step already uses this hand-back in words ("Tell Claude “wired” and the three readings"). · E · `json.md:249`; Artifact pages guide (clipboard `writeText` from a click; `alert`, `confirm` and `prompt` are refused); encoder artifact step 8 · supports only: the cheapest working path from click to Claude.

```
 Click path options, from the person's click to Claude acting:
 copy  : [Pick] → text in clipboard → person pastes → Claude runs parts.py --pick → files → page redraws (republish or db)
 db    : [Pick] → db row {op:pick, actor:you, base_rev:14} → (person says anything) → Claude db_query → runs pick → db ack row
 comment (cloud only): [Pick] → comment to Claude → session wakes → Claude reads thread → runs pick → republish
```

- UX-31 · How Claude changes the page: by writing db rows the page renders (live, no reload), or by republishing the page (`publish_files` with the kept `page.html`, a new version, every view reloads). build.md already has the republish path: "To update it after a rebuild, call the tool again with the same `file_path` and no `icon`". A republish is a change the person did not click, so the page must say so at the top (UX-12's change notice), with the actor and time, and a one-time highlight that respects `prefers-reduced-motion`. · E · `commands/build.md:163-165`; Artifact pages guide (Publishing); design guide ("respect prefers-reduced-motion") · supports only: both paths exist. The notice is a proposal (H).
- UX-32 · For Claude, the page's state must be readable as data, not by reading the HTML. If the page and the chat share one state document (a db doc, or a JSON file in the project) with `rev`, `actor`, each step's state word and code, Claude reads that instead of guessing what the person sees. Decisions by code, never by comparing English text, is already a spark rule. · E · P297 `finding.md:135-139`; the PO's memory note "No magic strings" (MEMORY.md, 2026-10-15); P481 #660 title ("each Operation, stage, check and step is described once, as data, rendered for the CLI, agents, MCP, LangGraph and the docs") · supports only: the page's labels should be rendered from the same codes the CLI uses.

### F. Chat and page: who does what, and how they stay in sync

- UX-33 · A split that follows what each surface is good at (H, my reading, from the jobs in jobs-and-journeys.md:14-17 and the command pages):

| on the page (click) | in the chat (words) | in the person's terminal only |
| --- | --- | --- |
| choose among offered candidates; pick, unpick | the goal; why a mark; a need nobody offered | the flash yes, a deploy grant (never-assume 7) |
| look at pictures, the steps, one step at a time | research a gap; a new part from a photo | a yes to a paid run, if ever |
| tick a wiring step; enter a meter reading | write the firmware (spark exports facts) | |
| see each step's state, the caveats, the next step | ask "why", "what if", a variant | |
| copy a command or a request | say "wired", "it beeps" | |

  · H · from `commands/idea.md:49` (questions one at a time, in the chat), `AGENTS.md` ("The conversation writes the firmware"), `never-assume.md:153-167` · supports only: a starting split to show the PO.
- UX-34 · The PO wants both, a fully automatic path and each step offered by hand: "we can offer a fully automatic way, but we should also definitely offer the steps themselves like download the picture or enter whatever mode on the board". On the page this is two buttons on each next-step panel, "Ask Claude to do it" and "I do it myself" (the command or the hand step), not one. · E · `spark-walks/walk3-rehearsal/walk3-rehearsal-diary.md:144-147` (the PO, 2026-10-31) · supports only: his words for one journey. That he wants it on every step is H.
- UX-35 · Who wins a conflict: the core's revision check, as P297 decided ("A stale command (an old `base_rev`) gets `conflict` and the newest state"). On the page that means: never drop a click without a word; show "Not applied: Claude changed light at 10:42 CET (rev 15). Your pick was made on rev 14. [Apply again] [Keep Claude's]"; and in the chat, Claude says the same when its write meets a newer click. · E · P297 `finding.md:80`; `db_write` refuses a stale `ifVersion` · H for the banner · supports only: a conflict must be visible on both sides.

```
+---------------------------------------------------------------------------+
| ⟲ Not applied. Claude changed "light" to led-red-5mm at 10:42 CET (rev 15).|
|   Your pick, the onboard LED, was made on rev 14.                          |
|   [ Apply my pick again ]   [ Keep Claude's ]                              |
+---------------------------------------------------------------------------+
```

- UX-36 · A turn's delay is the main surprise in every path but copy: the person clicks, and Claude does not know until the next message. The page should show each request's state: "sent to Claude, not read yet", "Claude is on it", "done at 10:45 CET", or "copied, paste it in the chat". Without that, a person clicks again or thinks the page is broken. · E for the delay (UX-25, UX-26); H for the states · supports only: a visible "not read yet" is needed whenever db carries requests.
- UX-37 · Wiring progress (which step the person ticked) is per-viewer convenience by the Artifact rules unless it must reach Claude: localStorage "reaches no other viewer or device and not Claude … never for state that must last". A tick that Claude should act on ("all wired, run the probe") needs db or a paste. · E · Artifact pages guide (localStorage paragraph, read 2026-11-15) · supports only: decide per field whether Claude must see it.
- UX-38 · Publishing stays on a yes. spark never publishes without the person's yes (D-e), and build.md says to ask "Publish this page as an Artifact?" The claude-artifacts server's own instruction tells Claude it "may publish its own work without being asked, because artifacts start private". The two conflict; for spark's pages, spark's rule is the narrower one. A page that republishes itself through `artifact.publish` after a click is the person's act, not Claude's. · E · brief.md:18; `commands/build.md:161-162`; the claude-artifacts server instructions (this session) · supports only: the first publish of each project page needs a yes; later republishes by Claude are — (the PO's call).

### G. Accessibility, themes, a page with no Claude

- UX-39 · The page must work as a static file with no Claude and no capability: every `claude.use(...)` may resolve `null` ("Branch on `null` and design for absence"), a page opened from disk has no runtime at all, and the kept `page.html` today has no script. So the content (the steps, the tables, the states) must be in the HTML; the script only adds the one-step mode, the pick buttons and the sync. The encoder page fails this: its steps are only in a script array, so with no script, and in a thumbnail or print, only an empty card shows. The amplifier page passes for the wires (an HTML table) and fails for the guide. · E · `describe_capabilities` preamble (read 2026-11-15); `tabbed_page.py:10-11`; encoder artifact (`STEPS` in `<script>`, the card's `#title` and `#text` empty in HTML) · supports only: progressive enhancement is a requirement for the standard.
- UX-40 · Keyboard and screen readers: the encoder page changes the step text with no live region, binds the arrow keys on the whole document (they fire while focus is in any other control), and its progress bar is unlabelled `<i>` elements; the amplifier page has `aria-live="polite"` on its step line and `aria-pressed` on its mode buttons. The shipped tabs show no focus (UX-8). The design guide requires a visible focus state, stable ids on controls, and reduced motion. A standard should take the amplifier page's choices and add `aria-current="step"` on the current step. · E · encoder and amplifier artifacts, read 2026-11-15; Artifact design guide ("give keyboard focus a visible state, respect prefers-reduced-motion, and give every form control a stable id"); Toyota stepper (`aria-current="step"`, search result, read 2026-11-15) · supports only: known gaps to close in the template.
- UX-41 · Color carries meaning twice: step colors on the wires and state colors on the badges. The amplifier table names each color in words beside its swatch ("Red", "Orange"); the drawn wires carry no step number, which the P269 council found before. A color-blind reader needs the number on the wire and the word on the badge. · E · amplifier artifact (the wire table); P269 `council/user.md:15` (USER-6, "there is no label with the step number on the wire") · supports only: numbers on wires and words on badges.
- UX-42 · Themes: the pictures stay on a white ground in both themes (`--backdrop: #fff` in light and dark, "spark's breadboard and tscircuit's SVGs are drawn for a light ground"), and both hand pages do the same (`.fig{background:#fff}`). In dark mode that is a bright slab beside dark text; a picture drawn with theme tokens would avoid it but is a drawing change, out of this epic's scope. · E · `tabbed_page.py:81-85`; both artifacts' `.fig` rule; brief.md:20 (out: "a redesign of the breadboard drawing itself") · H for the glare · supports only: keep the white ground for now and say so.
- UX-43 · Bench use: both hand pages draw the breadboard with a minimum width (760 px and 980 px) and scroll sideways inside their frame below that. On a phone beside the breadboard the picture needs a sideways scroll, and the step card falls below it. Whether he wires with a phone, a tablet or the laptop is —. · E · encoder artifact (`min-width:760px`), amplifier artifact (`min-width:980px`) · supports only: a phone layout is untested.

### H. Artifact page rules that shape the design

- UX-44 · Rules from the claude-artifacts guide that every spark page must meet: one HTML document with its own CSS, script, data and pictures (data: URIs or inline SVG); no remote image; scripts only inline or from the listed CDNs, pinned to an exact version; no `fetch` to other hosts; `alert`, `confirm`, `prompt`, `window.print` and page-started downloads refused (build dialogs in the page; offer Copy); a form has nowhere to submit; at most 16 MiB; title of two to four words; full light tokens on `:root`, dark under the guarded media query and again under `:root[data-theme="dark"]`; an explicit body background; a side gutter of 16 px and one column at about 400 px. The kept `page.html` is 230 to 382 KB today. · E · `guide` topics pages and design, read 2026-11-15; `ls -la` of `spark-walks/reaction-game/page.html` (230452 bytes) and `t-display/page.html` (382218 bytes) · supports only: the constraints. The TypeScript build must emit one file that meets them (D-d).
- UX-45 · A capability is declared after the first publish ("New page: publish it, then declare"), and a page gaining one declares first, then publishes the code. `db` rules default to signed-in readers and Contributors writing; a project page shared with a friend would let a Contributor write picks unless the rules say otherwise. · E · `describe_capabilities` (the declaration paragraph), `describe_capabilities db` (read 2026-11-15) · supports only: sharing a project page needs db rules chosen first.
- UX-46 · `mcp` with `host:<name>` reaches a local MCP server on the viewer's device in the Claude app only (else `server_not_connected`), and P297 read it as owner-only. A page button that runs spark on the Mac through it would work for the PO in the Claude app and fail everywhere else, including the browser and Claude Code. · E · `describe_capabilities mcp`, read 2026-11-15; P297 `finding.md:107-109` · supports only: a host-MCP path is a narrow, PO-only surface.

## What I could not check, and why

- Which page the PO meant by "the breadboard with the nice pictures and the step by step guide". I matched his words to the two 2026-11-11 artifacts by title and content; he did not name one, and I asked nobody (read-only lens).
- How the pages look rendered, in light, dark, at phone width, with a screen reader. I read their HTML and did not open them in a browser; the lens changes nothing and the read was enough for the rule checks. UX-40 to UX-43 are read from the code.
- Whether `files` works for a local Claude Code session on the Mac, and what project id it would carry. The capability text names `chan_…` ids and "a Claude Code project"; I declared nothing and published nothing, so it is unproven.
- Whether `db` rows written by a page reach a Claude Code session's `db_query` on this account in practice. The tools are listed in this session; I did not create an artifact to try it (no publish without the PO's yes).
- Whether `sample`'s consent prompt and rate limits suit a page used every few minutes at the bench. Not tried, for the same reason.
- How long builds take on the two candidate projects; one p581 row shows a 300 s timeout, and I did not run a build (read-only).
- The other lenses' papers in `council/` (existing.md, physics.md, risks.md, user.md): I did not read them, to keep this read independent.
- P481 #660's description schema: I read its title only, not its body or code, so UX-32's "render labels from codes" rests on the title.
- Whether the PO wires with a phone or tablet at the bench (UX-43): no log I read says.

## Questions for the decider

- Q-ux-1 · When you said "I love how you did the breadboard with the nice pictures and the step by step guide", which page did you mean: the encoder page ("Wire the rotary encoder, step by step"), the amplifier page ("FireBeetle 2 Amplifier Wiring"), or spark's `page.html`? · decides: which page is the template, and whether the standard is the one-step-at-a-time mode, the long sheet, or both (UX-1, UX-2, UX-9)
- Q-ux-2 · Of the four layouts (a step rail with a next-step panel; a tab per step; one long page with each step as a section; a page per step), which one would you open first for button-light? · decides: the page's shape (UX-7 to UX-10)
- Q-ux-3 · When you pick a part on the page, which way should Claude learn it: you copy a line into the chat, the page writes a row that Claude reads at its next turn, or both? · decides: the click path for the MVP (UX-25, UX-29, UX-30, UX-36)
- Q-ux-4 · By "store options", did you mean the parts in your own spark store and drawer, or shops where you can buy them (GME, LaskaKit, TME)? · decides: whether a shop step is in scope, given that spark knows no prices (UX-14)
- Q-ux-5 · If Claude and you change the same thing a moment apart, whose change should stay, and should the page ask you each time? · decides: the conflict rule and its banner (UX-35)
- Q-ux-6 · May Claude republish the project page after each step without asking, once you said yes to the first publish? · decides: how D-e applies to later republishes (UX-31, UX-38)
- Q-ux-7 · Should an "ask Claude" box on the page itself exist, knowing it is a separate Claude that does not see the chat and cannot run spark? · decides: whether `sample` is used, and for what (UX-27)
- Q-ux-8 · At the bench, what do you hold: the laptop, a phone, a tablet? · decides: whether the phone layout is in the MVP (UX-43)
- Q-ux-9 · Is the legend in UX-21 (decided, unverified, estimated, unknown, not checked, not measured, skipped, could-not-run, stale) what you want to scan for, or too many marks? · decides: the status vocabulary on the page (UX-20, UX-21)
- Q-ux-10 · Should the page keep working as a file you open from disk with no Claude, as `page.html` does today? · decides: whether progressive enhancement and "loads nothing from the web" are hard rules for the standard (UX-6, UX-39)

## Searches

| query, verbatim | the decision it served | used or not |
| --- | --- | --- |
| non-linear stepper progress indicator design system guidance edit completed steps | the layout choice: a stepper or a wizard, and whether a progress bar fits a journey that goes back (Q-ux-2) | used (UX-7, UX-40; result snippets from Morningstar, Material, Toyota, Zuora, Genesys, Benevity; pages not opened) |
| WAI-ARIA APG tabs pattern keyboard interaction roving tabindex | the keyboard model for the tab option and the template's step controls (Q-ux-2) | used (UX-8; the W3C tabs pattern page named, its text read through search snippets only) |
