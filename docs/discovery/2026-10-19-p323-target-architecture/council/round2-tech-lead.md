# P323 round 2: tech lead

**Verdict: ready after fixes.** F1 and F2 break the design as written. AGENTS.md settles both open
questions.

## Spot checks

1. `parts.py` `OPERATIONS` at line 1581: true.
2. `look.main(argv=None, run=subprocess.run)` at `look.py:41`: true.
3. `check_spine` imports `breadboard`, `sim_project`, `init_project`, and `init_project` imports `design`: true.
4. "`MicroPythonPlatform` subclass, `PLATFORMS[board firmware]`": not true today. `FirmwarePlatform.micropython` is a
   classmethod over lambdas, and no board record has a `firmware` key. It has `micropython_port`. See F3.

## Findings

**F1. The graph has a cycle (2.1, 2.2).** `project_image` (placed in firmware) imports `run_scenario` and
`sim_project`, and `run_scenario` imports `flash_image`. `firmware_platform` imports `DeployError` from
`project_image`. `deploy_service` (bench) imports `run_scenario`. Fix text: "`project_image` lives in `simulation`, since
the image is the one that passed the simulation. `DeployError` moves to `firmware/errors.py`. Add the edge bench to
simulation." Add `BENCH --> SIM` to the diagram. In 2.2 write "below means reachable by the arrows".

**F2. A 40-line door cannot hold `parts.py`'s 30 Operations (2.1, 2.4, D7, AC 2).** Fix text in 2.1 and 2.4: "An
area's `operations.py` holds its `OPERATIONS` tuple. A door imports that tuple and calls `run_door`." Fix the summary line to match.

**F3. The platform key does not exist (2.5, 2.7).** Fix text in 2.5: "`PLATFORMS` is keyed by the board record's
`firmware` field. The field enters with the second platform (records grow by need). Until then a record with
`micropython_port` maps to `micropython`, and a record with neither maps to no platform, which answers `skipped`."

**F4. The simulator seam has the wrong role (2.5, 2.1).** Flasher is a Strategy with an Adapter subclass, but
`SimulationEngine` is called an Adapter. It does not exist yet. Fix text: "a simulator: one `SimulationEngine`
subclass (an Adapter) of the `SimulationEngine` Strategy, one line in `ENGINES`."

**F5. The MCP switch is missing (2.5).** AGENTS.md says a setting switches a tool to its MCP version, and `tools.json`
already has `kind: mcp` rows. Add a row: "a tool's MCP version: a `kind: mcp` row for the same role and one MCP
Adapter. `tool_finder` picks the Adapter from the person's setting." Also `tools.py`
imports `boards` and `store`, so `tool_finder` cannot sit in `core` (stdlib only). Put it in `records`, or pass the
store path in.

**F6. Several MCUs contradicts the docs (D12).** `developing.md:301` and `journey.md:875` promise many boards in one
project in v0.13 (#94), this epic. Fix text in D12: "The v0.13 promise moves to P318. Edit both lines."

**F7. Acceptance criteria miss seams (AC 6).** Fix text: "a second board record, a fake `FirmwarePlatform`, a board
with no platform answering `skipped`, a new `Check`, a fake `SimulationEngine`, a tool switched to its MCP Adapter and
a new Renderer each plug in with no caller edit."

**F8. Slice 1 ships an orphan (5.2).** A `SparkError` nobody imports fails `test_orphans` once it reads `rglob`, and
breaks S13. Fix text: "Slice 1 adds no code under `spark/`. `SparkError` enters in slice 2 with `run_door`."

**F9. Names.** D9 gives `SparkError` `outcome` and `code`, the diagram adds `fix`. Pick one. "check" means a test of a
design, but `ReadyCheck` tests a board. Fix text: "check: one deterministic test that returns an answer." Section 4
lists role words but omits Result, Value, Store, Decorator and Fake. Fix text: "Role words are developing.md's table.
This table holds the domain words." Slice 2 says "under 40", AC 2 says "at most 40". Use "at most".

## Open questions, decided

1. **(b) until v0.13.** AGENTS.md: "The whole-repository change waits for v0.13, #94." STORY_MAP puts v0.11 and v0.12
   next after walk 1. So after walk 1 only the per-story pay-down runs, and a story may pull its area forward. Area moves are v0.13's work. Fix D13 and 5.3 to "after v0.12", and shrink 5.1 ("plans shrink with distance").
2. **(a) exit 2.** `docs/guide/agents.md:501` defines exit 2 as "it could not look". A crash produced no finding, and
   exit 1 tells Claude there were problems. It lands door by door, as each moves onto `run_door`. Fix text: "An unexpected exception is `could-not-run` with code `crash`, exit 2", and add
   that line to agents.md's exit table in the same PR.

## Walk 1 safety

Slice 1 is safe after F8: it touches tests, the baseline and `tools/measure.py`, no door.
