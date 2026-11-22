# R11 retro (prepared 2026-11-22 for Petr, not yet held)

> R10 set four actions. One held in part and three did not hold.
> The board grew by 1.75 cards for each card closed. Nobody built the two tools that R10 asked for.
> The inbox holds 62 entries: a gate catches 6 today, a card holds 10, and 46 drop.
> R11.1, for you to decide: the session-start status shows the inflow and the retro's age.
> R11.2, for you to decide: a slip that the learned rules hold twice becomes a check, the lane count first.

R11 was due on 2026-10-27, or after 10 merged stories. It comes 26 days late, after 374 merged PRs. The facts below
come from two read-only facts agents on Sonnet and from commands that the session ran on 2026-11-22 at about
19:10 Prague time. A Lean and Agile lens and the refuter, both on Opus, reviewed the page. P1016
[#1481](https://github.com/xmejkal/spark/issues/1481) holds this work. The proposed date of R12 is 2026-11-29.

## R10's actions, checked as written

| action | check at R11 | measured | verdict |
| --- | --- | --- | --- |
| R10.1 walk 2 by 10-27 with the board's button and LED | steps outside spark: 0 | Walk 2 ran on 10-22 and 10-23, inside the date. Its diary names one look outside spark that the person asked for (the button name). The six later walk diaries count no outside steps. Walk 4 (11-01) flashed an image with `mpremote` and `esptool` by hand. | held in part |
| R10.2 a found row becomes a card only when it is a bug or blocks the next walk step | cards opened per card closed: 1 or less | 657 opened and 375 closed from 10-20 to 11-22 (1.75). From 11-15 to 11-22: 201 and 104 (1.93). 402 open today. Of the 657, 18 are epics and 11 are plan tasks. | not held |
| R10.3 the push hook runs `tools/factcheck.py` on changed plan files | plans pushed with a factcheck result: all | `tools/pre-push` and `tools/check_commit.py` never call factcheck. P363 [#465](https://github.com/xmejkal/spark/issues/465) is still open. P786 (#1087) took the factcheck claim off the team pages. | not held |
| R10.4 each rows file holds "N planted, M escaped, K real gaps" | stories with the line: all. Rate-limit hits: 0 | 6 of the 159 rows files that were added since 10-20 and still exist hold a "N planted" line, and none holds the full line. 4 inbox entries after R10 name a rate limit (35, 42, 51, 54). `learned-rules.md:371` records one more, on 11-13. | not held |

The commands, as the facts agents ran them:

```
gh api -X GET search/issues -f q='repo:xmejkal/spark is:issue created:2026-10-20..2026-11-22' -q .total_count   # 657
gh api -X GET search/issues -f q='repo:xmejkal/spark is:issue closed:2026-10-20..2026-11-22' -q .total_count    # 375
/usr/bin/grep -n factcheck tools/pre-push tools/check_commit.py                                                  # no hits
git log --since=2026-10-20 --diff-filter=A --name-only --format= -- 'docs/observations/rows/*' | sort -u          # 315 paths, 159 exist
```

What to do with each, proposed:

- R10.1 ends, because walks now record their gaps as rows and nobody reads an outside count.
- R10.2 stays as the rule, and R11.1 makes its measure visible each day.
- R10.3 is dropped and P363 closes as not planned, because the refuter catches plan claims and P786 already took the
  claim off the team pages. If Petr drops it, this PR also prunes `docs/guide/developing.md:355-359`, which still
  tells a plan to run factcheck.
- R10.4 is dropped, because `tests/mutations/ledger.jsonl` and each PR's anchors file in `tests/mutations/` now hold
  what the line was for.

## The two changes, for Petr to decide

When Petr takes a change, its card is filed that day at the top of Ready, for spark-main, with R12 (2026-11-29) as
its *Needed by*. R10.3 failed because its card P363 stayed in Idea for a month.

### R11.1 The session-start status shows the inflow and the retro's age

The board holds 402 open cards: 131 are older than a month, 138 are from 10-23 to 11-08, and 133 are newer. 40 of the
402 are epics. R10.2 asked Claude to file fewer cards, and the ratio went from 2.5 (73 to 29) to 1.75, not to 1.
Closing old cards cannot balance it. The board gets about 25 new cards a day, but only about 2 old cards hold no
words of the PO. A rule alone did not hold, and no line shows the inflow. R11 also came 26 days late, because nothing
shows the retro's age.

The change: `tools/board.py status` and the day close print two more lines, "filed in 7 days: N, closed: M" and
"last retro: R11, D days ago". The day close is at risk when N is larger than M, or when D is larger than 7. R10.2
stays the rule behind the first line. The weekly look keeps its list of Idea cards to close, which the PO strikes or
confirms (`scrum/README.md:76`).

The check at R12:

```
python3 tools/board.py status | /usr/bin/grep -E 'filed in 7 days|last retro'
gh api -X GET search/issues -f q='repo:xmejkal/spark is:issue created:2026-11-23..2026-11-29' -q .total_count
gh api -X GET search/issues -f q='repo:xmejkal/spark is:issue closed:2026-11-23..2026-11-29' -q .total_count
```

If the first command prints both lines, and the third number is equal to or larger than the second, the change held.

### R11.2 A slip that the learned rules hold twice becomes a check

The learned rules hold the same slips again and again. Moving a card without counting the lane first is at
`learned-rules.md` lines 369 and 524, and it happened again today. A time written from feel, not from the clock, is at
lines 240, 448, 455, 481, 491, 492, 506 and 522. It happened again today, when six card comments carried times up to
an hour in the future. A further rule did not stop either slip.

The change: when an inbox entry repeats a slip that the learned rules already hold twice, the fix is a check in a
script or a hook, not a further rule. Each slip entry in the inbox starts with a tag, for example `slip:lane`, so that
a script can count it. The first check is the lane count: `tools/board.py move <card> <stage>` counts the lane and
the stage before it moves a card. It refuses a move over a limit and writes *Waiting since* from the clock. Sessions
move cards only through it.

The clock is the second check, and its card designs the pattern. The refuter showed three cases that a simple rule
gets wrong. "Auto mode until 06:00" is a true future time. A slip can be a past time that is a few minutes off. A
bare HH:MM breaks across midnight. If the clock check becomes a hook, it goes either in the repository's
`.claude/settings.json` (none exists today, so it comes by a PR) or in Petr's own settings. That is his pick on the
card.

The check at R12:

```
python3 tools/board.py move --help >/dev/null && echo move-exists
sed -n '/R11 HELD/,$p' ~/.claude/projects/-Users-petr-Development-spark/memory/retro-inbox.md | /usr/bin/grep -c 'slip:lane'
```

If the first command prints `move-exists` and the count is 0, the change held.
If the count is 0 and the hook's test refuses a body with a future time, the change held.

## The inbox, sorted

The verdicts: gate means that an automatic check catches it today. Card means that a card holds the work, named.
Drop means that it is handled, decided or no longer true, with the reason. Entries 1 to 30 come before R10, which
handled them, and entry 31 is R10's own line. "Rule" names a written rule in `CLAUDE.local.md`, `scrum/README.md` or
`learned-rules.md`.

| # | date | entry, short | verdict | why |
| --- | --- | --- | --- | --- |
| 1 | 10-15 | slice started while a PR was open | drop | rule "finish before switching" |
| 2 | 10-15 | an epic without its label counted in Ready | drop | an epic counts nowhere (`tools/check_backlog.py:200`) |
| 3 | 10-15 | one plan, two names for one thing | drop | rule: every plan checks its names |
| 4 | 10-15 | typed sub-tasks per story | drop | R10.4 dropped typed tasks |
| 5 | 10-15 | analyze logs before deleting them | drop | rule under "Never" |
| 6 | 10-15 | mine the transcripts | card | P259 [#279](https://github.com/xmejkal/spark/issues/279), open |
| 7 | 10-15 | an extra gaps round in every plan | drop | rule: the plan council's second round |
| 8 | 10-15 | judge the experiments | drop | judged at R9 and R10 |
| 9 | 10-15 | the weekly look and the refuter | drop | R10 kept the refuter |
| 10 | 10-16 | a coach skill for the retro | card | P266 [#298](https://github.com/xmejkal/spark/issues/298), open, and P265 is done |
| 11 | 10-16 | plan mode stopped writing agents | drop | learned rule AT272 |
| 12 | 10-16 | "rate the assumptions" confused | drop | rule: teacher-style questions |
| 13 | 10-16 | an edit script blew up a module | drop | learned rule: assert each anchor once |
| 14 | 10-16 | two autonomous hours, what worked | drop | a record, no action |
| 15 | 10-16 | a card that waits on the PO filled Design | drop | P928: cards that wait on the PO count apart |
| 16 | 10-17 | pulled past the in-flight limit | gate | the push hook counts the lanes (W6), but only at push; R11.2 adds the count before a move |
| 17 | 10-17 | does an epic count in flight | drop | R9: an epic counts nowhere |
| 18 | 10-17 | an agent detached HEAD | drop | R9.4: agents that use git get a worktree |
| 19 | 10-17 | too many full-suite runs | drop | the story run replaced the full run per push (P714) |
| 20 | 10-17 | two PRs on the same files | drop | R9 WIP C: same files never in parallel |
| 21 | 10-18 | a spike started over the limit | gate | the push hook counts the lanes (W6) |
| 22 | 10-18 | GraphQL limit from board edits | drop | joins 54 |
| 23 | 10-18 | are the stages used | drop | answered at R10 |
| 24 | 10-18 | "Closes #N" closed a card before the bench | drop | learned rule: "Part of #N" |
| 25 | 10-18 | one "yes" to a whole backlog | drop | rule: a card holds his words |
| 26 | 10-18 | the classifier blocked merges in auto mode | drop | merges run in auto mode (#1477 to #1480 today) |
| 27 | 10-18 | how useful is the refuter | card | P317 [#401](https://github.com/xmejkal/spark/issues/401), open |
| 28 | 10-19 | `item-list --limit 400` used the limit | drop | joins 54 |
| 29 | 10-19 | the P324 experiment | drop | judged at R10, dropped |
| 30 | 10-20 | catch hallucinations, two proposals | drop | they became R10.3 and R10.4, checked above |
| 31 | 10-20 | R10 held | drop | a marker |
| 32 | 10-20 | two pushes of one branch at once | drop | once, no harm |
| 33 | 10-22 | a card filed with no slice | drop | an Idea card needs no slice (P146); `tools/check_backlog.py` asks for it from Ready on |
| 34 | 10-22 | "where are we, what works" | gate | README table, `tests/test_journey.py`, the session-start status |
| 35 | 10-23 | two sessions on one backlog | drop | rule: when two sessions run, one stands down |
| 36 | 10-23 | do the learned rules feed agents | drop | agents slipped since (39, 60), but on tools, which R11.2 turns into checks |
| 37 | 10-26 | the push under 90 s | drop | met: this PR's push took 88 s for the whole gate |
| 38 | 10-26 | the first hook numbers | card | P495 [#677](https://github.com/xmejkal/spark/issues/677) |
| 39 | 10-27 | the disk fell to 1.2 GB | gate | `tools/board.py status` warns under 10 GB |
| 40 | 10-31 | the WIP limit counts cards, not PRs | drop | decided: every card counts (`scrum/README.md:129`) |
| 41 | 10-31 | walk predictions | drop | the PO: walks run free-form, no predictions |
| 42 | 11-01 | secondary limit, boards read in full | drop | joins 54 |
| 43 | 11-01 | a full MAC in a commit and a card | gate | `tests/test_no_board_address.py` scans tracked files at every push. A card text is not scanned |
| 44 | 11-01 | "this is taking way too long" | card | P495 [#677](https://github.com/xmejkal/spark/issues/677) |
| 45 | 11-01 | twelve PRs in auto mode, what cost | drop | `mutate.py --tier` and `--budget` answer the widened run |
| 46 | 11-02 | is P469 in flight | drop | P469 is no longer in flight |
| 47 | 11-05 | the classifier blocked a merge | drop | merges run in auto mode |
| 48 | 11-05 | a second writer after a clear | drop | rule: list the agents first after a restart |
| 49 | 11-05 | the gate printed no test name | gate | `check_commit.py` prints the red tests (P797) |
| 50 | 11-07 | a stack of PRs filled Review | drop | decided: every card counts |
| 51 | 11-08 | the board read cost the GraphQL limit | drop | joins 54 |
| 52 | 11-08 | mutate.py has no row selection or shards | drop | `--for`, `--tier` and `--budget` since P787 |
| 53 | 11-08 | no failing test ids | drop | fixed by P797 and P787 |
| 54 | 11-08 | use REST for the board and PR state | drop | the last hit was 11-13 (`learned-rules.md:371`), and the gate prints its GraphQL cost (`tools/check_backlog.py:119`) |
| 55 | 11-09 | architecture guards went silent | drop | `measure.py` reads every name of a spark import |
| 56 | 11-09 | copy_of copied ignored files | drop | fixed by P807 |
| 57 | 11-18 | are subagents used well | card | P317 [#401](https://github.com/xmejkal/spark/issues/401) holds the refuter's worth |
| 58 | 11-19 | two model tests offered, not run | drop | no stage waits on them |
| 59 | 11-20 | the story run missed a breadboard test, main went red | card | new card, a bug in the gate |
| 60 | 11-21 | a builder deleted the hook's output | card | new card: the hook keeps its output in a file |
| 61 | 11-22 | a card moved without counting the lane | card | R11.2's first check, `tools/board.py move` |
| 62 | 11-22 | times written from feel | card | R11.2's second check, the clock |

The rate-limit entries (22, 28, 35, 42, 51, 54) drop, because the last hit was 11-13 and the gate prints its cost.
Entries 59 and 60 are real defects in the gate, so they become cards under R10.2. If Petr takes R11.2, entries 61
and 62 become its cards.

The sort, counted: gate 6 (16, 21, 34, 39, 43, 49), card 10 (6, 10, 27, 38, 44, 57, 59, 60, 61, 62), and
drop 46.
