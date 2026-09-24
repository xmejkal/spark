# spark audit — 39 findings, ranked

216 tests pass. They pass because the suite tests the *functions* and almost never the *wiring between them*, and because several assertions cannot fail. I ran every script, in a clean second project, against the real `smartbin-local` artifacts.

---

## SEVERITY 1 — the headline feature is dead in its main entry point

**1. `scripts/check_all.py:86` calls a function that does not exist. `pin-capability` has never once run.**
```python
result = check_design.check(inputs["design"], inputs.get("board"))
```
`check_design.py` has no `check`. It has `run(design, board)`, and it takes *dicts*, not the path strings `check_all` passes. Verified:
```
$ python3 scripts/check_all.py --design examples/smartbin.design.json
  [????] pin-capability   AttributeError: module 'check_design' has no attribute 'check'
```
This is the check `plugin.json`'s description leads with, routed through the one command `spark-review` tells the agent to run. `git log -p` shows the line has been wrong since the commit that introduced `check_all`. **Cost:** the review loop's flagship check is a permanent `????`, and the final render still says "nothing found by the checks that ran".

**2. None of the 14 scripts is executable — every documented invocation fails.**
`git ls-files -s scripts/` shows mode `100644` for all 14. `./scripts/check_all.py --help` → `permission denied`. Every skill invokes them directly (`skills/spark-review/SKILL.md:24,33,84,102`, `skills/spark-check/SKILL.md:17`), and the `allowed-tools` patterns (`SKILL.md:4`) only match direct invocation — prefixing `python3` both breaks the allowlist and is nowhere documented. **Cost:** on a fresh install of the plugin, nothing in `scripts/` runs. This one is `chmod +x` plus a commit.

**3. `scripts/check_all.py:73` — a `SystemExit` from any check kills the whole run.**
The guard is `except Exception`, and `check_bom.read_bom` (`check_bom.py:50`) raises `SystemExit`, which is a `BaseException`. Verified:
```
$ check_all.py --package nobom.zip --circuit circ.json --rules rules.json
no bom.csv in nobom.zip
EXIT=1
```
Six other checks never reported, and exit 1 means "problems found". The comment on that line says *"one broken check must not hide the others"*.

---

## SEVERITY 2 — "could not run" still reads as "found nothing" (the stated cardinal sin), in seven places

**4. `check_all.py:121-133` — `vendor-truth` reports `[ok]` and exit 0 when it looked at nothing.**
`VendorTruth.call` folds `could-not-run` boards into `unmeasured` and returns `PROBLEMS if problems else OK`. It also hard-codes `offline=True` (line 126), and `check_vendor_pins.py:108` resolves the cache as `<board file>/../../.spark/cache/`. In any project other than this repo that directory does not exist, so **the only check that looks outside the project can never run there, and always says ok.** Verified in a clean project:
```
  [ok  ] vendor-truth   the board definition matches the vendor's own pin header
           ? firebeetle2-esp32s3: --offline but no cached header at .spark/cache/...
EXIT=0
```

**5. `check_all.py:102-111` — `Physics` silently discards `severity="could-not-run"` findings.**
It surfaces only `problem` and `needs-measurement`. `check_physics.check_i2c_rise_time` emits `could-not-run` for an unknown bus speed. Verified: a rules file with `i2c_hz: 250000` prints `[ok] physics` through `check_all` with no note at all, while `check_physics.py` standalone prints "1 could-not-run" and **still exits 0** (`check_physics.py:372-380` counts only `severity == "problem"`).

**6. `check_footprints.py:130-131` and `163-164` skip holes with no `hole_diameter` / `outer_diameter` and say nothing.**
On the real reference board (`smartbin-local/dist/board/circuit.json`, 70 plated holes): 4 `pill` holes carry no `hole_diameter`, 6 `circular_hole_with_rect_pad` carry no `outer_diameter`. **10 of 70 holes are never examined** and the tool prints `buildable — holes take their pins, packages hold their values`. The docstring's own flagship defect is *"the vendor's finished hole for the vendor's own obround pad"* — the obround shape is precisely the one it skips.

