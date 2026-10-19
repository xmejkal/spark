# P324 plans are claims: findings rows

The refuter of PR #416, the only review of this small team tool (2026-10-19).

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | A reference with the wrong folder (tools/boards.py:340) passed by falling back to the file name | refuter, PR | acted | a path with a folder must match exactly; a missing case in the test |
| 2 | A URL ending in foo.py:12 was reported as a broken reference | refuter, PR | acted | the reference may not start after a colon, slash, word character or dot; a URL case in the test |
| 3 | Two mutations survived: one-digit counts, and the STANDARD names | refuter, PR | acted | a one-digit count in the test; STANDARD removed |
| 4 | STANDARD was unused weight: those names are already in scripts/ | refuter, PR | acted | removed |
| 5 | Two semicolons in the docstring and the --help epilog | refuter, PR | acted | rewritten, the epilog names all three failures |
| 6 | Names another committed doc mentions are not listed, and .sh, .yml and line ranges are not checked | refuter, PR | raised | the experiment's retro decides if they matter |
