# P418: OC8, one leaf for the three text guards, findings rows

Findings from the plan councils, the build and the review of P418 (2026-10-26, Prague). The build checked each claim
of the approved plan in the code.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | `tools/mutate.py --anchors tests/mutations/*.json` passes, so the PR can require it | plan | rejected | on main it refuses 102 of 2026 rows. The check became "the refused set after the PR is main's, minus the rows this PR fixes": 101 after the PR, each also refused on main |
| 2 | Nine rows name the moved code, in three tables | plan, round 1 | acted | two more: `sprint-10-p95-final.json` ("C1 and bidi controls stay") anchors the `CONTROL` literal, and `sprint-10-p95-5.json` ("a label keeps its control characters") was refused since `clean` got its cap. Both point at `text_guards.py`, and the second works again |
| 3 | Dropping `import parts` from `emit_footprint` ends the cycle through `parts.audit` | plan draft | rejected | `emit_footprint` imports `design`, and `design.py:41` imports `parts`. Only the direct edge goes, and plan v2's "wave 2 removes no cycle" stays true |
| 4 | The new test file needs only `ast` and `unittest` | plan, round 2 | acted | `tests/test_suite_temp.py` fails any test file without the `suite_temp` header. The new imports in `parts`, `assign_pins` and `emit_footprint` also need `# noqa: E402` |
| 5 | The wave order is "the PO's order" from the comments on #94 | plan, round 1 | acted | no comment holds an order. It is the between-cards council's order after P335, which the PO accepted in chat on 2026-10-26. The plan says so |
| 6 | The relayed-yes guard and slice S9b are the PO's decisions | plan, round 1 | acted | the comment on #94 records the guard as "the reading recorded here", which the PO can change, and names no slice. Plan v2 marks both as a recorded reading and a proposal |
| 7 | Moving the regexes with a file write keeps them as they were | build | acted | the write turned the `\u` escapes of `CONTROL` and `COMMENT_UNSAFE` into real bidi and line-separator characters. The tests passed, because the sets matched the same text. A mutation anchor showed it. Both lines were copied byte for byte from main (commit 14d6dae), and a scan finds no character above U+007E but `§` and `—`. Learned rule logged |
| 8 | `printable` belongs in the test's `MOVED` table | review | rejected | its old module `screen_text` is gone, so any import of it fails at once. `parts.printable` worked on main too, so it is no moved name |
| 9 | `docs/2026-10-12-p211-matching-design.md:44` must say `text_guards.CONTROL` | review | rejected | a dated design record, which the plan keeps as history |
| 10 | `tests/test_imports.py` catches every way to reach a moved name | review | raised | it misses `from drawer import *`, `getattr(drawer, "clean")` and `importlib`. None exists in `scripts/` today. S3's rules test can widen it |
| 11 | `store.CONTROL_CHARACTER` (`store.py:107`) is a fourth copy of the character set, with U+2028/9 added | plan, round 2 | raised | it refuses a file name, while `clean` replaces characters, so it stays apart here. The PO's "reuse every fact" asks whether one set can serve both. For the between-cards council |
| 12 | "build" means the build chain and the MicroPython build a board names (`micropython_port`, `flash_image.board_build`, `build_entry`) | plan draft | raised | dropped from this PR, because no answer of the PO asked for it. A clash row for section 3 of plan v2, for the between-cards council |
| 13 | `areas/firmware.md:137-138` cite `flash_image.py:33` and `:89` | plan draft | raised | stale since P335. Today the image is `flash_image.image` and the board's build is read by `board_build`. Out of OC8's scope |
| 14 | `CONTROL` and `COMMENT_UNSAFE` say their role | plan, round 1 | raised | two names for "characters to strip" in one module now. A rename waits for OC3, which reads both |
| 15 | No behavior change | build | acted | every code line of `text_guards.py` equals a line of main's `drawer.py`, `parts.py` or `screen_text.py`, and the callers only lost their module prefix (a script compared them) |
| 16 | Plan v2 records all eight of the PO's answers | refuter | acted | Q1, *"quck now, split later"*, was missing from section 9's lesson 1 row. It is there now |
| 17 | The penalty staying in `assign_pins.py` is the PO's decision | refuter | acted | it is the example recorded with his Q5 answer (*"leta go with a then"*). Section 6 and section 7 now say it is a reading he can change |
| 18 | The eleven changed mutation rows still plant their defect | refuter | acted | `mutate.py --copy` on the branch caught all 11, and the suite was green after (1735 s) |
