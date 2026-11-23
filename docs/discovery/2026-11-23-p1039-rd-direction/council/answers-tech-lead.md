# P1039 council: the tech lead's answers (Opus, 2026-11-23, about 16:50 CET)

I answer for the PO from the delivery side. Each answer is "delegated to the council, the PO's to change". I read the
discovery's brief, risks-and-tests.md, items.md, direction.md and council/refuter.md in full. I also read #1522 with
its comments, #1105's body, scrum/VISION.md, the token budget in scrum/README.md, `tools/board.py status`, FE-11,
FE-12 and his memory notes.

Delivery facts I lean on, read today:
- `board.py status`, 16:4x CET: 409 open. "filed in 7 days: 174, closed: 95". "Ready is down to 2". P934 #1323 and
  P828 #1186 wait on the PO. Seven cards are in flight, among them P1036 (storage stage 1). P1035 #1518 (core piece 3) is
  in Ready.
- P793 #1105 already holds P200, P217, P417, P419, P481 and the other interface cards. Its Done-when is one Operation
  from the CLI, an agent prompt, MCP and LangGraph with no logic outside the core.
- The token budget: "A full council (about 90 M input tokens) runs only where a council belongs". The allowance is
  "one run per card in flight ... at most one full council a day. Anything bigger is asked first". The refuter shows
  the 90 M has no measurement on file. Today already ran two full councils (P1033, P1039).
- His words, 2026-11-22 08:24 CET (the store's hand-off, quoted by the refuter): "do not overcomplicate before
  the MVP of the whole flow works, avoid slop, fix gaps and bugs, and prioritize because tokens run out (my summary of
  his two sentences, which the refuter quotes in full).
- His CV words, 2026-10-26 and 2026-11-06: LangGraph and RAG on a clean core, "so I can show it as a project".

## Q1, part 1: importance of each assumption

| id | importance | reason |
| --- | --- | --- |
| A1 | high | It decides whether anything is filed at all, and the backlog takes 174 in and 95 out a week. |
| A2 | low | Q7 (a) holds whatever its result, and seams S1 and S2 are worth doing for the MCP and LangGraph consumers anyway. |
| A3 | low | No decision now waits on it. The Mac has 8 GiB and no local runtime, so Q11 stays a line under "later". |
| A4 | low | It matters only after A5 names a reader. The refuter shows 3 of 3 cannot tell a flaky task from a steady one. |
| A5 | high | W14 and two pruned evals: no eval gets built, run or kept unless a row of the model table waits on it. |
| A6 | high | A knowledge guard in the hook is a cost on every PR forever. It must rest on a cause, not on a count of names. |
| A7 | high | This is the delivery risk itself: Ready is at 2, P934 waits on him, and tokens are short by his words. |
| A8 | low | Q3 (a) puts the line's end first whatever its result, and the PCB and enclosure epics are far off. |
| A9 | high | P793 is in flight. If the split is wrong, the pieces built now are redone, which his rule of 2026-11-16 forbids. |
| A10 | high | A safety gate. The refuter finds at least seven network operations whose yes is a prompt, and auto mode skips it. |

## Q1, part 2: the riskiest assumption and its pass line

Keep A1 as the riskiest, because it gates the inflow. Change its test. The refuter shows that part 2 cannot score
the harness, local-model or eval directions: every walk ran in Claude Code on a cloud model. ★C6 is refuted, so "no
harness installed" is no longer evidence of no use. The refuter's rival also stands: the showcase (VISION.md,
Versions, "so I can show it as a project") is a pull that neither arm can see.

Pass line, in full, proposed 2026-11-23 before any result:

