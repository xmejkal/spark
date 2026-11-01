# P480 AI lens: where Claude went wrong in walk 3

> Claude made three wrong or near-wrong claims because a page or a JSON field was silent: init writes to the store, the board-only build records `built`, and a passed run tests the must lines.
> Spark already guards the third one well (`caveats`, `unnamed_must`), but it has no place for a bench result (C6) and its Mac test (C8) must say what it did not test.
> Keep C6, C8, C4 and C5, rewrite C3, and add two cards: a store-write field in every envelope, and a rule that a name is not a test.

## Findings

| # | finding | evidence | card or plan | proposal | severity |
|---|---|---|---|---|---|
| 1 | Claude told the person that init does not change the store. Init writes `projects.json`. The init page lists only project files. | diary G5, `commands/init.md` (no store line) | C4 (every store write is named) | Put a `writes` list in every envelope: file, store or project, and the line kind. Claude reads it instead of the prose. | high |
| 2 | Claude asked for a yes to a `built` write that never happened. The page says an end-to-end chain records `built`. `board_alone` returns before `parts.note_built`. | diary G27, `scripts/parts.py:963` (`note_built`), `commands/build.md` | C4 | The page and the envelope say which build kinds write `built`. A dry run lists the line. | high |
| 3 | `status: ok` and `simulation: passed` can sit beside two untested must lines. Claude read the caveat only at 08:22. The run log and the verdict say only "passed". | diary G32, `docs/guide/agents.md:904-938` (items 8 to 10) | C6 | Add the word to the verdict: "passed: starts only" when no step names a must line. Today `unnamed_must` and `caveats` carry it, and the guard works when read. | medium |
| 4 | A name is a claim. A scenario step named with the must text clears `unnamed_must`. Spark does not check that the step asserts the line. An agent can clear the list by naming. | `docs/guide/agents.md:939` | C6, C8 | A named step counts only with an `expect-pin` or `set-control` beside it. Else the look says "named, not asserted". | high |
| 5 | After the person said "it's working", no field holds that. The next look lists both must lines as untested again. An agent then has two bad choices: repeat "untested" or write the pass into a place that means something else. | diary G37, `docs/guide/agents.md:298` (`--fact-set` is for part facts) | C6 | See the C6 rewrite. | high |
| 6 | Claude wrote its own press test in the scratchpad and reported "13 checks passed". The stand-in clock is fixed at 0, so no timing was tested. Spark has no name for this result. | diary step 15, G31, `scripts/import_firmware.py:28-29` | C8 | See the C8 rewrite. The result carries `stand_in: true` and a `not_tested` list. | high |
| 7 | `look.py` gives `could-not-run`, exit 2, for "board read, no token yet" and for "board not read". The `no_token_reason` field exists but the status does not split. | diary G18, `scripts/board_look.py:336,356` | C5 | Keep the status. Add `read: true or false` to `data`, and put `no_token_reason` first in `next`. | medium |
| 8 | The look without `requirements.json` has an empty `fix` and an empty `next`. Claude had to guess the step (ask the person, then init). | diary G3, G19 | C5 | The error carries a `next` step: `/spark:init --board <id>`, with `boards.py --list`. | medium |
| 9 | The look's `next` names `--port`. The deploy page says to leave it out for one board. Claude must pick between a JSON field and a page. | diary G36, `commands/deploy.md` | row only | Drop `--port` from `next` when one board is on USB. Low cost, so file it with C5. | low |
| 10 | `parts.py <op> <project>` took the name "walk3" as a folder and made `walk3/walk3/`. Init prints a name, the idea page writes `<project>`, and nothing says which one. | diary G9, G17 | C3 | The page and `--help` say "folder". The command refuses a folder that does not exist. | medium |
| 11 | The warning "no serial monitor is wired" was a false alarm for the S3 stand-in. An agent that obeys it adds wires by hand or reports a failure that is not one. | diary G26 | C2 | Make the warning depend on the board's record, not on the converter age. Not checked in code. | medium |
| 12 | Claude copied the console-reading lines from walk 2 because the example firmware lacks them. A copy from an old project carries no proof. | diary G30 | C8 | Put the lines in spark's example, which the Mac test then runs. | medium |
| 13 | `--offer` prints a JSON line cut in the middle, and `--match` lists an unnamed stand-in part. Claude cannot parse the first and cannot explain the second. | diary G11, G12 | row only | Fix the cut line first. A broken JSON line is an AI-UX fault. Not checked in code. | medium |
| 14 | The auto-mode classifier refused `deploy.py`. The page says Claude Code does not ask. Claude did the right thing and gave the person the line. | diary G35, `commands/deploy.md:3,24` | row only | Add one sentence to the deploy page: "if the refusal comes from the host, hand the person the line". | low |
| 15 | The editor flags `machine` and `time.ticks_ms` on every firmware file. Claude cannot tell a real fault from noise. | diary G21 | C8 | Type stubs close this. Keep it as the last step of C8. | low |

