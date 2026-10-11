# Council — the user's journey, as a HUMAN typing (P158 part 1)

Written 2026-10-10 by the user-human lens, against spark 0.8.1 (main `a8aa34d`, `git log -1`). The question asked of
this lens: walk the job as a hobbyist does it today — an idea and a drawer, through every finding in `../catalogue.md`
(K1–K74), to a running board — and say where they stall, guess or come to harm (a short, a wrong store, a wrong
number), what the terminal would have to print for them to know where and why, and which proposed change moves their
experience most.

**How the walk was made.** I read the catalogue, the six diagnoses and their six verifications, the P100 folder
(`brief.md`, `items.md`, `risks-and-tests.md`, `verification.md`, `diary-round-0-board.md`, every council report),
irrigation's `DIARY.md`, the store cards (`gh issue view`, read-only: #17, #94, #99, #101, #123, #16, #93, #102), and
then the pages a hobbyist is handed: `README.md`, `commands/idea.md`, `build.md`, `drawer.md`, `research.md`, `init.md`,
`docs/guide/how-it-works.md`, `journey.md` (the recorded run, Firmware, Bench), `GLOSSARY.md`'s "Pick, and reserve", and
the terminal-facing code (`parts.py` `_say`, `OPERATIONS`, `_matches`; `needs.py` `_how_to_free`; `outcomes.py`;
`store.py` `home()`). Where a claim is about what the terminal prints I typed it myself, twice over: on a copy of the
PO's store (`cp -R ~/.local/share/spark <scratch>/store`, 2026-10-10) and in an **empty** store (`<scratch>/store-empty`,
the stranger's first hour), every command with `SPARK_HOME`, `HOME` and `TMPDIR` as three separate words
(`env | grep SPARK_HOME` under the prefix printed the scratch path once, first), `tsci 0.0.2621` from the bin's
`node_modules/.bin` on `PATH` for the one build, bash. The real store was not run against and not written; nothing was
written under spark but this file. Tags: **E** a pointer or a run and its output; **H** a claim with its source; **D** a
decision (who, when); — unknown. The PO's criteria (D, 2026-10-10): testable · diagnosable (where and why, to a person
and to an agent) · simple (remove before add).

**One limit above every finding.** No human has done this walk. Every account in the P100 folder is an agent's
(★C9, `scrum/VISION.md:40`), and mine is an agent's too; "a hobbyist would …" is H wherever it appears below. What is E
is what the terminal printed and what the pages say.

## 1. Findings

Ordered by what matters most to the person at the keyboard; the stage of the journey each belongs to is in brackets,
and the walk in order is at the end of this section.

- **USER-HUMAN-1 · The job ends at `pins.py`, and the page says so only by saying nothing** [firmware → bench] ·
  claim: after `assign_pins.py --emit-pins firmware/pins.py` the documents a hobbyist is given stop: no command, page
  or tool entry puts code on a board (`esptool`, `mpremote` appear in no README, guide, command or skill), `flash_image.py`
  builds an image for the simulator and names no board (its interpreter is a store-wide role, the S3 build), and
  Bench is "Not yet. No command does this yet." The README block never makes `firmware/`: in my first-hour run the folder
  existed only after I typed the `--emit-pins` line from build.md myself. · **E** my first-hour run (`ls` → no
  `firmware/` after the six README lines); `docs/guide/journey.md:911-914`; `README.md:77`; FB diagnosis RC-2 and its
  verifier (the grep → 0 files, 2026-10-10; `flash_image.py:72-76`); the user lens USER-7 · supports only: the
  documents and the code — a Claude session may carry a person past this (H); nothing has run on hardware (`README.md:219`).
- **USER-HUMAN-2 · "I own nothing" and "I am in the wrong store" print the same lines** [pick] · claim: a `--pick`
  in an empty store answers `firebeetle2-esp32s3: to get — known, not owned · listed <project> on your projects · wrote
  to your history: N reused`, exit 0; a `--pick` with `SPARK_HOME` naming a folder that does not exist answers the same
  lines word for word (`would list proj on your projects`, dry run), exit 0, and the folder is still absent afterwards;
  `SPARK_HOME=` (an empty value, the shape of #101's incident) silently uses `~/.local/share/spark`. Nothing printed names
  the store that answered. · **E** my runs: the first-hour `--pick` (empty store), run 6 (`store-missing`, `ls` → "No
  such file or directory"), run 7 (`store.home()` with `SPARK_HOME=` → `<home>/.local/share/spark`); `store.py:46-52`;
  SL diagnosis RC-2, its verifier M1 · supports only: the text mode on 0.8.1; whether a hobbyist ever sets `SPARK_HOME`
  is — (the pages tell agents to).
- **USER-HUMAN-3 · The plain refusal of a held part withholds the fix the JSON carries, and the listing never prints the
  key the fix needs** [pick] · claim: on the PO's store copy `--pick <proj> board=firebeetle2-esp32s3
  batt=1s-lipo-battery-1000-mah` prints two lines, `refused, so nothing was written: … — 1 owned, held by smartbin-local —
  1 picked here`, exit 1, and nothing else; the same with `--json` carries `fix: free it — a file holding [{"entry":
  "dfrobot-dfr0975", "used_in": …}] without smartbin-local, given to --drawer-set <file> after a dry run — or pick
  another`. The plain `--drawer` prints label, count, `is`, unsure/skip — no `dfrobot-dfr0975`, no `used_in` — while
  `drawer.md:43` says "give its key as `entry`". There is no `--release`. · **E** my runs 5 and 5b; run 2 (`--drawer`
  columns); `parts.py:2182-2184` (`fix` printed only when an answer has no lines); `parts.py:1772-1774`;
  `needs.py:250-257`; `commands/drawer.md:43-44`; the P100 user lens USER-3 (the walker grepped the store's files for
  the key) · supports only: the text mode on this store; for the PO every second project on the one FireBeetle meets
  it (the LiPo too).
- **USER-HUMAN-4 · A pick that does not fit is taken silently** [pick] · claim: `--match` for `temp — sense /
  temperature` offers the soil probe and a rangefinder, each marked `[other words]` with no legend anywhere in the
  answer; `--pick <proj> temp=l9110s-module --dry-run` — a motor driver for a temperature need, a verb the matcher
  would never list — answers `would set blue-l9110s-motor-driver: used_in null → {"proj": 1} · temp: l9110s-module ·
  would write to your history: 1 reused`, exit 0; and a wrong need cannot be dropped (`idea.md:24-25`: "fixed by hand in
  `<project>/.spark/needs.json`"). · **E** my runs 4 and 8; `parts.py:1963` (the only place `[other words]` is written —
  no legend line); NM diagnosis RC-2/RC-3 and its verifier M1 (the same wrong-verb run) · supports only: the pick path
  on 0.8.1; whether a person reads `[other words]` as a warning is H (USER-2's "would either quit here or accept a
  sensor that does not do what they wanted" is one walker's reading).
- **USER-HUMAN-5 · Quoting decides what `--need` finds, and the answer never says so** [idea] · claim: `--need "soil
  sensor"` (one argument, the way `research.md` and the refusal's own `/spark:research "soil sensor"` show a phrase)
  → `nothing in the library matches 'soil sensor'. Research it: …`; `--need soil sensor` (two arguments) → the
  SEN0193. The test is `all(word in haystack)` over the **arguments**, as substrings, so a quoted phrase must appear
  verbatim; `"12 V inlet"` works either way only because two catalog records carry that exact alias. The output names the
  phrase and never says it was searched as one word, which four fields were searched, or that the drawer is not. · **E**
  my runs (quoted vs unquoted, 2026-10-10); `parts.py:1326-1329`; irrigation `DIARY.md:26-31` (I1, 2026-09-29); the
  user lens USER-9 (quoted); NM verifier M5 (the substring test) · supports only: these phrases on this store; it
  explains why the P100 lenses found nothing where my unquoted run found the probe.
- **USER-HUMAN-6 · The drawer is mute, and no answer says so** [drawer → match] · claim: on the 2026-10-10 copy 110
  entries, 91 with neither `is` nor `function`, so no need reaches them; `--match` for `board — compute /
  microcontroller` lists the two library boards (`free 0` each) while the drawer holds six ESP32 SKUs; `--drawer` has no
  function column, `--audit` counts silent records and no entries, `--match` shows what it found and never what it could
  not look at. · **E** NM diagnosis RC-4 and its verifier (the same count, a script over `drawer/*.json`); my run 4
  (`--match`); `drawer.py:276-284`; `parts.py:171-172` · supports only: the PO's store (99 of the 110 are imports —
  SL verifier RC-1 (4)); a stranger who types the drawer is asked `function` at entry (`drawer.md:28`), one who imports
  is not (`drawer.md:55`, the payload is `{sku, name, count}` by D the PO 2026-10-04).
- **USER-HUMAN-7 · The agent is told what to do next; the person is not** [every step] · claim: `_say` prints, in text
  mode, the answer's lines only; `answer.next` (the `next` steps §6.4.2 defines) goes into the JSON envelope and is never
  printed as text, and a `fix` is printed only when there are no lines. So every "what now" spark knows reaches the
  agent and not the terminal. · **E** `parts.py:2173-2185` (read); `outcomes.py:75-78` (`step()`); my runs 5 vs 5b ·
  supports only: `parts.py`'s text mode; the design is "for agents first" (D the PO, `docs/2026-10-04-store-design.md`
  §6.4), so this is a consequence of a decision, not an oversight — and the README promises the terminal persona
  (`README.md:182-188`).
