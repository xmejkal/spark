# P776: the 565 raised observation rows, closed in one pass: rows

Card: [P776 #1074](https://github.com/xmejkal/spark/issues/1074). The PO, 2026-11-12: "Are we even ever processing all the logs and
notes and observations?", then "let's now take a little break to process what we have and then set up the process so that we
actually reflect these notes", then "based on what we find out, lets delete old stuff and create a few cards on what actually
still matters and adjust the overall process so that we really do reflect our notes regularly but also get rid of rules and
code and tools that we don't need anymore so we don't gather slop". 2026-11-12.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | 201 rows files held 4716 rows, 565 of them `raised` and never closed (303 from October, 262 from November); the oldest file is of 2026-10-18 | probe | verified | `git log --diff-filter=A` per file |
| 2 | a sample of 30 raised rows (10 per age band): 7 already a card, 7 fixed since, 7 valid with no card, 7 stale notes, 2 the lane's, 1 the PO's; age does not thin them, because most name product gaps | probe | verified | the three bands gave the same shares |
| 3 | a classifier sorted the 565: 178 name a card (89 closed, 87 open), 51 name a symbol or file that is gone, 336 need a reading | pass | verified | `raised-rows.tsv` in the session's scratchpad |
| 4 | four readers (Sonnet) judged the 387 read rows: 93 valid, 183 stale, 55 a card, 27 the PO's, 18 the pixel-games lane's, 11 fixed; most VALID verdicts rest on the row's text, so the groups were checked before a card was filed | pass | verified | `judged-1..4.tsv` |
| 5 | the 93 valid rows fell into 64 groups; the council (this session) filed 9 cards from 27 groups, marked 7 groups tracked by P331, 3 by P682, 2 by P498, 1 by P775, 1 by P726, 3 fixed (P387/P397 board-own parts, P464 LED level, --drawer's `held by` and --offer KEY), 3 the PO's, 21 dropped with a reason (an edge case or a wording that serves no board today) | council | acted | P777 #1075 to P785 #1083, in Idea; `cards.tsv`, `judged-5.tsv` |
| 6 | every raised row's status changed in its file, the trail kept: 138 tracked, 124 closed (done or fixed), 204 dropped, 46 filed, 18 handed to the lane, 32 stay raised for the PO; 2 malformed rows untouched | pass | acted | `close_rows.py`; this PR |
| 7 | the inventory (Opus): 9 rule contradictions (rules.md :55-56 vs :57-58, :65-67 vs :88 vs :90-91, :101-103 "sweep" vs :72, :84 doubled; AGENTS.md:34 "waits for v0.13" is dead, :48-49 Miro-in-the-PR vs rules.md:40-43; WORKING_AGREEMENTS.md:338 factcheck nobody runs); match_eval.py has no caller and P385 ruled "prune"; p215-ready.json names a gone file; 128 rows across 47 tables anchor nothing; learned-rules.md holds about 169 entries, 19 repeats, 17 already rules, 5 impossible now | inventory | verified | the report's file:line per item |
| 8 | the 128 dead-anchor rows and p215-ready.json are removed: they guarded nothing (the anchors tool refused each), so the sweep lost no net; `--anchors` over the 261 tables refuses nothing: the one row left (p191-breadboard, a `--keep` mutant that did not compile since its line grew) got a replace that compiles | pass | acted | this PR; P682 #918 is done by it |
| 9 | tools/match_eval.py and tests/test_match_eval.py removed with their three mentions (needs.py, matching.py, test_matching.py) | pass | acted | this PR |
| 10 | the rules contradictions and the AGENTS.md lines are rules changes: the PO's to merge; factcheck is one pair (the tool and WORKING_AGREEMENTS:338 go together, or the team runs it again); learned-rules.md is compacted after his OK | pass | raised | the reply to the PO lists each |
| 11 | the process: a raised row names its destination (a card, fixed, dropped because...) before the PR merges; the rows file holds acted, raised and rejected rows only; the day close reads the day's raised rows and the new learned rules; a pruning council at each wave or epic end | proposal | raised | rules.md, the PO's to merge |
