# Round 2: tech lead

Opus, 2026-10-18. Scratch store under the session scratchpad, `SPARK_HOME` inline, no USB, no Wokwi token.

> **TL;DR.** The order holds, but four dependencies are too strict (3, 12, 16, 19), item 6 contradicts the refuter's
> verdict on walking with plain `deploy.py`, and walk 1 never says who writes the firmware and the scenario. Two words
> mean two things ("token", "board log"/"console"). Item 1's command is not runnable as written.

## Reproduced

- `check_spine.py` takes the requirements file first: `check_spine.py req.json --keep DIR` (`check_spine.py:631-635`).
  Shipped XIAO, button + LED: exit 2, "the board states no power.io_volts". FireBeetle: exit 0, writes `breadboard.md`
  and `page.html` but no `breadboard.json`. So today only the `xiao-esp32-c6-fresh` fixture yields a kept layout.
- `ConsoleProbe` is at `board_console.py:86`. Signals already take a `pin` (`assign_pins.py:220`).
- `deploy.py` uses "token" for the look token (`deploy.py:6-7`); item 10 uses "token" for the Wokwi token.
- "Envelope" is defined only for `parts.py` (`agents.md:339`, `:362`).
- P279 #317's done-when is a build check on `breadboard.json` against `circuit.json`. It has no page in it.

## Findings, each with a fix

1. **Item 1's done-when is not runnable.** `check_spine.py --keep` with `"board"` in it reads as one call. Fix: "with a
   requirements file of tactile-button + led-red-5mm on `xiao-esp32-c6`, `check_spine.py req.json --keep DIR` exits 0
   and DIR holds `breadboard.json`". Move "a `ready` scenario passes once" to item 6: it needs a firmware, a scenario,
   the PO's token and paid minutes, none of which item 1 makes. Item 1 then has a CI test.
2. **Items 2 and 3 do not depend on 1.** Both can be built and tested on the `xiao-esp32-c6-fresh` fixture, which the
   breadboard tests already use (`tests/data/breadboard/button-light-xiao`). Fix: depends on "none"; they need 1 only
   for the walk. Three S items then run in parallel within the WIP limit.
3. **Item 2 carries more than the refuter allowed.** The refuter said labels can wait for the diary; item 2 still asks
   for row, column and pin labels on the picture. Fix: drop the labels from item 2 (holes in the steps only), and card
   the labels after walk 1 if the diary asks.
4. **Item 3 is M, not S.** It must diff two layouts into hand actions and also clear the false `move not kept` lines
   after adding BtnTwo (refuter verdict 6; P292 folded in). Fix: size M, or keep P292 as its own S before item 3.
5. **Item 6 contradicts the refuter.** The refuter's verdict: walk 1 with plain `deploy.py`, P213a/b beside it, fed by
   the diary. Item 6 depends on 5 and joins `/spark:deploy` to the walk; choice 3 hides the disagreement. Fix: split
   into 6a "walk 1 with `deploy.py`" (depends 1-4) and 6b "`/spark:deploy`" (depends 5, 6a's diary). Or state in the
   Council section that the synthesis overruled the refuter, and why.
6. **Walk 1 is missing two hand-overs.** Nobody writes `firmware/main.py` or `sim/scenarios/*.scenario.yaml`
   (`build.md:218-223`), yet both gate the deploy. The second LED needs both changed too. Fix: add to item 6: "Claude
   writes `firmware/main.py` and one scenario, `import_firmware.py` and `check_all.py` pass, and after the second LED
   both are updated before the second deploy." Start walk 1 with `/spark:init` in a new folder, so the "have" column
   and the rules file are tested (first-time install stays item 10).
7. **Item 6 lacks the journey update.** AGENTS.md: a step's status change updates the README table and
   `tools/journey.py` in the same PR. Fix: add "README 'What works today' and `journey.py` show step 7a green".
8. **Item 12 does not need P297.** Story 1 is a change by words: Claude edits `requirements.json` (or a `parts.py`
   operation) and rebuilds; the missing core part is removal in `_merge_parts` (`needs.py:486`, "kept, not from a pick"
   at `parts.py:2250`). P297 decides only how a person's edit reaches Claude, which is item 15. Fix: depends "3", and
   delete "Shape decided by P297" from item 12.
9. **Item 13's research half waits for nothing.** The buzzer record and `parts.py --need buzzer` need no swap. Fix:
   split, or mark "research: none; the swap: 12".
10. **Item 16 depends on 15 without cause.** A live view needs a page (14), not dragging (15). Fix: depends "14, P297".
11. **Item 19 depends on 15 without cause.** P279 is a build check with no page. A wrong jumper makes item 3's bench
    lines wrong. Fix: depends "none", and place it right after the MVP line.
12. **Item 10's dependency on 8 is weak.** Reading the token from the store needs no `--json`. Fix: depends "none".
13. **One word for one thing.** (a) "token" means the look token (item 5) and the Wokwi token (item 10). Fix: "look
    token" and "Wokwi token" everywhere. (b) "board log" (5, 6) and "console" (5, 7) and "serial" (map, table). Fix:
    "board log" = the file in `sim/runs/board/`; "console read" = item 7's live read; say "serial" only for the port.
    (c) "stand-in simulator" (16) and "stand-in" (17, choice 5). Fix: "stand-in simulator" at each first use.
    (d) "envelope" (5, 8, 9). Fix: "`parts.py`'s envelope (agents.md)" at first use. (e) "sheet" and "page" both mean
    `breadboard.md`/`page.html` loosely. Fix: "sheet" = `breadboard.md`, "page" = `page.html`.
14. **Item 9's done-when is a grep of prose.** Fix: "a test runs each loop script with `--json` and parses one
    envelope".
15. **Item 7 needs a test off the bench.** "On the XIAO, Claude sees the press print" needs USB. Fix: add "a test
    with a fake port covers N seconds and no port"; the XIAO line stays the bench check. Size S holds.

Not checked: any Wokwi run, USB, Artifact shared state.
