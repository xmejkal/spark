# Round 3: simplicity and consistency critic

## (a) Added before a second case needs it

1. **MCP Adapter seam** (2.5 row "a tool's MCP version", criterion 6). `data/tools.json` has 4 `kind: mcp` rows, but
   only Claude Code reads them. A seam test needs an MCP client. Fix: delete the 2.5 row and the criterion 6 item.
2. **New Renderer seam test** (criterion 6). `WIRING_VIEWS` and `DRAWING_RENDERERS` already have two members. Fix: drop it.
3. **The `firmware` key and the "no MCU" row** (2.5). Fix: keep one line, "`PLATFORMS` gains a key with the second
   platform", and drop the no-MCU row until a board without an MCU exists.
4. **Measure columns that stay 0 until v0.13** (5.4: `in package`, `doors on run_door`, `envelope`). Fix: slice 1a
   adds only `baseline` and `mock.patch`. Each other column enters in the slice that first moves it.
5. **Two headline measures** (5.4). Fix: one headline, "baseline N". The Miro table waits for v0.13.
6. **S8's "No `MagicMock` in new tests".** No test file uses `MagicMock` today (0 files). Fix: drop that sentence.

## (b) One word used two ways, or two words for one thing

| Term | Clash | Fix |
|---|---|---|
| exit status / exit code | design.md:318 says "exit status". agents.md says "exit code" 9 times (8, 121, 350, 367, 468, 492, 494). developing.md:206 uses "exit" | Keep "exit status" and edit agents.md in the same PR. "code" then means only the envelope code |
| outcome / status / verdict | design.md:317 outcome. Envelope key `status` (agents.md:350). `verdict` in look's `data` (agents.md:472, 477) | Vocabulary row: "outcome, printed as `status`". Name `verdict` as a later rename |
| library | design.md:308 means the record folders. AGENTS.md "library module", developing.md:225, and measure.py's kind `library` mean a module | Rename the module kind to "module" in measure.py and developing.md:225 |
| step | `outcomes.step` (2.4), `BuildStep` (2.3), breadboard `steps` | Rename `BuildStep` to `BuildStage`, since 2.3 already says "one per stage" |
| check | design.md:316 says a check is a deterministic test. Slice 1b's `ArchitectureCheck` is a test class, not a `Check` | Name it `ArchitectureRules` |
| gate | design.md:325 means consent. 5.3 line 371 "Gate:" means merge criteria | Rename 5.3's "Gate:" to "Done when:" |
| Error scope | developing.md:237 and :278 say "deploy area only". S7 says all of `spark/` | The PR edits both developing.md lines |
| Value | It is a role word (design.md:302) and a row again in 4 (line 326) | Delete the 4 row |

## (c) Inconsistencies

1. The top summary says each script "keeps its name, flags and output". But slice 2 adds `--describe`, slice 3 adds `code`,
   and D9 turns a crash (today a traceback, exit 1) into exit 2. Fix: "keeps its name and flags. Output only gains
   keys, and a crash exits 2."
2. Criterion 1 says the baseline ends with S8 entries only. S1 and S6 have scope "all", so this includes `tests/`.
   That is 482 test classes with no role word, and test modules up to 2544 lines. Fix: S1 and S6 scope `scripts/`.
3. D9 says "area subclasses". S7 says "every exception subclasses `SparkError`". Fix: S7 adds "directly or through
   its area's Error".

## (d) Rules that need judgment

- S3 needs a reviewer to decide what "touches a process, clock, network or environment" means. Fix: an AST rule. Inside
  `spark/`, only modules that hold an Adapter may call `subprocess`, `time.time`, `urllib` or `os.environ`.
- S13 needs judgment too. Fix: keep only "a base class has two subclasses or a Fake in `tests/fakes.py`", and check
  it in the AST test. Drop "a pure calculation stays a function". developing.md already says it.
- S10's "golden contract test per Operation" names no file. Fix: one entry per Operation `name` in
  `tests/test_json_contracts.py`, checked by name.

## (e) Area count: 10 can be 8

Line counts per area: parts about 3200, design 2050, checks 1960, bench 1900, breadboard 1700, records 1300,
build 754, setup about 600, simulation 454, firmware 385.

- **Merge firmware and simulation into `firmware`** (840 lines). This removes the edge from sim to firmware. It
  also makes two steps unneeded: the `project_image` placement (2.1) and moving `DeployError` to break a loop.
- **Merge setup into build** (about 1350 lines). Both are top-level flows.
- Fix: 8 areas, 5.4's "of 8", and the move order "bench, breadboard, firmware, checks, design with build, records
  and parts".

## (f) A newcomer's first change

1. Today a change is one file. After the design, a door, `operations.py`, a Service and a golden are four. Fix: in
   developing.md, add a five-line "add a flag" example next to the role table.
2. `tool_finder` is in `records`, and tool install is in `setup`. A tool's code then sits in two areas. Fix: put both
   in `records` as `tools`, or say so in 2.5's tool row.
