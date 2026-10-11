# Board order and WIP limits: a proposal (2026-10-06)

*For the PO, who orders both boards (W11). This serves P146 (#80). It merges four lenses in this folder: value,
truth and risk, dependencies, and flow and WIP. It is read-only work: no card was moved, no issue was edited, and nothing
was committed. Sources: spark at `8f7733d`, the bin at `8847eb8`, and both boards as exported at 12:41, plus P146,
filed at 10:44 UTC. Each line gives a reason you can check. Where the lenses disagree, the table at the end says so,
and this text follows its recommendation.*

## In short

- **Finish what is open first.** That means today's four reads, P146 (this proposal and its process twin), P102e (#29),
  and B1 (bin #1) tonight. P97 (#18) is the first new card to start.
- **Raise the limits a bit, and count honestly.** Ready goes from 3 to 5, and in flight from 2 to 3. Every working stage
  stays at 1. An epic counts where it is the work: in Discovery and Design. Build stays at 1, and P102e moves to Review
  when its build ends, which frees Build without a second branch.
- **spark's Ready, in order:** P146, P97, P143 (#77) with P107 (#41), P110 (#44) with P116 (#50), then P122 (#56). The
  checks are made honest before P136 (#70) adds any rule.
- **The bin, in order:**
  - the bench text tells the truth (P58, bin #5, widened; P73, bin #2);
  - a short bench session with owned parts;
  - the remedies of B25 (bin #19) and B26 (bin #20);
  - one parcel;
  - the rest of B14 (bin #8), then B16 (bin #10).
- **On the board:** close three cards, park five, and file one now and one when B1 closes.
- **Six decisions,** in §7.

## 1. Finish first

What is open now, in the order it finishes.

### Today

1. **Put the running work where it is.** These moves are proposed, not made. Today's gate still passes after them, because
   it exempts epics.
   - P146 (#80) goes to Design: its board and process proposals are running.
   - P136 (#70) goes to Discovery: its reads are running, and it is P102e's first use.
   - P94 (#17) and P76 (#5) end the day in Idea. Their reads only answer questions, and once an answer is posted on
     its card, the card goes back to Idea (rule 2 in §6).
2. **The four reads land.**
   - Data, chips and the component format go to P94.
   - Problem → fix → calculated parts, with B25 worked through, goes to P136 and bin B25.
   - Function-first suggestions go to P76 and P136.
   - The skill's research and design go to P102e.

   Each answer is posted on its card. Then one docs PR commits all of today's inputs as P136's discovery inputs, as
   planned. New cards from these reads stay few: the process lens R4 proposes a small cap per run, with the rest kept on
   one checklist under the epic.
3. **Your decisions.** First the six in §7, then the process proposal's as a separate batch (R4: one batch of at most
   six at a time). Then P146 goes to Ready.
4. **B1 (bin #1), at the end of the day, as you asked.** Read it from the drawer's DFRobot import, read-only, then post
   the answer and close the card. The memory note of 10-04 says the import shows a DFR0954 bought twice and no DFR0534
   from DFRobot, though one may have come from elsewhere.
5. **The day-close for 10-06.** It names each running workflow with its card.
6. **Housekeeping.**
   - Remove the worktree `~/Development/spark-p103` and the merged local branches. That worktree is on the merged
     `p103-process-docs-2` and lacks P105's (#36) fix d4faf06 (`git merge-base --is-ancestor` exits 1), so a push from it
     still risks the leak.
   - GitHub's `p103-process-docs`, which holds the leak's junk commits, stays your call.

### Then

7. **P102e (#29) finishes its build, in the order its 11:05 comment sets:**
   - the design's two critics;
   - the core;
   - the software scenario, re-run;
   - the extensions;
   - the spark scenario, re-run;
   - the negative scenarios.

   The rehearsal's `green/` folder is empty today. After the build, P102e goes to Review. It has no PR, so its final
   review reads the skill's files. It is Done when its first real use, P136's discovery, has produced journeys and a
   story map by following the skill (decision 3).
8. **P146 (#80) enters Build when P102e moves to Review.**
   - The work: the code half of the limits, with its tests, mutations and docs (§6).
   - It enters Review once P102e is Done, because Review holds one card. Then the merge.
   - It is Done when you confirm the written process describes how we work, and `board.py status` lists every card
     with work running and still says "the limits hold".

After that, Ready is pulled from the top.

## 2. Ready on the spark board (at most 5)

Today's gate allows 3 until P146's code half lands. Until then, Ready holds P146 (once you decide), P97 (already there)
and P143, with P107 riding as a task (decision 2). P110 and P122 join once the new limit is in the code.

| # | card | why |
| --- | --- | --- |
| 1 | **P146 (#80)** | Already in flight. It sets the limits every other card runs under, and it is one sitting (see `wip-prototype/`). |
| 2 | **P97 (#18)** | It ends idea → board, the README's "Not built yet", and has been in Ready since 10-05. It needs decision 4 first. |
| 3 | **P143 (#77)**, with **P107 (#41)** riding | A misspelled severity vanishes, so it would hide any rule P136 adds. P122's proof needs P107's null answer, and today a null bus capacitance crashes physics (`check_physics.py:415`). Cheap. |
| 4 | **P110 (#44)**, with **P116 (#50)** riding | Until the build reads the kept `board.tsx`, every check answers about a board the person does not have. This is the truth lens's first fix. It is one function (`keep_into`, `check_spine.py:594`), and you decided its behaviour on 10-05. |
| 5 | **P122 (#56)** | The checks read's first fix. On a generated board the I²C check prints nothing, and a series resistor counts as a pull-up. With its three new holes it may not fit one sitting; if not, split it by hole. |

**Next in line,** as slots free:

- P117 (#51), P131 (#65) and P119 (#53): could-not-run, instead of an ok or a traceback.
- P109 (#43) and P124 (#58): the CONFLICT behind B26 reaches `check_all` and the JSON. Relabel P109 as a bug.
- P141 (#75) and P108 (#42).
- P138 (#72), P123 (#57) and P113 (#47): what spark runs on a stranger's machine.
- P139 (#73).
- P106 (#39), first in line if Build is ever raised.

**No column orders what enters Discovery next.** Keep that order as the top rows of Idea: P136, then P100 (#6), then
P94's (#17) second phase.

## 3. Next per epic

- **P102 (#24), team tools.**
  1. P102e, then P146.
  2. P102b (#27): draw the first discovery's map in Miro, and in Canva once its connector is authorised.
  3. P102d (#28), narrowed. The README's "What works today" now answers its question; what is left is a proof on each issue
     and a field that says proven or not.
  4. The epic's review, audit and retro, the first under Kanban.

  Move P102f (#30) out of the epic to sit beside P77 (#13). P102's own *Value proven by* names P102b and P102d, but not
  P102f.
- **P133 (#67), the checks tell the truth.**
  1. P143 with P107.
  2. P122.
  3. P117, P131 and P119.
  4. P109 with P124.
  5. P141 with P108.
  6. P145 (#79), which rides with P122 if the shared predicate makes them one change.
  7. P118 (#52), which takes in P43 (#11).
  8. P115 (#49) and P125 (#59), with P135 (#69) from P134 (#68).
  9. P111 (#45).
  10. P120 (#54), only after its reshape: a driver draws what its motor draws, B26 adds the module's standing draw, and B15
      (bin #9) adds the measured current.
  11. P140 (#74), before any per-rail power rule.

  Park P142 (#76), P144 (#78) and P126 (#60) outside the epic (§5), so that its proof, "every sub-issue is Done", can be met.
- **P134 (#68), the build is the board you keep.**
  1. P110 with P116.
  2. P139: fix it now from DFRobot's schematic, and let the bench's VCC reading on USB confirm it.
  3. P135 (#69).
  4. P129 (#63).
  5. P121 (#55); the docs already call the XIAO pin-map only.
  6. P130 (#64), which spends Wokwi minutes and so needs your yes (W10).
- **P132 (#66), a stranger's first board.**
  1. P138, P123 and P113.
  2. P137 (#71) and P114 (#48), init's words.
  3. P112 (#46): pin the MCP servers.
  4. P127 (#61) and P128 (#62).
  5. The epic's proof: a cold run on a bare machine.

  Run R2.6 (#15) only after that, so that an outside person is not spent on known gaps.
- **P136 (#70), full circuit checks.**
  - The discovery runs now, as P102e's proof.
  - Its first question is yours: analogue simulation is out of v1 (`VISION.md:60`). Does P136 change that?
  - Then today's reads become decisions:
    - the architecture: the checks read recommends honest checks first, then general rules over record facts, with
      lessons arriving as proposals and no automatic learner;
    - suggesting fixes and calculating parts, with B25 as the worked case;
    - suggesting circuits from functions, which it shares with P76.
  - Question 4, where in the journey, goes to P100.
  - Nothing is built before P143, P107, P122 and P141 land. The first build card is likely the pull-up budget rule, and
    its first real case is the bin, with B21 (bin #15).
- **P94 (#17), the store.**
  1. P97.
  2. Your call on the tension with W21: "a record grows when a stage needs a fact", against every form and properties
     that keep growing as they are computed or found.
  3. A second design phase: the component format, project data updates, modules downloaded with their chips, and the
     catalogue of solution kinds.

  Before anything downloads or updates itself:
  - P87 (#19), P90 (#21) and P92 (#23) land;
  - the facts spark already ships are made true: P64a (#12), P139, P124, and the VL6180X card in §4.

  P89's (#20) remainder rides in P97's plan, and the plan says whether P90's and P91's (#22) overlaps ride too.
- **P100 (#6) and P76 (#5).**
  1. P100's discovery, after P136's. It covers both journeys, the new idea first and then irrigation, as you answered on
     10-05; those answers are only in the archive, so copy them onto #6. It answers P136's question 4.
  2. P76, which is where P102e's method reaches users (your 11:08 decision). Its output is `needs.json`.
  3. Function-first suggestions, which have no card yet. They come after P97 and P76.
  4. The catalogue, after P87, P90 and P92.

  P39 (#10) is that engine's gap at the command line.
- **No epic, but the vision's *Next* row.**
  1. P59 (#7), re-scoped first against the firmware direction of 10-01.
  2. P74 (#8): "a command that exits 1 on irrigation today and 0 after its fix".
  3. P77 (#13), which takes P78's (#14) last line and gives P102f its home.

## 4. The bin, up to and through the bench

The bench waits on your hands and one parcel, not on spark's slots. The bin's Ready column is empty today; put items 1
to 3 there.

0. **B1 (bin #1), tonight** (§1). When it closes, file a card to retire the DFR0534 fallback: `board-v3-dfr0534.tsx`
   and `Dfr0534Player` (W16).
1. **P58 (bin #5), widened to everything read at the bench.**
   - The README's pin table and its deep-sleep section still describe the XIAO, the C6 and `04_mp3.py`
     (`firmware/micropython/README.md:66-69, 166-190`).
   - **A new finding, on neither board:** `02_inputs.py` would pass a button that can never wake the bin.
     - It still says both buttons go to GND (`:4`), and it passes when "each button read 0 when pressed" (`:57`).
     - But OPEN has been active-high since 09-25, with `PULL_DOWN` (`:31`).
     - So a correctly wired OPEN fails, and one wired to GND passes.
   - `05_motor.py:6` says the 10k pull-downs keep the motor still. STATUS item 6 says they sit near VCC/2, above the
     2.5 V threshold.
   - Add this README to `check-current-docs.py`, so that it cannot go stale again.
   - Desk work, cheap.
2. **P73 (bin #2), and B14's proof line rewritten to use it.**
   - Today "each prints PASS" is met even if every step fails: 01, 02, 04 and 05 always print "PASS if …" (`01:24`,
     `02:57`, `04:71`, `05:52`).
   - The vision's *Next* proof is "the bin's bring-up 01–06 logged with a verdict per step". That is P73's log.
   - B14's proof becomes that log, with three named readings:
     - VCC with only USB plugged in (P139);
     - each L9110S input's resistance to VCC, and whether D1 lights (B26);
     - D12 with a hand over the sensor (B25).
3. **B8 (bin #3): the 200 runs.** Do them before step 06 runs the real firmware, and before a remedy edits it. Cheap.
4. **A short bench session with owned parts, nothing bought.** Each reading is posted on its own card.
   - B21 (bin #15): the SKU is DFR0975 from the import, so only the revision is left.
   - B20 (bin #14): the pitch.
   - The button height, which goes into B18 (bin #12).
   - The L9110S meter check, which goes into B26.
   - A photo of the VL6180X carrier, which goes into B25: its numbers assume a Pololu #2489.
5. **B25 (bin #19): decide the remedy at the desk before the bench is wired,** from the problem → fix read when it
   lands. Its proof moves to B16 (item 10).
6. **B14 (bin #8), steps 01, 03, 04 and 05, with owned parts.**
   - Step 05 also measures **B15 (bin #9)**: the motor's current, running and stalled.
   - At step 03, reproduce B25 first (W9). Wire it as `board.tsx` is today, including the 100 kΩ `TofIntPulldown` that
     the bench instructions never mention. D12 should read about 1.89 V, against the S3's 2.475 V; both figures were
     re-computed here. Then fit the remedy and read D12 again.
7. **B26 (bin #20): decide the remedy after B15,** because a motor above about 500 mA changes the driver. Correct its
   day count from its own inputs: 17.7–19.5 days with a red LED, or 20.6–23.1 with a blue one, not "20–26"
   (re-computed here).
8. **B18 (bin #12), rewritten for the breadboard, as one parcel.**
   - SHOPPING.md's board passives are 0603 SMD (`SHOPPING.md:94-104`), for a board we are not ordering.
   - The parcel carries the breadboard parts, B20's cable, the buttons at the measured height, and both remedies'
     parts.
9. **B14, steps 02 and 06.** B14 is then Done, with a verdict for every step in P73's log.
10. **B16 (bin #10) and B26's proof.**
    - B16's proof becomes B25's measurement. With the chip asleep, D12 reads at least 2.48 V while asserted, and at most
      0.82 V while not.
    - B26's proof: the pack draws under 0.1 mA while the board sleeps.

**After the bench:**

- B17 (bin #11), then B22 (bin #16, optional);
- B19 (bin #13), unblocked now that spark is public, then P32b (bin #6);
- B5 (bin #4).

**spark's half of B25 and B26.**

- File one spark bug under P133, needed by B25. Its record and its simulation both say the line works:
  - The VL6180X record says the interrupt line "clears an ESP32-S3's input high threshold", with no condition, and
    names its pull-up R6, where B25 says R5 (`parts/vl6180x-breakout.json:76`).
  - Its Wokwi chip drives INT push-pull (`parts/vl6180x-breakout/chip/vl6180x.chip.c:69,174`), so no simulation can
    show B25.
- Fold B26's half into P120's reshape: `parts/l9110s-module.json` has no LED fact and no standing-draw fact.
- **Noticed, not on a card:** spark's L9110S record says both inputs high is "Off" (`:88`), but the bin's `motor.py:77-80`
  calls it a brake that shorts the motor. The datasheet decides which is right.

## 5. Close or merge

| card | proposal | evidence |
| --- | --- | --- |
| **P72 (#31)** | Close it: its last cut is P146's. | Cut 2, "one sprint per slice", ended with Kanban (`scrum/README.md:47`). Cut 3 is done: `UNMUTATED` exists (`tests/test_self_confirmation.py:70`), and the backlog is archived. Cut 1 says a working agreement either fails a command or moves to one page of habits. P146's agreements audit is doing exactly that, and says "P146 covers the same ground" (W16). |
| **P43 (#11) and P118 (#52)** | Merge them: keep P118, and close P43. | The archive cut P43 to "the `fix` half only; the rest parked" (`PRODUCT_BACKLOG.md:1381`). That half is P118: both stop `check_all` flattening a finding to `subject: detail` (`check_all.py:129, 140-141, 229-230`). P118 sits under P133, whose bar it moves; P43 sits under no epic. Add P43's "a `fix` for every problem" to P118's proof. Also note on P119 and P131, which point at P43 for the status words and shapes, that those are parked. |
| **P78 (#14)** | Close it, and move its last line to P77 (#13). | Its premise has been false since `c233826`: `parts/led-red-5mm.json` exists, and `series` is a host part kind (`parts.py:330`). What is left is "irrigation's `STATUS_LED` becomes that part", and `irrigation.requirements.json:18` still has `"needs": []`. That is P77's regeneration. |

**Park, do not close.** Each card stays open until the first design that needs it pulls it (W14).

- P142 (#76): no design has two devices at one address, and P141 will name the gap meanwhile.
- P144 (#78): `copper_thickness_mm` is null in all four projects.
- P126 (#60): it belongs to slice 8, and "We are NOT ordering the board".
- On the bin: B23 (bin #17) and B24 (bin #18).

Take P142, P144 and P126 out of P133.

**Not duplicates, though they share code:** P110 and P116; P115, P125 and P135; P119 and P131; P109 and P124; P121 and
P126; P114 and P137. Each has its own reproduction, so keep the cards and ride each group in one PR (decision 2).

**Bodies to refresh.** The migration of 10-05 dropped what the archive said:

- P97: your open question, and the list from P96's fix round (P96 predates the issues);
- P100: your 10-05 answers;
- P76: "store first" (10-04) and the seven ways in;
- P89, P91, P92: the parts already done;
- B21: the SKU is known;
- B19: spark is public;
- P102e: its proof line still says P100 only.

## 6. WIP limits

| stage | now | proposed | why |
| --- | --- | --- | --- |
| Discovery | 1 | **1, epics counted** | One discovery at a time, because your answers are the constraint. Both day-closes so far were AT_RISK, B1 waited ten days, and the process lenses agree. P136 first, then the flows. |
| Design | 1 | **1, epics counted** | Your yes on a spec comes one at a time. |
| Ready | 3 | **5** | All four lenses agree. Ready is a queue, not work. It lets you order P97 and the first truth fixes together, and 17 bugs arrived today. |
| Build | 1 | **1** | One plan, one branch. The push gate still measures HEAD, not the ref being pushed (P106), and a pre-P105 worktree is still on disk. Riding pairs together gets more done per PR. |
| Review | 1 | **1** | |
| In flight | 2 | **3** | One in the session, one with agents in the background, one waiting. With every other stage at 1, the third card can only be in Discovery or Design, so there are still at most two code branches (Build and Review), as today. |

**Two counting rules, without which no number holds** (from the flow lens):

1. An epic counts in Discovery and Design, where it is the work itself. From Build on, its stories carry the limit, as
   today.
2. A card is in its working stage while any work runs on it, a background read included. A read that only answers a
   question puts the card back in Idea when its answer is posted.

Placed honestly, today's board had work running on at least four cards: P102e, P136, P146 and P94. Today's check said "the limits
hold"; the proposed check names the breach.

**The bin's cards.**

- Its desk cards (P58, P73, B8, a remedy's edit) use the same session, so they count in the same three.
- Its bench sessions are your hands: one at a time, outside the three.
- The gate reads only spark's board, so until it reads both, the day-close names any bin card in flight.

**Pair the raise with a cap on what reaches you** (process lenses R3 and R4): decisions come in one batch of at most six
at a time, and each run files only a few new cards. That cap is P146's process half.

**What changing them takes:**

- **The card:** P146 (#80). The code is the first task of its plan, not a new card.
- **Code** (`wip-prototype/proposed.diff`): 8 lines in `tools/check_backlog.py` and 1 in `tools/board.py`.
  - `check_backlog.py` gets the new limits, `MOST_IN_FLIGHT = 3`, and one `counts()` rule for epics and tasks.
  - `board.py`'s `in_flight()` uses the same rule, so the status cannot hide what the gate counts.
- **Tests:** two of today's 14 are rewritten (Ready's limit and the in-flight cap), and six are added or widened. Each
  writes the limits out instead of reading them from the module (W2).
  - I ran the prototype: all 19 pass on the proposed code, and 6 fail on today's code, which is where they pin the
    change.
  - The prototype is built for Discovery 2. Keeping Discovery at 1 changes one constant, two tests and one mutation.
    That variant has not been run.
- **Mutations:** a new table of 11, all caught in the run.
  - P102a's (#25) entry "an epic counts against the limits" is deleted, not re-anchored (W16), because its anchor no longer
    exists.
  - A gap closes on the way. Today the Discovery, Design and Review limits can each be raised with no test failing: 3
    such mutations escaped in the run.
- **Docs, in the same commit:**
  - `scrum/README.md:52, 65, 67, 72, 79, 81`;
  - W6 (`WORKING_AGREEMENTS.md:69-71`);
  - the backlog design: §3 (`:49`, `:51`, `:56`), §8 (`:139`), §9 (`:178`), and a dated entry in §11;
  - `GLOSSARY.md:220` and `docs/guide/developing.md:61` link to the README's table instead of repeating the numbers.
- **By hand:** the column limits in both boards' Board views, since GitHub's API cannot set them.
- **The trial's note:**
  - Keep 2026-11-02, and record "limits raised 2026-10-06, the trial's second day".
  - Widen its first question to "was any limit broken without being caught, counting work on a card the board showed in
    Idea".
  - Compare how many days cards waited on you before and after (R3).
  - Optionally add a question: did a card sit more than three days in one stage with no Waiting flag?
- **Memory:** `scrum-process.md` and `spark-scrum-state.md` repeat the old limits; update both after the merge.

## 7. Decisions for the PO

This is one batch of six. The process proposal's decisions come after it.

1. **The limits.**
   - **(a) Recommended:** Ready 5, in flight 3, and every working stage at 1. An epic counts in Discovery and Design, and
     a card sits in its stage while work runs on it (§6).
   - (b) As (a), but with Discovery 2, so that P136 and the flows run side by side, as #29's comment of 09:27
     records. This is the flow lens's choice.
   - (c) Build 2, so that P97 runs beside P102e. This is the value lens's choice, and it should wait until P106 lands.
2. **Pairs that one PR closes.**
   - **(a) Recommended:** they count as one. The lead card counts, and a companion moves with it, labelled `task`, which
     the gate already skips (`check_backlog.py:39`). No code is needed; P146's docs say so.
   - (b) The gate counts linked PRs instead of cards. That is code, in P146.
   - (c) Every card counts, so Build takes one bug at a time.
3. **P102e's finish line.**
   - **(a) Recommended**, by the flow and dependency lenses: it goes to Review when its build ends. It is Done when P136's
     discovery has produced journeys and a story map by following the skill. Its review reads the skill's files, since
     there is no PR. The cost: until that first output, P146's PR waits behind it.
   - (b) It is Done only after both P136 and the flows, as #29's comment of 09:27 records. The cost: it holds Review through two
     discoveries, and every PR waits behind it.
4. **P97, before it is planned.**
   - What does a drawer entry with no `count` mean?
     - **(a) Recommended:** owned, count unknown, and the pick says so. Your own-words entries carry no count, and
       bought is not the same as still in the drawer.
     - (b) Used up.
   - Either way, two fixes come with it:
     - P97 writes the requirements file (store design §4, §9; P76's output is `needs.json`). The README's Idea row
       credits P76 (`README.md:69`), so correct it.
     - P97's proof gains "and no stand-in line". `/spark:build` always passes `--assume-missing-sizes`
       (`check_spine.py:356`), so its `[ok]` cannot fail on a missing outline.
5. **The bin before the bench.**
   - **(a) Recommended:** decide B25's remedy at the desk, reproduce B25 at step 03, and make B16's proof B25's
     measurement. Run B14's owned-parts steps, with B15, before ordering. Then rewrite B18 for the breadboard, and order
     once, after both remedies.
   - (b) Order first, then run B14 whole. That reaches the bench sooner. But a remedy that needs parts means a second
     parcel, and the order as written buys 0603 SMD passives.
6. **Tidy the board.**
   - **(a) Recommended:**
     - close P72, P43 and P78 into P146, P118 and P77;
     - park P142, P144 and P126 outside P133, and B23 and B24 on the bin;
     - move P102f beside P77;
     - file one spark bug for B25's spark half, and fold B26's spark half into P120's reshape.
   - (b) Leave them as they are.

## Where the lenses disagree

| question | value | truth and risk | dependencies | flow and WIP | this proposal |
| --- | --- | --- | --- | --- | --- |
| Build limit | 2 | 1, with batches | 1; 2 only after P106 | 1, until P106 and the trial | 1; P102e moves to Review to free Build |
| Discovery limit | 1 | — | 1, epics counted | 2, epics counted | 1, epics counted (decision 1) |
| In flight | 3 | raise only after P106 | — | 3 | 3; the third card is upstream, so no extra branch |
| First spark fix | P122 with P107 | P110 | P143 with P107 | — | P143 with P107, then P110 with P116, then P122 |
| P142, P144 | park; lower | batch them | after P122; any time | — | park both |
| P102b, P102d | move out of P102 | — | keep them in P102 | — | keep them: P102's proof names them; move only P102f |
| B18 and B14 | order, then bench | — | owned-parts steps first, order after the remedies | — | the dependency lens's order |
| P73 | before B14 | with B14, or rewrite B14's line | optional | — | before B14: the vision's proof is a verdict per step |
| P43 and P118 | keep P43 | — | one change | — | keep P118, under P133 |
| The bin's cards in the count | desk cards yes, bench no | — | their own lane | the same total, once one is in flight | desk cards count; one bench session at a time |

*All of this is judgement (W11, W20).* The ranks are opinions, and "cheap" and "one sitting" are estimates. Three sets of
figures were re-run here: B25's levels, B26's day counts and the prototype's counts. Everything else is cited from the
lens files, the issues, or a file read today.
