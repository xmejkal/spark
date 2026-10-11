# P100 discovery — the refuter

Run 2026-10-09 against spark 0.8.1 (main a8aa34d). The brief changed on disk during this review (18:21: ★C1's caveat,
★C4 rewritten, F5 added); this report reads the 18:21 version and verification.md as of 18:21.

How it was checked. One copy of the store, `cp -R ~/.local/share/spark <scratch>/refute/store` (18:17); a second copy
`store-w` for the runs that write. Every `parts.py`, `check_spine.py`, `check_all.py`, `emit_board.py` call ran through
a bash wrapper with `SPARK_HOME`, `HOME` and `TMPDIR` as three separate words. Irrigation: an rsync copy without
`node_modules`, its `node_modules` symlinked; `PATH` led with `~/Development/smartbin-local/node_modules/.bin`, but
`check_spine` used the project's own tsci (its output says `tsci 0.0.2663`). No Wokwi. Nothing was written under
`~/.local/share/spark`, `~/Development/irrigation`, `~/Development/plant-alarm` or the bin; the real store's
`history.jsonl` (12:33) and `projects.json` (14:26) were last modified before any council or verification run, read by
`stat` only. `<scratch>` is this session's scratchpad.

## Check first — does the change address the observed problem, and what breaks for current users

The observed problem, in the PO's words (#123 body): *"I'd like to test what works now, you know the basic scenarios,
try a new demo project"*, and (#123, 15:48) *"so we test the system, but with the current store system"*.

What the folder now proposes does not test "what works now" first. D7/D8 make round 0 the documented "Your own dev
board" route, which docs/guide/how-it-works.md:155-156 itself marks *"this was not run for these docs"*, on a C6 board
whose firmware path differs from the one spark documents (commands/build.md:187-188: the image's interpreter is
*"MicroPython v1.29.0 for the ESP32-S3 … for another chip, `--micropython <its .bin from micropython.org>`"*). No round
in items.md or story-map.md re-runs the documented example (STORY_MAP 4.1, "yes, by record") as a baseline before it.
The rounds therefore measure a route the docs call unrun, then a new board's bring-up, before any "basic scenario".
Whether that is what he wants is his call; the folder does not say the order changed what is measured.

What could break for current users (the PO, the bin, irrigation, plant-alarm):
- **The real store.** diary-round-0-board.md says "in a scratch project" and names no store. The facilitator's own
  verification run (below, ★C1) shows that a `SPARK_HOME` set wrongly becomes a new empty store with no warning; one
  left unset reaches `~/.local/share/spark`, and every `--needs-set`/`--pick` from a new folder adds that folder to
  `projects.json` and appends to `history.jsonl`. Reservations are keyed by folder name: my pick from a copy of
  irrigation printed `listed irr on your projects` beside the existing `irrigation`.
- **Irrigation.** Q6's `git mv irrigation.requirements.json requirements.json` renames a file that DIARY.md, PLAN.md
  and the recorded commands name. items.md's bug asks for "`check_spine` on irrigation exits 0 again"; check_spine has
  never exited 0 there (★C4), and the only ways to make it do so are removing the bare `STATUS_LED` signal from the
  project, or making schematic notes non-fatal — which how-it-works.md:37 documents as *"It counts as a problem, so the
  run exits 1 even when the board builds"*. Clearing check_all's FAIL by relaxing the rule would undo the bin's B13
  guard (4daa58f: *"The L9110S inputs, with their pull-downs, still pass"*).
- **Round C's board.** Irrigation's `.spark/project.json` decides the S3; D7 kept the bin's hold; a pick of the S3
  from a copy of irrigation is refused (reproduced, ★C5). Round C cannot come onto the store as D7 leaves it.
- **The bin.** D7 leaves its hold alone. Q3(a), had it been chosen, would have moved the bin's only board.

## 1. The ★ claims

### ★C1 — every library board is held · holds; its new caveat and F5 refuted

Read (my run, store copy, a need `board`):
`refused, so nothing was written: firebeetle2-esp32s3 — 1 owned, held by smartbin-local — 1 picked here` (exit 1);
`board xiao-esp32-c6 stops at the footprint stage (P121) — no header geometry in its board file` /
`refused, so nothing was written: xiao-esp32-c6 — 1 owned, held by plant-alarm — 1 picked here` (exit 1).
The facilitator's exact case (a need `brain`, `does compute`, `what microcontroller`, `brain=firebeetle2-esp32s3`):
`refused, so nothing was written: firebeetle2-esp32s3 — 1 owned, held by smartbin-local — 1 picked here` (exit 1).
The same pick with `SPARK_HOME` at a folder that does not exist: `firebeetle2-esp32s3: to get — known, not owned`,
`would write to your history: 1 reused`, exit 0 — the facilitator's output, word for word.

