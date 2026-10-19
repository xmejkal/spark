# P223 one board per project: findings rows

The plan council of P223 (#205). Plan: [`plan.md`](../../discovery/2026-10-19-p223-one-board/plan.md).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | Picking the sentence by matching "circuit" in text is a magic string | council | acted | `CHOOSING` maps the need's key to `design.one_board_message` |
| 2 | A relative `--circuit` path fails when `--project` names another folder | council | acted | the ambiguous paths are absolute; test feeds the path back |
| 3 | "check one" is wrong for init, which seeds rails | council | acted | "use one with --circuit" |
| 4 | Tests compared with the function's own output | council | rejected | `test_self_confirmation` asks for literals |
| 5 | The plan says the list stays relative, but the reason lists absolute paths | review, PR | acted | the plan now says the reason is absolute and the note relative |
| 6 | "Absolute" is false with `--project .`, because `discover` does not resolve | review, PR | acted | `m.resolve()` for the ambiguous paths |
| 7 | The note test checks only a part of the sentence | review, PR | acted | the full sentence with the path |
| 8 | With a relative `--project`, the named `--circuit` is relative and fails from another folder | refuter, PR | acted | row 6's `resolve()`; a test with a relative `--project` |
| 9 | `rules` can never be ambiguous, so only `package` keeps the generic sentence | refuter, PR | verified | `.spark/rules.json` is one fixed path |
| 10 | Init's advice fails without `--force`, because the rules were already written | refuter, PR | acted | init says `--circuit <path> --force` |
| 11 | "Give each board its own folder" is not enough: the folder needs its own `parts/` | refuter, PR | acted | the sentence says "with its own parts/" |
| 12 | Init says "2 built designs" then "no built design found"; check_all prints AMBIGUOUS after `--circuit` was given | refuter, PR | acted | card P320 #406 (on main before this PR) |
