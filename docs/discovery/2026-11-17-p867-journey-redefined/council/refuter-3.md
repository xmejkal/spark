# Refuter 3: the count of the dry change (council/dry-change.md)

Ran 2026-11-17, 09:21:38 to 09:25:55 (Europe/Prague). Runs A, B, C and D repeated on scratch copies; every spark
command had `SPARK_HOME=$S/store` (amp) or `SPARK_HOME=$S/store2` (button) inline. No board, no simulation, no web.
This report decides nothing.

## 1. The runs repeated

Start, not counted: I wrote a stub `$S/amp/firmware/main.py` that imports `pins` and uses `I2S_BCLK`, `I2S_LRC`,
`I2S_DIN`, `AUDIO_SHUTDOWN`, `ONBOARD_LED`, then built. Start sha256: `requirements.json` 316b1d96..., `board.tsx`
838a6a27..., `pins.py` 0f22736c... (equal to DC-17).

Run A (amp, add `distance` = `vl6180x-breakout`).

- `--needs-set` printed only `set distance: does null → "sense"; what null → "distance"`. No next step.
- `flow.py show` after it: `◐ parts: partly done, 3 of 4 needs picked`, `↻ requirements: out of date, requirements.json differs from what the picks give`, `✓ build`, `stands at: parts`.
- After `--pick`: `stands at: requirements`. After `--requirements` (`wrote requirements.json: ... parts max98357a-dfr0954, speaker-terminal, vl6180x-breakout`): `↻ build: out of date, requirements.json changed after the build`, `↻ breadboard: out of date`, `stands at: build`.
- First build, exit 0: `left alone: board.tsx (delete it to have it regenerated)`, then `traces differ: board.tsx (it joins pins differently from the board this build made from the requirements, so do not wire or build from it: if you did not edit it, delete it to have it regenerated; if you did, carry this build's pins into it)`, 3 `only in yours`, 10 `only in this build`, `2 more not shown`. The same build printed `wrote dist`, `wrote breadboard.md`, 13 `changed:` lines, `wrote firmware/pins.py`, `wrote page.html`, `wrote sim`, `the chain runs end to end`.
- `flow.py show` after that build: `✓ build: the last build, 2026-11-17T09:22:48+01:00: ok`, `✓ breadboard: breadboard.md`, `stands at: simulate`, with `board.tsx` still 838a6a27....
- `rm board.tsx`, build again, exit 0: `wrote board.tsx` (542e8eda...), and no `changed:` line.

Run B (amp, drop `distance`).

