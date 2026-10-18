# P239 PR 7: the flasher seam

> TL;DR: esptool's commands, its offset and its boot hint leave deploy.py and live in `scripts/flasher.py`, as a
> `Flasher` base (a Strategy) and `EsptoolFlasher`. `deploy.py --dry-run` prints the same bytes. Nothing is built for
> Arduino or PlatformIO: the base only names where they plug in. Card [#238](https://github.com/xmejkal/spark/issues/238),
> brief item 3 of [P218's finish](../2026-10-17-p218-finish/brief.md).

## Council

Not yet run. Round 1: tech lead (Sonnet) and the refuter (Opus). Round 2: tech lead and PO assistant (Sonnet).

## What moves

| Now | Becomes |
|---|---|
| `deploy.IMAGE_OFFSET`, `deploy.ERASE`, `deploy.WRITE` (deploy.py:50-53) | `EsptoolFlasher.IMAGE_OFFSET`, `.ERASE`, `.WRITE` |
| `deploy.flash_commands(flasher, chip, image, port)` | `EsptoolFlasher(tool, chip).build_commands(image, port)` |
| `board_look.BOOT_HINT`, used by `PortFinder`, `EsptoolReader` and deploy.py | `flasher.BOOT_HINT`; `Flasher.BOOT_HINT` holds it for deploy |
| `tools.command_for(tool) + ["--port", port]` in `EsptoolReader.read` | `flasher.build_esptool_command(tool, port, chip=None)`, shared with the reader |

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

flasher.build_esptool_command(tool, port, chip)   the start of an esptool line; EsptoolFlasher and EsptoolReader call it

deploy.plan() -> DeployPlan(commands, mpremote, notes, flasher)   flasher is new: main reads flasher.BOOT_HINT
board_look.EsptoolReader                       keeps its own parse; only its command start comes from flasher.py
```

## Names, checked against developing.md's table

- `Flasher` stays a plain noun and its docstring says Strategy (the table's own example).
- `EsptoolFlasher` is what varies, then the base's whole name.
- A function starts with a verb: `build_commands`, `build_esptool_command` (not `commands`).
- `BOOT_HINT` ends in `_HINT` (a sentence). `IMAGE_OFFSET` is an address, not a number with a unit: it keeps its name.
- The module is `flasher.py`, as `deploy_gate.py` and `board_look.py` are named for their job.

## Test first

1. `tests/test_flasher.py`: `EsptoolFlasher(tool, "esp32s3").build_commands` with and without a port gives the exact
   two argv; the base raises `NotImplementedError`; a second subclass in the test proves a caller can swap it;
   `build_esptool_command` with and without chip and port; one `BOOT_HINT` for the flasher, the reader and the port
   finder.
2. Existing `test_deploy.py` dry-run and `test_deploy_gate.py` flash tests stay unchanged and green.
3. A rule in the suite style: no esptool command word in `deploy.py` code, read with `ast` (string constants), not a
   grep of prose.
4. Dry-run bytes: `scratchpad/dry.py` runs both dry runs (with and without `--port`) in a built test project, with the
   project path normalised; the output before and after is compared with `cmp`. `--help` is compared too.

## The two bench findings (P242, 2026-10-18)

1. Erase failed to connect right after the look restarted the board; the same command 5 s later connected. A fix changes
   what runs after the yes (a settle pause or one retry of the erase), and this PR's done-when is "the same commands".
   Lean: not in PR 7. PR 8 moves the run loop into `DeployService`; a retry on a non-zero exit code of the erase only
   (never on esptool's words, P260) belongs there, with a bench proof. Proposed as a note on PR 8's card.
2. The deploy time in the store is local with no zone; the grants are UTC with `+00:00`. The fix touches
   `board_facts.record_deploy`, the facts file and the board log header, and the files already written. Lean: a small
   card of its own, not a flasher change.

## Risks

- `board_look` imports `flasher`, and `deploy` imports both: no cycle, because `flasher` imports only `tools`.
- A local named `flasher` in `deploy.plan` (the tool) clashes with the module name. The tool is renamed `flasher_tool`
  there. `EsptoolReader.__init__` keeps its `flasher` parameter: it only shadows inside `__init__`.
- Mutation table `tests/mutations/p239-pr7.json`; tables that anchor on the moved lines are re-anchored.