**7. `check_bom.py:101-102` returns `[]` when the circuit file is missing** — and `tests/test_check_bom.py:124-126` asserts exactly that, under the name `test_a_missing_circuit_is_not_treated_as_clean`, with the comment *"it must not report zero problems as if it looked"*. The name and the comment say the opposite of the assertion. `check_all.TheOrder` calls it with a caller-supplied path, so a typo'd `--circuit` silently drops the fatal-at-fab warnings.

**8. `check_design.py:49` — exit 1 for a file it could not read.** A missing design, malformed JSON, and a usage error all `raise SystemExit(...)` → exit 1, which `skills/spark-check/SKILL.md:20` documents as "problems". No exit 2 anywhere in this script. A mistyped path tells the agent the board is broken.

**9. `findings.py:435-437` — `findings.py --json list` prints nothing and exits 0.**
`--json` is declared on both the top-level parser (SUPPRESS) and the subparser parent; the subparser's default clobbers the top-level value. Verified: `findings.py --json --circuit c.json list` → **empty stdout, exit 0**. `findings.py list --json` works. An agent that puts the flag where the top-level parser advertises it gets silence that reads as an empty finding list.

**10. `findings.py:496` — `append` on a missing or malformed file is a traceback, exit 1.**
```
$ findings.py append nope.json
FileNotFoundError ... EXIT=1
```
`main` only converts `SystemExit` into a refusal (`findings.py:472-474`); `json.loads(Path(...).read_text())` raises neither. Exit 1 = `EXIT_PROBLEMS`.

**11. `bench_sim.py:100-101,121-123` — `--json` drops the `simulated` marker entirely.**
```json
{"name":"mp3-idle-current","value":16.53,"unit":"mA","working":"...","why":"..."}
```
No `source`, no warning. The human path prints "NOT A READING"; the machine path — the one added "for a caller" — does not. The module docstring: *"Everything it produces is marked `simulated`. That is the whole design constraint… A simulator that produced convincing readings would be that same failure shipped as a feature."* That is what the `--json` path is.

---

## SEVERITY 3 — the two shipped boards do not speak the same language, and checks fall through the gap

**12. `check_design.py:144-149` — exclusivity is keyed on the silkscreen label, not the GPIO.**
`assign_pins.py:118-120` has a comment about exactly this (*"Two labels may share a GPIO — on one real board both A4 and SS are GPIO10 — so assigning one has to take the other out of play"*) and handles it by GPIO. `check_design` does not. Verified:
```
PartA -> A4, PartB -> SS   (both GPIO10 on the FireBeetle)
→ "nothing to fix." EXIT=0
```
"Two parts on one pin" is one of the five headline mistakes, and it misses the case on the only shipped board where it can occur.

**13. `check_design.py:163` hard-codes the role name `boot_log_tx`. The FireBeetle calls it `console_uart`.**
`boards/xiao-esp32-c6.json` → `boot_log_tx` (GPIO16). `boards/firebeetle2-esp32s3.json` → `console_uart` (GPIO43/44). Verified:
```
XIAO,  reads_serial on D6  → 1 problem, EXIT=1
FBv2,  reads_serial on TX  → "nothing to fix.", EXIT=0
```
The same hazard, one board checked and one not. The same split hits `assign_pins.ROLE_PENALTY` (`console_uart: 40`, `boot_log_tx` unlisted → `DEFAULT_ROLE_PENALTY = 5`) and `CONFLICTING_ROLES` — the boot-log pin is priced 8× cheaper on the XIAO and never produces the "something else is already wired here" explanation. `tests/test_assign_pins.py:46-50` builds its fixture with the FireBeetle's vocabulary only, which is why nothing noticed.

**14. `boards/xiao-esp32-c6.json` `adc_gpio: [0,1,2]` is board-filtered; `firebeetle2-esp32s3.json` `adc_gpio: [1..10]` is chip-level.** The C6's ADC1 is GPIO0–6. Both files also list `wake_capable_gpio` chip-level. No consumer breaks today (everything intersects with `pins`), but the two files answer a different question under one key name, and nothing states which.

---

## SEVERITY 4 — the generator emits a board that would destroy a part

