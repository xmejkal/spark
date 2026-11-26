# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>. -->

The architect's list (council/architect.md §11), changed by the refuter and the delegated council (D3 to D8). The order to build: P999 #1455 and item 4, then items 2 and 3, then P1078 #1582, then item 6, then item 1 (approved, D11). Item 19's first steps run beside P999 and P1078, before item 6's plan (D17). P999 may not cover the clock, because its stand-in lacks GPIO14 and the clock uses it (brief ★C25). Nothing is filed. spark-main files on the PO's yes.
Cards left alone: P999 #1455 (do it first), P1000 #1456 (waits on the bench read of the e-paper controller), P1078 #1582 (a prerequisite of item 6), P413 #539 (feeds item 9).

## 1. The flip: a board that no simulator covers ends the simulation stage `skipped` with a reason, in one small PR after the seam and after the PO's yes to Q11
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: a test fixture board with no Wokwi part builds with the simulation stage `skipped` and its reason, and a build record written before the change still counts as done <!-- REQUIRED:value-proven-by -->
- depends on: item 6. The PO approved it on 2026-11-26 (D11). Old records keep counting as done through `NO_MODEL_CODES`, and the PR names the exit code change (2 becomes 0) in `docs/guide/agents/flow.md` <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: absorbs the clock half of P995 #1452 (the spike's answer stands, the card closes as answered)

## 2. `check-firmware`: the move of `import_firmware.py` onto the core, with the project's own tests, in one free Operation that needs no `sim/` and calls no strategy yet, its record kept under `.spark/`
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: `check-firmware --json` on the clock gives the import count and "35 of 35" for its tests <!-- REQUIRED:value-proven-by -->
- depends on: the core's Operation pattern (P1078 #1582 is its next user, not a blocker). The dry run joins it as the strategy's `problem` in item 6. A failed own test blocks no deploy until the PO decides <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: absorbs P410 #536's "quick free check" and the `import_firmware` line of #1105

## 3. The page: the Simulation step's coverage line and the free checks' state
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: the clock's page names what can run and the free checks' result, in grey where nothing more runs <!-- REQUIRED:value-proven-by -->
- depends on: item 2. It reads the build record's simulation stage as it is today, so it does not wait on item 1 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): the page epic, linked to P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: —

## 4. The list "what this simulation cannot show" prints only after a run
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: a deploy with no run prints one line, "no simulation tested this image", and no list <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: —

## 5. Spike: do `wokwi-cli lint` and `chip compile` run with no token and no minutes?
- type: spike <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: a finding with the commands run and their output, token unset <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: absorbs Q1 of P492 #671, and leaves its Q3

## 6. The `Simulator` seam with no behaviour change: the base, `WokwiSimulator`, the Fake, one generic lookup from a role's contract to an Adapter (shared with the P1089 engine seam), at every selection site of council/architect.md §3. The guard moves into `coverage` and keeps its ending. It gives "selectable, not exchangeable" until a second Adapter speaks its own contract, and its plan waits for item 19's first steps (D17)
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: the goldens hold, and one table names the Adapter <!-- REQUIRED:value-proven-by -->
- depends on: P1078 #1582 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: —

## 7. The run record names its simulator and its grade
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: a log header names the simulator, its version and the grade <!-- REQUIRED:value-proven-by -->
- depends on: item 6 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: is P308 #374, absorbed