## C1 to C8

- C1, spike on Wokwi and an own emulator: keep. The AI lens adds one question: how does an agent learn what a model did not test? Same answer as C8.
- C2, a board's own parts as real parts: keep. For the AI, the gain is that the limit "onboard GPIOs: not checked" goes away. Not checked deeper (architecture lens).
- C3, project name or folder: rewrite.
  - The change: `parts.py <op> <project>` takes a listed name or a folder. It prints which one it used. It refuses a missing folder with a `next` step. The page and `--help` say "folder".
  - Done when: a test passes the name "walk3" from the parent folder and gets the listed project, and a missing folder gives `could-not-run` with no new folder.
  - Drop the "remove a project" command from C3. It is a separate need (G10). Move it to its own row.
- C4, store writes named: keep, and rewrite the change to a field.
  - The change: every envelope has `writes`, a list of `{where, kind}`. `--dry-run` fills it without writing. Every page that runs such a command names it.
  - Done when: a test reads `writes` from init, `--step`, `--pick`, the build and the deploy, and an AI-UX check reads no prose for the answer.
- C5, which board is on USB: keep. Add the `read` field and a `next` step to the look (findings 7 and 8). Merge the `--port` fix (finding 9).
- C6, a place for a bench result: rewrite. See below.
- C7, hand edits: keep. A page that lists kept and overwritten files helps Claude avoid a lost hand edit. Not checked deeper.
- C8, free Mac test: rewrite. See below.

### C6 rewrite

- The change: a `bench` line in the store's history for a must line. Only a typed command in the person's terminal writes it, with the gate that `deploy.py` already uses. The line holds the must text, the word "seen", the person, the time with its zone and the image sha256.
- The look reads it only when the sha256 matches the image. It shows `bench_seen` beside `unnamed_must`. It never changes `simulation`, `caveats` or `unnamed_must`.
- The look prints "seen by the person on the bench, not by spark". Claude may relay it and may not write it.
- A passed run that names no must line says "passed: starts only" in its verdict.
- Done when: a test shows that an agent call without the person's typed yes writes nothing, that a changed image hides the line, and that `unnamed_must` stays the same after a bench line.

### C8 rewrite

- The change: `mac_test.py` runs a scenario file on spark's stand-in `machine`. It offers press, release, read a pin's level, read a PWM duty and advance the clock by a given time. The scenario is Claude's file. Spark writes no thresholds.
- The result is honest in four ways:
  - It says `stand_in: true` and names the clock: "set by the test".
  - It lists `not_tested`: real timing and debounce, real PWM output, pin levels on the real board, MicroPython limits, memory and the USB console.
  - It counts assertions. Zero assertions is `could-not-run`, exit 2.
  - It never writes `simulation`, never gives a token and never feeds `unnamed_must`.
- Done when: a test with an assertion that fails exits 1, a test with none exits 2, the output has `not_tested`, and the deploy look shows no change after a run.
- The example firmware gets the console lines (finding 12). The type stubs come last.

## New cards

- P? — agent prose claims a store write that is wrong → every envelope lists `writes` (finding 1, 2). Need: Claude must know the store effect before a yes. Done when: C4's test passes for all five commands. This is the first half of C4. Keep it as C4 or split it, and the synthesis decides.
- P? — a named scenario step counts as a test → a name needs an assertion step (finding 4). Need: an agent cannot clear `unnamed_must` by naming. Done when: a test with a name and no `expect-pin` or `set-control` step still lists the line, as "named, not asserted".

## Not checked

- I did not run any script. The facts come from the diary, the rows and the pages.
- I did not read `scripts/check_spine.py`, `board_look.py` outside the lines cited, or `deploy_gate.py`. The C6 design assumes the typed-yes gate can write a second event kind. Not checked.
- I did not check whether the stand-in can set its clock now. The diary says `ticks_ms` is fixed (G31, `import_firmware.py:28`).
- Findings 11 and 13 rest on the diary only.
- I did not read `commands/research.md`, `drawer.md`, `identify.md` or `setup.md`.
