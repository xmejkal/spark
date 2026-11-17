# Dry change: hand actions when a project changes in the middle

Every spark command ran with `SPARK_HOME=$S/store` (runs A and B) or `SPARK_HOME=$S/store2` (runs C and D, see below). Two `--help` calls at the very start (`parts.py --help`, `flow.py --help`) ran with no `SPARK_HOME`; they print text and write nothing. No board, no simulation, no web. `$S` is a scratch folder from `mktemp -d`.

Scratch setup, not counted: `$S/amp` and `$S/button` are copies of the two walk projects. `$S/store2` is a second copy of the real store, made after run C's first `--pick` was refused (see DC-14).

## Findings

Counts

- DC-1 · Run A (amp copy: add `vl6180x-breakout` on I2C through a need): 1 hand action · E · `$S/amp`: `check_spine.py requirements.json --keep .` printed `traces differ: board.tsx ... delete it to have it regenerated`; the rest of the run (need, match, pick, requirements, build) needed none · supports only: the count of A
- DC-2 · Run B (amp copy, after A: drop the same need): 2 hand actions · E · `parts.py --requirements .` printed `kept, not from a pick: vl6180x-breakout` and left it in `requirements.json`; then the build printed `traces differ: board.tsx` again · supports only: the count of B
- DC-3 · Run C (button copy: second button as a new need `button2`, `tactile-button`): 0 hand actions · E · `parts.py --needs-set`, `--pick button2=tactile-button`, `--requirements`, `check_spine.py ... --keep .` all exited 0 with no refusal and no `traces differ` (the project was board-only, so it had no `board.tsx`) · supports only: the count of C
- DC-4 · Run D (button copy, after C: replace the pick of `button2` with `cjmcu-111-rotary-encoder`): 2 hand actions · E · `parts.py --requirements .` printed `kept, not from a pick: tactile-button`; then the build printed `traces differ: board.tsx` · supports only: the count of D
- DC-5 · Total over the four runs: 5 hand actions (A 1, B 2, C 0, D 2) · E · DC-1 to DC-4 · supports only: the total

Hand actions, each with the output that made it necessary

- DC-6 · A1: delete `board.tsx` with `rm`, then run the build again. The first build after the part was added left the old `board.tsx` in place and said `traces differ: board.tsx (... if you did not edit it, delete it to have it regenerated)`, listing 10 trace lines (3 `only in yours`, 7 shown `only in this build`, `2 more not shown`). The output names the deletion; it does not name the build as the step after it. Proposed class: a command fix, because the build already reads `board.tsx`'s traces and knows it differs, so it could do the regeneration (or ask) in the same run when the person never edited the file; the one fact it lacks is whether the person edited it, and that is a fact only the person has, so the command could ask once · E · command: `SPARK_HOME=$S/store python3 scripts/check_spine.py requirements.json --keep .` (in `$S/amp`), line `traces differ: board.tsx ...`; after `rm board.tsx` the rebuild printed `wrote board.tsx` and `board.tsx` sha256 changed from 838a6a27... to 542e8eda... · supports only: that A1 is needed, and its proposed class
- DC-7 · B1: edit `requirements.json` to remove `vl6180x-breakout` from `parts`. `parts.py --needs-drop . distance` printed `requirements.json still lists vl6180x-breakout: run parts.py --requirements . or edit the file, then build.` Running `parts.py --requirements .` (dry run and real) then printed `kept, not from a pick: vl6180x-breakout` and exited 0 with `unchanged requirements.json`: the command the first output named did not do what it said it would. Only the edit removed it. Proposed class: a rule that spans phases, because the needs phase made the fact "this part was picked for need X and the need is gone" and the requirements phase must read it; today `--requirements` keeps every entry no pick explains (by design, so hand-added parts stay) and cannot tell a part once picked from a part added by hand · E · commands: `parts.py --needs-drop . distance`, `parts.py --requirements .`; file `requirements.json` before and after (sha256 211bacda... to 316b1d96..., the second equal to the start) · supports only: that B1 is needed, and its proposed class
- DC-8 · B2: delete `board.tsx` again and rebuild. The build after B1 printed `traces differ: board.tsx` with 10 `only in yours` lines naming the removed part's traces. Proposed class: a command fix, same reason as DC-6 · E · command: `check_spine.py requirements.json --keep .` in `$S/amp`; after `rm`, `wrote board.tsx`, sha256 back to 838a6a27... (the start's) · supports only: that B2 is needed, and its proposed class
- DC-9 · D1: edit `requirements.json` to remove `tactile-button`. After `parts.py --pick . button2=cjmcu-111-rotary-encoder` printed `released: 6-6-tactile-buttons-a-bag — no pick of this project explains it`, `parts.py --requirements .` printed `kept, not from a pick: tactile-button` and wrote `parts tactile-button, cjmcu-111-rotary-encoder`. The pick step released the hold on the old part, and the requirements step then kept the old part anyway. Proposed class: a rule that spans phases, same reason as DC-7 (the pick phase knows the old part was a pick that was replaced; the requirements phase does not read that) · E · commands: `parts.py --pick . button2=cjmcu-111-rotary-encoder`, `parts.py --requirements .` · supports only: that D1 is needed, and its proposed class
- DC-10 · D2: delete `board.tsx` and rebuild. The build printed `traces differ: board.tsx` (2 `only in yours` lines for `TactileButton`, 4 `only in this build` for the encoder). Proposed class: a command fix, same reason as DC-6 · E · command: `check_spine.py requirements.json --keep .` in `$S/button`; after `rm`, `wrote board.tsx` · supports only: that D2 is needed, and its proposed class
- DC-11 · Not counted, in A to D: the person must also re-run the commands in order after the needs are set (`--match`, `--pick`, `--requirements`, the build). `--needs-set` printed `set distance: ...` and no next step. These commands are named only in commands/idea.md (the M, C and L steps) and in the stale lines of `flow.py show` (`stands at: parts`, then an offer `requirements`, then `build`). By the brief's rule they are not hand actions · E · `parts.py --needs-set . $S/needsA1.json` output has no `next`; commands/idea.md "M" and "L" sections · supports only: the exclusion

