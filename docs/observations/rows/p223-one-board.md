# P223 one board per project: findings rows

The plan council of P223 (#205). Plan: [`plan.md`](../../discovery/2026-10-19-p223-one-board/plan.md).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | Picking the sentence by matching "circuit" in text is a magic string | council | acted | `CHOOSING` maps the need's key to `design.one_board_message` |
| 2 | A relative `--circuit` path fails when `--project` names another folder | council | acted | the ambiguous paths are absolute; test feeds the path back |
| 3 | "check one" is wrong for init, which seeds rails | council | acted | "use one with --circuit" |
| 4 | Tests compared with the function's own output | council | rejected | `test_self_confirmation` asks for literals |
