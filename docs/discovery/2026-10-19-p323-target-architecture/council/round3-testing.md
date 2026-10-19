# Round 3: the test engineer

Nine gaps in how the design keeps spark testable. Each has a fix and a cost.

## 1. Test shape per role is not written down

S8 and S10 exist, but no rule says what each role's test looks like.

Fix: add one line per role to developing.md.

Value: plain equality. Service: built with Fakes. Strategy: the contract mixin (gap 3). Adapter: injected `run` returns canned output. Operation: golden envelope and exit equals `EXIT_FOR[status_of]`. Door: one smoke test that spawns the script, the rest call `main(argv)` in process.

Cost: half a page.

## 2. Where Fakes live

`tests/fakes.py` holds 7 Fakes. Nothing stops one drifting from its real class.

Fix: keep Fakes in `tests/fakes.py`, and split by area (`tests/fakes/bench.py`) past 400 lines. Each Fake passes its
Strategy's contract mixin, so drift fails a test. Cost: the mixins, one file split later.

## 3. Contract tests have no shape

"One contract test on the real class and its Fake" proves little for a second board or platform.

Fix: a mixin per Strategy, such as `FlasherContract`, with the shared cases (missing tool gives `ToolMissingError`,
a refusal never writes, every problem has a code). Each implementation is a `TestCase` that sets `make()`. The `FirmwarePlatform` contract loops over
every board record in `boards/` plus a no-platform record, so criterion 6 stays true as boards arrive. New rule S14:
every class with the Strategy role has a mixin of that name. Cost: about 40 lines per Strategy, about 240 in all,
landing with each area's move.

## 4. Goldens can hide a regression

A bulk `--update` turns a bug into the new truth.

Fix:
- One file per Operation and outcome in `tests/golden/`.
- Only `python3 tests/golden.py --accept <op>` updates, one file, printing the diff. No bulk flag.
- Times and temp paths become placeholders.
- The hook fails a move PR that changes a golden (criterion 8).

Cost: about 80 lines and one hook rule.

## 5. A move can leave mutation rows quietly meaningless

A hand edit of 188 bench rows can retarget one to a line that guards nothing.

Fix: `mutate.py --retarget OLD NEW` rewrites `file` only, never `find`, and refuses when the `find` count is not 1.
Each move PR prints "rows N, caught N". A row whose `find` text changes is a new row with a new reason. Cost: about
30 lines.

## 6. Suite speed

110 s today. The new test parses every file with `ast`.

Fixes:
- Parse each file once and share the tree among the rules. Free if built so in slice 1b.
- Add suite seconds to `tools/measure.py`. When it passes 150 s, shard the suite across processes in the hook. Cost
  about 25 lines, built only at the trigger.

Goldens and mixins run in process, so they are cheap and the hook should stay under 2 minutes.

## 7. Hardware: what stays manual

The design is silent on it. Fakes cannot show a real ESP32 boots the image.

Fix: list in developing.md what only the bench proves: flash write and read back, the serial console, a button press,
the USB permission prompt. A test never claims them. With no
board plugged in the answer is `could-not-run` or `skipped` with a code such as `no_board`, never a pass. Cost: one
page.

## 8. The architecture test must fail clearly

Fixes:
- Each line reads `S4 scripts/spark/design/x.py:12 imports spark.bench (2.2: design may not import bench)`. It names
  the rule, the file, the line and the reason.
- A stale baseline line reads `S6|scripts/parts.py|_op_list is 52, baseline 71: run --lower`.
- It prints at most 20 breaches, then a count. `--lower` refuses to raise a value.
- Every rule has a planted-breach case. Slice 1b plants five. S6, S7, S11, S12 and S14 need theirs.

Cost: about 40 lines beyond the 290 planned.

## 9. Patches that pass and test nothing

A move retargets 336 patches by hand. If the old module still imports the name, a stale `mock.patch("old.name")`
passes and checks nothing.

Fix: a guard test that every `mock.patch` target resolves to the module that defines the name. Cost: about 40 lines.

## Order

Gaps 8, 9, 1, 7 in slice 1b. Gaps 3, 4, 5 with slice 2. Gap 6 at its trigger.
