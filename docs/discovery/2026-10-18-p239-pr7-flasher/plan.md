# P239 PR 7: the flasher seam

> TL;DR: esptool's commands, its offset and its boot hint leave deploy.py and live in `scripts/flasher.py`, as a
> `Flasher` base (a Strategy) and `EsptoolFlasher`. `deploy.py --dry-run` prints the same bytes. Nothing is built for
> Arduino or PlatformIO: the base only names where they plug in. Card [#238](https://github.com/xmejkal/spark/issues/238),
> brief item 3 of [P218's finish](../2026-10-17-p218-finish/brief.md).

## Council

Round 1 (2026-10-18): tech lead (Sonnet) and the refuter (Opus). They found no broken test, doc link or mutation anchor
(the refuter scanned every table: none names the moved lines), no import cycle, and agreed the bytes can stay equal. What
round 1 changed:

- One `BOOT_HINT`, on `EsptoolFlasher`; the base holds `""`, and deploy.py omits the `: hint` tail when it is empty.
  `board_look` uses `EsptoolFlasher.BOOT_HINT`; its PR 7 comment goes. developing.md:247 is edited.
- The helper is `build_esptool_prefix(tool, port=None, chip=None)` (it returns a prefix, not a command), `--chip` before
  `--port`. `test_board_look.py:194` pins the reader's line, `test_flasher.py` pins the order.
- The ast rule is a denylist of exact string constants (`erase_flash`, `write_flash`, `flash_id`, `--chip`, `0x0`),
  docstrings and EPILOG/WATCH skipped, modelled on `test_board_look.py:451-471`. The `cmp` is the real guard.
- Finding 1: both reviewers say not PR 7. The tech lead put it in PR 8, the refuter says PR 8 must print the same lines,
  so a retry or pause does not fit there: it gets its own bug card (verdict below).

Round 2 (2026-10-18): tech lead and PO assistant (Sonnet). What it changed:

- No `choose_flasher` (PO assistant, over the refuter's round 1 point). It was a name lookup with an error path, a first
  step to other platforms, and it would change behaviour: a non-esptool `flasher` tool would fail at plan time, where it
  fails today in the look. deploy.py calls `flasher.EsptoolFlasher(tool, chip)`; PR 8's `FirmwarePlatform` is the one
  place that will choose. deploy.py then names a class, and holds no esptool string. The reader keeps its own check.
- The empty-hint tail is tested with a second Flasher subclass; the esptool failure line is pinned in full.
- The ast rule skips docstrings and the exact names `EPILOG` and `WATCH`. `commands/build.md` repeats the hint: checked.
- Build order: baseline already taken; `test_flasher.py` first; then `flasher.py` and `board_look`; then deploy;
  developing.md last.

**Needs the PO:** nothing blocks PR 7. Two bench findings become two separate cards (verdicts below): say yes or no.
This PR is a refactor that PR 8 and `--json` need, with no change a user sees.

## What moves

| Now | Becomes |
|---|---|
| `deploy.IMAGE_OFFSET`, `deploy.ERASE`, `deploy.WRITE` (deploy.py:50-53) | `EsptoolFlasher.IMAGE_OFFSET`, `.ERASE`, `.WRITE` |
| `deploy.flash_commands(flasher, chip, image, port)` | `EsptoolFlasher(tool, chip).build_commands(image, port)` |
| `board_look.BOOT_HINT`, used by `PortFinder`, `EsptoolReader` and deploy.py | `EsptoolFlasher.BOOT_HINT`; deploy reads `planned.flasher.BOOT_HINT` |
| `tools.command_for(tool) + ["--port", port]` in `EsptoolReader.read` | `flasher.build_esptool_prefix(tool, port=None, chip=None)`, shared with the reader |

Not moved, because PR 8 moves it: the run loop in `main`, `DeployPlan`'s other fields, the board log, the store record.
`--help`, exit codes and the store record do not change. `--help` still names esptool in prose: it is the person's tool.
"deploy.py holds no esptool text" means no esptool command word, offset or hint in code.

## Classes

```
Flasher  <<Strategy>>                          how an image goes onto a board
  BOOT_HINT = ""                               what to try when the tool cannot connect
  build_commands(image, port=None) -> [argv]   the commands to run, in order; a subclass supplies it
    ^
EsptoolFlasher                                 esptool: erase all, then write one image at 0x0
  ERASE, WRITE, IMAGE_OFFSET, BOOT_HINT
  __init__(tool, chip)                         tool: the tools.find("flasher") Tool; chip: as esptool names it

flasher.build_esptool_prefix(tool, port, chip)    the start of an esptool line, --chip before --port

deploy.plan() -> DeployPlan(commands, mpremote, notes, flasher)   flasher is new: main reads flasher.BOOT_HINT
board_look.EsptoolReader                       keeps its own parse; only its command start comes from flasher.py
```

## Names, checked against developing.md's table

- `Flasher` stays a plain noun and its docstring says Strategy (the table's own example).
- `EsptoolFlasher` is what varies, then the base's whole name.
- A function starts with a verb: `build_commands`, `build_esptool_prefix` (not `commands`).
- `BOOT_HINT` ends in `_HINT` (a sentence). `IMAGE_OFFSET` is an address, not a number with a unit: it keeps its name.
- The module is `flasher.py`, as `deploy_gate.py` and `board_look.py` are named for their job.

## Test first

1. `tests/test_flasher.py`: `EsptoolFlasher(tool, "esp32s3").build_commands` with and without a port gives the exact
   two argv; the base raises `NotImplementedError`; a second subclass in the test proves a caller can swap it;
   `build_esptool_prefix` with and without chip and port; one `BOOT_HINT` for the flasher, the reader and the port
   finder.
2. Existing `test_deploy.py` dry-run and `test_deploy_gate.py` flash tests stay unchanged and green.
3. A rule in the suite style: no exact esptool string constant in `deploy.py` code (see round 1), read with `ast`.
4. Dry-run bytes: `scratchpad/dry.py` runs both dry runs (with and without `--port`) in a built test project, with the
   project path normalised; the output before and after is compared with `cmp`. `--help` is compared too.

## The two bench findings (P242, 2026-10-18)

1. Erase failed to connect right after the look restarted the board; the same command 5 s later connected. A fix changes
   what runs after the yes (a settle pause or one retry of the erase), and this PR's done-when is "the same commands".
   Verdict: not in PR 7, and not in PR 8 either (PR 8 must print the same lines). A bug card: retry the erase once on a
   non-zero exit code only (never esptool's words, P260), as a Decorator over the Flasher, with a bench proof. Today the
   failure tells the person to press BOOT, which is the wrong advice there.
2. The deploy time in the store is local with no zone; the grants are UTC with `+00:00`. The fix touches
   `board_facts.record_deploy`, the facts file and the board log header, and the files already written. Verdict: a small
   card of its own (`datetime.now().astimezone()`; readers must accept old naive records), not a flasher change.

## Risks

- `board_look` imports `flasher`, and `deploy` imports both: no cycle, because `flasher` imports only `tools`.
- A local named `flasher` in `deploy.plan` (the tool) clashes with the module name. The tool is renamed `flasher_tool`
  there. `EsptoolReader.__init__` keeps its `flasher` parameter: it only shadows inside `__init__`.
- Docs this PR updates: developing.md (the Flasher row in the pattern table, line 247 on what each PR gave, the module
  list if there is one). README "What works today" and `tools/journey.py`: no change, an internal seam. `agents.md`: no
  change, no JSON or exit code moves. `--help`: unchanged; it names esptool in prose, which stays.
- Words: a Strategy is a base class a caller can swap; a Decorator wraps an object and adds one behaviour; the ast rule
  reads deploy.py's syntax tree for forbidden string constants; a mutation anchor is the exact line a mutation table edits.
- Mutation table `tests/mutations/p239-pr7.json`; tables that anchor on the moved lines are re-anchored.
