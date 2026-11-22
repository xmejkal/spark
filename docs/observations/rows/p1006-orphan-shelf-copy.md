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
| 5 | a copy is adopted by a listed project that holds another part under the same id, so a write changes a project the run never named | PR refuter (Opus) | acted | `orphan_home` adopts only when the holder's record has the copy's `name` and `kind`. A test and row 7 |
| 6 | `--step --json` and `--pick --json` leave the adoption out | PR refuter (Opus) | acted | `data.adopted` (ids) in both, in json.md; the exact `--pick` answer in test_needs gains the key |
| 7 | the dry runs of `--step` and `--pick` say nothing about the adoption | PR refuter (Opus) | acted | "would adopt ..." lines; `orphan_home` reads the folder the dry run would list (`listing`). A test and row 8 |
| 8 | `list_project` drops the "shelf copy not refreshed" reason | PR lens (Sonnet), refuter | acted | `NOT_ADOPTED`: "shelf copy of <id> not adopted: <why>" |
| 9 | no test through `/spark:init` or `--pick`, and scripts.md does not name the shelf write | PR refuter (Opus) | raised | P1014 [#1474](https://github.com/xmejkal/spark/issues/1474) |
| 10 | a library copy on the shelf could be adopted; the dry run of `--pick`; init's wording differs from --step's | PR lens (Sonnet) | raised | dropped because a library record is never shelved from a project, and the other two are by design or wording ("MVP first") |
