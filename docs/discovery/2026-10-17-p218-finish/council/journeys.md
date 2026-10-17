# PO-assistant lens: use cases P218 must support (2026-10-17)

Read: AGENTS.md, CLAUDE.local.md, P218 brief and story-map, cards #200 #192 #249 #238, README Bench row,
agents.md 123-151 and 613-627, deploy.py --help, INDEX rows AT157-AT313. I did not run the board.

## Use-case table
| Case | Who | Today on main | Pain at the bench | In plan? |
| --- | --- | --- | --- | --- |
| First flash of a passed image | person | Works: look.py gives a token, `deploy.py --token` asks yes, erases, writes, prints `ready seen` (deploy.py:53, 61-70; AT159, AT165, P215 bench 10-15) | Two commands and a token to copy; 4 bench re-runs to get `ready` (AT168, AT173, AT176, AT177) | Yes: P213 one command |
| Same, found from the plugin | person, Claude | Only `commands/build.md` names deploy; no `commands/deploy.md`; `deploy.py` has no `--json` (grep of add_argument: 5 flags, none json) | Claude must read build.md prose or agents.md to find it | Yes: P213 |
| Re-flash after a change | person | Works but heavy: every run erases all flash, then asks yes and a fresh look (deploy.py:108-110) | Each tweak costs look, token, yes, erase, 20 s ready. The PO changed the blink period by typing `200`, not by re-flash (AT159) | Partly: story-map slice 1 "known board, one receipt line", no card |
| Update only the code, no erase | person, Claude | Not built; no `mpremote cp` path. Spike P222 moved to P235 | Erase also wipes any data the firmware kept | Slice 4, "stays with P218", no card, no date |
| Which board is connected | both | Works: look.py reads chip, flash, MAC, compares to the record, no erase (README Bench row) | Port name changes after flash (AT165). Two boards need `--port` | Done (P219) |
| Claude deploys, board allowed once | Claude | Not built. Every deploy needs a yes typed by the person; with no terminal deploy.py prints the line and exits 2 (agents.md:613-616). Grant (P253) covers only `live.py`, not flash | The PO asked for this at the bench: "can you run it yourself without the yes?" (#249) | Yes: P242, reuses the grant record |
| Claude tries code live | Claude | Works inside a grant: `live.py` refuses USB and flash pins, resets at the end (AT313, bench 10-17) | One bench run only (n = 1); the grant line used to be a bare path (fixed, P283) | Done (P247, P283) |
| Wrong board (other chip, small flash, other MAC) | both | Works: the look says stop or differs; gate refuses. No offer to migrate | Message only; no next step beyond "stop" | Offer to migrate moved to P286; refusal is done |
| Board in download mode | person | Works: deploy.py sees `waiting for download`, asks for R, waits 60 s (agents.md:620; AT165) | The cause is not settled (AT161, AT178, AT185); the BOOT/RESET place is not in the board record (AT158) | Done (P243); AT158 open, no card found |
| Lost console (no answer) | both | Works: look, grant, reach, live say why and give one step (P282). Bench: a replug fixed it, "hold BOOT" did not (AT313) | The hint text is wrong for some cases (AT313 "open") | Done (P282); the hint fix is a leftover |
| Two similar boards | person | Refuses and lists; no names, no blink (story-map slice 2) | Not hit at the bench | P286, later |
| Another build (PSRAM) / other framework | person | No | Not hit | P286, out of P218 |
| No cable (OTA) | person | No | Not hit | P235 later, out |

## Ranked gaps (value toward "a basic project closer to a breadboard with working firmware")
1. Claude cannot flash. Every deploy needs the person's typed yes, and `deploy.py` has no `--json`. The conversation
   writes the firmware, so the loop write, simulate, flash, see it run stops at the deploy step. (P242 + P213.)
2. One command for the first flash: look, token, yes, erase, write, ready are separate steps with a copied token.
   (P213, with `/spark:deploy`.) Claude cannot find the path today.
3. Re-flash after a change costs a full gate and a full erase. The loop of "change, put on, look" is what makes
   the product feel like a tool. The cheap form is the known-board receipt (slice 1); the file-only update is the
   better one. Both have no card.
4. Update only the code, without erase. Needs a finding first (P222 spike moved away; D20). Without it, slice 1 is
   the only speed-up.
5. Board record facts that the hints rest on: BOOT and RESET place (AT158), LED polarity (AT212), the "hold BOOT"
   hint that the bench contradicted (AT313). Small, help every bench run.
6. Wrong board and two boards: refusal works; migrate offers and board names are P286.

## What to drop or move out of P218
- Slice 2 (names, blink to tell boards apart) and slice 3 (MicroPython variants): already P286. Keep out.
- OTA, Wi-Fi REPL: P235. Keep out.
- P239 PRs 6 to 8: keep only what P242 and P213 need (a ConsentStrategy that reads the grant record, a core call
  that returns a result for `--json`). The rest of the rename work waits (principle: the bar is a board that runs).
- A deployer agent: not needed. The thin `/spark:deploy` page plus `--json` serves Claude.
- A standing yes with no end: give it the grant's time limit and the board's MAC, as P253 does. One record class.

## Proposed stories to finish P218 (order)
1. P239 PR 5 (in Build): finish and merge. Done when its tests and the push hook pass and PR 6 can start.
2. P242 AI deploy on a granted board: Done when Claude runs `deploy.py` on a board the person granted in their
   terminal, with no typed yes for that run, and the store's deploy record says whose yes and when; a board with
   no grant still refuses; an ended grant refuses.
3. P213 `deploy.py --json` and `/spark:deploy`: Done when `/spark:deploy` runs look, gate and flash in one call and
   Claude relays a refusal word for word from the JSON (outcomes.envelope, exit codes 0, 1, 2 as today).
4. NEW known-board re-flash (slice 1): Done when the PO changes one line, runs one command and reads one receipt
   line with the image sha256; any differing or unknown field returns to the full gate.
5. P239 PRs 6 to 8 trimmed to what 2 to 4 left unclean: Done when no class a caller imports lacks its role word
   and docstring, and no new behaviour lands in them.
6. NEW bench close-out walk: Done when the PO, with Claude, goes in one session from a passed Wokwi run to a lit
   LED on the XIAO by `/spark:deploy`, changes one line, redeploys, and one log shows it. This also settles the
   "hold BOOT" hint and the BOOT/RESET place (AT158, AT313) as small fixes in the same PR.
7. Spike (not P218's done-when): update the files without erase (old D20). Done when a finding with sources says
   whether `mpremote cp` plus the facts file keeps the gate's guarantees. File it as a card in P286 or P235.

## Open for the PO
- Is the re-flash receipt (story 4) in P218, or does "finish it" end at 3 plus 6?
- Does the standing yes end after a time, as the grant does, or last until deleted?
