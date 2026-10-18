# PO-assistant lens: the MVP walk and the slices that make it run

> **TL;DR.** The MVP is one walk of button + LED on the XIAO ESP32-C6: words, parts, build, simulation, wiring, deploy,
> a lit LED, then "add a second LED" and a second deploy. Four PRs make it run: the shipped XIAO record (S), P290 (S),
> P213a (S), and P213b with its bench walk as P100's round A (M). Remove or swap, the buzzer, drag and save, and the live view come after the line.

## Claims and evidence (reproduced 2026-10-18, scratch store, no USB)

1. **The test project is button + LED, not a buzzer.** `SPARK_HOME=<scratch> parts.py --need buzzer` prints "nothing in
   the library matches 'buzzer'" (also for "beep"); `--need led` finds `led-red-5mm`. `parts/` holds 8 records, none a buzzer.
   A buzzer means research agents that never ran (README Research "partly"). Using one in walk 1 adds risk to the first walk.
2. **The shipped XIAO record stops the build. The facts that fix it already exist in a fixture.** `check_spine.py` on
   `{"board":"xiao-esp32-c6","parts":["tactile-button","led-red-5mm"]}` exits 2: schematic `could-not-run`, "the board
   states no power.io_volts". The same parts on `tests/data/breadboard/button-light-xiao/boards/xiao-esp32-c6-fresh.json`
   build all stages and write `breadboard.md/.json/.svg`, `page.html`, `sim/` ("the chain runs end to end"). The fixture
   has keys the shipped record lacks: `power` (io_volts 3.3, cited Table 5-2 p.64), `power_pads`, `documents`, `sources`, `sku`.
   So slice 1 copies cited facts. It needs no new research and is S, not the "header facts" chore that P278 #314 describes.
