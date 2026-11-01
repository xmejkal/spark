# P480 refuter: which claims of walk 3 and its five lenses hold

> Three claims fall: deploy does not take an untested pass as tested (product), P468's "no wires, no ready" (the run heard ready), and "the build keeps Wokwi positions" (diary, architecture).
> New bug: every `/spark:build` overwrites the person's `sim/diagram.json`, because the merge runs in an empty temp folder.
> G27 (no `built` for a board-only build) is a written decision, AT151. Diary card C4 says the opposite, and G34's cause is known from P472.

Base: worktree `spark-p480` at `0dec04b6` (main `53c1cbb8` plus P480 docs). Each row names the line I read or the command I ran.

## Findings

| # | claim | who made it | verdict | evidence |
|---|---|---|---|---|
| 1 | G27 (board-only build writes no `built`) is by design | technology | CONFIRMED | `check_spine.py:621-624` refuses `built` when any stage is SKIPPED. Commit `183b6a93`, row AT151 of the P236 refuter, made it so. A PO decision, not a bug. |
| 2 | G27: "the verdict says otherwise" | technology, diary | REJECTED | `check_spine.py:645` prints "the chain runs end to end for the board alone: nothing to wire, so no board was built". The diary quote stops early. |
| 3 | G27 makes deploy or the look say something false | brief question | REJECTED | Only the tally reads `built` (`parts.py:2275`). The look and deploy never read it. The false lines are `commands/build.md:147` and the tally hint `parts.py:2282`, "check_spine records it". |
| 4 | Diary C4: "the build's `built` line, which a board-only build also writes" | diary (Claude's card) | CONFIRMED false | It contradicts G27 and `check_spine.py:623`. Rewrite: a board-only build writes no `built` by design. Whether it starts to is the PO's call. |
| 5 | A step named with the must text clears `unnamed_must` with no assertion | AI | CONFIRMED, documented | `image_evidence.py:292-293` compares names only. `docs/guide/agents.md:939`: "A name is a claim, not a test". The run's no-control caveat (`image_evidence.py:38-40`) still shows. Walk 3 named no step (log: "step names: 0"). Medium, not high. |
| 6 | Deploy counts a pass that tested no must line as tested, "the one false green" | product | REJECTED | The look lists both lines in `unnamed_must`. Deploy's question adds "N must lines were not named by any scenario" (`board_look.py:57-58`). Diary 08:22 and 08:31 show both. Still true: the run verdict "passed" (`run_scenario.py:431`) and the store's `"simulation": "passed"`. |
| 7 | G32: the run log and the verdict say only "passed" | diary, AI | REJECTED in part | Run log lines 3-4: "step counts: expect-pin 0, set-control 0, wait-serial 2" and "step names: 0". Only the verdict line is bare. |
| 8 | P468 (#636, serial wires): without them a scenario cannot hear ready, ranked 3 | product, P468 body | REJECTED | Walk 3's `sim/diagram.json` has `"connections": []`, and its log line 40 says `Expected text matched: "ready"`. Walk 2 heard the XIAO too. The defect is the warning text at `check_spine.py:605-607`. |
| 9 | Build keeps Wokwi positions (`merge.ts`). Architecture: a hand edit is lost only on the board-only path | diary G33, architecture 5 | REJECTED | `check_spine.py:705` builds in a new `mkdtemp`. The converter writes `<tmp>/sim/diagram.json` (`:540-541`), so `cli.ts:85` finds no old file and keeps nothing. `:985` then copies over the project's diagram. |
| 10 | "Nothing keeps a hand-added part or wire, only positions" | diary G33 | REJECTED | `merge.ts:8-10,16` keeps routes and parts marked `handAdded`. Row 9 makes it moot through the build. `tools/circuit-to-wokwi/ARCHITECTURE.md:89-91` is untrue for `/spark:build`. |
| 11 | G34: spark does not know why the FireBeetle needs the buttons. Add a `silent_step` board fact | technology, UX, diary | REJECTED | `docs/discovery/2026-10-31-p472-no-hands/finding.md:21,32`: MicroPython owns the TinyUSB port, and `machine.bootloader()` through mpremote enters download mode, tried on the bench. Card #643's last comment routes it to P469. `silent_step` is a tool field already (`data/tools.json:134,145`). |
| 12 | G16, G19, G34 ride P465 (#633, a board that does not start after a flash) | product | REJECTED | G34 is a running board that esptool cannot reach. That is P469 (#637, look without restart) with the P472 finding. |
| 13 | G36 (`--port` in `next`) rides P473 (#647) | product | REJECTED | P473's body names only the store in `next`, never `--port`. `board_envelope.py:38` always adds `--port`. `commands/deploy.md:37-38` documents it now. |
| 14 | G35 (auto mode refusal) rides P476 (#652) | product | REJECTED | P476 asks one why line per deploy step. It says nothing of a host refusal or of `deploy.md:24`. |
| 15 | G12 rides P406 (#531, the offer shows the fact) | product | CONFIRMED in part | P406 names the 1000-character cap on `power`, the cut JSON. It does not name the doubled `does` words. |
| 16 | G26 rides P468, G15 and G7 ride P466 (#634, MAC names its unit) | product | CONFIRMED in part | P466 ties a MAC to a unit and hold, so G15 fits. G7's one view of library, drawer and store record is not in it. P468: see row 8. |
| 17 | P410 (#536), P413 (#539), P399 (#515) carry "simulation back on" | product | CONFIRMED | One setting, a minute count, and component ids checked before a paid run. The bodies match. |
| 18 | C4, C5, C6 wait on W4-2 and the event seam P479 (#657) | architecture | REJECTED for C4, C5, C6a | `wave4-plan.md` names neither `run_scenario.py`, `check_spine.py` nor `parts.py`. W4-2 is deploy (`:86`), W4-3 is grant, live and reach (`:115`). The look is on the core already (`:204`). Only C6b's bench record meets deploy's seam. |
| 19 | C6 (bench result, honest verdict) goes first | product | REJECTED as ranked | It rests on row 6. C6a is one verdict line, free of wave 4. C6b is a design. |
| 20 | Names `writes` (AI), `store_writes` (UX), `StoreWrite` (architecture) | three lenses | CONFIRMED conflict | `parts.py` declares effects per operation (`("writes",)`, `parts.py:1599`), printed by `--describe --json` (`agents.md:110`). Envelopes carry `effects` (`board_envelope.py:59,98`) and a `written` boolean. Extend `effects` with a place, store or project. Add no fourth name. |
| 21 | G8: only the code and the output say that `--step` writes | diary | REJECTED in part | `--describe --json` marks `step` as `writes` (`parts.py:1597-1599`). The pages and `--help` still say nothing of the store. |
| 22 | New code `NO_REQUIREMENTS` | UX | CONFIRMED, rename the flag | `board_look.py:470-474` maps a missing file to `NO_BOARD_NAMED`. A split fits the `NO_SIM_TOML` pattern. But `look.py --board-only` reuses `board_only`, the requirements flag (`needs.py:514`). UX's `NOT_BUILT` repeats `NO_SIM_TOML`. |
| 23 | P-C5d adds "after the look, press RESET once" | UX | REJECTED as new | `board_doctor.py:46-47` already says "After it, press RESET once so the firmware starts". G19 is only that the look's `next` lacks it. |
| 24 | `board_alone` at `:571`, the `board_only` fork at `:386`, `host_parts` taken | architecture | CONFIRMED | `check_spine.py:386-389,571-590`. `parts.py:313` `host_parts` means passives a part asks of its host. `carried_by` is free. |
| 25 | P391 (boards as modules) has only stored kinds | architecture | CONFIRMED | `design.md:6-7,57-67`: a `RecordKind` per stored record kind, a module as a third. No derived part. |
| 26 | C2 deletes "about 80" lines, a net cut, and "closes G27" | architecture | REJECTED | `board_alone` is 20 lines and the fork 4. Sheet, schematic and diagram lines for carried parts add code. A board-only `built` reverses AT151, so the PO decides. |
| 27 | C2: "a stand-in board needs no GPIO check" | architecture | REJECTED | The S3 devkit stand-in exposes GPIO 0-21 and 35-48 only (`boards/firebeetle2-esp32s3.json:108`). The P396 check (`boards.py:417-430`) finds a part on a missing GPIO. Keep it. |
| 28 | C2a: keep the S3 devkit `wokwi-board` document, as the XIAO has | technology | CONFIRMED feasible | `github.com/wokwi/wokwi-boards/tree/main/boards` lists `esp32-s3-devkitc-1` (fetched 2026-11-01). The FireBeetle record holds no such document. |
| 29 | G14 (the other-choice note) not checked | technology | CONFIRMED, checked now | `needs.py:377` names the other choice only when `limits.no_pin`. Here the limit is "no Wokwi definition". `commands/idea.md:128-129` says the note always names one. Fix the page. |
| 30 | G11 not checked | technology | CONFIRMED, ran | `parts.py --match .` in walk 3 lists `xiao-esp32-c6-fresh (button-light)` under all three needs, with no word. |
| 31 | G2 not checked | technology | CONFIRMED | `installed_plugins.json`: spark 0.4.0, installed 2026-09-23. The cache holds `hooks`, a README and 4 skills, no `commands/`. The repo is 0.9.0. |
| 32 | C3: refuse a folder that is not there | four lenses | CONFIRMED, with a rule | `store.py:276-297` and `needs.py:113-116` reproduce G9. `needs.py:114` cites §8 S rule 5, "the project's folder made when it is new". C3 changes that rule, so the card names it. |
| 33 | G1, G3 to G10, G13, G15, G17, G18, G20 to G26, G28 to G31 hold | technology | CONFIRMED by reading | `board_look.py:467-474`, `init_project.py:430`, `commands/init.md` (no store line), `image_evidence.py:95`, no `ticks` in `scripts/stand_in/`, no dry run in `check_spine.py`, no `p295-own-simulator` link in user pages. |

## C1 to C8, after the refutation

- C1 (Wokwi and own emulator spike): keep. No claim against it.
- C2 (a board's own parts): keep the `carried_by` design, but keep the P396 GPIO check. Take G27 out as a PO question.
- C3 (project name or folder): keep. The card names §8 S rule 5, which it changes.
- C4 (store writes said): rewrite onto the existing `effects` declaration. First fix `build.md:147` and `parts.py:2282` for board-only builds.
- C5 (board on USB): split code from flag. Name the flag apart from `board_only`. Move G34 to P469.
- C6 (bench result): C6a, one verdict line in `run_scenario.py`, now. C6b, the bench record, is a design after W4-2.
- C7 (hand edits): starts with the row 9 bug, not with a page.
- C8 (Mac tests): G30 and G31 hold. Nothing else checked.

## New cards

- P? — `/spark:build` overwrites the person's Wokwi diagram → the converter merges into the kept `sim/diagram.json`. Need: row 9. Done when: a test builds twice with a moved part and a `handAdded` part, and both stay.
- P? (or a rewrite of P468) — the "no serial monitor" warning fires for boards that print over USB → the warning reads a board fact. Need: row 8. Done when: walk 3's build prints no serial warning, and a board without a USB console still gets it.

## Not checked

- G12 and G24 not re-run. No Wokwi page read on duty checks, so "expect-pin reads level only" rests on the diary.
- No build and no converter run. Row 9 rests on reading `check_spine.py` and `cli.ts`. A test is the next proof.
- Whether `${CLAUDE_PLUGIN_ROOT}` in `deploy.md`'s `allowed-tools` pointed at the 0.4.0 cache in walk 3 (a link between G2 and G35).
- The feasibility of AI's C6 typed-yes gate for a bench line (`deploy_gate.py` not read).
- `scrum/VISION.md`, `scrum/STORY_MAP.md` and the rehearsal rows.
