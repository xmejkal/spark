<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# P1190 the simulation step: discovery brief

> TL;DR. Spark's simulation is today one build stage and one paid command, both written for Wokwi. A board that Wokwi
> lacks reads `could-not-run`, although the gadget works. This discovery proposes the simulation as a step of its own
> with five substeps: what can be simulated, the free checks, the scenario, the run and the result. It also proposes
> one strategy seam that a spark setting chooses, and three ways to simulate a part. Nothing here is decided until the PO or the delegated
> council says so.

**Ready for:** collecting evidence <!-- REQUIRED:ready -->
**Stands on:** 9 H, — of which would change the decision <!-- REQUIRED:debt -->
**Decision needed:** the PO picks a direction for the simulation step (the substeps, the strategy seam and the first
slice), and says whether a simulation verdict ever gates the permanent build (gate A). <!-- REQUIRED:decision-needed -->

## Frame
- Request, verbatim (corrections marked): the PO, 2026-11-26, on [P1190 #1735](https://github.com/xmejkal/spark/issues/1735): "Wait, so, actually that's a good question, please let als the spark main know about the need for the simulation screen and step built in. And since it not always works, because we're currently using the Wokwi tool to run it and it doesn't always have all the boards etc, so it doesn't always pass or can run at all even though its actually working in real life, we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part, also that Wokwi as the strategy for simulation adds some screens or ux and ui parts in general , because of woring with the parts that are matchable directly  so wokwi knows how to simulate it, to the module or boards and parts we can simulate by some script or setting, adding sliders etc to set the measured value for example and also being able to werite the webassembly to simulate more compex modules and parts  and boards, which maybe we can somehow reuse existing working librariws and then just extend them , I am not really sure, so this all needs to be researched, alternatives found, separated into the actual substeps of it, the editor, displaying the resultsm etc.." And for every brief: "the architecture needs to be well made so that we can change these srtrategies and tools and its reusable, dry". <!-- REQUIRED:request -->
- Decision · decider: which shape the simulation step takes (its substeps, its screens, its strategy seam and its first slice), and what it means for gate A · the PO. Choices that the council of three on Fable (the PO assistant, the architect, the tech lead) can answer are delegated to it while he is away, recorded "delegated, the PO's to change" (spark-main's brief, 2026-11-26). <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): the card's "Done when": "A person sees the simulation as one step on the page: the free checks, then a run by the chosen strategy, with each part simulated directly, by a setting or by a custom chip, and a board Wokwi lacks no longer reads as a failure." Observed on the clock walk project (p934-display2): its `.spark/build.json` today says `simulation: could-not-run, board_not_in_wokwi`. The proof is the same project after the change: the page names the simulation step, the free checks run, and the board's state says which strategy covers it or why none does, in grey and not as a failure. <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): D-a no paid simulation runs without the PO's yes, its cost named first (CLAUDE.local.md "Never"; AGENTS.md). D-b spark exports facts, never behaviour: the conversation writes firmware and scenarios (AGENTS.md, the firmware decision). D-c a build that stopped only on `board_not_in_wokwi` counts as done (the PO, 2026-11-21, `scripts/spark/flow/guide.py:24-25`). D-d free, few and local, and a spark setting switches a tool (AGENTS.md). D-e analogue simulation and a link between two boards are out of v0.10 (scrum/VISION.md:77). D-f one core: logic in a small class behind an Operation, every interface thin (AGENTS.md, the PO 2026-11-25). D-g the PO's strategy rule quoted above (2026-11-26). <!-- REQUIRED:decided -->
- Open questions: listed under Questions, Q0 to Q8. <!-- REQUIRED:open -->
- Scope · out of scope (proposed): in: the simulation step's substeps, its screens and states on the page, the free checks, the paid run and its yes, the three ways to simulate a part, the alternatives to Wokwi, the strategy seam, how the result reads at gate A. Out: building any of it (design and plan come after), analogue simulation (D-e), a full own simulator (P295 option D), the PCB and perfboard screens (the past-breadboard council), and any paid run. <!-- REQUIRED:scope -->
- Start and reach (proposed until Q0): start existing product · decider reachable no (the PO is often away, and questions go through spark-main) · users the PO only (n = 1, the walks) · data and connectors: the code, the walk projects, the cards and the web, all read. Wokwi's account page is not connected (minutes left unknown) · decider as a user n = 1 · must not get worse: a passed Wokwi run still opens the deploy, and the free checks stay free. <!-- REQUIRED:start-reach -->
- Flags (yes · no · —; asked only when it changes a decision; never legal advice; any date or threshold is read at its source at run time and cited):
  - sold or given away, or personal use: no (spark is MIT and public, the gadgets are personal) <!-- REQUIRED:flag-sold -->
  - connects to a network or runs software (for example the EU's Cyber Resilience Act): — (spark runs software, but the item changes no shipped product) <!-- REQUIRED:flag-network -->
  - children or food contact: no <!-- REQUIRED:flag-children -->
  - market: — (not relevant to a simulation step) <!-- REQUIRED:flag-market -->
  - radio (unlicensed-device rules; read at their source when it decides): no (a simulation radiates nothing) <!-- REQUIRED:electronics-firmware:flag-radio -->
  - a Li-ion cell (charging, transport, battery rules): no <!-- REQUIRED:electronics-firmware:flag-li-ion -->
  - mains: no <!-- REQUIRED:electronics-firmware:flag-mains -->
  <!-- EXTEND:flags -->
- Extensions (each active id · the fact that activated it; when none matched, only "none matched: core only · the fact that decided it", naming no extension; list any directive skipped under rule 9): electronics-firmware · repo-has boards/*.json; spark-process · repo-has scrum/WORKING_AGREEMENTS.md. Its directive "questions go through AskUserQuestion" is replaced by spark-main's brief for an away PO: no question dialog, delegated questions to the council of three, the rest relayed by spark-main. This tightens nothing away: every question still waits for an answer. <!-- REQUIRED:extensions -->
- The item (its issue, or the proposal in the decider's words) · what is still open elsewhere · the repository's push check, or "no push check here": [P1190 #1735](https://github.com/xmejkal/spark/issues/1735), in Discovery since 2026-11-26 · open elsewhere: the P1089 spike (PR #1733, the engine strategy pattern), the past-breadboard council (gate A waits on this item), and other sessions' cards run by spark-main · the hook (`tools/check_commit`, the pre-push gate) and spark-main's push slots. <!-- REQUIRED:spark-process:item -->
<!-- EXTEND:frame -->
- Depth: TRIO (the PO assistant, the user, the tech lead), three agents on Opus, then the refuter on Opus and the architect for the synthesis, as spark-main's brief names. <!-- REQUIRED:depth -->
  <!-- Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06). -->
- Search budget: one or two searches per alternative, stop at the first good match (CLAUDE.local.md). Spent: two research agents, 40 tool calls in all ([research-wokwi.md](research-wokwi.md), [research-alternatives.md](research-alternatives.md)). Each lens has at most 3 searches. <!-- REQUIRED:budget -->
- Appetite (the decider's, asked only when heading for design) | —: — <!-- REQUIRED:appetite -->

## What we found <!-- CLAIMS -->
- [★C1] The simulation is a stage of the build, and the build's simulation stage knows only Wokwi: a board record with no `wokwi_part_type` ends it as `could-not-run` with the code `board_not_in_wokwi` · E `scripts/spark/build/stages.py:112-113`, `scripts/spark/build/build_service.py:395`, `:451` · caveat: none
- [★C2] The clock's own build reads `simulation: could-not-run, board_not_in_wokwi`, and the page counts that build as done and says there is no simulation · E the walk project p934-display2's `.spark/build.json` (read 2026-11-26), `scripts/spark/flow/guide.py:24-25`, `scripts/flow.py:33-35` · caveat: one project (n = 1)
- [★C3] Simulate is phase 8 of 9 on the page. Its one offer, "Run the simulation", asks Claude, and the step runs in the person's terminal and "uses Wokwi CI minutes" · E `scripts/spark/flow/flow_codes.py:11`, `:141`, `:153`, `:364` · caveat: the page has no screen of its own for the simulation's substeps or result
- [★C4] The free checks exist, but only as the first part of the paid command: `run_scenario.py --dry-run` checks the simulation project, `firmware/main.py`, the steps, the component ids against the diagram, littlefs and the image, with no token and nothing written · E `scripts/run_scenario.py:10-21`, `scripts/spark/firmware/scenario_run.py:131-178` · caveat: a second free check, the import of each firmware module on the stand-in, is a different command (`scripts/import_firmware.py`)
- [★C5] Half a strategy seam exists: the tools list has a role `simulator` (today `wokwi-cli`) with the contract `wokwi-project`, and a role `diagram-converter` (`circuit-to-wokwi`). A person or a project can point a role at another tool · E `data/tools.json:5`, `:7`, `:21`, `:23`, the P1089 finding §3.1 (PR #1733) · caveat: the contract is Wokwi's project shape, so a second simulator must speak Wokwi's files today
- [★C6] Wokwi's words are spread through the code: 42 modules under `scripts/spark` contain "wokwi" (case ignored). The firmware area (`sim_project.py` 39 lines, `scenario_run.py` 35) and the breadboard drawing (`drawing.py` 47) hold the most · E `grep -rci wokwi scripts/spark`, run 2026-11-26 · caveat: a line count, not a count of Wokwi logic. The breadboard reuses Wokwi's pictures and pin positions to draw, which is not simulation
- [★C7] A part record says how it is simulated in three ways: a Wokwi part (`simulation.wokwi.part`), a custom chip kept beside the record (`simulation.wokwi.chip`), or a reason to skip it (`simulation.skip`). Of the 8 part records in the repository's `parts/`, 2 name a Wokwi part, 2 a custom chip and 4 a skip · E `parts/*.json`, counted 2026-11-26, `scripts/spark/firmware/sim_project.py:1-8` · caveat: the person's store holds more records, most with no `simulation` key (17 of 18 read)
- [★C8] A slider for a measured value already exists in one custom chip: the VL6180X chip shows a "Distance (mm)" range control, a "Range status" range and an "Unplug the sensor" switch · E `parts/vl6180x-breakout/chip/vl6180x.chip.json` · caveat: Wokwi's chip.json page lists only `range` as a control type (research-wokwi.md §2), and this chip also uses `boolean`
- [★C9] Wokwi's custom chips compile to WebAssembly from C (recommended), Rust or AssemblyScript, and can model GPIO, analog, timers, UART, I2C, SPI and a framebuffer · E https://docs.wokwi.com/chips-api/getting-started, read 2026-11-26 (research-wokwi.md §2) · caveat: read by a research agent. The research did not find the Chips API's beta label on the page
- [★C10] Wokwi's paid part: the free plan has 50 minutes of simulated time per rolling 30 days. Pro is EUR 20 per seat a month with 2000 CI minutes. No offline run without minutes is documented · E https://docs.wokwi.com/wokwi-ci/getting-started and https://wokwi.com/pricing, read 2026-11-26 (research-wokwi.md §1) · caveat: Hobby and Hobby+ CI minutes are not on the pricing page. Spark keeps no count of the minutes it spent (P413 #539)
- [★C11] A stand-in board exists for a board Wokwi lacks: the FireBeetle 2 ESP32-S3 record names `board-esp32-s3-devkitc-1` with `wokwi_is_stand_in: true`. P999 #1455 proposes the same for the FireBeetle 2 C6 on Wokwi's ESP32-C6 DevKitC-1, with GPIO14 missing there · E `boards/firebeetle2-esp32s3.json`, [P999 #1455](https://github.com/xmejkal/spark/issues/1455) · caveat: a stand-in tests the chip's GPIO numbers, not the board's own parts
- [★C12] No open simulator drives the pins of an ESP32-C6 today. Espressif's QEMU (9 Nov 2026) boots the C6 with GPIO strap values only. Velxio drives GPIO, ADC, I2C and SPI from outside on the ESP32, S3 and C3, under the AGPL · E https://github.com/espressif/qemu/releases, https://github.com/espressif/esp-toolchain-docs/blob/main/qemu/README.md, https://developer.espressif.com/blog/2026/07/velxio-browser-based-esp32-simulation/, read 2026-11-26 (research-alternatives.md) · caveat: whether Velxio loads a MicroPython image is not confirmed
- [★C13] A free logic-level base exists in spark: the `machine` stand-in has a Pin that remembers its level, with `set_level` and `level` for a test, and the import check runs each firmware module on it. It does not run `main.py` or its loop · E `scripts/spark/firmware/stand_in/machine.py:1-23`, `scripts/import_firmware.py:1-15` · caveat: P295's option B (2026-10-18) priced a bench on it as "large"
- [★C14] Gate A of the past-breadboard design leaves the simulation out, because the clock's simulation is `could-not-run`. Its refuter found that "the board said ready" locks the clock too (the sleeping firmware gives "ready unknown") · E the store's councils/past-breadboard/architect.md:9 and :271, refuter.md:35 · caveat: a council's design, not yet the PO's decision
- [★C15] The scenario run is not yet an Operation: `run_scenario.py` has its own argparse and prints, and P1078 #1582 moves it onto the core with the paid run as a `needs_yes` step · E `scripts/run_scenario.py:62-81`, [P1078 #1582](https://github.com/xmejkal/spark/issues/1582) · caveat: P1078 waits on PR #1580 and P1077

## Options <!-- CLAIMS -->
- ⟨filled after the council⟩ <!-- REQUIRED:options -->
- Proposed no-gos and rabbit holes (proposals until the decider confirms): ⟨filled after the council⟩ <!-- REQUIRED:nogos -->

## Riskiest assumption and its test
- Riskiest: ⟨filled after the council⟩ <!-- REQUIRED:riskiest -->
- Test · kind · pass line, dated before any result · proposed | D<n>: ⟨filled after the council⟩ <!-- REQUIRED:test -->

## Questions
- Q0 · Is this frame right: the decision, the start and reach, the extensions and the depth? · decides: the frame · status: queued, for the delegated council <!-- REQUIRED:q0 -->
- Q1 · How important is each assumption, and what pass line must the riskiest test meet? · decides: importance and pass lines · status: queued <!-- REQUIRED:q1 -->

## Decisions

## Found on the way <!-- CLAIMS -->
- ⟨filled after the council⟩ <!-- REQUIRED:found -->

## Board actions <!-- REQUIRED:spark-process:board-actions -->
- none taken. Every board move, filing and push goes through spark-main (its brief, 2026-11-26).

## Hand-off
not yet: the frame, the jobs, a direction and the remaining risk are unconfirmed <!-- REQUIRED:handoff -->

## Files
[Jobs and journeys](jobs-and-journeys.md) · [Story map](story-map.md) · [Risks and tests](risks-and-tests.md) · [Verification](verification.md) · [Items](items.md) · [Research: Wokwi](research-wokwi.md) · [Research: the alternatives](research-alternatives.md) · council/
