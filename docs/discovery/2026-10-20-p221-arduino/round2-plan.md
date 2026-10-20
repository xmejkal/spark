# P221 round 2: plan and tests lens, four platforms (Sonnet, 2026-10-20)

Input: finding.md, refuter-1.md (trusted over finding.md), the three lenses, `gh pr list --state merged --limit 80`.
(V) checked this run, (U) unverified. New PO constraint: ESP-IDF and PlatformIO will come, not only Arduino.

> **TL;DR.** One seam, three cuts. A `platform` names the framework (`micropython`, `arduino`, `espidf`). A `toolchain`
> names the build tool (`arduino-cli`, `idf.py`, `platformio`). Order: seam refactor, Arduino by arduino-cli, ESP-IDF,
> then PlatformIO as a second build tool for both C++ frameworks. Each slice leaves MicroPython working and adds one
> thing. Honest total: 30 to 44 PRs (median 36), about 4 to 7 weeks of calendar at spark's pace, set by the bench.

## 1. Slice order, and why Arduino is second

Spark merged 80 PRs from 10-14 to 10-20 (V), about 11 a day, so PR count is cheap and the PO's bench time is the limit.

| Option for second | Install cost | Closeness to spark's flow | Verdict |
|---|---|---|---|
| arduino-cli + esp32 core | 5.6 GB core, all chips (V, refuter 7); a C6-only install is smaller (U) | compile gives one image; esptool unchanged; C6 supported in core 3.3.10 (V, refuter 8) | **Second** |
| PlatformIO, Arduino framework | `pip install platformio`; packages come per board and framework (U, likely smaller than 5.6 GB) | one tool covers Arduino AND ESP-IDF frameworks (U) | Strong, but see below |
| ESP-IDF direct (`idf.py`) | export script plus a toolchain per target, 1 to 3 GB (U) | native C6; C++ allowed; Kconfig and a `main/CMakeLists.txt` the person never wants to see | Third |

Honest weighing of PlatformIO as the first C++ step: it is the better long-term tool (one tool, two frameworks, a
`platformio.ini` file that pins versions, `pio run` writes `firmware.bin` and a merged image). But stock `espressif32`
lacked the C6 in the platforms.md council (U), and the C6 needs the community fork (pioarduino) with Arduino core 3.x (U).
spark's only walked board is the C6, so a fork and an unverified claim sit on the critical path. arduino-cli has the C6
verified in the core's `boards.txt` (V). So: **A0 is a two-tool bench spike** (arduino-cli and PlatformIO, same sketch, C6
only, measure disk, time, merged image, verify-flash). If PlatformIO builds the C6 cleanly and is smaller, swap slices 2
and 4 and make PlatformIO the Arduino toolchain. Default without that proof: arduino-cli. "Object-oriented C++" works in
all three frameworks, so it does not pick the order.
Design consequence: the build tool is a role strategy (`Compiler`), not the platform. PlatformIO then costs 2 to 3 PRs
at the end, because the platform seams already exist. "A spark setting lets a person switch a tool" (AGENTS.md) is this key.

## 2. Slices (something always works after each)

Naming rule: refactor PRs touch only MicroPython and keep every outside test green. Platform PRs add a strategy.

**S0, test base and seam (MicroPython only). 8 to 11 PRs.** Works after: everything as today, behind `FirmwarePlatform` roles.
- T1 `ServiceCase.make_service()` and `FakeToolFinder` (tools.find patched about 60 times in 19 files, V tests lens). 1 PR.
- T2 `PlatformContract` mixin written against MicroPython (see section 3). 1 PR. Overlaps P323 slice 1a (contract mixins, goldens).
- R1 `platform` key (default `micropython`) and one picker, replacing `deploy.py:171` and `run_scenario.py:150`; the person
  picks it at `/spark:init` and in requirements.json (the missing "where" of refuter 2). `PinMapRenderer` out of
  `assign_pins.py`. 2 PRs. R2 board record `firmware_images` map, `micropython_port` optional in `board.ts`. 1 PR.