**15. `emit_board.py:48,183-189` — SPKP and SPKN both land on `net.SPEAKER`.**
`RAIL_NETS` maps a rail name to exactly one net, and `parts/dfr0534-module.json` gives both bridged amplifier outputs `"rail": "speaker"`. Generated output:
```jsx
<trace from=".Dfr0534Module > .SPKP" to="net.SPEAKER" />
<trace from=".Dfr0534Module > .SPKN" to="net.SPEAKER" />
```
That shorts a class-D BTL output to itself — the part file's own note says *"bridged amplifier output — never ground either side"*. Emitted under a banner reading *"The CONNECTIONS are derived and trustworthy… Nothing here is guessed."* No test asserts the two are on different nets.

**16. `emit_board.py:154-157` — pin numbers come from dict insertion order, not the module's physical pinout.**
`pinLabels={{ pin1: "AIA", pin2: "AIB", pin3: "VCC", pin4: "GND" }}` for `footprint: "headermodule6"`. `parts/l9110s-module.json`'s own comment says the header is **BIA BIB GND VCC AIA AIB** — so physical pin 1 is BIA and every trace to that module lands on the wrong pad. Also: `unused_pins` is never read by anything, so BIA/BIB are left floating on a 6-pad footprint — which the same part file's `host_requirements` says must never happen. And the footprint default (`part.get("footprint", "pinrow4")`, line 160) is a pin count, unrelated to how many labels were produced.

**17. `emit_board.py:206-212` — the documented `--assignment` flag does not exist.** The module docstring (line 6) says `emit_board.py requirements.json --assignment saved.json`. argparse accepts only `requirements`, `--project`, `--board`:
```
emit_board.py: error: unrecognized arguments: --assignment foo.json
```

---

## SEVERITY 5 — skill prose contradicts the code it drives

**18. `skills/spark-review/SKILL.md:36` tells the agent to run `--boards boards/*.json`. `boards.py:344-345` warns against exactly that glob** (*"Deliberately not `boards/*.json`: that glob also matches active.json, which is a selection rather than a board"*). Verified in a project that follows `boards/README.md`:
```
  [ok  ] vendor-truth
           ? active: no vendor.arduino_variant in active.json, so there is nothing to check it against.
```

**19. `spark-review` never runs `check_firmware.py`.** Its check table (lines 42-49) lists six checks and omits `firmware-vs-board`; its command (lines 33-37) passes no `--firmware`/`--board-file`. It then launches a `firmware-hardware` reviewer (line 64) and tells reviewers *"Do not ask a reviewer to look at anything in that table"* — and firmware is not in the table. `BACKLOG.md` claims `check_firmware.py` "takes firmware-hardware agreement off the reviewer entirely". It did not; the skill was never updated. `check_all` also offers no way to pass an assignment, so the "real check" in `check_firmware`'s own docstring is unreachable through the runner.

**20. `skills/spark-review/SKILL.md:4` — `allowed-tools` lists only two Bash patterns**, but the skill's own steps require building (`make` / `tsci build`, step 1), launching subagents (step 3) and collecting their JSON into a file (step 4). Frontmatter and body disagree about what the skill may do.

**21. `findings.py:138` tells the user to "Run `spark init`". There is no `spark init`** — no `commands/` directory, no such string anywhere else in the repo. It is the first thing a second project hits: every `findings.py` subcommand exits 2 until someone guesses that `mkdir .spark` is the fix.

**22. `README.md` is a release behind.** Footer says `v0.1.0` (`plugin.json` says 0.6.0); it describes "four reviewers" (the agent has five since S3); it documents six skills and mentions **none** of the 14 scripts, the `boards/` library or the `parts/` library — i.e. everything built after the first day is undocumented for an installer.

**23. `skills/spark-check/SKILL.md:74` — "`boards/README.md` in the smart-bin project has the schema."** That file now ships inside this plugin. A reader is sent to a repo they do not have.

**24. `README.md` claims a "verification gate that refuses to emit a board with unverified part pins".** `spark-verify/SKILL.md` implements it entirely as prose instructions — no script enforces it, and it never mentions `parts.py --unverified`, which is the machine-readable half of exactly that.

---

## SEVERITY 6 — dead code and unused capability