3. **The MVP change can be an add, so no remove command blocks the MVP.** On the fresh record, adding
   `{"part":"led-red-5mm","name":"LedTwo"}` builds to simulation (10 traces, 8 wires). Named duplicates already work
   (`tests/data/breadboard/motor/requirements.json` has two buttons). The missing remove or swap (`parts.py:2250`, "kept, not
   from a pick") hurts only a swap. It moves after the line.
4. **Risk carried into slice 1.** Both XIAO builds warn "no serial monitor is wired in the diagram ... a scenario's
   wait-serial may hear nothing" (`check_spine.py:569`). gaps.md says a XIAO scenario passed on 2026-10-14. Slice 1 must
   show that a `ready` scenario passes on the shipped record, or name why it does not.
5. **P213b already holds the second deploy.** #192 PR b: "The PO changes one line, and the scenario passes. Claude deploys
   again, and both board logs show it." P100 #6's last comment asks for "a walk with the PO on a small real project". One
   bench session can serve both: P213b's walk *is* round A, with the change made in the circuit and not only in a line of firmware.
6. **P290 #347 bites on the first deploy call.** The PO's run on 2026-10-18 failed at the erase and worked 5 s later
   (#347). In a first walk, that failure reads as "spark is broken". It is S, so it goes first.

## Ordered slices (the MVP line after 4)

| # | card | title | done when (testable) | interface | size |
|---|---|---|---|---|---|
| 1 | P278 #314, widened | The shipped XIAO record builds the loop | `check_spine.py --keep` on tactile-button + led-red-5mm with `"board":"xiao-esp32-c6"` reaches simulation and writes `breadboard.json`; facts copied from the fresh fixture with their cites; a `ready` scenario passes once, or the serial gap is a card | Claude | S |
| 2 | P290 #347 | Deploy retries the connect once | the first call after the look goes through in 3 of 3 bench runs; tests for one failure, two failures | both | S |
| 3 | P213a #192 (+ P291 #348 if same files) | `look.py` / `deploy.py --json` | envelope with `needs_yes`; agents.md lists them | Claude | S |
| 4 | P213b #192 + P100 #6 | `/spark:deploy` and walk 1: words to lit LED, then a change | in one session: "a button that lights an LED" via `/spark:idea` to a requirements file, build, scenario passes, the PO wires the sheet, `/spark:deploy`, press = lit; then "add a second LED" by words, rebuild `--keep` keeps the moves, scenario, deploy again; both board logs; each stall filed as a card | both | M |
| — | **MVP line** | | | | |
| 5 | P248 #270 | A bounded console read | Claude reads 5 s of output after a deploy and sees the button press print | Claude | S |
| 6 | NEW (P293 story 1, part 2) | Remove or swap a part by words | after "this LED out", `--requirements` drops it and a `--keep` build keeps the other moves | both | S |
| 7 | NEW + P209 #178 | Walk 2: "a small thing that beeps" | the research route runs for the first time and writes a buzzer record; `--need buzzer` finds it; swap the LED for it (slice 6); the scenario passes; deploy | both | M |
| 8 | P292 #351 | A lost jumper is named | test as on the card | person | S |
| 9 | P293 story 2 | Drag, save, Claude reads it | the person moves a part on a local page and saves `breadboard.json`; a rebuild keeps it; Claude names the move (P294 option a, the saved file) | both | M |
| 10 | NEW | The Wokwi token in `/spark:setup` | setup names the token, its page and its cost | person | S |
| 11 | P295 #356 | Live view: own page + bench on the `machine` stand-in | the button and LED project runs in the page with no token; `wokwi-cli` stays the final check | both | L |
| 12 | gaps #8 | RC car, first slice | one epic line until 7 and 9 are done | both | L |

**Why the line falls after 4.** After slice 4 the PO's sentence runs once: he talks, Claude uses spark, it builds,
it simulates, it deploys, "we go back and edit the schema, and then everything rebuilds". Slices 5 to 12 make the
walk nicer or wider ("fully nice and useful"). Slice 4 does not need any of them.

**P296 #358 runs beside the slices, not in the order.** It touches no journey code. A conflict merge cost one agent most of 390k tokens (#358).
That cost lands on every slice. It is S. Pull it when a slot frees.

## On gaps.md's order of 8

- Keep 1 (the shipped XIAO). It is smaller than gaps.md says, because the facts already exist (claim 2).
- Move 5 (`/spark:deploy`) and P290 ahead of 2 (the walk). Then the walk tests the interface that Claude will really use, and one bench session does the work of two.
- Move 3 (remove or swap) after the line. The MVP change is an add (claim 3).
- Keep 4 (the buzzer) as walk 2, after 6 (the console read). Keep 7 (the token) late. For the PO it is a cost, not a stop.
- Keep 8 (the RC car) last, as one line only.

## Park or drop

- Park: P284 #331 and P288 #344, the mutation chores. They do not move a breadboard closer. #344's analysis already
  set "once per story, cap 12" (#349), so the rest can wait.
- Park: P275 perfboard, P276 catalogue editor, P277 Fusion and P279 jumper check. P279 comes back with slice 9, which edits jumpers.
- Park: P286 #336 (unknown boards and other firmware), P76 #5 and P74 #8, until walk 1's diary asks for them.
  P223 #205 goes with the RC car.
- Shrink: P278 #314 becomes slice 1 (power and header facts from the fixture). P100 #6 becomes walk 1, inside slice 4.
  The plants project and the update round wait for walk 2. P293 splits: story 1 part 1 is done in walk 1, part 2 is slice 6, and story 2 is slice 9.
- P218 #200 closes with slices 2 to 4 and #348.

## Risks

- Slice 1's serial warning (claim 4): if the shipped record cannot pass a `ready` scenario, deploy refuses, and the MVP waits.
- The walk spends 2 or more Wokwi CI runs (before and after the change). No free limit is stated (build.md:207).
- `/spark:idea` has never run as a conversation. Walk 1 may stall at step 1. If so, file the stall as a card and go on with a hand-written needs file. Do not stop the walk.
- If P213b slips, walk with plain `deploy.py`. Do not hold the walk for the command.
