# P935 PR 1: the core's codes carry their meaning and fix: rows

Card: [P935 #1330](https://github.com/xmejkal/spark/issues/1330). This file holds the acted, raised and rejected findings
only. The plan check: the architecture lens and the refuter, both on Opus; council 2 on Fable (delegated, the PO's to
change). 2026-11-20.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a fix that differs in kind is a variant Code of the same word, named after its parent, not a dict of fixes | council 2, A | acted | `codes.BAD_ARGUMENT_REPLIES_UNREADABLE`, `_UNWRITABLE`, `UNKNOWN_REPLY_NEAR`, `BAD_REPLY_AS_ASKED`; codes.py's docstring says the core holds only its own contexts |
| 2 | input_unreadable gets a fix instead of null | council 2, B | acted | cli.py's `_unreadable_payload` raises `codes.INPUT_UNREADABLE` with its fix; json.md updated; a test sees the fix under `--json` |
| 3 | test_core's "the constants equal CODES" pin no longer holds with variants | the plan check | acted | changed, no weaker: each constant is a Code whose word CODES holds with its meaning, and each word is the constant named by it; test_json_contracts' pin over every table leaves out a variant, which `EveryCodeHoldsItsFixTest` holds to its word |
| 4 | the template check belongs in `codes.fix_of` at run time, not in the scan | the plan check | acted | a TypeError when a Code whose fix holds `%` comes with no fix; the scan has no template rule |
| 5 | the scan's fix rule must be tight | the plan check | acted | every part of a given fix, but the values right of a `%`, is the `.fix` of a Code of the call's word; the one exception is `text.bad_argument_fix`, named in `INJECTED_FIXES` |
| 6 | misfit_fix is a function the scan would have to follow | the plan check | acted | inlined into `reply_problems` as one if/else; its three assertions moved onto the Findings, the same bytes |
| 7 | `cli.CRASH_FIX` is only an alias | the plan check | acted | dropped; cli.py and test_core read `codes.CRASH.fix` |
| 8 | seven sites outside the core use `codes.BAD_ARGUMENT` | the plan check | raised | left for their areas' PRs of P935 #1330: pick_parts.py:70, audit_records.py:96, answer_operation.py:60, mark_step.py:38, set_facts.py:43, promote_record.py:35, write_skeleton.py:55 build a plain Finding with their own fix, byte-equal; a raise there with no fix now fails loudly through `fix_of` |
| 9 | P853's raised gaps (`**{"fix": ...}`, `Finding.__new__`, an alias of Finding, `_replace(code=...)`, `x.__class__(...)`) | P853 rows 8 and 9 | acted | the scan and test_core's rebuild scan name each, with a planted test |
