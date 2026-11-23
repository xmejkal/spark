# P1039 council: the refuter, second pass

Fable 5.2, 2026-11-23. `date` printed 16:48 CET at my first check and 16:56 CET at the last one. Read-only on the tree at 664aac84. Scope: the sections changed since 67071ff3 (`git diff 67071ff3 HEAD` on the folder), parts 2 to 4 only. Every line below was read or run by me in this pass. One experiment ran in a scratch folder outside the tree, removed after. Nothing here decides anything.

The five findings that matter most:

1. The option letters changed after the council answered. The three agents read the brief at 67071ff3. There Q3 (c) was "an unattended line" and Q8 (c) was "no change". In the revised brief Q3 (c) is "a line for software projects that are not gadgets" and Q8 has no (c). So the tally's "Q3 ... (c) is a no-go" now rules out a reading that two of the three agents left to the PO, and D3's "Q8: (c) now" names an option that does not exist.
2. D2 and A1's test disagree. D2 records a rows arm ("20 % or 4 rows", his to set). The brief's Test line and A1's row say "The walk rows are no longer part of it". The pass line in the brief is none of the three in the answer files, and its "A missing answer is not a fail" is in no answer. D2's "four conditions" for A9 are not in A9's row. D3's "not gated on the row sort" for Q9 is not in A6's row or in items.md ("waits on A6").
3. "No pruned eval scored an agent" is wrong. The suite pruned on 2026-09-29 scored a model with the plugin against a baseline with none, and its result changed a decision (commit 2aad7674). The phrase is ★C17's keep words and stands in the Riskiest paragraph, Q10, A5 and J3.
4. Five questions read "answered D3 (delegated)" while the council says the question as worded is the PO's only: Q10 and Q11 whole, Q2's first half, Q3's meaning, both halves of Q7. The header still asks for Q1, Q4 and Q5, and the Hand-off says "Q1 to Q18 are open".
5. `build-board` does not declare `fetches`. The architect's answer and the tally's Q12 row say it does and ask for "a small design first" on that ground. Line 56 is the effect list of the `research` step that the build names in `next`. Four modules declare the effect, not five. My first report wrote "declared in five modules", and that line was loose.

## 2. Summary against detail

The first pass's verdicts. All 14 "partly" verdicts, the refuted ★C6 and ★C14 are carried into the brief's claims, each with my sentence or close to it. D4 holds: `git diff --name-only e0c0dc77 HEAD` outside the folder gives 24 files, the same 24 that D4 lists and that the merge f22981ab brought. Not carried, or carried in one place and not in another:

- ★C2: verification.md:38 still reads "the commands and agent files are in Claude Code's formats", and the first diagram of direction.md has the node "9 commands and 4 agent files in Claude Code formats" beside "agent knowledge in open formats: 3 skills". ★C2 itself now says frontmatter and variables with plain Markdown bodies, and that 12 of the 16 files name the plugin's variable. Nobody checked that the 3 skills carry none of it.
- ★C3: verification.md:39 still reads "the core's own sentences name Claude". The claim now opens "The core's code names Claude", and its count is over scripts/ as a whole, which holds the CLIs and every area. direction.md says "names in the areas' code". One of the three is right.
- ★C5: the sentence "It is an MCP client and runs on local models" cites council/refuter.md:21. That line says of those two parts "not re-read by me".
- ★C26: brief.md:26 keeps the comment "Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06)". The claim below it says the repository holds no measurement. A card named P900 did not exist on that date (first pass).
- The header: "Decision needed" was not revised. It reads "P1039 with at most two spikes". Q4 (b), direction.md and items.md read "at most three".
- Part 4 of the first pass: "nine earlier discoveries ... (probe, 2026-11-23)" still has no command. "3 of 33 facts verified" (direction.md stage 2, J1 step 2) still has no pointer. verification.md:59 still reads 64,430.

Claims stronger than their source, new in the revision:

- ★C17, "neither pruned eval scored an agent", with the keep words "no pruned eval scored an agent". My first report said this of `tools/match_eval.py` only. The other one: commit f6e2f7fa (2026-09-23) adds `evals/` with prompts and graders, "the two things this project taught that a model gets wrong". Commit 2aad7674 (2026-09-24): "finds-assembly-problems: with-plugin 0.67, no-plugin baseline 1.00, delta −0.33 ... That kills a line of work, and the backlog now says so." Commit 066c4af6 (2026-09-29) deleted `evals/`. That eval scored a model on a task with and without the plugin, and a decision read it. The smallest fix: "one pruned eval scored the plugin against a baseline, and its result ended a line of work (2aad7674). Nobody re-ran it. The other scored the part matcher." A5's evidence cell, Q10's tag, the Riskiest paragraph's "any named reader of an eval result", verification.md:56 and jobs-and-journeys.md:129 change with it.
- ★C15, "The walks hold no clean case of an untaught name". The source is my finding that the two cases the lens named are refuted. The claim's own caveat says 27 of the 32 rows were read by no lens. One lens read P934's diaries, and its two cases are the refuted ones. Change it to "No clean case was shown: the two named cases are refuted, and 27 of P711's 32 rows were read by nobody." The same words stand in the usability risk row, in direction.md's loop, in story-map.md slice 2 and in Found on the way.
- ★C11's caveat, A10's test and the tally's Q12 row: "five modules declare `fetches`", and `build-board` "declares `fetches` and is pre-approved today (scripts/spark/build/build_board.py:56)". Read today: line 56 is `effects=(READS, WRITES, ASKS, FETCHES)` inside `outcomes.step("research", ...)`, the step that the build offers next. The Operation's own line is :122, `effects = (READS, RUNS, WRITES)`. The four that declare it: research_part.py:145, resolve_sources.py:25, fetch_documents.py:31, find_documents.py:73. Whether the build's `runs` reach the network was not checked by anyone.
- ★C9's caveat and A9's evidence, "no second interface ever ran". The architect's answer file reports a run of a 20-line second frontend on `show-flow`. It is carried into no changed section, and its script was removed. I ran one of my own: it imported `spark.core` and `ShowFlow` only, built a tool from `name`, `summary`, `input_schema()` and `effects`, and called `run_operation` on a scratch copy of tests/data/breadboard/walk-c6. It returned an `OperationResult` with the data keys `fingerprint`, `guide`, `phases`, `stands_at`, 0 events, 0 findings and a `next[0]` of `build-board` with absolute paths in `argv`. `git status` stayed empty. I did not compare it key by key with `flow.py show --json`. So the sentence should read "one read-only Operation ran through a second frontend with no change in the core (the architect's answers, reproduced by the refuter). No MCP or LangGraph process ran."
- brief.md:5, "6 of which would change the decision (the council's high ratings, D2)". A rating by three agents is counted as the decider's. The template's cell was "— (decider)".
- The Test line, "the council kept A1 in D2 and left the number of arm 3 to the PO". The test as written has no arm 3.

D2 to D4 against the three answer files:

- D2's importance table is faithful: I compared the ten rows with the three files. The architect's qualifiers are dropped ("low as written" for A1 and A6, "low now" for A2 and A8, with "High on the day a second harness is in use").
- The pass line. Three lines exist in the answer files and a fourth in the brief. Arm 2: the PO stand-in wants the PO to name who sees spark, what runs and by when. The tech lead wants a dated showcase or CV use. The architect's reads "his recorded words name a job that the direction serves and a card that carries it", which holds today for the interface direction with no answer from him. The tally's "an arm for a named showcase need" hides that. The tech lead's line has a deadline, "by R12 (2026-11-29)". It is carried nowhere, and the brief's "A missing answer is not a fail" says the opposite.
- Arm 3. The tally gives a split of two (20 % against 4 rows). The architect's fallback line, written "If the majority keeps A1", also says 20 %, for two directions. So the count is 2 to 1 for 20 % and 2 to 1 for two directions, and the populations differ: "the rows that were read" (the PO stand-in) against "the 72 walk rows" (the tech lead). All three lines keep a rows arm. The revision took the rows out against all three.
- "A9 is next, with the architect's four conditions as its pass line" is tabled as the majority. One agent wrote the conditions. The PO stand-in says only "Its test is P417 #545". The tech lead says nothing on A9's line. A9's row still reads "It runs with 0 lines changed in the core", and story-map.md slice 4 the same. Condition 1 allows a change that an open piece of P793 names.
- Q5. "No line goes onto a piece in Build or Ready" is the tech lead's alone. The PO stand-in's condition is another ("a seam only where it already touches that code"). The architect says S1, S3, S4 and S5 are on #1105 already and only S2 and S7 are new lines. D3 records "S1 to S7 as acceptance lines" with the tech lead's condition. The tally names the architect's narrowing, and D3, story-map.md slice 0 and items.md do not.
- Q6. "All three" pick (a). The architect's (a) leaves skills out ("skills as the carrier are Q8's, not part of this order yet"). The brief's (a) holds skills. That is 2 to 1 on the very point the question asks.
- Q8. The picks are (a) as the direction for the PO stand-in and the tech lead. The architect picks "no change" and names another home for the knowledge, the core's own answers. D3 records "(a) as the direction" with no split.
- Q9. The picks are (b), (a) and (a). "Not gated on the row sort" is the PO stand-in's and the architect's. The tech lead rates A6 high because a guard "must rest on a cause, not on a count of names" and keeps the row sort as his arm 3. "All three in substance" hides that. The PO stand-in puts the guard on P200 #153, and the tech lead says "not a card".
- Q12. "(c) is a no · all three". The tech lead's words: "(c) changes never-assume rule 7, which is his."
- Q2. "Free" is the architect's word. The tech lead's read-only tests "run now", and one is an agent on Sonnet that sorts 72 rows, with its tokens "named before it runs".
- Q4. The PO stand-in's line says "at most two spikes are filed". The brief now offers three.
- Each answer file says what it read. None read the revised options, the new A6 test (a search from the names), A4's 5 reruns or the new Q18.

