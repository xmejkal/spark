# P663 the pin conflicts discovery: rows

What the council, the refuter, the review and the session found while the discovery ran. Card:
[P663 #892](https://github.com/xmejkal/spark/issues/892). Folder: `docs/discovery/2026-11-07-p663-pin-conflicts/`.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The step 4-5 draft made K3 (the backlight and the onboard LED on GPIO21) a stop, but the LED is soldered, so no answer exists and every GDI project would stop | refuter, first pass | acted | K3 is a note on the run (D6), in story-map.md slice 0 and P665 #894 |
| 2 | The facilitator called `docs/guide/agents.md:131` a contradiction of the assigner's exit 1. The line covers input a script cannot read (`assign_pins.py:529-531` returns 2) | refuter, first pass | acted | ★C3 and P671 #899 name the real split: `Impossible` exits 1 from `assign_pins.py` and 2 from `emit_board.py` and `check_spine.py`. Logged in the learned-rules file |
| 3 | The proposed card for the board record's restricted pins duplicated P281 #323 for USB and flash | refuter, first pass | acted | P672 #900 holds only straps 45 and 46 and JTAG 39 to 42 |
| 4 | The Q18 option text said "Like ESPHome", but ESPHome warns and proceeds with no flag, and its flag only silences the warning | refuter, second pass | acted | D7 quotes the chosen option and says the comparison was inexact. The no-flag behavior and the flag's name are Q20, for the plan council. Logged in the learned-rules file |
| 5 | After D4 and D6, the story map still asked "cable or wires?", A4 and A7 stayed open, and the bridge spread over three cards | refuter, second pass | acted | story-map.md slices 1 and 2 follow D4. A4 and A7 are retired. P667 merged into P665 #894 |
| 6 | The epic #892's body still asked "cable or wires?" and refused the strap | PR review, Sonnet | acted | a "Changed by the discovery" paragraph at the top of #892 names D4 and D7. The first text stays as history |
| 7 | The frame's "Already decided" line kept C4's refusal as standing, with a loose pointer `:65-70` | PR review, Sonnet | acted | brief.md line 18 says D7 replaces it. The pointer is `:69-71`, raised at `:263-265`. The council reports keep their own pointers |
| 8 | The story map's closing line called four rows of three cards "P665" | PR review, Sonnet | acted | each row names its card: P665 #894, P666 #895, P668 #896, P660 #886 |
| 9 | Q5's option (c) was glued onto option (b), and ★C3 ran two sentences together | PR review, Sonnet | acted | split into two lines and two sentences |
| 10 | Q15, Q20 and Q21 share lines with Q14 and Q19 | PR review, Sonnet | rejected | the check caps brief.md at 150 lines, and each joined question keeps its own number |
| 11 | Three council reports held home paths before the first push | facilitator | acted | replaced with `~/` and amended before the push. No home path reached GitHub |
| 12 | `gh project` answered "unknown owner type" when gh's GraphQL limit was used up, so `check_backlog.py` reported could-not-run with the wrong reason | facilitator | raised | a direct `gh api graphql` call said "API rate limit already exceeded". The filing of 8 cards and their board fields used the limit up |
