# P218 council draft, 2026-10-17

Code read: origin/main 7554792 (a copy is in scratchpad/main). P239 PR 5 is only a plan on branch p239-pr5-project-image (docs/discovery/2026-10-17-p239-pr5-project-image/plan.md). Nothing is edited on any card yet.

## #200 P218 (epic)

Done when (kept, with two additions):
- One command deploys (P213 #192).
- Claude deploys to a board the PO allowed once (P242 #249).
- Both run on the deploy core that P239 #238 builds.
- Order: P239 PR 5, P242, P239 PRs 6 to 8, P213.

Now on main:
- P239 PRs 1 to 4 are merged (#240, #241, #244, #335).
- The grant work is merged: grant.py, board_grant.py (P253), the full-path line (P283).
- Deploy has no `--json` today (docs/guide/agents.md:410-411 lists deploy.py and look.py as having none).
- There is no `/spark:deploy` command. Only commands/build.md:270-334 (deploy.py first named at :281) names deploy.py.
- Gap: P242 changes who can run deploy.py. commands/build.md:283 and docs/guide/agents.md:613-616 both say the yes is only the person's. Both texts change in P242.

## #238 P239 (deploy core)

Done when (replaces "Value proven by"): PRs 5 to 8 of the synthesis (docs/observations/2026-10-14-p239-oo-council/synthesis.md, section e) are merged, each with the suite green and no change to `--help`, exit codes or store records. After PR 8, `DeployService` runs the whole deploy with no print and no `sys.exit`. `main` only parses, prints and maps the exit code.

Now on main:
- PR 1 to 3 merged: rules in developing.md, tests/fakes.py, renames (`ConsentStrategy` deploy_gate.py:37, `TerminalConsentStrategy` :55, `GateClosedError` :29, `require_open_gate` :77, `BoardUnreachableError` and `BoardCodeError` board_connection.py:33,41).
- PR 4 merged. Two names differ from the synthesis. `RunLog` became `BoardLog` (deploy.py:118). `DeployPlan` has three fields, `commands mpremote notes` (deploy.py:115). `ReadyResult` is ready_check.py:40. `ConsentStrategy.who` is deploy_gate.py:41, and `record_deploy` takes it (board_facts.py:55,62). The clock is injected as `clock` (deploy.py:182,239).
- PR 5 is planned, not built (another agent). The plan puts `ProjectImage` and `DeployError` in a new `project_image.py`, moves `runnable` to `tools.command_for`, and puts `BOOT_HINT` in board_look.py until PR 7. The synthesis said "beside the flasher".

What PRs 6 to 8 still need, with the new callers the synthesis did not list:
- PR 6 (`DeployToken`, `LookReport`, renames). `token()` sits on `Report` (board_look.py:210) and is called at look.py:52, deploy_gate.py:84 and deploy.py:220. `EsptoolReader` (board_look.py:112) is also built in grant.py:76. `BoardReader` is a plain class (board_look.py:105), so it is not yet an ABC. `Reading.mac` is read in board_grant.py:122 and deploy.py:139. `board_token(mac)` (board_look.py:39) is also the grant's `board_token` field (board_grant.py:101,127). So `DeployToken` must keep one place for the board half. Rename order: `Look` to `LookService` (:217), `Report` to `LookReport` (:172), `Reading` to `BoardReading` (:33), `EsptoolReader` to `EsptoolBoardReader`, `lines` (look.py:37) to `report_lines` in board_look.py. Grant code (grant.py:76, board_grant.py:108) and the tests test_board_look.py, test_look.py and test_deploy_gate.py change in the same PR. board_doctor.py does not (it imports only LookStop and PortFinder).
- PR 7 (`Flasher`, `EsptoolFlasher`). Takes `flash_commands`, `ERASE`, `WRITE` (deploy.py:53,107) and the run loop (deploy.py:228-234). Reader and flasher both build their command with `image_check.runnable` (board_look.py:121, deploy.py:109), which PR 5 renames `tools.command_for`. A shared helper is new work in PR 7. `BOOT_HINT` moves here from board_look.py.
- PR 8 (`DeployService`, `DeployResult`). New facts since the synthesis: the post-flash stage holds the download-mode probe (deploy.py:241-258), which prints a hand request (:249). Printing is mixed into the flow at :205, :207, :210-212, :216, :223, :226, :229, :233, :249, :261-267. So `DeployService` needs a way to tell the person to press R, as a callback or a result field. `DeployResult` must hold the look report, `ReadyResult`, `facts_line`, the board log path, the store record path or its error (:263-265), and the consent `who`. `consent` must be a parameter of `deploy`, so P242 and P213 plug in. `verify(port)` is the post-flash stage and runs with no erase.

Order note: PR 6 comes before P242 only if P242 needs `matches`. It does not. P242 can use `report.reading.mac` and `report.verdict` as they are.

## #249 P242 (AI deploys to an allowed board)

Value proven by (replaces): The AI runs `deploy.py --token T` on a board the PO allowed, and no yes is typed for that run. The store's deploy record (board_facts.py:62, field `yes`) names who said yes and when. A board never allowed still asks for the yes in the PO's terminal. A look with a warning or an unknown field still asks too.

Now on main:
- `ConsentStrategy` has two members, `ask` and `who` (deploy_gate.py:41-48), and `require_ready` (:50). A standing-yes subclass fits. `deploy.py` builds the strategy after the look (deploy.py:217), so the MAC is known: `report.reading.mac`.
- The grant (P253) is `Grant(mac board_token granted_by granted_at expires_at)` (board_grant.py:30), kept in `GrantStore` as `grants/<mac>.json` (:77-103, store.py:65). The record says whose yes it was (`granted_by`, :132) and when (`granted_at`).

What is missing, so P242 does not reuse the live grant as it is:
1. No scope. The live grant means "let Claude run code on the board" (board_grant.py:128). The file has no field for what it allows. If deploy read it, every live grant also allows an erase. Add a `scope` field with a default, and read only a grant of the scope asked for. An old file with no scope reads as `live`. (board_grant.py:98 builds `Grant(**json)`, so a new field needs a default.)
2. One file per MAC (board_grant.py:82-89). A deploy yes and a live yes for one board replace each other. The key must hold the scope.
3. `granted_by` is the login name (board_grant.py:132). It ignores `ConsentStrategy.who`. Use `who` so the record and the deploy log say the same thing.
4. `GrantService.issue` refuses a board whose USB serial is not its MAC (board_grant.py:125). Deploy has a look, so it has the MAC. Deploy needs no serial rule. The issue path for the deploy scope skips it.
5. `grant.py` cannot issue a deploy grant (grant.py:61 has `--minutes` only). It needs a scope option. Its epilog and agents.md:125-134 change.
6. The expiry. `MAX_MINUTES` is one day (board_grant.py:34, checked :117 and :154). The card says "standing". Question for the PO below.
7. A new `StandingConsentStrategy(grants, mac, fallback)`. `ask` returns True when a valid deploy grant exists, else asks the fallback (`TerminalConsentStrategy`). `who` names the granter and the time. Chosen in `main` only when `report.verdict == "match"` (board_look.py:189), so the strategy never parses the question text.
8. Docs: commands/build.md:283 and agents.md:613-616 say the yes is never the AI's. They say "unless the board has a deploy grant". The AI never runs `grant.py` for it. agents.md:127 ("Never run grant.py --minutes") and :133-134 (never write a grant file) still hold.
9. Tests: AT116 recheck (deploy.py:220) must stay green with a standing yes. A new test: a live grant does not open the deploy gate.

Keep it one PR. It touches board_grant.py, grant.py, deploy_gate.py, deploy.py (one line), docs and tests.

Questions for the PO:
- Does the deploy yes end? Proposal: the same limit as the live grant (1 to 1440 minutes). "Standing" then means one yes for a day. A longer limit is a separate decision.
- A look with a warning or an unknown field: does the standing yes cover it? Proposal: no, it asks in the terminal.

## #192 P213 (/spark:deploy and --json)

Value proven by (replaces): A person or Claude finds deploy from `/spark:deploy`. The path runs from the image that passed to `ready` on the board: the dry run, the look and its token, the yes, the flash, the REPL line, the BOOT and RESET hint. `look.py --json` and `deploy.py --json` print the one envelope (`outcomes.envelope`, outcomes.py:68), with the token, the stops, the verdict, the board log path and the store record in `data`. A step that needs the person's yes carries `needs_yes` (outcomes.py:84). Proven at the bench, P192 (c), run through `/spark:deploy`.

Now on main:
- Neither script has `--json` (agents.md:410-411). The token only exists as a text line (look.py:14,53).
- No `commands/deploy.md` exists. The deploy section is inside commands/build.md:270-334 (deploy.py first named at :281).
- `deploy.main` mixes parsing, orchestration and printing (deploy.py:182-269), so `--json` needs P239 PR 8 first. That is why the order puts P213 last.
- `grant.py` and `live.py` already print one JSON line with their own fields (grant.py:49, live.py:64). They do not use the envelope. P213 uses the envelope, as the card says. Whether to move them is not part of this card.

What P213 needs from `DeployService` (PR 8): `plan()` for the dry run, `deploy(token, consent)` returning `DeployResult`, `verify(port)`, the consent as a parameter, and the press-R request as data. It needs the gate refusal as data too: `GateClosedError.code` (deploy_gate.py:32) and the rerun line (deploy_gate.py:23).

Suggested split, two PRs on this card:
1. `--json` for `look.py` and `deploy.py` (envelope, tests, agents.md:410-411 list).
2. `commands/deploy.md`, the build.md section shortened to point to it, agents.md, and the P192 (c) bench.

After P242, `/spark:deploy` has two paths to describe: the allowed board and the board that asks in the terminal.

## Added after the refuter

- Line numbers for deploy.py move when PR 5 lands. PR 5 also renames: `BOOT_HINT` (image_check.py:15) goes to `board_look.BOOT_HINT`, `runnable` (image_check.py:90) to `tools.command_for`, `DeployProblem` to `DeployError`. Cards use the names, not the lines.
- More text P242 makes untrue, to change in its PR: commands/build.md:296-302 ("the person runs it"), build.md's `allowed-tools` list (deploy.py is left out on purpose), store.py:62 ("one live grant per board"), board_grant.py:6, `GRANT_COMMAND` and `MESSAGE_FOR` (board_grant.py:41-53, which name only `--minutes N`), and agents.md:131-132 (the serial rule is stated for every grant).
- Refuter result: 5 claims rejected (board_look.py lines off by 35, a helper at board_look.py:86 that does not exist, board_doctor.py not in PR 6, the build.md range, the agents.md rule line). All fixed above. All other citations confirmed.
