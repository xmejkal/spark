<!-- The delegated council, round 2, the tech lead seat (Fable), 2026-11-26. Read-only. The session saved its returned text here unchanged. Delegated, the PO's to change. -->
# P1190, round 2: the delegated tech lead

**Short version.** A1 stays the riskiest, and its split line holds with one addition. Two of my ratings drop: A3 and A9. Run item 19's first step before the seam's plan fixes its contract. Order is opinion, the PO's to decide.

## Ratings

| id | now | round 1 | reason |
| --- | --- | --- | --- |
| A1 | high | high | D13 gave no account. Still no evidence. |
| A2 | low | low | Item 19 replaces item 14. The stand-in still has no `deepsleep`. |
| A3 | low | high | Changed. The clock uses GPIO14, so the result is near known. D11 and D12 accept grey either way. |
| A4 | low | low | A plan question. A second strategy makes it matter later. |
| A5 | low | low | No own part model exists yet. |
| A6 | low | low | D13's policy holds whatever the count says. |
| A7 | low | low | D14 said yes. The spike sits in slice 3. |
| A8 | high | high | D11 ships the grey state. Its words are the outcome's proof. |
| A9 | low | high | Changed. D15 names a second Adapter, and item 18 depends on item 6. |

## New assumptions

**N1, feasibility (D15).** esp-emulator or esp32sim boots spark's MicroPython C6 image. Test: item 19's step 1, free, in a temporary folder. Start with the button-light image, because the clock imports `network` and `ntptime`. Pass line, dated 2026-11-26: one walk project's unchanged `sim/flash-with-firmware.bin` prints its `ready` line within 60 s on one emulator, and one press changes an LED level read back.

**N2, value (D13).** A person marks a version important, and a paid run follows. Test: a use log over 3 walks on a board Wokwi covers, with one offer at the deploy. Pass line, dated 2026-11-26: at least 1 mark, followed by a paid run. Below it, only `ask`, `never` and the threshold ship.

## Riskiest

A1. The split line holds. Addition: log a fault found by the project's own tests apart from one the import check finds. D12 makes the free checks part of v0.10's line, so "who started them" matters more.

## Order (opinion)

1. Item 19's step 1 before item 6's plan. The contract is `wokwi-project`, and no emulator speaks it.
2. Item 2 before P999. P999 no longer gives the clock a `sim/`, which was my round 1 reason.
3. Item 16 after P413 and P1194. Pause item 18's build until item 19 reports.

## Checks

- The clock, walk project p934-display2: `firmware/pins.py:6` (`EPD_CS = 14`), `firmware/main.py:22-23`, `:189`. Its build record reads `could-not-run`, `board_not_in_wokwi`.
- Contract: `data/tools.json:21`, `scripts/spark/records/tool_finder.py:300-302`.
- Guard: `scripts/spark/build/build_service.py:450-456`.
- No minutes count: `scripts/spark/firmware/scenario_run.py` records none. P413 #539 is open.
- The mark has a home: `scripts/spark/bench/image_evidence.py:430-436` matches by sha256.
- C6 image: `data/tools.json:185-188`. `ticks_ms` is 0: `scripts/spark/firmware/import_child.py:37`.
- `gh api`: esp-emulator v1.2.0 (2026-11-20) ships an `aarch64-apple-darwin` binary, and this Mac is arm64. esp32sim is MIT, Rust.
- P999 #1455 and P1078 #1582 are open, in Idea.

## Not checked

- Nothing was installed or run. N1 is untested.
- Whether Wokwi's C6 DevKitC-1 lacks GPIO14.
- Whether esp-emulator models Wi-Fi, and whether its source is open.
- Whether a past walk's import check found a fault.
- `research-wokwi-settings.md` and a change to `items.md` appeared during my run. I read neither.
- The store's preanalysis/2026-11-26-own-simulator.md is the only source for both emulators' features.

## Searches

none. Two `gh api` reads of public repository data.
