# Findings rows: loop backlog council, 2026-10-18

Rows for this council, kept here and not in `docs/observations/INDEX.md` (P296 #358 moves rows out of the shared file).

| id | finding | by | status |
|---|---|---|---|
| LB1 | The shipped XIAO record needs five facts (`power`, `power_pads`, `wokwi_power_pins`, `documents`, `physical`) to build; each removal fails | architecture, refuter (Opus) | verified; acted: item 1 |
| LB2 | Adding TX/RX does not clear the "no serial monitor" warning; the converter reads Wokwi's pin list (`converter.mjs:6797`) | refuter | verified; acted: clause dropped from item 1 |
| LB3 | The warning did not stop a XIAO scenario on 2026-10-14 (`2026-10-14-p215-bench.md:9`) | refuter | verified; acted: not a blocker |
| LB4 | The two XIAO records disagree on `deep_sleep.single_polarity_for_all_pins`, `adc_gpio`, `flash_mb` | refuter | raised; acted: folded into item 1 |
| LB5 | No buzzer in the library (`parts.py --need buzzer`); adding a second LED builds through simulation | PO assistant, refuter | verified; acted: LED for walk 1 |
| LB6 | `page.html` holds three images only; steps name no holes; a rebuild renumbers steps and prints false "move not kept" lines (after BtnTwo, not after LedTwo) | UX, refuter | verified; acted: items 2, 3, 16 |
| LB7 | `commands/build.md:354` says nothing ran on a board; the README records `ready seen` on 2026-10-15 | UX, refuter | verified; not acted (a docs fix for the next PR on build.md) |
| LB8 | `deploy.py`, `look.py`, `run_scenario.py`, `breadboard.py`, `init_project.py`, `tools.py` lack `--json`; `parts.py`'s `next` is never filled | AI-UX, architecture, refuter | verified; acted: items 6, 10, 11, 13 |
| LB9 | `ConsoleProbe.console()` reads 2 s but no CLI exposes it | AI-UX, refuter | verified; acted: item 9 |
| LB10 | The tools role `bench` already means sigrok; P295's runner needs another name | architecture, refuter | verified; acted: item 19 |
| LB11 | A `/spark:loop` page would repeat logic in a prompt; a facts script (`loop_status.py`) instead | AI-UX | acted: item 13, page dropped |
| LB12 | Architecture risk "a test pins `XiaoRealFootprint`" | refuter | rejected: no such name in `tests/` or `scripts/` |
| LB13 | Walk 1 must not wait for `/spark:deploy`; it named no firmware, scenario or journey update | round 2 tech lead, PO assistant | acted: items 5 and 7 split, done-when widened |
| LB14 | Change by words runs on today's core and needs no P297; jumper check and live view need no drag | round 2 tech lead | acted: dependencies loosened |
| LB15 | No card for "dark colors" style by words, the Artifact republish, or Czech shops | round 2 PO assistant | acted: items 16, 17, 21 |
| LB16 | "token", "board log", "console", "serial" each meant two things | round 2 tech lead | acted: a terms line |
