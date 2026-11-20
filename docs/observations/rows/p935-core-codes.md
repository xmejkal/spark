# P935 PR 1: the core's codes carry their meaning and fix: rows

Card: [P935 #1330](https://github.com/xmejkal/spark/issues/1330), PR [#1342](https://github.com/xmejkal/spark/pull/1342).
This file holds the acted, raised and rejected findings only. The plan check and the PR's review: the architecture lens
and the refuter, both on Opus; council 2 on Fable (delegated, the PO's to change). 2026-11-20.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a fix that differs in kind is a variant Code of the same word, named after its parent, not a dict of fixes | council 2, A | acted | `codes.BAD_ARGUMENT_REPLIES_UNREADABLE`, `_UNWRITABLE`, `UNKNOWN_REPLY_NEAR`, `BAD_REPLY_AS_ASKED`; codes.py's docstring says the core holds only its own contexts |
| 2 | input_unreadable gets a fix instead of null | council 2, B | acted | cli.py's `_unreadable_payload` raises `codes.INPUT_UNREADABLE` with its fix; json.md updated; a test sees the fix under `--json` |
| 3 | test_core's "the constants equal CODES" pin no longer holds with variants | the plan check | acted | changed, no weaker: each constant is a Code whose word CODES holds with its meaning, and each word is the constant named by it; test_json_contracts' pin over every table leaves out a variant, which `EveryCodeHoldsItsFixTest` holds to its word |
| 4 | the template check belongs in `codes.fix_of` at run time, not in the scan | the plan check | acted | a TypeError when a Code whose fix holds `%` comes with no fix; the scan has no template rule |
| 5 | the scan's fix rule must be tight | the plan check | acted | every part of a given fix, but the values right of a `%`, is the `.fix` of a Code of the call's word; the one exception is `text.bad_argument_fix`, named in `INJECTED_FIXES` |
| 6 | misfit_fix is a function the scan would have to follow | the plan check | acted | inlined into `reply_problems`; its three assertions moved onto the Findings, the same bytes |
| 7 | `cli.CRASH_FIX` is only an alias | the plan check | acted | dropped; cli.py reads `codes.CRASH.fix`, and test_core pins the fix as a literal (test_self_confirmation refused `codes.CRASH.fix` as the expectation) |
| 8 | sites outside the core use core codes with their own fix | the plan check, the review | raised | left for their areas' PRs of P935 #1330: pick_parts.py:70, audit_records.py:96, answer_operation.py:60, mark_step.py:38, set_facts.py:43, promote_record.py:35, write_skeleton.py:55 build a plain Finding of `BAD_ARGUMENT`; research_part.py:189 raises `BAD_ARGUMENT` with its own fix; known_board.py:311 builds a plain Finding of `NEEDS_REPLY` with its own fix. All byte-equal; a raise of a template code with no fix now fails loudly through `fix_of` |
| 9 | P853's raised gaps (`**{"fix": ...}`, `Finding.__new__`, an alias of Finding, `_replace(code=...)`, `x.__class__(...)`) | P853 rows 8 and 9 | acted | the scan and test_core's rebuild scan name each, with a planted test |
| 10 | an alias (`CRASH_TOO = CRASH`) passed as a variant: a variant must show its parent and differ from it | the review's refuter | acted | the table filter takes only `<PARENT>_...` names; `variants_off_their_parent` names a variant off its parent's name or holding its parent's fix; a planted test and two rows |
| 11 | an unfilled template, `codes.BAD_ARGUMENT.fix` given bare, passed the scan and `fix_of` | the review | acted | `foreign_fix` takes a template's `.fix` only left of a `%`; a planted line and a row |
| 12 | input_unreadable's fix did not fit stdin and did not stand alone | the review | acted | "make the file or the stdin that the sentence names hold JSON, then run again"; json.md and the `--json` test follow |
| 13 | the read-only replies-file pin passes under root | the review | acted | `skipIf` root, as test_check_vendor_pins does |
| 14 | two global `MAY_READ` entries for one test | the review | acted | dropped; the template test raises a local `Code("x_bad", ...)` with literal expectations |
| 15 | the scan's loop wrote the `**` check twice and the `_replace` receiver check inline | the review | acted | one `**` check above the if-chain, plain ifs in `codes_own`, the helper `made_from_its_own_fix` |
| 16 | `reply_problems` tested `lacks` twice | the review | acted | one `if lacks:`; the two cases are in `_misfit`, because two nested ifs there break rule R2 (nesting 4) |
| 17 | patterns-and-names.md's sentence was over 120 characters, verbless, and vague on what the test fails on | the review | acted | rewritten at 120: "a fix that differs in kind is a variant, a Code of the same word", and the test fails "on a code off its table, or a fix not its code's"; paid by cutting `(spark.core.errors)` |
| 18 | the PR body's left-out list and the mermaid | the review | acted | research_part.py:189 and known_board.py:311 added; BAD_ARGUMENT drawn as an instance of Code |
| 19 | `parts.py --step <proj> nope --json` prints `bad_argument` with fix null: mark_step's `_cannot` builds a dict and never calls `fix_of` | the review | raised | a line on card P935 #1330; the sourcing area's PR moves it |
| 20 | a literal `%` in a future fix is refused by `fix_of`'s guard | the review | rejected | dropped because such a fix writes `%%`, the D5 rule |

A note from the review: `_unreadable_payload` always says `INPUT_UNREADABLE`; no other CodedMessageError reaches it today.