Why the facilitator's run differed: its history went to a folder literally named
`<scratch>/verify100/store HOME=<scratch>/verify100/home TMPDIR=<scratch>/verify100/tmp/`, whose `history.jsonl` holds
`{"event":"reused","project":"proj","need":"brain","board":"firebeetle2-esp32s3"}` and whose `projects.json` holds only
`proj`. `SPARK_HOME` was the three assignments as one string (zsh does not split a variable), so the pick read a new,
empty store. Its `check_spine` log shows the same: `wrote /var/folders/…/T/spark-spine-5nh70vhk/…` — the system
`TMPDIR`, not the scratch one. The real store was not written (its files predate the run).

Change: the caveat *"PARTLY — the facilitator's own fresh-copy run of the same pick answered `to get — known, not
owned`, exit 0 … the pick's reading of it differs between runs — itself a finding (F5)"* → *"caveat: the XIAO's hold
is plant-alarm's, the recorded walk of 2026-10-08 (store `history.jsonl` lines 1–8); a contrary run read an empty store
— its SPARK_HOME was one unsplit string — not the copy"*. F5 as written is refuted; what the run does show is narrower:
*a `SPARK_HOME` naming a missing folder becomes an empty store with no warning, and every owned part then reads "known,
not owned"* (one reproduction, mine; a guard question for P164). verification.md's ★C1 line ("CONTRADICTED") needs
the same correction.

### ★C2 — only the S3 builds; his other boards have no record · holds; caveat incomplete

Read: `--match`: `owned 1    xiao-esp32-c6 (library)   microcontroller  free 0  stops at the footprint stage (P121)`;
`boards/xiao-esp32-c6.json` `physical` keys: `footprint_export, footprint_module, height_mm, width_mm, wokwi_size_px`
(no `header`). Drawer (copy): `dfrobot-dfr1075 2 … None None`, `dfrobot-dfr1117 3`, `dfrobot-dfr0994 1`,
`dfrobot-dfr0575 2` (count, `is`, `used_in`). `--pick … board=dfrobot-dfr1075`, exit 0, printing
`dfrobot-dfr1075: a board needs a board file — a record in boards/ — before spark can build with it`; then
`--requirements`, exit 1: `refused, so nothing was written: dfrobot-dfr1075 — picked as the board, but a board needs a
board file — a record in boards/ — before spark can build with it, and it has none; spark has one that builds for
firebeetle2-esp32s3; xiao-esp32-c6 stops at the footprint stage (P121) …`.

Change: *"· caveat: none"* → *"· caveat: the pick prints the same warning before it accepts; the counts are his DFRobot
orders' (the import's), not a count of the drawer"*. Why: FEAS-3 says the pick returned "no problem"; 0.8.1 warns in
the pick's own output, which changes the gap the diary would score ("accepted, refused later"). The counts' provenance
is PO-assistant §2's own caveat ("Counts are the import's, not his").

### ★C3 — neither menu domain is servable · holds

Read: `nothing in the library matches 'temperature'.` — the same for `humidity`, `footswitch`, `usb midi`, `gas`,
`co2`, `light sensor`. `--match`: `temp — sense / temperature-humidity` → `sen0193-soil-moisture (shelf) soil-moisture
[other words]`, `vl6180x-breakout (library) distance [other words]`; `switch — input / footswitch` → `tactile-button
(library) button [other words]`; `usb — connect / usb-midi` → `jst-ph-2-power-inlet … power-inlet [other words]`,
`speaker-terminal … speaker [other words]`. `--list`: 13 rows (8 library, 5 shelf), none a thermometer, footswitch or
USB part. `--catalog`: `18 record(s), 0 broken` — jacks, terminals, regulators, RTCs, flow meters, the soil probe. In
`boards/firebeetle2-esp32s3.json` "USB" appears only as a mechanical datum (line 40, `"//alignment": "Both rows are flush
at the end away from USB-C…"`) and in the revision test (line 298).

