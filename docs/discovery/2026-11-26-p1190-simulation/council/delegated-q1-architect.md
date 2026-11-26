<!-- The delegated council, round 2, the architect seat (Fable), 2026-11-26. Read-only. The session saved its returned text here, its claim list shortened. Delegated, the PO's to change. -->
# P1190 the delegated council, round 2: the architect seat

Read on branch `p1190-simulation` at 4dddd8ef, 2026-11-26. Nothing written. No paid run.

## Short version

A1 stays the riskiest, and the split line holds with one added sentence. Two ratings change: A3 goes low, A4 goes high. A9 stays high, but its question changed. Run the free boot test (A10) before the seam's plan, because it is the cheapest result that can change the seam's shape.

## 1. The ratings

| id | now | round 1 | one line of reason |
|---|---|---|---|
| A1 | high | high | D13 gave no account. D12 puts "the free checks passed" into v0.10's line, so more rests on them. |
| A2 | low | low | Item 19 replaces its test. It goes high only if A10 misses, because way 3 is then the one free way left. |
| A3 | low | high | Changed. D11 and D12 approve the grey ending, and the fixture board proves the branch. `EPD_CS = 14` is already read. Neither result changes a decision. P999 still runs first. |
| A4 | high | low | Changed. D14 and D15 make "every strategy" real: another author's chip, an emulator's part kit, spark's own models. The record's key is `simulation.wokwi` today. |
| A5 | low | low | No slice gives a pass from a model before slice 3. |
| A6 | low | low | D13's threshold handles either result. Its count is the open part (A11). |
| A7 | low | low | D14 answered the dependency. The free half of item 12 stays cheap, and no project needs it before P1000. |
| A8 | high | high | More states now read grey: skipped, role off, a policy that holds the run. |
| A9 | high | high | D15 makes item 6 a dependency of item 18, so "is it worth a card" is nearly answered. The risk is now the seam's shape, drawn from one Adapter. |

On A9: a role has one contract, `wokwi-project`, and the finder refuses a tool that does not meet it. The scenario's step kinds are wokwi-cli's own words, and the run hands wokwi-cli the scenario file. So item 6 as written gives "selectable, not exchangeable". Its card should say that. Item 10's plan and the `Simulator` base's run method should wait for item 19's steps 2 and 3. Item 19 is free and can run beside P999 and P1078, so D3's order does not move.

## 2. Two new assumptions

A10 (D15, feasibility). A free local emulator boots spark's own MicroPython C6 image with no edit, and a host can drive it. Test: item 19's steps 1 and 2, free. Pass line, dated 2026-11-26 before any result: on esp-emulator v1.2.0 or on esp32sim, the image spark built for the XIAO C6 button-light project prints `ready` on serial within 120 s of wall clock, and one press sent by the host changes one pin that the host reads back. A miss: ways 1 and 2 leave the epic's first slice, way 3 is sized alone, and A2 goes high. Note: the XIAO runs Seeed's port, not `ESP32_GENERIC_C6`, so the spike boots spark's merged image and not the bare download.

A11 (D13, feasibility). Spark can count the paid minutes a run used, well enough for a threshold. Evidence against: a kept run log names the cap ("timeout 60000 ms") and no time used. Test: free, read wokwi-cli's printed output and its documentation for a simulated-time line (the first step of P413). Pass line, dated 2026-11-26: one source names the simulated time of one run. A miss: the count is the sum of the caps, an upper bound, and the threshold's words say "at most".

## 3. The riskiest

A1, as before. It gates the most build work (the screens of slices 2 and 3), it has the least evidence, and its test is the slowest. A10 is second, and it is contained: D15's spike is its test. The split line holds. One added sentence: a fault found by a free emulator run, if item 19 leads to one, is logged apart and does not count as `check-firmware`'s yield.

## Open choices, each with my recommendation

- The unit of "a version" in item 16: the image's sha256, as the run log and the deploy already use. A mark then ends at the next firmware edit. A mark that outlives edits is the project setting `paid_runs`, not a mark.
- A second simulator and the role's one contract: each Adapter names the contract it speaks, and the table maps contract to Adapter. An H for item 6's plan.

## Claims checked (short)

`data/tools.json:5`, `:21`, `:185-188`. `scripts/spark/records/tool_finder.py:300-302`. `scripts/spark/firmware/scenario_steps.py:15-19`. `scripts/spark/firmware/scenario_run.py:213-216`, `:243-247`. `boards/xiao-esp32-c6.json:8`. `gh api` of both emulator repositories. No `Simulator` class under `scripts/spark` (grep).

## What I could not check

Nothing was installed or run. Neither emulator's host interface or part format. Whether wokwi-cli prints the simulated time. Which MicroPython port the clock's FireBeetle 2 C6 runs. P1194's and P413's code. The other two seats' round 2 answers.

## Searches

none. Three `gh api` reads of two public repositories.
