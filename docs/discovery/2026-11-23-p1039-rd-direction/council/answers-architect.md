# P1039 council: the architect's answers, for the PO

Fable 5.2, 2026-11-23, written at 16:41 CET (`date`). Read-only on the tree at 67071ff3. Every answer is delegated, the PO's to
change. I judged the synthesis fresh, with the refuter's report. Where I differ from the synthesis, the line says so.

## The short version

1. The riskiest assumption is A9, not A1. A1's result moves nothing now, and its test cannot see three of the five
   directions (refuter, finding 4). A9 carries every seam on the core work in flight, and no second interface ever ran.
2. No new epic and no new spike. P417 #545 already exists with the PO's words and his order. It tests the interface
   split, harness reach (a stdio MCP tool) and the trace's first caller in one spike.
3. The seam comment on #1105 gets shorter. S1, S3, S4 and S5 are already pieces of P793. Only S2 (the network yes,
   stated by effect) and S7 (one contract line) are new. S6 belongs to P417.

## One thing I ran (E, 2026-11-23, between 16:36 and 16:41 CET, in a scratch folder, removed after)

A second frontend of 20 lines, outside the tree. It imported `spark.core` and `ShowFlow` only, no `scripts/*.py`.
It built an MCP-shaped tool from the Operation's own declarations and ran it through `run_operation` on a copy of
tests/data/breadboard/walk-c6, with a Reporter of its own.

- The tool: `{"name": "show-flow", "description": "Say where a project stands, ...", "inputSchema": {...
  "project" ...}, "effects": ["reads"]}`.
- The answer equals `flow.py show --json` for the same folder in every key but one: `tool` (`show-flow` against
  `flow`, the name the CLI's own text gives).
- 0 lines changed in the core. `git status` stayed clean.
- What it does not show: `show-flow` reports no Event (0 arrived), declares `reads` only and asks nothing. No MCP
  or LangGraph process ran. So it is a weak yes for A9, for one read-only Operation.
- `next[0]` holds `op`, `argv` with absolute paths and `env` with the store's path. It holds no values. The core can
  parse the argv back (`values_of`, scripts/spark/flow/run_request.py:163), so an adapter is not stuck. The absolute
  paths are the open part (S7).

## Q1, part 1: importance of each assumption

| id | importance | one reason |
| --- | --- | --- |
| A1 | low as written | Its result changes nothing now: under Q2 (a) no direction leaves Idea either way, and the PO's order of 2026-10-26 already names the first spike. Its "no use" evidence is refuted (★C6; the wait was his own order, RA-5). |
| A2 | low now | No work in flight rests on it. A9 and A10 carry its costly parts. High on the day a second harness is in use. |
| A3 | low | No machine is named and no local runtime was found. It moves only Q11, which is one line under "later". |
| A4 | low | It matters only after A5 names a reader. Its line needs repair first: 3 of 3 passes a task that works 8 times in 10 about half the time (refuter, numbers). |
| A5 | high | One answer from the PO decides whether any eval is built (W14). Two evals were pruned already (★C17, corrected). |
| A6 | low as written | Its evidence is refuted (★C15, second reading), and a row sort undercounts an untaught name by construction (refuter, rival 3). The fix does not wait on it: a surface generated from the declarations cannot be untaught. |
| A7 | high | The MVP walk, P793 and these directions spend the same tokens. His words, 2026-11-22 08:24 CET: "we don't want to overcomplicate things before the MVP of the whole flow works". The check is free. |
| A8 | low now | It orders the PCB against the bench step, both after the MVP. The deploy that never shows as done (★C19) is an MVP gap and is fixed either way. Its test is his own account (Q14). |
| A9 | high, the riskiest | Every seam and every open piece of P793 rests on "no second design". It is read from the code. 15 of 27 CLIs are off the core and no second interface ran (★C7, ★C9). |
| A10 | high | A gate that lives in one harness's prompt is no gate in any other interface. "Five" became at least seven, and nobody listed the gates from the code (refuter, ★C11). The list is cheap and read-only. |

## Q1, part 2: the riskiest assumption and its pass line

Change it. Riskiest: A9, today's split serves a second interface with no other architecture.

Why not A1. If A1 fails, the directions wait as lines under "later", which costs nothing and can be undone. If A9
fails, P793's pieces, the event design and the seam list are aimed wrong, and that work is in flight now. A1's part 2
confirms Q4 (a) by construction (refuter, finding 4). A1 also cannot see the showcase job, which is on record: "we
really need to get to the Langgraph/RRag mvp asap, so I can show it as a project" (the PO, 2026-10-26, scrum/VISION.md).

The pass line, set on 2026-11-23 before any result of P417:

> P417 #545 runs as filed, at its place in the PO's order. LookAtBoard runs as a LangGraph node and as a stdio MCP
> tool, both built from the Operation's own declarations (name, summary, input_schema, effects). It passes when all
> four hold. (1) `git diff --stat` from the spike's start to its end is empty under scripts/spark/core/ and under the
> Operation's own area, except a change that an open piece of P793 already names (the catalogue, the END and FINDING
> event kinds). (2) The adapter holds no sentence, code table or rule of spark's: each line a person reads comes from
> the result or from an Event. (3) Each Event of the run reaches the adapter's own Reporter in order, before the
> result. (4) The stop for the person reaches the adapter as the core's coded answer, and the adapter collects no yes
> of its own for a flash (never-assume.md, rule 7). A miss on any of the four: Q6 opens again before the next piece
> of P793 is planned, and the finding names the change that the core needed.

