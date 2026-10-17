# P242 (#249): Claude deploys to a board the PO allowed once, the plan

> TL;DR: `grant.py --scope deploy --minutes N` keeps a deploy grant, a second file per board. `deploy.py` reads it
> through a `StandingConsentStrategy`, only for a look with verdict `match`, no `--ignore-older-runs` and a grant that has
> not ended. Everything else still asks in the terminal. `deploy.py` joins build.md's `allowed-tools`.

## Council

Round 1 (2026-10-17): a tech lead (Sonnet) and the refuter (Opus). The design is decided in
[the P218 brief](../2026-10-17-p218-finish/brief.md); this plan turns it into steps. Round 1 changed:

- Refuter, confirmed: `deploy.main`'s clock has no zone, and a grant time has one, so a subtraction would crash. The
  standing yes gets `board_grant.utc_now`, and `why_not_valid` returns `WHY_NO_ZONE` for a clock with no zone (test).
- Refuter, confirmed: a hand-written `expires_at` a year away turned valid in its last day. `why_not_valid` also reads
  `granted_at`: it must be a time with a zone, not in the future, and at most a day before `expires_at` (tests).
- Refuter, confirmed: the grant is not tied to a project or an image. Decision 6 below: the question and the docs say
  "any passed image of any project"; the PO can ask for a project binding later.
- Tech lead: a `consent` given to `main` wins and the grant is never read (test); `Grant` has `defaults=(SCOPE_LIVE,)`;
  hand-edited files (no zone, over a day, garbage date, unknown scope, a file that is no grant) fall back, never crash
  (tests); a deploy file alone opens no live grant, and the reverse (tests); `--scope` with `--check` and an unknown
  scope are refused (tests); `StandingConsentStrategy.require_ready` checks the expiry too; the fallback says why: new
  `DeployConsentResult(consent, why)` and the line `standing yes: not used: <why>`; the verdict constants replace every
  bare string; `FakeUtcClock` is used by the tests; the docs list adds how-it-works.md (setup.md and idea.md say nothing
  about deploy) and the press-R relay goes into build.md and agents.md.
- Rejected by the refuter: a `<mac>.json` and `<mac>-deploy.json` mix-up, MAC case, and a time-of-check gap.

Round 2: not run yet (tech lead and PO assistant, Sonnet).

## Decisions taken without the PO (routine; he can overrule)

1. `grant.py --scope` goes with `--minutes` only. `--check` stays about the live grant, because a deploy grant is found
   by the look's MAC, and a USB bridge board has no serial that equals its MAC.
2. A deploy grant skips the "serial is the MAC" rule (the brief: it stays for live grants only).
3. The expiry check is a module function `why_not_valid(grant, now)` in board_grant.py, not a private method: both
   `GrantService.check` and `StandingConsentStrategy.ask` call it, and a strategy has no service.
4. `board_look` gets `VERDICT_STOP`, `VERDICT_WARNING`, `VERDICT_MATCH` (no bare strings, the no-magic-strings rule).
5. When deploy.py falls back to the terminal for a clean look, its no-terminal line adds the deploy grant line, so
   Claude can relay it to the PO.
6. A deploy grant is for a board, not a project or an image: the token and the passed-run check still gate each
   image. Its question says so.