- `--needs-drop . distance` printed: `dropped distance: sense distance`, `released 1 of 1: vl6180x-rangefinder — its need is dropped`, `requirements.json still lists vl6180x-breakout: run parts.py --requirements . or edit the file, then build. If the firmware imported its signal, run import_firmware.py.`
- `flow.py show` after it: `✓ needs: 3 need(s)`, `✓ parts: 3 of 3 needs picked`, `✓ requirements: requirements.json`, `✓ build ... ok`, `✓ breadboard`, `stands at: simulate`.
- `--requirements .`, exit 0: `unchanged requirements.json: ... parts max98357a-dfr0954, speaker-terminal, vl6180x-breakout` and `kept, not from a pick: vl6180x-breakout`. `flow.py show` unchanged.
- A build without the edit (my addition): exit 0, `the chain runs end to end`, the sensor still in it, `pins.py` equal to run A's. No line named the dropped part as a problem.
- After the edit by hand (sha256 back to 316b1d96...): `↻ build: out of date`. Build, exit 0: `traces differ: board.tsx`, 12 `only in yours`, 3 `only in this build`, 11 `changed:` lines (`Take out Vl6180xBreakout.` ...). `pins.py` equal to the start.
- `rm board.tsx`, build again: `wrote board.tsx` (838a6a27..., the start's). `breadboard.md` lost its 11 change lines and now reads `- Nothing to change on the bench.`

Runs C and D (button, fresh `$S/store2`). C: no refusal, `wrote board.tsx`, no `traces differ`. D: `--pick . button2=cjmcu-111-rotary-encoder` printed `released: 6-6-tactile-buttons-a-bag — no pick of this project explains it`; `flow.py show`: `↻ requirements: out of date`; `--requirements .` printed `wrote requirements.json: ... parts tactile-button, cjmcu-111-rotary-encoder` and `kept, not from a pick: tactile-button`; `flow.py show`: `✓ requirements`. A build without the edit: exit 0 with both parts. After the edit: `traces differ: board.tsx` (2 `only in yours`, 4 `only in this build`), 5 `changed:` lines; after `rm` and a rebuild `breadboard.md` reads `- Nothing to change on the bench.`

Cleanup: `rm -rf $S` ran; `ls -d $S` printed `ls: $S: No such file or directory`. The real store's folder date (2026-11-16 18:57) and the two walk projects' `requirements.json` dates (2026-11-16) are older than this run.

## 2. The five counted hand actions

- R3-1 · A1 (delete `board.tsx`): partly. The line is real and it names the deletion. The action is not needed for the build: without it the build exits 0 and writes `dist/`, `breadboard.md`, `firmware/pins.py`, `page.html`, `sim/` from this build's own board. Only the kept `board.tsx` is stale. No script under `scripts/` reads the project's `board.tsx` (searched); a person does, with `npx --no tsci build board.tsx` (commands/build.md:167-168 says that builds the old pins into `dist/`). So: stale, wrong only for a person who wires or builds from that file. Told action, a delete by hand, counted by the definition.
- R3-2 · B1 (edit `requirements.json`): holds. Needed: without it the build passes with the dropped sensor on the board and every status reads `✓`. Told: `--needs-drop` named two ways, `run parts.py --requirements . or edit the file`; the first does nothing (`unchanged`), the second is the edit. Counted by the definition.
- R3-3 · B2 (delete `board.tsx`): partly, same as R3-1.
- R3-4 · D1 (edit `requirements.json`): holds. Needed: the build passes with both parts. Not told: no output of `--pick` or `--requirements` says to edit; `kept, not from a pick: tactile-button` states a fact only. This one is both an edit and a thing the person had to know.
- R3-5 · D2 (delete `board.tsx`): partly, same as R3-1.
- R3-6 · The definition was applied the same way each time: every edit or delete by hand was counted, told or not; no rerun of a command was counted. The count of 5 holds as a count of edits and deletes. 3 of the 5 do not change what the build makes.
- R3-7 · DC-6's sentence "it does not name the build as the step after it" holds: the line says `delete it to have it regenerated` and names no command.
- R3-8 · DC-21 ("this is said") is refuted in part: the `changed:` lines are in the first build's output only. See R3-9.

## 3. Hand actions the run missed

- R3-9 · Missed, seen in B and D, and in A by its signs: the rebuild that the deletion calls for replaces the sheet's change list with `- Nothing to change on the bench.` (diff of `breadboard.md` before and after the second build: 11 lines lost in B, 5 in D; in A the second build printed no `changed:` line and `breadboard.md` changed from 04ca884a... to fe2d9ad0...). The list compares with the last sheet, not with what is wired. In my run D the list after the edit said `Take out the jumper from board D12 to the row of Cjmcu111RotaryEncoder GB`, a jumper that only an earlier sheet held. The person has to know to act on, or copy, the first build's `changed:` lines before building again. No output says so. By the definition this is "a thing the person had to know that no output said", met at the desk, in a file, with no board.
- R3-10 · DC-11 (the order after `--needs-set`, not counted): holds for A, C and D. `--needs-set` names no next step, but `flow.py show` after each step named the right place (`stands at: parts`, `requirements`, `build`). The agent called these lines stale; in A they were true. In B the order came from the drop's own line (`... then build`), while `flow.py show` said `stands at: simulate`.
- R3-11 · DC-15 (moved pins of kept signals): the pin facts hold (`I2S_LRC` 11 to 12, `I2S_DIN` 12 to 13, `AUDIO_SHUTDOWN` 13 to 14). No output line holds any of these three names or says a signal moved (searched the build's output). The bench moves are named by pad and part pin: `Move the jumper from board D11: it now goes to the row of Max98357aDfr0954 DIN (it went to the row of Max98357aDfr0954 SD)`, and for D12 and A5, and `Run a jumper from board D10 to the row of Max98357aDfr0954 SD`. So a person with a wired breadboard need not compare two files, as long as R3-9 did not erase the list.
- R3-12 · Firmware after a moved pin: `main.py` imports names, all still in `pins.py`, so no rewrite; the board needs the new `pins.py` flashed. No output said so. `flow.py show` kept `· firmware: firmware/main.py written 2026-11-17T09:22:09+01:00` through A and B; its firmware reader has no out-of-date status (scripts/spark/flow/phase_readers.py:223-234; the status exists only for requirements, build and breadboard, lines 175, 204, 219). The build's last line `first write firmware/main.py from pins.py` printed while the file existed. Whether a deploy step says the board holds an old pin map: not checked, no board.
- R3-13 · DC-12 and DC-13 hold as observed (lines in part 1; `.spark/build.json` holds status, stages, missing facts and the requirements' sha256, and no `traces differ` entry). They are not further hand actions: each is the same knowledge as B1, D1 or A1. They do make B1 and D1 "had to know" for a person who reads `flow.py show` and not the command's output.
- R3-14 · Bench actions that "no board" removed, named and not counted: move the jumpers of the moved pins; take out or put in the part, its pull-ups and jumpers; flash the new `pins.py` and firmware; the order of flashing and wiring; a board that still runs the old image on the old pins; the scan that confirms the new part answers at 0x29.

## 4. The classes

- R3-15 · Delete `board.tsx`. For "a command fix": the build writes the file and reads it again in the next build; scripts/spark/build/kept_files.py:318 tells its own `pins.py` by its header line and rewrites it, and `kept_into` (lines 97-104) has no such test for a `.tsx`. A header with a hash of the body would let the same command know the file is untouched. For "a rule that spans phases": the second refuter's reading, a record written in one build and read in a later one. Both ends are the build, so the evidence supports a command fix. The proposed class holds.
- R3-16 · Edit `requirements.json`. For "a rule that spans phases": `_merge_parts` (scripts/spark/design/need_requirements.py:129-161) keeps every entry no pick explains, "added by hand, or left by a pick since changed", and the file holds no origin per entry, so `--requirements` alone cannot tell the two apart. For "a command fix": the command that makes the change knows the part at that moment. `--needs-drop` printed its id (`requirements.json still lists vl6180x-breakout`; scripts/spark/idea/drop_need.py:27-28, need_requirements.py:23) and leaves the file alone by design. `--pick` holds the needs before and after (scripts/spark/design/pick_parts.py:74, `plan_pick`) and prints the released hold, but does not read `requirements.json`. So B1 can be closed inside one command from what it already reads; D1 needs `--pick` to read the next phase's file, or an origin in the file. The evidence supports "a command fix" for B1 and is open for D1. The agent's reason for B1 ("cannot tell") is true of `--requirements` and untrue of `--needs-drop`.
- R3-17 · The lost change list (R3-9). For "a command fix": the build could keep the list when the requirements' sha256 equals the last build's (it is in `.spark/build.json`). That covers the rebuild after a deletion only. For "a rule that spans phases": the right baseline is what is wired, a fact of the bench phase that the build does not read. The evidence supports the rule for the general case and the command fix for the three cases seen.

## 5. The pass line

- R3-18 · On the run's own 5 counted actions: lowest 0 (strict: each has a fix inside the command that makes or meets the change), highest 2 (loose: B1 and D1 need an origin that the parts phase makes and the requirements phase reads). "At least 3" is not met under any fair reading of these 5.
- R3-19 · With the missed action R3-9 counted once per run where it happened (A, B, D): lowest 0, highest 5 (2 and 3). "At least 3" is then met only under the loose reading of R3-9, and the result rests on one question the run's brief did not settle: whether a sheet that reads `Nothing to change on the bench` is a hand action of the desk (counted) or of the bench (left out by "no board").
- R3-20 · What the test cannot show: anything at the bench (R3-14); a board whose image is older than its pin map; a second board model, a part with no record, a project with a hand-edited `board.tsx` or a hand-added part of the same id as a pick; a person, since an agent reads every output line and a person reads `flow.py show`, which said `✓` in the cases of DC-12 and DC-13; the actions of writing firmware for the new part, left out by the brief's rule.

## What I could not check, and why

- What `look.py` or `deploy.py` says after a pin moved: no board is allowed.
- Run A's change list in `breadboard.md` before the second build: I kept its hash, not its text; B and D show the text.
- Why `dist/board/circuit.json` differs between two builds of the same requirements (8509957d... and c040de27...): not followed.
- A `board.tsx` the person did edit: not tried.

## Searches

- none

Commands, in order, each with `SPARK_HOME=$S/store` (amp) or `SPARK_HOME=$S/store2` (button) inline, all exit 0: `flow.py show --project $S/amp`; `check_spine.py requirements.json --keep .`; `parts.py --needs-set . $S/needsA1.json --dry-run` and without; `parts.py --needs .`; `parts.py --match .`; `parts.py --pick . distance=vl6180x-breakout`; `parts.py --requirements .`; the build; `rm board.tsx`; the build; `parts.py --needs-drop . distance`; `parts.py --requirements .`; the build; the edit; the build; `rm board.tsx`; the build; `flow.py show` after each step. Button: the build; `parts.py --needs-set . $S/needsC.json`; `parts.py --pick . button2=tactile-button`; `parts.py --requirements .`; the build; `parts.py --pick . button2=cjmcu-111-rotary-encoder`; `parts.py --requirements .`; the build; the edit; the build; `rm board.tsx`; the build. Code read with `/usr/bin/grep` and `sed`. Last: `rm -rf $S`, `ls -d $S`.
