# The refuter (Opus, 2026-10-06; first pass, on brief.md as it stood at 18:57; its report verbatim, except that its Searches part's sub-bullets are joined onto one line in the skill's format, words unchanged)

I reviewed `brief.md` as it stood at 18:57:06 CEST (blob 0560187) and `items.md` at 18:56:20 (65a3960). The brief was edited while I read it: between 18:55 and 18:57 the Ready-for line, ★C6 and ★C12 were reworded. `inputs/` means `docs/discovery/2026-10-06-p136-inputs/`. I re-ran spark's checks on the bin with `PYTHONDONTWRITEBYTECODE=1` and a fresh `SPARK_HOME`. `git status` in both repositories is the same as when I started.

## Check first (own idea, on an existing product)

**Does the change address the observed problem?**
- **The problem.** spark says nothing about the bin's faults. Three circuit faults were filed on the bin on 2026-10-06:
  - B25, the wake-line level;
  - B26, the standing current;
  - B28 (bin #22), the motor return on 0.15 mm copper, "seen in KiCad's DRC of the exported board". B28 appears in none of the eleven files.
- **The facilitator's first pick does not reach them.**
  - Q4 (a) is four cards that the brief's own Scope calls "prerequisites, not scope" (brief.md:20).
  - Q4 (b) is a test.
  - Neither reports B25, B26 or B28.
- **Only Q4 (c) reaches B25**, and only after five facts that no record holds are added, plus a path into hand-written boards (Q10).
- **B28's kind of fault is in no option.**
- **Q3 (a) cannot touch the bin.** It changes `scripts/emit_board.py`, and the bin's hand-written `board.tsx` never goes through it.

**What breaks for current users:**
1. **A B25 rule turns the bin's `make check` red** (`bin:Makefile:228`, the physics step) until the hardware fix is fitted. The bin has been here before: `bin:.spark/rules.json:30` says a standing red line "kept the commit gate red on this one line, and every commit skipped the gate". The brief's "must not get worse" list leaves this out.
2. **Q3 (a) makes tscircuit write `*_error` elements** for gaps between 0.1 mm and the fab's figure.
   - `check_spine`'s build stage fails on any such element (`scripts/check_spine.py:230,430-433`). That breaks the brief's own "`check_spine` exits 0" (brief.md:21).
   - spark's fab data holds no spacing figure at all. For scale, KiCad counted "63 gaps under 0.15 mm" on the bin (bin #22 comment).
3. **The product's own review skill disagrees with Q3's default.** `skills/spark-review/SKILL.md:77-78` calls `kicad-cli sch erc` and `pcb drc` "the authoritative electrical and layout checks". The brief does not mention this.
4. **Q6 and items.md's "P154" duplicate #89**, which is already P154 (created 2026-10-06T16:38:58Z). The PO filed #89 so that this would not be done now: "Don't do it now, only create a chore and we can get to it right after what we're doing is done".

**Confirmation bias:**
- **The KiCad answer gives one side.** Q3's text (brief.md:85) carries only the feasibility lens's view, which matches the PO's stated preference. Three lenses said the opposite (part 2), and B28 is absent.
- **Pass lines sit just under results already in hand:**
  - A1 asks for "at least 6 of the 17", and the first reader already had 7.
  - A3 asks for "at least 1", and RI-11 already counts "1 transient".
  - A2's figures are the verifier's known answers.
- **Outcome (2) is a known answer** on the only board.
- **This run is also P102e's proof.** #29 (11:32Z) makes P102e "Done when P136's discovery (#70) has produced journeys and a story map". RI-3's warning that this "pulls toward delivering artefacts whatever the result" was dropped.
- **The case for waiting was dropped:**
  - RI-1 to RI-3 found that no design is blocked without P136.
  - The PO's request carries the condition "we'll work on it next when everything works" (`.superpowers/discovery-inputs/2026-10-06/po-request-2026-10-06.md:74`, git-ignored).
  - No option offers "nothing enters Design yet".

**The team standing in for its users:**
- **The jobs are the PO's own examples.** Every "When… / I want…" clause in J1–J8 cites #70, the PO's request, as its E evidence (jobs-and-journeys.md:16-23).
- **Every test reader is the PO or an agent:**
  - A6 and A9: the PO reads, n = 1.
  - A2: two fresh agents.
  - A1 and A3: a second agent reader.
- **The maker's journeys narrate an agent-written log.** The journey lens itself warns: "79 of 94 commits since 2026-09-20 carry a Claude trailer … the log shows what the project recorded, not what he saw or did" (council/journey.md:60). That warning was dropped.

## 1. The ★ claims, source by source

**★C1: holds.**
- **Re-run, as `bin:Makefile:228` calls spark's `scripts/check_physics.py`:** "  [trace-current] GND: carries up to 1.50 A and is served by a copper pour, which this check cannot size", exit 0.
- **`scripts/compare_design.py` on the same inputs:** "every rule holds.", exit 0.
- **`inputs/remedies-verify-claims.md:28`:** "| 20 | On the bin all three checks exit 0 and say nothing on the wake line | holds | bin-run.checker.txt: exit=0 x3; only a GND pour note and two annular-ring advisories |"
- **Pointer fault.** The command cannot run "in the bin" as written, because the bin has no `scripts/` folder. It is spark's script run on the bin's files.

**★C2: partly.**
- **What the three cards say.** bin #19, bin #20 and #73, Archive line, each: "— (new on the board, 2026-10-06, found by a rehearsal discovery and verified)".
- **The claimed set is incomplete.** bin #22 (B28, labelled bug, created 2026-10-06T16:22:53Z) has this Archive line: "— (new on the board, 2026-10-06, seen in KiCad's DRC of the exported board and verified against board.tsx and the built board)".
- **The gloss is not in the source.** "agents reading datasheets and schematics" appears in no Archive line, and #73's body says nothing about checks.
- **Sentence to change:** "The three faults filed on 2026-10-06 (B25 and B26 on the bin, P139 in spark) were each "found by a rehearsal discovery and verified": agents reading datasheets and schematics, not a check, Wokwi or the bench".
- **Why.** It leaves out the one fault filed that day that a board check found. Q5 (c)'s caveat and the journey row "found by reading, not by any check" inherit the gap.

**★C3: holds, clause by clause.**
- **`bin:firmware/micropython/sim/chips/vl6180x.chip.c:69`:** "  chip->pin_int = pin_init("INT", OUTPUT_LOW);"
- **`:174`:** "  pin_write(chip->pin_int, assert_interrupt ? HIGH : LOW);"
- **`chips/wokwi-api.h:12-20`:** "enum pin_mode {" … "INPUT_PULLDOWN = 3," "ANALOG = 4," "OUTPUT_LOW = 16," "OUTPUT_HIGH = 17,". There is no open-drain member.
- **`inputs/data-chips-format-verify.md:203`:** "| 116 | The Handson guide was retrieved 2026-09-24, and the chip models no current | `parts/l9110s-module.json:170`, `:148` |"
- **A non sequitur in the claim.** "the L9110S chip models no current" is no reason Wokwi cannot show B25, which is a level on the time-of-flight line. It belongs to stall and B26.

**★C4: partly.**
- **`inputs/remedies-verify-maths.md:14`:** "- **One material gap: the "worst corner" leaves out the sensor pin's own input current.** VL6180X"
- **`:19-20`:** "  - no passive option reaches the S3's VIH, **even at nominal**. The released line tops out at / 2.33 V nominal and 2.20 V worst, against 2.475 V (R03–R06);"
- **`council/feasibility.md:12`:** "At 10 µA, no pull-down: 2.328 V nominal, 2.204 V worst (−0.271 V against 2.475 V)"
- **The figures hold; the story of how they arose does not.**
  - The source describes one working that "leaves out" the input, caught by an "**Independent calculator.**" (`:45`, a nodal-solver script). These were agent scripts, not two hand workings that "disagreed". FE-4 is a third working.
  - "nominal" includes the 10 µA maximum. The verifier says at `:248-249`: "ST gives no typical GPIO1 current, so "nominal" means zero sensor current". And at `:182`: "A1 holds only while GPIO1 draws ≤ 1.96 µA at the worst corner (≤ 4.34 µA nominal). No source gives that figure."
- **Sentence to change:** "Worked by hand twice from the same datasheets, B25's fixes disagreed on one input, the sensor pin's own current of up to 10 µA; with it no pull-down reaches 2.475 V (2.328 V nominal, 2.204 V worst, calculated)".
- **Why.** The choice of riskiest assumption rests on this claim. It calls an omission caught by a second script a disagreement, and it calls a datasheet maximum a nominal.

**★C5: holds.**
- **`council/risks.md:33`:** "My split of 17 faults or unknowns from the bin, rc-car and the reads: 7 closed-form arithmetic over stated facts (…); 1 transient (470 uF, removed with its part); 2 bench-only (motor current, wake); 2 facts errors (P139, DFR0954 bias); 1 netlist rule (no pull-ups); 4 geometry or fab"
- Other sections contradict its "1 transient" (part 2).

**★C6: partly.**
- **`scripts/check_all.py:201`:** "    for requirements in sorted(root.glob("*requirements.json")):"
- **`:211-212`:** "…requirements files describe this circuit, so no rail was " "summed from the part records"
- **`parts/vl6180x-breakout.json:76`:** ""note": "R6, 47k to VDD — which is 2.8 V, not the host's 3.3 V — with R8 1k in series out to the header. …"
- **`council/feasibility.md:11`:** "Five are absent: open-drain output type and series R8 1 kΩ (prose only), …"
- **What holds:** facts reach physics only through a requirements file, and the series 1 kΩ is in prose.
- **What is refuted:** the output type is in the record in no form. The words "drain", "push-pull" and "output type" appear nowhere in the file, and the pin entry says only `"direction": "out",` (`:23`).
- **Sentence to change:** "the output type and the series 1 kΩ (prose in a note only)". The same wording is in items.md:24.

**★C7: partly; the caveat is refuted.**
- **`bin:node_modules/@tscircuit/checks/dist/index.js:1724-1725`:** "// node_modules/@tscircuit/jlcpcb-manufacturing-specs/lib/jlcpcb-manufacturing-specs.ts" / "var jlcMinTolerances = {"
- **`:2520`:** "  minClearance ??= getBoardDrcValue(board, "min_trace_to_pad_edge_clearance") ?? DEFAULT_TRACE_MARGIN;"
- **`:2605`:** "      if (obj.type === "pcb_trace_segment") {". So trace-to-trace spacing is measured, contrary to EX-13.
- **`bin:node_modules/@tscircuit/core/dist/index.js:70066`:** "const shouldRunRoutingChecks = !drcChecksDisabled && !pcbDisabled && !routingDisabled && !routingDrcChecksDisabled;"
- **What refutes the caveat:**
  - bin #22's comment: "KiCad 10.0.6 ran its DRC with its default rules on `tsci export board.tsx -f kicad_pcb`, on 2026-10-06. It found 585 violations and 0 unconnected items."
  - bin #22's body: "How it was found. KiCad 10.0.6's DRC of the exported board flags all 199 tracks narrower than its default 0.2 mm minimum. This is the one that carries the motor's current."
- **Sentence to change:** "caveat: KiCad not run on an export, so what it adds is unknown".
- **Why.**
  - KiCad's DRC was run (its ERC was not), and what it added is filed: B28, plus the checklist in the comment (the V33 feed to the amplifier at 0.15 mm, a self-intersecting FireBeetle courtyard, keepout hits).
  - "its own minimums" also hides that the code labels them JLCPCB's.

**★C8: holds.**
- **`bin:node_modules/@tscircuit/ngspice-spice-engine/dist/index.js:2`:** "var EECIRCUIT_ENGINE_URL = "https://jscdn.tscircuit.com/@tscircuit/eecircuit-engine/1.7.6/+esm";". It is fetched at `:6` and imported at `:16`.
- **`council/existing-first.md:33`:** "…1.8918918918918914 V at the probe with the default engine and 1.8918918918918919 V with `spiceEngine="ngspice"`; native ngspice-47 `op` gave 1.891892 V in 0.12 s: all B25's awake level."

**★C9: partly.**
- **`commands/setup.md:60`:** "| `add sigrok` | `tools.py --on sigrok` | `{"sigrok": {"on": true}}`; installs it, and registers an MCP server with Claude Code |"
- **`scripts/tools.py:158-159`:** "    if kind == "mcp":" / "        return None  # Claude Code runs a server; spark has no command for it"
- **`council/feasibility.md:26`:** "`simulator`→`wokwi-mcp` is refused because that entry declares no `meets`."
- **What exists is narrower than claimed.** It registers a server beside the CLI. It does not switch a job to the MCP version, and only Wokwi has a twin entry.
- **Sentence to change:** ""The CLI by default, its MCP version by a setting" already exists as `/spark:setup`'s add and remove of a twin entry".
- **Why.** It is not what the PO confirmed, "a setting switches a tool to its MCP version" (brief.md:15). He has also sent this design to #89.

**★C10: partly.**
- **`git show 6557c71`:** "Out of v1, by the PO's call: real PCB layout, analogue / simulation, a link between two boards, …"
- **`scrum/VISION.md:60`:** "| Analogue simulation; a link between two boards | out of v1 by the PO; R10 parked |"
- **`skills/spark-design/references/verification-loop.md:28-29`:** "5. **Deferred: analog SPICE (ngspice/PySpice).** Only when a real analog subcircuit exists; / meaningless for a digital module board with a motor load."
- **The deferral is conditional, and the file is old.** The same file still says "Wokwi CI for ESP32-C6" and names the TB6612 (`:24-25`), so it was written before the S3 board.
- **Sentence to change:** "spark's own design reference defers SPICE as "meaningless for a digital module board with a motor load" … caveat: none".

**★C11: holds, for what the existing-first lens (EX) read.**
- **`council/existing-first.md:49`:** "EX-17 · I found no tool that joins Wokwi's firmware simulation to an analogue solver; …"
- **`:51`:** "EX-18 · the installed ngspice 47 carries lock-step hooks: `ngSpice_Init_Sync` …"
- **`:53`:** "… quasi-static (analogue resolved once per 1 ms slice) …"
- **The hook exists.** Homebrew's ngspice 47 header, `sharedspice.h:398` (outside both repositories): "int  ngSpice_Init_Sync(GetVSRCData *vsrcdat, …"
- **Not opened.** Velxio's own documentation was not fetched.

**★C12: holds.**
- **`council/electronics-firmware-physics.md:39`:** "…stall = 1.08 / 0.73 / 0.55 / 0.37 A … for 4 / 6 / 8 / 12 Ω [calculated; R_motor assumed]"
- **`bin:.spark/rules.json:28`:** "1.5 A is the L9110S's own limit, NOT a measurement of this motor."
- **`council/feasibility.md:21`:** "the L9110S record states 0.8 A continuous"
- The context this claim dropped is in part 2.

## 2. Each section against the detail it summarises

**Header**
- **"on the lenses' evidence … KiCad optional".** Three lenses said otherwise, and no split is recorded:
  - EX-24 (council/existing-first.md:67): "does the user need KiCad? For KiCad's own ERC and DRC, which spark's skills call authoritative, yes".
  - JO-17 (council/journey.md:49): "today only for DRC/ERC, the one measure of net spacing".
  - RI-9 (council/risks.md:27): "without it no design-rule check exists".

**Frame**
- **Request.**
  - The quote of the PO's request drops the condition at `:74`: "we'll work on it next when everything works".
  - Comment 3's quote drops its opening "in general," without an elision mark.
- **Outcome (2):** "physics, rules-vs-design and buildability all exit 0". Dropped context:
  - spark's own one-call check, `check_all --project .`, exits 2 on the bin: "[????] physics … ! 0 requirements files describe this circuit, so no rail was summed from the part records" (re-run).
  - The bin's `make check` runs neither `compare_design` nor `check_footprints`: no call to either appears in `bin:Makefile` (EX-8).
  - "on the bin at 8847eb8" does not fit Q10's option of the bin gaining a requirements file.
- **Already decided.** It omits #89, where the PO said: "lets note it down and have the council come up with a good easy system … Don't do it now, only create a chore". D5, Q6 and items.md's P154 cut across that.
- **Scope against Options.** Scope puts P107, P122 and P141–P145 out as prerequisites, yet the first Design pick, Q4 (a), is those very cards.
- **Start and reach.**
  - "decider reachable: no" — but he answered a clarification mid-run (brief.md:15), and his new words of the same day are on #89.
  - The KiCad install is reported without its result (bin #22).
  - "must not get worse" omits the bin's commit gate (see Check first).
- **Item.**
  - Build also holds P102 (#24).
  - Idea also holds P154 (#89), on Q6's subject.
- **Search budget.**
  - "six verified reads": `inputs/README.md` gives board-proposal "—" as its check, and process-proposal only "its own skeptic pass".
  - "cover most outside tools": `inputs/remedies-verify-claims.md:56` says "Cadence PSpice, KiCad ERC, Altium, SKiDL, tscircuit, lcapy, ngspice rows | could not open / not rechecked".
  - "PH 3": these are one Espressif-docs MCP query and two WebFetches (council/electronics-firmware-physics.md:88-90). The existing-first and feasibility lenses count fetches as "not searches" (existing-first.md:112, feasibility.md:60).

**What we found**
- **C1** drops `check_all`'s exit 2, which risks-and-tests.md:18 does carry.
- **C4** drops the verifier's caveats K01 and R03.
- **C7** drops three things:
  - EX-13's "no licence file in tscircuit/checks";
  - tscircuit's own advice that DRC errors "can frequently be ignored during development";
  - that the bin's board already passes the fab's via minimums and `fabricatorPreset="jlcpcb_economy"` (`bin:board.tsx:50-54`). tscircuit runs a fab DRC from that preset only when a platform supplies an engine (`bin:node_modules/@tscircuit/core/dist/index.js:70078`). No lens examined this route.
- **C8:** 1.8919 V excludes the sensor pin's 10 µA. The feasibility lens's own B25 deck (FE-12) gave "1.5885/1.5727 V" (feasibility.md:20).
- **C12** drops two things:
  - The project's own stall figure: `bin:LID_CLOSE_DETECTION.md:15` "running, ~230 mA stalled, 200 mA threshold", and `bin:STATUS.md:53` "The 70 mA / 230 mA figures are from patent literature". That is below the whole 0.37–1.08 A range.
  - PH-12 (electronics-firmware-physics.md:37) places 1.5 A as "in L9110 the typical peak, max 2 A", and the record lists 1.5 A among sellers' figures (`parts/l9110s-module.json:60`).
- **C13 is bin #22, already filed.** Neither the brief nor items.md:47 says so.
- **Carried nowhere in the brief:**
  - RI-1 to RI-3: nobody is blocked, and P102e's Done "pulls toward delivering artefacts whatever the result".
  - RI-21: the checks may work only on the maker's Mac.
  - RI-25: worst-case defaults that flag every open-drain line teach agents to skip the check.

**Options**
- **Q2 (c)** says the split "found none that needs it", and the A3 row (risks-and-tests.md:39) says "none of the 17 (RI-11)". Both contradict RI-11's own "1 transient". RI-19 says "none", so the risks lens contradicts itself, and the brief took the stronger reading.
- **Q3 (a)** has three gaps:
  - `emit_board` never builds a hand-written board.
  - `data/fabrication.json` has no spacing key; it holds only `min_trace_width_mm` 0.15 and the via and ring sizes. "Sourced keys" therefore means new research.
  - The feasibility lens's "the effect on `/spark:build` exits is untested" (FE-8) became "may fail".
- **Q3 (b)** drops the installed size, "4.8 GB by `du`" (EX-5).
- **Q3 (c):** FE-22 says "~100 lines each … (H)".
- **Q4 (a)** cites `board-proposal.md:17`, but the four cards are listed at `:156`.
- **Q5 (c):** "three faults found by reading" ignores B28.
- **Q6:** "small" was FE-20's "~20-60 lines … H".
- **The no-go** "no KiCad … on the default path" was written without B28.

**Riskiest assumption and its test**
- **"every job's output rests on it".** J6 (board checks) and J7 (bench) read no record bounds.
- **"failed on an input".** It failed in an agent's working; no record was involved.
- **The pass line is stricter than its source, RI-18 (council/risks.md:51), in two places:**
  - The brief says "raises nothing on the bin's other pull lines". RI-18 says "raises no finding on the bin's other pull lines (SDA, SCL, BtnOpenPulldown, L9110S inputs) that both readers cannot defend". The brief's version would fail a calculator that correctly reports the real L9110S input band (PH-4).
  - The brief says it "prints `?` wherever a verdict rests on a typical-only input". RI-18 says "for the S3's pull-down and GPIO1's leakage", and its test is "typical-only or unsourced". GPIO1's 10 µA is a maximum with no typical, so the brief's rule would not mark it.

**Questions**
- **Q3** gives one side.
- **Q12** asks the PO for an origin that PH-12 already proposes.
- **Lens questions dropped:**
  - RI's question 1: whether B25's desk decision waits for spark (the W14 pull).
  - PH's question 4: whether a return net not named in rules.json is examined (B28's kind).
  - EX's question 2: the checks package has no licence; whose numbers win?
  - JO's DQ2: is "could not run" for DRC and ERC acceptable without KiCad?

**Decisions.** There is no D for #89.

**Found on the way**
- **P156.**
  - `docs/guide/journey.md:603` already says "The build stage stops on any error tscircuit writes into `circuit.json`".
  - EX-6 and EX-13 disagree with FE-8 on trace-to-trace spacing, and the split is not named. The code at `checks/dist/index.js:2605-2617` supports FE-8.
- **P152's third proof.** #86 asks for "A simulation of the bin's wiring shows the line asserting below the S3's input-high level.", not "a Wokwi run".
- **The search-count claim** is right, by the discovery skill's `scripts/discovery.py:37,439`, but its pointer cites the lens files instead.
- **B26's days.** 17.7 needs 7.06 mA. With the card's stated "6.4–7.1 mA", the range is 17.6–19.5.

**Board actions.** "file P154–P156": P154 already exists as #89.

**jobs-and-journeys.md**
- **J6 "Today"** omits bin #22.
- **Maker step 6 (`:46`):** "runs `make check`: physics, rules-vs-netlist and buildability exit 0". Of those three, `make check` runs only physics.
- **Hobbyist step 8 (`:70`):** "its ADC is referenced to 5 V" cites `journey.md:350`, which is the L9110S chip line. EX-14 attributes the 5 V reference to `pin_dac_write`, a chip's output, and PH-16 tags it H.
- **Hobbyist step 11 (`:71`):** "without it net spacing is measured by nothing" contradicts ★C7.

**risks-and-tests.md**
- **`:13`:** "the bin's faults to date are mostly steady-state arithmetic". RI-11 has 7 of 17 (41 %), from three sources, not the bin alone.
- **A4's pass line** is met by "could-not-run naming what it lacks".
- **`:20` and `:70`:** "about 79 °C" is a temperature rise: 10 °C × (1.5/0.604)^(1/0.44) = 79.0 °C.

**story-map.md**
- **`:35`** says "no resistor change fixes the line", and items.md:23 says "so no resistor change fixes it". Against both:
  - `inputs/remedies-b25-worked.md:108`: "Only a source tied to 3.3 V lifts it: a pull-up (option B) or a transistor (option C)."
  - `inputs/remedies-verify-maths.md:27-28`: "What stands: … the option B and abs-max figures".
  - bin #19 rejects option B for its sleep current and the unplugged-cable wake loop, not for the level.
- **`:43`:** "KiCad not run" is refuted by bin #22.

**items.md**
- **`:6`** "P153 is the highest" is false. #89 is P154, and items.md was last written at 16:56Z, after #89 was created.
- **`:47`:** the MOTOR_SENSE item is bin #22.
- **`:50`** drops PH-6's "Which case holds depends on the lid window".

## 3. Interpretations and their strongest rivals

1. **C1 and outcome (2): the silence means a rule is missing.**
   - Rival: spark's single answer already says "could not look" (exit 2), and what is missing is data. Five of the facts sit in no record.
   - Agents reading datasheets found B25. spark's reviewer already covers "logic thresholds between parts on different rails, pull-ups and their budget" (`agents/design-reviewer.md:39`). And: "Whether `/spark:review` ran on the bin after 2026-09-25: no log".
2. **C2: found by reading, so checks miss faults like these.**
   - Rival: sampling. The three came out of a reading exercise.
   - A board check found B28 the same day, and the bench has never run.
3. **C3 and Q5 (a): the chips as written are the obstacle, so put computed values in chips.**
   - Rival: no chip lets Wokwi show this fault. Resistors work only as pull-ups or pull-downs (EX-14), Wokwi's S3 support table has no sleep or wake row (PH-21), and wake-from-GPIO was shown only on the C6 (B27).
   - A chip carrying a precomputed "below VIH" encodes the very answer it is meant to test.
4. **C4 and A2 as the riskiest assumption.**
   - Rival: one agent missed an input and a second caught it. That is evidence for the two-reader check, not against the records, which neither working used.
   - "No passive fix" follows from treating a no-typical maximum as the corner, and that policy is still open (Q8). Passive fixes hold below 1.96–4.5 µA.
5. **C5, A1 and Q2 (a): arithmetic dominates, so formulas first and SPICE out.**
   - Rival: survivorship. Desk reading finds steady-state faults.
   - Transients such as motor start, brown-out and inrush (PH-15, PH-22) would show up at a bench that has not run. RI-11 itself counts one transient.
6. **C7 and Q3: the user does not need KiCad for spacing.**
   - Rival: tscircuit's DRC checks its own router against the router's own 0.1 mm limit. bin #22 reports the smallest gap as "0.100 mm", exactly that limit.
   - An independent checker, KiCad, found what self-consistency could not.
7. **C8: three engines agree, so native ngspice is a viable rung.**
   - Rival: they agree on 2.8 × 100/148, which is arithmetic.
   - That says nothing about how they handle transients or module internals.
8. **C9: the switch already exists.**
   - Rival: it is a side-by-side registration, not a switch.
   - The PO routed this design to #89.
9. **C10: the not-goal and the reference support leaving SPICE out.**
   - Rival: both predate B25 and B26.
   - The reference is conditional and was written for the earlier C6/TB6612 board.
10. **C12: stall is 0.37–1.08 A.**
    - Rival: the project's own patent figure, 230 mA.
    - That implies a motor of about 20 Ω, outside the assumed 4–12 Ω.
11. **A2 is the riskiest assumption.**
    - Rival: the riskiest is value — whether P136 should move now at all.
    - No design is blocked (RI-1 to RI-3), and the PO said "when everything works".
12. **J1–J8 are the hobbyist's jobs.**
    - Rival: they are the PO's examples from #70's question 1.
    - Those examples are then cited as their own evidence.
13. **Q12: the 1.5 A has no origin.**
    - Rival: it is the L9110 datasheet's typical peak (PH-12), or a seller's figure (`parts/l9110s-module.json:60`).
14. **P152's third proof may be out of Wokwi's reach.**
    - Rival: #86 asks for "a simulation".
    - ngspice already reproduces the level.
15. **B26's day count does not follow from its own figures.**
    - Rival: the card may have used the battery's capacity at a 6–7 mA drain, which is higher than the 3.0 Ah rated at 25 mA.
    - The folder does not rule this out.
16. **51 of 74 open items missing from STORY_MAP is a gap.**
    - Rival: since 2026-10-05 the project board holds the order.
    - The map is kept "as text for P102b to draw" (`scrum/STORY_MAP.md:49-52`).

## 4. Numbers lacking unit, population, period or provenance

- **"the lenses used 12 (… PH 3)":** the 12 mixes web searches with an MCP query and two fetches.
- **"1,404,303,659 bytes":** "the coordinator's check", with no URL or version given. The installed size, 4.8 GB, is absent.
- **"2.475 V":** valid at VDD 3.3 V and 25 °C (Table 5-4). At a 3.0 V supply it is 2.25 V (bin #19).
- **"1.89 V" / "1.8919 V":** assumes zero current into the sensor pin. With its maximum the level is about 1.57 V (FE-12).
- **"2.328 V nominal, 2.204 V worst":**
  - "nominal" already includes the 10 µA maximum;
  - the corners rest on ±3 % and ±5 % tolerances that have no source (FE-4);
  - no temperature is given.
- **"17 faults or unknowns":**
  - no period;
  - the 4 geometry or fab items are not named;
  - faults and unknowns from three projects are counted together.
- **"5 of the 10 inputs":** the ten are FE-3's list and are not named in the brief.
- **"0.1 mm":** its source, `jlcMinTolerances` (`checks/dist/index.js:1724-1733`), is not stated.
- **"0.37–1.08 A":** assumes a 6.4 V pack, the L9110's typical drops measured at 9 V and 750 mA, and an assumed 0.2 Ω path.
- **"20–26" and "17.7–19.5 days":**
  - the 3.0 Ah is rated at 25 mA to 0.8 V per cell;
  - 17.7 rests on 7.06 mA, not the stated 7.1;
  - "flat" is not tied to the L9110S's 5.0 V input-high limit (PH-4).
- **"51 of 74":** no time of day is given. It counts #89 (16:38Z) and R2.6.
- **Unquantified estimates:**
  - "a sitting" (Q3 (c), Q4 (b));
  - "four small cards";
  - "small" (Q6), which was 20–60 lines in FE-20;
  - "one rule (an estimate)" (Q4 (c)), with no owner named.
- **"one metered scenario":**
  - how many Wokwi minutes it costs is unknown (feasibility report, §2);
  - W10's "~21 of 50" free Wokwi minutes predates 2026-09-25 (JO-1).
- **risks-and-tests.md:**
  - "79 °C" is a rise, not a temperature.
  - "0.41–2.9 mA" asleep is the LiPo/3V3 side, while "1.92 mA + 3.4–4.5 mA" is the AA pack; neither battery is named.
  - "35.85 s … 40–65 mA" is at 160 MHz, with boot and the sound cue excluded (PH-10).
  - "20 wakes a day" is an assumption.
  - "0.49–0.50 A at 8 Ω" assumes an unverified 0.6 W at 0.9 efficiency (PH-11).
- **items.md "2.46 mA, seven times":** holds only with nothing in view, at 2 Hz.

## Searches

1. **Query:** "JLCPCB PCB capabilities minimum trace spacing clearance 2-layer mm" · **Decision it serves:** Q3 (a). Would passing "the fab's numbers" to tscircuit change any spacing verdict, given that its built-in 0.1 mm is labelled JLCPCB's? · **Result:** not decisive. The snippets disagree for 2-layer boards (0.127 mm / 5 mil against 0.10 mm), no page was opened, and nothing above rests on it. **Returned, not opened:** [api.jlcpcb.com capabilities](https://api.jlcpcb.com/capabilities/Capabilities), [design.jlcpcb.com capabilities](https://design.jlcpcb.com/capabilities), [Quilter on JLCPCB](https://help.quilter.ai/en/articles/11689889-jlcpcb)