The probe above is a result already seen. It is not part of this line.

The row sort (72 rows) is dropped as a gate. It costs tokens and cannot tell a harness cause or a model cause. The
account questions Q13 to Q17 stay, and they are his.

If the majority keeps A1, its pass line must read: "A1 holds for a direction when one of three is true. The PO names
a dated occasion and its step (Q13 to Q16, and whether he uses the second harness that is installed). Or his recorded
words name a job that the direction serves and a card that carries it. Or, only for the two directions a row can
show (the line's end, the agents' knowledge), at least 20 % of the rows have that cause. A miss in the rows closes no
direction, because every row comes from a walk in Claude Code on a cloud model."

## Q2 to Q12

| Q | pick | reason |
| --- | --- | --- |
| Q2 | (a), with (b) only for a free read-only test | The big scheme is his: "finish the MVP make sure it works, do the refactoring and right after it the LangGraoh" (2026-10-26). The seams are part of the refactor, so (a) does not block Q5. Free tests now: A10's list of gates and his account questions. **What proves the MVP is his only**: scrum/VISION.md names the button-and-LED walk, and P934 was another gadget. |
| Q3 | (a) as the default reading, (c) a no-go | (c) breaks the firmware decision. Every later stage fits as Operations and phases only as a reading (★C22 is H, refuter). **The meaning of "software factory" is his to confirm**: the refuter shows a fourth reading, software that is no gadget, which no option offers. Nothing in flight waits on it. ★C19's fix is an MVP gap, already noted for piece 6 on #1105 (15:17 CET). |
| Q4 | (a) | Not because of A1's test. P417 #545 is already the first spike, with his words and his order, and ★C28's cards hold his words for four directions. "A later version is one epic with the PO's words" (AGENTS.md): P1039 is that epic. Only his local-AI words have no card: one line under "later". Filing anything is his yes. |
| Q5 | (a), narrowed | One comment on #1105. S1, S3 and S4 are already pieces 6, 4 and 1, 2, 5 of the core-gaps finding, and S5 is the event piece named there at 12:54 CET: map them, add no line. New lines: S2, stated by effect and not as a list of five (every Operation that declares `fetches`), and S7 as one contract line. S6 goes to P417, whose card names the trace. S8 waits. |
| Q6 | (a), with two corrections | The probe and ★C9 say the split holds for one read-only Operation. Correction 1: (b)'s "no server until a case needs it" is the same rule as (a)'s, and the claimed conflict with his words is withdrawn (refuter, part 2). Correction 2: skills as the carrier are Q8's, not part of this order yet. Opinion: the core stays plain sync code, and an async host uses a thread and a queue Reporter. |
| Q7 | (a) | Generality is a property of the core and its seams. Its first proof is P417's stdio MCP tool, which any MCP client can call. The no-install trial (FE-12) is free of code, and it spends his other account, so it is his yes. **Whether he uses the installed second harness and which "Hermes" he means are his only.** |
| Q8 | (c) now | Differs from the synthesis. The home of the journey's knowledge is the core's own answers: `next`, a Code with its fix, `--describe`. "An agent prompt never repeats its logic" (AGENTS.md). After pieces 1 to 3 the commands shrink by themselves, and thin text ports cheaply to any format. A rewrite of 9 commands before that is work that gets redone (the PO, 2026-11-16). (a)'s claim that a skills reader walks the journey is unproven (refuter: the trust step, `${CLAUDE_PLUGIN_ROOT}`). |
| Q9 | (a), without the row sort as its gate | His question's honest answer: one direction is guarded (★C13). The other half comes as generation, not as a test on hand-written text: pieces 4 and 7 and P937 write the agents' surface from the declarations. Then (b) is one small hook test over the catalogue. The stale entry page is a docs fix now. (c) no. |
| Q10 | (a) | W14 names an eval harness as its own example, and two were pruned. An eval is a consumer outside the core, graded on `--json` facts, and spark calls no model. **The row, the ceiling for paid runs and whether a report leaves the Mac are his only** (money and privacy). If (b) ever runs, A4's line needs more than 3 runs. |
| Q11 | (a) | No local runtime was found, and the Mac has 8 GiB. What serves a small model is what serves every interface: a small answer with its next step. **The machine is his only.** |
| Q12 | (a), stated by effect | His rule of 2026-10-31 for a stop that needs the person: it "must work through every interface (CLI, MCP, LangGraph), so it is a coded result in the envelope, and each interface asks in its own way". Inside Claude Code an allow rule or auto mode already runs the network steps unasked (docs/guide/agents.md:74-75), so (b) is weaker than the brief says. (c) is already ruled out: a relayed yes "is neither of the two" (never-assume.md:166, P675). How the network yes is given (each run, or a standing yes in the store's settings) is S2's own small design, because `build-board` declares `fetches` and is pre-approved today. |

## Q13 to Q17

His only.

## Where the PO must answer himself

- Q2, first half: what proves the MVP. It is his verdict by scrum/README.md, and the vision names another walk.
- Q3: what he meant by "software factory".
- Q7: which "Hermes", and whether he uses the second harness. Also his yes for a trial on his other account.
- Q10: the row of the model table, the ceiling, and whether a report leaves the Mac.
- Q11: which machine.
- Whether P417 moves earlier. My recommendation: right after pieces 1 to 3 and before the event piece is built,
  because P417 is the only test of that design's consumers (his words on #1105, 12:55 CET). His words of 2026-11-16
  put the CLI first, so the order is his.
- Every filing, and the confirmation of the final understanding.

## What I checked (file and line)

- The effect words: scripts/spark/core/operation.py:31. The tool schemas: operation.py:105-117.
- Consent is given only with `asks`, and `fetch` only with `fetches`. No consent hangs on `fetches`:
  scripts/spark/core/outside.py:85-87.
- `fetches` is declared in five modules: build/build_board.py:56, sourcing/research/research_part.py:145,
  sourcing/resolve_sources.py:25, sourcing/fetch_documents.py:31, sourcing/find_documents.py:73. scripts/tools.py
  and scripts/check_vendor_pins.py name neither `run_cli` nor an effect (grep, no line), so their network step is
  outside the effect words until they move onto the core.
- Three `parts.py` network flags: tests/test_routes.py:491. `research.py`: commands/research.md:126. The allow rule
  and auto mode: docs/guide/agents.md:71-75.
- Two event kinds: scripts/spark/core/events.py:14. The trace is None by default: scripts/spark/core/cli.py:41-43.
- The step's fields: scripts/spark/core/result.py:33 and outcomes.py:114-121. The argv parses back to values:
  scripts/spark/flow/run_request.py:163.
- The relayed yes: docs/guide/agents/never-assume.md:153 and :166.
- The pieces 1 to 8 and the PO's words of 12:54 and 12:55 CET: the comments on #1105 (`gh issue view 1105`).
- P417 #545: open, in Idea, a sub-issue of #1105, with his words of 2026-10-22 and "the core does not change".
- The MVP's written proof and the big scheme: scrum/VISION.md, Versions.

## What I did not check

- The 72 walk rows, the MCP elicitation page, and the second harness on his Mac (the main session reproduced it).
- P1033 #1515's storage design. I judge no seam for it.
- Whether `check_vendor_pins.py` is one of the nine inner tools that stay off the core.
- The async opinion under Q6. It is a reading of the code, not a run.
- P1004 #1463's body (the main session reproduced it).
