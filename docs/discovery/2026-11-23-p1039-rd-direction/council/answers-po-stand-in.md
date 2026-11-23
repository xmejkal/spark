# P1039 council: the PO's stand-in

Fable 5.2, 2026-11-23, about 16:40 to 17:00 CET. Read-only. I answer from the PO's recorded words. Each answer is
"delegated to the council, the PO's to change". It is never his own word. Where his words do not settle a question,
the line says "not settled by his words" and gives my best reading.

Read: the brief, risks-and-tests.md, items.md, direction.md and council/refuter.md in full. #1522 with its four
comments. scrum/VISION.md, AGENTS.md (Principles), scrum/README.md (the token budget), W14. The memory notes
(architecture direction, UX and AI-UX, council answers, team way of working, showcase and teaching, no work that gets
redone, delegate row decisions). The bodies of #199, #213, #153 and #545. never-assume.md, rule 7.

## His words that the answers stand on

- W1, 2026-10-26 (VISION, Versions): "finish the MVP make sure it works, do the refactoring and right after it the
  LangGraoh will be next, then RAG fr example." And: "we really need to get to the Langgraph/RRag mvp asap, so I can
  show it as a project".
- W2, 2026-11-22, 08:24 CET (the store's hand-off, quoted by the refuter): "Remember we don't want to overcomplicate
  things before the MVP of the whole flow works, we are trying to avoid slop. However, we do want t fix gaps and
  bugs." And: "We're also running out of tokens, so we really need to prioritize".
- W3, 2026-10-31: "we want it to be ready for the future as far as architecture goes ... but now we only implement
  the micropython and easy cli and skills version".
- W4, 2026-11-16 (P834): each MVP card takes the small seam that keeps other hosts open, never the other host itself.
- W5, 2026-11-23 (#1105): the core ready for streaming and async; the CLI works fully first; consumers "like when
  we'll want to use Langgraph etc or make a live web page or an SSE MCP".
- W6, 2026-10-31: a stop and its question "must work through every interface (CLI, MCP, LangGraph), so it is a coded
  result in the envelope, and each interface asks in its own way".
- W7, 2026-10-13 (#199): "usable ... in agentic systems or in just claude code and other ais ... we can just take
  notes and get back to the more advanced options later".
- W8, 2026-10-11 (#153): an inventory of what spark can do, "mostly ai, that it can really use the system", as "a
  chore for after the big refactoring or as part of it".
- W9, 2026-10-17: "We don't want bloat". AGENTS.md: "Plans shrink with distance", "Free, few and local", "Name any
  cost and ask first". W14: nothing is built on paper before a project reaches for it.
- W10, 2026-11-06 (memory): spark goes with his CV for an AI developer job, shown "being used by langgraph, maybe RAG
  integration".
- W11, #1522: "really high level". Needed by: "No build."

## Q1, part 1: importance of each assumption

| id | importance | one reason |
| --- | --- | --- |
| A1 a direction has a pull today | high | W14 is his own pull rule, and Q4 turns on it. The refuter shows its test must change (part 2) |
| A2 another harness can drive the journey with `--json` and SKILL.md alone | high | He asked for "generally runnable" twice (W7, #1522). If it is false, the seams alone do not give it and Q8 (a) comes first |
| A3 an 8 GiB model reads spark's answers | low | His words are "Maybe in the future". No decision of today rests on it |
| A4 reruns of one task agree | low | It matters only after A5 holds. The refuter shows that "3 of 3" cannot tell a flaky task from a steady one |
| A5 an eval result changes a decision | high | Tokens are short (W2) and Fable is spared. An eval that nobody reads is slop, and W14 names an eval harness as its example |
| A6 agents fail because the skills do not teach | high | He asked it himself on #1522 and on #153 (W8). The refuter shows the row sort undercounts this cause, so its test is weak, not its weight |
| A7 the directions do not slow the MVP | high | W2: the MVP of the whole flow first, and tokens are short |
| A8 his gadgets need the line past the bench | low | The order is already his: the PCB comes "only later, when the circuit is tested and the firmware good" (VISION, 2026-10-03) |
| A9 today's split serves a second interface | high | "One core, many interfaces" and the showcase (W1, W10) stand on it. P417 #545 is his ordered test |
| A10 the gates hold in any harness | high | A flash or a network step with no yes is a thing that cannot be undone. ★C11 undercounts: at least seven operations, not five |

## Q1, part 2: the riskiest assumption and its pass line

Keep A1 as the riskiest. Change its pass line. Reasons: the refuter's bias point holds (walk rows from Claude Code on
a cloud model can show no harness cause and no model cause). ★C6 is refuted, so "the evidence of use is nil" is too
strong. And the pull that his own words name is the showcase (W1, W10), which neither arm of the old line could see.
A9 is next in line. Its test is P417 #545, in his order of 2026-10-26.

The pass line, in full, set on 2026-11-23 before any result:

> A1 passes for a direction when one of three arms holds for that direction.
> Arm 1, his own use: the PO names at least one dated occasion and its step that the direction removes (Q13 to Q16).
> Arm 2, the showcase: the PO names who is to see spark, what they must see run, and by when, and the direction
> gives that (for example spark sent with his CV and shown as a LangGraph node, an MCP tool or in a second harness).
> Arm 3, the walk rows, for two directions only (the agents' knowledge, and the line's end past the deploy): at
> least 20 % of the rows that were read have that cause and no card of the MVP removes it. The count names how many
> rows were read and which diaries were left out.
> The rows are no test for harnesses, a local AI or evaluation. For those three only arms 1 and 2 count.
> A direction that meets an arm gets the first spike, and at most two spikes are filed. A direction that meets no arm
> gets no epic and no spike now, and its seams stay on P793 #1105.
> A miss of arm 3 says nothing about the other three directions, and it does not close Q9, because a row records
> only what an agent noticed.

The 20 % has no source (the refuter). I keep it only so that a number stands before the result. It is his to change.

## Q2 to Q12

| Q | pick | reason |
| --- | --- | --- |
| Q2 the order against the MVP | (a), with (b) only for a test that needs no council and no build. P417 and P419 keep their place from W1: after the refactor | W1 and W2 give the order: the MVP, the refactor, LangGraph, RAG. #1522 is "No build". What proves the MVP is not settled by his words: VISION names his walk to a working gadget, kept by `tests/test_journey_basic.py`, and no written verdict says the MVP is done (★C25). That verdict is his |
| Q3 what "factory" means | (a) the product's line, its end first. (c) is a no-go | VISION (2026-10-03) and AGENTS.md describe one conversation from needs to parts, firmware, PCB and 3D, and the firmware decision rules out (c). Not settled by his words: he said only "how to make it a software factory". The refuter notes a third reading that no option holds: a line for projects that are not gadgets |
| Q4 how the directions enter the backlog | (a) now. (b) only when a direction meets an arm of the new pass line, and each filing is his yes. Do not close #199 | W9 ("We don't want bloat"), "Plans shrink with distance" (a later version is a line), and W2 on tokens. The open cards carry the directions (★C28, as "open cards with matching titles"). #199 holds his own words, and the refuter shows the spike that would absorb it is not filed |
| Q5 the seams on the core work in flight | (a), as lines on the open pieces of P793. Two conditions: S2 covers every network operation, listed from the code, not "five". A piece takes a seam only where it already touches that code | W3 and W4: the small seam, never the other host. The 2026-11-17 council's line: no card per finding, add a line to an open card. ★C11 is partly right (the refuter). W2 drops generality that the flow does not need yet, so no separate wording pass. The lines are checked against the core-gaps finding first, because the architect did not read it |
| Q6 the split of the core from its interfaces | (a), as a direction. It stays an opinion until P417 runs (A9) | W5: the CLI works fully first, the core ready for streaming. His words of 2026-10-22 on #545: "langgraph or ... a plugin or an mcp, skills, whatever, it would just be the interface". "No server before the CLI and a stdio MCP are whole" fits "when we'll want". The refuter is right that (b) does not conflict with his words. (a) adds only the skills and the neutral sentences |
| Q7 harness generality | (a) now: a property that the seams and the open formats keep. Not (c). Offer him the refuter's trial with no install: the harness that is already installed runs `flow.py show --json` on a fixture, scripts only. It runs only on his yes. "Hermes" is the harness | W3 and W7 ("take notes and get back ... later"). ★C6 is refuted, so Q7 (b)'s cost "an install" is wrong, and FE-12 puts a scripts-only run at about 0 code. The trial uses his own account, so it waits on him. His sentence is "other harnesses, like Hermes or others", so he names Hermes as a harness. Whether he wants to run a second harness himself is not settled by his words |
| Q8 the form of the agents' knowledge | (a) as a direction. No rewrite before P793's pieces 1 to 3 land, so (c) is the state until then | AGENTS.md: "An agent prompt never repeats its logic". W3 names "cli and skills" as the version built now. His rule of 2026-11-16: no work that gets redone. The refuter: "a harness that reads skills walks the journey" is not shown (a trust step, `${CLAUDE_PLUGIN_ROOT}`), so it stays a direction |
| Q9 the guard for the agents' knowledge | (b), on P200 #153, when the catalogue (S3) lands. Now: the hand fixes of (a) (the stale entry page, the untaught flags). Do not wait for the row sort. Not (c) | He asked for this system himself (#1522, his fourth comment) and timed it on #153: "after the big refactoring or as part of it" (W8). The refuter shows that ★C15's second reading is refuted and that the row sort undercounts the cause by construction, so (a)'s test cannot decide. W2: gaps and bugs are fixed now. (c) makes the skills longer, which is slop |
| Q10 evaluation and model choice | (a): no scored eval now. He first names the row and the result that changes it. (b) follows only on his yes, with its cost named | W14 names an eval harness. "Name any cost and ask first". Walks stay without a score (the PO, 2026-10-31). His words of 2026-10-15: experiment, "but know why and evaluate". Not settled by his words: the row, the ceiling, and whether a report leaves the Mac. My reading of where to look first: the four parts of the table that "stand on no words of his" (scrum/README.md) |
| Q11 a local AI | (a): one line under "later" | "Maybe in the future, we might want to run it on local AI" (#1522). No approved work needs the download. The machine is his to name, and other hardware is a cost |
| Q12 where the person's yes lives | (a) for every network operation, listed from the code. The yes to a flash stays as it is: his own terminal, or a grant. (c) is no | W6: a stop is a coded result in the envelope, and each interface asks in its own way. never-assume.md, rule 7, already rules out (c): a yes that another program collected "is a relayed yes (P675), and it is neither of the two". ★C11 undercounts (the refuter), and the guide says an allow rule or auto mode already runs these with no prompt |

## Q13 to Q17

his only.

## Questions that the PO must answer himself

- Q2, the first half: whether P934's run of 2026-11-22 proves the MVP. No written verdict exists, and the README's
  table follows from it.
- Q3: what he meant by "software factory". The word is his, he said it once, and one reading (a line for projects
  that are not gadgets) is in no option.
- Q7, the first half: whether he wants to run a second harness himself, and whether he uses the one that is
  installed. The trial with no install uses his account.
- Q10: the row of the model table, the ceiling for paid runs, and whether a report leaves the Mac. These are money
  and privacy.
- Q11: the machine. Other hardware is a cost.
- The pass line's arm 2: who is to see spark, and by when (the CV date). His memory note says to ask him for that
  date when it decides an order.
- Not a numbered question: whether the names of his installed software go into the public file (the refuter's note).
- Q13 to Q17, and the confirmation of the final understanding, and the yes to file any card.