Narrowing, not a fault: the search covered library, shelf and catalog, so "the library's eight records" understates it.

### ★C4 — irrigation's chain reports problems though it builds · partly

Read (my run on the copy): `[ok  ] build            42 trace(s), 0 errors, tsci 0.0.2663; the documents were measured on
core 0.0.2600`; `[!!  ] schematic-notes  note: STATUS_LED was assigned a pin and no part claims it, so nothing in the
emitted board connects to it`; `the chain is broken`; exit 1. `check_all.py --project .`: `[FAIL] rules-vs-netlist
written rules hold in the design that was built`, `- [floating-input] Valve1.SIGNAL: joined to Mcu.D3 and no resistor to
a rail` (Valve2 `Mcu.A5`, Valve3 `Mcu.D12`, Valve4 `Mcu.D11`); exit 1. Reproduced.

What the claim leaves out, each read:
- `~/Development/irrigation/DIARY.md:134-135` (2026-09-29): `part for any module on this board. Exit 1, "the chain is
  broken": the STATUS_LED note is `!!`,` / `as build.md says it will be.` No line in DIARY.md records check_spine
  exiting 0 on irrigation. docs/guide/how-it-works.md:37: *"It counts as a problem, so the run exits 1 even when the
  board builds"*.
- `~/Development/irrigation/check-all-4.txt` (2026-09-29 18:56): `[ok  ] rules-vs-netlist   written rules hold in the
  design that was built`. spark `4daa58f` (2026-10-03): *"B13: "must not float" now fails a pin that floats — joined
  only to a GPIO, with no resistor to a rail"*. The project's DFR0457 record: *"The signal is a CURRENT load — two LEDs
  behind resistors — not a CMOS input."*
- scrum/VISION.md:52 sits under the header `| | done when | proved by |`: `| **v1 — a stranger's checked board** | from
  an empty directory and the docs alone, on **the documented example and irrigation** | `check_spine.py` exits 0, and
  `check_all.py` shows no `[FAIL]` …` — a target, not a status. scrum/STORY_MAP.md:70: `| 4.2 | irrigation ·
  `check_all` · no `[FAIL]`; each `????` names what to state | the command | **yes** |` — about check_all only.
- commands/build.md:72-73: *"`dist/` is still replaced with a build of the freshly generated board, not of your
  `board.tsx`"* — check_all, run after `check_spine --keep .`, judged the regenerated board (★C5's 13-line diff,
  including a new `BtnModePullupA`), not the committed `board.tsx`.

Change (1): *"while STORY_MAP scenario 4.2 and VISION's v1 line say it passes"* → *"while STORY_MAP scenario 4.2 marks
check_all's no-[FAIL] 'yes'; VISION's v1 line names both results as v1's target"*. Why: VISION.md:52 is "done when".
Change (2): *"cause unexamined (spark's later rules, or the project's data)"* → *"the check_spine exit 1 is the
STATUS_LED note the cold test recorded on 2026-09-29 as expected (DIARY.md:134) — it has never exited 0 there; the
check_all FAIL is new since 2026-09-29 and follows spark 4daa58f (B13, 2026-10-03), meeting four must_not_float inputs
whose module input is an LED load; check_all judged the regenerated board"*. Why: the two halves have different causes,
both findable in the repositories, and one is not a change at all.

### ★C5 — irrigation's board is generated, its requirements file exists, it came onto the store · partly

Read: `~/Development/irrigation/board.tsx:4` ` * DFRobot FireBeetle 2 ESP32-S3 — generated from a module list.`
Regeneration on the copy (`emit_board.py irrigation.requirements.json --project .`, exit 0): `diff` prints 13 lines, of
which 8 are changed lines (four added for `BtnModePullupA`, the pair `Beyond the 1 passive(s)` → `2 passive(s)`, one
jack note added, one tactile-button note removed). `scripts/needs.py:381` `REQUIREMENTS = "requirements.json"`.
`~/Development/irrigation/parts/` holds seven records, each `function= None` (dc-barrel-jack-12v-inlet, dfr0457,
dfr0641, dfr0831, ds3231-at24c32, sen0217, sen0308). From a git-tree copy of irrigation on `store-w`:
`refused, so nothing was written: firebeetle2-esp32s3 — 1 owned, held by smartbin-local — 1 picked here` (exit 1).
council/tech-lead.md, opening: *"In the scratch store I deleted `used_in` from the `dfrobot-dfr0975` drawer file to see
what `--requirements` does once the S3 is free"*. FEAS-8 (3): *"`--function-set` must be run first"* — it does not say
it was run.

