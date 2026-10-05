# The backlog revalidation — the W14 lens's proposals (P102a, Task 1)

**What this is.** One row for each of the 35 open items of `scrum/PRODUCT_BACKLOG.md` (a heading matching none of
`DONE|ANSWERED|CLOSED|PARKED|MERGED|DELETED|SPLIT|~~`), plus six new rows for P102's sub-items a–f. The lens
proposes; the PO confirms or changes in one pass (spec `docs/2026-10-05-backlog-in-github-design.md` §5), and the
confirmed table is the migration's only input. Written 2026-10-05 from the backlog, `STORY_MAP.md`, `git log` and the
files named in the evidence column. Nothing was run against the store, the web or the hardware.

**Rules applied.** W14 (every kept item names the design that needs it; an item no design pulls is parked), W21
(a datum stays only if a decision rests on it), W16. Stages: Idea (the backlog), Discovery 1, Design 1, Ready 3,
Build 1, Review 1, at most 2 in flight across Discovery/Design/Build/Review. Epics carry no limit, so an epic's Status
is written for the record and is not counted. The PO's order of 2026-10-05: P102 first (P102a in Build, P102c next, in
Ready), then P100 with P101, then P97.

**Repository.** `bin` for B1, B5, B8 only, as the brief says; everything else `spark`. P58 and P73 are about the
bin's README and bring-up logs, so the PO may want them in `bin` (flagged below).

## Summary

| proposal | rows | ids |
| --- | --- | --- |
| close as done | 3 | P80, P81, P93 |
| merge into | 2 | P70 into P102; P101 into P102e |
| park | 4 | P64b, P64c, P84, P86 |
| keep (the 35 open items) | 26 | P38, P39, P43, P58, P59, P64a, P72, P73, P74, P76, P77, P78, P79, P87, P89, P90, P91, P92, P94, P97, P100, P102, R2.6, B1, B5, B8 |
| keep (new rows, P102 sub-items) | 6 | P102a, P102b, P102c, P102d, P102e, P102f |

3 + 2 + 4 + 26 = 35 open items, as the brief counted. Of the 32 kept rows: 5 epics (P76, P79, P94, P100, P102), the
rest stories, chores and bugs.

**Statuses of the kept rows (limits).** Build: P102a (1, limit 1). Ready: P102c, P97 (2, limit 3). Discovery 0,
Design 0, Review 0. In flight: 1 (limit 2). Idea: every other kept row, epics included except P102, which is recorded
as Build for its child P102a.

## 1. Close as done (3)

| id | proposal | type | slice | parent | repo | status | waiting | reason | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P80 | close as done | story | 4 v1 on two projects | — | spark | — | — | The two small agents, `parts.py --read`, the routing in `/spark:research`, the MCP wiring and the cost tool are built and were used once on a real need (with three fixes after it). Flag: the backlog's own Open line (reader not yet used on a real need; the M1–M10 mechanical checks "next") is not done; if the PO wants either, it comes back as a new item pulled by a design. | `git log --oneline --grep P80`: d2979a6 (agents built and routed), cfa176e (`--read`), e68cb1e (`tools/research_cost.py`), 581fa8a (first use, three rules); backlog "Built 2026-10-03" and "First use" paragraphs |
| P81 | close as done | story | 2 First copper | — | spark | — | — | Both increments are done and their proof lines hold: `validate` refuses a `pin_order` without `pin_order_proof` (scripts/parts.py:342), the three live warnings are printed (host_requirements, `pull_conflicts`, the DS3231 note replaced). What to do about the L9110S pull-ups waits on the bin's meter reading, which is the bin's bench, not this item. | `git log --oneline --grep P81`: c2afc47 (increment 1), ecf822a (increment 2, with B11); 7846690 (B11); backlog "Increment 1 done 2026-10-03" and "Increment 2 done 2026-10-03" (lines 703–795) |
| P93 | close as done | story | 10 The store | P94 | spark | — | — | Its only proof line, `--drawer --json` lists the PO's real parts, was run for P95: 110 entries, 12 linked. Later importers (AliExpress, photos) are "not now" by the PO and are pulled by a design, not kept as an item. | `git log --oneline --grep P95`: afde5c8 ("110 entries, 12 linked"), 0189184 (the drawer), cc89b3d (merge of PR #1); backlog P95 "Proven 2026-10-04"; commit 01c1300 maps P93 into store 1a |

## 2. Merge into, and park (5)

