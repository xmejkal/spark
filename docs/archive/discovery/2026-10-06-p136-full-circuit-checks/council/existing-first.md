# The existing-first lens (Sonnet, 2026-10-06; its report verbatim; the PO's mid-run inputs reached it by message)

## Findings

Tool tags read [licence · kind · network at run time · MCP version]. `ext:` = repository read via `gh api`, 2026-10-06; `cmd:` = run here the same day. "Shown" = code, feature documentation or a run; "claimed" = vendor text. The bin has tscircuit CLI 0.1.2124 / tscircuit 0.0.2621; spark pins 0.1.2113 / 0.0.2600 (data/tools.json:77-82); I read the bin's.

**In the product**

EX-1 · spark's five checks hold no solver and no voltage-threshold rule (re-read; agrees with the reads, H: inputs/remedies.md §1) · E · scripts/check_all.py:279-290; scripts/check_physics.py:196-425; scripts/compare_design.py:117-212; scripts/parts.py:1284-1316 · supports only: today's code. [MIT · local Python CLI · offline · no MCP]

EX-2 · spark's converter already states what Wokwi cannot model: decoupling caps "do nothing in a digital simulation", I²C "idealised", wake pulls have "no floating-input model", no part for the I²S amplifier; `limits_of` writes each stand-in's stated limit to `WHAT-THIS-CANNOT-SHOW.md` · E · tools/circuit-to-wokwi/lib/mapping.ts:218,232,236,245; scripts/sim_project.py:74-122 · supports only: limits stated for digital simulation; a slot analogue limits could use.

EX-3 · neither shipped chip uses the analogue API (grep `pin_adc_read|pin_dac_write|ANALOG`: none); the VL6180X INT is `OUTPUT_LOW` plus `pin_write`, push-pull, so B25 cannot appear; the L9110S prints direction only; both chips and `wokwi-api.h` are byte-identical to the bin's copies · E · parts/vl6180x-breakout/chip/vl6180x.chip.c:69,174; parts/l9110s-module/chip/l9110s.chip.c; bin:firmware/micropython/sim/chips/ (diff empty) · supports only: the two chips.

EX-4 · the converter's "KiCad hand-off" extension point reads `Netlist`, which holds names and pins but no values, so a SPICE emitter cannot be built on it as it stands; tscircuit's converter reads `circuit.json` (EX-12) · E · tools/circuit-to-wokwi/lib/types.ts:10-44; ARCHITECTURE.md:110-117 · supports only: today's IR.

EX-5 · `roles` has no analogue-solver, ERC or DRC job and `tools.json` no kicad, ngspice or spice entry; a `path` entry finds a tool by `exe` or an `also` list. Here `command -v kicad-cli` is empty though KiCad 10.0.6 is in the user's Applications folder (4.8 GB by `du`; kicad-cli inside the bundle); `command -v ngspice` finds Homebrew's 47, installed 2026-10-06 16:07 UTC, so the frame's "not found" no longer holds for ngspice; lcapy does not import · E · data/tools.json:3-14,36-44; cmd · supports only: this machine and today's list.

EX-6 · tscircuit's findings reach spark thinly: `check_spine` (the build) fails on any `*_error` in circuit.json; `check_all` reads one warning type (`supplier_footprint_mismatch_warning`, via the-order) and no `*_error`. The journey doc's "Nothing here measures the spacing between nets" holds for trace-to-trace only (EX-13) · E · scripts/check_spine.py:230,430-441; scripts/check_bom.py:49; scripts/check_all.py:258-275; docs/guide/journey.md:602-606 · supports only: what spark reads.

EX-7 · the reviewer agent has `Read, Grep` only: it can run neither a calculator nor ngspice, yet its `signals` dimension names "logic thresholds … pull-ups and their budget" · E · agents/design-reviewer.md:4,39 · supports only: its toolset.

**In the person's own tools**

EX-8 · `make check` runs four of spark's scripts (boards validate, vendor pins, BOM, physics) and not `check_all`, `compare_design` or `check_footprints`; Wokwi runs are separate token-gated targets. The bin's wake-polarity check compares two statements (config text, the rail behind BtnOpen) and knows nothing of the sensor's INT level · E · bin:Makefile:202,212,220,228,232,147,160; bin:tools/circuit-to-wokwi/lib/checks/wake-polarity.ts:24-99 · supports only: what runs.

