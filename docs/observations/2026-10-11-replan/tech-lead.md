# Tech-lead lens: the code and the dependencies

E = evidence (card, file:line, output). H = hypothesis. Spark cards by issue number.

## 1. Stages and done-tests
1. **Parts**: `parts.py --requirements .` exits 0 (scripts E journey.md; conversation unrun E #6).
2. **Build**: `check_spine.py requirements.json --keep . --sim-dir sim` exits 0 (E #6).
3. **Checks**: `check_all.py --project .` exits 0 on a fresh project; today 2: no rails stated, `compare_design.py:255` has no rule (E #6).
4. **Sheet**: `breadboard.md` exists; a person wires from it alone (never wired, E P191).
5. **Firmware**: `check_firmware.py` runs it on a stand-in `machine`; every pins.py signal driven or read (nothing ships, E #7, #8).
6. **Simulate**: a generated scenario passes `wokwi-cli` (a hand one did, E #64).
7. **Deploy**: `deploy.py --dry-run` prints the flash lines; the real board prints `ready` (missing, E #144).
8. **Bench**: a button press lights the LED on the PO's breadboard, one logged line (H).
9. **On request**: `tsci export -f gerbers|glb` exits 0 (E #16), held by a test.

## 2. First slice
- **J1 #7 (a)**: ship the stand-in `machine`. S, no deps. Proof: button-light firmware imports under CPython; LED 0 released, 1 pressed (a 15-line one did, E #7).
- **J2 #8**: `check_firmware.py`, sixth `check_all` entry. M, J1. Proof: irrigation exits 1 naming Valve4 and the mode button (E #7); button-light exits 0.
- **J3 #45 + #42 + one new card**: init seeds rails the board file knows (C79's seeding half, H). M, no deps. Proof: `check_all.py --project .` on the button-light fixture exits 0, last line counts unmeasured values.
- **J4 #64**: (a) smoke scenario written from pins.py (S–M, J1; proof: test reads text, no Wokwi minute); (b) one dated run (S, PO's yes plus `WOKWI_CLI_TOKEN`).
- **J5 #144**: (a) `esptool`, `mpremote` in tools.json (S; = P158's C76; proof: `tools.py --status`, test_tools); (b) `deploy.py` from the board's `chip` and `micropython_port` (boards/firebeetle2-esp32s3.json:7), `--dry-run` (S–M, a). Not the sim image: its 4 MB layout is fixed (`flash_image.py:30-31`). With #145 (S). (c) bench: the board prints `ready`.
- **J6 P100 round A, narrowed**: drawer to lit LED from the pages alone, each break filed. M. Conversation steps now; bench after J5.
- **J7 `tests/test_journey_basic.py`** (C11 minus the baseline): button-light fixture through stages 2–6, `tsci` and Wokwi skipped by name. S–M, J1–J4. Proof: dropping a stage's output turns it red naming the stage.
- **J8 #47, #72**: setup must not npm-install into a parent folder; init must not write bare `npx tsci`. S each, before J6.

**Finish first**: #94 leaves Build; #6 leaves Discovery (J6 replaces it); P186, P187, P189 leave Ready (mutation scoring; a C6 scenario, and only the FireBeetle builds, E journey.md); bin P58, P73, B8 wait.

**P158 layers**: none now. New scripts call today's `outcomes.envelope` (outcomes.py), so a later move to `cli` is mechanical (H). C76 and C79 sit below P158's cut behind C4 and gates Q13, Q4 (E plan): pull out as J5a, J3. C15 envelope 2, C33/C45 ledger, C35 `where`, C43, C7: wait.

## 3. Ask the PO
1. On your desk: breadboard, jumpers, button, LED, resistor, USB-C cable?
2. Wokwi minutes and token for J4b? A stranger has none, so is J1/J2's free harness the journey's pass?
3. Is your FireBeetle the N16R8? The generic S3 build leaves octal PSRAM off (H).

## 4. Prune from the active backlog (later, not closed)
- **Architecture epics**: #94, #96, #17, #123, #93, #99, #89, #70, #5, #102, #103, #97. The basic path runs on today's modules; #102's `body_mm` already only warns (E #102).
- **Store hardening**: #19-#23, #82, #101, #114, #118, #119, #83-#85. One person, one store.
- **Team tooling**: #27, #28, #30, #39, #108, #111, #113, #121, #135. Process, not product.
- **Checks for bigger projects**: #41, #43, #49-#51, #55, #56, #59, #60, #63, #69, #74-#76, #78, #79, #86, #87. They bite I2C, a second board or fab, not button-and-LED. Keep #45, #42, #52, #54, #73.
- **Stranger polish**: #46, #48, #53, #57, #61, #62, #81, #128. README changes after the journey works.
- **Umbrella epics**: #66, #67, #68; their children stand alone. #16 stays as the journey's epic.
- **Bin board, 23 cards**: later. B31 (#26) closes with P32b (#6), not before.
