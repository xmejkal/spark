# The refuter's report on P867 (the whole journey redefined), first pass

Read and run on 2026-11-17 (Europe/Prague) on the branch as it stood, by the refuter (Fable 5.2). Nothing but this file
was written. The scratch folder under $TMPDIR was removed after the runs. "Run" means I ran the command and read its
output. "Lens line" means I read only the council report's line, not its primary source.

## Checked first: does the change address the observed problem, and what breaks for current users

- R-0a · The observed problem in the rows is the behaviour of commands, and the brief's first slice is a status word.
  The 32 rows (16 + 7 + 9, counted in the three rows files) hold no row that says a tick was shown on a phase that
  was out of date. The three rows about `flow.py` are 9, 10 and 11 of walk 3 (a wrong sentence, `${CLAUDE_PLUGIN_ROOT}`,
  the idea line). ★C1 was found by the facilitator's run, not by a walk. What the walks saw of a change is hand work:
  row 13 ("The person must delete it by hand"), row 12 (a blocker, P868 #1235) and the comment's "A person removes them
  by hand". The risks lens says so in a sentence the brief dropped: council/risks.md:21 (RI-10), "Each is a behaviour
  of a script, so redefining the journey on paper does not remove them; they need cards (#1236 can hold them)". None of the six proposed
  items (items.md) fixes row 13 or the "kept, not from a pick" entries.
- R-0b · The proof project is not a change in the middle. In spark-walks/p711-sound-demo the picks are amp, speaker
  terminal and a rotary encoder (`.spark/needs.json`: `"what": "rotary encoder", "pick": [{"part":
  "cjmcu-111-rotary-encoder"}]`), and requirements.json holds `dfr0664-tft-2in`, `max98357a-dfr0954`,
  `joystick-module-mh`, `speaker-terminal`. Row 12 says why: "The way around: repeat the box's whole design (p581's
  requirements), so the assigner places the bus on the same pins." So the "↻ requirements" there is the mark of a
  hand-written file that works around P868. The build, the sheet and the firmware were made from that file and are the
  newest things in the folder. Slice 0's proof (story-map.md, "the build and the breadboard read 'out of date, because
  requirements.json changed'") would mark them out of date, with a cause that is false by the brief's own caveat on
  ★C1 ("that file did not change here: the picks did"), and its offer (`requirements`) leads back to the design that
  P868 refuses.
- R-0c · What breaks for current users. (1) `stands_at` and the status of the build and breadboard phases change
  meaning for every project whose requirements.json a person wrote or edited; `--requirements` keeps such entries on
  purpose (council/feasibility.md:38, "a design choice (the file may hold a person's own entries), not a bug"). The
  Frame lists the keys of the JSON as "must not get worse", and not the meaning of their values. (2) OQ4 (a) reverses
  P280's rule; the brief says so. It also meets P816 #1168, whose Done-when is "an earlier `dist/` is removed and
  said ..., or kept and named". (3) Under OQ8 (a) P829 #1187 leaves Ready's flow, and P820's A11 waits on P829 (the
  Frame's item line), so this discovery would hold P820's own open assumption.

## 1. The ★ claims, each against its source

| claim | the line I read, verbatim | verdict |
| --- | --- | --- |
| ★C1 | Run: `↻ requirements: out of date, requirements.json differs from what the picks give (claude)`, then `✓ build: the last build, 2026-11-17T07:59:38+01:00: ok (claude)`, `✓ breadboard: breadboard.md (you)`. Code, scripts/spark/flow/phase_readers.py: `if (record and why_build_stale(project, record)) or read_built_from(project) != read_requirements(project):` | partly |
| ★C2 | phase_readers.py, DeployReader: `return self.phase(flow_codes.NOT_STARTED, [flow_codes.LOOK_FIRST_MESSAGE, flow_codes.DEPLOY_COMMAND])`; FirmwareReader: `return self.phase(None, [flow_codes.FIRMWARE_MESSAGE % stamp(...)])` | holds |
| ★C3 | council/architecture.md:27: "Every dependency and every "out of date" rule is code inside one reader, and each uses its own mechanism. There are four mechanisms for the same question" (its table has seven edges). Code read for three: `if given.content != held:`, `sha256_of(path) != record.get("requirements_sha256")`, `read_built_from(project) != read_requirements(project)` | partly: the file-time mechanism (project_image.py) could not open in the time |
| ★C4 | Run: base, 15 signals, equal to firmware/pins.py on 15 of 15. With JoyTwo: `'AUDIO_SHUTDOWN': ((6, 'A2'), (8, 'A3')), 'JOY_SW': ((7, 'D5'), (47, 'D14'))`, new `'JOYTWO_JOY_X': (6, 'A2')` | holds, and its caveat is now too narrow (below) |
| ★C5 | scripts/spark/design/loader.py:382: `raise DesignError("signals[%d] pins %s, an %s bus line: the assigner places the bus, so drop \`pin\`"`; scripts/import_firmware.py:3: "Import a project's firmware on the Mac, without running main.py (P59, #7)." | partly |
| ★C6 | spark-walks/p711-sound-demo/firmware/main.py:21: `shutdown = Pin(pins.AUDIO_SHUTDOWN, Pin.OUT, value=1)`; my run puts JOYTWO_JOY_X on GPIO6 | holds for the state; the harm stays not measured |
| ★C7 | scripts/spark/build/kept_files.py:303-306: `if path.exists():` / `path.unlink()` / `"did": "removed", "why": why + ", and it described an earlier build"`; :324-325: `if ours:` / `target.unlink()` | holds; its caveat is partly |
| ★C8 | kept_files.py:316-317: `ours = target.is_file() and target.read_bytes().startswith(pin_assigner.PIN_MODULE_HEADER.encode())`; rows.md row 13: "traces differ: board.tsx" for the board.tsx that spark itself wrote for the earlier design, never edited." | partly: need_requirements.py:129-161 could not open in the time |
| ★C9 | rows.md row 16: "The record of a built gadget drifted from the gadget, and nothing in spark notices."; p711-walk4-button-led/rows.md row 6: "The skill says so, but a person reads it as the box's state."; scripts/spark/core/outcomes.py: `RECORDED, NONE_RECORDED, NOT_CHECKED = "recorded", "none-recorded", "not-checked"` | partly: the two records' readers could not open in the time; a wiring-record.json is in the walk folder |
| ★C10 | Run: `✓ build: the last build, 2026-11-16T18:55:21+01:00: ok, parts: skipped, schematic: skipped, footprint: skipped, build: skipped (claude)`; scripts/spark/flow/show_flow.py: `stands_at = next((phase.phase for phase in phases if phase.status not in (OK, None)), None)` | holds |
| ★C11 | scripts/spark/flow/flow_codes.py:9: `PHASES = ("idea", "needs", "parts", "requirements", "build", "breadboard", "firmware", "simulate", "deploy")`; council/architecture.md:11: "at least five places"; council/risks.md:12: "already a third definition" | partly: the lenses count five and three; the other vocabularies could not open in the time |
| ★C12 | My count over parts/*.json: 8 files, `sku` 1, `vendor` 1, `sourcing` 0. council/feasibility.md:30: "The brief can hold `sellers`/`prefer` (a list of shops, local first)"; :33 (FE-15): "The PCB as its own phase: the data exists in part." | partly |
| ★C13 | Run, `flow.py show --json`: an offer is `{"key":"needs-drop:board","effect":"drops need board from needs.json and frees its holds"}`; the answer's keys are `data, envelope, next, op, problems, status, tool, truncated, unchecked`, and `next = []` | partly |
| ★C14 | council/architecture.md:107, :138, :211 (AR-12, AR-13, AR-14), each "H this lens"; :262-263: "supports only: a comparison of shapes, not a choice." | holds as proposals; a caveat is dropped |
| ★C15 | #1187: "`RunRequest`, commands/page.md (`/spark:page`), `.spark/page.json`"; mvp-plan.md:60: "revision: the sha256 of needs.json, requirements.json and .spark/build.json together."; council/architecture.md (AR-20): "both parts are small and would be folded into the definition later (a rename and a move ...)"; council/risks.md:11: "Order of risk: P827 high, P828 medium, P829 low" | partly |
| ★C16 | council/risks.md:10: "The one person blocked is the PO at the bench, who has no page that says where the project stands (page-notes.md gap 9)."; #1236: "No, actually, let's start over with a new walk when  we fix the gaps and bugs from these runs"; rows 2 and 12 of walk 3 have the kind "blocker" | refuted as worded |
| ★C17 | mvp-plan.md:186-187: "D10, Q15 and Q16: "store options" means his drawer and spark's records; ... shops with prices come after the MVP." | holds |
| ★C18 | rows.md row 10: "The simulate and deploy commands start with `${CLAUDE_PLUGIN_ROOT}`, which a person's own terminal does not set."; p711-walk4-button-led/diary.md:37: "07:01:44 CET, the PO in his own terminal (download mode first): deploy.py --no-simulation" | partly: "Claude typed every command" is a diary reading by one lens; I opened two diary lines, not the three diaries |
| ★C19 | Fetched: bazel.build/basics/hermeticity: "The output of an action can be cached, and the action need not be run again unless inputs change."; GOV.UK: "Always allow users to go back into a task to change their answer.", and "Cannot start yet" is described as "grey text with no background colour". Terraform, LangGraph and KiCad: could not open in the time | partly for Bazel and GOV.UK; could not open for the other three |

For each partly or refuted, the sentence to change and why:

- ★C1 · change "'Out of date' does not travel down the phases" to "'Out of date' travels one link only: a changed
  requirements.json marks the build and the sheet; a change of the needs or picks stops at the requirements phase".
  The code already carries it from the file to the build and from the build to the sheet, and council/existing.md:11
  says "one hop", which is narrower than the brief's headline. Add to the caveat that this folder's requirements.json
  was written by hand as P868's way around (row 12), so the case is not a change in the middle (R-0b).
- ★C3 · keep "four mechanisms", and add that the lens's table has seven edges and that two of the four (the stored
  copy of what the sheet told, and the deploy record) are witnesses of an output, not of an input: "one check" over
  recorded inputs does not replace them.
- ★C4 · replace the caveat "one project, one board, one added part; an added button moved none" with the runs of
  this pass (provenance simulated, the assigner's answer, one board model, FireBeetle 2 ESP32-S3):

  | project (kept signals) | added part | kept signals that moved |
  | --- | --- | --- |
  | p711-sound-demo (15) | joystick-module-mh as JoyTwo | 2 (AUDIO_SHUTDOWN, JOY_SW) |
  | p711-sound-demo (15) | vl6180x-breakout (I2C) | 6 (TFT_DC, I2S_BCLK, I2S_LRC, I2S_DIN, AUDIO_SHUTDOWN, JOY_SW) |
  | p711-sound-demo (15) | tactile-button, led-red-5mm, l9110s-module, a named second button | 0 each |
  | p711-identify-amp (4) | dfr0664-tft-2in (SPI display) | 4 of 4 (I2S_BCLK, I2S_LRC, I2S_DIN, AUDIO_SHUTDOWN) |
  | p711-identify-amp (4) | vl6180x-breakout (I2C) | 3 of 4 (I2S_LRC, I2S_DIN, AUDIO_SHUTDOWN) |
  | p711-identify-amp (4) | joystick-module-mh, a named second button | 0 each |
  | p711-walk4-button-led (0, board only) | any | nothing to move |

  The I2S bus lines move, and those are the lines whose pin the loader refuses to keep. The joystick case, the only
  one the brief ran, moves no bus line.
- ★C5 · change "Nothing compares the earlier pin map with the new one" to "No answer names a moved pin as moved; the
  sheet's 'Changes since the last build' compares the earlier wiring record with the new one" (row 6 of walk 3 quotes
  that section; council/physics.md:23 quotes "Move the <color> jumper from X: it now goes to Y"). The claim as written
  is stronger than the walk's own row.
- ★C7 · change the caveat "P816 #1168 holds the opposite rule for one case" to "after a build that did not finish,
  an earlier dist/ stays today, and P816 #1168 asks that it is removed or named". P816 is a bug card about the
  opposite behaviour, and one of its two fixes is removal.
- ★C11 · write the count once, with what was counted: the architecture lens says "at least five places", the risks
  lens three, the brief "at least four ... the PO's list is a fifth".
- ★C12 · add "the project's brief can hold a list of sellers (council/feasibility.md:30, not opened by the refuter)"
  and change "the schematic, the PCB and the facts to test have data today" to "the schematic and the facts to test
  have data; the PCB has it in part (FE-15)". The pointer "FE-10 to FE-14" does not cover the PCB.
- ★C13 · change "`flow.py show` answers no `next`" to "`flow.py show`'s envelope has the key `next`, and it is an
  empty list". The key is there; a reader who trusts the sentence would add a second one.
- ★C14 · add the lens's own limit: "a comparison of shapes, not a choice" (council/architecture.md:262-263), and its
  line 336-337: "The other two walks' rows ... and page-notes.md: not read (time)."
- ★C15 · change "P829 #1187 is exposed, because ..." to "the lenses split: the architecture lens says P829 would
  write a second definition, small to fold in later ('a rename and a move'); the risks lens ranks P827 high and P829
  low". The card #1187 itself names neither a kind table nor "revision"; both are in mvp-plan.md.
- ★C16 · change "Nobody is blocked by the missing definition" to "No card is blocked by the missing definition. The
  walks of P711 #960 are stopped on the PO's order until P869 #1236's fixes, and the PO at the bench has no page that
  says where the project stands (RI-2)". The source's own last sentence names a blocked person, and the brief cut it.
- ★C18 · tag "Claude typed every spark command" as "read by the lens in the diaries".
- ★C19 · add "neither the Bazel page nor the GOV.UK page says what happens to the things made from a changed thing"
  (both fetched: "not on the page"; council/existing.md:48 and :50 say the same). The claim lists these as "patterns
  that fit" a discovery whose question is exactly that.

## 2. The brief against the detail it summarises

Dropped caveats:

- D-1 · Frame, outcome. council/risks.md:35 (RI-19): the proof "passes on the files that already work and says nothing
  on firmware or the bench; a green result could be read as "the journey is redefined"". Its cheapest test, "write down, before running, which phases should be out of date ... (the pass line)", is not in the brief. The Frame tightened the proof for the firmware
  and the bench, and kept no guard against a rule that marks everything out of date: such a rule "names every phase
  that is out of date" too.
- D-2 · Frame, outcome. "no file is deleted or edited by hand" has no item behind it: row 13 (board.tsx) and the
  "kept, not from a pick" entries are in no item of items.md. The architecture lens names row 13 as the graph's
  "Smallest first slice" (council/architecture.md:203), and story-map.md's slice 0 is the other case (AR-4).
- D-3 · Options, OQ6 (2). "proves: 'did the kept pins move' and 'does the firmware name old pins' as facts read from
  files". A recorded input checksum gives neither. pins.py changes whenever a part is added (new lines), so the
  firmware reads out of date also when no kept pin moved: the same over-report the brief holds against option 1. The
  two facts need a comparison of two pin maps and a read of main.py's names (council/feasibility.md:43, "a text read
  ... (H, a spike: FE-27)"), which either shape can call.
- D-4 · Options, OQ6 (2), "three mechanisms folded into one check". The lens's table has two edges that are stored
  outputs and one that needs the board on USB ("readable only with the board on USB"). Stronger than its source.
- D-5 · Options, OQ5 (b). The caveat says "can be impossible"; it does not say for which lines, and it is the common
  case (section 3, I-3). "proves: a wired breadboard stays right after an added part" is stronger than its sources:
  ★C4 is simulated, and items.md's proof has an "or" ("moves no kept signal, or the answer names each one that
  moved") that today's assigner plus a printed difference passes.
- D-6 · Options, OQ9 (b). "proves: 'the board holds an older image than the project' is said without a look". Row 6
  of walk 2 is the counter-case in the folder: "spark-3d flashed the box many times since, outside spark's deploy".
  The witness can say what spark last deployed, never what the board holds.
- D-7 · Options, OQ1 (a) and Q6. council/feasibility.md:29 (FE-11): "simulation" names two things in code, and the
  PO's "simulation after the breadboard" needs "a word for each of the two before it is a question of order". No
  question in the queue asks it.
- D-8 · Risks, value row. "H: nobody is blocked" carries ★C16's cut sentence into the one row that rates value.
  council/risks.md:51 (RI-29) names the cost: "The discovery took weeks while P711 stayed stopped". Not in the brief.
- D-9 · Risks, A2. council/risks.md:29: "n = 1 and he is also the decider, so a 'yes' from him is not independent
  evidence." A2's cheapest test is "Q6 and Q9", which is that yes.
- D-10 · verification.md, Agree / split. Missing splits: P827 high and P829 low (risks) against P829 exposed
  (architecture); "at least five" against "third" definitions; the graph's first slice, row 13 (architecture) against
  AR-4's case (the synthesis).

Claims stronger than their source:

- S-1 · C25 (Found on the way): "The second joystick's switch lands on GPIO47". In the run it is the first
  joystick's switch, a kept signal, that moves there (`JOY_SW` 7 to 47); the second's lands on GPIO1, the pad printed
  SDA (`JOYTWO_JOY_SW: (1, 'SDA')`). council/physics.md:14 has it right. This matters for I-3: a new signal took the
  I2C data pin.
- S-2 · ★C7, ★C8, J2 and J3 cite "#1234's comment" as E. The comment's list ("What P711's walks saw") was written by
  the session, not by the PO, and four of its seven bullets (the needs-drop note, "kept, not from a pick", the
  firmware naming dropped pins, the board keeping old firmware) are in no row of the three rows files. Only row 12's
  card text (#1235) records the refused build's removal. They are an agent's account, one walk, with no row.
- S-3 · jobs-and-journeys.md, the journey's title: "after the board is wired and flashed". No walk added a part to a
  wired and flashed project of its own; row 16 says of the box "The joystick is not connected, only the rotary
  encoder". Steps 5 and 6 are simulated or read from code, as the table says; the title reads as an account.
- S-4 · story-map.md, slice 0 proof: "because requirements.json changed". It did not (R-0b).

## 3. The strongest rival explanation for each interpretation

- I-1 · "Out of date must travel down" (★C1, slice 0). Rival: the build is right to read ok, because it is a true
  build of the file it names, and the stale mark belongs to the picks, which are behind a file a person wrote. The
  folder cannot rule it out: its one case is that case.
- I-2 · "The definition should be a dependency graph" (OQ6, opinion 2). Rival: the graph answers what the
  architecture lens found interesting, and the PO asked for steps, states, going back, and screens per interface
  ("what the steps are for each of the states", "when we can go back", "how", "the screens"). The opinion rests on
  one lens's H proposals; that lens did not read two of the three rows files, and calls its own comparison "not a
  choice". Does option 1 already close the walks' rows? No row is closed by option 1 or by option 2's status marks
  (R-0a); row 13 is closed by one recorded checksum of board.tsx, which needs no graph. What the graph adds beyond
  the line, on today's evidence, is a framework's node list, for a framework that does not exist (A5: "none cheap
  before a framework is chosen").
- I-3 · "The parts that stay keep their pins" (OQ5 b). Rival: keeping is impossible or unsafe often enough that
  "ask per change" or "name the moves" is the default that works. Run on the sound demo: keeping the five non-bus
  signals by name works today (`AUDIO_SHUTDOWN: A2, JOY_SW: D5`, exit 0) and sends the new parts to worse pads
  (`JOYTWO_JOY_Y: SDA`, `JOYTWO_JOY_SW: D14`, the board's own button). Keeping a bus line is refused: `signals[9]
  pins max98357a-dfr0954's I2S_BCLK, an I2S bus line: the assigner places the bus, so drop pin` (exit 2). A kept
  signal on the pad SDA then makes an I2C part impossible: `SDA asks for SDA (GPIO1), which is already taken`
  (exit 1). So the default depends on P868 #1235 for every bus line, the lines that moved in four of my runs, and the
  item's proof (the joystick) can pass without it. Unsafe: a kept pin can hold a new part on the board's own button,
  where council/physics.md:14 reads "a long stick press can power the board down" on an older revision; the PO's
  revision is "not recorded".
- I-4 · "A1 is the riskiest assumption" and the paper spike. Rival: the assumption that is both more important and
  less evidenced is one the table does not hold: that the PO (n = 1, the decider, who "directs Claude rather than
  typing commands", scrum/VISION.md) stands in for the hobbyist, whom the vision calls "Hypothesis ... no person
  outside the project has installed spark". Every value row (A2, A3, A7, A9) is tested by asking him. A second
  candidate: that a status mark is what a change in the middle lacks, and not fixed commands (R-0a); it has no A row
  either. A1 is a feasibility belief with E for two links already. Its spike can hardly fail: the one who proposed
  the table writes it and applies it by hand; "names" is the bar; the "7 things" are the session's own list, and the
  seventh is "Not looked at: do the pins ... move", already answered by ★C4. A paper table also cannot show the
  failure of D-3.
- I-5 · "The bench as witnesses" (OQ9 b). Rival: a shown record is read as the state. The folder's only evidence on
  this is against it (row 6: "a person reads it as the box's state"), and A4 says so; the opinion "this one first"
  stands on the row that speaks against it.
- I-6 · "The PO's additions are views, 'test on the bench' is a phase" (OQ1). Rival: his list is a guess about
  order of availability on the page ("Only later will breadboard and PCB and simulation be available, right?"), a
  question about what the page shows when, not a wish for new phases. Q6 asks "step or view" and not that.
- I-7 · "P827 and P828 survive" (★C15, OQ8 a). Rival: P827's title and Done-when say "the nine phases"; the lens
  itself wrote "(not read; the card holds no code yet)" (council/risks.md:11). Survival is a property of a plan
  nobody has read.
- I-8 · The Frame's proof can pass while the problem stays: a rule that marks all later phases; a project whose
  requirements were written by hand; a change that adds a non-bus part; the CLI only (no page, no agent prompt, no
  going back). After such a pass the person still deletes board.tsx by hand, the I2S pins still move, and the box
  still differs from its record.

## 4. Numbers that lack their unit, population, period or provenance

- N-1 · "10 H" (Stands on): ten assumptions, of which A1, A4, A10 and others carry E tags in risks-and-tests.md; the
  count mixes "open" with "H".
- N-2 · "at least 5 of the 7 things that #1234's comment lists": the population is seven bullets written by the
  session, one of them a question; no reason is given for 5.
- N-3 · "2 of the 15": holds, simulated; the population is one requirements file. With the table in section 1 the
  range on two projects is 0 to 6 of 15 and 0 to 4 of 4, one board model, seven added parts, all simulated.
- N-4 · "40 mA, datasheet-typ" (★C6): no page in the brief; the lens gives "IOH 40 mA at VOH >= 2.64 V" and I did
  not open the datasheet (could not open in the time). "3.3 V output": nominal, not measured.
- N-5 · "1 of the 8 library parts": reproduced (8 files in parts/, 2026-11-17); the store's catalog, which the PO
  uses, is not counted, as the brief says.
- N-6 · "32 rows": 16 + 7 + 9, counted; period 2026-11-16 to 2026-11-17, one person, one board model.
- N-7 · "four vocabularies", "five", "third": three counts of one thing (★C11).
- N-8 · "five new phases" (OQ1 b) and "marks five phases out of date" (OQ6 3): the first is not listed, the second
  is an invented example that reads as a result.
- N-9 · "about 0.6 A against a 1.5 A regulator figure" (Budgets): "calculated from unverified values", no source
  page for 1.5 A in this folder.
- N-10 · "Costs" in Options: no unit at all ("the smallest", "the least code"); the brief says they are H.
- N-11 · "6 agents, 499 calls and about 90M input tokens (2026-10-06)": another council's cost, one run; this
  council ran seven lenses and a refuter.
- N-12 · "three walks in two days", "n = 1": stated; the walks are three sessions on two projects of one gadget
  family (an amplifier, a button and LED), none of which added a part to a finished project.

## What I could not check, and why

- The pages of Terraform, LangGraph and KiCad; the ESP32-S3 datasheet page; need_requirements.py, project_image.py,
  bench_changes.py, deploy_record_store.py, commands/idea.md, tools/journey.py, the README table; the three diaries
  in full; P820's brief.md (D5, D7 to D11); the board's status line. Reason for all: the 30-minute limit. None of
  them is "holds" here.
- No build, pick, look, deploy or simulation was run, by the rules. So "a refused build removes the outputs" is read
  in code, not seen, and every pin result is the assigner's answer, not a board.
- Other boards: every walk project uses the FireBeetle 2 ESP32-S3, so "one board" stays in ★C4's caveat.

## Searches

- none: no web search. Two pages fetched: https://bazel.build/basics/hermeticity and https://design-system.service.gov.uk/patterns/complete-multiple-tasks/ (both for ★C19).

Commands: `flow.py show` (and `--json`) on the three p711 walk folders; `assign_pins.py --json --project <walk folder> <scratch copy>` 25 times (4 base runs, 18 runs with one added part, of which 2 were refused as a bare second copy of a part already there, and 3 kept-pin cases); `gh issue view` for 1234 (with comments), 1236, 1235, 1185, 1186, 1187, 1168, 960; a count over parts/*.json; `/usr/bin/grep` in the council folder, mvp-plan.md and the diaries.