EX-9 · the bin's scenarios assert serial lines and 0/1 pins only; `set-control` drives presses and the chip's sliders; the firmware-level sim's `FakeADC` is a settable integer: both are slots for a computed analogue value · E · bin:firmware/micropython/sim/*.scenario.yaml; bin:firmware/micropython/tests/fake_machine.py:170-182 · supports only: current use.

**tscircuit as installed in the bin (question c)**

EX-10 · analogue simulation exists: `<analogsimulation>` (plus transient, DC-op, DC-sweep, AC-sweep variants), voltage/current sources, probes, ammeter, `<spicemodel>` (a vendor `.subckt` onto a `<chip>`); default engine `spicey` (pure JS; R, C, L, V, diode, switch; `.ac` and `.tran` only; no BJT/MOSFET in its types); `ngspice` is eecircuit-engine WASM fetched from jscdn.tscircuit.com at run time; `tsci simulate analog` fetches 1.7.4 to the temp folder; the CLI has no `spice` export though the docs list one · E, shown (code + docs) · bin:node_modules/@tscircuit/core/dist/index.js:62507-62640; bin:node_modules/spicey/dist/index.d.ts; bin:node_modules/@tscircuit/ngspice-spice-engine/dist/index.js:1-17; bin:node_modules/@tscircuit/cli/dist/cli/main.js (export list ~:352077); ext:tscircuit/docs docs/command-line/tsci-export.md · supports only: features of this version. [MIT · library + CLI · spicey offline, ngspice needs network on first use · no MCP in the CLI; `tsci agent` runs a separate tsci-agent, unread]

EX-11 · run: a scratch board (2.8 V, 48 kΩ, 100 kΩ) built with the installed `tsci build` gave 1.8918918918918914 V at the probe with the default engine and 1.8918918918918919 V with `spiceEngine="ngspice"`; native ngspice-47 `op` gave 1.891892 V in 0.12 s: all B25's awake level. The bin's circuit.json holds 0 simulation elements · E, shown (run) · cmd, 2026-10-06 · supports only: one hand-made divider, not the bin's board.

EX-12 · `circuit-json-to-spice` converts R, C, L, diode, LED, BJT, MOSFET, switch, sources, op-amp, subcircuits (its README lists only R, C, BJT); nothing found builds a `.subckt` from a part record's facts (H: none found); `@tscircuit/ti-parts-engine` loads TI SPICE models automatically (docs) · E, shown (code) · bin:node_modules/circuit-json-to-spice/dist/index.js, README.md; ext:tscircuit/docs docs/guides/running-tscircuit/platform-configuration.md · supports only: converter coverage. [MIT · library · offline · no MCP]

EX-13 · board checks without KiCad: `@tscircuit/checks` 0.0.208 exports 35 checks (pad-pad, pad-trace, via-trace, via-via, copper-to-edge, copper-pour shorts, overlap, out-of-board, pin-must-be-connected) against built-in JLC minimums (trace 0.1, via 0.2/0.3 mm); no trace-to-trace clearance and no pin-type ERC by name. They run inside `tsci build` and land as `pcb_*_error`; the bin shows 0 errors and 7 warning kinds. `tsci check shorts` is bitmap-based. tscircuit's skill: DRC errors "can frequently be ignored during development". spark's via minimum (0.3/0.6 mm, trace 0.15) differs · E, shown (code + docs) · bin:node_modules/@tscircuit/checks/README.md, dist/index.js:1725-1733; data/fabrication.json (process); bin:dist/board/circuit.json; ext:tscircuit/skill CLI.md:159-163,189 · supports only: named checks of one version, not their accuracy. [no licence file in tscircuit/checks (GitHub: none); core and CLI MIT · library · offline · no MCP]

**Wokwi (question b)**