Other observations

- DC-12 · Statuses that were untrue: after B's `--needs-drop`, `flow.py show` said `✓ requirements: requirements.json` and `✓ build ... ok` while `requirements.json` still listed the dropped part (the only sign was the `needs-drop` output line). Same in D after `--requirements` rewrote the file with the replaced part still in it: `✓ requirements`, and `stands at: simulate` (B) / `deploy` (D) · E · `flow.py show --project $S/amp` after `--needs-drop`; `flow.py show --project $S/button` after the D `--requirements` · supports only: this status was read as ok while the file listed a part no pick gives
- DC-13 · Build read `ok` and `breadboard.md` read current while the kept `board.tsx` was out of date: after the first A build, `flow.py show` printed `✓ build ... ok` and `✓ breadboard`, and `board.tsx` sha256 was still 838a6a27... The `traces differ` line was in the build's own output only, not in `flow.py` or `.spark/build.json` as far as `flow.py show` printed · E · `flow.py show --project $S/amp` after the first A build · supports only: the status line did not mention the stale `board.tsx`
- DC-14 · One refusal came from my own run, not from the change: in C, `parts.py --pick . button2=tactile-button` with `store` exited 1 with `refused, so nothing was written: firebeetle2-esp32s3 — 3 owned, held by amp, p581-sound-joystick, smartbin-local — 1 picked here`. Run A had reserved the third board for the amp copy in the same store copy. I made `$S/store2` from the real store and ran C and D there. The refusal output named a fix (`--drawer-set` with a file, after a dry run). Not counted · E · `parts.py --pick . button2=tactile-button` with `SPARK_HOME=$S/store`, exit 1 · supports only: why C and D use `store2`. The first, refused `--pick` was followed by a `parts.py --requirements .` that wrote `unserved: button2`; the later `--requirements` rewrote it
- DC-15 · Pins that moved (signals kept across a change): in A, `I2S_LRC` 11 to 12, `I2S_DIN` 12 to 13, `AUDIO_SHUTDOWN` 13 to 14; added `SDA = 1`, `SCL = 2`, `TOF_INT = 11`. In B they went back to the start values (the file's non-comment text equals the one before A). In C: added `BUTTON = 38`, `BUTTON_PULL = "up"`, no kept signal moved. In D: `BUTTON`/`BUTTON_PULL` replaced by `ENC_A = 38`, `ENC_A_PULL`, `ENC_B = 11`, `ENC_B_PULL`; no kept signal moved. The build said so for the pins that A moved as jumper lines (`Move the jumper from board D11: it now goes to ...`) · E · `diff` of `firmware/pins.py` (comments cut) before and after each build · supports only: the pin facts
- DC-16 · Firmware names: the `firmware/main.py` of each copy uses names that the new `pins.py` still has, in all four runs (amp: `AUDIO_SHUTDOWN I2S_BCLK I2S_DIN I2S_LRC ONBOARD_LED`; button: `ONBOARD_BUTTON ONBOARD_BUTTON_ON ONBOARD_LED ONBOARD_LED_ON`). No firmware file changed. No firmware names a removed signal, so no command had to say so. The firmware does not use `SDA`, `SCL`, `BUTTON` or `ENC_*`; no command said that the firmware lacks them. The build's last line `next: ... look.py ... — first write firmware/main.py from pins.py` printed in every run, including where `firmware/main.py` exists · E · `/usr/bin/grep -o "pins\.[A-Z_0-9]*" firmware/main.py | sort -u` against the names in `firmware/pins.py`; build output last line · supports only: the firmware-name check. Writing firmware that reads the new pins is not counted as a hand action (it is the conversation's job, by the AGENTS.md principle), and I did not write any
- DC-17 · Starting states: amp copy had `requirements.json` (board, `max98357a-dfr0954`, `speaker-terminal`), `board.tsx`, `breadboard.md`, `firmware/pins.py`, a build `ok, simulation: skipped` from 2026-11-16, and no `firmware/main.py`. Button copy was board-only (`board_only: true`, build stages `skipped`), had `firmware/main.py` and `firmware/pins.py`, and no `board.tsx` and no `breadboard.md`. Starting sha256: amp `requirements.json` 316b1d96..., `pins.py` 0f22736c..., `board.tsx` 838a6a27..., `breadboard.md` ac84591d..., `.spark/needs.json` f480a66b...; button `requirements.json` dc20f456..., `pins.py` 8a688210..., `main.py` 6f5f266f..., `.spark/needs.json` 6177ccf3... · E · `shasum -a 256` · supports only: the starting state
- DC-18 · Getting to the start (not counted in A to D): 1 hand action on the amp copy: write `firmware/main.py` by hand (the project had none; the start asks for "built, with firmware"). The button copy needed none; I re-ran `check_spine.py requirements.json --keep .` there, which wrote the same `pins.py` (sha256 8a688210... both times) and `sim/` and no `board.tsx` · E · `flow.py show --project $S/amp`: `○ firmware: not started, no firmware/main.py yet` · supports only: the start count
- DC-19 · Wordings: the first need wording for A, `sense` / `distance`, led to `vl6180x-breakout` (owned 1, library) in `parts.py --match`. No failed wording; 0 hand actions of the kind "had to know" · E · `parts.py --match .` output under `distance — sense / distance` · supports only: that no wording hunt happened
- DC-20 · Needs file: `parts.py --needs-set` takes the whole list ("every write sets, never adds", `parts.py --help`), so the file I wrote repeated the three existing needs without picks plus the new one. The dry run showed only the new need as a change (`would set distance: does null → "sense"; what null → "distance"`) and the existing picks stayed. Writing that file is what commands/idea.md step 3 tells; not counted · E · `parts.py --needs-set . $S/needsA1.json --dry-run`; `parts.py --needs .` afterwards · supports only: the exclusion
- DC-21 · After B and after D the person is not told whether the removed part's breadboard parts, resistors or jumpers come out: the build said so (`changed: Take out Vl6180xBreakout.`, `Take out R1 ...`, etc.), so this is said · E · `$S/buildB.txt` lines starting `changed:` · supports only: that the bench changes were named

