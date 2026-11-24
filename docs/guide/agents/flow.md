# Where a project stands, for AI agents

Part of the [guide for AI agents](../agents.md). `flow.py show` says where a project stands, phase by phase
([P825](https://github.com/xmejkal/spark/issues/1183)). The phases go from the idea to the deploy. It reads the project's
files and the store, and writes nothing. `flow.py` with no verb shows too. `flow.py page` writes the same phases as a page ([below](#the-page)).
`flow.py run-request` runs the step the page asked for ([a page request](#a-page-request)). `show`'s `next` holds the
step to take now ([the next step](#the-next-step)).

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/flow.py" show --project . --json
```

With `--json` it prints the envelope, as `parts.py` does, with `tool` `flow` and `op` `show-flow`. Its `data` is one reading of the flow (`reading_of`, [P1060](https://github.com/xmejkal/spark/issues/1558)), the one `flow.py page` draws, in nine keys:

- `name`, `title`, `stamp` and `artifact` (P1060): the project folder's name; the page's title, which names the published Artifact; `stamp.newest`, the newest change time of the fingerprint's three files (`null` with none), the page's `data-written`; the id of the Artifact the page is published as, from `.spark/page.json` (`null` with none kept, or an id that is no Artifact id).

- `phases`: the nine phases in order, `idea`, `needs`, `parts`, `requirements`, `build`, `breadboard`, `firmware`,
  `simulate` and `deploy`. Each is `{phase, status, mark, by, says, offers}`.
- `fingerprint`: the sha256 of the current offers (each `key`, `effect` and `makes_stale`, as canonical JSON) and of
  `.spark/needs.json`, `requirements.json` and `.spark/build.json`. It changes when one of these files changes, or when
  an offer changes: a pick's effect changes with the drawer count. No other file of the project changes it, except through
  an offer. The page carries its first 12 hex digits ([P829](https://github.com/xmejkal/spark/issues/1187)).
- `stands_at`: the phase of `guide.now`, kept for old readers. Read `guide.now.phase`: it is the same phase, by one rule
  ([P1030](https://github.com/xmejkal/spark/issues/1510)). It is `null` when no phase is open (the deploy is `ok`), or with a phase list a test swaps in.
- `guide` ([P977](https://github.com/xmejkal/spark/issues/1407)): what the person does now. `now` is `{phase, by, says,
  offer, needs, steps}`: the phase to act on, who acts (a list: `["you", "claude"]` when the firmware and the wiring are two jobs, else one item), one sentence for the person, `offer`, for the
  parts, the needs with no pick, and `steps`: the number of wiring steps when wiring is part of now (the two jobs of the
  firmware), else `null`. `offer` is the key of the now offer: the now phase's one offer of a kind the page sends (a
  pick, the parts list or the build), else `null`. With one pick offer for the parts, `offer` is that pick. A
  breadboard now names no offer, because the build's offer is in the build phase.
- `deploy` ([P1043](https://github.com/xmejkal/spark/issues/1533)): the newest board log in `sim/runs/board/`, or `null` with none or with one that cannot be read (the deploy phase says why). `at` is its time as written, with its zone; `image` the whole sha256 of the image it wrote; `verdict` `ready seen`, `ready not seen` or `ready unknown`; `cause` the code of the cause, from the log's reason line or its sentence's fixed start; `fact` `current`, `image-differs`, `firmware-newer` or `no-image` (what the image the project holds now says of it); `read_back` whether spark read the board's files back after the write (`null`: the log cannot tell). A `null` `cause` means ready seen, or a cause not recorded: never fill it in. To answer "is the new firmware on the board", read `fact`, `read_back` and `verdict` together: `fact` `current` says only that the log's image is the image the project holds now.

  While no need is written, `now` is the idea. `now` is `null` when the deploy is `ok`, and then `no_open_phase` holds one sentence that says nothing waits (else it is `null`), or with a phase list a
  test swaps in. `done` names the phases before `now` that were done. With no picks behind the parts list (a
  requirements.json written by hand, or a project whose last need was dropped), `needs` and `parts` are left out and
  `done` says `requirements (no needs or picks behind it)`.

  With every need set aside, the parts phase is `ok` (nothing is left to pick), but no pick can make the parts list, so
  `now` is `parts` and tells the person to bring a need back and pick a part.
  The requirements phase has no offer then (no board is picked, P993): ask the person which need to bring back. A
  requirements phase that could not run stays `now`. The
  breadboard is in `done` only once `now` is past the firmware's
  two jobs and the sheet is current, as `breadboard (spark cannot see it)`. `later` names the phases after `now`; one whose status is
  `ok` carries the suffix ` (done, may change)`, because a change before it can make it stale. An item of `done` or
  `later` can carry a suffix in parentheses: match on the name before it.

  `set_aside` lists the needs
  the person set aside (`aside: true`). To bring one back, the person tells Claude, which writes `{"id", "aside": null}`
  with `--needs-set`.

  A build whose only stop is a simulation stage with the code `board_not_in_wokwi` is counted as
  done: `done` says `build (no simulation)`, a simulate with no status or not started is in `later` as `simulate (no
  Wokwi model of this board)`, and `no_simulation` says why (else `null`). The build phase keeps `could-not-run`, so the
  exit stays 2. Else the simulate is `now` while a run failed on its image, a file under `firmware/` changed after the
  image, or no run tested it, each with its own sentence and who acts (`claude` for the first two, which name the failed log
  or ask for a new image). Relay `now.says` as it is.

The words of a phase:

| key | holds |
| --- | --- |
| `status` | `ok`, `problems` or `could-not-run`, a phase word, or `null`. The phase words: `not-started` (nothing done yet), `partial` (some needs have no pick, or a build skipped a stage) and `stale` (done, but what it was made from changed after it: see the build, needs and idea below). See `null` below |
| `mark` | the glyph a page shows for the status |
| `by` | who does the phase: `you`, `claude` or `your terminal` |
| `says` | sentences for a person. A value nobody recorded reads `unknown` |
| `offers` | `{key, label, effect, makes_stale}`: a next step, with the four keys under this table. `flow.py` runs none |

An offer has four keys ([P829](https://github.com/xmejkal/spark/issues/1187)):

- `key`: the step, such as `pick:light:led-red-5mm`, `requirements` or `build`.
- `label`: the words of its button, such as `Build the board`.
- `effect`: plain sentences that name every write the step makes, such as `Uses 1 of your 3 “DFRobot FireBeetle 2
  ESP32-S3” for the brain.` The part's name stands in quotes. A pick that lets a hold go says whose it was: "Frees
  what the old pick held." for the need's old pick, and "Frees a part this project held without a pick." for a hold
  given by hand.
- `makes_stale`: the phases the step can make out of date. It lists only the phases that hold something now. With
  requirements.json there, a pick names `requirements`. Write the parts list names `build` when `.spark/build.json` is
  there and `breadboard` when breadboard.md is there. A build names none.

A `null` status means spark does not judge the phase, and `says` tells where it stands. The idea has `null`. A
hand-written project (requirements.json and no needs file) has `null` for its needs and parts, and says so. A project
whose last need was dropped (needs.json holds no need, requirements.json stays) has `null` too, and says "no need is
left: the last one was dropped" for its needs and "no need or pick is behind the parts list" for its parts. Written firmware and a
simulated image have `null`, because you judge them. Without firmware/main.py, or without an image, they are
`not-started`. A firmware line in sim/wokwi.toml that spark cannot use gives the simulate phase `problems`.

The hints of the simulate and deploy phases name the command and who acts, and hold no placeholder
([P979](https://github.com/xmejkal/spark/issues/1411)). The page masks every path, and the scripts live in the plugin, not
in the project. So a hint says "ask Claude" and never gives a path: you take the full lines from `commands/build.md`
(the scenario run) and `commands/deploy.md` (the dry run). The deploy line the person runs is the one `deploy.py` prints
(`commands/deploy.md`, step 2), and the image line comes from `look.py` and `deploy.py`. A
could-not-run line is the error's own sentence, masked.

A phase that spark did not judge is never a pass, and a skipped stage is not one either
([P878](https://github.com/xmejkal/spark/issues/1246)). These phases have `null` too, and their mark is the dot, not the tick:

- A requirements file with no needs beside it. Spark compared it with nothing.
- A breadboard sheet that is current. Spark does not judge the wiring.
- A build on the board alone, whose `build` stage is skipped. No board was built, and the breadboard phase has
  nothing to wire. A rebuild skips the same stages, so `stands_at` passes both phases and the build phase has no offer.
- A build that ended `ok` and skipped only its `simulation` stage, because every part is skipped from the simulation.

A build that ended `ok` and skipped any other stage is `partial`. No build does that today. With no log in
`sim/runs/`, the simulate phase says to run a scenario. It blames an older spark only for a log that names no image.

The offer keys are `needs-drop:<need>`, `pick:<need>:<id or entry>`, `requirements` and `build`. A pick's effect says
how many the person has.

Since [P993](https://github.com/xmejkal/spark/issues/1446), the requirements phase has the `requirements` offer only
when the parts list's own rule (`need_requirements.requirements`) has no problems, so a click is never one that writes
nothing. With problems, the rule's lines are the phase's `says` (after `no requirements.json yet` when there is no file).
A pick whose record owes a fact is named with its need and the facts, such as `“Soil probe” for soil
still lacks what spark needs: footprint, pin_order. Ask Claude how to fill it in.` An owed `simulation` blocks
nothing ([P996](https://github.com/xmejkal/spark/issues/1453)): the parts list is offered, and the phase says it as a
warning, such as `Spark cannot simulate “MH-ET LIVE 2.9 Inch E-paper Module, …” for screen yet. The parts list and the
build go on, and a deploy asks your yes for firmware that no simulation tested.` Before a requirements.json, the status is
`problems` once every need that counts has a pick (exit 1, and the guide says the phase has problems), else
`not-started`: the parts phase is `now` and holds the blocker. The guide's NOW sentence of the parts list and of the build
names Claude (`Ask Claude in the chat to build the board. …`) in `flow.py show`, on the page from disk and for a viewer.
Where the published page's script adds the NOW line's button for the owner, it puts the step and `Use the button.` in its
place (`Build the board. … Use the button.`, the words block's `now_button`). A pick's NOW line stays as it is.

The parts phase offers at most three picks per need ([P976](https://github.com/xmejkal/spark/issues/1406)). They are
the need's plausible candidates in the order of `parts.py --match`: each holds the need's words or scores above 0 with
the matcher. A board is plausible for a `compute` need whatever its words. The need's current pick is never offered,
even when it is stored as the drawer entry of its record. Nor is a pick that the pick itself refuses
(`needs.PickPlan`): too few of the part are free. One line of `says` per need counts the rest and names each refused
pick, with "none free" or "too few free" and the other projects that hold it (P991's review), such as `Not shown for
board: 3 more picks; refused: “DFRobot FireBeetle 2 ESP32-C6” (none free, held by p934-epaper). Claude can list them
with parts.py --match.` Two refused picks have "; " between them. A count of 0 is left out.
A need with candidates and none plausible gets no offers and the line `No pick fits <need> by its words. Ask Claude to
run parts.py --match.` When another need's pick cannot get its part, the need gets no offers, and its line holds that
problem's own sentence once, with the part by its name (its record's, else its drawer label), such as `Spark can save
no new pick for wet: the pick for soil cannot get “Soil probe” (…).` (P993: the picks already saved stay.)

Since [P991](https://github.com/xmejkal/spark/issues/1444), the order of `--match` puts a record the person owns before
an owned drawer entry with none, so the first offers are what spark can build from. Each need with a pick has a first
line that names it, such as `Picked for screen: “MH-ET LIVE 2.9 Inch E-paper Module, …”.`, with ", " between two picks.
A drawer entry is named by the record it says it is, else by its label. A pick offer for a `compute` need whose
candidate is no record spark knows asks the parts list's own rule (`need_requirements.board_problems`) with the pick
made. When that refusal names the candidate, the effect says `Spark cannot build from this pick: it has no board file
for “Beetle ESP32 Microcontroller”.` before the history sentence. A board that another need picks is the board the
parts list places, so then the offer says nothing. An offer for a need that does not compute never says it.

The build phase reads `.spark/build.json`. If the folder of `check_spine.py --keep` is a project, the build writes this
file and lists it under `kept`. It holds the build's `status`, its `stages`, the `requirements` file, its sha256 and the
time. The file is named relative to the project when it is inside the project, else by its whole path. If the sha256 of that file is different now, the build phase is `stale`, and the breadboard phase is `stale` too.

A phase with problems adds one item to `problems`, with the code `phase_problems`. A phase that spark cannot read adds
one item to `unchecked`, with the code `phase_could_not_run`. A build that ended in `could-not-run` does the same. The
subject of each item is the phase. The exit is 0, 1 or 2 by those items. If both kinds are there, the status is
`problems` and the exit is 1, and the phase that could not run is still under `unchecked`. Every phase answers either way. For example,
a broken `.spark/needs.json` makes the needs, parts and requirements phases `could-not-run`, and the others still answer.
A `.spark/build.json` that is not JSON, or is no build record, makes the build phase `could-not-run` with one sentence, and
the breadboard phase too when the sheet exists ([P886](https://github.com/xmejkal/spark/issues/1256)).

The needs phase and the idea phase read `.spark/needs-basis.json` ([P1027](https://github.com/xmejkal/spark/issues/1506)):
the needs are `stale` when the goal or the must lines changed after them, and the idea is `stale` when a need was
dropped after the must lines were last gone through. [What the needs were written from](needs-basis.md) says how.

## The page

`flow.py page` writes `page.html` in the project ([P827](https://github.com/xmejkal/spark/issues/1185)). It draws the reading `show` prints (P1060), so a person reads the same facts from the disk, in a browser. Its one script does nothing there ([the page script](#the-page-script)). A line under the title says
what the page is and that every change goes through Claude in the chat. Under it stands the guide
([P977](https://github.com/xmejkal/spark/issues/1407)), the section `id="guide"`: `data.guide` as one line each, NOW with its
phase in parentheses and its sentence, DONE, LATER and SET ASIDE, and a list with no item draws no line.

When `now.steps` is set and the page holds wiring
steps, the NOW line ends in the link "One at a time: start at step N", the wiring section's own link, to the first step's own `#step-N`. The sentence about why there is
no simulation stands as a line of its own under LATER. A `now` that is `null` draws no NOW line. With a guide the line "The
project stands at" is not drawn; a page from a caller that gives no guide keeps it.

Then comes a rail of links, one for each phase,
and one section for each phase. Each section is folded (`<details>`) under its heading: the phase name, a mark and a
status word. Opened, it shows who does it, what it says and its offers as plain text. A section `Wiring` comes when the
project holds a `requirements.json` ([P828](https://github.com/xmejkal/spark/issues/1186)). If the section holds wiring steps,
the wiring, the pictures and the marks come first and the folded phases after them, so a person at the bench finds step 1
at once. If it holds no sheet, the phases come first, each open. In "Before you power it", the host requirements of one part that
stand together are one item, with the part's name once. It has the lines "Before you power it" first, then
the wiring steps, one connection each, which a person can follow to wire a breadboard. When the project is not built, or
was built from other requirements, the section shows no steps and says why in the refusal's own words. A failure that is not the sheet's own refusal gives one fixed sentence: run the build again. The sentence about the Breadboard picture shows only when that picture is drawn. The pictures
follow, in one section. The breadboard comes first when the project holds `breadboard.svg`. The schematic and the PCB are
files too, `dist/board/schematic.svg` and `dist/board/pcb.svg`, which the build with `--keep` writes in a project, so
`flow.py page` alone shows them. It never runs `tsci`. The full rules are in `commands/build.md`. Until a build kept them, the two pictures say why they are not drawn. In a project,
the build writes the same page with all three pictures, after it kept the simulation project. A build that did not finish
removes `page.html` in a project, and `flow.py page` writes it again. If the flow page cannot be written, the build keeps
its own result and lists one `not written` entry. An ok `parts.py --pick` writes an existing `page.html` again, never published ([the next step](#the-next-step)). `flow.py page` replaces a `page.html` that is a link or a FIFO with a file: it never writes through the link and never waits on the FIFO.

The breadboard stands in the page as inline SVG ([P949](https://github.com/xmejkal/spark/issues/1353)), so a player can
find its parts. Each jumper's group carries `data-step`, the number of its step, and holds its wire, its end dots and
its pill (`class="pill"`: the number and the two pads it joins, P953), and each part's group carries
`data-part`, the part's id in the steps. A step that places a part has no jumper, so it has no `data-step`: the step's
part comes from the guide's own data. No key is an `id`. The page inlines the breadboard only when it is plain shapes:
it parses, has no DOCTYPE, uses only `svg`, `g`, `path`, `rect`, `circle`, `ellipse`, `line`, `polyline`, `polygon`,
`text`, `tspan` and `title`, and only attributes of geometry and colour that spark draws with, and its three keys
(`part_pictures.PLAIN_ATTRIBUTES`; no `style`, no `href`, no handler). No value may hold `url(`, `image-set`,
`javascript:`, `expression` or a backslash, read after the parse in any case. One more element may stand
([P946](https://github.com/xmejkal/spark/issues/1349)): an `image` whose one `href` is a JPEG embedded as base64
(`data:image/jpeg;base64,...`), the rule `picture_check.is_embedded_jpeg` that a kept picture of a part passed, with
only `x`, `y`, `width`, `height`, `preserveAspectRatio`, `transform` and `opacity` beside it. No element may stand
inside a `title`. Else the page shows it as an `<img>`, as
it shows the schematic and the PCB, so a script in a hand-edited `breadboard.svg` never runs, and nothing loads. The
dot on each pin is yellow when its row joins a wire or another part and gold when it is free. Under the picture a
legend names the states that the dots draw: "pad in use" and "pad free". "Pad held: do not use" shows only when a pad
is held, and spark draws none yet ([P950](https://github.com/xmejkal/spark/issues/1354)). The page takes the colours of
the wiring page that the PO chose as the model, light and dark, with the system's fonts. It loads nothing.

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/flow.py" page --project . --json
```

With `--json` it prints the envelope with `op` `write-flow-page`. Its `data` holds `file` (`page.html`, relative to the
project), `did` (`wrote`), `stands_at`, `phases`, each only `{phase, status}`, `fingerprint` and `guide`, as `show`'s,
and `artifact`: the id of the Artifact the page is published as, or `null`. A page that cannot be written is one
`unchecked` item with the code `page_not_written`, and the exit is 2. A link, a folder or a FIFO at `page.html.part` is refused and left, never written through, and the item's `fix` says to remove it ([P1054](https://github.com/xmejkal/spark/issues/1551)).
A phase that holds problems does not change this status. Read it with `show`.

`--artifact ID` keeps the id in `.spark/page.json` before it writes the page: `{"artifact": ID}`, the id only, never a
path ([P829](https://github.com/xmejkal/spark/issues/1187)). An id that is no UUID in lower case is a `bad_argument`, exit 2, and nothing is
written. A record that spark cannot read, or that holds no such id, answers `null`.

For an agent or a later script, the page has hooks. Each rail entry and each section has `data-phase` (the phase name) and
`data-status` (the flow's code, or `none` for no status). The `<body>` has `data-stands-at` (the guide's now phase, or `none`
when no phase is open). Each offer is an `<li>` with `data-key` (its key), the `<body>` has `data-fingerprint` (the first
12 hex digits of the fingerprint) and `data-written` (the newest change time of the three files, with its zone, or `none`). All the pictures stand together in the section `id="pictures"`, which the rail links to. The
wiring is in the section `id="wiring"`, which the rail links to as "Wiring". Its steps are the items of `<ol id="steps">`,
each `<li id="step-N" value="N">`, and the lines before power are a `<ul>` of their own, never inside the steps. In that list, a run of one record's host requirements is one `<li>` with the part's name in `<strong>` and a nested `<ul>` of its lines. Each phase's rail link targets `<div id="phase-NAME">` inside the phase's `<details>`, so following it opens a folded phase.

One at a time lives in the URL. The link "One at a time: start at step 1" goes to `#step-1`. While a step is the target of
the URL, the page shows that step alone, with its menu, the element `class="nav"`. The menu says "Step N of M" and has the
links Back, Next, All steps and Picture. Picture shows only when the breadboard picture is drawn. So the browser's Back
button walks the steps. The links "Wiring", "Pictures", "All steps" and "Picture" leave that view, and the browser's Back
returns to the step. In a
browser that does not know the CSS `:has()`, every step shows. When the page prints, every step shows. In a published
Artifact, the fragment may not survive a reload of the outer page. The steps need no script, the page has no checkbox on a step, and
it never says that the board is wired.

The words on the page:

| status | word |
| --- | --- |
| `ok` | ok |
| `problems` | problems |
| `could-not-run` | could not run |
| `not-started` | not started |
| `partial` | partly done |
| `stale` | out of date |
| `null` | not checked by spark |

The page adds no tick. A phase that is not `ok` never shows the tick, whatever mark it carries. It shows the could-not-run
mark. A code that the flow does not know shows as itself. No color says a status. The page reads the project's files and its
board logs, and cannot see the wiring or what the board shows now: one line says so. Every text on it is masked, so no path of the home folder reaches the file.

### The page script

The page ends with one script and its words ([P829](https://github.com/xmejkal/spark/issues/1187)): an inert block
`<script type="application/json" id="spark-words">`, then one `<script>` with no `src`, whose text is
`scripts/spark/flow/page_script.js`. Python writes every word the script shows into the block: per offer it may send its
label and the lines of its confirm, the published page's intro, and the words of the wait and of each answer. The script
fills in only a time, a label or spark's own line, and never shows a key or the fingerprint. Without the block the page
is the page with no script, byte for byte, but its hooks (below). The markup holds no `<button`, `<input`, `onclick` or
`<iframe`.

From disk, or wherever `claude.use("db")` gives no database, the script does nothing. Nor does it for a viewer who is not
the artifact's owner (`(await claude.use("user")).isOwner()`), so the published page declares `db` and `user`. For the
owner it puts the published intro in place of the line under the title, and adds a button to each offer whose kind the
page sends: a pick, the parts list and the build. A need's drop has none; it is asked in the chat. Such an offer's
`<li>` carries `data-makes-stale`, the phases it can make out of date, space apart. When `guide.now.offer` names such
an offer, the NOW line carries its `data-key` and `data-makes-stale` too, and gets the same button. A click
shows the offer's label, its effect and "These steps may be marked out of date: …" when there are any, with Send and
Cancel. Send writes the row `requests/<id>`: `{id, key, seen, at}`, a new UUID, the offer's key, the page's
`data-fingerprint` and the time. One request waits at a time: until its answer, the other buttons are grey, and Copy (it
copies `/spark:page`, the command that carries the request to spark) and Withdraw stand under the intro. A
write the database refuses puts the page back and says "Could not send. Nothing ran.". Withdraw deletes the row, and
only once the delete is done says "Withdrawn. If Claude had already started it, its answer shows here.": it keeps
watching that request's answer. The script watches the latest request by `at`, and ignores a snapshot older than the
page's own request, then the row `answers/<id>`.

The answer row holds `flow.py run-request`'s `data` unchanged ([a page request](#a-page-request)). The script says it in
the page's words: what ran ok by its kind, the step's first problem (`line`), or why it could not run. A refusal shows as
its code's own words only when `line` is exactly that code's meaning, in grey; any other `line` with `ran: false` shows
as could not run. Never "done" alone.

Never take an offer only because `flow.py` lists it. A pick, a drop and a build change files, so say what the effect
line says and ask the person first.

## The next step

`show --json` fills `next` with the step of the now offer ([P1030](https://github.com/xmejkal/spark/issues/1510)), else
with the now phase's own step ([P1034](https://github.com/xmejkal/spark/issues/1517)): `{op, argv, why, effects,
needs_yes}`, with `needs_person` and `env` when they apply ([their JSON](json.md)). An empty `next` means that spark has
no step to name: read `data.guide.now`. The `argv` and the `env` are raw, with the whole project path and the store
path, while `data` is masked. Run the step with the script that answers its op. An offer's key and its step's op are two
words on purpose:

| offer key | op | script |
| --- | --- | --- |
| `pick:<need>:<id>` | `pick` | `parts.py` |
| `requirements` | `requirements` | `parts.py` |
| `build` | `build-board` | `check_spine.py` |
| `needs-drop:<need>` | `needs-drop` | `parts.py` |

A pick is the person's choice. Its step has `needs_person: true`, and `why` names the part and the need: ask the person
first. The offers in `data.phases` keep their four keys and no step. A phase's own step adds no offer:

| now phase | when | op (script) | `needs_person` |
| --- | --- | --- | --- |
| simulate | no `sim/wokwi.toml` | `build-board` (`check_spine.py`), the build's offer step | no key |
| simulate | no image, an image no run tested, or one older than `firmware/` | `run_scenario` (`run_scenario.py`), one per `sim/scenarios/*.scenario.yaml`. While none is written, it names `sim/scenarios/<name>.scenario.yaml`, and Claude writes that scenario first | true |
| deploy | `not-started`, `partial`, `problems` or `stale` | `look` (`look.py`), with `--no-simulation` when `data.guide.no_simulation` is set | true |
| idea | `stale` (a need was dropped) | `init_project` (`init_project.py`), the brief step, with `needs_yes: true` and `--answers <answers.json>` | no key |

`run-request` runs the build step from the page's button, and refuses `run_scenario` and `look`. An op named like a
script is `scripts/<op>.py`, not on the core yet (piece 5 of [P793](https://github.com/xmejkal/spark/issues/1105)). With
`needs_person`, the person acts first: they run a scenario in their own terminal, and it spends Wokwi CI minutes, so ask
before each run. Before a look, they plug the wired board into USB. After a deploy, the deploy phase reads the newest
board log (P1043). Ready seen on the image the project holds now is `ok`, and nothing is open. Ready unknown is `partial`, ready not seen is `problems`, and firmware newer than that image, another image or no image is `stale`, which wins over `problems`; the says line keeps the verdict. Claude acts first on firmware newer than the image and on no image (`by` `["claude"]`), the person's terminal on another image. The cause's words are spark's own, by the code: the log's own sentence, port and console stay in the file. `sim/runs/` is gitignored, so a clone has no board log and shows the deploy `not-started`. The text's NOW line ends with `[<offer key>]`, `[next: <op>]` or `[next: <op>, needs you]`.

After an ok run that writes to a project, `parts.py --pick` and `check_spine.py --keep` end `next` with the same steps
([P1035](https://github.com/xmejkal/spark/issues/1518)), after the command's own, and their text with one `next:` line each,
with `, needs you` after the command for a step with `needs_person` or `needs_yes`, as on the NOW line. A run that is not `ok`, a dry run, a build without
`--keep` and a step that runs the same again get none. Claude fills a `<name>` or an `<answers.json>` before the line runs. A follow-up that fails adds `follow-up: <class> raised, the result stands` on stderr. Then, when the project already has `page.html` as a regular file (no folder, FIFO or link), spark writes it again on disk, whole or not at all, and never publishes it (the PO's D16): the text ends with `wrote page.html again: /spark:page publishes it`, and `--json` holds that sentence as a note with `subject` `page.html`. The build with `--keep` writes its own page. A write that fails adds `refresh: <class> raised, page.html not written again, the result stands` on stderr; the old page and the run's status, items, `next`, `data` and text stand.

## A page request

`flow.py run-request` runs the step that the person asked for on the page ([P829](https://github.com/xmejkal/spark/issues/1187)).
The request is one file, `.spark/page-request.json` in the project: `{id, key, seen, at}`, the page's id for the click
(a UUID), the offer's key, the first 12 hex digits of the fingerprint the page was read at, and when it was sent. Spark
does not read `at`. Claude writes the file from the page's request, as the page sent it. Never write a key or a `seen`
of your own into it.

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/flow.py" run-request --project . --json
```

It reads the file and deletes it at once, so one request runs once at most. A file it cannot delete, and anything that
is no regular file (a folder), runs nothing and is left. Then it reads the flow, as `show` does. It runs the step only
when `seen` is the fingerprint now, the key is one of the offers now, its kind is `pick`, `requirements` or `build`,
and its step's op is `pick`, `requirements` or `build-board`. The fingerprint comes first, so a second click on a pick,
which is no offer once it ran, is stale. It runs the offer's step, its argv parsed by the Operation of its op. A step
whose argv does not parse runs nothing. The values come from spark's offer, never from the request: a pick of that one part for that need, the parts list with no
`--dry-run` and no `--replies`, so it removes nothing, and the build of the project's `requirements.json` with `--keep`
the project. The step writes what the offer's effect says. A deploy, a simulation, a look or a grant is never an offer
here, so a request for one runs nothing.

After any run, run `flow.py page`, so the page carries the new fingerprint (only the build writes the page by itself),
and `flow.py show` for the next step.

The envelope has `op` `run-request`. Its `data` holds:

- `for`: the request's id, so the page matches the answer to its click, or `null` when the id is no UUID.
- `key` and `label`: the offer's key and the words of its button, or `null` when the key is no offer now. A key that is
  no offer never reaches the answer.
- `ran`: `true` when the step ran, `false` when nothing ran.
- `status` and `mark`: how the step ended, as a phase's (`ok`, `problems` or `could-not-run`). A refusal is
  `could-not-run`.
- `line`: one sentence. For a step, its first problem or reason, or `ran <label>: ok` when it ended ok. For a refusal,
  the code's meaning below.
- `note`: `null`, or one sentence beside an ok answer. A build whose only stage that could not run is the simulation,
  with code `board_not_in_wokwi`, built the board, the sheet and the pin map
  ([P1008](https://github.com/xmejkal/spark/issues/1467)). Its `status` is then `ok`, its `line` is `ran <label>: ok`,
  and `note` is the meaning of that code. The guide counts such a build as done, too. The envelope keeps the build's
  own `unchecked` item, so its `status` stays `could-not-run` and the exit stays 2. Decide on `data.status`.
- `fingerprint`: the fingerprint after the run, the whole sha256.

The text output starts with `ran <label>: <status word>`, the word of `data.status`. A step's own `problems` and `unchecked` items are the
envelope's. A refusal is one `unchecked` item, and its fix tells you what to do:

| code | meaning | what to do |
| --- | --- | --- |
| `request_malformed` | the file is missing, is no regular file or no JSON object, holds an id, key or seen that cannot be read, or could not be deleted | write the page's request to the file as the page sent it; if it was written that way, ask the person to click again |
| `request_in_chat` | the key is a need's drop, which is asked in the chat | tell Claude in the chat, for example: drop the light need |
| `request_stale` | the project changed after the page was read: `seen` is not the fingerprint now | write the page again with `flow.py page`, then click again |
| `request_not_offered` | spark does not offer the key now, the page never runs its kind or its step's op, or the step's argv does not parse | write the page again with `flow.py page`, then click again |

A stale refusal is normal: a second Build from the same page is stale once the first one ran. The exit is 0 when the step
ran ok, 1 when it ran with problems and 2 when nothing ran or the step could not run, also for a build with a `note`. Only a wrong argument answers
with no `data`.

## The published page

`/spark:page` publishes the page and carries its requests ([P829](https://github.com/xmejkal/spark/issues/1187),
[`commands/page.md`](../../../commands/page.md), [the how-to](../artifact-how-to.md)). It is the only command that publishes or republishes the page. It reads with `flow.py show --json` and takes no fact from `page.html`, which it reads only to publish. In this order:

1. The first time, `data.artifact` is `null`. On the person's yes: `flow.py page`, `publish_files` with `page.html` as `index.html` and `data.title`, then at once
   `flow.py page --artifact ID`, which keeps the id, so a step that fails after it never leaves a second Artifact. Then
   `declare_capabilities` with `{"db": {"rules": [{"path": "", "read": "view", "write": "owner"}]}, "user": {}}`
   (viewers read, only the owner writes, and the script asks who views).
2. The id from `show`'s `data.artifact`, then the ten newest rows of `requests` by `at`, and the rows of `answers` whose `for` is one of their ids. For each
   request with no answer, the oldest first: the row to `.spark/page-request.json` as the page wrote it,
   `flow.py run-request` in the foreground, `flow.py page`, the republish, and last the answer row `answers/<id>`,
   `run-request`'s `data` unchanged. A refusal goes on to the next request; a step that ran with problems or could not
   run stops the turn. With no request waiting, the page is still written and republished.
3. A republish is `get_artifact` (its version, and its `read` as `shared_live` when shared), `list_files`, then
   `publish_files` with that `base_version`. An Artifact that is not found is gone: the person is asked whether to
   publish again, and a new `--artifact` replaces the id.

The answer comes after the republish, so the page that shows it is already the new one when the person reloads. A
republish with `publish_files` keeps the database's rows and the declaration: checked on 2026-11-21, a row written before
the republish read back the same after it.
