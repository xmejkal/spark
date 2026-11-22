# P989: a board file that a project wrote reaches the store's shelf: rows

Card: [P989 #1442](https://github.com/xmejkal/spark/issues/1442). The PO at the p934-display page, 2026-11-22: "do the
beetle 2 c6 that we created is not even there. We have to make sure when any project usus or adds/modifies a board, it
appears in the store". The walk's rows are in `~/Development/spark-walks/p934-display/diary.md`. The plan check: a lens on
Sonnet and the refuter on Opus, one round (v2 of the plan). This file holds the acted, raised and rejected findings only.
2026-11-22.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the shelf layer alone sends a write of a shelf board to the shelf copy, and leaves the project it came from behind | the plan's scratch run | acted | fixed: `record_home.record_path` looks in the board shelf for a board and finds its home in the project's `boards/`; `refresh_shelf_copy` compares with the copy's own shelf (`part_facts.shelf_of`). Tests `test_a_shelf_copy_of_a_listed_project_s_board_is_filled_in_that_project_and_shelved_again`, mutation rows 7 and 8 |
| 2 | the walk's C6 link exists already, so no new link shelves it: the boards already linked need a one-time sweep | the plan, §1 | acted | a throwaway script in the session's scratch (`plans/p989-sweep.py`), not in the tree. Proved on a copy of the store without `sources`, `downloads`, `toolchain` and `miro`; its output is below. The session runs it on the PO's store after the merge, dry run first |
| 3 | a board on the shelf shadows spark's library board of the same id for every project (R1) | the plan, risk R1 | raised | dropped because MVP first: one rule for parts and boards, the shelf before the library (session decision Q2); the refuter found no case through the three ways onto the shelf |
| 4 | `--requirements` shelving a board picked from another project (W1) can name a broken board, and no walk needed it | the plan check, lens 1, refuter 4 | rejected | dropped because MVP first: W1 is cut, a link in the drawer is the one way a board reaches the shelf by a new act |
| 5 | `boards.py --list` and `--validate` call a shelf board "(project)", from its folder | the plan check, refuter 2 | acted | fixed: both take the layer `board_records.records` gives. `test_a_shelf_board_is_listed_and_validated_as_the_shelf_s`; the P707 row "every board is called the library's" re-anchored on the row's `layer`; row 10 |
| 6 | the unlisted-folder refusal of `--drawer-set` says "part contract" and `parts.py --validate` for a board | the plan check, refuter 6 | acted | fixed: it says the board contract and `boards.py --validate --project .`; the "not shelved" line too. `test_a_board_that_breaks_the_board_contract_is_not_shelved`, row 6 |
| 7 | the board-shelf branch of `_write_record` had no test, and four docstrings became untrue | the plan check, refuter 6 | acted | fixed: `test_a_shelf_board_whose_project_has_lost_it_is_filled_where_it_is_and_stays_private` (0600), row 9; `find_nearest_records`, `board_records.records`, `board_records.available` and `_board_problems` say the shelf |
| 8 | the shelf copy's digest uses a part's facts for a board, `_make_ready` leaves a new middle folder 0755, and init `--board` or a build could shelve a board too | the plan, §7; the plan check, refuter 8, lens 5 | raised | dropped because MVP first: nothing reads that digest, the sweep's run made `shelf/` 0700 because it was there already, and a link or a write covers the walk |
| 9 | button-light's `boards/xiao-esp32-c6-fresh.json` is no drawer link, so the sweep leaves it where it is | the plan check, lens 4 | acted | on purpose: the sweep shelves only what a drawer entry links to. A later link to it shelves it |
| 10 | json.md has no `--drawer-set` `shelved` line to widen, so no json.md line changes | the build | acted | the store design (§5.1, §5.5) and the scripts.md shelf bullet say it |

## The sweep, proved on a copy of the store

`SPARK_HOME=<copy> python3 plans/p989-sweep.py --dry-run`, run from this branch's tree, 2026-11-22 08:57 CET:

```text
store: <copy> (dry run)
  dfrobot-dfr0975 -> firebeetle2-esp32s3: left, it is in library
  dfrobot-dfr1075 -> firebeetle2-esp32c6: would shelve from p934-epaper (~/Development/spark-walks/p934-epaper/boards/firebeetle2-esp32c6.json)
  lilygo-ttgo-t-display-esp32-v1-1 -> lilygo-t-display: would shelve from t-display (~/Development/spark-walks/t-display/boards/lilygo-t-display.json)
  seeed-xiao-esp32-c6 -> xiao-esp32-c6: left, it is in library
```

`diff -r` of the copy against a second copy made before: no difference. Then the run without `--dry-run`:

```text
store: <copy>
  dfrobot-dfr0975 -> firebeetle2-esp32s3: left, it is in library
  dfrobot-dfr1075 -> firebeetle2-esp32c6: shelved from p934-epaper (~/Development/spark-walks/p934-epaper/boards/firebeetle2-esp32c6.json)
  lilygo-ttgo-t-display-esp32-v1-1 -> lilygo-t-display: shelved from t-display (~/Development/spark-walks/t-display/boards/lilygo-t-display.json)
  seeed-xiao-esp32-c6 -> xiao-esp32-c6: left, it is in library
```

`diff -rq` against the copy made before: `Only in store/shelf: boards`. `shelf/boards` is 0700, both files 0600, and their
`based_on.project` are `p934-epaper` and `t-display`.

## The value, on a copy of p934-display

With the store copy before the sweep, then after it:

```text
parts.py --match .   before:  owned 2    firebeetle2-esp32c6 (p934-epaper)   microcontroller  free 0, held by p934-display, p934-epaper
                     after:   owned 2    firebeetle2-esp32c6 (shelf)         microcontroller  free 0, held by p934-display, p934-epaper
init_project.py      before:  no board chosen. Available: firebeetle2-esp32s3, xiao-esp32-c6
                     after:   no board chosen. Available: firebeetle2-esp32c6, firebeetle2-esp32s3, lilygo-t-display, xiao-esp32-c6
```
