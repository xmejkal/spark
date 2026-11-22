# P1001: a deploy with no simulation needs no sim/wokwi.toml: rows

Card: [P1001 #1459](https://github.com/xmejkal/spark/issues/1459). Found in the P934 walk, 2026-11-22 11:51 CET: the
look gave no token for the C6, "no sim/wokwi.toml in .: build with /spark:build --keep . first". The PO chose "Fix
now, then resume". This file holds the acted, raised and rejected findings only. 2026-11-22.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `ProjectImage` refuses a project with no `sim/wokwi.toml`, also under `--no-simulation`, so a board with no Wokwi part cannot be deployed | the walk | acted | `ProjectImage(project, default_without_toml=True)` stands for `sim/flash-with-firmware.bin`; `image_evidence.image_of(project, evidence)` asks for it when the evidence's `simulation` is `none`. The look and the three uses in `deploy_service` call it. Rows 1 to 3 of `tests/mutations/p1001-no-sim-toml.json`, each planted by hand and caught |
| 2 | a method `image_of` on the evidence classes | the first draft | rejected | 15 look tests use a `mock.Mock` as the evidence, whose method returns a Mock. A module function keyed on the existing `simulation` attribute needs no test change |
| 3 | the fix works on the board | the walk | acted | the branch's `look.py --no-simulation --json` on the walk project: status ok, verdict match, a token, the caveat "no simulation tested this image" and the records' limits |
| 4 | the hook's quick run fails `test_parts_describe_ok_txt` | the hook, 11:56 CET | acted | not from this change: P996 #1458 changed the `--requirements` help to "its outline or its simulation" and left the golden `parts-describe-ok.txt` with the old sentence, so main fails it. The golden takes P996's sentence; the rest of the file is unchanged |
| 5 | a board with no Wokwi part gets no `sim/` folder, and `flash_image.py` does not make it, so the documented build step fails with FileNotFoundError on a fresh project | PR refuter (Opus) | acted | fixed: `flash_image.py` makes the output's folder. A test and row 4. In the walk the session had made `sim/` by hand |
| 6 | `scripts/deploy.py`'s docstring and the `no_sim_toml` sentence in board_codes and firmware_codes do not name the no-toml case | PR lens (Sonnet) | dropped | dropped because they are incomplete, not false ("MVP first"); json.md says the rule |