- **USER-HUMAN-8 · Two documented orders, two results, and a sentence that blames the person** [init → checks] ·
  claim: typing the README's order (`init` after the build) `check_all` says `1 check(s) could not look: physics`, exit 2,
  with `rules-vs-netlist` `[ok]`; typing `idea.md:126`'s order (`init` before `--requirements`, before any part exists)
  it says `2 check(s) could not look: physics, rules-vs-netlist` with `the rules file states no rule to compare: i2c_buses
  and must_not_float are both empty, which is what /spark:init writes and where they have stayed` — true of the file,
  false about the cause (init ran before the parts it would have seeded from), and the fix text sends the person to type
  entries by hand that `--force` derives. · **E** my first-hour run (init after the build → one `????`); CC diagnosis
  RC-1 (init before parts → two, the sentence verbatim) and its verifier (holds; MC-6: the derivation needs no build) ·
  supports only: the two documented sequences on 0.8.1.
- **USER-HUMAN-9 · A number on the line with no source on the line** [checks] · claim: for a button and an LED
  `check_all` prints `? V33: draws 355 mA of 1.50 A, resting on figures nobody has verified: Mcu.3V3: regulator_3v3_a`.
  The 355 mA is the WROOM-1 module's own radio transmit peak, `module_peak_a` in the board record (verified, Table 11 of
  the datasheet), summed as the rail's own draw by design (`own_draw`, P52); the line says none of that. The P100 user
  lens listed it under what it could not check; the catalogue traced it. A person building a button sees "355 mA" and
  has nothing to check it against. · **E** my first-hour run; `boards/firebeetle2-esp32s3.json:132-135`, `:393-399`;
  `check_physics.py:309`; `../catalogue.md` "Not a fault" (the 355 mA entry); the user lens "What you could not check"
  (the 355 mA) · supports only: this line; the figure is right by its record — the finding is that the line does not say
  where it is from, the PO's own criterion ("a wrong number") turned around.
- **USER-HUMAN-10 · The one line a person reads is about a board they do not have, or is false by agreement** [build]
  · claim: with `--keep .` an existing `board.tsx` is "left alone" and `dist/` is the regenerated board's, so the
  verdict, `check_all` and the `built` record describe a board the person does not have beside the one they do
  (irrigation: 13 diff lines); and on irrigation the chain prints `the chain is broken`, exit 1, for the one signal the
  person declared (`STATUS_LED`), as it has since 2026-09-29 — a verdict the diary records as expected and therefore stops
  reading. · **E** CC diagnosis RC-2, RC-3 and its verifier (holds); `commands/build.md:72-74`;
  `~/Development/irrigation/DIARY.md:134-135`; #44 (D the PO, 2026-10-05: build the kept file) · supports only: projects
  with an edited `board.tsx` or a bare `signals` entry (irrigation is one; the bin's board is hand-written).
- **USER-HUMAN-11 · Three mouths on one owed fact, and the chain refuses what the store calls merely owed** [match →
  requirements] · claim: `--need rtc` prints `--promote … --project . builds with it` for records that `--audit` lists
  as `owes: pin_order_proof, simulation` and that `--requirements` then refuses; and a record owing `pin_order_proof`
  alone is refused by the chain's parts stage as "does not meet the part contract" (exit 2) while `--audit` calls it owed
  and `--need` says it builds. The person reads the promise first and the refusal second. · **E** CC diagnosis RC-4 and
  its verifier (the `<scratch>/proj-proof` run; MC-3); `parts.py:97-98`, `:1631`; #102 (D the PO, 2026-10-08: "check when
  is what actually needed") · supports only: the catalog's 17 owed records on the copy (`--audit --json`, CC
  diagnostician, 2026-10-10).