- R3 `FirmwareLayout`, `FirmwareCheck`, `ImageBuilder`. 1 to 2 PRs. R4 `BoardProof`, `ConsoleReader`, optional
  `BoardShell`, `DeployService.verify` free of mpremote. 1 to 2 PRs.
- R5 `FirmwarePlatform` as role objects, `unsupported` prints `skipped` never `ok` (refuter 9). 1 PR.
- R6 pull-up text from the renderer, platform in the run log, wake facts under `micropython`, `PROJECT_FILES` of
  `tools/check_docs.py:25` made per platform. 1 PR.
- Doc: developing.md role table, agents.md "platform" key. In R1 and R5, not later.

**S1, Arduino on the C6. 9 to 12 PRs.** Works after: button and LED, build to compile to flash to `ready`, `pins.h`, sheet, diagram.
- A0 bench spike, docs only (core or PlatformIO, C6 compile, merged image, verify-flash, `ready`, CDC on boot). 1 PR + bench.
- A1 setup: `compiler` role in `data/tools.json` with fetch and checksum, `/spark:setup` shows size first, core pinned. 1 to 2 PRs.
- A2 `CppPinMap` + `pins.h`, `//` marker. A3 layout, compile check (first 40 lines of errors), merged image. A4
  `ArduinoPlatform`, `FlashReadProof`, `not_for_platform` for live and reach. 1 PR each, 3 to 4 with fixes.
- A5 Wokwi for a compiled image: `sim_project` with the real `.elf`, `wokwi.toml` (U, may stay out). 1 PR or a finding.
- A6 commands, skills, agent prompts (102 tracked files name MicroPython or mpremote, V refuter 2; about 25 steer Claude).
  1 to 2 PRs. A7 README table, `tools/journey.py`, Miro, doc pages. 1 PR. Bench walk fixes 1 to 3.

**S2, ESP-IDF on the C6. 6 to 9 PRs.** Works after: the same project as C, `idf.py build`, merged image, same deploy.
Needs: an `EspIdfCompiler` role, a generated `main/CMakeLists.txt` and `sdkconfig.defaults` (spark exports facts only:
pins in `pins.h`, no behaviour), `app_main` as the conversation's C++. Adds nothing to the proof (the same esptool
verify). PRs: E0 spike (install size, `idf.py set-target esp32c6`, build time), E1 tool and setup, E2 layout and check,
E3 platform, E4 prompts and docs, plus 1 to 3 bench fixes. Pays off: a second C++ strategy proves the seam is generic.

**S3, PlatformIO as a toolchain. 3 to 5 PRs.** Works after: `toolchain: platformio` builds Arduino or ESP-IDF projects.
P1 `PlatformioCompiler` + `platformio.ini` writer (pins framework and platform version), P2 setup, P3 docs, bench 1 to 2.
The contract test must pass unchanged. Moves to slice 2 if A0 favours it.

## 3. Tests that stay the same while the insides change

1. **Outside, never edited:** `tests/test_json_contracts.py`, the CLI tests, `tests/test_deploy_json.py`, `tools/snapshot.py
   --against` (baseline 2026-10-11). New platforms add goldens as additive keys. Cheap edge: run `--against` at the end of S0 (V).
2. **`PlatformContract` mixin**, one test class every platform subclasses: `pin_map_text` is accepted by its own check;
   `make_image` returns one or more blobs with an offset list; `layout` names the boot file; `check` of an empty
   firmware tree gives `could-not-run`, never `ok`; an unsupported step (`live`, `reach`) prints `skipped` plus a code;
   `proof` returns `ready`, `not_seen` or `unknown`, never a pass for an unknown. Written for MicroPython (T2), subclassed by
   Arduino, ESP-IDF and PlatformIO in a few lines each. Ripple W1 rows 1, 4, 5 and 12 become contract cases.
3. **Fakes for tools:** `FakeToolFinder`, `FakeCompiler`, `FakeFlasher`, `FakePortFinder` in `tests/fakes.py`; recorded
   output from real tools in `tests/data/` (as `board_look` does). A fake that always succeeds proves the call, not the code.
