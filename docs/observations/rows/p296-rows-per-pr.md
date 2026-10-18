# P296 rows per PR: findings rows

The plan councils of P296 (#358). Plan: [`plan.md`](../../discovery/2026-10-18-p296-rows-per-pr/plan.md).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | One `rows.md` per discovery folder still conflicts, because two PRs can share a folder | refuter, round 1 | acted | reproduced in a scratch repo (`CONFLICT (content)`); one file per PR in `docs/observations/rows/` |
| 2 | A listing tool `tools/rows.py` is bloat, and INDEX.md's rows have three widths and stray status words | tech lead and refuter, round 1 | acted | tool dropped; one grep line in `developing.md` |
| 3 | The plan's columns used other names than INDEX.md's for the same things | tech lead, round 1 | acted | the rows file header is INDEX.md's own |
| 4 | A guard on AT numbers alone misses a new row with another prefix | tech lead, round 1 | acted | the test pins INDEX.md's row count, 1067 |
| 5 | `GLOSSARY.md`, `DECISIONS.md`, `docs/README.md` and `keep-current/rows.md` still send rows to INDEX.md | refuter, round 1 | acted | changed in this PR |
| 6 | Freezing INDEX.md breaks code that reads it | refuter, round 1 | rejected | no code reads it; tools cite AT numbers in comments only |
| 7 | An edit to an old row's status can still conflict with an edit to a nearby row | refuter, round 1 | closed | rare and visible; no fix |
| 8 | The grep line missed the bold status cells (`**raised**`) that most INDEX.md rows use | tech lead, round 2 | acted | the line matches `\**`; 274 unresolved rows in INDEX.md on 2026-10-18 |
| 9 | "Row count" had no definition, and INDEX.md holds a second table | tech lead, round 2 | acted | the count reads only `## The table`, without header and separator lines |
| 10 | A branch name can hold `/`, and agent branch names say nothing about the card | senior, round 2 | acted | a rows file is named by card and topic |
