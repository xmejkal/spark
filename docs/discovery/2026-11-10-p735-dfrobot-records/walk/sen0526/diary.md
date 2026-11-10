# Walk diary: DFRobot SEN0526 (P735 #1010)

Record: walk/sen0526/project/parts/sen0526-i2s-mic.json
(`P` = that project dir. Every parts.py run had `SPARK_HOME=$HOME/.local/share/spark` inline.)

## Steps
1. `parts.py --drawer` -> "Fermion: I2S MEMS Microphone (Breakout)  3  -" (no record linked). Entry file drawer/dfrobot-sen0526.json, part_number dfrobot SEN0526.
2. `parts.py --need i2s microphone --project P` -> "nothing in the library matches 'i2s microphone'".
3. `parts.py --kept SEN0526` / `--kept i2s microphone` -> "nothing kept matches SEN0526 - fetch it, or --keep a file you have".
4. Read parts/max98357a-dfr0954.json and vl6180x-breakout.json as models (I2S / breakout shape).
5. `parts.py --skeleton sen0526-i2s-mic --kind microphone --vendor dfrobot --project P` -> "wrote .../parts/sen0526-i2s-mic.json".
6. WebSearch "SEN0526 Fermion I2S MEMS Microphone wiki.dfrobot.com" -> https://wiki.dfrobot.com/sen0526/
7. WebFetch https://wiki.dfrobot.com/sen0526/ -> specs (3.3 V, 59 dB SNR, 11x16 mm), pin table, chip MSM261, links to dimension/schematic/datasheet PDFs, CAD zip, STP zip, GitHub DFRobot_MSM261.
8. Hand-edited `sources` with 6 URLs, `parts.py --fetch ... --dry-run` -> 5 URLs to fetch: the PDFs, the PNG and the webp. It skips the zips and the wiki page.
9. `parts.py --fetch sen0526-i2s-mic --project P` -> 5 kept, exit 0. Documents entries with title/version null.
10. `parts.py --read <store>/bd2a.../SEN0526_..._datasheet_v1.0.pdf --want supply_voltage current sensitivity snr input_high input_low` -> exit 1. Supply_voltage FOUND p3 on ABSOLUTE MAXIMUM row. Current LABEL ONLY. Snr FOUND p12 in REVISION HISTORY. Input_high/low NOT FOUND.
11. `pdftotext -layout` p1-5 and p6-12 of the datasheet -> spec table p3, logic table p4, pin table p7, I2S format p10.
12. Pdfinfo/pdftotext + pdftoppm of schematic (14 pages) and dimension (1 page) PDFs. Read sch p1, a 600 dpi crop of U1/R1, sch p2 (copper print), dim p1, the wiki pinout PNG.
13. Wrote facts/needs/power/pin_order/body/host_requirements by a python script. Removed `sourcing` and `//sourcing`.
14. `parts.py --validate --project P` -> "sen0526-i2s-mic ok", exit 0.
15. Filled documents title/version by hand. `parts.py --sources` -> 7 x "ok", exit 0 (it checked 7 URLs). Then dropped the GitHub URL from sources (never read it).
16. `parts.py --unverified sen0526-i2s-mic --project P` -> it lists 6 unchecked facts (regulator, standby current, CHIPEN, SD pull-down, SEL pull, pin_order).
17. `parts.py --show` (no CONFLICT), `--signals` (I2S_SCK, I2S_WS, I2S_SD on bus i2s), `--kept SEN0526` (now finds the 5 docs and their citers), `--need i2s microphone` (finds the record). Final `--validate` ok.

## Bugs
- `--read --want supply_voltage` reports FOUND on the ABSOLUTE MAXIMUM row (-0.3 to 4.0 V), not the Operation voltage row (1.6-3.6 V) on the same page: a reader trusting FOUND records the abs max as the supply range.
- `--read --want snr` gives FOUND for the wrong row. The row is on p12 REVISION HISTORY ("1.4 | Update the typical of SNR | 2018-08-22"). The spec row is on p3 ("Signal to noise ratio - 59 - dB"). It also read all 12 pages and did not stop on p3.
- `--read --want input_high input_low` NOT FOUND although p4 has "High Voltage Input ... VIH 0.7 x VDD" / "Low Voltage Input ... VIL": the label set misses VIH/VIL wording.
- `--skeleton` writes `"sourcing": []` with `"//sourcing": "Where it can be bought ... {seller, url, price_czk, checked}"`, which the research agent's rules forbid (no seller listings). The researcher must delete it.
- `--fetch` names the image document key `sen0526-main-01-360x240-jpg` for a `.jpg.webp` file (the key says jpg, the file is webp). And the pinout PNG gets the opaque key `38fcb541ed109957203c88c3caecec50`.

