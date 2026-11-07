# User's-journey lens: P663 pin conflicts

Paths: W4 = `~/Development/spark-walks/walk4/walk4-diary.md` (cited by line). P581 = `~/Development/spark-walks/p581-sound-joystick/` (`p581-rows.md`, `requirements.json`, `firmware/pins.py`, `parts/dfr0664-tft-2in.json`). Spark = `~/Development/spark-p663`. Account = a past-tense question for the PO; an answer would be E, account, n = 1.

## Findings

Format: JO-n · claim · tag · pointer · supports only.

- JO-1 · In P581 the GDI conflict surfaced to the PO only as Claude's reading of `assign_pins` output (unpinned run put I2S_BCLK on GPIO18 and JOY_SW on GPIO9, the GDI CS and SD_CS). Spark printed no conflict. Nothing in the files shows the PO himself saw it before Claude named it · E · `p581-rows.md` row 1 ("no check reads them") · supports: the conflict is silent at build today; does not show what the PO saw in the chat (not recorded)
- JO-2 · Spark holds the cable's pins in the screen record (`facts.gdi_on_firebeetle2_s3_gpio`, and a `host_requirements` line "these pins are taken, do not give them to another part") and does not read them. The facts are `verified: false`, read off a schematic image · E · `parts/dfr0664-tft-2in.json:245-258, :268`; W4:79 · supports: option B would place from an unverified table; the PO has bench-confirmed only the backlight (GPIO21, `verified: true`, W4:86)
- JO-3 · The pin map in the P581 project still lies today: `pins.TFT_DC = 11` (comment "needs nothing special"), while the cable holds DC on GPIO3. `firmware/pins.py` carries no word of the cable. A person wiring from the sheet would put DC on A5 and the screen would stay blank, with no short and no damage · E · `firmware/pins.py` line TFT_DC; `p581-rows.md` row 3 · supports: the harm is a wrong wire or a dark screen, not a burnt part; it did not reach the bench because he used the cable
- JO-4 · The harm was avoided by Claude going around spark: the firmware's `gdi.py` types the cable's numbers (DC 3, RST 38, CS 18, SD_CS 9, BL 21) while spark's `pins.py` says otherwise. This breaks the rule "firmware never types a GPIO number" · E · W4:27 (20:00 CET row), W4:160 (G27), `p581-rows.md` row 1 ("the games' `gdi.py` holds 18, 9, 3, 38, 21") · supports: two sources of truth for the same pins exist in the working project
- JO-5 · The PO's own pin work is hidden behind Claude: the workaround is top-level `signals: [{"name":"TFT_RST","pin":"D3"}...]` by board pad label (D3, D6, D7, D13), not by GPIO. Claude translated GPIO to pad labels. Nothing shows the PO knows these labels · E · `requirements.json`; `p581-rows.md` row 2 · supports: the PO directs, Claude edits; any question to him should name the connector and the part, not a pad label
- JO-6 · K3 (backlight GPIO21 = onboard LED) was first seen on the bench, by the PO's eyes: "the display's backlight is kind of glowing like the LED, following the same rhythm". No record said so before the research agent's table; `--match` and the pick could not warn · E · W4:86 (19:52 row, his words), W4:155 (G22) · supports: the bench is where K3 first showed; earliest possible: research (W4:25-26) once the connector table existed
- JO-7 · After the PO dropped the LED, `pins.py` still names `ONBOARD_LED = 21` and now beside `TFT_BL = 21`. Spark names the second job on the same pin only when its assigner chose the pin; a pin named by the person goes unnamed · E · `firmware/pins.py` (TFT_BL carries the onboard_led text, ONBOARD_LED = 21 stays); W4:164 (G31); `p581-rows.md` row 4 · supports: K3 is half-visible in a comment and is not a stop
- JO-8 · Walk 4's build with the screen did not fail on a pin conflict. It failed on trace names (`MOSI`/`MISO` vs `MO`/`MI`), with `source_trace_not_connected_error` and no trace named. The PO's first sight of "the GDI screen" in the build was a broken chain. The conflict (5 of 8 signals disagree with the cable) was masked behind that defect · E · W4:87 (19:57 row), W4:162-163 (G29, G30), W4:160 (G27) · supports: in walk 4 the conflict could not be seen until another fault was out of the way. Whether G29 is fixed is — (README says SPI parts built on 2026-11-01 after P512; not re-run by me)
- JO-9 · In P581 the build did not finish: `check_spine.py` stopped at 300 s ("the chain was NOT exercised — this is not a pass"). No breadboard sheet, drawn breadboard, picture or page. So the wire list that would carry the conflict to the bench was never produced in P581 · E · `p581-rows.md` rows 5-6; `ls dist/board` holds only `circuit.json` · supports: the sheet-step visibility of any conflict is unproven in this project; the later P659 fix (#890) is in Review, not read by me
- JO-10 · A stale kept file hides a changed pin map: `board.tsx` (00:24) is older than `pins.py` (00:38) and `requirements.json` (00:32). Spark says "left alone" and not that it no longer matches · E · `p581-rows.md` row 7; file times read by `stat` · supports: after the person resolves a conflict and the pin map changes, `--keep` can build the old board. A resolved conflict needs a regenerated sheet
- JO-11 · Each walk's decision was taken by the PO through Claude's question, in his words, and each was about use, not pins: walk 4 "we will use the display with the GDI ... screw the LED" (W4:86); P581 "how would we like spark to behave ... Can we offer some solutions?" (#892); he chose B with C as net. He decided between whole options; he was not asked for a pin number · E · W4:86; `p581-rows.md` row 13; issue #892 · supports: he can answer "cable or wires?" and "drop the LED?"; whether he can answer pin-level questions is —
- JO-12 · In walk 4 the PO's own first words already named the connector ("i've used the gdi cable ... the firebeetle 2 and the displays have it and there also similar interface for camera I think") — he volunteered what spark did not ask. Spark then had no field for it (G20, G23, G24) · E · W4:24 (19:46 row), W4:153, :156-157 · supports: the connector fact is available from the person at idea/research, before build
- JO-13 · Spark's `--match` and the screen need's condition `plugs into the board's GDI connector` changed nothing in ranking and the answer did not say it did not read the condition. Which owned display has a GDI connector was unknown until the PO named it (stall S8) · E · W4:152 (G19), W4:98 (S8) · supports: the idea step is the earliest place the connector can be asked; it is blind to it today
- JO-14 · For a project that already works (K6), init sees none of it: "no board chosen", rails empty, goal null, in the games repo with a FireBeetle 2 and a GDI screen. The PO starts from zero. No `pins.py` or `requirements.json` of the working gadget is read · E · `p581-rows.md` row 11 · supports: K6 is invisible at the first step. That the working gadget's wiring lives in `gdi.py` and old `pins.py`, not in spark's records, is E W4:27 and the P581 folder `firmware/` (many hand files: arcade.py, gdi.py, lcd.py, st7789.py)
- JO-15 · Adding a part to a held board is blocked by ownership, not pins: the FireBeetle 2 shows `free 1, held by smartbin-local, walk3` and a trial folder lands on the projects list. Nothing yet says that a board two projects hold also holds two pin maps · E · W4:23; `p581-rows.md` row 12 · supports: K6 has a second face: pins "used" by another project's gadget on the same board. The records do not link a board instance to a pin map. Whether that matters to the PO is —
- JO-16 · The K1 assignments from an unpinned run are plausible-looking and carry a reason text per pin. The reason strings do not mention the cable or the connector. A person reading `pins.py` sees "needs nothing special" next to TFT_DC and cannot tell it is wrong · E · `firmware/pins.py` lines TFT_DC, JOY_SW · supports: the reason text is a place to show a conflict; today it is where a lie sits
- JO-17 · Two pins in the P581 final map sit on other connector pins that are unused today: JOY_SW = 7 is GDI FCS and camera Y6; JOY_X = 4 is camera Y5; AUDIO_SHUTDOWN = 6 is camera VSYNC; I2S_BCLK/LRC/DIN on 12/13/14 are GDI TCS/INT/BUSY. None conflicts with the DFR0664 (it uses GDI pins 18 to 9). A second GDI screen with touch or font chip would · E · `firmware/pins.py`; W4:81, :83; `parts/dfr0664-tft-2in.json` ("those eight are used only by DFRobot's other GDI screens (font chip, touch)") · supports: "unused connector pins" are a real quiet class; the camera pins are unverified (W4:79)
- JO-18 · The research agent contradicted itself on K4 (its tables put GDI FCS and camera Y6 both on IO7, its summary named only IO1 and IO2). Claude took the tables. So IO1, IO2 and IO7 are all shared · E · W4:85, W4:197 (O5) · supports: K4 is read off an image and was never checked by the PO; `verified: false`

### Journey 1: walk 4, the GDI screen added to a FireBeetle 2 ESP32-S3 (2026-11-01)

| step | what he does | evidence | friction or harm | today: works / partly / not yet |
| --- | --- | --- | --- | --- |
| 1 Goal | Asks for a button and LED effect on the board, then adds "a GDI display" as the next goal (19:16-19:33) | E W4:10, :17 | None for pins; the board has 2 onboard parts on GPIO21 and 47 that he does not name | works |
| 2 Idea: needs | "yes" to a screen need with the condition "plugs into the board's GDI connector" (19:42) | E W4:23 | The condition is free text; `--match` ranks the same with or without it (G19). Spark cannot tell which owned display has GDI; he is the one who names it (S8) | not yet |
| 3 Idea: pick | Names "the 2 inch ips" and "i've used the gdi cable" (19:46) | E W4:24 | He supplies the connector fact unasked. Spark has no word for "plugs into a fixed connector" (G23) | not yet |
| 4 Research | Says yes to a web search; an agent reads the schematic image for the GDI (P2) and camera (P1) pins | E W4:25-26, :79-85 | The pins are `verified: false`, read off an image; the agent's summary and tables disagree (O5). Library board record is not changed (G24) | partly |
| 5 Bench observation | Sees the backlight follow the LED (19:52) and drops the LED | E W4:86 | K3 appears first by eye, on hardware. Harm: a firmware driving the LED drives the backlight too (G22) | not yet |
| 6 Idea: remove a part | Wants to remove the light need; no flag does it; Claude edits `.spark/needs.json` by hand | E W4:86, :97 (G26) | `pins.py` keeps `ONBOARD_LED` after the need leaves (G31) | not yet |
| 7 Pin map | `--requirements` then `assign_pins.py` places SPI on GPIO17/15/16 (same as GDI) and TFT_BL 38, CS 11, DC 12, RST 13, SD_CS 14 (the cable: 21, 18, 3, 38, 9) | E W4:86 (19:52 row), G27 | 5 of 8 signals disagree with the cable; no warning. DC on GPIO3 is not in the free list | partly |
| 8 Build | `check_spine.py --keep .` exits 1: `source_trace_not_connected_error`, no trace named | E W4:87, G29, G30 | Masks the pin conflict. He waits (S11) and says "we definitely should fix this" | not yet (SPI part build; README says P512 fixed it on 2026-11-01 — not re-run by me) |
| 9 Sheet | No breadboard sheet was produced | E W4:87 ("no breadboard sheet") | The step where a wrong wire would be told never ran | not yet |
| 10 Firmware / deploy | Claude writes `gdi.py` with the cable's numbers by hand; the PO flashes with his own yes and reports "It works" | E W4:27, :43 (S13 stall text) | `gdi.py` and `pins.py` disagree; nothing checks it | works (by going around spark) |

### Journey 2: walk P581, an MAX98357A amplifier and a joystick added to the same board with the screen on the cable (2026-11-07)

| step | what he does | evidence | friction or harm | today: works / partly / not yet |
| --- | --- | --- | --- | --- |
| 1 Init in the working repo | Runs init in the games repo (FireBeetle 2, GDI screen, README says so) | E `p581-rows.md` row 11 | Spark sees no board, no rails, no goal; he starts from zero (K6) | not yet |
| 2 Idea: needs and matches | Asks for sound and a joystick; `--need sound` finds nothing; the record's words are "I2S", "MAX98357A" | E row 8 | Not a pin issue, but he cannot reach the amplifier by the word he uses | partly |
| 3 Pick and requirements | `requirements.json` lists the screen, amplifier, joystick, speaker terminal | E `requirements.json` | The screen is listed as a part with no word that it sits on the cable | works |
| 4 Pin map, unpinned | `assign_pins.py` puts I2S_BCLK on GPIO18 and JOY_SW on GPIO9 (cable CS and SD_CS) | E row 1 | Silent K1. Harm if built: two wires on one pin, a screen that fails or a joystick that always reads | not yet |
| 5 Pin map, pinned | Claude pins four signals by pad label (D3, D6, D7, D13) | E row 2, `requirements.json` | Needs the PO's knowledge of the cable via Claude; four of five took | partly |
| 6 DC on GPIO3 | DC pinned to D2 is refused: strapping, "see P527" (C4) | E row 3 | Dead end: the refusal tells Claude, not the PO, and offers no way through. Without `pin`, DC lands on GPIO11 and `pins.TFT_DC` says 11 while the cable holds 3 | not yet |
| 7 Backlight on LED | TFT_BL = 21 is right, ONBOARD_LED = 21 is the same pin and unnamed | E row 4, `pins.py` | K3 unnamed; any firmware that blinks the LED lights the backlight | not yet |
| 8 Build | `check_spine.py --keep .` stops at 300 s, exit 2, no sheet, drawing, picture or page | E rows 5-6 | `pins.py` and `dist` were still written; the build "is no hang", 8 min 16 s alone. The PO cannot reproduce by hand (no node_modules) | not yet |
| 9 Pin change after fix | Pin map changes; `--keep` leaves an old `board.tsx` | E row 7, `stat` times | A second run builds the old board | not yet |
| 10 Question to the PO | Asks how spark should behave; options A place, B ask, C warn, D keep wired; he chooses B with C as net | E row 13, #892 | The decision is taken in a chat question, not recorded in the project; where the answer lives — (J3 in jobs-and-journeys) | partly (card P663 filed) |
| 11 Sheet and bench | Not reached in P581 (build did not finish) | E rows 5-6 | Unknown whether the sheet would say "plug the ribbon cable" | not yet |

### Scenario (a), H: a working gadget that is wired, one part added (K6)

Source: H, derived from K6 and from P581 row 11, J4 and #892 option D; no PO session has done it through spark. The P581 session is the nearest real run, because the games repo already worked and held `gdi.py`.

| step | what he does | evidence | friction or harm | today |
| --- | --- | --- | --- | --- |
| 1 | Says "add a buzzer" in the repo of a working gadget | H, P581 row 11 | Spark sees no board, no rails (init); nothing says which pins the wires already use | not yet |
| 2 | Spark picks pins from the free list; the free list has no wires in it | H, `assign_pins` reads the board record and `requirements.json` only (W4:160, G27) | New part may take the pin of an existing wire with no spark record: a short or an inverted signal. A tolerable result is a part that does not work; a harmful one is two outputs on one pin | not yet |
| 3 | He could supply: the old `requirements.json` if one exists; a photo of the board; or "what is wired" in words | H; photo path exists (`/spark:identify`) | Spark did not ask. What Claude could read: the firmware files (`gdi.py`, `pins.py`) as evidence of pins in use — E that such files exist in the P581 folder | — |
| 4 | Sheet lists wires for the new part and, if a pin map exists, for the old ones | H | A sheet that re-lists all wires tells him to rewire a working gadget | not yet |

Candidate account questions here: see Q1, Q2, Q3 below.

### Scenario (b), H: two connectors share pins (K4: GDI and camera on IO1 and IO2)

Source: H, derived from K4 (E W4:81-85, unverified). No PO session has put a camera on this board.

| step | what he does | evidence | friction or harm | today |
| --- | --- | --- | --- | --- |
| 1 | Has a GDI screen on the cable and asks for a camera | H | Spark's board record names neither connector (G24) | not yet |
| 2 | Pick of an I2C/DVP camera module; the shared pins are IO1, IO2 (I2C on the GDI side: SDA/SCL), IO7 (FCS vs Y6) | E W4:81-85 as a table; E W4:197 says the agent's own summary was wrong | The sharing is one level up from a pin: an I2C bus can be shared, an FCS/Y6 pair cannot. Spark's `SHARED_LINES` code handles shared bus lines (E `assign_pins.py:272-282`) | not yet |
| 3 | Plugs both ribbons | H | If both connectors drive IO1/IO2 as outputs: contention. If only the screen's DFR0664 (pins 18 to 9) is plugged, the shared pins are not used by it and there is no conflict | not yet |
| 4 | He could say which connector he really needs; the answer may be "just the screen" | H | The conflict depends on which cable pins the part uses (JO-17). A check by connector and not by part would raise a false alarm for the DFR0664 + camera pair. Unknown; — | not yet |

### Where each conflict first becomes visible

Journey steps are the README's eight (drawer, idea, research, build, checks, firmware, simulate, bench) mapped to the PO's five (idea, research, build, sheet, deploy). Evidence = E pointers in the tables above.

| kind | first visible today | earliest it could be | pointer |
| --- | --- | --- | --- |
| K1 connector pin vs another part | build, by Claude reading `assign_pins` output; not flagged | idea (pick), once the board record holds the connector and the part record names its host pins (both exist as text; no code reads them) | JO-1, JO-2 |
| K2 connector pin on a strap | build, as a refusal of a named pin (C4); otherwise not at all (DC lands on a free pin) | idea (pick) | JO-3; `assign_pins.py:65-70` |
| K3 connector pin on an onboard part | bench, by the PO's eyes (walk 4); for P581 in a comment on `pins.py` | research (the record already lists the GDI table and the board's LED), or idea | JO-6, JO-7 |
| K4 two connectors share pins | research, in a table read off an image (walk 4), then not again | research, when the second connector is recorded; real only if a part uses both | JO-18; E W4:85 |
| K5 two signals on one pin | build (`assign_pins.py:283`, stops with no choices) | build; earlier only if the person names a pin at idea | E `assign_pins.py:283` |
| K6 pins a working project wires | not visible (init row 11) | init, from the code in the repo | JO-14 |
| K7 a pin spent that a later need wanted | not visible; noted by Claude in rows (row 10) | idea, when a goal says WiFi | `p581-rows.md` row 10 |

## What you could not check

- Whether the PO saw spark's output or only Claude's relays in either walk. The diaries record Claude's reading and his short replies; the chat text is not in the files. So "where he stalled" is E for stalls that the diary names (S8, S10, S11, S12) and — for what he thought.
- Whether he would have wired by the sheet. In both walks he used the cable and no sheet was produced (W4:87; P581 row 5), so no wrong-wire harm happened on the bench.
- The truth of the GDI and camera pin tables: read off a schematic image by an agent, `verified: false`. Only the backlight is bench-confirmed (W4:86).
- Whether G29 (SPI trace names) is fixed. The README says an SPI part built on 2026-11-01 after P512; I did not run a build.
- The effect of #890 (P659, build timeout) and #888, both in Review.
- P581's other files (`arcade*.py`, `render.py`, `space3d.py`, the `sim/runs/` logs) and the middle of walk 4 (steps 30 to 54, games and C driver). I read them only by search for pin terms. Time limit.
- The `docs/guide/journey/*.md` pages were found, not read in full; I used the README table and `commands/build.md` and `commands/idea.md` by search. Whether the idea page tells Claude to ask for a connector is therefore only checked by grep (no hit for "connector" beyond a match line).
- Scenarios (a) and (b) are H. No session has run them.

## Questions for the decider

Account questions (past tense, his own use; the answer is E, account, n = 1):

- Q-A1 · In walk 4, when the backlight followed the LED, what did you think was wrong first, and what did you do before Claude explained it? · account · decides: whether K3 needs a warning at pick time or only a name on the sheet
- Q-A2 · When you used the GDI cable, did you plug it from the sheet, from the display's wiki, or from Claude's words? Did you look at `pins.py` or the sheet at all? · account · decides: whether he reads the pin map and the sheet, which sets where a conflict must show
- Q-A3 · In the games repo before P581, how did you know which pins were already used? Did you write them down anywhere other than `gdi.py` and the README? · account · decides: where K6 could read the used pins from
- Q-A4 · When Claude pinned TFT_RST to D3 and TFT_CS to D6, did you see those pad names, and did they mean anything to you? · account · decides: whether a conflict question may name a pad label or must name a connector and a part
- Q-A5 · When spark said DC on GPIO3 was refused as a strapping pin, did you know GPIO3 was a strap before? What did you do then? · account · decides: whether the strap is news to him or noise
- Q-A6 · Have you ever added a part to a gadget that worked and then had a thing stop working? What was it? · account · decides: whether K6 is a lived harm or only predicted
- Q-A7 · When you chose B with C as net in #892, what did you picture the question looking like, and where did you picture the answer being kept? · account · decides: where the answer lives (requirements file, project record, board record)

Decision questions:

- Q-D1 · For a part that can use a connector or wires, is "cable or wires?" always asked, or only when the board has the connector and the part record names it? · decides: the ask rule at pick time
- Q-D2 · If the pin table in a record is `verified: false` (an image reading), may spark fix pins on it and say so, or must the PO confirm first at the bench? · decides: whether option B trusts unverified facts; the screen's own table is unverified (JO-2)
- Q-D3 · If a conflict is unresolved, may the build still write `pins.py` (as it did in P581, JO-9) or must it remove it? · decides: whether the pin map can lie after a stop
- Q-D4 · When a kept `board.tsx` no longer matches the pin map, does spark stop, warn or regenerate? · decides: JO-10's rule
- Q-D5 · For the "unused pins of a connector" class (JO-17), is a conflict declared only when a part uses a pin, or when any plugged cable could? · decides: false-alarm rate for K4 and the DFR0664 + camera pair
- Q-D6 · Is K6 (working project) in the first slice, or only the question "what is already wired?" asked once? · decides: how much of scenario (a) is built first

## Searches

None.