Change: *"renamed, with `function` filled on its 3 project records and the multiplicity limits accepted, irrigation came
onto the store in a scratch copy without touching board.tsx"* → *"renamed, irrigation's needs, picks and requirements
ran in a scratch store whose drawer had the bin's hold on the S3 deleted by hand; the store then holds one pick per need
(Valve2–4, Soil2–3, BtnMode kept, not picked); SEN0308 is neither owned nor on the shelf; all seven project records
have `function` null, and FEAS-8 names `--function-set` as needed, not as run"*; and *"differs in 13 lines"* → *"13
lines of diff output, 8 of them changed lines"*. Why: as written it reads "a rename brings irrigation onto the store";
the run reached that only through a scratch-only release that D7 has since declined for the real store.

### ★C6 — no documented path to a running board · partly

Read: no hit for `esptool` or `mpremote` in README.md, docs/guide/*.md, commands/*.md, skills/*/SKILL.md. "flash"
hits, e.g. docs/guide/how-it-works.md:111 `- `flash_image.py`: a flash image with MicroPython and the project's files,
for a headless simulation.`; commands/build.md:186-188 *"the second puts MicroPython and the project's own files into one
flash image (the interpreter is the tools list's `firmware-image` — MicroPython v1.29.0 for the ESP32-S3, fetched and
checked by `/spark:setup`; for another chip, `--micropython <its .bin from micropython.org>`)"*; docs/guide/journey.md:
911-914 `## Bench` / `**Not yet.** No command does this yet. spark's own hardware step is P79 (the link elided), not designed yet.`

Change: *"(no esptool/mpremote/flash anywhere)"* → *"(no esptool or mpremote anywhere; "flash" appears only as
`flash_image.py`'s image, documented for the simulator)"*. Why: "flash" is in five of those files — verification.md's
own ★C6 line says so — and spark already builds a MicroPython image of the project; the missing piece is the step from
that image to a real board, not every step after `pins.py`.

### ★C7 — the green build covers less than the goal · partly

Read: `scripts/check_spine.py:551-554` `EXIT_OK: "  the chain runs end to end",` … `}[code] + (" — but not every need
is on the board: %s" % ", ".join(unserved) if unserved and code == EXIT_OK else ""))`; its docstring at :536 *"so "the
chain runs end to end" never stands alone over a goal the board does not serve"*. My `--match`: `radio — communicate /
wifi  (report)` / `nothing in the store does this — a gap`. `boards/firebeetle2-esp32s3.json` has no `function` key;
"wifi" appears only in ADC2 notes and the radio's peak (lines 198, 220, 233, 397). USER-3: *"I did, after a dry run, and
the pick then passed"* (the bin's S3 and LiPo freed in its scratch store); USER-2: *"I picked the soil-moisture probe
(it is in the library and the drawer) for the temperature need."* I did not rerun the node's check_spine; the mechanism
is confirmed in the source.

Change: add to the caveat *"the exit 0 was reached only after the walker freed the bin's S3 and LiPo in a scratch store
and re-aimed the temperature need at the soil probe (USER-2, USER-3); on the real store the board pick is refused
(★C1)"*. "the exit code is not [honest]" is a reading; check_spine.py:536 states the design (the exit code is the
chain's, the suffix the goal's).

### ★C8 — the third cold test is a weaker model · partly

Read: `~/Development/irrigation/PLAN.md:6-7` *"Predictions are made here so they can be scored honestly later, by an
audit that did not write them."*; DIARY.md:163 `### Predictions, scored against what happened` (no scorer named);
`firmware/main.py:1` `# Irrigation controller — a firmware stub for the simulation, not the product.`; DIARY.md:218-219
*"the diary holds I1–I10. Ten gaps: seven fixed in the plugin the same night (I2, I3, I5, I6, I7, I8, I9 — counted from
this list)"*; DIARY.md:262 `### I11 · FACT · Wokwi's virtual ADC is referenced to 5 V, whatever the chip`, :275
`### I12 · FACT · scenario keys …`.