4. **Opt-in compile-only tests:** `arduino-cli`, `idf.py`, `pio` each run on a tiny sketch when the tool is found. When it
   is absent they print `skipped`, never pass (AGENTS.md); an env var `SPARK_TEST_TOOLCHAINS=1` is one switch. There is no CI
   in the repo (V), so they run on the PO's Mac or by hand. A compile is "compiled", not "checked".
5. **Mutation tables:** a platform PR names its planted defects (`tools/mutate.py`); T1 should say how tables find a line (U).
6. **Bench walks:** one real board per platform, the P100 walk, the PO's time. A bench pass is the only proof of pins and boot.
7. **First test PR:** T1 (builder helper and `FakeToolFinder`), one PR, no behaviour change. T2 is the second. P323 slice 1a
   (parked until the PO's yes, PR #414 is a draft) also adds contract mixins and goldens: T2 either is that slice's test
   half or waits for it. Recommend T1 now; T2 is delayed until the PO answers D4, so nothing runs twice.

## 4. Honest PR range and bench time

Counted from 80 merged PRs in 7 days (V). P239's deploy seam took 8 PRs (V refuter 2) for a smaller change than S0.

| Slice | PRs | Bench walk by the PO (U) |
|---|---|---|
| S0 test base and seam | 8 to 11 (median 9) | 0, only a MicroPython regression walk of 30 min |
| S1 Arduino | 9 to 12 (median 11) | first C6 walk 1 to 2 h incl. the core download, A0 spike 1 h, 1 to 3 fix rounds 30 min each |
| S2 ESP-IDF | 6 to 9 (median 8) | 1 to 2 h incl. the toolchain install |
| S3 PlatformIO | 3 to 5 (median 4) | 45 min |
| Journey, Miro, rows | 3 to 5 | none |
| **Total** | **29 to 42 (median 36)** | **about 6 to 9 h in all, in 4 to 6 sittings** |

Calendar: 4 to 7 weeks (U). If the PO skips refactor first, S1 alone is 4 to 8 PRs but leaves `if platform` in callers,
and S2 would repeat it. Six refactors pay off without a second platform (finding.md): S0 is not a bet on Arduino.

## 5. Decisions waiting on the PO (yes or no, recommendation)

1. Platform key plus a separate `toolchain` setting (framework and build tool apart)? **Yes**: PlatformIO and ESP-IDF fit as strategies.
2. Order Arduino by arduino-cli, then ESP-IDF, then PlatformIO, with the A0 spike deciding if PlatformIO moves up? **Yes**.
3. Refactor first (S0), MicroPython only, before any platform? **Yes**.
4. Run T1 now and T2 and R1 to R5 only after his yes on P323 (PR #414, draft) and in its package move, not beside it? **Yes**:
   the same files, and the course of 10-19 parks P323 until his yes.
5. Proof is the flash write's MD5, a verify-flash only as an extra? **Yes**: esptool already checks the MD5 (V refuter 3), no build id.
6. D22/D34 (record and file after flash; backup offer from the facts file, both his choices): keep "no facts on the board"
   for compiled platforms (the Mac keeps the deploy by MAC address, `board_facts.py:55`)? **Yes, as a platform fact**:
   `BoardProof` says `facts_on_board: false`, and D22/D34 keep working for MicroPython. Do NOT silently override them.
   If he wants them on Arduino, the core's mklittlefs makes a small partition possible (V refuter 4): a later card.
7. Compiled platforms follow P337's rule on simulation (no gate of their own)? **Yes**.
8. Each toolchain is optional like KiCad, with size shown before the install? **Yes**: named cost, ask first.
9. Bench time for A0 (one C6, two tools, about 1 hour) after P337 and the retro? **Yes**. The walk first (P326 #418), then A0.
10. File one epic with S0 to S3 as one-sentence stories, refine only S0 and A0 now ("plans shrink with distance")? **Yes**.

## 6. Not verified here

No tool ran: no arduino-cli compile, no PlatformIO or ESP-IDF install, no C6 bench. PlatformIO's C6 support, all install sizes
except the Arduino core, the PR medians and the bench times are estimates. P323's design.md was read only through the lenses.