**25. `findings.py:367-370` — `_circuit()` references a global `CIRCUIT` that does not exist.** Calling it is a `NameError`. Dead since `Store` landed.

**26. `findings.py` defines `_show` twice (373 and 388) and `_measurement` twice (381 and 396).** The first definitions are shadowed. The dead `_measurement` is the one *without* the `<- NOT A READING` marker — a copy-paste that would silently un-mark simulated numbers if the later copy were ever removed.

**27. `parts.py`'s `project` parameter is never passed by anything.** `search_path`/`available`/`definition_path`/`load`/`signals_for`/`unverified` all take `project=None`, and grep across `scripts/` and `tests/` shows **zero callers supply it**. So the docstring's promise — *"a project may keep its own in `parts/`. A project's own wins"* (`parts.py:35-36`) — is unreachable from every entry point, and no test covers it. The `boards.py` equivalent does work.

**28. 11 of the 14 scripts are referenced by no skill, no agent, no hook and no README** — only by `BACKLOG.md`. Only `findings.py`, `check_all.py` and `check_design.py` appear in a skill. Notably the entire "use case B" chain (`parts.py` → `assign_pins.py` → `emit_board.py`), which `BACKLOG.md` marks **works**, has no skill at all: nothing tells an agent it exists. `bench_sim.py` is referenced by nothing but the backlog. `boards.py`'s CLI (`--list/--paths/--get/--resolve/--validate`) is invoked by nothing inside the plugin — it exists for the sibling project's Makefile.

**29. Fields in the part schema that nothing reads:** `unused_pins` (and it is not validated either), `direction` (validated, never consumed), `also_known_as`, `on_board`, `sources`, `needs[].note`. `boards/*.json` similarly carries `micropython_port`, `wokwi_*`, `deep_sleep`, `sku`, `physical.header`, `physical.mounting_holes` — none read by any script in this repo; they are consumed by the sibling project's generators.

**30. `.mcp.json` declares five MCP servers unconditionally**, three of which need binaries nothing installs (`sigrok-mcp-server`, `wokwi-cli`, `uvx kicad-mcp`). Every session in a project with this plugin tries to spawn them.

---

## SEVERITY 7 — tests that cannot fail

**31. `tests/test_check_all.py:110-127`** — `test_every_check_script_on_disk_is_wired_into_the_runner` greps `check_all.py`'s *source text* for `load("check_design")`. The string is present; the call is broken. This is the test that was supposed to catch finding #1, and its own docstring warns about a previous version that "could not fail".

**32. `tests/test_check_all.py:63-67`** — `test_one_exploding_check_still_lets_the_rest_report` asserts only `len(results) == len(check_all.CHECKS)`. `run()` is `[check.run(i) for check in CHECKS]`, so the length is equal by construction, whatever explodes. **Nothing in the file ever passes `--design`**, which is why finding #1 survived.

**33. `tests/test_emit_board.py:136-141`** — `test_the_board_is_big_enough_for_what_is_on_it` asserts `width > board.width_mm` and `height > board.height_mm`, but `place()` computes `width = module_width + MARGIN + GAP + widest + MARGIN` and `height = max(module_height, …) + 2*MARGIN`. Both assertions are arithmetic identities of the function under test.

**34. `tests/test_findings.py:421-425`** — `test_both_doors_agree` asserts `spoken == json["rendered"]`, and `main()` prints `result["rendered"]` on one path and `json.dumps(result)` on the other. It compares a string to itself. The docstring admits the property is structural ("built from the result, so the two cannot drift apart") and then asserts it anyway.

**35. Exit-code tautologies:** `test_check_all.py:69-71`, `test_check_vendor_pins.py:139-142`, `test_check_firmware.py:129-130` assert that module-level constants defined as `0, 1, 2` on a single line are unequal to each other.

**36. Two tests read a hard-coded sibling checkout and skip silently elsewhere.**
`tests/test_check_firmware.py:135` → `../smartbin-local/firmware/micropython/config.py`
`tests/test_findings.py:288` → `../smartbin-local/dist/board/circuit.json`
Both run on this machine and turn themselves off on anyone else's. They are the only two tests that touch a real firmware or a real `circuit.json`. `tests/test_check_vendor_pins.py:155-156` does the same with `skipTest` when the cache is missing — a test that opts out of running when its input is absent, in the file whose docstring is about refusals not being passes.

