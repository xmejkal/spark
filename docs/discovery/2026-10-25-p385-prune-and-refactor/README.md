# P385: prune and refactor

Card P385 [#494](https://github.com/xmejkal/spark/issues/494), base commit `d064a65`. The tag
`pre-refactor-2026-10-25` keeps the version before the refactor.

> TL;DR. The spike measured the 76 modules of `scripts/` and `tools/` and gave each one verdict: keep 68, split 4, move
> behind a module 3, prune 1. It also rewrote the refactor plan as version 2, with six stages and 22 slices. No product
> code changed.

The pruning list holds the facts for each module and the verdict that Fable 5.1 drew from them. The drift list names what
plan version 1 says that the code no longer holds. Plan version 2 answers both, and five lessons teach the PO the
decisions it needs.

## The files of this folder

- `README.md`: this page.
- `pruning_facts.py`: a read-only script that prints the fact table of the pruning list, one row per tracked module.
- `pruning-list.md`: the verdicts for the PO, then the fact table for an agent and the facts behind each verdict.
- `drift.md`: what plan version 1 says that the code no longer holds, and each comment of #494 mapped to a plan item.
- `PRUNED.draft.md`: the draft of `PRUNED.md`, with what goes, why, what keeps it and the command that brings it back.
- `lessons.md`: five lessons, each with one question for the PO.

The plan is [refactor-plan.md, version 2](../2026-10-19-p323-target-architecture/architecture/refactor-plan.md). It
replaced version 1 in place, and git keeps version 1.

## How a later walk adds a column

Each walk record is a file or a folder. Run this from the repository root, and the script prints the fact table with one
more column that counts how often the record names each module:

    python3 docs/discovery/2026-10-25-p385-prune-and-refactor/pruning_facts.py --walk <record>

The column is named after the record. A record outside the repository prints only its file name and its sha256. A walk
column vetoes no verdict, because a record names scripts in prose.

## What waits on the PO

- The merge of the PR for this card.
- Decision 1, readability first (lesson 3 in `lessons.md`).
- Decision 2, the shape of the package (lesson 2).
- Decision 4, the start of the area moves (lesson 2).
