# P221 Arduino and other platforms: findings rows

Gaps and findings from the agent runs of P221 #203 (2026-10-20). The plan is
`docs/discovery/2026-10-20-p221-arduino/plan.md`.

## Round 1 refuter (Opus, `refuter-1.md`)

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The PR count does not add up: the total is 14 to 16, not 12 to 18 | refuter-1 item 1 | acted | ranges recomputed per slice; plan, section 4 |
| 2 | Three pieces of work have no PR: the setup, Wokwi for an Arduino image, the docs and prompts | refuter-1 item 2 | acted | A1, A5, A7 and A8 in the plan |
| 3 | verify-flash adds nothing, because esptool's write already checks the MD5 | refuter-1 item 3 | acted | no verify-flash; plan, Council |
| 4 | "No facts on the board" overrode D22 and D34 unnamed | refuter-1 item 4 | acted | decision 4 names them |
| 5 | P323 is a draft that waits on the PO's yes, not settled | refuter-1 item 5 | acted | decision 5 and the P323 paragraph |
| 6 | The import check on a lone `.ino` prints `problems` and exits 1, not could-not-run | refuter-1 item 6 | acted | `CompileFirmwareCheck` replaces it (A3) |
| 7 | The Arduino install is 6 GB to fetch and 12 GB on disk | refuter-1 item 7 | acted | risk 1 and the cost basis |
| 8 | Rejected: the C6 needs no CDCOnBoot setting, `boards.txt` has `cdc_on_boot=1` | refuter-1 item 8 | rejected | the claim was wrong; arduino-cli stays the second platform |
| 9 | W1 has no single rule for a step a platform lacks | refuter-1 item 9 | acted | the skip rule, in `PlatformContract` |
| 10 | `tools/factcheck.py` found 0 broken references | refuter-1 item 10 | closed | rerun on the final plan |

## Lens disagreements the syntheses settled

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 11 | A build id cannot hold its own sha256 | lens synthesis | acted | the id names the inputs, and the image keeps its own sha256 |
| 12 | The import check on a lone `.ino` cannot run on a compiled platform | lens synthesis | acted | a compile check replaces it on compiled platforms |

## Round 2 refuter (Opus, 7 confirmed, 2 rejected)

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 13 | `micropython_port` has more readers (`tools/snapshot.py:75`, `tests/test_boards.py:414`, `data/tools.json:153-181`, fixtures, stores) | round 2 refuter | acted | R2 reads the new key first and falls back; `--get micropython_port` keeps answering |
| 14 | Official espressif32 supports the C6 with ESP-IDF (`round2-idf-pio.md:77`), so only PlatformIO for Arduino needs the fork | round 2 refuter | acted | slice 3, risk 3 and the disagreements |
| 15 | Nothing named the link from the tools.json role to the code choosing `PlatformioImageBuilder` | round 2 refuter | acted | P1 names `ImageBuilderChoice` |
| 16 | The role `firmware-image` names the interpreter, against the plan's own rule. `arduino-builder` is Arduino's legacy tool name | round 2 refuter | acted | R4 renames it `interpreter-image` with a fallback read; the role is `arduino-compiler`; "role", not "job" |
| 17 | A0 must run before R1, to answer the PO's MVP question and test the C6 first | round 2 refuter | acted | the Order paragraph, decisions 6 and 10, risk 2 |
| 18 | W1 needs each step and its `skipped` cause listed | round 2 refuter | acted | the list under the skip rule |
| 19 | Line numbers moved on today's main (R1, R6) | round 2 refuter | acted | symbols cited: `_deploy`, `ScenarioRun`, `ReadyCheck.check`, `DeployService.verify` |
| 20 | "PlatformIO is a build tool, not a language" | round 2 refuter | rejected | the claim holds; no `toolchain` key |
| 21 | Wokwi needs a new token for compiled images | round 2 refuter | rejected | MicroPython already needs `WOKWI_CLI_TOKEN` (`run_scenario.py:248-251`) |

## Process

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 22 | The PO stopped round 1's fixes and asked for round 2 with ESP-IDF and PlatformIO as certain platforms | PO, 2026-10-20 | acted | round 2 ran three agents, then the refuter |