Delegated answers that go beyond the PO's recorded words:

- Q3 (c) as a no-go, through the changed letters (finding 1).
- The status "answered" on Q2, Q3, Q7, Q10 and Q11 (finding 4). The smallest fix: "option (a) delegated in D3. The question is the PO's".
- A2 as low. The one agent that answers from his words rates it high, on "generally runnable", said twice. The tally names the split, and D2 gives only the count.
- Q9's "hand fixes now" and the tech lead's sort "under #1522 with no card". The card says "No build", D0 says this session writes only in the folder and on #1522, and no item or board action holds either one.
- The order to delegate. D2 and D3 say "relayed by spark-main at about 16:10 CET". The folder holds no words of his for it, no pointer to a comment and no rule. `grep -i delegated` over scrum/README.md and scrum/WORKING_AGREEMENTS.md gives no line. The four comments on #1522 hold no such order: the one match for "council" is "how a walk or a council is scored".

## 3. Rival explanations

- "The council's majority answered Q2 to Q12." Rival: one opinion, read back. Each of the eleven majority picks equals the opinion that the brief printed for that question. The council's architect is a fresh instance of the agent that wrote those opinions and every cost. Two of the three agents run on the model of the synthesis. All three read one brief and one refuter report. The folder cannot tell agreement from a shared input, and no agent was asked to argue for another option.
- "A1 stays the riskiest (2 to 1)." Rival, the dissent's, and no file answers it: under D3's own Q2 (a) and Q4 (a) no result of A1 moves anything now. The revised line makes it stronger. A missing answer is not a fail, and a direction with no pull "waits as a line under later", which is Q4 (a). No outcome of the test changes a decision. A9's failure would redirect work that is in flight. The two votes for A1 reason from the inflow ("174 in and 95 out"), and ★C24's caveat says that ratio measures the filing rule too.
- "Q3 means the gadget's line" (from the vision of 2026-10-03). Rival: a new phrase seven weeks later can mean a new thing. He said it once, beside "whats next". Two of the three agents say that only he can say.
- "Evals die here unread" (W14, "two evals were pruned", A5 high). Rival: the first eval did its job. Its result ended a line of work on 2026-09-24, and then no further question asked for a rerun. That is a record of an eval that a decision read, the thing A5 doubts.
- "The split holds for a second interface" (the architect's probe, reproduced above). Rival: `show-flow` is the easiest case. It declares `reads` only, sends no event and asks nothing. The Operation of P417 looks at a board. The architect says so, and the brief carries neither the result nor its limit.
- "No local model runtime was found" (★C6, A3, Q11, cited by all three agents). The first pass gave no search for it beyond PATH. Checked now: 0 of ten common runtime names on PATH, 0 matches in the two application folders, in the home's dot folders, in the cache folder, in the package manager's lists and in the Python packages, and 0 model files of the usual format to depth 4 of the home. The sentence holds for that search. A runtime inside another application would not show.
- "A6 is high" and "the guard comes with the catalogue". Rival to both: after ★C15 no case is on file in either direction. The importance stands on his having asked, and the timing on his words of 2026-10-11 on #153 (the PO stand-in's quotation, not re-read by me). Neither is evidence that an untaught name cost a step, and the folder says rows cannot show it.
- "The PO was away, so the council answers." Rival: the answers were needed only because the next step of the skill wanted Q1. Nothing in flight waits on Q2 to Q12 today (the architect, on Q3: "Nothing in flight waits on it"). A queue of 12 open questions was an available state.

## 4. Numbers

Each lacks its unit, population, period or provenance, or does not reproduce. New or changed since the first pass only.

- "20 % or 4 rows" (D2): two populations (the rows read, the 72 rows) and two scopes (two directions, one direction). Neither number has a source, and both authors say so.
- "at most three spikes" (Q4 b, direction.md, items.md) against "at most two" (brief.md:6, the PO stand-in's line): no source for either. Three is the count of blocks in items.md.
- "about 16:10 CET" (the relay, D2, D3), "away from about 16:10 to 18:20 CET" (delegated-answers.md:3), "about 16:40 to 17:00 CET" (the PO stand-in), "about 16:50 CET" (the tech lead): all four lines are in commit 0df88140, made at 16:42:14 CET. Three name a time later than the commit that holds them. The architect's "16:41 CET (`date`)" is the only one from a clock.
- "6 of which would change the decision" (brief.md:5): a count of agents' ratings.
- "(A1 2 to 1, A2 1 to 2, A6 2 to 1)" (D2): reproduced from the three files.
- "5 of 5 ... about one time in three" (A4): 0.8⁵ = 0.33, reproduced. No source for 5 or for ±30 %. A task that succeeds 95 times in 100 fails this line about one time in four (0.95⁵ = 0.77), so the line still cannot tell a steady task from a flaky one. "8 times in 10" is an example and not a measured rate.
- "within 30 days" (A5) and "In the last 30 days" (Q13): no source for 30.
- "five modules declare `fetches`" (★C11, A10): four.
- "at least seven network operations" (★C11, S2, Q12 a, the ethics row): a count from two doc pages and one test. The code gives four Operations with the effect, and `tools.py` and `check_vendor_pins.py` name no effect (the architect's grep, not re-run by me). No list from the code exists yet.
- "36 commits in the walk's own repository" (direction.md stage 12): 36 on main, 47 over all refs.
- "407 open" (★C24, 16:30 CET) and "409 open" (the tech lead, "16:4x CET"): two readings, the second with no minute.
- "12 hold, seven of them ... to fix. 14 hold partly" (verification.md:64): 12 + 14 + 1 + 1 = 28, reproduced from my first report.
- "None of the board's 21 options" (items.md:39): no command. Unchanged by the revision.
- "A second frontend of 20 lines ... 0 arrived" (the architect's answers): the script is gone. Mine had about 30 lines and saw 0 events.
- The corrected times of the PO's words (brief.md:9): reproduced. GitHub gives 14:29:02Z for the issue and 14:30:45Z, 14:31:37Z and 14:37:38Z for the three comments, which is 15:29, 15:30, 15:31 and 15:37 CET. The comment of 15:30 CET holds "generally runnable" and "what models we use for what", as items.md says.

What I could not check, and why: the 72 walk rows and the P934 diaries (not opened in this pass). Whether the main session reproduced ★C6 at 16:34 CET. The council's readings of #199, #153, #545 and of the memory notes (time). The architect's claim that his probe's answer equals `flow.py show --json` in every key but one. The architect's grep on `tools.py` and `check_vendor_pins.py`. Whether the three agents ran in parallel and with the same brief, as delegated-answers.md says. The PO's order to delegate, which exists only as a relay.

## Searches

none

## What the main session did with it

All five must-fix findings were fixed on 2026-11-23: D3 names each answer by its content, the test carries the council's three arms, ★C17 records the baseline score of 2aad7674, the statuses of Q2, Q3, Q7, Q10 and Q11 name his parts, and the `fetches` count is corrected. Of the minor ones, ★C15 now reads "the walk rows that were read". Later the same day, in auto mode, the main session also fixed the probe sentence (★C9), the stated times (delegated-answers.md), the old wording of ★C2 and ★C3 (verification.md and direction.md), the probe command in the frame, and the word count. Still open: "3 of 33 facts verified" has no pointer.
