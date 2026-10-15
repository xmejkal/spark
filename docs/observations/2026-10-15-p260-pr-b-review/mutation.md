# P260 PR B (#285): the mutation tester

The first run planted 9 defects and the suite caught 7. The `id` guard escaped: no test showed that a record that
owes `id` skips the id-and-file-name check. The footprint guard escaped too, and the refuter showed it repeated
`_absent`, so it was removed. A new assertion in `test_validate_does_not_check_an_owed_required_key` covers `id`.
The kept table is `tests/mutations/p260-owed.json` (8 rows). Its rerun result is below.

Rerun, 2026-10-15: `tools/mutate.py --copy tests/mutations/p260-owed.json` caught 8 of 8 (329 s).
