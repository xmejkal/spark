# Verification of answer.md (adversarial, read-only)

spark at 8f7733d, bin at 8847eb8 (both confirmed). Numbers recomputed with my own scripts (/tmp/v.py, /tmp/v2.py) from datasheet figures in src/ (ESP32-S3 v2.2, VL6180X Rev 7, Pololu schematic image, BSS84).

| # | Claim | Verdict | What the source says |
|---|---|---|---|
| 1 | A need is one of 13 verbs plus words; "No part numbers" (idea.md:15-20, parts.py:59-61, needs.py:1-27) | holds | 13 VERBS; "No part numbers" at idea.md:20 |
| 2 | Record function comes from its part kind, one kind per function; board only "computes"; pin ability only wake/adc/pwm | partly | function_of (parts.py:72-78) uses the record's own `function` list first, kind only as fallback. CAPABILITIES = wake, adc, pwm holds (:184); board = compute/microcontroller holds |
| 3 | spark knows 7 parts and 2 boards | holds | parts/ has 7 JSON records, boards/ 2 |
| 4 | Research runs only for a gap after the yes; stops at first vendor that fits | partly | store-design:440-442 holds; parts-researcher.md:35-36 says stop at first fit "unless you were asked to compare" |
| 5 | Match shows owned/free counts and what each owes; "spark knows no prices"; no trade-off columns | holds | idea.md:38-47 |
| 6 | Picks/reservations wait for P97 (Ready) and P76 (Idea) | holds | idea.md:67-71; gh project: #18 Ready, #5 Idea, #6 Idea, #70 Discovery |
| 7 | Synthetic robot run: eight unrelated sensors then "... 3 more"; cap explained as "keeps the first 8" (needs.py:163-164, parts.py:1724-1726,1738) | partly | The sort holds, but the cut is `rank < 8 or c["what_matches"]` (parts.py:1725): a candidate whose words match the need is never hidden. Hiding happens only for fitting candidates with other words (here "distance" vs "obstacle"). Run outputs in runs/ not re-run |
| 8 | 1.4 / 7: "the cap of 8 hides fitting ones" | partly | Same exception: only fitting ones that lack the need's words are hidden |
| 9 | `--need` never reads a record's function; finds nothing for obstacle/distance (parts.py:1202-1227); research reuse-first uses it; story map 4.3 "no" | holds | _matches reads id, name, kind, aliases only; research.md:17-24; STORY_MAP.md:71 "no (P39)" |
| 10 | Touch refused: "not something a pin can be asked for. Known: wake, adc, pwm" (assign_pins.py:207-211) | holds | Exact text |
| 11 | ESP32-S3 has 14 touch pins (Espressif guidelines) | holds | Guidelines page and datasheet: 14 touch IOs, GPIO1-14; series resistor 470 ohm-2 kohm confirmed |
| 12 | `--function-set` finds part records only (parts.py:1645-1648) | holds | _record_path uses kind "part" only |
| 13 | Unclaimed IR signals "ASSIGNED, AND CONNECTED TO NOTHING" (emit_board.py:737-746) | holds | Text identical |
| 14 | LED resistor: (I/O V - forward V)/current, E12 rounded up, arithmetic printed (emit_board.py:595-618) | holds | series_ohms |
| 15 | Seven backwards limits; "three printed limits fail the very rule that printed them" ([fixes]) | could not open | [fixes] not in the three assigned reads; not checked |
| 16 | I2C message "use <= ... ohm, or drop the bus to a slower mode ..." (check_physics.py:416-424) | holds | Exact |
| 17 | Pull-down vs module pull-up fault is calculated (parts.py:1284-1316) | holds | pull_conflicts |
| 18 | Board states no input-high level, only io_volts (firebeetle json:413-421) | holds | grep for input_high/vih/threshold in board file: nothing |
| 19 | VL6180X record's note names R6, but it is R5 on Pololu | holds | Pololu schematic image: R5 47k goes to GPIO1, R6 47k to GPIO0/CE |
| 20 | Same note: "line clears the S3's threshold holds only typically" | holds | 2.8 V typical vs 2.475 V; worst case fails per recompute below |
| 21 | Same note has the "fighting" backwards | partly | Note says a host pull-up "is fighting a divider rather than helping". Whether that is "backwards" is interpretation: a pull-up to 3V3 raises the level (confirmed +221 mV), a pull-down lowers it. Defensible, loosely worded in the record |
| 22 | No kinds step; 7 parts; part-finder "finds one part, not a survey" (part-finder.md:3) | partly | part-finder.md:3 says "at most two candidates", still one need |
| 23 | Pick points at a part or drawer entry; writer places only picks with a record (store-design:173-177, 180-182) | holds | |
| 24 | Records may ask four resistor kinds (parts.py:327-330); transistor is advice (emit_board.py:609-611) | holds | HOST_PART_KINDS = pulldown, pullup, divider, series; error text "through a transistor" |
| 25 | `kinds library` is "not spark's catalog layer, which holds researched parts nobody chose" (GLOSSARY:177-182) | partly | GLOSSARY: "Everything research has ever read, chosen or not" |
| 26 | Hirtz 2002: terminology "repeatable and meaningful results"; claimed in abstract | holds | NIST page quote; 13 verbs are spark's own, not Hirtz's list |
| 27 | Ritchey GMA: quote "not to allow normative judgments to initially influence" p.6 | holds | PDF p.6 |
| 28 | Ritchey "more than 100 projects" (p. 1) | partly | The phrase is in the author bio on p.8 ("Since 1995 he has directed more than 100 projects involving computer aided GMA"), not p.1; and it is about his projects, not a validation |
| 29 | 4,096 combinations but 240 pair judgements (6 needs x 4 options) | holds | 4^6 = 4096; C(6,2) x 16 = 240 |
| 30 | SparkFun groups distance sensors LED, LIDAR, ultrasonic, VCSEL | holds | Page shows exactly those four |
| 31 | HWE-Bench: 8.15% best, 300 tasks, datasheets supplied | holds | Abstract; 2,914-datasheet knowledge base |
| 32 | pcbGPT: 20 tasks, 0.90 pass@1, 0.72 hard, verdict quote, tasks name components | holds | Abstract |
| 33 | AnalogCoder 20 circuits; Pro 28 circuits across 13 types | holds | Both abstracts |
| 34 | Ma et al.: AI ideas more feasible/useful, less novel; few-shot steers | holds | Abstract (12 challenges) |
| 35 | Massoudi & Fuge: covered under 20% of requirements | holds | "Requirement coverage remained minimal (less than 20%)" |
| 36 | Kannengiesser & Gero, Jensen & Andreasen, Pahl & Beitz page range, Zwicky, Pugh/Frey, TRIZ, CELUS 75%, Circuit Mind 90%/4h13, JITX 3-5 details, Flux, atopile, kicad-happy, WEBENCH, ADI | could not open | Not re-opened (books, paywalled or marketing); answer correctly labels vendor figures "claimed" |
| 37 | store-design cites: :14 proven by use, :25-40 spine and ways in, :29-30 "spark gives facts...", :417-420 owned first simpler beside, :101/:231 passed over keeps reason, :191 nearer layer wins, :39-40 swap/extend | holds | Read each |
| 38 | firmware-and-tests.md:15-18, 86-100, VISION.md:39, :60, :61; DECISIONS.md:18-22 four outcomes; SKILL.md:3 chain | holds | Read each |
| 39 | W21 (WORKING_AGREEMENTS:255-257) keeps no prices | partly | Lines 255-257 are the "keep a datum only if a decision rests on it" rule; prices are excluded in store-design.md:228-243 ("Never: ... prices") and idea.md:44-45 |
| 40 | W14 :150-156; backlog P76 :589-591, P97 :803-813, P100 :815-835; circuit-json is_subcircuit README:490 | holds | Read each |
| 41 | Bin: SENSOR_OPTIONS has eight options, compares interface/range/cost/driver/verdict, constraint :3-5; added 125e73a 2026-09-23 10:29 | holds | 8 table rows; git log |
| 42 | LID_CLOSE_DETECTION added 8088892 on 2026-09-22; three patent methods :7-28; chose own :42-50; "Simplest, no extra parts" | holds | |
| 43 | Deep sleep arrived 1809f1f 10:50 on 2026-09-23 | holds | git log |
| 44 | Strategies via config strings (config.py:27-30, 253-256) | holds | |
| 45 | 3.2 conditions "30-100 mm" cited to SENSOR_OPTIONS:3-5 / config.py:21-23 | partly | Those lines do not give 30-100 mm; SENSOR_OPTIONS says 5-15 cm. 30-100 mm is TOF_NEAR/FAR_MM at config.py:108-109 (not cited). Section 5 Test 1 uses 5-15 cm: the two sections disagree |
| 46 | "Among the parts the bin researched, only the VL6180X in interrupt mode meets 'keeps watching while the chip sleeps', apart from the button" | partly | SEN0239 and SEN0019 (one digital output pin, researched in SENSOR_OPTIONS.md:23-24) would also meet it electrically; they were rejected on size and 5 V, not on this condition. The ULP/touch were never listed (answer says so) |
| 47 | "'Sense a hand' had ten answers" (3.5 item 2) | partly | SENSOR_OPTIONS lists eight; ten only if the button and touch are added; not stated |
| 48 | Polled VL6180X awake costs 13.2-42.3 mA (S3 Table 5-9 p.67) | holds | WAITI 13.2 (40 MHz) to 42.3 (160 MHz); p.67 |
| 49 | Touch deep sleep 18 uA typ at 1% duty (Table 5-10 p.68) | holds | Footnote 3 of Table 5-10 |
| 50 | S3 Table 5-4 p.65: VIH 0.75 VDD, IIH 50 nA, pull-down 45 k | holds | |
| 51 | VL6180X 105-355 uA at 2 Hz; 2.46 mA worst (Table 14 p.36) | holds | Recomputed: 105.2, 354.9, 2459 uA; datasheet example 2472 reproduced |
| 52 | VL6180X pin current 10 uA (Table 24 p.47); GPIO1 open-drain, 47 k pull-up (Table 2 p.10) | holds | |
| 53 | Today: 1.892 V awake, 1.099 V asleep, needs 2.475 V; headroom 0.325 V; R5 59.6 uA | holds | Recomputed 1.8919, 1.0995, 2.475, 0.325, 59.57 |
| 54 | A0 reads 72 mV with internal 45 k pull-up vs 1 k; STALL_COUNTS 4000 = 0.58 A | holds | 71.7 mV; 4000/6898 per A (16-bit, 0.95 V, 0.1 ohm) = 0.58 |
| 55 | 1 MOhm row: +0.092 V (50 nA), -0.349 V with 10 uA | partly | Both reproduce, but on different bases: +0.092 includes 5% carrier and 1% pull-down tolerances; -0.349 has none (with tolerance it is about -0.385). "Nothing on the line" similarly +0.222 (tolerance) vs -0.247 (none; about -0.279 with it). Row mixes corners in one cell |
| 56 | 47 k to 3V3 active-high: +221 mV (10 uA), 128 uA | holds | Recomputed worst margin +0.221 over VDD 3.0-3.6, AVDD 2.7-2.9; 69+59.6 uA |
| 57 | Active-low 47 k: +221 / +242 mV, 5.3 uA fed back | holds (not independently re-derived for +242) | 5.26 uA reproduces; asserted case from calc.py |
| 58 | BSS84 R_G 47 k: +122 mV off-margin; 70 C threshold about 0.665 V vs 0.678 V | holds | Max V_SG 0.678 recomputed; 0.8 - 0.003 x 45 = 0.665; datasheet 3 mV/C typ (Rev 5 p.2), flagged INFERRED |
| 59 | PNP stage: 3.4 V/70 C/10 uA D12 0.707 V (0.143 under V_IL); 3.6 V turns on; 1.2 uA fed back, 58.4 uA saved | holds | Re-derived V_EB 0.420, I_C 7.0 uA, D12 0.707 with the answer's model; model itself is an estimate (ideal-diode extrapolation), as labelled |
| 60 | Re-chosen values 150 k/68 k: back-feed 1.88 uA, creep 0.159 V vs 0.101 V | holds | 0.5 V/266 k = 1.88 uA; x0.49 s/5.8 uF |
| 61 | Active-low wiring dated 2026-09-24 in 85cb86d | holds | At 85cb86d: WAKE_ON_HIGH = False, 100 k pull-ups |
| 62 | Bin code cites: board.tsx:273, :168-178, :355-361, :384-385, :166-167; close_detection.py:35-37, :49-50; proximity.py:45, :205-232, :235-244; l9110s.chip.c:1-17; test_assembly.py:111-116; TEST_PROTOCOL:65-70; SHOPPING:66-75 | holds | Read each. Note board.tsx:380-385 comment calls GPIO1 "push-pull"; the datasheet says open-drain (answer follows the datasheet) |
| 63 | "Limit" detector passes validation but copper does not serve it (consequence: lid reports closed at once) | holds (inference) | config.py:255 allows "limit"; consequence follows from the 72 mV figure |
| 64 | Statuses #18 Ready, #5 Idea | holds | GitHub project read |
| 65 | `bin:` doc claims "[bin] 2.33 V guaranteed" (2.8 - 0.47) | holds | 2.8 - 47k x 10 uA = 2.33 |

Checked: 65 rows (about 120 individual claims). The ones I could not open: [b25], [fixes], [tools] contents beyond what I recomputed, and the books, papers behind paywalls and vendor pages in row 36.