> A1 holds for a direction when, by R12 (2026-11-29), at least one of these is true. (1) The PO names a dated
> occasion in his own use (Q13 to Q16) and its step, which the direction removes. (2) The PO names a dated
> showcase or CV use that needs the direction (for example a LangGraph or MCP run for P417 #545). (3) For the
> agent-knowledge direction only: one read-only agent on Sonnet sorts the 72 walk rows (P711's 32, P934's 14 and 26)
> by cause, and at least 4 rows have the cause "no agent page named the tool or flag that existed", which no card of
> the MVP removes. The walk rows count neither for nor against the harness, local-model and eval directions. Below
> all three: seams only (Q4 a), no epic and no spike. The sort runs under #1522 with no card, inside the allowance,
> and its tokens are named before it runs.

The "4 rows" is my number, not sourced. It is low on purpose, because the refuter shows that rows undercount an
untaught name by construction.

## Q2 to Q12

| Q | pick | reason |
| --- | --- | --- |
| Q2 | (a), and the read-only tests run now | Ready is at 2 and P934 waits on him. His words of 08:24 CET: no complication before the MVP of the whole flow works. Tests with no council and no card (the A1 test, the gate list of A10) run under #1522. Which run proves v0.10 is his. |
| Q3 | (a), the line's end first | The end is small: the deploy reader reads the store's deploy record (★C19, in Found on the way). It fits the flow's phases with no second architecture. (c) breaks the firmware decision. |
| Q4 | (a) now, (b) only after A1 passes | 43 open epics and 174 in against 95 out a week (★C24). Cards with matching titles exist (P217, P227, P417, P200, P711). The refuter says "matching titles", not "cover"). Do not close P217 #199: it holds his words. |
| Q5 | (a), with two conditions | Lines on open pieces add no inflow. Conditions: S2 counts the network operations from the code (FETCHES), not the doc list (the refuter: at least seven). No line goes onto a piece already in Build or Ready (P1035 #1518), so no Done-when moves under a builder. |
| Q6 | (a) | It is P793's own order, and it keeps "the CLI works fully first" (#1105, 2026-11-23). The refuter shows (b)'s "no server until a case needs it" does not conflict with his "when we'll want". (c) breaks "free, few and local". |
| Q7 | (a) now. The zero-install probe is offered, not run | ★C6 is refuted, so FE-12's "about 0 code" probe exists: `flow.py show --json` on a fixture in the installed harness. It uses his installed software and his account, so it is his yes. No adapters per harness: each one is a set of files to keep on every change. |
| Q8 | (a) as the direction. No rewrite before P793 pieces 1 to 3 merge | A rewrite of 9 commands and 4 agent files now is redone when pieces 1 to 3 land (his rule of 2026-11-16). Until then (c) holds in fact. The trust step and `${CLAUDE_PLUGIN_ROOT}` in other harnesses are unknown (the refuter). |
| Q9 | (a) now. Later (b), as a line on the catalogue piece (S3), not a card | The counting method of ★C14 is not on file, so no guard can be built that reproduces it. A guard compares only declared names, and 11 Operations and 15 scripts declare none. Fix the stale entry page and `cost.py` by hand now (Found on the way). |
| Q10 | (a) | "tokens are short" and W14. Two evals were pruned. If (b) ever runs, 3 runs are too few: 0.8 cubed is 0.51 (the refuter). The ceiling and whether a report leaves the Mac are his. |
| Q11 | (a) | 8 GiB M1, no local runtime. The 84 s and 142 s figures are on a 128 GB M4 Max (the refuter on ★C27). No decision waits on A3. The machine is his. |
| Q12 | (a) | The existing deploy and grant pattern (Question, ReplyStrategy) carries over at a small cost per operation. The refuter: at least seven operations, and inside Claude Code an allow rule or auto mode already runs them with no prompt. The flash's yes stays typed in his terminal. (c) changes never-assume rule 7, which is his. |
| Q13 to Q17 | his only | account questions about his own use |

## Questions the PO must answer himself

- Q2, first half: which run proves v0.10. It is a version verdict, and a release is his by the rules. VISION.md
  names "the PO's walk of button-and-LED to a lit LED". Whether P934's run of 2026-11-22 replaces that is his.
- Q7: whether he wants to run a second harness himself, which "Hermes" he meant, and whether his installed software
  may be used for a probe or named in a public file. This is his intent and his machine.
- Q10: any spend on paid model runs, its ceiling, and whether an eval report may leave the Mac. Money and data.
- Q11: which machine the local AI is for. Other hardware is a cost.
- Q12 (c), if it is ever proposed: a change to never-assume rule 7 (the yes to a flash).
- The A1 pass line itself: the refuter found the proposed test biased, so the line the council sets is weaker
  evidence than his own. Also the RA lens's dropped question (council/risks-and-assumptions.md:103): the hobbyist's
  journey first, or showing spark as a project first. That ranks Q2 and Q4, and only he can answer it.
- Any edit of scrum/VISION.md (Q4 (a)'s "later" lines) is a change to his confirmed page. It goes to him as a PR.
