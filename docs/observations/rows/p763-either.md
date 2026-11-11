# P763 a cited question is `either`'s, so a person at the terminal is asked too: rows

Card: [P763 #1050](https://github.com/xmejkal/spark/issues/1050), XS, under P735. Plan `~/.claude/plans/p763-either.md`. Rows 1 to 7 are the plan
refuter (Fable), 8 and 9 the implementer, 10 to 12 the PR refuter (Fable). 2026-11-11.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `AGENT if cites else EITHER` (research_source.py:47) is the only place research makes an AGENT question; the import can go | plan refuter (Fable) | verified | grep AGENT under scripts: research_source.py, replies.py (the definition), deploy_gate.py (its own import); the import is dropped |
| 2 | the terminal prompt shows the citation for an EITHER question and the Reply carries `cites`; the fold writes `read from <doc> <at> by typed in a terminal by ada`, so the new test must assert the full string | plan refuter (Fable) | acted | the test asserts `read from x-dimension-v1 page 1, typed in a terminal by ada` (see row 3) |
| 3 | two wording defects the plan would freeze: `SEE_PAGE` = "see %s, page %s" with `at` = "page 1" prints "page page 1"; `READ_FROM` = "read from %s %s by %s" with TYPED_BY prints "by typed in a terminal by" | plan refuter (Fable) | acted | SEE_PAGE is "see %s, %s" and READ_FROM "read from %s %s, %s"; test_replies.py:112 and three test_research asserts follow; replies.md says the two sentences |
| 4 | after the change `VALUE, EITHER,` is unique in research_source.py; only p737-research row 19 anchors on "AGENT if cites"; p737-live's rows stay anchored (THICK is AGENT) | plan refuter (Fable) | verified | the row is inverted (find `VALUE, EITHER, why_of(need),`); `--anchors` on p737-research and p737-live: 37 present once |
| 5 | `needs_person` (research_part.py:134) and `order_open` test PERSON only, so EITHER changes neither; `--json` builds no terminal | plan refuter (Fable) | verified | no change |
| 6 | stale "agent" claims live only at replies.md:12,42,59 and research.py:27; the discovery's design.md (2026-11-10) says AGENT as a dated record | plan refuter (Fable) | verified | the four are rewritten; design.md stays as a record of the day |
| 7 | the plan's title says "anybody's" beside `either` and "whoever is there" | plan refuter (Fable) | acted | one word: `either`, glossed "whoever is there" (replies.py:31) |
| 8 | the new live test's input of one line made the terminal stop after the second question (end of input is Ctrl-D), so two prompts showed, not three | implementer | acted | the input is one value and Enter twice |
| 9 | `physical_proof` carries one `source` for the block, not one per key | implementer | acted | the test asserts `physical_proof.source` |
| 10 | the suites pass and the new test kills the revert: `mutate.py --copy --for research_source.py` caught both rows in 424 s, and an in-memory revert fails the test with `0 != 3` | PR refuter (Fable) | verified | `Ran 218 tests` OK; the refuter ran one mutation run on its own, against the rule of `--anchors` only per PR (a brief gap: the brief allowed it "if safe"); the sweep will run the rows again |
| 11 | no stale text: SEE_PAGE, READ_FROM, "page page" and "by typed" live only in the new definitions, the inverted row and this file; the deploy's consent calls `ask(question.text)`, never `_prompt`, so SEE_PAGE reaches no deploy prompt | PR refuter (Fable) | verified | replies.py:214, deploy_gate.py:76-80; the discovery's design.md:200 is a dated record |
| 12 | `cites.at` from a hand-written replies file is free text, so `"at": 3` prints `see doc, 3`; replies.md:15 called `at` "the page" without its form | PR refuter (Fable) | acted | replies.md:15 says `at` is the words `page 1`, as the prompt and the source repeat it |