EX-14 · Wokwi's docs: "a digital simulator with basic analog support … very limited analog simulation"; `pin_adc_read` needs ANALOG mode; `pin_dac_write` uses a fixed 5 V reference "regardless of the MCU"; resistors cannot be combined with analogue parts, only used "as external pull-up/pull-down"; for the ESP32-S3, the ADC is simulated, I²S is not, RTC is partial (pull-ups/pull-downs only), ULP is not. The docs repo never mentions SPICE · E, shown (docs) · ext:wokwi/wokwi-docs docs/chips-api/analog.md, docs/parts/wokwi-resistor.md, docs/guides/esp32.md · supports only: what Wokwi documents on 2026-10-05.

EX-15 · what a chip can model: digital pins (INPUT_PULLUP/PULLDOWN, ANALOG; one watch per pin), timers in µs or ns (µs preferred for speed), `get_sim_nanos`, float attributes, 'range' sliders (the only control type), I²C/SPI/UART devices; no open-drain mode or pin impedance is documented; API "in beta"; any WASM language; compile is local and free · E, shown (header + docs) · chips/wokwi-api.h; ext:wokwi-docs docs/chips-api/{time,gpio,attributes,chip-json,getting-started}.md; data/tools.json:37-38 · supports only: the documented API; not run.

EX-16 · a running Wokwi simulation can be driven from outside: `wokwi-client` (PyPI 0.5.1) offers `resume_simulation(pause_after=ns)`, `read_pin` (a digital bool plus pull flags), `listen_pin`, `set_control` (float), `read_vcd`; `wokwi-cli mcp` is an experimental MCP server. The simulation runs in Wokwi's cloud (firmware uploaded); free is 50 min per rolling 30 days, 5-min sessions · E, shown (code + docs) · ext:wokwi/wokwi-python-client src/wokwi_client/client.py:270-300,379-420; ext:wokwi-docs docs/wokwi-ci/getting-started.md:23,29-44, mcp-support.md; data/tools.json:164-176 · supports only: the control surface; no analogue read. [MIT · CLI + library · network required · MCP yes, official, experimental; spark's entry is off]

**Co-simulation (question a)**

EX-17 · I found no tool that joins Wokwi's firmware simulation to an analogue solver; a web snippet mentions feature requests (H, not opened) · E, shown (absence in the docs repo and the org's repository list) · supports only: absence in what I read.

