# P337 deploy without a simulation: findings rows

Gaps and findings from the agent runs of P337 #431 (2026-10-20). The plan is
`docs/observations/2026-10-20-p337-no-simulation/plan.md`.

## The plan's refuter (Opus, one round)

`tools/factcheck.py` on the fixed plan: 16 references ok, 0 broken, 4 new names the plan proposes.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The import check as the gate refuses PWM, `network` and `bluetooth` firmware, the walks this path is for | refuter | acted | the gate is now main.py, compile and image = firmware/; plan, Council |
| 2 | A missing firmware/ passes: `import_firmware.look` puts it in `unchecked`, and `files_under` gives `[]` | refuter | acted | PR B refuses no firmware/ and no main.py |
| 3 | A bool `standing_yes_allowed` cannot name the grant's WHY_ code | refuter | acted | `grant_refusal`, None or a WHY_ code (PR A) |
| 4 | deploy.py offers a grant hint that would never answer (`deploy.py:112`, `:209`) | refuter | acted | offered only when `grant_refusal` is None (PR A) |
| 5 | `interpreter_path` and a missing littlefs raise past `LookService.run` as a traceback | refuter | acted | PR B turns them into a sentence |
| 6 | The flag runs through 8 places, not 4 | refuter | acted | `evidence.argv()` in every step builder (PR A) |
| 7 | 9 places still say "passed" for a deploy that no simulation tested | refuter | acted | listed in the plan for PR B |
| 8 | The import check would run 3 times per deploy, one subprocess per module | refuter | acted | gone with row 1 |
| 9 | The plan's "tests pass unchanged except constructor calls" was false: 3 tests and 6 mutation files | refuter | acted | a false claim by the builder; tests and mutation tables changed in PR A |
| 10 | The refusal's build line can pick the wrong interpreter without `--project` | refuter | acted | PR B names `--project` |

## Process

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 11 | The builder ran `factcheck.py` on the plan only after the PO asked, and marked one claim "seen" before its grep | builder, the PO's question | raised | retro inbox; proposal: the push hook runs it on plan files |
| 12 | The PR A implementer did not re-run the whole suite after its last fix | builder | acted | the builder ran it before the PR |
