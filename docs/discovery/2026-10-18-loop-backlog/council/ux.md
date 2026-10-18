# Council lens: UX (what Petr sees and does at each step)

> **TL;DR.** The pieces exist, but the person reads three files, copies commands into a terminal, and after a change
> compares two sheets by eye. The cheapest wins are text, not a new page: hole numbers in every step, a "what changed
> at the bench" list after a rebuild, and one page that holds the steps. The P293 page should be a TypeScript view of `breadboard.json`, served by a small local server that can push changes, so watch mode can grow from it later.

Lens: opus. Runs 2026-10-18, scratch store, no USB: a copy of `tests/data/breadboard/button-light-xiao`, `check_spine.py
--keep .` (exit 0), then again with a second button `BtnTwo` (exit 0).

## Claims, with evidence

1. **The page holds pictures only.** `page.html` is three radio tabs with one `<img>` each (Breadboard, Schematic, PCB),
   no parts list, no steps, no script. To wire, the person opens `breadboard.md` for the steps and the picture for
   the places. Seen by stripping the page's data URIs.
2. **Steps name no holes.** `breadboard.md` says "Put R1 ... end 1, in a free row" and "Run a jumper from board D8 to
   the row of R1 end 1". The picture has no row numbers, no column letters and no pin labels on the board, so "D8"
   cannot be found on it. Yet spark has coordinates: the rebuild printed `jumper 8b.j-17b.g`.
3. **The picture misleads in places** (`breadboard.svg` rendered with qlmanage). Jumpers 5 and 8 are drawn across the
   board's and the button's bodies. After the rebuild, `R1` sits on top of `BtnTwo` and the labels overlap, and
   jumpers 7 and 9 run on one line. The XIAO's USB-C tab points into the button beside it, so a plugged cable may hit it.
   Nobody checked this on a real breadboard.
4. **A rebuild says what was not kept, but not what to change on the bench.** Adding `BtnTwo` renumbered every step
   from 4 on. It also moved one existing jumper: before, step 7 ran GND to the LED's K row. After, GND goes to BtnTwo B,
   with LED K joined to BtnTwo B. Nothing says "take this jumper out". Found only by `diff` of the two sheets.
5. **False "move not kept" lines.** The rebuild printed `move not kept: jumper 8b.j-17b.g` and `jumper 12t.a-17b.h`,
   but nobody moved a jumper. They were spark's own. The person is told about moves he never made. P292 #351 is the
   opposite case: a lost jumper with no line.