## What you could not check, and why

- A firmware that reads a signal the new `pins.py` no longer has: neither `main.py` used one, so I did not see whether `check_spine.py`, `flow.py` or `look.py` says so (`look.py` is not allowed here). In B, `--needs-drop` printed `If the firmware imported its signal, run import_firmware.py`; I did not run `import_firmware.py` (not needed, the firmware used no such signal).
- Whether the hand-written `firmware/main.py` for the amp copy is a fair start: I wrote a stub that only names pins; a real firmware that reads the sensor would show more hand edits, which this test does not count by the brief's rule.
- Runs are one pass in one order. Picks of other candidates (a part with no record, a board with a different footprint state) were not tried. Run D replaced a part with a rotary encoder that has no drawn breadboard (`no drawn breadboard: no Wokwi pin positions for wokwi-ky-040 ...`); a replacement with a drawn breadboard might behave differently.
- Whether the real store and a real second project would have refused C the same way as in DC-14: I used a second store copy to avoid it.
- Whether `traces differ` appears when the person did edit `board.tsx`: I did not edit it; every `rm board.tsx` assumed it was not edited, as the output says.

## Questions for the decider

- Does a hand action that the output itself names (A1, B2, D2: `delete it to have it regenerated`) count the same as one nothing names? · it decides whether the counts are 5 (as here) or 2 (only B1 and D1, where the command named a step that did not do what it said)
- Is writing the firmware that reads a new or changed pin part of "the change" for this test? · it decides whether a sixth kind of action (firmware for the new sensor, the second button, the encoder) enters the counts; here it is out, by the brief's rule