## 8. The `simulator` role, on or off, as the one setting, said by the commands
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: a project with the role off runs the free checks and says that no paid run happens <!-- REQUIRED:value-proven-by -->
- depends on: item 6 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: replaces P410 #536
- the setting (the PO's rule of 2026-11-26, P1194 #1740): the role `simulator`. Default: `wokwi-cli` (Wokwi), and "off" as a no-simulator entry (D5). Layers as the tools list has them today (`data/tools.json:2`): global (spark's `data/tools.json`), user (the person's `tools.json` in the store), project (`.spark/tools.json`, which wins). The free checks have no setting: they always run. The seam reads the setting through P1194's settings seam once that exists

## 9. The cost and the time cap before the yes for a paid run
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: the question before a run names the minutes this month by spark on this machine and the free plan's 50 <!-- REQUIRED:value-proven-by -->
- depends on: item 6, P413 #539 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: P413 #539 stays and feeds it

## 10. The simulation editor: the values, how each part and the chip are simulated, and the steps (D16)
- type: story <!-- REQUIRED:item-type -->
- needed by: the PO, 2026-11-26, verbatim: "Well, basically what wokwi has, pease research what all wokwi allows to set for the simulation and we should also allow it, so yes, a temperature or values in general, but really also to set up how its simulated the chip or part, maybe even the steps" <!-- REQUIRED:needed-by -->
- value proven by: on the VL6180X project's page, the editor shows the distance with its range, the board's CPU setting, the model that stands for each part, and the scenario's steps as sentences. A change asked of Claude lands in the project's files, and the next run uses it <!-- REQUIRED:value-proven-by -->
- depends on: item 6. The editor reads and writes spark's own words through the `Simulator` seam, and `WokwiSimulator` turns them into Wokwi's `attrs`, chip attributes and scenario steps, so a second simulator reuses the same editor <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- what it sets, from research-wokwi-settings.md: (A) values: a part's `attrs` (a DHT22's temperature and humidity, a potentiometer's level, a photoresistor's lux), a custom chip's attributes and its controls' ranges, and the run's timeout. (B) how a part or the chip is simulated: the board's attrs (`cpuFrequency`, `flashSize`, `psramType`, `serialInterface`), a button's `bounce`, and which model stands for a part (a Wokwi part, a chip, or a skip). (C) the steps: `delay`, `wait-serial`, `write-serial`, `set-control`, `expect-pin`, `take-screenshot` and the four touch steps. One table of control names per part, kept with the part's record, because Wokwi documents them per part page
- the settings it names (P1194 #1740): a part's values and the steps live in the project (layer project). How a part is simulated has its default in the part's record (global, the library), and a project can override it (layer project). The board's attrs have their defaults in the board record and a project override
- slices: first the values and the steps, drawn and changed through Claude (D6). Then how each part and the chip are simulated

## 11. The result on the page, the caveat in the verdict's line
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: walk2's run reads "passed, but it tested only the start" <!-- REQUIRED:value-proven-by -->
- depends on: item 7 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: —

## 12. Spike, in two halves: a community chip named by reference in wokwi-cli, and its licence rule (the free half first, the run after the PO's yes for its minutes)
- type: spike <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: one free run with a chip named by `github:` reference, its licence read, and the rule written <!-- REQUIRED:value-proven-by -->
- depends on: the PO's yes for the run's minutes <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: replaces P409 #535. P344 #439 is its worked example

## 13. Spike: a live value in Wokwi's editor for a spark project
- type: spike <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: a finding: how a spark project opens in Wokwi's editor with its controls, or why it cannot <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: —

## 14. Spike, free: the clock's `main.py` loop on the stand-in with a virtual clock, with no device model (replaced by item 19, D15)
- type: spike <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: a finding: whether the loop runs 10 simulated seconds with no edit to firmware/ <!-- REQUIRED:value-proven-by -->
- depends on: A1's test result, and the PO's reading of the non-goals (Q3) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: —

## 15. Gate A: one free condition, "no failed run on the current image", and the evidence row "Tested before the board", with the highest tier reached (D10)
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: the "On the board" card shows the row, and gate A stays shut while the current image has a failed run, which costs no minutes <!-- REQUIRED:value-proven-by -->
- depends on: item 7. The deploy's reader of a failed run exists (`scripts/spark/bench/image_evidence.py:433`) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P79 #16 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: —

## 16. A paid-run policy: when a paid simulation runs, warns or asks, and how a person marks a version important or risky
- type: story <!-- REQUIRED:item-type -->
- needed by: the PO, 2026-11-26, verbatim: "generally it should as all things like that be configurable, if we run the pyd minutes and like a threshold for example when it should warn and not run the payed ones by default, and it would also be great to have the option of somehiow only running it even though its payed only for the important releases or version or something like that, or it can always ask, lets try to have some reasonable conditions like that and figure out how we could work with such limits, like how do we mark a version/deployment as important or risky enough to actually use the sim even thouhg its payed.." <!-- REQUIRED:needed-by -->
- value proven by: a project with the policy "only for a version marked important" runs the free checks and asks no paid run on an unmarked version. It names the policy when it skips the run, and it warns once the minutes spent this month pass the threshold <!-- REQUIRED:value-proven-by -->
- depends on: item 8 (the role), item 9 and P413 #539 (the minutes count), P1194 #1740 (the settings seam with layers) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the settings it names (the PO's rule, P1194 #1740), each a proposal for its plan: the policy `paid_runs`, one of `never`, `ask`, `important-only` and `always`, with the default `ask` or `never` to be chosen in the plan (the PO's words name both "not run the payed ones by default" and "it can always ask"), layers user and project. The threshold `paid_minutes_warn_at`, in simulated minutes per 30 days, default to be set in the plan against the free plan's 50 (brief ★C10), layers user and project. The mark: a version or deploy marked important or risky, kept with the image's sha256 in the project, layer project. So a mark ends at the next firmware edit, and a choice that outlives edits is the project's `paid_runs` (the architect, D17). How a person marks it (a word to Claude, an offer on the page, a release tag) is an open question for its design
- the tied card: P410 #536 (replaced by item 8) held the first words of this choice. P413 #539 feeds its threshold

## 17. The vision's v0.10 line says "firmware that passes the simulation where a simulator covers the board"
- type: chore <!-- REQUIRED:item-type -->
- needed by: the PO's yes to Q10 on 2026-11-26 (D12): "skipped, with the reason, and the free checks passed" is enough for v0.10 <!-- REQUIRED:needed-by -->
- value proven by: `scrum/VISION.md`'s v0.10 line and D-c agree <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): chore <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: the vision is the PO's file. The change is his to merge, and this discovery edits it nowhere

## 18. Spark's own simulator, reuse first (epic)
- type: epic <!-- REQUIRED:item-type -->
- needed by: the PO, 2026-11-26, verbatim: "Actually, I would like to spike and create an epic for re-implementing the simulator and seeing how difficult or possible it would be for us to actually re-implement the simulator. Obviously, not from scratch, but maybe there are some available resources or code that would be useful for us. Let's actually create the cards for it and just do some pre-analysis now." <!-- REQUIRED:needed-by -->
- value proven by: a spike's finding (item 19) that the PO reads and picks from, then, if he picks a way, one walk project whose firmware runs on spark's own simulator for a board that Wokwi lacks <!-- REQUIRED:value-proven-by -->
- depends on: item 6 (the `Simulator` seam), so an own simulator is one more Adapter and no screen changes <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): epic <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one, or after v0.10 as P492 #671 was <!-- REQUIRED:spark-process:slice -->
- the tied card: takes over item 14 (the stand-in runner spike) and P492 #671's question 2. The pre-analysis is in the store's preanalysis/2026-11-26-own-simulator.md. Its setting (P1194): the `simulator` role points at it, with its default left at Wokwi

