# P213 b1 deploy command: findings rows

The plan council of P213 part b1 (#192). Plan: [`plan.md`](../../discovery/2026-10-19-p213b1-deploy-command/plan.md).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | PR a of P213 (`--json` for look and deploy) is on main already; the card's "now on main" is stale | lead, before the plan | acted | merged in #378; the card gets b1 and b2 |
| 2 | Card C (the button's place) needs the PO's photo as its source (AT158) | lead, before the plan | acted | moves to b2, at the bench |
| 3 | `check_docs.unlisted` needs `/spark:deploy` in the README and `docs/guide/commands.md`, and the plugin text names commands | council | acted | all three name it |
| 4 | Claude inside `/spark:build` does not load the deploy page, so build.md must keep the order | council | acted | build.md's section says the order in one sentence and the restart |
| 5 | `image.sha256` is read twice | council | acted | read once in `verify` |
| 6 | A grant's `who` is long | council | acted | `yes:` is the line's last part |
| 7 | getpass can fail, and the new line read `consent.who` before the store record could say so | lead, tests | acted | the line says "not known (...)"; the store record still names the error |
| 8 | build.md said "Nothing has run this on a board yet", which the journey contradicts (2026-10-14) | lead, the move | acted | `commands/deploy.md` says when it first ran, with the journey link |
| 9 | 84 rows of the mutation tables have anchors that no longer match | lead, `mutate.py --anchors` | raised | the same 84 on main; not this PR's |