## Searches

- none

## Commands run

All in `$S/amp` unless noted; `P` is `scripts/parts.py`, `F` is `scripts/flow.py`, `C` is `scripts/check_spine.py` of the repository. Each has `SPARK_HOME=$S/store` (A, B) or `SPARK_HOME=$S/store2` (C, D) inline. Exit code after each.

Start (not counted)
1. `F show --project $S/amp` 0; `F show --project $S/button` 0
2. hand: write `$S/amp/firmware/main.py` (stub naming pins)
3. `C requirements.json --keep .` in amp 0; in button 0
4. `F show --project` for both 0

Run A (amp)
5. `P --needs .` 0
6. hand: write `$S/needsA1.json` (4 needs, no picks), as commands/idea.md says
7. `P --needs-set . $S/needsA1.json --dry-run` 0; `P --needs-set . $S/needsA1.json` 0
8. `P --needs .` 0; `F show --project .` 0; `P --match .` 0 (vl6180x-breakout offered under `distance`)
9. `P --pick . distance=vl6180x-breakout --dry-run` 0; `P --pick . distance=vl6180x-breakout` 0
10. `P --requirements . --dry-run` 0; `P --requirements .` 0; `F show --project .` 0
11. `C requirements.json --keep .` 0 (`traces differ: board.tsx`)
12. hand A1: `rm board.tsx`
13. `C requirements.json --keep .` 0 (`wrote board.tsx`); `F show --project .` 0

Run B (amp)
14. `P --needs-drop . distance --dry-run` 0; `P --needs-drop . distance` 0
15. `F show --project .` 0
16. `P --requirements . --dry-run` 0; `P --requirements .` 0 (`kept, not from a pick: vl6180x-breakout`, `unchanged requirements.json`)
17. hand B1: edit `requirements.json`, remove `vl6180x-breakout`
18. `F show --project .` 0; `P --requirements . --dry-run` 0 (shows 2 parts, no kept line); `C requirements.json --keep .` 0 (`traces differ: board.tsx`)
19. hand B2: `rm board.tsx`
20. `C requirements.json --keep .` 0 (`wrote board.tsx`); `F show --project .` 0

Run C (button)
21. hand: write `$S/needsC.json` (4 needs, no picks)
22. `P --needs-set . $S/needsC.json --dry-run` 0; `P --needs-set . $S/needsC.json` 0 (`store`)
23. `P --match .` 0; `F show --project .` 0
24. `P --pick . button2=tactile-button --dry-run` 0 with `store` (shows `not written:` lines and `refused`); `P --pick . button2=tactile-button` exit 1 (refused, DC-14); `P --requirements .` 0 (`unserved: button2`)
25. `cp -R` the real store to `$S/store2`
26. `P --pick . button2=tactile-button --dry-run` 0 (`store2`); `P --pick . button2=tactile-button` 0
27. `P --requirements . --dry-run` 0; `P --requirements .` 0 (`board_only removed`)
28. `F show --project .` 0; `C requirements.json --keep .` 0; `F show --project .` 0

Run D (button, `store2`)
29. `P --pick . button2=cjmcu-111-rotary-encoder --dry-run` 0; `P --pick . button2=cjmcu-111-rotary-encoder` 0
30. `F show --project .` 0; `P --requirements . --dry-run` 0; `P --requirements .` 0 (`kept, not from a pick: tactile-button`)
31. hand D1: edit `requirements.json`, remove `tactile-button`
32. `C requirements.json --keep .` 0 (`traces differ: board.tsx`)
33. hand D2: `rm board.tsx`
34. `C requirements.json --keep .` 0 (`wrote board.tsx`); `F show --project .` 0

## Cleanup

`rm -rf $S` is run as the last step; the `ls` that shows it gone follows below.

`rm -rf $S` ran. `ls -d $S` printed: `ls: $S: No such file or directory` (the scratch folder, both store copies and both project copies are gone). The real store and the spark-walks folder were not written by any command.
