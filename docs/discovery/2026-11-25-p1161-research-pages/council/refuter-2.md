# P1161 council: the refuter, second pass

Read on 2026-11-25 from about 21:05 to 21:20 CET by the machine clock (`date` read 21:17:59 CET), at 50fc270d. The
diff since 2145be09 and since my first pass (cceba566) was read; read only otherwise. Scope: the sections named as
changed. I decide nothing.

## 2. The changed sections against their detail

D1 to D14 against the majority column of council/delegated-answers.md:
- D3 has no source. The table has no row for "test A1 before any build or in the slice 0 walk". delegated-brief.md
  never asked it. Only the Q12 bullet "Its 'value proven by' gains the A1 diary rows" comes near, with no count. D3's
  "3 of 3" and its "options: test before any build, test in the slice 0 walk" are not in the source.
- D2: "counted across walks until 5 (2 of 3)". The seat columns show only the tech lead saying it. The architect adds
  "Fewer than 5 moments is no result", which D2 drops. The Test line still says "the next walk's diary", and
  delegated-brief.md Q1 says "in the next walk".
- D1 drops the majority's condition "once the refuter's report and the README exist". At 21:11 (2145be09) neither
  existed. Both exist now (b1263d6e, 50fc270d).
- D4 adds "naming the job, never the how" (architect only, 1 of 3). The majority cell is "A (3 of 3)".
- D7 adds "the home comes from the core's `record_path`" (architect only, 1 of 3).
- D6 drops "before the slice 0 PR merges" (Only the PO, item 3).
- D13 drops "limits" from option A ("the model and the agent's limits").
- D14 says "3 of 3 on the changes". The Q12 section also holds a 1-of-3 change (the stamp's slice) and the M1 split.
- Decision needed drops item 4 of Only the PO (Q2 C and Q8 B), and "go to design or build" becomes "go to design". The
  seats' sentence for the PO says "Three things", but their own list has five.

The decisions and the corrections:
- All of D1 to D14 were voted on the brief before my corrections. At 2145be09 it still read "Nobody is blocked today"
  (★C15), "0 of 9" (★C16), "No Operation writes a record into the catalog" (★C14), and "the PO's 'most important'"
  (★C17). Q0's row says "no refuter report yet". D8 ("tell spark what you saw" leads) and D5 rest on the old ★C16 and
  ★C15. Nobody re-read them after the change.
- verification.md, Agree: "the refuter and the three seats found the same two gaps (no refuter report then, the clock
  times)". I did not raise "no refuter report". Split rows say the seats "agreed" with me or "chose" against me, but
  they never read my report.
- verification.md ★C12: "reproduced how: not reproduced here" sits beside "result: reproduced after the change, in
  part".
- ★C9's keep ("n = 1 per lean run") leaves out the unit I asked for ("tokens processed, cache reads included").

Propagations that the changes missed (risks-and-tests.md is a changed file):
- The value row still reads "Nobody is blocked today (★C15, n = 1)".
- A5 still reads "0 of 9 facts of one part need a new web search (★C16)". The corrected ★C16 sorts 6, and none of
  them to the web, and leaves 3 unsorted.
- Q3 A's caveat in the brief still reads "P1002 becomes slice 1", against D5 (P1002 stays open, linked).
- The no-go "an outside parametric search that needs an account" still cites ★C12. The corrected ★C12 no longer says
  that an account is needed.

Pointers:
- Q7's caveat quotes "Changes 5 to 7 can pause" at finding.md:146-147. At e882d7b5 that quote is at :201, and :146-147
  read "6. Can wait. The build stamp leaves out the part records…". C24 corrects one pointer error and adds another.
- Q5 A's caveat cites record_home.py:46-48. Those lines refuse a record held only in another project
  (`OTHER_PROJECT_RECORD`, "spark writes only the project --project names"). The write behind a shelf copy is at
  :49-54 and :181. My first pass gave the same wrong lines.

Each changed ★ claim against my first-pass correction:
- ★C4: matches. The caveat's "change 6" holds at e882d7b5:146.
- ★C6: matches. I confirmed P1152 #1688 open, status Idea.
- ★C8 and ★C14: match.
- ★C9: matches. The 0.55 M and 0.17 M figures still carry no "processed".
- ★C11: matches, but "is untried" has no pointer.
- ★C12: matches, but its no-go and its keep ("one module query") do not.
- ★C15: matches. Its board clause holds: BOARD_WRITE_KEYS = ("pin_roles", "joined_pads") (records/missing_facts.py:37).
- ★C16: matches in the brief, not in A5.
- ★C17: matches.
- C23 is stronger than its source. My first pass said that one hour ahead is "consistent, not proven". C23 states "run
  about one hour ahead".

## 3. Rival interpretations not ruled out

- The 3-of-3 agreement: each Option row is labelled "opinion (the architect's)", and the architect sat as a seat. The
  agreement may follow that anchor rather than come from three separate judgements.
- D3: the slice 0 walk gives perhaps one research moment, so "across walks until 5" lets slices 1 and 2 ship before A1
  has a result.
- C23: the times were estimated by the agents and never read from a clock. The gaps vary (≥16, ≥43, ≥13, ≥19 min). A
  CET/CEST mix-up is a second rival. A one-hour offset is one reading among three.
- ★C16 and D8: the 3 unsorted facts (the input thresholds of the buffer chip) are datasheet facts. If they go to the
  web, the web gets 3 of 9.
- Q5 A and D7: `record_path` returns project B's file for a shelf copy shelved from B. The chosen option then sends the
  rabbit hole "a write from project A's page into project B's record" to the chat.
- ★C11 "untried": a compare run may exist outside the walks. Nothing was searched.
- The no-go "sends queries off the machine" would also bar today's web research.
- ★C6: D8's list may be a set of examples. The PO's own reading is unknown.

## 4. Numbers lacking unit, population, period or provenance

- A6, the risk row and items: the ceiling is anchored on "0.17 M to 5.0 M tokens", which are tokens processed with
  cache reads (research-cost.md:4-11). The run is to be measured by `scripts/cost.py`, which counts "new tokens apart
  from cache reads" (research-cost.md:5). The ceiling and the result are in different units. `cost.py` also reads one
  transcript (cost.py:20-26), so it misses either the main transcript or the subagent's.
- ★C9 "S 14, C 13, M 12, L 10": these are step lines in history.jsonl, for all time up to 2026-11-25. Neither is
  stated.
- "Stands on: 10 H": 7 of the 10 assumptions have E in their evidence column.
- D2 "3 of the first 5, counted across walks": there is no period and no end date.
- D14 "six cards": five new numbers, plus P992 refined in place.
- C23 "about one hour": no measure is given. The four gaps are lower bounds of 13 to 43 minutes.
- A5 "107 unverified facts": an object at any depth (my first pass), still unstated.

## Searches

None. No pages fetched. Reproduced: `git show e882d7b5:…/finding.md`, `sed` of record_home.py, cost.py,
run_cost.py, research-cost.md and missing_facts.py, `gh issue view 1688`, `git log` times, `git show 2145be09:…/brief.md`.
Not checked: the README beyond its head (not in scope), story-map.md lines other than the one changed, and the seats'
own working (only their table exists).
