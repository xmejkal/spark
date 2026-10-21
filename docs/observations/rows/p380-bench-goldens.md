# P380 goldens for the five bench CLIs: findings rows

Findings from planning and building P380 (2026-10-21, Prague). The plan council ran two rounds: a design reviewer on
Sonnet and the refuter on Opus, then a PO-assistant on Sonnet and a tech lead on Opus.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | A canned C6 flash id fails the S3 record, and an 8 MB S3 file on a C6 is a chip stop, not "flash differs" | refuter | acted | the fixture is the S3 project; `look-problems.json` uses `s3-flash-id-8mb.txt` |
| 2 | The 4 MB flash image cannot be checked in, because every install copies the repository | refuter | acted | `golden_bench.build_project` builds it at test time |
| 3 | `live` loads `boards/active.json` before any grant check | refuter | acted | `build_project` writes it |
| 4 | Firmware newer than the image adds a note, and a git checkout sets file times freely | refuter | acted | `build_project` makes the image the newest file |
| 5 | A bad-flag golden holds nothing, because argparse writes only to stderr | design reviewer | acted | cut |
| 6 | `reach` writes its could-not-run case only to stderr | tech lead | acted | cut; `check_golden` refuses an empty output |
| 7 | Without a token, deploy stops at "run look.py first", before the terminal check | tech lead | acted | the no-terminal Case takes look-ok's token |
| 8 | The image build gives one sha256 each run, so only the image half of the token needs a placeholder | tech lead | verified | the token prints as `5aed-<image>` |
| 9 | A stray `SPARK_ACCEPT` could rewrite goldens inside the push hook and pass | tech lead | acted | accept fails the test, and `run_script` drops the variable from the child |
| 10 | A child does not pick the scratch store, because it never imports unittest | Explore | acted | `run_script` sets `SPARK_HOME` to a store per Case |
| 11 | A fake package without `__init__.py` is a namespace package, and an installed mpremote wins over it | implementer | acted | each fake has an `__init__.py`; the first run had run the real mpremote |
| 12 | `reach --json` prints the moment of the run | refuter | acted | `golden_bench.MOMENT` replaces it with `<at>` |
| 13 | Ready seen, granted and ran need a faked board or clock | design reviewer, tech lead | acted | P383 #491 |
| 14 | The card's files, names and placeholders changed in the plan | PO-assistant | acted | #487's text has a section "Changed by the plan council" |
