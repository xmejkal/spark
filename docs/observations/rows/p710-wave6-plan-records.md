# P710 the wave 6 plan, records with sourcing: rows

What Fable 5.1 found while refining the records-with-sourcing group of the wave 6 plan, before its council. Card:
[P710 #959](https://github.com/xmejkal/spark/issues/959). Plan:
`docs/discovery/2026-10-19-p323-target-architecture/architecture/wave6-plan.md`, section "The records-with-sourcing
group (P710, at 8bfaeffa)". Every count is from `origin/main` 8bfaeffa. A row "acted" names the plan section that
changed. The council adds its rows below.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | the first count, "13 modules, 5,949 lines" | plan | verified | reproduced at 4e63057e: `store`, `boards`, `tools`, `provenance`, `deploy_record_store`, `brief`, `board_codes` (115 then), `board_pads`, `versions`, `parts`, `drawer`, `matching`, `cost`. It left out `onboard_parts.py` and `missing_facts.py`, which no page names. 15 modules, 6,189 lines now. The group section |
| 2 | `boards.footprint_stop` is "called in `main`" (`areas/records.md`) | plan | acted | five callers: `boards.py:956`, `init_project.py:401`, `:490`, `needs.py:513`, `parts.py:2222`. It moves to `footprint_emitter.py` in W6-R3a, and the page is corrected there |
| 3 | `board_codes.py` is the bench's leaf alone | plan | acted | 13 bench importers and `missing_facts.py:8` (`MISSING_FACT`, `:31`). `spark/core/codes.py` and `privacy.py` name it in comments only. W6-R2 gives `records_codes` its own `MISSING_FACT`, then W6-R3a moves the leaf into `spark/bench/` |
| 4 | the pull-up band's home | plan, P695 | acted | `PULLUP_MIN_OHM`, `PULLUP_MAX_OHM` (`rules_check.py:32`, `:33`) go to sourcing beside `i2c_pullup_problems` (`parts.py:484`) in W6-S2: sourcing sits below checks, and the band judges a part record's fact. Open: the PO may want it in design as a design rule, and design sits above sourcing, so `parts.py` could not read it |
| 5 | `validate` (`parts.py:619`) can live in `record_kind.py` | plan | acted | it calls the part rules (`host_part_problems`, `simulation_problems`), so records would import sourcing. It goes to `part_rules.py`, and `boards.py:830` reads the shape functions from `record_kind`. W6-S3a. Open: the exact function list of each module waits for the PR's scratch script |
| 6 | the `_op_` handlers can move with their names | plan | open | 30 `_op_*` functions import across modules after W6-S3b. No test names `parts._op_` (grep), so the rename is cheap, but it is a rename, so it is a card. The council may fold it into W6-S3b |
| 7 | the goal handlers belong in `spark/design/operations.py` | plan, `areas/design.md:7`, `:19` | open | they import `needs` and `footprint_emitter`, design's. A sourcing PR then adds a design module. The alternative, `spark/sourcing/goal_operations.py`, makes an upward edge |
| 8 | `MAY_READ` has 16 keys on the 15 | count | verified | `tests/test_self_confirmation.py:43` to `:96`: `boards.*` 9, `parts.*` 4, `board_codes.CODES`, `onboard_parts.ONBOARD_PARTS`, `tools.DOWNLOADS` |
| 9 | 728 mutation rows in 100 tables, 52 baseline keys, 230 import lines outside and 39 among | count | verified | a scratch `ast` walk over `scripts/`, `tests/` and `tools/`. The 51 lazy outside lines are all in tests. The per-PR row split of `parts.py` (est. 200 and 133) is a guess until the scratch script maps each `find` |
| 10 | a golden child never reaches the network | plan | verified | `store.fetch` (`store.py:403`) is the one `urlopen`, `_must_be_web` (`:385`) refuses `file:` outside `unittest`, the proxies point at a closed port, `tools.py --install` runs `curl` (`:403`) only without `--dry-run` (`:600`). Open: `cost.py` shells out nowhere (`NETWORK_SHELL`, `cost.py:33`, is a regex), but the PR probes it |
| 11 | `tools` and `operations` clash with no local | count | verified | neither is a local or a parameter in `scripts/` (grep). P694's lesson applies to neither |
| 12 | no function of `boards`, `tools`, `store` is between 41 and 60 lines without a key | count | verified | `boards.main` 53 and `validate` 147, `tools.plan` 68 and `main` 80 have keys. `ButtonPlaces` (45) and `DeployRecordStore` (53) are classes. `parts`: `simulation_problems` 56, `conflicts_of` 44, `_op_requirements` 44 go to W6-S2 |