7. The bench run on the XIAO ESP32-C6 (the card's last done-when) is not done by this agent: step 9 is a hand run with
   a fake MAC. The PR says the bench run waits for the PO.

## Tests first (each fails before the code)

tests/test_board_grant.py
- a deploy grant keeps `grants/<mac>-deploy.json` with `scope: deploy` and leaves the live file alone, and the reverse;
- its question says it erases ALL of the flash and that no yes is asked for each deploy; minutes 0 and 1441 refuse;
- a deploy grant needs no USB serial equal to the MAC; a live grant still does;
- `find` refuses a live file with scope `deploy` and a deploy file with scope `live` (WHY_NOT_A_GRANT);
- an old file with no `scope` reads as a live grant;
- `consent_for_deploy`: standing for match plus a valid grant; the fallback for no grant, an ended one, a live grant
  only, a file whose scope differs, a warning, an unknown field, a stop, `ignore_older_runs`;
- `StandingConsentStrategy.who` reads "standing yes typed by ada at T, until U"; `ask` raises GateClosedError when the
  grant ended after the strategy was built.

tests/test_deploy_gate.py
- deploy.py with a valid deploy grant flashes with no terminal and no consent given; the store record's `yes` is the
  standing phrase; AT116 (image changes after the yes) and the token mismatch still refuse;
- each fallback case exits 2 with no terminal and erases nothing; the no-terminal text carries the deploy grant line.

Existing guards (tests/test_journey.py, the docs checks) stay green; commands/build.md lists deploy.py.

## Classes

```
 ConsentStrategy (deploy_gate.py)      who  ask  require_ready
   |- TerminalConsentStrategy          unchanged
   `- StandingConsentStrategy          NEW, board_grant.py: (grant, now); who = "standing yes typed by ..."
 Grant (Value)      mac board_token granted_by granted_at expires_at  scope=SCOPE_LIVE   (scope NEW)
 GrantStore         save(grant)  find(mac, scope=SCOPE_LIVE)     file: <mac>.json | <mac>-deploy.json
 GrantService       issue(..., scope)  check(port)  consent_for_deploy(report, ignore_older_runs, fallback)  NEW
 why_not_valid(grant, now) -> WHY_ code | None     NEW, shared by check and StandingConsentStrategy
```

## Sequence

```
 PO terminal          grant.py / GrantService                deploy.py (Claude's shell)            GrantStore
 grant.py --scope deploy --> look, ask yes ------------------------------------------------------>  <mac>-deploy.json
 ...later, no terminal...
                                                  look -> report (match, MAC)
                                                  consent_for_deploy(report, False, terminal)  --> find(MAC, deploy)
                                                  valid? -> StandingConsentStrategy ; else TerminalConsentStrategy
                                                  require_open_gate: stops, token, ask() = yes
                                                  erase, write, facts, ready
                                                  record_deploy(..., consent.who)
```

## Steps

1. Tests above (red). 2. board_look verdict constants. 3. board_grant: scope, store, `why_not_valid`, strategy,
`consent_for_deploy`, issue by scope. 4. grant.py `--scope`. 5. deploy.py builds consent after the look, prints
`standing yes:` and the fallback line. 6. build.md allowed-tools and prose. 7. Docs: grant.py and deploy.py `--help`,
docs/guide/agents.md, docs/guide/journey.md, README and tools/journey.py if a status moves. 8. Mutation table
tests/mutations/p242-deploy-grant.json, re-anchor moved tables. 9. Hand run in a scratch store with a fake MAC.

## Names, checked against developing.md's table

| Name | Role | Fits |
| --- | --- | --- |
| `StandingConsentStrategy` | Strategy | ends in `Strategy`, like `TerminalConsentStrategy` |
| `Grant` | Value | plain noun, gains one field |
| `GrantStore`, `GrantService` | Store, Service | unchanged names |
| `SCOPE_LIVE`, `SCOPE_DEPLOY` | constants | one word for one thing: scope |
| `consent_for_deploy` | method | says what it returns, for which flow |
| `why_not_valid` | function | the `why_` prefix answers a question about a Value |
| `FakeUtcClock` | Fake | `Fake` plus the whole name, in tests/fakes.py |

Words: "deploy grant" is the file; "standing yes" is the consent read from it. No other word is used for either.

## Risks

Accepted (brief, risk 5): Claude can write a grant file by hand. The deploy record and the board log name the image's
sha256, so the PO sees each flash afterwards. The one new gate is the allowed-tools line: with it, Claude Code runs
deploy.py without asking, and the grant is the only yes.