| id | proposal | type | slice | parent | repo | status | waiting | reason | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P101 | merge into P102e | story | team tools | P102 | spark | — | — | The same thing as P102e, a discovery skill; P102e comes first, before P100 needs it (the PO, 2026-10-05). | backlog line 830; P102 entry |
| P70 | merge into P102 | story | team tools | P102 | spark | — | — | Its heading already says "taken into P102"; its design stands and is what P102a (the spec) implements. Its Value proven by is P102's first line. | backlog line 514 ("taken into P102, 2026-10-05"); git 763793f ("taking in P70"); spec §1 ("P70's line, kept") |
| P64b | park: pulled back when the PO decides that `host_requirements` need a pointer, or a prose claim reaches a board and is wrong again (the ALL_LOW case) | story | 6 Shared, not copied | — | spark | — | the PO (his decision whether and when; no date in the backlog) | The heading says "whether is the PO's"; no design is blocked on it this week (W14). | backlog line 1228; `/usr/bin/grep -rn --include=*.py "rests_on" scripts` finds nothing |
| P64c | park: pulled back by P64b | story | 6 Shared, not copied | — | spark | — | — | Heading says "after P64b"; it ships only if research or `--promote` routes to it (W15). | backlog line 1234 |
| P84 | park: pulled back when the first person outside the project researches a part (slice 5, R2.6) | story | 10 The store | P94 | spark | — | — | The PO's decision after P85: the shared database starts at that moment; its prerequisites are P87–P92, which are items in their own right. | backlog lines 1024–1050 ("starts when the first person outside the project researches a part") |
| P86 | park: pulled back by the first design that needs more than `--json` reads (the viewer waits on P90–P92 and P84) | story | 10 The store | P94 | spark | — | — | "An idea, not designed yet"; Value proven by "to be set in discovery"; no design is blocked without it. | backlog lines 935–946 |

## 3. Keep, by slice (27 open items and 6 new rows)

### Slice 1b — From a vague idea

| id | proposal | type | slice | parent | repo | status | waiting | reason | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P76 | keep | epic | 1b From a vague idea | — | spark | Idea | — | Not designed (the backlog says so); it is the seven ways in, so an epic; it comes after the tools chore and P100's discovery, which tests the first ways in. | backlog line 574; STORY_MAP slice 1b |
| P100 | keep | epic | 1b From a vague idea | — | spark | Idea | — | The PO's order puts it right after P102; its discovery cannot start until the tools chore ends. Slice is my choice (see unsure list): its first journey is the new idea. | backlog line 808; STORY_MAP "the epic in refinement"; git 763793f, 2f26fe9 (PR #3 merged) |

### Slice 2 — First copper

| id | proposal | type | slice | parent | repo | status | waiting | reason | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 | keep | chore | 2 First copper | — | bin | Idea | the PO (a look in the drawer; the backlog gives no date, last touched 2026-10-04) | Four things wait on which audio module is in the drawer. | backlog lines 1654–1664 |
| P58 | keep | bug | 2 First copper | — | bin | Idea | — | Still true: the bin's firmware README names the XIAO's pins (D1, D6, D4/D5) and `04_mp3.py`, against `config.py`. Its fix lives in the bin's repository, so the PO may want it in `bin`. | `/usr/bin/grep -n "OPEN btn D1\|04_mp3\|DFR0534 on D9" /Users/petr/Development/smartbin-local/firmware/micropython/README.md` finds lines 67 and 69; backlog line 1275 |
| P73 | keep | story | 2 First copper | — | bin | Idea | — | The bench has never run, so no verdict log exists; the command that lists verdicts can be built before the bench. Logs are kept in the bin, so the PO may want it in `bin`. | backlog line 1166; bin CLAUDE.md "Nothing has ever touched hardware" |
| B8 | keep | bug | 2 First copper | — | bin | Idea | — | One failure in 36 runs, test name never kept; the bin's gate is only trusted while it never fails for nothing. | backlog line 1756 |
| B5 | keep | chore | 2 First copper | — | bin | Idea | — | Still true: every gated commit dirties `board-gerbers.zip` (creation dates only). | backlog line 1765 |

### Slice 3 — Firmware on a Mac

