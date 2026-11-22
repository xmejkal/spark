# P1006: an orphan shelf copy follows the one listed project that holds it: rows

Card: [P1006 #1465](https://github.com/xmejkal/spark/issues/1465). Found in the P934 walk, 2026-11-22 11:41 CET: the
shelf copy of the e-paper record had no `based_on`, so no write refreshed it, and the build drew no breadboard. The
plan was checked once by the refuter (Opus). This file holds the acted, raised and rejected findings only. 2026-11-22.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a record shelved while its folder was on no list gets a copy with no `based_on`, and `record_path` never lets it follow its record | the walk; the plan check | acted | `record_home.orphan_home`: a copy with no `based_on`, no catalog record of its id, and one listed project holding it belongs to that project; `record_path` uses it on both paths. Rows 1 to 5 of `tests/mutations/p1006-orphan-shelf-copy.json`, each planted by hand and caught (row 3 after a test for a copy that names another project) |
| 2 | only a write that touches the id would heal it, so old orphans stay | plan check (refuter, Opus) | acted | `record_home.list_project`: listing a folder (`/spark:init`, `--step`, `--pick`) adopts the orphan copies of its records and says each; a test through `--step`; row 6 |
| 3 | the writer rule in json.md, scripts.md and commands/idea.md names only "the project a shelf copy came from" | plan check (refuter, Opus) | acted | the three lines name the orphan case |
| 4 | in the PO's store, `dfr0664-tft-2in` is held by two listed projects, and `sen0193-soil-moisture` has a catalog record | plan check (refuter, Opus) | verified | both guards hold: no adoption for two holders or a catalog id; tests pin each |
