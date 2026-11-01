# P479 event seam: plan council, round 2

Card [P479 #657](https://github.com/xmejkal/spark/issues/657). Round 2 ran on 2026-11-01 after round 1's fixes: PO
assistant with tech lead and senior architecture on the everyday model, the refuter on the strongest. Each finding was
checked in the code. Rows 37 to 49 of `docs/observations/rows/p479-event-seam.md` hold them.

## PO assistant and tech lead

Findings: make each "You decide" item a question and take the rename out of item 1. Add no Reporter row to the names
table. Say "result lines" and list the meanings of "report". Split E2a from E2.

What the plan did: four questions in the box, the rename as a section 3 row for W4-2. No role row, because the Strategy
row at `developing.md:302` already allows a plain noun. Rule 2 says "result lines" and the glossary row lists the
meanings. E2a is its own PR with its own Done when.

## Senior architecture

Findings: the source of the two-space indent is unclear at `deploy.py:243` and `board_look.py:390` (verified). One event
is one line. The world's report is the only path. Severity, phase order and MCP progress enter later.

What the plan did: risk 3 and E2a's Done when name the indent per site. The `text` field holds one line. Rule 5 is the
only path. One paragraph under the later Reporters holds the MCP notes. Nothing is built.

## Refuter

Findings confirmed: cite `test_core.py:276`. Risk 3 claimed too much, since the goldens stop at the gate. A Reporter row
needs a `ROLES` entry, which the no-row decision removes. `FakeOutsideWorld` needs a `reporter=` parameter, and E2
breaks `test_core.py:287-288` and `test_deploy_json.py:455`.

Rejected: `for_json` breaks X2. `_may_print` lets a `TERMINAL_CLASSES` class print, so the class is exempt.

What the plan did: each confirmed finding is in the plan, and the rejection has row 49.