| id | proposal | type | slice | parent | repo | status | waiting | reason | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P59 | keep | bug | 3 Firmware on a Mac | — | spark | Idea | — | Still true: irrigation's `main.py` ends with `main()` at module scope, so it cannot be imported. | `tail -5 /Users/petr/Development/irrigation/firmware/main.py` ends `main()`; backlog line 1288 |
| P74 | keep | story | 3 Firmware on a Mac | — | spark | Idea | — | No check of firmware against `pins.py` exists in `scripts/` (no file, no "never driven" string in `scripts` or `tests`); it waits for P59's importable firmware. | `/usr/bin/grep -rln "never driven" scripts tests` finds nothing; backlog line 1173 |

### Slice 4 — v1 on two named projects

| id | proposal | type | slice | parent | repo | status | waiting | reason | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P38 | keep | story | 4 v1 on two projects | — | spark | Idea | — | Still true: `HOST_PART_KINDS` is pulldown, pullup, divider, series; no capacitor kind. | scripts/parts.py:330; backlog line 1539 |
| P39 | keep | story | 4 v1 on two projects | — | spark | Idea | — | Still true: a `--need` miss still prints "Research it" and no index. Flag: P96's `--match` may have taken over the job; one look settles it. | scripts/parts.py:1494–1497; backlog line 1403 |
| P43 | keep | story | 4 v1 on two projects | — | spark | Idea | — | The `fix` half only, as the heading says; `check_all` still flattens findings (no `fix` handling in `scripts/check_all.py`). | `/usr/bin/grep -n "fix" scripts/check_all.py` finds only a comment; backlog line 1374 |
| P64a | keep | story | 4 v1 on two projects | — | spark | Idea | — | Not done: `validate` checks that `verified` and `source` keys exist, never that a verified fact cites a URL or a kept document. | scripts/parts.py:53 and 597; backlog line 1218 |
| P77 | keep | story | 4 v1 on two projects | — | spark | Idea | — | Needs a council and the PO; its irrigation example is held for it; P102f gives the regenerated examples a home. | backlog line 596; spec §2 (spark-demos) |
| P78 | keep | story | 4 v1 on two projects | — | spark | Idea | — | The generator half is done (c233826); the LED record and the acceptance line are open. | `git log --oneline --grep P78`: c233826; backlog line 612 |

### Slice 5 — A real stranger

| id | proposal | type | slice | parent | repo | status | waiting | reason | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R2.6 | keep | story | 5 A real stranger | — | spark | Idea | the PO (picks the domain) and outside (a real person) | The product's only outside test; its own heading says the PO picks the domain. | backlog line 1559 |

### Slice 7 — Perfboard to PCB

| id | proposal | type | slice | parent | repo | status | waiting | reason | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P79 | keep | epic | 7 Perfboard to PCB | — | spark | Idea | — | "An overview, not a process"; designed with the PO before anything is built; no story under it yet. | backlog line 632 |

### Slice 10 — The store

| id | proposal | type | slice | parent | repo | status | waiting | reason | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P94 | keep | epic | 10 The store | — | spark | Idea | — | Its spec and plan are approved, P95 and P96 are done; what remains are its stories (P97 and the P85 items), so it stays the epic. | backlog line 904; git 5fa72d2, cc89b3d; STORY_MAP slice 10 |
| P97 | keep | story | 10 The store | P94 | spark | Ready | — | The next store increment, third in the PO's order (P102, P100, then P97); its spec (§4 store 1c) is approved and its Value proven by is set. | backlog line 796; git bb88d87 |
| P87 | keep | story | 10 The store | P94 | spark | Idea | — | "Before any shared record"; a crafted record produced live JavaScript in the board file. No commit addresses it. | backlog line 966; `git log --oneline --grep P87` finds only 0fea69f (the item written) |
| P89 | keep | story | 10 The store | P94 | spark | Idea | — | Partly carried by P96 (`--audit`, b9fcf8a); still open: `--need` showing what a candidate owes, `--show` printing `why_not`. The backlog says it is pulled by 1c's step. | backlog lines 985–995 |
| P90 | keep | story | 10 The store | P94 | spark | Idea | — | Still true: no checksum comparison or manifest for `--fetch`. | backlog line 996; `git log --oneline --grep P90` finds only 0fea69f |
| P91 | keep | story | 10 The store | P94 | spark | Idea | — | The shelf is done by P95 (1845f29, 0189184); what is left is that `--promote` from a project still writes spark's library by default (`promote`, scripts/parts.py:1172), with no maintainer flag. | scripts/parts.py:1161–1182; backlog line 1006 |
| P92 | keep | story | 10 The store | P94 | spark | Idea | — | The JSON envelope came with P95 (0104e20); still open: `--skeleton --catalog`, `--keep --into`, `--set-aside` do not exist, and agents still name `~/.local/share/spark/...` paths. | `/usr/bin/grep -rn '\.local/share' agents commands` prints agents/parts-researcher.md lines 53 and 58; backlog line 1016 |

