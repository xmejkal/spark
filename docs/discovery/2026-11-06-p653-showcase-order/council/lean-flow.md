# P653 council: lean flow lens

Tags: E = evidence with a pointer, H = hypothesis, D = decision (who, when). "—" = unknown. gh calls used: 7 (of 8). Scratch data: /private/tmp/claude-501/-Users-petr-Development-spark/d278b9fb-f69a-4627-a382-d87c26d5c958/scratchpad/ (items2.json, closed.json, created.json, open.json).
"Games" = the project field "slice" is pixel-games or graphics library. "Spark" = every other slice or none.

## 1. Findings

- LF-1 · A first `gh project item-list --limit 400` returned only 400 of 535 items and missed cards 839 to 876 (the newest Ready and in-flight cards). A second call with `--limit 1000` returned 535 items, highest issue 876. Any board count made from a 400 limit is wrong. · E · `jq '.items|length'` gave 400, then 535.
- LF-2 · Board now, in the stages that count (Discovery, Design, Build, Review), 11 cards sit in flight against a flight limit of 4. By slice: games 6 (Discovery #743, #787, #841; Design #769; Build #812, #840), spark 5 (Design #224, #304, #417; Build #467; Discovery #876 this spike). · E · `jq` on items2.json, status and slice fields. Qualifier: the rule says an epic counts in no stage and its stories carry the limit (scrum/WORKING_AGREEMENTS.md W6, line 85; the PO made it standing 2026-11-05). Which of these 11 are epics, I did not read — so the true count against 4 is —. Titles marked "(epic)" in the list: #224 only. #812 and #769 read like epics ("a mature engine", "each one is a wild, beautiful indie game") — H.
- LF-3 · Ready holds 4 cards (limit 5): games #829 (P622 StepClock), #850 (P635 silhouette people), #858 (P640 scene lists its layers); spark #710 (P514 --needs-drop). Games 3, spark 1. · E · items2.json, status Ready.
- LF-4 · Idea holds 253 open cards: spark 189, games 64. · E · open.json (open issues) joined to items2.json status and slice.
- LF-5 · Age of in-flight cards (created to last update, today 2026-11-06): spark #224 created 10-13, last touched 10-20 (17 days old, 17 days untouched); #304 created 10-16, untouched since 10-16 (21 days); #417 created 10-19, untouched since 10-19 (18 days); #467 created 10-20, last touched 11-02 (4 days untouched). Games #743 and #769 created 11-02, untouched since 11-02 (4 days); #787 created 11-03, touched 11-04; #812, #840, #841 touched 11-06. · E · open.json createdAt/updatedAt. Three spark cards in Design or Discovery have had no update for 17 to 21 days, while they hold WIP slots.
- LF-6 · Cards closed, by date of closing (all closed issues since 10-30, n = 84): 10-30 to 11-02 all spark (3, 8, 26, 23 = 60); 11-03 to 11-06 games 21 and spark 3 (2 on 11-05, 1 on 11-06). Since 10-31: games 21, spark 60. · E · closed.json joined to slice. Last day with spark closings above 3: 11-02.
- LF-7 · Cards filed since 10-30 (n = 197): spark 97, games 94, over the same 8 days; 11-01 spark 54 filed; 11-02 games 34 and spark 20; 11-03 to 11-05 games 21, 14, 22 and spark 0, 1, 1; 11-06 games 3 and spark 8. · E · created.json joined to slice. Games filed 94 and closed 21 over the period: 73 more filed than closed (many are still Idea; 64 games cards sit in Idea).
- LF-8 · Wave 4 of the refactor (epic P158 #94, Idea on the board) has these cards Done: P474 plan #649, P475 W4-1 #651 (closed 11-01), P479 event seam #657, P507 E1 #702 and P508 E2a #703 (closed 11-02). No W4-2 or later card is filed as a card; the only card that names W4-2 is P478 #656 (Idea, parked after v0.10). So "finish wave 4" has no card list on the board to measure against. · E · items2.json titles matching W4; closed.json dates. What W4-2 to S9 contain: — (plan text not read, time).
- LF-9 · Focus switches in the two weeks, from closings and filings: spark only to 11-01; both on 11-02 (games 34 filed); games only 11-03 to 11-05 (games 18 closed, 0 to 2 spark per day); spark again 11-06 (P645 closed, 8 spark cards filed, this spike). That is 2 clear switches (spark to games on 11-02/11-03, games to spark on 11-06) plus the PO's 11-04 "Finish wave 4 first" (D, Petr, 2026-11-04, from the task brief) which no board movement followed. · E for the dates; D for the words. Before 10-30: — (closed list starts 10-30).
- LF-10 · Cost of the 11-02 switch, visible on the board: spark Design cards #304 and #417 and the epic #224 stay in Design; none has an update after 10-20 (see LF-5). They were already idle before the switch (last touch 10-16 to 10-20), so the switch did not stop them; wave 4 did (H: spark attention went to wave 4 until 11-02, then to games). Open PRs now: 0 (`gh pr list --state open` returned []), so no draft is stranded. Paused discovery: P605 #807 (spark Idea) and the P539 graphics library discovery #743 (Discovery, 4 days untouched) — E for status, H for "paused because of the switch".
- LF-11 · The games side keeps generating cards faster than it closes them (LF-7), and 6 games cards are in the working stages at once. A showcase finish line that is not written down will absorb every new "effect" idea, since 64 games cards wait in Idea. · H · from LF-4 and LF-7; no source says the line is missing except the PO's wish "some nice demonstratable state" (D, Petr, 2026-11-06).
- LF-12 · WIP rule text: "two per working stage, three in Build, five in Ready, four in flight; an epic counts in no stage". The push gate (tools/check_backlog.py) fails when a limit breaks. 11 cards in flight (LF-2) therefore either include epics, or the gate is not looking at this board state. · E for the rule (scrum/README.md line 7, WORKING_AGREEMENTS.md W6 lines 83 to 91); the reason for the gap: —.

## 2. Proposed order and finish line

Not decided; a proposal for the PO.

Option comparison (flow terms only):

| option | what it does | flow cost | risk |
|---|---|---|---|
| (a) showcase to a finish line, then wave 4, then controls and sound | one switch now, one back, each with a written end | one more switch than (b) | the line drifts, since 64 games Idea cards pull (LF-11) |
| (b) wave 4 first | no switch; games drop to Idea/Ready | the 6 games in-flight cards stay half-done: 4 days idle on #743, #769 and so on (LF-5) | it breaks the 11-05 order (D, Petr, 11-05, games first); wave 4's remainder has no cards (LF-8) |
| (c) controls and sound inside the showcase before wave 4 | showcase grows | longest delay of wave 4 | the finish line moves while we walk to it; "controls and sound" are new epics, not slices of the engine |

Lean proposal: (a), with the line written first and a date.

Finish line, "demonstrable" as a checklist (to be confirmed by the PO; each item testable on the board or in Wokwi):
1. At least 2 games run on the bench board using the shared engine and effects (which ones: — ask PO).
2. Each of those games runs at 25 fps or more, or the finding for the gap exists (D, Petr, 2026-11-04: 25 ok, 30 super).
3. Cards #829 (StepClock), #858 (layers list) done, since both are in Ready and remove duplicate glue.
4. One short page or video that shows the games and the effects, for a person who has not seen them (form: —).
5. The in-flight games cards are down to at most 2 working stages x 2 and 4 in flight, and every card above that is Done, parked or dropped.
6. No new games Idea card enters Ready until the line is met (new ideas go to a "after showcase" list).

WIP for the stretch: games at most 2 cards in flight and 2 in Ready; spark 0 in Build, 1 in Ready (#710); all the idle Design cards (#224, #304, #417) parked back to Idea or Ready with a reason (LF-5). Wave 4 returns when the checklist above is met, or after a fixed time box that the PO names (a proposal: 5 working days — H, no data on the pace beyond LF-6: games closed 21 cards in 4 days). Before wave 4 returns, file W4-2 to S9 as real cards (LF-8); "plans shrink with distance" says only the next slice is refined, so file the next slice only.

Park, drop, merge:
- Park (to Idea or Ready, state the reason): #224, #304, #417 (idle 17 to 21 days).
- Merge candidates (H, from titles): #743 (graphics library) with #812 (the engine across chips and display drivers) and #841 (engine layers options): three games cards all about the engine's shape — ask whether one discovery can hold all three.
- Finish first (nearest to Done): #840 and #812 (touched today), then #829, #858.
- Drop: none proposed without the PO.

## 3. Not now

- #224 (P235 live on the board, epic), #304 (P269 views and editors), #417 (P325 walk with the XIAO) · idle 17 to 21 days; wave 4 and the showcase take the attention first.
- #467 (P365 walks, Build) · spark Build slot used by a card untouched since 11-02; walks need the PO's bench time (D, Petr, 10-19, memory "remind bench P100").
- #94 (P158 one core, v0.13) as a whole · wave 4 remains the first slice; the whole-repository change waits (AGENTS.md).
- #743 (P539 public C/C++ graphics library) · asks the largest question (public library, MicroPython bindings) and is not on the finish line; the showcase does not need it (H).
- #841 (P628 options for engine layers) · design options for the engine after the showcase; the games run without them (H).
- New games ideas in Idea (64) · P606 #808 (Runner gets wet), P625 #838 (spark burst on a hit) and similar: the showcase needs a few games, not ten effects each (H).
- New controls and sound as epics · see option (c); start them only after the finish line, as new epics with their own card (the PO's rule: ask before a new epic while other work is in progress).
- Spark's 189 Idea cards · no change in the next stretch.

## 4. What you could not check

- Which of the 11 in-flight cards are epics (LF-2); the true flight count against 4 is —.
- The content of wave 4's remaining slices (W4-2 to S9) and their size: plan text not read — time.
- Focus switches before 10-30: the closed list started at 10-30; no earlier count.
- Time between "Waiting since" and today for each card: the project's Waiting fields were not in the export I used.
- The PO's 11-04 and 11-05 words are quoted from the task brief, not from a file in the repository (grep for "Finish wave 4" returned nothing usable in the time).
- Whether the push gate (check_backlog) passes with 11 in-flight rows: not run.
- Cost of a switch in minutes: no clock data.

## 5. Questions for the PO

- Which games count in the showcase, and how many? · decides the finish line (item 1) and the size of the games WIP.
- Is a time box (for example 5 working days) acceptable for the showcase, after which wave 4 returns whatever is left? · decides whether the line is a date or a checklist.
- Should #224, #304 and #417 go back to Idea while wave 4 and the showcase run? · frees 3 spark in-flight slots.
- Are #812, #769, #787, #743 epics (so their stories carry the limit)? · decides the real flight count (LF-2).
- Do controls and sound start as a new epic after the line, or does one slice enter the showcase? · decides option (a) versus (c).
- Is the 11-04 "Finish wave 4 first" still the rule, or does the 11-05 "games first" replace it? · decides option (a) versus (b).
