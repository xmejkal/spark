# The six-lens council over P130, P208 and the bin's B32, 2026-10-12

P130's pull request ([#174](https://github.com/xmejkal/spark/pull/174)) changed more than 50 lines but got the light
council, which the council's size table does not allow. So the six lenses ran on Sonnet over it and over P208
([#176](https://github.com/xmejkal/spark/pull/176)) in one pass each. One Sonnet reviewer read the bin's B32
([#29](https://github.com/xmejkal/sisuo-brain-transplant/pull/29)). One refuter on Opus then checked every finding.
P130 was merged while the lenses ran, so its fixes went into a follow-up pull request. Each row below is a merged
finding, and each is a row in [`INDEX.md`](INDEX.md), SL1 to SL23.

| id | change | the lenses' ids | verdict | what happened |
| --- | --- | --- | --- | --- |
| SL1 | P130 | PO1 UJ1 DH1 EX1 DA3 | holds | The README said that Simulate was partly done and that spark wrote no scenario. It now says works and names `run_scenario.py`. |
| SL2 | P130 | PO3 EX3 DH8 | holds in part | The committed log came from the first version. It is replaced by the run of the merged code, 10:51:44. PO3 was rejected, because that run passed. |
| SL3 | P130 | PO2 DA1 | holds | Auto mode or an allow rule would run a paid scenario unasked. The build page tells Claude to ask first, and TEAM.md names the script. An ask rule was offered to the PO. |
| SL4 | P130 | UJ7 DA4 DH5 | holds | wokwi-cli 0.27.1 refuses a scenario with no `name:` or `version: 1`. The example has both, and the page says which step takes `name:` and which takes `pin:`. |
| SL5 | P130 | UJ6 DH7 DA2 EX5 | holds | No step said that the firmware must print `ready`. The guide, the spark-design skill and the verification loop now say so, and that you create `sim/scenarios/`. |
| SL6 | P130 | DH4 EX2 DA4 UJ5 | holds | "Fails with that sentence" quoted none. The page quotes it. |
| SL7 | P130 | DH6 EX6 UJ8 | holds | `--help` had one sentence. It now names the cost, the token, the ready contract and the exit codes. |
| SL8 | P130 | DH3 | holds | Three guide pages did not list the script. They do. |
| SL9 | P130 | TL1 | holds | Only one path of `main()` had a test. Each exit code, each flag and each refusal now has one. |
| SL10 | P130 | TL2 | holds | A `firmware` line in single quotes read as none, so a run wrote one image while Wokwi ran another. Such a line is now refused. |
| SL11 | P130 | TL4 | holds | A screenshot path in a scenario resolved against a deleted temporary folder. The scenario now runs beside its original. |
| SL12 | P130 | UJ2 | holds | A project with no `firmware/main.py` paid for a run that cannot pass. It is now refused first. |
| SL13 | P130 | UJ3 UJ4 | holds | The token was asked before the build was checked, and the scenario path ignored `--project`. The free checks now come first, and the path is the project's. |
| SL14 | P130 | TL3 EX4 DH2 | holds, a suggestion | Every run used wokwi-cli 0.27.1, but setup installs 0.28.0. The guide names the version. A run on 0.28.0 is the PO's call. |
| SL15 | P208 | UJ9 UJ10 TL5 DH9 DH11 DA7 EX7 EX8 PO6 | holds | The glossary, W13 and a test comment still describe a table for every fix and the gate's anchors. To fix in P208. |
| SL16 | P208 | UJ11 DH10 DH12 DH13 DA5 DA6 PO7 | holds | No page gives the mutation job to anyone, and two lenses mutated inside a worktree. To fix in P208: the mutation tester, and the copy in `mutate.py`. |
| SL17 | P208 | TL6 EX9 UJ11 | holds | The epic-end command has no table and exits 2. To fix in P208 with `--for`. |
| SL18 | P208 | PO4 DH14 | holds in part | The rule set no bound. The arithmetic was rejected: 23 of 25 rows were caught by the nearby tests. To fix in P208. |
| SL19 | P208 | PO5 | holds in part | The 3 missing tests and the 615 s were only in scratch. To record in P208. |
| SL20 | P130 | RX1 | holds | A run past its wall clock left no log, though it spent minutes. It now leaves one. |
| SL21 | P208 | RX2 RX3 | holds | The agent must make one call, and a moved anchor must not count as an escape. To fix in P208. |
| SL22 | B32 | BR1 BR2 BR3 | BR3 holds | BR1 and BR2 were rejected. BR3 is fixed: each note says that the rail is only where the current is filed. |
| SL23 | B32 | RX4 | holds | V33's 0.5 A was estimated for the retired DFR0534. It is the bin's card B33 ([#30](https://github.com/xmejkal/sisuo-brain-transplant/issues/30)). |