---

## SEVERITY 8 — the data libraries

**37. `parts.py:116-119` — the fact contract checks key *presence* only.** `{"value": 2.5, "verified": true, "source": null}` and `"source": ""` both validate with zero problems. Verified directly. The error message for the missing-key case reads *"a number with no provenance is an opinion"* — an empty source is exactly that. `boards.py:238-240` does check `role["note"].strip()`, so the author applied the rule in one library and not the other.

**38. `skills/spark-design/references/verified-parts.md:22-32` carries the full XIAO pin map in prose**, duplicating `boards/xiao-esp32-c6.json`. `boards/README.md` opens by saying the library exists because *"that knowledge was in six places… six copies of a fact are five chances to be wrong."* Nothing compares the two; `check_vendor_pins.py` validates the JSON against the vendor, never the markdown. `spark-design` reads the markdown.

**39. One `verified: true` section with no provenance:** `verified-parts.md` "Prototyping module picks" — the heading claims "verified from vendor wikis" and its subsections repeat `verified: true`, but several entries carry no URL or datasheet. Everything else in that file has a `provenance:` line.

---

## Cross-tool inconsistency (accidental, not meaningful)

- **`--json` shapes:** `{"tool","results"}` (check_all) · `{"tool","status","findings"}` (check_footprints) · `{"tool","status","design","findings"}` (check_physics) · `{"tool","status","design","checked","problems"}` with *object* problems (compare_design) · **a bare list, no wrapper** (check_vendor_pins) · `{"tool","board","assignments","free"}` **with no `status` at all** (assign_pins) · `{"name","value","unit",...}` **with no tool and no status** (bench_sim).
- **Status vocabulary:** everything says `problems` except `check_vendor_pins`, which says `mismatch`.
- **No `--json` at all:** `check_design.py`, `check_bom.py`, `boards.py`, `emit_board.py` — including the two the skills actually invoke.
- **`--json` accepted and ignored:** `parts.py --list --json`, `--show X --json`, `--validate --json` all print prose and exit 0; `--signals` prints JSON whether you ask or not.
- **Only two exit codes** (no could-not-run) in `check_design.py`, `parts.py` and `boards.py` — so "this project does not exist" and "this file is invalid" are the same answer.
- **Four different ways to find the project:** `boards.project_root()` (walks up for `boards/active.json` **or** `.spark/`) · `findings.project_root()` (walks up for `.spark/` only) · `check_physics.py:363` and `compare_design.py:287` (`circuit.parent.parent.parent/.spark/rules.json`, i.e. the build output *must* be at `dist/board/`) · `check_vendor_pins.py:108` (`board file/../../.spark/cache`).

## Project assumptions a second repo hits

`emit_board.RAIL_NETS` hard-codes `MOTOR6V` and `SPEAKER` (`emit_board.py:48`) — a 12 V design gets a net called `MOTOR6V`, and `tests/test_emit_board.py:72,104` assert that string. `boards.py`'s usage text says `python3 tools/boards.py` (a path that exists only in the sibling project) and `FORBIDDEN_KEYS` points at `mcu-pins.ts` and `config.WAKE_ON_HIGH` (`boards.py:5-11,74,77-78`). `hooks/hooks.json` runs the *project's* `make check` and nothing of the plugin's own, so its README claim about catching drift "in seconds" is true only for a project that already has that Makefile. `check_physics`/`compare_design` default their rules file relative to `dist/board/`. `boards/README.md` step 4 says `python3 tools/boards.py --validate`.

## Two things worth noting about the evals

`deep-sleep-pins` and `testing-without-hardware` use `runs: 1` — the README and `BACKLOG.md` rung 3 both say results are "a rate over *n* runs"; one run is not a rate. And no case has a `tool_used` grader on the skill or on `check_all.py`, which `BACKLOG.md` §4b identifies as *the* thing that needs grading ("that is the thing that varies and the thing the plugin controls"). All four cases still grade answer quality, which the same section concludes measures the model rather than the product.