Change: *"(seven of twelve gaps the same night)"* → *"(seven of its ten gaps the same night; I11–I12 are facts)"*. Why:
the diary's own count. And *"a weaker model than its reputation"* cites no reputation; the nearest is #15's *"found
twelve gaps in one evening and ten of them were invisible to every test"*, whose "twelve gaps" the diary contradicts and
whose "invisible to every test" has no source in DIARY.md or PLAN.md. DIARY.md:223-224 also records that the v1 close
audit corrected the count — an outside reader did touch the scoring, if only the count.

### ★C9 — every logged run was an agent; P100 is slice 1b's test · holds

Read: scrum/VISION.md:40 `| **A constraint** | **The agent at the keyboard.** Every logged run was one. …`; :38 *"Every
"stranger" so far was Claude in one of our sessions, and no person outside the project has installed spark. Slice 5 tests
it with a real one."*; scrum/STORY_MAP.md:38 `| **5** | **A real stranger, to running firmware** | … a person outside the
project, README only, own machine and board, keeps a diary nobody helps with; someone else scores it | **R2.6** (#15),
then F3 and F4 as they pull |`.

Two narrowings: VISION says every logged run was an agent's — "or the PO" is the brief's addition. And R2.6 was slice
5's named item; merged into P100 by D2, slice 5 keeps no item of its own. The claim's caveat does not say so.

## 2. The brief against its detail

### Header
- **Ready for** *"collecting evidence (the frame is proposed, not confirmed)"* vs D5 *"the frame confirmed"* and Q0
  *"answered D5"*: one of the two is wrong.
- **Stands on** *"0 H, 0 of which would change the decision (nothing gathered yet) H, (fill) …"*: risks-and-tests.md
  lists six open assumptions, A1–A6, each "— (decider)". By the brief's own rule ("…or — while any is unrated") the line
  is 6 H, —. "0 H" is stronger than its source.
- **Decision needed** names "the first round" as the demo project; since D7/D8 the first round is round 0 (a C6 board
  record, diary-round-0-board.md). The quoted *"the basic scenarios fully covered"* appears in no PO words in the
  folder, #6 or #123 (grep: brief.md:12, :19 and council/po-assistant.md:32 only).

### Frame
- *"how the two rounds of P100 are run"* — D6 made three; D7/D8 added round 0.
- Start and reach: *"(proposed until Q0)"* though Q0 is answered; *"must not get worse: the irrigation project builds and
  simulates today (`check_spine` end to end)"* — check_spine has never exited 0 on irrigation (DIARY.md:134;
  how-it-works.md:37). The corrected ★C4 says it exits 1; this line still says the opposite.
- Search budget *"two web lookups at most (the domain menu's parts)"*: the councils made four — po-assistant §4 two web
  searches (MicroPython USB MIDI; ESPHome deep sleep), tech-lead §4 one Espressif-docs query and one web search (DFR0975
  deep sleep). None was about the menu's parts. The overrun is not stated.
- Open questions: *"WHICH board (Q4)"* is listed open after D8 answered it; "who scores" / "who scores the predictions",
  "the appetite" / "the appetite in working days", "the pass lines (Q1)" / "the pass line for 'the basic scenarios fully
  covered'" each appear twice.
- Scope: *"the new round ends in firmware that runs"* — singular, while A and B are now separate; items.md's proof for B
  (*"a cited record the person can read and a build using it"*) carries no firmware, so B leaves D2's "ends in running
  firmware" with no D saying so. Round 0 is not in scope.

### What we found — caveats dropped, claims stronger than their source (beyond part 1)
- ★C1: the LiPo a battery node needs is held too — USER-3 *"refused, so nothing was written: 1s-lipo-battery-1000-mah —
  1 owned, held by smartbin-local — 1 picked here"*; FEAS-1. Dropped.
- ★C1/C12: reservations are keyed by folder name (tech-lead §2 raised it as unchecked; shown above). Dropped.
- C10 *"recorded outputs one version behind (0.7.0 vs 0.8.1)"*: docs/guide holds 16 markers "spark 0.6.0" and 28 "spark
  0.7.0" (journey.md 12 and 24); USER-11 names both. The brief keeps only 0.7.0.
- C11 *"the duty cycle decides, not the sleep current"*: PHYS-3's own conclusion is *"with a ≥1 h period the sleep floor
  starts to matter (227 → 116 d)"*. Stronger than the source. And the kept WROOM-1 v1.1 datasheet, page 15, the line
  above Table 12: `Note that the data in Table 12 only applies to the module variants that embed the chip variant
  ESP32-S3.`; page 3: *"Among the module variants, those embed ESP32-S3R8 operate at –40 ~ 65 °C"*, and Table 1 lists
  `ESP32-S3-WROOM-1-N16R8   16 MB (Quad SPI)   8 MB (Octal SPI)   –40 ~ 65`. The PO's DFR0975 is N16R8 (drawer label
  *"FireBeetle 2 Board ESP32-S3 (N16R8)"*), so by the datasheet's own note the 8 µA row is for the variants without
  PSRAM. PHYS-1 and C11 do not say so. D8 then chose a C6, to which no S3 figure applies; C11 is not marked as no longer
  about the chosen board.
- C12 *"the catalog's state (18 records)"*: `--catalog` prints `18 record(s), 0 broken`; `--audit` prints `catalog
  0 current,  17 owe facts,   0 broken` (the eighteenth, sen0193, is counted on the shelf). Two counts of one layer.
- C12 cites FEAS-10, whose *"`store.py` refuses drawer/history writes inside a git work tree, so the rounds' projects
  must be outside the bin's and irrigation's git folders"* is refuted: scripts/store.py:212-214 refuses a private
  *target* inside git (*"… would be inside the git work tree at … point SPARK_HOME at a folder outside it"*); my picks
  from a git-tree copy of irrigation printed `set dfrobot-sen0193: used_in {"plant-alarm": 1} → {"plant-alarm": 1,
  "irr": 1}` and `wrote to your history: 2 reused`. Round C's planning would inherit the wrong constraint.

### Options
- Q3(a) *"zero cost"* drops PO-11: the bin's B14 bring-up is the same firmware-on-hardware step on the same single S3.
- Q3(c) and D7 *"about a day"*: no source.
- Q4 *"the plant alarm's shape (S3 + soil probe + LED + button)"*: `~/Development/plant-alarm/requirements.json` is
  `{"board": "xiao-esp32-c6", "parts": ["sen0193-soil-moisture", "max98357a-dfr0954"]}` — a XIAO (which stops at the
  footprint stage), a probe and an amplifier. *"the only goal the library serves fully today"* rests on "from ★C3",
  which is about the menu domains; nothing in the folder shows an S3 + probe + LED + button goal served fully (USER-5's
  S3 + probe build left `batt` and `report` unserved). After D8 the S3 premise is moot.
- Q5: the MIDI option needs a USB-device-capable S3 (PHYS-4); D8's C6 cannot be one. Not marked.
- Q6 *"find why irrigation no longer builds (★C4)"*: contradicts the corrected ★C4 (it builds) and DIARY.md:134 ("no
  longer").

### Riskiest assumption and its test
- *"or if irrigation is already broken (★C4)"*: after the correction, it builds; the exit 1 is documented behaviour.
- Test (1) *"watch whether the release and the pick are documented acts"*: D7 declined the release; under D7 it
  watches nothing.
- Test (2) *"a MIDI note seen on the Mac"*: impossible on D8's C6 (PHYS-4: *"the XIAO C6 cannot present a MIDI device
  however it is wired"* — the chip, not the carrier).
- Test (3) *"record ★C4's cause"*: answerable from the repositories now (DIARY.md:134; 4daa58f).

### Found on the way
- F1 *"a regression in spark or in the project's data since 2026-09-29"*: refuted for check_spine (the same exit on
  2026-09-29); for check_all the change is spark's deliberate B13 (4daa58f). "The project's data" (four must_not_float
  entries on LED-load inputs) is the remaining rival.
- F5: refuted (★C1).
- F3 *"one version behind"*: two (0.6.0 and 0.7.0 blocks).

### Decisions — internal consistency
- D5 confirms *"two rounds"*; Scope and D6 say three; the header says the frame is not confirmed. D5 confirmed a frame
  that has since changed (three rounds, round 0, the board); nothing records his yes to the changed one.
- D6: the chosen label *"Two rounds: owned first, then new parts (Recommended)"* against the D's *"P100 has three
  rounds"* is consistent only if the label's two rounds are A and B with C carried from D1. The D does not say so, and
  D5's "two rounds" meant new + irrigation: the same words with two meanings on one page.
- D7: the label *"Research one of your other boards first"* matches option (c); *"(a board record, about a day)"* is the
  facilitator's estimate, not his.
- D8: *"For now, lets just create one from these"* names no board; the D records the facilitator's recommendation (the
  C6) as his choice — "taken as" says so, and the D still lists it as his. "For now" (provisional) is not carried into
  the D's first half. D8 cites *"AskUserQuestion Q4"*; the Options' Q4 is round A's domain.
- Board actions: (fill), and items.md says *"none taken"*; two were taken — #6's comment of 2026-10-09T15:59:35Z (D5,
  D6) and #123's of 16:13:47Z (D8's requirement, as *"the first fix in this epic's concept"*).

### The other files against the brief
- jobs Job 2 *"a PLAN.md with eight predictions"*: holds (PLAN.md:29-50). Job 3 *"twelve gaps, ten invisible to the
  tests"*: the diary counts ten gaps; "invisible" has no source in it.
- Journey A step 2 *"his drawer has 112 entries"*: `--drawer` on the copy reports `total: 110`; 112 is the store
  design's estimate (docs/2026-10-04-store-design.md:66, *"about 112 entries"*).
- Journey C step 1 *"it does not build today on 0.8.1 (★C4)"* against step 4 *"works today for the current
  board.tsx"*: they contradict each other and the corrected ★C4.
- risks-and-tests A6 offers two causes; the third (no change: a documented note since 2026-09-29) is ruled in by
  DIARY.md:134. The risk table's rows carry five cells under a four-column header. The "wake and low power" row speaks
  of the S3; D8's board is a C6, and `~/Development/smartbin-local/CLAUDE.md` (Power) records *"`Pin.irq(wake=DEEPSLEEP)`
  silently no-ops on the C6"* and *"`esp32.wake_on_ext0` does NOT exist on the C6"* — neither is in the folder.
- story-map Delta *"STORY_MAP scenario 4.2 and VISION's v1 line say irrigation passes `check_spine`"*: 4.2 is about
  check_all; VISION:52 is a target. Refuted as worded. Slice A *"the plant alarm's shape"*: see Q4.
- items.md: the title *"Irrigation no longer builds on spark 0.8.1"* and the proof *"exits 0 again"* — "no longer" and
  "again" are refuted.
- diary-round-0-board.md names no store for the run (see Check first). P0.6's candidate gaps omit the C6's MicroPython
  wake limits and `flash_image.py`'s S3 default.

## 3. Rival explanations the folder does not rule out

- **★C1 "held".** (a) A demo's reservation: the XIAO's hold comes from plant-alarm, the recorded walk of 2026-10-08
  (store `history.jsonl` lines 1–8: steps C and L, `passed_over … firebeetle2-esp32s3 … "held by the bin; a C6 would
  do"`); the folder is not a git repository and holds only `board.tsx`, `requirements.json`, `.spark/needs.json`. Not a
  stale `projects.json` (the folder exists), but not a project in use either. The S3's hold is the bin's live one.
  (b) "The pick reads the hold unreliably" — ruled out here (empty store, ★C1).
- **★C2 "his other boards have no record".** Ruled out for the repository (`boards/` holds two) and the store (no board
  in shelf or catalog). Open: whether a project-level `boards/<id>.json` is enough for `--requirements` to accept a
  drawer entry without `is` — the refusal text names "a record in boards/" without saying whose `boards/`; not tested.
- **★C3 "not servable".** A vocabulary miss (C10 shows `soil sensor` misses where `soil moisture` hits) — ruled out by
  `--list` and `--catalog`, which hold no such part under any word.
- **★C4 "the chain reports problems".** (a) No change at all — the documented bare-signal note, exit 1 since
  2026-09-29: ruled in by DIARY.md:134 and how-it-works.md:37. (b) For check_all: a deliberate rule tightening (B13,
  4daa58f) meeting four `must_not_float` entries on inputs the DFR0457 record calls an LED load — a false positive the
  project's rules file invites, neither "a regression" nor plainly "the project's data". (c) The copy's environment:
  unlikely — the failing stages are Python (schematic-notes, rules-vs-netlist), and the build passed under the project's
  own tsci; but check_all judged the regenerated board, not the committed one (build.md:72-73).
- **★C5 "came onto the store".** It came onto a scratch store with the bin's hold deleted; on the store as it is, the
  board pick is refused (reproduced). Not ruled out by the folder: that "onto the store" means only needs and picks,
  while the board stays outside it.
- **★C6 "no documented path".** Documented under another word: `flash_image.py` makes the project's MicroPython image,
  documented for the simulator. The gap may be one undocumented write (the image to the board), not the whole path.
- **★C7 "the exit code is not honest".** By design: check_spine.py:536 separates the chain (exit) from the goal (the
  suffix). That it misleads a reader is USER-5's own H (*"whether a reader misreads it (H, mine)"*).
- **★C8 "a weaker model than its reputation".** No reputation is cited; the rival is that nobody held it as more than
  what #15 says — a source of gaps.
- **★C9 "measures slice 1b".** The PO may have typed commands himself in unlogged runs; VISION speaks only of logged runs.
- **C11 "the duty cycle decides".** At an hourly report the sleep floor halves the life (PHYS-3's table); and for the
  PO's N16R8 the datasheet's deep-sleep row does not apply by its own note — the floor is unknown, not 8 µA.
- **A6 / F1 "regression or data".** See ★C4 (a) and (b).

## 4. Numbers without unit, population, period or provenance

- **C11** *"8 µA"*: datasheet-typ at 25 °C, module only, and — by the datasheet's note above Table 12 — for variants
  embedding the ESP32-S3, not the PO's N16R8; the temperature and the scope are dropped. *"1000 mAh"*: the drawer
  label's, a cell held by the bin. *"80% usable"*: H, no source. *"100 mA × 5 s"*: H. *"~59 days … ~227 days"*:
  calculated at 8 µA sleep only (I recomputed: 564 µA avg → 59 d; 147 µA → 227 d); at 148 µA or 174 µA the same
  formula gives 47/46 d and 116/107 d. *"140 µA"*: for 8 MB octal PSRAM at 3.3 V, footnote 1 on the Light-sleep row.
- **"the library's eight records"**: `parts/` at a8aa34d; `--audit` counts the library as 10 (8 parts + 2 boards);
  `--list` shows 13 (with the shelf's 5).
- **"18 records"** (C12): `--catalog` on the 2026-10-09 copy; `--audit` says 17 owe facts in the catalog. Store-design
  §5.4's "all owed" is 2026-10-04's statement.
- **"twelve gaps"** (jobs Job 3, #15, #6 comment): the diary's items I1–I12, of which ten are gaps; "ten … invisible to
  every test" has no source in the diary.
- **"seven of twelve"** (★C8): the diary says seven of ten.
- **"eight predictions"** (Job 2): PLAN.md's eight numbered predictions — provenance holds; who scored them is unnamed.
- **"13 lines"** (★C5): lines of `diff` output, 8 of them changed lines, on a regeneration made 2026-10-09 with
  0.8.1.
- **"42 trace(s)", "four floating-input findings"** (★C4): the regenerated board's, built with tsci 0.0.2663 from
  irrigation's own `node_modules`, not the committed `board.tsx`.
- **"112 entries"** (Journey A step 2): a 2026-10-04 estimate; 110 counted on 2026-10-09.
- **"DFR1075 ×2, DFR1117 ×3, DFR0994, DFR0575 ×2"** (★C2, Q3c): bought counts from the DFRobot import, not a count of
  what is in the drawer.
- **"about a day"** (Q3c, D7): no provenance.
- **"0.7.0 vs 0.8.1"** (C10, F3): 16 markers of 0.6.0 and 28 of 0.7.0 in docs/guide.
- **"6 agents, 499 calls and about 90M input tokens"** (the Depth comment): "measured once", no pointer to where.
- **"355 mA"** (check_all's physics line on irrigation, and USER's walk): untraced; USER says it appears identically in
  README.md:47 for a different design.
- **Round 0's predictions** (*"under 20 minutes"*, *"over 60 minutes"*, the confidences): no statement of how wall time
  is measured or by whom.

## Searches

None — no web search and no documentation-server query. Local reads only: the folder's files; spark's README.md,
docs/guide/*.md, commands/*.md, skills/*/SKILL.md, scrum/VISION.md, scrum/STORY_MAP.md, boards/*.json, scripts/
(check_spine.py, needs.py, store.py, emit_board.py); `git log -S` for "no part claims it" and "no resistor to a rail";
irrigation's DIARY.md, PLAN.md, check-all-4.txt, parts/, firmware/main.py; plant-alarm's files; the store copy's
drawer, history and projects files; the facilitator's `verify100` scratch logs; the kept WROOM-1 v1.1 datasheet (pages
1-6, 15) from the store copy; `gh issue view` of #6, #15, #80, #123 (read-only).