6. **`board.tsx` goes stale** (`left alone: board.tsx`): `tsci dev` shows the old circuit (P110 #44). **The sheet is
   heavy:** "Before you power it" puts a deep-sleep paragraph before "the long LED leg goes to the resistor".
7. **The deploy yes is a copy step.** With no grant, deploy.py prints a line that the person copies into his own
   terminal (`commands/build.md:311-314`). The grant removes that, but it is one more line to copy
   (`build.md:316-318`). The hand steps come as plain text: BOOT, then RESET (`:336`), or R once (`:320`). No picture shows
   where B and R are on the XIAO.
8. **Stale words, a paste, a vague warning.** `build.md:354` says "Nothing has run this on a board yet ... on a
   FireBeetle"; the README says the XIAO printed `ready seen` on 2026-10-15. `build.md:82`: the person pastes
   `breadboard.json` into wokwi.com. The build printed "no serial monitor is wired ... wait-serial may hear nothing",
   and nothing says whether that blocks him.

## Manual steps

| step | today | remove or keep | how |
| --- | --- | --- | --- |
| open md, svg and page | three files | remove | one page with picture, parts, steps, changes; Claude opens it after each build |
| compare old and new sheet | by eye | remove | "what changed at the bench" list |
| edit requirements.json to drop a part | by hand (gaps step 3) | remove | P293 story 1: Claude changes the circuit from his words |
| copy a deploy line to a terminal | each deploy | reduce to once | one grant per session, said in one sentence |
| Wokwi token | met at the first simulation | keep, move | `/spark:setup` asks once, at the start |
| wire the breadboard | hands | keep | one step at a time, hole numbers, picture with labels |
| plug USB, press BOOT/R | hands | keep | only when a tool asks; a picture of the XIAO with B and R ringed |
| the erase yes | his terminal | keep | the grant says what it allows: "erase and write this board for 60 min" |
| check the wiring | not done | keep, assist | after the deploy, Claude says "press the button now" and reads the console (P248 #270) |

## Ordered slices (UX view)

| # | id | title | done when (testable) | for | size |
| --- | --- | --- | --- | --- | --- |
| 1 | NEW | Steps a hand can follow | each step names its holes ("D8 to 15j"). The picture has row and column labels and board pin names. No jumper crosses a part body. The USB end stays free. Test on the fixture | both | M |
| 2 | NEW (+ #351) | What changed at the bench | a rebuild prints and writes "add / move / remove" lines, one physical action each. No line names a jumper spark drew itself. Test: add BtnTwo, get 3 adds and 1 move | both | S |
| 3 | NEW | One page to wire from | page.html's breadboard tab shows the parts with "have", the steps, the changes and the "before power" lines (beginner lines first) | person | S |
| 4 | #347, #192 | Deploy in one step | `/spark:deploy` with `--json`. The first connect retries. The hand prompt names the button and shows where it is | both | M |
| 5 | #270 | See it work | after the deploy, Claude reads the console for N s and says "LED on" when he presses. This is the wiring check | both | S |
| 6 | #352 story 1 | Change by words | "a buzzer on pin 20" changes the requirements and rebuilds. Claude relays slice 2's list | Claude | S |
| 7 | #352 story 2 | Drag and save on a local page | see below | person | L |
| 8 | #356 | Live view | see below | person | L |

## The page: first useful, then nice

- **P293 story 2, first:** a local page from `breadboard.json`, with holes labelled. Parts snap to holes. Jumper ends drag.
  **Save** writes `breadboard.json` through a small local server, and Claude reads it. After any rebuild the page
  reloads by itself and rings what moved. Use `@wokwi/elements` pictures where they exist (LED, resistor, button,
  buzzer). The XIAO and the breadboard stay spark's own (P294).
- **P295 live view, first:** the same page, not a second one. The LED glows and the button can be pressed, both driven
  by the stand-in bench, with a serial pane. A label says "stand-in, not Wokwi" so a green page is not read as a pass.
- **Nice, later:** real photos or good drawings per part (P276 #312), the schematic and PCB dragged the same way
  (tscircuit `manual-edits.json`), an Artifact copy for sharing.

## Vision after the MVP: AI-first, he watches

His words: "I basically just watch it and maybe then drag and drop things myself ... just tell Claude, and he would do it."
- **What he sees:** the page is open beside the chat. Claude changes the circuit. Within a second the page redraws, each
  added or moved thing is ringed for a few seconds, and one caption names it: "added BtnTwo, jumper D9 to 22a". It is
  slice 2's list, drawn. An **undo** per change goes back one rebuild.
- **Dragging to correct:** he drags a part, the page saves, and Claude is told that the file changed. The next rebuild keeps the
  move (P273) or names why it cannot.
- **Shape it now, or it blocks this:** (a) a TypeScript module that draws `breadboard.json`, not an SVG baked into
  page.html, so one module serves the local page, an Artifact and later Electron. (b) Have the local server push "file changed" to the page (watch, then reload and diff), not
  only accept saves. (c) Put the ring and caption on the diff of the old and new JSON, so slice 2 and the page share
  one source of changes. No Electron now.

## Drop or park

- Park the Wokwi paste (`build.md:82`) once story 2 ships; the schematic and PCB drag and #311, #313 until the
  breadboard page was used at a bench. No separate live-view page: P295 goes into the story 2 page.

## Risks

- The page needs a running local server. Claude must start and stop it, and say where it runs. An Artifact cannot reach it.
- `@wokwi/elements` has no XIAO and no breadboard, so the pictures will mix two styles. He dislikes the current look.
- A pretty page can hide a wrong picture (claim 3). The jumper check P279 #317 should run before the page is trusted.
- Slice 1 changes every sheet line, so fixtures and journey docs change with it.
