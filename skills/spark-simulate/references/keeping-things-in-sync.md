# Keeping a hardware project in sync

A hardware project has one design and many things derived from it: a simulator project, gerbers,
a schematic image, a 3D model, a bill of materials, and firmware that must agree with the pin
map. Every one of those can drift, and drift is discovered on a bench, expensively.

## The rule

**One source of truth, everything else derived and regenerated.** If a file can be generated, it
is never edited by hand — and the way to enforce that is to regenerate it and fail when the
result differs from what is committed.

## Use Make, not a script

The dependencies are real files, which is exactly what Make is for:

```make
dist/board/circuit.json: board.tsx           # the design is the root
sim/diagram.json: dist/board/circuit.json    # the simulation comes from it
board-gerbers.zip: dist/board/circuit.json   # so does the fab package
```

Change the design and only what is downstream rebuilds, in order. `make -n` shows the plan and
why. Make is already installed everywhere, and needs no configuration.

A script (`check-all.sh`) is worse in one specific way: it has no dependency graph, so it either
rebuilds everything or trusts a human to know what changed. Task runners (`just`, `task`) are
pleasant but add an install; Bazel and Nx are for repositories a hundred times this size.

## Two halves: regenerate and verify

* `make` — regenerate what is out of date. For a person working.
* `make check` — change nothing, and fail if anything disagrees. For CI, and for the hook.

The second is what prevents a stale artefact from being committed. Generators need a `--check`
mode that regenerates in memory and compares.

## Four layers, and what each one catches

| Layer | Catches | Misses |
| --- | --- | --- |
| **Make** | anything out of date, on demand | anyone who does not run it |
| **Claude Code hook** (`hooks/hooks.json`) | drift the moment an AI session edits a design file | edits made in another editor |
| **git pre-commit** (`core.hooksPath`) | drift before it enters history | `--no-verify`, and CI-only changes |
| **CI** (`make check` on push) | everything, permanently | nothing — but it is the slowest feedback |

Use all four: each is cheap, and each covers the one before it. The hook gives seconds-fast
feedback, the commit hook catches humans, CI can never be forgotten.

## What a plugin can and cannot do

A plugin can ship the **hook** (this skill's `hooks/hooks.json` runs `make check` after a design
file is edited) and the **knowledge** (this file). It cannot replace the dependency graph — that
belongs in the repository, next to the files it describes, so it works for someone who has never
installed the plugin.

## Checking the thing nobody checks

The obvious checks are that generated files are current. The one people forget is **firmware
against hardware**: that the pin numbers in the firmware are the pins the board actually wires.
It is a twenty-line script — read the pin constants out of the firmware, read the labels out of
the design, compare — and it catches the bug that wastes an evening with a multimeter.
