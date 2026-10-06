# Non-maths claims in answer.md: verdicts (adversarial check, 2026-10-06)

Spark read at 8f7733d, bin at 8847eb8 (both HEAD, unchanged). Read-only. No spark command was run; existing run outputs
(probe-output.verify.txt, led-and-i2c.verify.txt, show-l9110s.verify.txt, bin-run.checker.txt) were read and cross-checked
against the source. Other tools: URLs fetched today.

| # | claim | verdict | what the source says |
|---|---|---|---|
| 1 | 17 places report a fault: physics 6, rules-vs-design 4, buildability 6, CONFLICT 1 | holds | check_physics.py Findings at :250,279,321,329,376,418; check_footprints.py :180,217,223,245,270,375; compare_design.py :133,155/166,196,207; parts.py:1284 |
| 2 | Column totals (fix 15 + 1 partly, alternatives 8, calculates 7 + 3 partly, re-checks 0) | holds | Consistent with the rows and the fix= strings read |
| 3 | I2C message verbatim, 3541 ohm fails its own rule (300.03 ns); exact 3540.7 | holds | check_physics.py:416-424; probe-output.verify.txt A3; led-and-i2c.verify.txt 3540.667 |
| 4 | "use >= 6 V" fails for 6.3 V cause; 10 V passes | holds | probe A1: 4.2*1.5 = 6.300000000000001, 6 V rejected, 10 V no finding |
| 5 | "at least 0.18 mm" fails at 15 of 26 currents | holds | probe A2 prints 15 of 26 and 0.60/0.69 A |
| 6 | LED resistor 0.090 W -> 0.132 W when lowered | holds | probe A4 |
| 7 | Only the hole size rounds the safe way, check_footprints.py:188 | holds | math.ceil at :188 |
| 8 | Asked 60 mA the generator gives 27 ohm, ~51.9 mA; record says 30 mA max | holds | led-and-i2c.verify.txt; parts/led-red-5mm.json:71-72 |
| 9 | emit_board.py:595-618 E12 sizing; :585 table; :609-611 "higher rail through a transistor" | holds | line 585 is E12; 611 has the string |
| 10 | data/fabrication.json:38-48 package power / max capacitance tables | holds | lines 36-50 |
| 11 | CONFLICT test parts.py:1284-1316, L9110S quote | holds | code matches; show-l9110s.verify.txt:19 has the sentence (answer quote is cut before "(input-high threshold 2.5 V)") |
| 12 | Generator places those pull-downs in the file carrying the warning (emit_board.py:673-678, :945-947) | holds | :672-678 pull-down resistors; :946-947 CONFLICT line |
| 13 | Reviewer has no field for a fix and never had one (agents/design-reviewer.md:89-107; git log -S) | holds | JSON schema has no fix field; `git log -S"fix"` on the file returns nothing |
| 14 | check_all drops every fix (check_all.py:129,139-141,229-231) | holds | of() returns "subject: detail" only; :129 is the problem-line builder |
| 15 | Review skill: "one next action. Not a plan", SKILL.md:23, 59-61, 86-87 | holds | :23 command, :60 "propose **one** next action. Not a plan", :86-87 |
| 16 | The 100k pull-down satisfies the floating-input rule; cited compare_design.py:188-189 | partly | Behaviour correct (resistor to a rail net counts). Line numbers wrong: the logic is at :200-205 (:188-189 is docstring text) |
| 17 | Sensor record states the carrier's 47k pull-up, verified, names R6 (parts/vl6180x-breakout.json:72-80); no code reads it | holds | key `carrier_pulls_up_the_interrupt` value 47000 verified:true, note says R6, 2.8 V in prose; grep finds the name only in that record (outside .superpowers) |
| 18 | Board file states no input-high level for the S3 (boards/firebeetle2-esp32s3.json:413-422) | holds | :413-422 is io_volts; grep for input_high/vih/0.75/input_low finds nothing |
| 19 | Two names for a module's own pull: onboard_input_pullups_ohms (l9110s-module.json:84) and carrier_pulls_up_the_interrupt | holds | both present |
| 20 | On the bin all three checks exit 0 and say nothing on the wake line | holds | bin-run.checker.txt: exit=0 x3; only a GND pour note and two annular-ring advisories |
| 21 | Spark's physics only computes limits; the generator's trace width = min x 1.15 (copper.py:60, 88-98) | holds | TRACE_WIDTH_MARGIN 1.15 at :60; width_to_emit_mm :88-99 |
| 22 | Bin: TofIntPulldown 100k to GND (board.tsx:273, 384-385) | holds | |
| 23 | Bin: internal pull-down armed just before sleep (board.py:88-89); none while awake (hardware.py:183-185 cited in b25) | holds | board.py:88 `pull = Pin.PULL_DOWN`; hardware.py:181-185 no pull |
| 24 | Bin: SOT-23 pin order bit this board before (board.tsx:207-208) | holds | comment names the gate/source/drain order defect |
| 25 | VISION.md:60 analogue sim out of v1; :61 "spark exports facts and a harness" | holds | |
| 26 | W11 :114-118, W14 :150-159, W18 :236-242 | holds | text matches (W11 "propose, ranked, with reasons and costs. Petr decides") |
| 27 | P136 question 1 names "choosing part values ... (a pull-up, an LED resistor, a divider into an ADC, the motor's supply)" | holds | #70 body, question 1 |
| 28 | P136 comment 6014466635 point 3: pull-up budget first general rule; extended it "would also catch B25 (INFERRED)" | holds | quoted text at body line 22 |
| 29 | Comments 6014188640 / 6014250100 are the PO's questions, answer to be linked | holds | |
| 30 | P43 (#11) is "in Idea" and its fix-dropping is a live card; "These cards are all in Idea" | refuted | #11 is CLOSED (not planned) on 2026-10-06 11:31, merged into P118 (#52), which now carries "a fix for every problem" in its proof. The answer is dated after that (file 13:20). P78 (#14) is also closed (done), not Idea. The other cards (#52,#43,#58,#56,#75,#67) are open, Idea |
| 31 | B25 is bin #19 on xmejkal/sisuo-brain-transplant; its facts (R5 not R6, 1.89 V, 1.10 V, 2.475 V, not caught by Wokwi/wake-polarity) | holds | gh issue 19 body |
| 32 | Pull-down tolerance: "No code reads" etc. fine; MicroPython #17334 cited as low-level wake bug | could not open | not fetched (outside scope of read-only list; CLAUDE.md of the bin also cites it) |
| 33 | kicad-happy 0684046: level table 1.8/2.5/3.3/5 (validation_detectors.py:469-477), level-shifter text :646-665, 4.7k I2C fix :757,:772 | holds | read raw at that commit; fix_params type add_component, "Add a level shifter between..." |
| 34 | kicad-happy what-if: snaps to E-series with error (what-if.md:216), calculates dividers/filters/gain/crystal/shunts, re-simulates in ngspice | holds | what-if.md :26, :57 `--spice`, :161-212, :216 |
| 35 | kicad-happy VALIDATION.md: 5,857 projects, measures crashes and regressions not correctness | partly | 5,857 and crash/regression testing confirmed; its regression assertions are "seeded from validated output ... after manual verification", so it does claim some correctness, not none |
| 36 | kicad-happy MIT | holds | LICENSE |
| 37 | JITX divider solver walks precision series, checks both temperature extremes (solver.py:37-129), note at :116 that worst case is not computed | holds | file is src/jitxlib/voltage_divider/solver.py at 6e0dd09; :116 "TODO: Compute the worst case v-out" |
| 38 | JITX: free only for open-hardware designs; docs page 404 | holds | pricing page: "Free ... Open Source (CERN OHL-Permissive v2) Designs Only"; quickstart URL returns 404 |
| 39 | atopile 619eda7: "verif[ies] that candidate combinations satisfy all constraints" (solver/README.md:357-389); MIT; Python 3.14 | holds | README quote at 357-389 region; pyproject requires-python >=3.14; MIT |
| 40 | WEBENCH: power supplies only, datasheet equations, recomputed and simulated | holds | Overview: "end to end system that produces power supply solutions"; OpVals: values from "datasheet equations" (simulation step not re-checked) |
| 41 | AllSpice DRCY from $34,800/year; paper has no accuracy figures; blog suggests E96 value | holds | plans page "Starting at $34,800/ year"; arXiv text has no accuracy/precision/recall figures; blog "Suggested an alternative resistor value using a standard E96 series" |
| 42 | DRCY detects "mismatched voltage domains" and "missing pull-ups" (claimed) | partly | Not in the cited paper or blog. The "missing pull-ups" wording is on allspice.io/ai-agent (not cited); "mismatched voltage domains" not found there either, only in other-tools.md's quote |
| 43 | Flux four named checks incl. "Pull-Up/Pull-Down Resistors: Checks configuration correctness based on the IC's datasheet requirements"; marketing "sizing passives, I2C pull-ups, decoupling caps" | holds | docs page lists Resistor Power Rating, Pull-Up/Pull-Down, Capacitor Voltage Rating, Parts Availability; flux.ai/docs/copilot/overview has the marketing sentence. Outcome levels pass/warning/error stated generally |
| 44 | Siemens Xpedition >150 "voltage-aware" rules, pin voltage mismatch, missing pull-ups | partly | >150 rules and "Pin voltage mismatch" confirmed on techdesignforums; "missing pull-ups" not found on either cited page |
| 45 | CELUS refuses to connect blocks with differing supply levels | holds | docs: interconnected blocks must have compatible supply voltages |
| 46 | Circuit Mind generates translators/passives; SnapMagic product pages 404 | partly | Circuit Mind: article says translators and passives generated. SnapMagic 404 not shown by the cited TechCrunch URL (snapmagic.com home returns 200) |
| 47 | PySpice GPL-3.0, last release 2021 | holds | PyPI: GPLv3, 1.5, 2021-05-15 |
| 48 | Cadence PSpice, KiCad ERC, Altium, SKiDL, tscircuit, lcapy, ngspice rows | could not open / not rechecked | PSpice PDF and others not re-read beyond spot checks; lcapy LGPL and ngspice BSD-3 not fetched |
| 49 | LCSC part numbers and prices | not checked here | covered by verify-maths.md (D38-D40) |

## Corrections in verify-maths.md that answer.md did not take in
answer.md (575 lines) still carries all of these:
- R03/R04/R05/R06: the sensor pin's own IIH <= 10 uA (VL6180X Table 24, p. 47) is left out. With it A1 is 2.097 V worst (-0.378 V), A2/D/E fall below VIH, and no passive pull-down works. answer.md still says A1 "2.57 V worst (+0.09 V)", A2 +0.22 V, D 2.70 V, and the slice's proof numbers (566 k, 680 k +0.035 V, accept 1 M +0.09 V, "no resistor change can give more than 0.325 V" stays true only as an upper bound).
- R07: option C idle "at most 0.032 V ... at every corner computed" fails at 3.4 V/2.7 V/70 C (D12 0.707 V) and conducts at 3.6 V/2.7 V/70 C with GPIO1 at 10 uA. Better pair on the same grid: R_b 150k / R_be 68k (M44).
- R02: idle margin at a 3.2 V rail is +0.795 V, not >= 0.82 V (b25 doc; answer lines 242 is "at most 0.032 V" only).
- R09: creep "at most 0.101 V" is nominal-rail only (0.121 V at 3.4/2.8); the bench criterion "<= 2.9 V" can fail on a healthy design (answer line 276).
- R12: the 8/7 uA deep-sleep figure is stated only for the N4 module, unsupported for the DFR0975 N16R8 (answer line 41-ish "58 uA less" is a difference and unaffected; the ~408 uA budget uses the 8 uA).
- R01/R11: 1.40 mAh not 1.43; 0.46 V not 0.45 V (answer.md already says 0.46 V; R01 is in b25 only).
- R10: back-feed range 4.28-7.31 uA (b25 only).
