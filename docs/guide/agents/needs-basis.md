# What the needs were written from

Part of the [guide for AI agents](../agents.md), beside [the flow](flow.md). The needs phase and the idea phase of
`flow.py show` read `.spark/needs-basis.json` ([P1027](https://github.com/xmejkal/spark/issues/1506)). The reader writes
nothing.

## The goal and the must lines

`parts.py --needs-set` writes the record when a write defines a need or is a review (`[]`). It holds the sha256 of the
brief's goal and of its must lines, sorted, as they were then. If either is different now, the needs phase is `stale`.
Its `says` then holds the needs line, what changed (`the goal changed after the needs were written`, `the must lines
changed …` or `the goal and the must lines changed …`) and `Claude goes through the needs and the must lines with you,
and when they still fit, runs parts.py --needs-set with []: spark changes none of them itself`. That `[]` run clears the
mark. The guide's NOW is the needs phase, by Claude, with no offer. The drop offers stay. A project with no such record
(one written before P1027), or a brief with no goal, says what it said before. A record or a brief that spark cannot read
keeps the phase `ok` and adds one line: `spark cannot tell whether the needs fit the goal: <the reason>`.

## A dropped need

The record also notes the ids of the needs (`needs`, slice 2 of P1027). A review notes the needs as they are. A write
that defines a need notes its needs and keeps the noted ids it lacks, so only a review clears a drop. A noted need that
`.spark/needs.json` no longer holds is a dropped need, and the idea phase is then `stale`. Its `says` holds `Tell Claude
your goal in the chat`, `needs dropped after the must lines were last gone through: <ids>` and `Claude asks you about
each must line a dropped need served, and on your yes changes it in the brief: git keeps each change, so it can be taken
back. If the must lines still hold, Claude runs the review: parts.py --needs-set with []`. The guide's NOW is the idea,
by you, and `next` is the brief step, `init_project` with `needs_yes: true` ([the next step](flow.md#the-next-step)).

A record of slice 1, with no `needs` key, names no drop until the next review. A `needs` value that is no list of ids
makes the record unreadable, as above. A needs file that cannot be read leaves the idea phase as it was: the needs phase
says why.

## The brief step and the way back

The brief step names `<answers.json>`: Claude writes the must lines the person agreed to in that file, outside any
repository, and runs the step only after their yes. When git holds `.spark/project.json` as it is, on a branch, the write
is one commit of that file alone, and the step prints `committed as <sha>. To go back, run in this project: git revert
--no-edit <sha>`. Go back newest first. Else the brief is written as before and one line says why there is no commit
([init](../../../commands/init.md)). Then Claude runs the review.
