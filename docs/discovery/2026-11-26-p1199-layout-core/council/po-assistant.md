# The PO assistant lens (P1199)

Opus, 2026-11-26. The lens agent is read-only, so it returned this report as text. The main session saved it
unchanged except for this header.

## Findings

PA-1 · No person's move was ever seen in the data. 28 projects are listed in projects.json. 5 of them are temp paths that no longer exist, so 23 folders were read, and only 1 holds a breadboard.json: spark-walks/reaction-game. It was written 2026-10-19 at 19:58, the same minute as its wiring-record.json. Its 2 connections equal `drawn_jumpers` [["12t.a","8b.j"],["14t.a","3b.j"]], only in another order. No line in bench-2026-11-20.md, bench-2026-11-25.md or handoff-epaper-2026-11-23.md mentions Wokwi, a move or a kept move. · E (files read, grep, 2026-11-26) · supports only: no move was observed for one maker. It does not show that nobody wants to move a part. It matches P1193's ★C17, which found breadboard.json in 1 of 42 .spark folders.

PA-2 · The breadboard that reached the bench has no edit path today. p934-epaper/breadboard.md and p934-display2/breadboard.md both say: "There is no Wokwi diagram: Wokwi has no part for the board and epaper-2in9-bwr-mh-et-live. Use the picture." The rule that refuses the file is drawing.py:565-575. So the wokwi.com round trip and kept_moves cannot work on the FireBeetle board that the PO actually wired. Also, `written_sha256` in p934-epaper/.spark/build.json covers only board.tsx. · E · supports only: J3 and J4 have no path on that board. A move Operation on a spark-owned layout record would not depend on which parts Wokwi has. It does not show that he wanted a move there.

PA-3 · Against the MVP bar, nobody is blocked. The README's Bench row says a breadboard wired from its sheet ran the e-paper clock on 2026-11-22 (P934). The bench notes name no layout friction. The one wiring item is a wake wire (#13), which is a circuit change, not a layout one. Two earlier decisions put the rest later: D-a (P269 D8) puts the perfboard after the editor, and D-i puts the editor after the MVP. · E and D · supports only: the goals, the perfboard, the editors and the move Operations all come after the MVP. Only a measurement, and maybe a stamp on breadboard.json, comes near the MVP bar (H, my opinion).

PA-4 · The riskiest belief is that the PO or Claude will move parts, or want a goal, often enough to pay for refactoring code that 181 tests pin. PA-1 and PA-2 point against it. A second risky belief is that the perfboard ships within six months. #311 still says "Later (D3)", and P269 #304 has been parked since 2026-11-06. · H (my reading) · The cheapest test is a 2-week use log. Each time the PO or Claude wants a part elsewhere on breadboard.svg, add one line to the store's bench file. A pass line would be at least 3 such wishes across at least 2 projects. The number is proposed and must be dated before any result. Cheaper still is the account question Q-a below.

PA-5 · Pre-mortem: "Six months after it shipped, the layout core failed." These are the likely reasons.
- The core served only the breadboard, because the perfboard stayed parked. It added a layer, and nobody used the goals.
- The mm round trip drifted. data/wokwi-geometry.json says its px are "facts about Wokwi's drawings, not about the physical parts". A resistor's legs are 58.8 px apart where six pitches are 57.6, and the tolerance is 1.5 px. The golden bytes broke and the refactor stalled.
- Kept moves waited on P1152 slice 5 and the A2 spike, so edits never survived through the timeline.
- Annealing, or any random goal search, broke the rule that the same input gives the same bytes.
- The web editor was built before the Operations, so its logic exists twice.
- Claude still edits px by hand, as in today's journey.
- Tags: the px facts are E (data/wokwi-geometry.json). The failure stories are H.

PA-6 · Overlaps with open cards. · E (gh issue view, 2026-11-26)
- #352 P293 already owns J4, the PO asking Claude to put a buzzer there. Its words: "tell Claude, and he would do it for me on the board".
- #1699 P1163 owns moving a part or a wire on the page, and what that move makes out of date.
- #304 P269 owns "one common base" for every stage. It is parked in Idea. P1199 is that base, scoped again.
- #1688 P1152 slice 5 already keeps board.tsx and breadboard.json with a stamp. That is where kept_moves joins the timeline.
- #1751 P1202 reads `written_sha256`, and breadboard.json has none (PA-2).
- #311 P275 holds the perfboard router and the drawer record (note 2).
- #1740 P1194 should hold the setting rows.
- #1698 P1162 and P1203 to P1206 (#1752 to #1755) do not overlap. P1201 (#1750) only gives words.
- Proposed order by the MVP bar:
  1. A read-only spike: count jumper fallbacks over the goldens and the walks, and run a px to mm to px round trip with the golden bytes compared.
  2. A comment widening #1751: breadboard.json gets a stamp.
  3. A comment on #1688 slice 5: kept_moves becomes a decorator fed by the timeline.
  4. A comment on #304: its "base" moves to P1199.
  5. After the MVP: a move Operation on the CLI. P1199, P1163 or P293 owns it (Q-c).
  6. After the MVP: placement goals, with rows in P1194. Proposed row: `layout.placement_goal`, default `first-fit`, layer project (H).
  7. After the MVP: the perfboard surface, the drawer record and the joins (#311).
  8. After the MVP: the web editors (P269 step 5, P1162).

PA-7 · Inside spark, no Operation reaches the layout. operation_catalogue.py:26-27 has 8 tables, and none is about the breadboard or the layout. The layout is reached only through the build's `--keep` (build_board.py:106-115). board_components.py:13 says its own layout constants are "Ordinal, not designed". · E · supports only: G9 in pre-analysis.md is right.

PA-8 · Outside tools that research.md seems to miss. These come from model knowledge, not from a search, so each licence must be read at its source.
- Freerouting: GPLv3, a rip-up-and-reroute autorouter. Ideas only.
- OR-Tools CP-SAT: Apache 2.0. It places parts toward a goal without randomness, so it would keep the same-bytes rule better than annealing.
- BlackBoard Circuit Designer and LochMaster: perfboard planners. Their licences are unknown, and LochMaster is paid.
- · H (model knowledge) · supports only: there are candidates for D-q2 and D-q6.

## What I could not check

- The Perfboard artboard of P1038. It lives only in the claude.ai canvas. No .md file in docs/discovery/2026-11-23-p1038-page-design/ mentions a perfboard (grep).
- Whether the PO ever used the wokwi.com round trip outside his project folders. It would leave no trace in the folders.
- The 5 projects whose temp folders are gone.
- How often a jumper falls back, and the px to mm round trip. Either needs a run, and I ran no build.
- Web searches. This session had no search tool.

## Questions for the decider

- Q-a (account) · "When did you last want a part elsewhere on a drawn breadboard, and what did you do?" · decides: whether J3 and J4 are worth building now · options: name the time and the project / never / I would if I could. Ask it first.
- Q-b · Does the core refactor go first, or wait for the perfboard? · decides: when the core is built · options: (a) it waits until the perfboard card is pulled, (b) it is built now on the breadboard alone, (c) it is built now together with the perfboard. I would pick (a).
- Q-c · Who owns "move a part" as an Operation? · decides: one epic holds it, not three · options: P1199, P1163 or P293. I would pick P1199 for the Operation, which the CLI reaches first (D-h), and P1163 for the page.
- Q-d · Should the read-only spike in PA-6 item 1 be the first item? · decides: the evidence for the riskiest belief and for the mm unit · options: yes / no.

## Searches

None. This session had no web search tool. The candidates in PA-8 should go to the architect or the refuter to check.