### Team tools

| id | proposal | type | slice | parent | repo | status | waiting | reason | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P102 | keep | epic | team tools | — | spark | Build (epic, not counted) | — | The PO's first item; the epic for the six stories below. | backlog line 842; git 3b773bc (the spec), 763793f |
| P102a | keep (new) | story | team tools | P102 | spark | Build | — | The backlog in GitHub: this table, then the issues, the projects, the freeze and the check, per the spec. Needed by: P100's discovery and every design after it (P102's entry). Value proven by: `gh project item-list` lists every open spark item with Needed by filled; the frozen file says it is the archive; the W14 check reads the issues. | spec §1, §11; git 3b773bc |
| P102c | keep (new) | story | team tools | P102 | spark | Ready | — | The session-start status and where the day-close is written; next in the PO's order. Needed by: the PO's wish to see what is in progress at every session. Value proven by: a session in spark opens with what is in progress and the open PRs. | spec §10; backlog P102 "split … c" |
| P102b | keep (new) | story | team tools | P102 | spark | Idea | — | Maps and journeys as text, drawn in Miro and Canva (Canva needs its connector authorised). Needed by: P100's discovery. Value proven by: the story map exists as text and as a Miro board drawn from it. | spec §7, §10; backlog P102 |
| P102d | keep (new) | story | team tools | P102 | spark | Idea | — | Proofs run as commands, the *Proven* field, the epic-done audit as a command. Needed by: the PO's wish that the map says proven or not. Value proven by: one open story's proof runs from its issue and the map shows it proven or not. | spec §3, §10; backlog P102 |
| P102e | keep (new) | story | team tools | P102 | spark | Idea | — | A discovery skill (reading one or two community skills whole; installed only with the PO's yes). Needed by: P100's discovery. Value proven by: P100's journeys follow the skill. | spec §10; backlog P101, P102 |
| P102f | keep (new) | story | team tools | P102 | spark | Idea | — | `xmejkal/spark-demos`: one public repository and project, a folder per demo, each history checked before it is published (vendor files, GPS, tokens); needs its own design. Needed by: the PO's rule that demos get their own repository and project. Value proven by: to be set in its design. | spec §2, §10; backlog P102 "f" |

### Desk lane

| id | proposal | type | slice | parent | repo | status | waiting | reason | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P72 | keep | chore | desk lane | — | spark | Idea | — | P102a's Kanban answers its cut 2 (sprints and retros); cuts 1 and 3 (agreements that name a command, mutation tables only for verdict code) remain and are not done: WORKING_AGREEMENTS still has 22 W sections. After P102a. | backlog line 1154; `/usr/bin/grep -n "^## W" scrum/WORKING_AGREEMENTS.md | wc -l` printed 22; spec §9 |

## Items I was unsure of

- **P80** (close): everything it built is real, but its own "Open" lines (the reader on a real need, the M1–M10 checks)
  are not done. I propose closing because no design is blocked on them (W14).
- **P91** and **P92**: P95 delivered the shelf and the JSON envelope, so each is half done; I kept both with the
  remainder named. The PO may prefer to close them and let a design pull the rest.
- **P39**: the "Research it" miss is still in `_op_need`; I did not run it (the store is off limits to me), and P96's
  `--match` may have made the item moot.
- **P100's slice**: it sits on no slice in `STORY_MAP.md` and the orphan test needs one; I chose 1b. The PO may want
  a new slice for it.
- **P101 against P102e**: both are "a discovery skill"; the PO's order names P101 with P100, so I kept both.
- **P58 and P73 repo**: the brief says `bin` only for B-items; their fixes are in the bin's tree.
- **P72**: kept, but it may be closed by the P102a freeze commit if the PO counts Kanban as the whole answer.
- **P102's Status** is written as Build for the record; if the check counts epics, it should read Idea.

## Confirmed by the PO, 2026-10-05

As proposed, with three changes: **P101 merged into P102e** (one discovery-skill story, in the tools chore before P100
needs it); **P58 and P73 to the bin** (the README, the bring-up scripts and their verdict logs live there; spark takes
the verdict pattern later if a second project needs it, W14); **P91, P92 and P72 kept with their remainders**. The
closes (P80, P81, P93), the merge of P70 into P102 and the four parks stand.
