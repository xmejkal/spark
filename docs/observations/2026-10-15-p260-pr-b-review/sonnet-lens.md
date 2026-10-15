# P260 PR B (#285): the Sonnet lens

The reviewer had no shell, so each finding is PLAUSIBLE, read from the code only.

1. Same list as main for empty owed values, `body_mm` with one side, a missing `id` or `schema`, and the helpers at
   the end of `validate`.
2. The new skip keeps a problem that `_about` dropped, for example `host_parts[0] kind ...` when `kind` is owed.
   Rejected: `_about` matched a sentence that starts with the key or says "no <key>", not any substring, so main
   kept these problems too. `test_a_problem_that_merely_names_an_owed_key_is_still_broken` passes on main.
3. Before this PR: `chip_folder` (parts.py:365) reads `part["id"]`. A record with no `id` and a
   `simulation.wokwi.chip` raises `KeyError`, so `_shape_problems` gives one shape problem in place of the list.
4. Name: `skip` also names `simulation.skip` and a drawer field. `owed` says the role better (a nit).