## 19. Spike: how hard is spark's own simulator, and which free code does it build on, with licences
- type: spike <!-- REQUIRED:item-type -->
- needed by: the PO, 2026-11-26 (item 18's words) <!-- REQUIRED:needed-by -->
- value proven by: a finding with sources (URL, version, date, licence) that sizes each way the pre-analysis names and recommends one, run on one walk project's firmware with no paid minutes. Its first steps test A10 and run before item 6's plan (D17) <!-- REQUIRED:value-proven-by -->
- depends on: the pre-analysis <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): item 18 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): as item 18 <!-- REQUIRED:spark-process:slice -->
- the tied card: replaces item 14

## 20. `chips/wokwi-api.h` carries no licence line and comes from Wokwi
- type: chore <!-- REQUIRED:item-type -->
- needed by: AGENTS.md:64, "Never commit a vendor file, because installing spark copies the whole repository", and brief C26 <!-- REQUIRED:needed-by -->
- value proven by: the header's licence is read from Wokwi's own terms and cited beside it, or the build fetches it and the repository no longer holds it <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): chore <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: — . Found on the way by the pre-analysis (D15)

## Board actions
- file items 1 to 20 (item 14 replaced by 19, so 19 cards) · pending, the PO's yes to this list · through spark-main <!-- REQUIRED:board-actions -->
- close P995 #1452 as answered, P409 #535 and P410 #536 as replaced, P308 #374 as absorbed · pending, the PO's yes · through spark-main
