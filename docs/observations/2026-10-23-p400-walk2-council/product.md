# Product lens on P396 to P399 and the 29 gaps of walk 2

> Walk 2's four cards all answer one stall, S3. S1 (the goal never reaches idea) and S2 (the hold) have no card.
> The root of S3 is a verdict that says "passed" and hides what no scenario tested. So P345 with I5 goes first. P389 and two small new cards follow, then P396.
> P398 and the name check of P399 fail R10.2, because no walk used a name yet. No card goes against the vision.

## Findings

R10.2 (`scrum/RETROSPECTIVES.md:266`): "A found row becomes a card only if it blocks the next walk step or is a real bug. Every other row stays "raised" in its rows file." The PO decided: yes, plus bugs.

| # | finding | evidence | card or plan | proposal | severity |
|---|---|---|---|---|---|
| 1 | The four cards all answer stall S3. S1 (about 8 minutes) and S2 (about 3 minutes) have no card. S4 is by design. | Body of #6: "each stall is filed as a card". Diary S1 to S4. | P100 (#6) | New cards N1 and N2 below. | high |
| 2 | The harm of S3 is the verdict. The look said "simulation: passed" and deploy flashed the image as tested. Nothing pressed the button. | Diary O12. Comment on #440. `scrum/VISION.md:30` and `:60`. | P345 (#440), P308 (#374) | Propose P345 for Ready (4 of 5 used). Two PRs: what the run did not touch, then I5. Plan it with P308, which also changes what the gate says. | high |
| 3 | No card gives a free test of the press. The vision puts that test on the laptop. Walk 2 wrote its own, and R10.1 counts steps outside spark. | `scrum/VISION.md:31`. `scrum/RETROSPECTIVES.md:265`. Diary G23. Comment on #6, 2026-10-22 16:23. | none | Row now. Refine a card right after P345, because the change step needs the same test. | medium |
| 4 | P396 is the right base. It is silent on the LED. The store holds one Wokwi part file, and a comment in it breaks strict JSON. | `find ~/.local/share/spark -name '*.board.json'` found one file. Its lines 12, 32, 33. #512 "Nobody tried yet". | P396 (#512) | Rewrite below: three words per name. Add G18, the false serial warning. | medium |
| 5 | P397 needs P389 and P396 first. Its other choice is none for the PO's XIAO, which has no soldered pins. | Body of #513. Comment on #6, 2026-10-22 16:17. | P397 (#513), P389 (#504) | Rewrite below. It waits in Idea. | medium |
| 6 | No walk named a part id, control or pin in a scenario. Walk 1 did not run its scenario. Walk 2 ran one that waited for "ready". No card goes against the vision, but P398 serves only the agent. | `docs/observations/2026-10-19-p326-walk1.md:57`. Diary step 01:15. `scrum/VISION.md:40` and `:75`. | P398 (#514), P399 (#515) | P398 to a row. P399 shrinks to a dry run and an id check. | medium |
| 7 | A wrong name costs little. The free plan has 50 CI minutes per rolling 30 days, and the CLI stops after 30 s. Walk 2's run took 8 s. | docs.wokwi.com/wokwi-ci/getting-started and /cli-usage, 2026-10-23, from a search summary. `scrum/VISION.md:38`. | P399 (#515) | The value of P399 is the dry run (G26), not saved minutes. | low |
| 8 | Cards open faster than they close. R10.2 targets 1 or less. Since 2026-10-20 (UTC), 45 opened and 16 closed, about 2.8 to 1. | `gh issue list --state all --limit 600` and `jq` counts, seen before this line. | R10.2 | Net the new cards out: close P355 into P389, P398 to a row. | medium |
| 9 | G7: `--match` offers neither the board's own LED nor its BOOT button. The team predicted it. | Diary G7. #504 "It widens P355 (#453)". `docs/observations/rows/p378-walk2-map.md` row 2. | P389 (#504), P355 (#453) | Existing card. Add the XIAO's BOOT button to the test of P389. | medium |
| 10 | G4, G5, G6, G21: no command writes the brief, no run lists its open fields, and idea never reads its goal. | Diary S1, G4 to G6. The idea page itself is not checked. | none open | New card N1 (G6). G4, G5 and G21 ride in its PR. | medium |
| 11 | G9 to G13: `--match`, `--drawer` and `--offer` hide the holder, and the dry run misreads one refusal. | Diary S2, G9 to G13. A search of 338 issues for used_in, holder and held by found no open card. | none open | New card N2. G12 and G13 ride along if small. | medium |
| 12 | G2 and G20: init says nothing when it skips the git exclude. Its advice loops after a board-only build. | Diary G2, G20. P137 is parked (`scrum/STORY_MAP.md:38`). | P137 (#71) | Existing card. G20 is a real bug. Widen P137 and pull it after the verdict cards. | low |
| 13 | G1 and G22: one word, skipped, has two reasons. check_all says "not asked for", check_spine says "board only: nothing to wire". | `scripts/outcomes.py:21-26`, `scripts/check_all.py:462`, `scripts/check_spine.py:547`. | P118 (#52) | Row only. Use the check_spine reason in check_all, in the PR of P118. | low |
| 14 | Rows with a host card. G3: P309 (#375) sets what sellers does. G8: P314 (#388) and P390 (#505). G14 and G15: P389 edits `commands/idea.md:53`. G16: P349 (#445). G25: P345 edits `run_scenario.py:212`, per #440. | Diary G3, G8, G14 to G16, G25. `grep -n 1b commands/idea.md` finds line 53 only. | see cell | Row only. Fix small finds in the host PR. | low |
| 15 | Rows with no host: G27 and G28 (next PR on deploy.py), G24 (next PR on journey.md). G17: no change to setup, the unused package.json joins the prune list (P385 #494). | Diary G17, G24, G27, G28. `docs/guide/journey.md:1217-1220` names "ready unknown" and shows no lines. | P77 (#13) | Row only. For G24, the lines worked on the board ("ready seen", 06:55), so "no board ran them" is stale. | low |
| 16 | G19 and G29: the hold and the last deploy are two facts. The yes before the erase names neither. | Diary G19, G29, O14. | none | Row only. Card when a deploy erases the firmware of another project. | medium |
| 17 | Order: P345, P389, N1, N2, P396, P399, P397, P137. P398 is a row. Ready has 4 of 5, so one card enters now. | `gh project item-list 2`: Ready holds #479, #493, #504, #505. | all | The PO orders Ready. | none |
| 18 | The next walk needs P345 first, whatever it is. A new walk on the XIAO also meets S1, S2 and G7 at steps 2 and 3. A radio walk needs P347 (#442) and P348 (#443). | Diary S1, S2, hold section. Titles of #442, #443. #417. #440 body. The diary has no change step (13 rows). | P325 (#417) | The PO picks the walk. | none |

Gap map: G23 is in rows 2 to 5, G18 in row 4, G26 in row 7. All other gaps are in rows 9 to 16.

## The four cards

None of the four repeats an open card. P396 gives the reason, P345 gives the verdict, and P355 (#453) sits inside P389 (#504). The PO asked for these cards, so a drop needs his word.

- **P396 (#512): rewrite.** The person reads before a paid run that the press cannot be simulated. It is the base of the chain and the smallest build line that helps. It never fills a gap.
  - The change: "The build reads the Wokwi part definition that the store keeps. For each GPIO name in `pins.py` it prints reachable (with the Wokwi pin), not reachable (with the reason) or not known (with what nobody tried). It prints no serial warning for a part with `serialInterface` `USB_SERIAL_JTAG`."
  - Done when: "For a fixture of the walk 2 project, the build prints ONBOARD_BUTTON (GPIO9) as not reachable, because the part has no pin on GPIO9. It prints ONBOARD_LED (GPIO15) as not known, because `$gpio15` is not tried. A board with no stored part file prints not known. The XIAO gets no serial warning. A test reads the stored file."
- **P397 (#513): rewrite, then wait.** The person reads the same fact at the pick, before the build. It follows P389 and P396.
  - The change: "At the pick, spark says that no scenario can press the board's own button. It names a button from the drawer that the project can wire. It names none if the drawer holds none."
  - Done when: "With P389 and P396 done, `parts.py --match` and the `--pick` dry run print the sentence for the press need. With a tactile button in the drawer, they name it. Without one, they name no other choice."
- **P398 (#514): drop to a row.** Claude gets a list and the person gets nothing. No run needed a name. The store holds one Wokwi file and no source I found for the controls of the button and LED parts. Reopen when a run fails on a name.
- **P399 (#515): rewrite, shrink.** Claude checks a scenario at no cost. Its Done when needs only the ids of the diagram, so the title overpromises controls and pins.
  - The change: "`run_scenario.py --dry-run` runs every free check and stops before wokwi-cli starts. One check compares each part id of the scenario with the ids in `sim/diagram.json`."
  - Done when: "A scenario with a misspelled part id exits 2 under `--dry-run` and in a real run, before any Wokwi minute. The message names the word and the ids that the diagram has. A fake wokwi-cli shows that no run started."
- **P345 (#440), not one of the four: add a Done when.** PR 1: take a board-only fixture with a scenario that waits for ready. The run log, the look and the line before the yes of deploy show one sentence. It says: this run waited for ready, pressed no control and read no pin. PR 2 (I5): each scenario names the must line it tests. The verdict names each must line that no scenario tested.

## New cards

- **P? — the goal in the brief never reaches idea → idea starts from the goal in the brief.**
  - Need: stall S1 (21:05 to 21:13) and G6. The PO's bar for P100 is that every handover works (comment on #6, 2026-10-11).
  - Done when: in a fixture whose `.spark/project.json` holds a goal, `/spark:idea` starts from that goal. It asks again only when the goal is null. The idea page says so.
- **P? — a pick stops on a hold that no view names → every view names the holder.**
  - Need: stall S2 and G9 to G13. reaction-game holds the XIAO again since 21:30 on 2026-10-22. P325 (#417) plans two more walks on the XIAO.
  - Done when: in a fixture where project A holds the XIAO, `parts.py --match` in project B names A beside "free 0". The `--pick` dry run says that one refusal stops every pick of the command. `--offer` prints each line once and cuts none.

## Not checked

- The code behind G1 to G22, G25, G27 and G28. I read the diary, and only the lines I name in the evidence column.
- Whether a scenario can read `$gpio15`, and whether Wokwi accepts a spark field in a scenario for I5.
- The source of controls for the built-in Wokwi parts. The store holds one Wokwi file, so I found none.
- Wokwi billing: one search summary on 2026-10-23, no page opened. The pricing page lists other figures.
- Where the example firmware of G24 lives (`examples/` does not exist), and whether the plans P323 and P391 cover holds. I only searched issue text.