- **USER-HUMAN-12 · A board the person owns with no file: taken, recorded, then refused, then a five-step page** [pick
  → requirements] · claim: `--pick <proj> board=dfrobot-dfr1075` writes the hold, the `reused` line and the project
  listing and prints `a board needs a board file — a record in boards/ — before spark can build with it`, exit 0;
  `--requirements` refuses; the hold and the event stay; the remedy is `how-it-works.md`'s "Your own dev board", five
  steps that round 0 (an agent) ran in 14 minutes with ten gaps (G0.1–G0.10). Four of the PO's six owned ESP32 SKUs have
  no file (DFR0575 ×2, DFR0994 ×1, DFR1075 ×2, DFR1117 ×3 — the import's counts). · **E** BR diagnosis RC-6 and its
  verifier (reproduced; the state left behind); `council/round-0-runner.md`; `diary-round-0-board.md:19-25` · supports
  only: the pick/requirements split as it is; D8 (the PO, 2026-10-09) names the automatic board record as the first fix.
- **USER-HUMAN-13 · On the own-board route a mistake no check names reaches every check** [own board → build] ·
  claim: a board file whose pad labels are bare GPIO numbers passes `--validate`, `--for-fab` and the footprint; tscircuit
  then reads `"17"` as pin position 17 and the netlist every check reads has the 3V3 pad answering to `17` and GPIO14/15
  grounded (no copper short observed in tsci 0.0.2621 — the verifier's narrowing); the only message arrives two stages
  later and names an unrelated open terminal, while tscircuit's own `Could not find port for selector ".Mcu > .MISO"`
  sits in `circuit.json` and `check_spine` returns on the island before it reads the errors (BR verifier M1). The
  stand-in's missing pin stops at the last stage with `"14" is not a pin of board-esp32-c6-devkitc-1` — a number, not a
  cause or a remedy. · **E** BR diagnosis RC-1/RC-2 and its verifier (holds; M1); FB diagnosis RC-1 and its verifier
  (the two library boards' "absent" pins are name mismatches, 0 GPIOs absent — a correction that matters for the fix);
  `round-0-runner.md:22-25` · supports only: the own-board route and a hand-edited `board.tsx`; the shipped S3 meets
  K23 only once a design spends `MOSI`/`MISO` (21 LEDs; the FB diagnostician's "found on the way").
- **USER-HUMAN-14 · The silent harms a person can meet, each verified on a copy and met by no lens** [various] ·
  claim: (a) `--promote <part> --project <p>` prints `would promote to ~/Development/spark/parts/<id>.json` — the plugin
  folder, which the next update replaces; the person is told it was kept (K12); (b) `--fact-set` accepts `body_mm` of
  −3 × 0 and calls a non-number "absent" (K54); (c) a `requirements.json` whose top level is a list is replaced by an
  object and the answer lists what was written, not what was lost (K61); (d) `--fetch` drops a URL that does not answer,
  status `ok`, and the record then cites a document the store never kept (K17); (e) a two-entry `--drawer-set` can
  write one entry and stop with a Python list repr (K8); (f) a sync client's `(conflicted copy).json` in `drawer/`
  doubles what is owned (`owned 16`, the drawer holds 8) until the first write refuses a key the person never typed
  (K9); (g) `flash_image.py` packs an interpreter built for another chip without a word (FB RC-2) — the board prints
  nothing on the bench. · **E** SL diagnosis RC-3/RC-4/RC-5 runs and its verifier; CC diagnosis RC-5/RC-7 runs and its
  verifier; FB diagnosis RC-2 and its verifier (the chip-id read: 9 = ESP32-S3 is E from esptool 3.3's source) · supports
  only: reproductions on copies; none was met in a P100 walk.
- **USER-HUMAN-15 · The rule that fails irrigation's valves cannot be told the thing the record already says** [checks]
  · claim: `check_all` fails `rules-vs-netlist` with four `[floating-input] ValveN.SIGNAL … no resistor to a rail`; the
  DFR0457 record's own note says the input is a current load (an opto's LED behind a resistor) that cannot float into
  conduction; the finding's remedy — "remove the rule if the part pulls it itself" — is undone by the next `init
  --force`, which re-seeds an emptied list, or nagged entry by entry; and the rules file's `//` note claims the four
  entries were "Seeded from every pin the design's own part records declare" when the diary shows the person typed them
  on 2026-09-29, a day before seeding existed (CC verifier RC-8, MC-2). A person deciding whether they may delete an
  entry is misled by the file's own words. · **E** CC diagnosis RC-1/RC-8 and its verifier (`init_project.py:296-302`;
  irrigation `c6c583e`, `DIARY.md:203-205`); the refuter's ★C4 · supports only: irrigation today; plant-alarm's four
  amplifier inputs would fail the same way on its first seed (CC verifier MC-5).
- **USER-HUMAN-16 · The tally never counts for a person typing, and the README's typed block ends in it** [tally] ·
  claim: after the README's six lines in an empty store, `--tally .` prints `3 picks: 3 from the store (0 owned) — its
  cost was not counted … no step of first-hour is in the history — parts.py --step <project> <step> marks each`, exit 2;
  with the four `--step` marks the docs verifier got `no transcript of session … here`, exit 2 — honest and named both
  times, and the block was written to end there (`README.md:121-123` explains its own exit 2). · **E** my first-hour run;
  DC diagnosis RC-2 and its verifier (five-and-one reproduced); `cost.py:225`, `:232` · supports only: the terminal
  persona; in Claude Code the line ends with the cost (`journey.md:384-385`, an unrecorded run of the author's).
- **USER-HUMAN-17 · The recorded outputs are behind the version and, where compared, right** [documents] · claim:
  44 markers say `spark 0.6.0` (16) or `0.7.0` (28), none `0.8.x`, against plugin 0.8.1; the five blocks the docs
  diagnostician re-ran, the three the user lens compared and my first-hour build (`journey.md:341-358` against my
  `check_spine` output: the same 17 lines, the same `tsci 0.0.2621; the documents were measured on core 0.0.2600`) match
  in form. · **E** DC diagnosis RC-1 and its verifier (the grep re-measured); my run · supports only: the blocks compared
  (the `--match`/`--pick`/`--audit` blocks need the 2026-10-08 drawer, not rebuilt); "behind" is measured, "wrong" is
  shown nowhere.
- **USER-HUMAN-18 · The first hour is both undocumented and skipped by every run** [install → drawer] · claim: the
  install path "was not run for these docs" (`README.md:102-103`), the drawer's words-to-entries and the DFRobot import
  "were not run here" (`:70`), research "done by agents, not run here" (`:72`); the PO's store starts past all of them
  (110 entries, 18 catalog records on the copy), so no run — P100's or mine — has seen the empty-drawer, empty-store
  start except my six-line README run, which is the one path that does not touch the drawer. · **E** `README.md:62-72`,
  `:102-103`; DC diagnosis RC-3 (about 20 "not run" admissions, re-counted 21 by its verifier); PO-15 · supports only: the
  documents' own admissions; the structural ones (a conversation, Claude in Chrome, an agent) cannot be run by a script.
- **USER-HUMAN-19 · No page or output says "start here" to a person at a terminal** [before the first command] · claim:
  `parts.py --help` is argparse's usage line over 28 operations (counted in `OPERATIONS`), `docs/guide/commands.md` has no
  "without Claude Code" section (`grep -n -i 'terminal\|without claude\|typing'` → nothing), and the one place that
  lists the terminal persona (`README.md:182-188`) sends them to the guide for AI agents. The design says agents first
  (§6.4, D the PO 2026-10-04); the README promises both. · **E** my run 1 (`--help`); my grep; `parts.py:1472-1529`
  · supports only: the pages and the usage text; whether a hobbyist would type these commands at all rather than drive
  Claude is the PO's account question (user lens Q11, unanswered).
- **USER-HUMAN-20 · The inlet case shows the data has been patched where the code should have been** [idea] · claim:
  "12 V inlet" is found only because two catalog screw terminals and irrigation's jack carry that exact phrase as an
  alias, written on 2026-09-29 to work around I1; the library's JST inlet, which `power inlet` finds, is still hidden
  behind the word "12". A person's own words are matched against words someone already typed into an alias. · **E** my
  runs (`--need 12 V inlet`, `--need power inlet`); NM diagnosis RC-1 (the aliases named, E); `DIARY.md:218-223`
  ("worked around rather than fixed") · supports only: these records on this store.

**The walk, in order, by finding.** before the first command: 18, 19 · drawer: 6 (and 2 when the drawer is empty) ·
idea → needs: 5, 20, 4 · match → pick: 3, 4, 12, 2, 7 · requirements → build: 11, 10 · init → checks: 8, 9, 15 ·
firmware → bench: 1, 14(g) · tally: 16 · the documents under it all: 17 · the harms met by nobody yet: 14 · on the
own-board route: 12, 13.

**Where a person stalls alone, guesses, or is harmed (the question asked).** Stalls they cannot pass from the pages:
1 (no flash step), 3 (the hold, for the PO), 12 (an owned board with no file). Guesses: 5 (quote or not), 4 (what
`[other words]` means; which pick is "similar enough"), 8 (which page's order), 15 (whether an entry may be deleted).
Harms with no sign: 2 (the wrong store), 13 (a netlist every check reads with merged pads), 14(a) (a record "kept" where
an update discards it), 14(c) (a file overwritten), 14(d) (a document "kept" that was not), 14(g) (an image for another
chip), 9 (a number with no source on its line — right today, unreadable as right).

**What the terminal would have to print.** For each stall, one sentence the person could act on, in the shape the
refusals already use (where · why · the next command): see §2's "Missing" and the message lines quoted under each
change. The pattern that recurs: spark already knows the fix (it is in the JSON `fix` or `next`), knows the store it
read (`store.home()`), knows the source of the number (the record's `source`), and knows which word missed (the
haystack) — and prints none of them to the person.

## 2. The proposed changes, judged from this lens

For each change in the six diagnoses, by its title: keep · change (how) · drop (why) — judged on what it does for the
person at the keyboard, against the PO's three criteria. The verifiers' corrections are taken as read where they
change the shape (they are named). Sizes are the diagnoses' estimates (H, theirs).

### store-levels-and-holds

- **C1 · A `SPARK_HOME` that names nothing is refused, and every answer names its store** — keep, and add the
  verifier's M1 (an empty value is refused too) and a third sentence for the human case: when the drawer holds 0
  entries, every `--pick`/`--match` answer carries one line, `your drawer is empty (store <path>) — /spark:drawer puts
  what you own in it`, so USER-HUMAN-2's two identical answers become two. The `in store <path>` line on every write is
  the one thing that lets a person later answer "where did that go?". Message as proposed names where and why; good for
  both readers.
- **C2 · The real store is written only on purpose (P164)** — keep as the PO's decision (#101 names both mechanisms).
  From this lens the temp-folder rule costs a hobbyist nothing; `SPARK_STORE=real` costs them a flag they must learn
  before their first real pick, and a refusal they will meet first: write that refusal as `this command would write
  your store at <path>; say so with SPARK_STORE=real, or point SPARK_HOME at a scratch store` — never a bare "refused".
- **C3 · One lock beside the data; a writer with no lock refuses** — keep; invisible to the person when it works, and
  the failure it prevents (K5–K7) has no sign today. The verifier's costs (33 direct writes in the suite; the home must
  exist before `.lock`) are the implementer's.
- **C4 · An operation's writes land all or none, and a stop says what landed** — change to the verifier's smaller
  form: keep the ordered sequence, and on a stop print `written before the stop: …; the rest was not; the same command,
  retried, finishes it`. For the person that sentence is the whole value; the all-or-none primitive (L) buys them
  nothing they can see and costs the history its append-only wall.
- **C5 · A project is its folder, not its spelling** — keep the spelling half (S); hold the "never reuse a name" half
  until the id lands (the verifier: a moved folder — the commonest thing a hobbyist does — would otherwise lose its
  holds and get `proj-2`).
- **C6 · Holds are seen in the listing and released by an operation** — keep; it is the stall the PO meets. Two
  conditions from this lens: (a) decide the verifier's M2 first (derive holds from each project's `needs.json` on read,
  or keep them stored and add `--release`) — under (i) the person is never told to free anything, the bin's pick simply
  is the hold; (b) the command must be printed in the **plain** refusal, which means fixing K56 with it (below), or the
  person still sees `1 owned, held by smartbin-local — 1 picked here` and nothing more. The key column in `--drawer` is
  right; a `held by …` note beside it is what USER-3 grepped the store for.
- **C7 · Reads refuse what writes refuse: keys, and labels in one form** — keep; the conflict-copy sentence (`… is not a
  drawer entry: its name is not a plain key (a sync client's conflict copy?) — compare it with <file> and delete one`)
  is exactly what a person with Dropbox sees and can act on. The NFC half has no occurrence on the PO's store today (SL
  verifier RC-1 (4)) — rank it by mechanism, not by K10's clause.
- **C8 · One reader for a store file; no store problem is a traceback** — keep, with the verifier's caution: catch
  `UnicodeDecodeError` and `StoreProblem` by name, not every `ValueError` (a traceback is *where*, for the agent). For a
  person `<path> is not UTF-8 at byte 67 (0xE9) — re-save it as UTF-8` is readable; a traceback is not.
- **C9 · `--fetch` names every URL it could not keep, and says problems** — keep; "kept, checked" is the document
  store's whole promise to the person.
- **C10 · One layer, one count** — keep; S; two true counts that look like one wrong one are a trust cost.
- **C11 · A record has one home that is the store: promote to the shelf, shelve the project's own** — keep the
  direction (K12 is a silent loss told as a keep), slow the shelving half as the verifier says: today it would put four
  placeholder-footprint records on the PO's shelf where every project's `--list` offers them. "Proven in one project"
  needs the `built` line's definition (M3) first. The `--promote` dry run should say `to the plugin's own library, which
  the next update replaces` until the branch goes.
- **C12 · The spec and the code say the same about privacy** — keep as a chore; no person meets it on one Mac. Take the
  verifier's correction: do not shrink §5.1 — `sources` are document bytes the spec promises twice not to publish.
- **C13 · The `built` line vouches for what the chain reads** — drop the digest half until a reader exists (verifier
  M3: nothing compares a digest; `--tally`'s `built: true` says "proven" for a design whose pin order may have changed);
  keep the half where `note_built` returns a sentence and `check_spine` prints `the build was not recorded in your
  history: … — /spark:init or parts.py --step puts it there`.
- **The existing-mechanism option (the PO's relayed question, 2026-10-10)** — from this lens the criterion is: can the
  person see and repair the state with what they have (a file browser, a text editor)? Per-entry JSON files plus C7's
  named conflict copies plus C1's store line pass it; one SQLite file for the drawer shows up in a sync client as one
  binary conflict a person cannot open (H, mine; the SL verifier's note that synced folders are where file locking is
  weakest points the same way); git as transport gives diffs a person can read and a merge many hobbyists have never
  done (H, mine). The four invariants the SL diagnosis names (identity, lock, unit of work, one reader) are what a
  person needs whatever the backing; I add only the readability criterion for the P178 council.

### board-records

- **C1 · A `header_order` label tscircuit would read as a pin number is refused** — keep; the refusal as drafted
  (`… is "17": a bare number, which tscircuit reads as pin position 17 — the pad at position 17 is "3V3" … Print the
  silkscreen word`) is the best-diagnosed sentence in the whole set: where, why, the fix. Add the verifier's M6 (keys
  too) and both regexes.
- **C2 · `pad_aliases` reaches the footprint** — keep, with the verifier's rule (an alias target that is also a key must
  map to the same GPIO; the drafted rule refuses the S3's own `SS → A4`). For the person the one change that matters
  more is the verifier's **M1**: `check_spine` prints tscircuit's own `Could not find port for selector ".Mcu > .MISO"`
  beside — or before — the island line. It is a reorder of two `return`s, it names the pad by its selector, and it would
  have turned round 0's "unrelated open terminal" into the cause in one line. Do M1 first, then judge whether C2's
  reconstructed hint is still needed.
- **C3 · The `physical` schema is written where it is enforced, and a key nobody reads is refused** — keep; the
  own-board person learns the schema from refusals today (G0.2, G0.5, G0.10). Take M3 (five unread keys, not three) and
  the bin's `make check` dependency on the library file (change the file in the same commit). Mounting holes: the
  person ordering a board needs them; a decision, not this lens's.
- **C4 · `emit_footprint.py --json` prints JSON on every path** — keep the simpler variant (`--json needs --out`); S.
- **C5 · The footprint's header says what the drawing states** — keep; a `?` in a generated file is a trust cost.
- **C6 · One comment-key rule for every walker** — keep; the `//jtag` refusal told round 0 its note was a role.
- **C7 · The vendor-header cache lives in the store, and the check says where it wrote** — keep; `cached at <path>` is
  the sentence (G0.7 was found by `git status`, which a hobbyist never runs on the plugin). Say which door the write
  takes (the verifier).
- **C8 · A board record from a drawer entry: the skeleton spark can fill, the fields it must ask for** — keep as the
  PO's own first fix (D8). For the person it turns "a five-step page and a vector PDF" into one command plus a list of
  owed fields each naming the document to read it from — the diagnosable form the PO asked for. Two cautions carried: the
  per-chip table is a third copy of chip facts (test it against both shipped boards), and not writing `reused` at a
  board pick with no file changes a by-design behaviour (the PO's call).
- **C9 · A board says every stop it stops at, from one rule; `--for-fab` requires geometry** — keep; the person reads
  "stops at the footprint stage" and is stopped a stage earlier by the LED's resistor today. Change both spellings of the
  sentence (verifier M5), and take the verifier's point that filling the XIAO's `physical.header` would draw through-holes
  for a castellated module — the `footprint_source` route is the proposal, not a footnote.
- **C10 · A board's `function` is a documented, validated key** — keep; USER-4's "nothing in the store does this — a
  gap" for WiFi on an ESP32 is the sentence a hobbyist least believes. Take M4: the drawer entry already has the slot;
  the record is where a fact about every board of the SKU belongs, with its source.
- **C11 · `pins` are checked against the stand-in's pin list** — change, per the FB verifier: for both library boards
  the "absent" pins are **names** (`TX`/`RX`, `SDA`/`SCL`), 0 GPIOs absent; the fix is the emitter's name choice and a
  documented, validated override (`wokwi_power_pins` already carries renames and `null`), not a "spend last" role that
  would be false for the library boards. Keep the `--validate`-time sentence for a user's generic devkit (round 0's case).
- **C12 · Remove `footprint_module`** — keep; a removal, and the XIAO's value names a footprint nobody has.
- **On the PO's question** — the stand-in's pins are already in a library spark ships (`@wokwi/diagram-lint`'s registry,
  137 parts, E the two verifiers); the SKU → variant bridge is `boards.txt` in the Arduino core (E the BR diagnostician's
  fetch, 11 DFRobot variants). Nothing here needs a sync library.

### needs-matching-vocabulary

- **C1 · One matcher: `--need` reads `function.what` and the drawer, matches by words hit, and says which words
  missed** — keep, with the verifier's two conditions (tokens, not substrings — M5; and a definition of what "a match is
  the answer" means when ranked by hits) and one from this lens: tokenise the **arguments** so `"soil sensor"` and `soil
  sensor` are one search (USER-HUMAN-5), and print what was searched: `searched soil, sensor in id, name, kind and
  aliases of 31 records (library 8, shelf 5, catalog 18); the drawer's 110 entries are not searched`. The empty answer
  as drafted (`nothing holds any of: … — the store's words near this verb: …`) is the sentence that keeps a person from
  being sent to research what they own. The verifier's cheaper alternative (keep the AND, add the two sentences) still
  misses the quoting case.
- **C2 · The pick says what the match knew, and the needs listing shows the pick** — keep the note at pick time, and
  make it carry the verb first (`temp: l9110s-module does drive, not sense`, verifier M1) — USER-HUMAN-4 is the silent
  write of a wrong intent. **Drop the mark/pick pair rule** (the verifier: it refuses plant-alarm's real file on read and
  the documented gap → research → pick path). `--needs` showing `pick` and `mark` on its line is trivial and right.
- **C3 · A need can be dropped, and a pick cleared, through the same set-only door** — keep; "fixed by hand in
  needs.json" is the one hand edit the pages prescribe. Say in the answer that history lines keep the old id (verifier).
- **C4 · Every answer that runs over the drawer says how many entries it could not look at** — keep, and it is
  incomplete without the verifier's M8: a `drawer.md` step after the import where the agent proposes `function` from the
  label and the person says yes. The count (`91 of 110 drawer entries say nothing of what they do, so no need reaches
  them`) is what turns USER-HUMAN-6 from invisible into one line.
- **C5 · The research skeleton carries every chain fact, and research ends with `--audit`** — keep; correct the
  diagnosability line as the verifier says (`--validate` accepts `function: null` and `simulation: null`; only `--audit`
  names them) so the next reader does not trust `--validate` again.
- **C6 · The cut lists its words and ids** — keep; cap the ids per word (verifier).
- **C7 · A need says how many the design uses** — a PO decision; from this lens the verifier's M7 (one need per
  instance already yields `Valve1…Valve4` and four reservations; one sentence in `idea.md`) is the remove-before-add
  path, and the `given twice, taken once` line costs one sentence either way.
- **C8 · `--requirements` refuses when a differently named requirements file sits in the project** — keep after the
  verifier's M6 (one `git mv` in irrigation ends it there); the refusal names the file and the fix.
- **C9 · The store's words are shown where a need is written and matched** — keep; cheap; add the verifier's M2 case
  ("your need says 'distance sensor'; the store's word is 'distance' — one word more"), the commonest cause of
  `[other words]` on the copy.
- **Missing here (nobody proposed):** a one-line legend under a `--match` answer that contains the marks: `[other
  words] = the same verb, not your words — your call; (drawer) = owned, no record — reserved, not placed; owes = a fact the
  build needs`. Today the marks are undefined on the page where a person reads them (`parts.py:1963`).

### chain-and-checks

- **C1 · The chain re-seeds the derived half of `rules.json` (C1a) / the derived half leaves the file (C1b)** — change
  to the verifier's MC-6: seed at `parts.py --requirements`, which is already a writer and already holds the picks and
  records, so the derivation happens where the person is and no check becomes a writer; the "after a build, run init
  again with `--force`" step leaves three pages. From this lens USER-HUMAN-8 then has one order. Carry MC-1 (an empty
  rule list has two meanings held by two tools on purpose) as the decision C1b cannot avoid.
- **C2 · A signal the file declares is reported, not refused** — keep; "the chain is broken" for life on a declared
  signal is the clearest case of a verdict nobody reads. Share the `note:` prefix as a constant (verifier).
- **C3 · A record can say that an input defines its own level** — keep the vocabulary, widen it as the verifier says
  (MC-5: module-side pull-ups and gated data inputs — spark's own amplifier record), and pair it with MC-2 so the rules
  file's `//` note never claims a person's entries were derived.
- **C4 · One table says what each owed fact does to the chain, and every mouth reads it** — keep; it is the fix for
  USER-HUMAN-11, and its named test (`check_spine.run` per missing fact, assert the stopping stage) caught the
  diagnosis's own wrong row. Decide MC-3 first (`pin_order_proof`: owed or a contract failure).
- **C5 · The requirements writer reads the file through `design.read` and names instances with the one function** —
  keep; S; three silent writes become three refusals where the person is. Fold `_name_after` (verifier).
- **C6 · The board changes in one place** — keep the recommended variant now; the person's `boards.py --id` then agrees
  with their requirements file.
- **C7 · Five small contract fixes** — keep all five; for K63 take the refuse variant and reorder `idea.md:13-15`
  (verifier) so the store never lists a folder that is not there; for K52 also return could-not-run (MC-8).
- **C8 · `--keep` builds the kept `board.tsx` and says how it differs** — keep (D the PO, 2026-10-05), built in place
  (verifier MC-4: a hand-edited file's imports are not in the work folder). Say to the PO that irrigation records no
  `built` until its board is regenerated.
- **C9 · ★C7 — keep; one wording option** — keep; the note in every outcome.

### firmware-and-bench

- **C1 · The stand-in's pins are a board fact the chain reads first** — change, per the verifier: fix the emitter's
  name choice (`mapping.ts`), give the override a documented name and a validator, and make the converter's own sentence
  carry the remedy (`the stand-in <part> has no pin for GPIO<n> (pad <label>); move <signal> or prove it on the bench`);
  the `check_spine` classification of that sentence as could-not-run (not "a defect in the design") is the half a person
  reads. Amend, do not delete, the S3 note and the README sentence (M9).
- **C2 · `flash_image.py` refuses an interpreter built for another chip** — keep, in the verifier's simpler form (the
  16-byte read called from `check_spine`'s simulation stage where the board and `--firmware` already meet; `--chip` for
  the standalone case). The sentence (`<file> is a MicroPython build for chip id 13 (esp32c6) but <board> is an esp32s3
  (chip id 9) — refused, nothing written`) is the one a hobbyist with a C6 needs before the bench.
- **C3 · The step from the image to the board: two tools and the commands spark composes** — keep as the change that
  ends USER-HUMAN-1; the PO chooses the script or the page. From this lens even the page variant (S) changes the
  journey's end from "nothing" to "two commands and the first line the board prints"; the script adds the chip check and
  three could-not-run sentences. Carry M5 (esptool 3.3 on the PO's machine cannot flash a C6; a minimum version).
- **C4 · A sixth check: the firmware against the pin map it imports** — keep as a story, named as what it is (a
  use-against-map check, not the triangle; the check was cut on 2026-09-29 by the PO and the convention changed since —
  verifier M2/M3). For the person it is the first time anything says `BTNMODE_BUTTON = GPIO18: in pins.py and never
  constructed as a Pin`. Fix `tools/mutate.py`'s over-count (K53) before leaning on its table.
- **C5 · A scenario is measured against the pin map before it spends a minute** — keep as a note (`asserts 1 of 12
  pin-map constants … a pass proves those pins nothing`); the person pays the Wokwi minute.
- **C6 · The documents follow the code** — keep; the verifier's correction stands (spark has no retired-phrase check;
  the bin does — propose one, S).
- **Missing here (the verifier's M7, which this lens seconds):** the record's deep-sleep facts (`wake_api`, "one level for
  all pins", the C6's missing `wake_on_ext0`, `simulated_by_wokwi false`) written into `pins.py`'s header beside the pins
  — a few lines inside the 2026-10-01 boundary, and the first time a person writing firmware sees them without opening
  the board file.

### docs-and-recorded-outputs

- **Change 1 · The gate counts, and names, every recorded output behind the shipped version** — keep as a report line,
  not a failing check (the verifier: a version is provenance, a diff is currency; 44 false alarms on a patch).
- **Change 2 · The README's typed block ends where a shell can finish it, and the gate runs it** — keep; a stranger's
  first typed block exits 0 at every line. Take the verifier's M8 (give the block a recorded output, and show the tally's
  honest exit 2 as a recorded block beside the sentence that explains it, so the refusal is shown, not only told).
- **Change 3 · Recorded outputs are re-recorded by one tool at each release** — keep the direction; promote or delete
  the recorder that exists untracked (verifier M1) before writing a third; classify the 42 blocks (M2/M3); and the
  "release gate" it names does not exist (M4) — it runs in `check_commit.py` on a version change, or it is prose again.
- **Change 4 · The own-board route is recorded on 0.8.1, and the three facts the scripts hold are written where the
  steps are** — keep; the variant-folder listing and `--keep`/`--kept` for a board's documents are what round 0 guessed
  and re-fetched. Cut the half already on the page (`how-it-works.md:172`).
- **Change 5 · The gate reads the pages agents follow** — keep; S; with M7 (name a page by its path, or three
  `SKILL.md`s are one name).
- **Change 6 · Density and long lines: one measured rule, or none** — the PO's call; from this lens README's long lines
  are table rows (verifier) and the real cost is 231 lines where the design said about 120 — a pointer to the journey,
  not a retelling, is the simpler README.
- **Change 7 · One sentence says what spark has built** — keep; add the per-store fact (the library holds 8 records;
  `parts.py --list` adds what the person's store holds — 13 on the PO's copy).

### Missing — changes nobody proposed, from the person at the terminal

- **M-a · Text mode prints `next` and `fix` always.** `_say` prints `answer.lines`, and `fix` only when there are no
  lines; `answer.next` is never printed as text (`parts.py:2173-2185`). One change: after the lines, print each problem's
  `fix` and each `next` step's `op` + `argv` + `why` as indented lines. Testable (a text-mode test asserting the fix line
  for the held-board refusal); diagnosable by construction; removes nothing. It is the cheapest change in this report
  and the one every refusal in USER-HUMAN-3/4/5/11 passes through.
- **M-b · An empty drawer is said on every answer that ran over it**, and every write names its store (C1's line): the
  two sentences that make USER-HUMAN-2's identical answers different.
- **M-c · Every number a check prints carries its provenance.** `? V33: draws 355 mA of 1.50 A` becomes `? V33: draws
  355 mA (the module's radio TX peak, module_peak_a, datasheet-typ, Table 11) of 1.50 A (regulator_3v3_a, unverified)`.
  The provenance words exist in the records (`verified`, `source`; the tech lead's five words: stated, datasheet-typ,
  datasheet-max, calculated, measured); the check reads the record and drops them. Testable (the line carries the
  key and the word); S.
- **M-d · `--need` tokenises its arguments and prints what it searched** (under NM-C1 above): quoted or not, the same
  answer; and `the drawer is not searched` said once, until C1 searches it.
- **M-e · A legend line under `--match`** (under NM above).
- **M-f · One documented order for `init`** — or none, by MC-6: the pages `README.md:155`, `commands/idea.md:126` and
  `commands/init.md:36` disagree today; a person following one gets a different `check_all` than one following another
  (USER-HUMAN-8).
- **M-g · A start line for the terminal persona.** `parts.py` with no arguments prints the five commands in the order
  the README types them (`--needs-set`, `--match`, `--pick`, `--requirements`, then `check_spine.py`), not argparse's
  28-flag usage; or `README.md:182-188` stops promising the terminal persona and says "the scripts are for agents and for
  checking what an agent did". Either is honest; today the page promises and the usage line does not deliver.
- **M-h · `parts.py --store`** (#101's own suggestion): `store ~/.local/share/spark — drawer 110 entries, shelf 5,
  catalog 18, projects 5` — the one line that answers "which store am I in, and is it the one with my parts?" before
  anything is written.
- **M-i · `check_spine` stops printing the work folder's path** (`wrote <scratch>/tmp/spark-spine-…/FireBeetle2Esp32S3.tsx
  (32 pads, 1.00 mm holes)` before `wrote FireBeetle2Esp32S3.tsx`): polish; the journey redacts it as `<temp>`, the
  terminal shows a folder that is deleted a second later.

### The ten that matter most, in this lens's order

1. **FB-C3 — the step from the image to the board** (even as the page). Reason: the job is "firmware that runs" and
   every round, every persona and the README's own flowchart end at a step that does not exist; nothing above the bench
   is worth more than the bench being reachable. The PO owns P79's shape; the smallest piece under it is this.
2. **SL-C6 + the K56 fix (M-a) — holds listed, released by a command, and the plain refusal carries the command.**
   Reason: the PO meets it on every second project today, the fix is already computed and withheld from the terminal,
   and the way out today is a hand-written JSON file against a key the listing never prints. M2 (derive vs stored) first.
3. **M-a — text mode prints `next` and `fix`.** Reason: one function, every refusal; it is the single change under
   which USER-HUMAN-3, 4, 5 and 11 all get their next command for free. S.
4. **NM-C1 + M-d + NM-C9 — one matcher over tokens that says what it searched and which word missed, and shows the
   store's words.** Reason: the first thing a person types after their needs is `--need`, the answer today depends on
   their quoting, and the wrong answer sends them to research what they own (I1 open since 2026-09-29).
5. **NM-C2 (without the pair rule) — the pick says what the match knew, verb first.** Reason: a wrong intent is written
   with exit 0 and "1 reused"; nothing downstream can tell; the person who made the pick is the only one who knows.
6. **SL-C1 + M1 + M-b — a missing or empty `SPARK_HOME` is refused; every answer names its store; an empty drawer is
   said.** Reason: the harm is silent and the real store is one unset variable away; the person cannot tell "I own
   nothing" from "wrong store" today. S.
7. **BR-C8 — a board record from a drawer entry.** Reason: four of the PO's six boards cannot be built with, the route
   today is a five-step page round 0 ran with ten gaps, and the PO named it the first fix (D8). L, so seventh.
8. **CC-C4 + MC-3 — one table of what each owed fact does, read by every mouth.** Reason: "builds with it", "owes" and a
   refusal are three answers to one question; the person reads the promise first. Decide `pin_order_proof` first.
9. **NM-C4 + M8 — the mute drawer counted, and a drawer.md step that asks what each imported thing does.** Reason: the
   owned-first promise fails invisibly for 91 of 110 entries; the count is one line, the step is the only path to zero.
10. **CC-C2 + CC-C8 (in place) — a declared signal is reported, not refused; `--keep` builds the kept file.** Reason:
    the one line a person reads at the end of a build is false by agreement on irrigation and about another board on any
    edited project; a verdict that is wrong on purpose stops being read.

Just below the ten, and cheap: **BR verifier M1** (print tscircuit's own selector error — the own-board route's cause in
one line, a reorder), **M-c** (provenance on every number a check prints — the PO's "a wrong number" criterion),
**DC-Change 2** (the README block exits 0 as typed), **CC-C1 as MC-6** (rules seeded where the person is; M-f falls out
of it), **BR-C1** (the bare-number label refused — the one short-class fault, on a route the PO's first fix makes common).

## 3. What I could not check, and why

- **A human.** n = 0 strangers; every account in the folder and this walk are agents'. Where a person stalls, quits
  or misreads (`[other words]`, "the chain runs end to end — but …", a hold's refusal) is H throughout.
- **The conversations** (`/spark:drawer`'s words to entries, `/spark:idea`'s questions and marks, `/spark:research`'s
  agents, the review): they need Claude Code and were not run; the terminal persona I walked is the README's
  "without Claude Code" one, which the design calls secondary (§6.4).
- **The install path, the DFRobot import, Wokwi, hardware**: not run (Claude Code's own command; Claude in Chrome;
  paid minutes, D4; nothing has touched hardware).
- **The real store**: never read by a command nor written, by rule; the copy is as of 2026-10-10; the empty store is
  mine.
- **Whether a hobbyist sets `SPARK_HOME` at all**: —. USER-HUMAN-2's missing-folder case is an agent's shape (#101);
  the empty-drawer half is every stranger's first hour.
- **The silent harms in USER-HUMAN-14**: taken from the diagnoses' reproductions and their verifiers' re-runs on
  copies; I did not re-run them (each writes to a store, and the copy already holds the P100 lenses' scratch state).
- **Sizes** (S/M/L) are the diagnoses' estimates, H.
- **The XIAO route and plant-alarm**: not walked (it stops at the footprint stage by the docs; the FB verifier shows
  its stand-in pins are a naming case, not a limit).
- **Whether the terminal persona is wanted at all**: the user lens's Q11 (typing commands, or directing Claude) was
  asked on 2026-10-09 and is unanswered; several of §2's "missing" items are void if the answer is "only Claude".

## 4. Questions for the decider

| question | what it decides |
| --- | --- |
| Is a person typing spark's scripts without Claude Code a persona spark serves, or only a way to check what an agent did? | whether text mode gets `next`, `fix`, a legend and a start line (M-a, M-e, M-g), or `README.md:182-188` stops promising it |
| A hold: derived from each listed project's `needs.json` when a pick is made, or a stored decision released by `--release`? | SL-C6's shape (SL verifier M2); under "derived" nobody is ever told to free anything, under "stored" the bin keeps its S3 by saying so |
| The step to the board: a script that composes `esptool`/`mpremote` from the record and refuses a wrong chip, or a page with two commands? | FB-C3's size, and whether USER-HUMAN-14(g) can be refused before the bench |
| The real store's guard: the temp-folder rule, `SPARK_STORE=real`, or both? | C2; the cost to the PO is one flag learnt once, the cost to an agent's slip is a refusal naming the rule |
| One documented order for `init`, or the derived rules seeded at `--requirements` so the order stops mattering? | USER-HUMAN-8; CC-C1 as MC-6; three pages |
| `pin_order_proof` absent: an owed fact (buildable, warned, marked — #102) or a contract failure (as `validate` says since P81)? | CC-C4's table and `--requirements`' policy (MC-3) |
| Must every number a check prints carry its provenance word and its record key? | M-c; the PO's own criterion read against the 355 mA line |
| A need the board itself serves (WiFi, the LiPo socket): marked served by the board pick, or picked as a need? | BR-C10's open half; USER-4/6 |
| Who runs the first walk by a person without Claude Code, on a fresh store, and who scores it? | whether anything in this report moves from H to E; ★C9 |
| The README's typed block: a heredoc into the project with no tally (DC Change 2), or the whole `/spark:idea` with its honest exit 2 shown as a recorded block (the verifier's M8)? | what a stranger sees first: a block that exits 0, or one that shows the refusal they will meet in a shell |

## 5. Searches

none — every claim rests on the files named in the header, the cards read with `gh issue view` (read-only), the
diagnoses' and verifiers' runs as cited, and my own runs on a copy of the store and on an empty one (2026-10-10):

```text
SPARK_HOME=<scratch>/store HOME=<scratch>/home TMPDIR=<scratch>/tmp env | grep SPARK_HOME      → the scratch path
1  parts.py --help
2  parts.py --drawer                                                                           → labels, counts, is; no key, no used_in, no function
3  parts.py --need soil sensor ; --need temperature ; --need "soil sensor" ; --need 12 V inlet ; --need "12 V inlet" ; --need "power inlet"
4  parts.py --needs-set <proj> needs.json (temp, board, report, batt) ; --match <proj>
5  parts.py --pick <proj> board=firebeetle2-esp32s3 batt=1s-lipo-battery-1000-mah --dry-run ; the same --json
6  SPARK_HOME=<scratch>/store-missing … parts.py --pick <proj> board=firebeetle2-esp32s3 --dry-run ; ls store-missing
7  SPARK_HOME= HOME=<scratch>/home python3 -c 'import store; print(store.home())'
8  parts.py --pick <proj> temp=l9110s-module --dry-run
first hour (empty store, bash, tsci 0.0.2621 on PATH, CLAUDE_PLUGIN_ROOT=~/Development/spark):
   --needs-set . button-needs.json ; --match . ; --pick . press=tactile-button light=led-red-5mm board=firebeetle2-esp32s3 ;
   --requirements . ; check_spine.py requirements.json --keep . ; --tally . ;
   init_project.py --project . --board firebeetle2-esp32s3 ; check_all.py --project . ; init … --force ; check_all … ;
   assign_pins.py requirements.json --emit-pins firmware/pins.py
```
