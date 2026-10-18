# Refuter: the four lenses, checked

Opus, 2026-10-18. Scratch store and scratch projects under the session scratchpad, `SPARK_HOME` inline, no USB, no Wokwi token.

> **TL;DR.** Most load-bearing claims hold. Two do not: adding TX/RX to the XIAO record does **not** remove the
> "no serial monitor" warning (architecture slice 1 cannot pass as written), and evidence says that warning did not stop
> a XIAO scenario before (PO risk 4 is smaller than stated). The MVP project is button + LED, and a part is added, not swapped.

## Verdicts

1. **CONFIRMED, PO 1 and 3.** `parts.py --need buzzer` and `--need beep`: "nothing in the library matches". Shipped record:
   `check_spine.py --keep` exits 2, "the board states no power.io_volts". The fresh fixture exits 0 and writes
   breadboard.md/.json/.svg, page.html and sim/. Adding `{"part":"led-red-5mm","name":"LedTwo"}`: exit 0, 10 traces, 8 wires.
2. **CONFIRMED, architecture 1 (five facts).** Copying `power`, `power_pads`, `wokwi_power_pins`, `documents`, `physical`
   into the shipped record: exit 0 through simulation. Each one is needed: without `physical`, the footprint step cannot run
   (exit 2). Without `documents` or `wokwi_power_pins`, the board contract fails (exit 2). Without `power_pads`, exit 1.
   Note: the two records also disagree on `deep_sleep.single_polarity_for_all_pins` (shipped true, fixture false),
   `adc_gpio` and `flash_mb`. Copy the five. Fix the disagreements in their own card, not quietly in slice 1.
3. **REJECTED, architecture slice 1 done-when "no serial warning" (adding TX/RX).** With TX/RX added too, the warning
   stays. The fixture, which has TX/RX, warns as well. The cause is the converter: `serialMonitor()` asks Wokwi's pin
   registry whether `board-xiao-esp32-c6` has pins named TX and RX (`tools/circuit-to-wokwi/dist/converter.mjs:6797`). It
   never reads spark's record. Fix: drop the clause from the done-when.
4. **PARTLY REJECTED, PO 4 (the warning may stop the MVP).** The check is real (`check_spine.py:567-569`, `serial_wired`
   at :247). But a XIAO scenario passed on 2026-10-14 (`docs/observations/2026-10-14-p215-bench.md:9`), and deploy then
   printed `ready seen` (README, Bench). Deploy needs a passed log, so `wait-serial` heard the board, probably over the
   C6's USB serial. I could not rerun it (no token). Keep "a `ready` scenario passes once" in slice 1. Card the warning
   wording as a likely false alarm on the C6.
5. **CONFIRMED, architecture 2-6 and AI-UX 2-6.** `_merge_parts` returns `list(existing) + added` with `kept` (`needs.py:486-517`).
   `DeployService` is in `deploy_service.py:62` with no `print(`. `why_untested` is at `project_image.py:57`. The log header
   (`run_scenario.py:194`) names no simulator. The roles hold `"simulator": "wokwi-cli"` and `"bench": "sigrok"`.
   `"--json"` appears 0 times in deploy, look, run_scenario, breadboard, init_project and tools. `READ_S = 2`
   (`board_console.py:20`), and only the cure, download-mode and doctor paths call `console()`. `next` is "empty today"
   (`agents.md:380`). Nuance: the token variable is the tool entry's `account_env`, which defaults to `WOKWI_CLI_TOKEN`
   (`run_scenario.py:248`). It is not hard-coded.
6. **CONFIRMED, UX 1, 4, 5 and 8, with a limit on 5.** page.html has 3 `<img>` and no steps. A rebuild renumbers the steps
   (adding LedTwo moves old step 4 to 5, and so on). False `move not kept: jumper 8b.j-17b.g` and `12t.a-17b.h` appear
   after adding **BtnTwo** to a layout spark drew itself. They do **not** appear after adding LedTwo. `build.md:354`
   ("Nothing has run this on a board yet ... FireBeetle") is stale against README's XIAO `ready seen` of 2026-10-15.
7. **REJECTED, architecture risk "a test that pins XiaoRealFootprint may break".** No file in `tests/` or `scripts/` names
   `XiaoRealFootprint` or `XIAO-ESP32-C6-SMD`.
8. **CONFIRMED, a hidden dependency in architecture slice 4 and UX slice 6.** "A buzzer on D9" needs a buzzer record
   that does not exist (verdict 1). That is research, which has never run (#178), so it is M or L, not S.

## Contradictions between the lenses, and my verdict

- **Bench walk before or after `/spark:deploy`.** The PO lens puts deploy first, the architecture lens puts the walk first,
  and AI-UX has no walk. Verdict: XIAO record, then P290, then walk 1 with plain `deploy.py`. P213a/b run beside it and
  take the walk's diary as input. Reason: `deploy.py` already reached `ready seen` on this board. The PO lens's own risk
  says "do not hold the walk for the command", and the PO's top ask is the walk.
- **Swap or remove in the MVP.** The architecture lens has it at 3, the PO lens after the line. Verdict: after the line.
  An add rebuilds (verdict 1). It is the PO's "edit the schema, and everything rebuilds", and a drop needs a 2nd part to swap in.
- **LED or buzzer as the MVP project.** AI-UX, architecture and UX use a buzzer, the PO lens uses LED. Verdict: LED. No
  buzzer record exists, and getting one is the untested research route. A buzzer is walk 2.
- **Hole numbers before the walk (UX 1, M) or not (PO).** Verdict: one S slice before the walk. Steps say "in a free row"
  (seen in breadboard.md), and the PO wires from that sheet. Labels and the part overlap fix can wait for the walk's diary.
- **AI-UX's `loop_status.py`.** No other lens has it. Verdict: after the line. It reads records that the `--json` work changes.

## Not checked

Any Wokwi run (no token), so verdict 4 rests on the 2026-10-14 log. UX 3 (the picture overlaps): I did not render the SVG.
The P290 retry behaviour (it needs USB). Artifact shared state (unknown, as p294.md says).