## Gaps in the flow
- No field to strap a module pad to a rail. SEL floats and must go to GND. I encoded it as `power: {pin: SEL, rail: ground, direction: in}` with a note. `--validate` accepts it silently. `--signals` does not show it. Needs a `straps` (or `tie`) field the board generator wires.
- `host_parts` pin must be a `needs` signal pad, so "pull-down on SEL" is not expressible without spending a GPIO.
- `host_requirements` prints every line as "the board must:". Three of my lines are for the firmware (I2S slot width, channel) or the enclosure (the port faces the hole). The record has no place for firmware or mechanical warnings.
- research.md never says how to add URLs for `--fetch`: I learned from datasheets.py that it reads `sources` and fact `source` strings. Step 2 ("--fetch <id>") only works once sources are filled by hand.
- `--fetch` keeps only .pdf/.jpg/.png/.webp/.svg (KEEPABLE). The vendor's CAD zip and STEP zip (the PO's holes/outline source) cannot be kept.
- `--fetch` prints a 12-char hash prefix (`aff604c1545f/...`), not the full store path `--read` needs. I had to `find` the store. `--kept` afterwards prints the full path, but only after a record cites it.
- `--fetch` leaves documents' title/version null. No command sets them, so I edited JSON by hand (research.md says --keep/--fetch answer the entry, nothing about version).
- Agent rules say a pinout read off a drawing is `verified: false`. Library record vl6180x-breakout marks schematic readings `verified: true`, and led-red-5mm marks a pin order read from a package drawing `true`. Two records, two rules. I followed the agent rule (false).
- No step tells the researcher to link the drawer entry (`is`) to the new record. `--drawer` still shows "-". I did not write the drawer (brief forbids).
- If body_mm is false, `--unverified` lists it. Nothing lists the datasheet's internal contradiction (VDD 1.8-3.3 V p7 vs 1.6-3.6 V p3) except my `note`.
- Datasheet currents are given at Vdd = 1.8 V only. The `draws` fact has no field for its test condition other than prose.
- Kind `microphone` is accepted with no check of what a microphone record must hold (research.md table has no microphone/audio row).

## No place in the record
- Product picture: https://dfimg.dfrobot.com/enshop/SEN0526/SEN0526_Main_01_360x240.jpg.webp (360x240 thumbnail only. Kept in documents, but no `image` field).
- Pinout render (top side, silkscreen): https://img.dfrobot.com.cn/wiki/60c1e008bddfc41c3293de80/38fcb541ed109957203c88c3caecec50.png (kept).
- Schematic: https://dfimg.dfrobot.com/wiki/19409/SEN0526_i2s-mems-microphone_schematics_v1.0.pdf, Rev V1.0 2022-08-08, 14 pages. P1: U1 MSM261S4030H0R. VDD to VCC with C1 10uF + C2 100nF. CHIPEN to VCC. Pin 2 NC. R1 100K from SD (DOUT) to GND. L/R to SEL with no pull. Header P1 1 DOUT 2 BCLK 3 SEL 4 WS 5 VCC 6 GND. Fiducials FD1 FD2. Mounting holes MH1 MH2. P2-14: PCB layer prints, PCB "SEN0526 [V0.0.3]", 1.0 mm, black mask, white silk.
- Board outline: 16 x 11 mm, corner radius R1, PCB 1.0 mm, 2.01 mm over all with mic can. Dimension PDF https://dfimg.dfrobot.com/wiki/19409/SEN0526_i2s-mems-microphone_dimension_v1.0.pdf (only width/height have fields).
- Mounting holes: 2, diameter 2 mm, 12 mm apart. Centres are 2 mm below the top edge (the edge opposite the pins). They are symmetric, so 2 mm from each side edge (computed from 16 and 12). Same PDF.
- Header holes: 6 in one row on the bottom (long) edge, drill diameter 0.9 mm, pitch 2.54 mm. The row centre is 1.35 mm from the bottom edge. The row is centred on the board's centre line, so the first pad centre is 1.65 mm from the left edge (computed: (16 - 5 x 2.54) / 2). Left to right, mic up: GND 3V3 WS SEL SCK DO. Pad ring diameter not dimensioned. Same PDF.
- Connectors: one, P1 "Header 6", 6 plated through-holes, 2.54 mm, pin 1 = DO (right end) .. 6 = GND (left end). No Gravity/JST connector. Schematic p1 + dimension PDF.
- Mic sound port: top-ported can on the component side, centred on the board's vertical centre line (dimension PDF. Datasheet p2 "Top-ported").
- CAD: https://dfimg.dfrobot.com/wiki/19409/SEN0526_i2s-mems-microphone_cad_v1.0.zip . STEP: https://dfimg.dfrobot.com/wiki/19409/SEN0526_i2s-mems-microphone_stpfile_v1.0.zip (listed on the wiki. Not downloaded: --fetch cannot keep zips).
- Vendor library: https://github.com/DFRobot/DFRobot_MSM261 (listed on the wiki. Not read).

## Not found
- Whether header pins ship with the board (soldered or loose): not in the wiki text (https://wiki.dfrobot.com/sen0526/) or the drawings.
- Pad (annular ring) outer diameter: not dimensioned in the dimension PDF.
- Current with SCK stopped / standby: not in the datasheet (pp 1-12) or the wiki.
- Current at 3.3 V: datasheet tabulates at Vdd = 1.8 V only (p3).
- Product page URL: the wiki's "Buy now" link is `javascript:;`. Not searched further (distributor pages do not count).
- Larger product photo: only the 360x240 webp seen on the wiki.

## Counts
- Searches: 1 of 8. Fetches (WebFetch): 1 of 12. Parts.py --fetch downloads: 5 documents. --sources HEAD checks: 7 URLs.
- Wall time: about 25 minutes (clock 09:30 to about 09:36 by `date` between commands, plus model time. Estimate).
