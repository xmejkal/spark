# What the observations found, and what happened to it

One line per claim. **A claim leaves this table only by being reproduced and acted on, or by
being rejected with a reason.** Nothing sits here unread.

## Why the table exists

This project has a live demonstration of what happens without one. The findings store in the
smart-bin repo is genuinely good engineering — structural identity so the same defect worded
differently is one finding, anchors validated against the built netlist so a hallucinated
component is refused, locking that survived twelve concurrent writers. On 2026-09-25 it held
**20 findings: 11 blocked, 8 open, 1 rejected, 0 resolved.** Nothing has ever come out of it.

A folder of observation essays would do the same thing, only worse, because nothing would even
be counted.

## Status, and what each one obliges

| status | meaning | what has to happen next |
| --- | --- | --- |
| `raised` | an observer claimed it | reproduce it, or reject it |
| `verified` | reproduced here, by running something | put it in `BACKLOG.md` or fix it |
| `acted` | fixed, or in the backlog with a named item | nothing; keep the row as history |
| `rejected` | reproduced and found wrong, or judged not worth doing | nothing; **keep the row**, so it is not raised again |

`rejected` matters as much as `acted`. An observer that is confidently wrong will be wrong the
same way next time, and a claim with nowhere to retire comes back every run.

## The rule that keeps it honest

**Reproduce before promoting.** Several observer reports have been confidently wrong: one
council's central claim about the evals was correct and changed the roadmap, another's verdict on
two of nine findings was wrong in a way that would have buried real defects. A row moves to
`verified` only when someone has run something and seen it.

## The table

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| | *(first observer reports land here)* | | | |
