# P675 the relayed yes (W4-4): rows

What the plan council and the session found while W4-4 was planned and built. Card:
[P675 #905](https://github.com/xmejkal/spark/issues/905). Plan: wave4-plan.md, W4-4, and its note of 2026-11-07.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | W4-4 had no card, though P476's comment said it would be filed when P657 merged | session | acted | filed as P675 #905, a sub-issue of #94 |
| 2 | The wave-4 text names `outside.consent`, which P657 replaced with `make_consent(line)` | session | acted | the note under W4-4 in wave4-plan.md |
| 3 | `issue` keeps the machine's login as `granted_by`, so a relayed grant would name the wrong person | session | acted | `ConsentStrategy.granted_by(user_name)` |
| 4 | Two `yes_kind == RELAYED` checks make a fourth kind change the gate and `issue` | Sonnet reviewer, plan | acted | one `opens_erase` attribute |
| 5 | A refusal before the token checks gives a rerun line with a missing or stale token and hides a real stop | refuter, plan | acted | the refusal sits after the token checks, a test keeps `token_missing` first |
| 6 | A closed gate leaves `data.yes` null, so json.md's kinds must not gain `relayed` | refuter, plan | acted | the test asserts null, and json.md keeps `"typed"\|"grant"` |
| 7 | `granted_by(self.user_name())` calls getpass for a relayed yes, which can raise | refuter, plan | acted | the callable is passed, and a test makes getpass raise |
| 8 | "relay" already means that Claude passes a sentence to the person (board_envelope.py:8) | refuter, plan | acted | the callable is `ask_in_program` |
| 9 | A live grant lets live.py run any code that names no restricted pin, so the docs must say "the erase", not every change to the board | refuter, plan | acted | never-assume.md section 7 says so |
| 10 | `FakeConsent` does not inherit from `ConsentStrategy`, so every test would fail on the new attributes | refuter, plan round 2 | acted | `FakeConsent` has both |
| 11 | The `opens_erase` check trusts the strategy's own attribute, so code in the same process can claim it | refuter, plan | acted | one docstring sentence on `ConsentStrategy`. The guard is the rule, as for the grant file |
| 12 | The full council that wave4-plan asks for would be today's second, over the PO's one-a-day allowance | session | raised | the lenses, the refuter and the mutation run go first, and the PO decides on a full council |
| 13 | `opens_erase = True` on the base class fails open: a new kind that forgets it opens the erase | tech lead, PR | acted | False on the base, True on the terminal and standing kinds |
| 14 | The "no CLI flag" test only looked for "relay" in flag names | tech lead, PR | acted | the test now finds no script but deploy_gate.py that builds the class |
| 15 | No test pinned the gate order with a stale token, and the code's list was loose | tech lead, PR | acted | a stale-token test, and the code asserted in `unchecked` |
| 16 | "relayed by ada through X" is unclear to a person; the grant sentence had two colons | journey, PR | acted | "given through X by ada", and both sentences rewritten |
| 17 | The docstring did not say how a frontend passes the class, or that only an exact True is a yes | examples, PR | acted | one docstring sentence each |
| 18 | how-it-works.md, scripts.md and commands/deploy.md were silent on the relayed yes; never-assume split a passage | docs lenses, PR | acted | one clause in each, and the never-assume sentences moved after the deploy record |
| 19 | The old W4-4 text and decision 6's line still read as the plan, and S9b was in the future tense | docs for humans, PO assistant, PR | acted | a lead line on the old text, "built" in decision 6, the past tense in S9b |
| 20 | A lost space in `report.warnings + [` | examples, tech lead, PO assistant | acted | restored |
| 21 | Three defects no row planted: printable dropped, the check before the tokens, NEXT_LOOK | mutation tester | acted | the first two planted by hand, both caught, and added to the table. NEXT_LOOK is pinned by the test that asserts the next op is deploy |
| 22 | The mutation table caught 8 of 8 | mutation tester | closed | `tools/mutate.py --copy`, 486 s |