EX-18 · the installed ngspice 47 carries lock-step hooks: `ngSpice_Init_Sync` with `GetVSRCData`/`GetISRCData` (the host supplies an EXTERNAL source's value at each time), `GetSyncData` (the host sets the next step), `SendData` (vectors per step); `digital.cm` holds `d_cosim` (Verilog via Verilator since 42, VHDL via GHDL since 44) and `d_process` (C processes over pipes, since 42). BSD-3 core; COPYING lists exceptions (KLU LGPL-2, xspice table GPL-2+, osdi MPL-2) · E, shown (header + docs) · cmd: libngspice sharedspice.h:290-320; https://ngspice.sourceforge.io/extras.html (2026-10-06); ngspice COPYING · supports only: that hooks exist; nobody has wired them to an MCU here. [free · CLI + shared library · offline · MCP third-party, EX-21]

EX-19 · Velxio is the one open mixed-mode firmware+SPICE simulator I could read: Xtensa ESP32/ESP32-S3 on a QEMU fork, MicroPython, ngspice-WASM; its docs say quasi-static (analogue resolved once per 1 ms slice), the ESP32 ADC gets a precomputed periodic waveform interpolated per read, lock-step is a backlog "large refactor"; chips use its own `velxio-chip.h`, not `wokwi-api.h`; its MCP server imports/exports Wokwi `diagram.json` · E, shown (docs + test names, not run) · ext:davidmonterocrespo24/velxio README.md, docs/wiki/circuit-emulation-overview.md, -adc-aliasing.md:237-266, -esp32-qemu.md, docs/CUSTOM_CHIPS.md:5-8, docs/MCP.md · supports only: its own statements. [AGPL-3.0 plus commercial licence · web app / Docker · offline when self-hosted · MCP yes]

EX-20 · Proteus VSM is a commercial firmware+SPICE co-simulator; only vendor text (a search snippet, not fetched) supports it · claimed · supports only: its existence. SimulIDE, Renode and simavr did not surface; unchecked.

**Skills, plugins, MCP servers beyond kicad-happy (question d)**

EX-21 · SPICE MCP servers exist, all needing a native simulator: SPICEBridge (GPL-3.0; `pip install`; 28 tools; 11 E24-snapping templates, among them divider, RC, op-amp; Monte Carlo; none for pull-ups, level shifts, LEDs, transistor stages), ltspice-mcp (GPL-3.0; plugin or `uv tool install`; LTspice or ngspice; six tools; its README says MCP "adds little" for quick local ngspice runs), mcp-spice (Apache-2.0 per README; `npx`; ngspice batch in a Podman image; `.meas` as JSON) · E, shown (READMEs, none run) · ext:clanker-lover/spicebridge README.md, src/spicebridge/templates; ext:Cognitohazard/ltspice-mcp README.md:46-51,106; ext:zesun33/mcp-spice README.md · supports only: their descriptions. [free · MCP servers · offline, needs ngspice · MCP-only]

EX-22 · BoardRepo: a Claude Code plugin (MIT wrapper) onto a closed hosted MCP: KiCad DRC/ERC on stored boards (`run_checks` runs kicad-cli server-side), fab-limit profiles for three houses, `review_board` findings marked deterministic or heuristic with a `notChecked` list; boards must be on BoardRepo (public, or the user's own via OAuth); no upload tool; price not stated · claimed (service) · ext:flintt-dev/boardrepo-plugin README.md, skills/boardrepo/SKILL.md · supports only: the plugin's description. [hosted · MCP · network required · MCP-only]

EX-23 · ESP32-AI-Agent-Skill (MIT): a pin-map validator (strapping, ADC2/Wi-Fi, flash pins) and fixed rule-of-thumb tables (4.7 kΩ I²C …); no SPICE, ERC, DRC or calculation; overlaps `scripts/assign_pins.py` · E, shown (files) · ext:ezrover/esp32-ai-agent-skill README.md, references/electrical-constraints.md · supports only: its files. [MIT · local Python · offline · no MCP]

**Without installing KiCad**

EX-24 · does the user need KiCad? For KiCad's own ERC and DRC, which spark's skills call authoritative, yes: I found no other local engine for them. kicad-cli ships only in the full install (1.40 GB image: the coordinator's check, 2026-10-06; 4.8 GB installed here); third-party MCP servers wrap an installed kicad-cli: kicad-mcp (MIT, last push 2025-10-17), kicad-buddy 0.1.0 (MIT). spark treats KiCad as optional · E, shown (metadata) · README.md:160; skills/spark-review/SKILL.md:77-79; skills/spark-design/SKILL.md:92; ext:KiCad/kicad-source-mirror; ext:lamaalrajih/kicad-mcp; PyPI · supports only: licences, sizes, stance, and absence among what I looked up. [GPL-3.0 · CLI inside a GUI app · offline · MCP yes, third-party]

EX-25 · what runs without KiCad: tscircuit's build-time checks (EX-13; offline; partial); hosted JLCDFM, whose own page says "free", Gerber ≤ 50 MB, "30+ point checklist", five modules (traces, masks, drilling, silkscreen, assembly), no API on the page (the bin's package is 0.41 MB); BoardRepo (EX-22). No pip/npm engine runs DRC on a `kicad_pcb`: kiutils and kicad-skip parse files, gerbonara and pygerber read Gerber, kicad-python needs a running KiCad (H) · claimed (JLCDFM) · https://jlcdfm.com (2026-10-06); PyPI summaries; bin:board-gerbers.zip · supports only: vendor text; names I looked up. [JLCDFM: free web service · network required · no MCP. Libraries: kiutils and kicad-skip licence not in PyPI metadata; gerbonara Apache-2.0; pygerber MIT; kicad-python MIT · offline · no MCP found]

EX-26 · analogue engines without a big app: Homebrew's ngspice added 8 formulae, 18.4 MB; PyPI has no `ngspice`, `libngspice`, `ngspice-bin`, `ngspice-shared`, `pyngspice` or `ngspyce` (PySpice 1.5 and spicelib 1.6.4, both GPL-3.0, are pure-Python wheels of 0.7 and 0.3 MB, so no bundled simulator); npm `eecircuit-engine` (MIT, 43 MB unpacked, WASM embedded, no dependencies) can run offline once installed, and is what tscircuit fetches · E, shown (metadata) · cmd `du`, `brew info`; PyPI JSON and `npm view`, 2026-10-06 · supports only: those names. [ngspice: BSD-3 core · CLI · offline · MCP third-party (EX-21). eecircuit-engine: MIT · library · offline once installed · no MCP found]

**Defaults and swapping (D: the PO's inputs of 2026-10-06, relayed; candidates are my reading, H; nothing decided)**

EX-27 · per job, a candidate default and what a setting could offer (tags as above):
- Calculate: spark's scripts over part facts [MIT · CLI · offline · none], the only code that sees the facts (H: the reads). Alternatives: SPICEBridge's solver [GPL-3.0 · MCP-only]; kicad-happy what-if [MIT · skill, no MCP]; atopile [MIT · local CLI · — · —].
- Rule checks: spark's `check_all` [same]. Alternatives: BoardRepo `review_board` [hosted MCP]; kicad-happy detectors (KiCad files only; skill, no MCP).
- ERC/DRC: `@tscircuit/checks` via `tsci build` [no licence file · offline · no MCP], partial (EX-13). Alternatives: `kicad-cli` [GPL-3.0 · offline · third-party MCP]; JLCDFM [web]; BoardRepo.
- Analogue: native `ngspice` CLI [BSD-3 core · offline · three third-party MCPs]. Alternatives: tscircuit spicey (offline, few devices) or ngspice-WASM (npm offline, or CDN); LTspice and Xyce (GPL-3.0, unchecked), both reachable through ltspice-mcp.
- Digital: `wokwi-cli` [MIT CLI · cloud, free quota · network · official experimental MCP], in use. Alternatives: the bin's MicroPython runtime sim (local, offline, no peripheral timing); Velxio self-hosted [AGPL-3.0 · MCP yes; chips not portable].
· H (from EX-1 to EX-26) · supports only: a candidate list, not a ranking by accuracy.

EX-28 · swap patterns. In spark: `roles` map a job to a tool, `meets` declares a contract, a role pointed at a tool without it is refused by name, `--use ROLE=TOOL` writes the choice, `--on/--off` installs and registers or unregisters an MCP server (sigrok; `wokwi-mcp` off); every contract is named for the file exchanged (`wokwi-project`, `tscircuit-board`, `esp32-littlefs`), none for a SPICE netlist, a KiCad file or Gerber. Outside (from sources already read; no search left): tscircuit's `spiceEngineMap` and `defaultSpiceEngine` (named engines taking a netlist and returning Circuit JSON, chosen per `<analogsimulation spiceEngine>`, a missing name raises a named error); ltspice-mcp's `[simulator] default` with auto-detection over LTspice, ngspice, QSPICE, Xyce, built on spicelib; file formats as adapters (`tsci export`, Velxio's `diagram.json` import). Chips have none: `wokwi-api.h` against `velxio-chip.h`. spark's two MCP servers start unpinned with `npx -y` (P112) · E · data/tools.json:3-22,164-176; docs/2026-10-03-tools-design.md:124-140; commands/setup.md:2,60-62; README.md:156-157; ext:Cognitohazard/ltspice-mcp README.md:122-134; bin:node_modules/@tscircuit/core/dist/index.js:62523-62640; ext:tscircuit/docs docs/guides/running-tscircuit/platform-configuration.md:37-38 · supports only: that the patterns exist.

## What I could not check, and why

- Velxio, BoardRepo, JLCDFM, SPICEBridge, ltspice-mcp, mcp-spice and the KiCad MCP servers were read, not run: documentation at best, "claimed" for the hosted ones.
- No Wokwi run (metered, needs the PO's yes): whether `pin_dac_write` on a chip pin reaches the S3's MicroPython `ADC`, and how the fixed 5 V reference maps to counts, are untested.
- `kicad-cli` ran only `version` (10.0.6); no ERC or DRC on an exported `kicad_pcb`, so what KiCad finds beyond tscircuit's checks on the bin is unknown here.
- spark's pinned tscircuit versions were not read; BJT support in `spicey` is from type declarations, not a run; the CDN fetch for the ngspice engine is inferred from code and the differing last digits, not seen on the network.
- Licences are GitHub's detection, README badges or package metadata, not a legal reading; `tscircuit/checks` shows none.
- Not read: Renode, SimulIDE, simavr, Qucs-S, Xyce, `tsci agent`, BoardRepo and JLCDFM terms, price or API; Proteus beyond a snippet; the reads' tool claims (kicad-happy, JITX, atopile and the rest), as the brief says.

## Questions for the decider

- Is "no KiCad install" a requirement, or is today's stance (KiCad optional, README.md:160) enough, with tscircuit's build-time checks as the default and `kicad-cli` opt-in? · decides the ERC/DRC role's default and whether J6 may call a check complete without KiCad.
- Is `@tscircuit/checks` (no licence file; minimums that differ from `data/fabrication.json`) an acceptable named source for spark's board checks, and whose numbers win? · decides whether spark reads tscircuit's `*_error` list or keeps its own limits.
- Is Wokwi's free quota (50 min per rolling 30 days, firmware uploaded to a cloud) "free" for the digital-simulation default, or is a local simulator the default and Wokwi opt-in? · decides that role's default (W10 already budgets minutes).
- Analogue default: native `ngspice` CLI (18 MB via Homebrew, no pip or npm wheel), tscircuit's in-build engines (spicey offline but few devices; the ngspice option needs the network), or npm `eecircuit-engine` offline (43 MB)? · decides the analogue role's contract and whether its default needs a native install, a network, or neither.
- Should a contract be named for a file format (SPICE netlist, `kicad_pcb`, Gerber), as `wokwi-project` is today, so a swap is refused before running? · decides the adapter shape.
- MCP switch: only where an official MCP exists (Wokwi), or also for third-party wrappers (kicad-cli, ngspice), given unpinned `npx -y` (README.md:156-157) and ltspice-mcp's own "adds little"? · decides which tools get an MCP setting.

## Searches

Five web searches, all used.
1. `co-simulation microcontroller firmware emulator with ngspice analog circuit simulation open source (SimulIDE, Renode, simavr, QEMU, Proteus VSM)` · whether a tool already joins firmware simulation to an analogue solver (question 5) · used: Velxio, ngspice hooks, Proteus (claimed); SimulIDE, Renode, simavr not returned.
2. `Claude Code skill OR plugin OR MCP server that runs SPICE (ngspice) simulation, circuit value calculation, KiCad ERC DRC for electronics design` · other skills or plugins beyond kicad-happy (question d) · not used: it returned only kicad-happy's spice skill, already surveyed.
3. `MCP server ngspice SPICE circuit simulation for AI agents (LTspice MCP, ngspice MCP, circuit simulator MCP)` · whether ngspice has an MCP version (the PO's MCP-in-settings input) · used: SPICEBridge, ltspice-mcp, mcp-spice; `circuit-sim-mcp` (PySpice) not verified.
4. `JLCDFM free online DFM check Gerber upload before ordering JLCPCB design rule check` · a board check needing no KiCad at the fab the bin uses · used: jlcdfm.com.
5. `Wokwi simulator analog circuit simulation SPICE ngspice support resistors capacitors feature request` · whether Wokwi has or plans analogue · barely used: second-hand; Wokwi's docs repo settled it; a conda ngspice package surfaced, unchecked.

Named-page fetches (not searches): velxio.dev/circuit-simulator; ngspice.sourceforge.io/extras.html; hackaday.io/project/205046-spicebridge; dfm.jlcpcb.com (redirect) and jlcdfm.com. Via `gh api`: the wokwi-docs and tscircuit/docs tarballs, wokwi-python-client, Velxio, SPICEBridge, ltspice-mcp, mcp-spice, boardrepo-plugin, esp32-ai-agent-skill, EEcircuit-engine, licence fields of about 25 repositories. Registries: `npm view eecircuit-engine`; PyPI JSON for 17 names.
