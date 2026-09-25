# Claims audit — 2026-09-25

**Observer:** a session whose only job was to test what the plugin says about itself. Read-only on
the plugin; the only file written is this one.

**What was audited:** every assertion the plugin makes about its own behaviour, harvested from
`README.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, all four
`skills/*/SKILL.md` (frontmatter *and* body), both `commands/*.md`, `agents/design-reviewer.md`,
all fifteen script module docstrings, `BACKLOG.md` §4d and `boards/README.md`.

**State audited:** `10eea53` (the tree moved twice during the audit: `b32422a` → `10eea53`; the
test count and `plugin validate` were re-run against `10eea53` and did not change).

**Method:** every claim was tested by running something. Three environments, deliberately:

1. the plugin repo itself;
2. the author's reference project `~/Development/smartbin-local`;
3. fresh temporary directories with nothing in them, to separate "the tool works" from "the
   author's machine works". A copy of the whole plugin was also run from a directory with no
   `smartbin-local` sibling.

A claim that could not be tested by running something is recorded as `untestable`, which is
itself a finding.

**Verdicts used:** `false` (the tool does not do this), `stale` (it did once; the sentence was
not updated), `misleading` (literally defensible, reads as more than it is), `untestable`,
`true`.

---

## 1. False

### F1 — `tsci build` does not compile what `emit_board.py` emits

> "`scripts/emit_board.py` closes it. `{"board": "firebeetle2-esp32s3", "parts": [...]}` produces a
> `board.tsx` that `tsci build` compiles, that routes, and that passes the buildability check out
> of the box" — `BACKLOG.md` §4d / S5
>
> "So the output is a starting point that BUILDS and can be checked, not a finished board."
> — `scripts/emit_board.py` docstring

Reproduced four ways. It fails all four.

**(a) The documented input is refused outright.** The exact parts list §4d names:

```
$ cat requirements.json
{"board": "firebeetle2-esp32s3", "parts": ["l9110s-module", "vl6180x-breakout", "dfr0534-module"]}
$ emit_board.py requirements.json > board.tsx
no outline recorded for: VL6180X time-of-flight rangefinder breakout
  Every placement below would be arranged around an invented size...
EXIT=2   (board.tsx: 0 lines)
```

`vl6180x-breakout` is the only library part with no `body_mm`, and it is in §4d's own example.
Two claims in the same document contradict each other: S5 says this input "is enough input";
§4d says "a part nobody measured makes the generator refuse". The refusal is the true behaviour.

**(b) With `--assume-missing-sizes`, the emitted file imports a file the plugin does not ship.**
Line 1 of the output is `import { FireBeetle2Esp32S3 } from "./FireBeetle2Esp32S3"`
(`emit_board.py:201` interpolates `physical.footprint_export`). `find . -iname '*FireBeetle*'` in
the plugin returns two JSON/header files and no `.tsx`. The file exists at
`/Users/petr/Development/smartbin-local/FireBeetle2Esp32S3.tsx` and nowhere else.

```
$ tsci build board.tsx
error: Cannot find module './FireBeetle2Esp32S3' from '.../board.tsx'
  Circuits  0 passed 1 failed
Build exiting with code 1
```

**(c) With the author's own footprint file copied in, it still fails and does not route.**

```
  Circuits  0 passed 1 failed
Build exiting with code 1: circuit build errors occurred
```

`dist/board/circuit.json`: **0 `pcb_trace` elements**, 8 `pcb_port_not_connected_error`,
6 `pcb_trace_missing_error`.

**(d) The one-part minimum fails too.** `{"parts": ["l9110s-module"]}` → `Circuits 0 passed 1 failed`.

**Why nothing caught this:** `grep -rn tsci tests/` returns four comments and zero invocations.
No test in the 298 has ever run the build this claim is about. `tests/test_emit_board.py:226`
records the routing observation in a *comment* ("nets the build refused to route were exactly
the three the generator had named") — a human's note, not an assertion.

To its credit the generator *predicts* the failure on stderr ("nothing sources net.MOTOR6V —
… that net has one member and the board will not route"). The tool is honest; the BACKLOG
sentence about it is not.

### F2 — the "all checks skipped exits non-zero" guard cannot fire through the documented door

> "**With one exception, and it overturns the simpler rule above.** If EVERY check was skipped, the
> run exits non-zero as well. 'I asked for nothing and was told everything is fine' is the cleanest
> form of the failure this file exists to prevent" — `scripts/check_all.py` docstring

The guard exists (`verdict()`, `all(r["status"] == SKIPPED ...)`) and is unit-tested against a
synthetic result list. It cannot fire in `--project` mode, because the vendor-truth check always
finds the **plugin's own** shipped board library and therefore is never skipped:

```
$ mkdir empty && cd empty && check_all.py --project .
    boards       2 definition(s): firebeetle2-esp32s3, xiao-esp32-c6
  [ok  ] vendor-truth       the board definition matches the vendor's own pin header
  [--  ] buildability ... [--] the-order ... [--] physics ... [--] rules-vs-netlist ...
  [--  ] firmware-vs-board ... [--] pin-capability
  6 not asked for: ...
  nothing found by the 1 check(s) that completed, of 7
EXIT=0
```

An empty directory gets a tick and exit 0. This is the same shape as the defect §4d says was
fixed — verified in the one environment where things work, tested at the function and not
through the door.

### F3 — an empty design examines nothing, reports `ok`, exits 0

> "an empty netlist, everywhere | four checks examined nothing, found nothing, and reported `ok`"
> — `BACKLOG.md` §4d, listed as **found and fixed**

The fix (`circuit_of()`, `check_all.py:118-125`) guards the checks that read `circuit.json`.
`PinCapability` — the flagship — has no such guard.

```
$ echo '{"board":"firebeetle2-esp32s3","parts":[]}' > empty.design.json
$ check_all.py --project .
    design       empty.design.json
  [ok  ] vendor-truth       ...
  [ok  ] pin-capability     every pin can do what it is being asked to do
  nothing found by the 2 check(s) that completed, of 7
EXIT=0
```

Directly, too — and a design file with **no `parts` key at all** behaves identically:

```
$ check_design.py empty.json
empty.json: 0 parts against DFRobot FireBeetle 2 ESP32-S3
nothing to fix.
EXIT=0
$ echo '{"board":"firebeetle2-esp32s3"}' > noparts.json && check_design.py noparts.json
noparts.json: 0 parts against DFRobot FireBeetle 2 ESP32-S3
nothing to fix.
EXIT=0
```

### F4 — "Every one … takes `--json`" — 5 of 15 do not

> "Every one runs standalone, takes `--json`, and is what the skills above actually call."
> — `README.md`, Scripts

```
$ for s in scripts/*.py; do grep -q '"--json"' "$s" && echo "yes $s" || echo "NO  $s"; done
NO  scripts/boards.py
NO  scripts/check_bom.py
NO  scripts/check_design.py
NO  scripts/emit_board.py
NO  scripts/init_project.py
```

The worst of the five is the flagship. `check_design.py` has no `--json` flag, so the flag is
consumed as the positional design filename:

```
$ python3 scripts/check_design.py --json
no design at --json
EXIT=1
```

A caller that is not a person, given the flag the README promises, gets a failure about a file
called `--json`.

The second half — "is what the skills above actually call" — is false for three scripts that no
skill, command or agent references at all: `emit_board.py`, `assign_pins.py`, `bench_sim.py`.
(The `check_*` ones are reached via `check_all`; these three are reached by nothing.) `spark-design`,
the skill whose description says it produces tscircuit code, never mentions the generator that
produces tscircuit code.

### F5 — "Every tool reports four outcomes, not two" — one tool does

> "Every tool reports four outcomes, not two: `ok`, `problems`, `could-not-run` … and `skipped`"
> — `README.md`, "The one rule everything here is built around"

Only `check_all.py` implements all four; `SKIPPED` appears in no other script. `check_design.py`,
`boards.py`, `parts.py` and `bench_sim.py` have no `could-not-run` concept at all. `check_design.py`
returns exit 1 both for "the design is wrong" and for "I could not load the board":

```
$ check_design.py nb.json           # names a board that does not exist
no board definition for 'no-such-board'.
EXIT=1
$ check_design.py bad.design.json   # a real design with three real defects
3 problem(s): ...
EXIT=1
```

Those are the two outcomes the README's central rule says must never be conflated, conflated in
the plugin's headline check.

### F6 — the install instructions do not work for anyone but the author

> ```
> /plugin marketplace add xmejkal/spark
> /plugin install spark
> ```
> — `README.md`, Install

```
$ gh repo view xmejkal/spark --json visibility
{"visibility":"PRIVATE", ...}
$ GIT_TERMINAL_PROMPT=0 git clone https://github.com/xmejkal/spark.git
remote: Repository not found.
fatal: Authentication failed for 'https://github.com/xmejkal/spark.git/'
```

### F7 — the "only tool that looks outside" does not look outside through the documented door

> "`check_vendor_pins.py` — re-derives the pin map from the vendor's own `pins_arduino.h`. **The
> only tool here that consults something outside both the design and the model.**" — `README.md`
>
> "| vendor-truth | the pin map, re-derived from the vendor's own header |" — `spark-review` SKILL

`check_all.py:193` hardcodes `offline=True`. Run the documented command with the GitHub CLI
removed from `PATH` entirely and it still reports a tick:

```
$ env PATH=/usr/bin:/bin check_all.py --project ~/Development/smartbin-local
  [ok  ] vendor-truth       the board definition matches the vendor's own pin header
```

What it compared against was `<project>/.spark/cache/dfrobot_firebeetle2_esp32s3.pins_arduino.h`
— a file checked into the repo. The line a reader takes away ("matches the vendor's own pin
header") is, in every `check_all` run, a statement about a local cache.

Standalone, with `gh` present, it genuinely does fetch — so the claim is true of the script and
false of the product.

### F8 — a second project's own parts are invisible to `parts.py`'s own commands

> "`parts/` holds module definitions. Both are small and both are extensible: a project's own
> file of the same name wins" — `README.md`, Libraries
>
> "parts a second project can add | **0** (the flag was unreachable) | any" — `BACKLOG.md` §4d

`boards.py` walks up to find the project by itself. `parts.py` does not, and says the part does
not exist:

```
$ ls parts/            # standing inside the project
my-own-part.json
$ parts.py --list
  dfr0534-module ... l9110s-module ... max98357a-dfr0954 ... vl6180x-breakout      (4, all "library")
$ parts.py --show my-own-part
parts.py: no part called 'my-own-part'.
  available: dfr0534-module, l9110s-module, max98357a-dfr0954, vl6180x-breakout
$ parts.py --validate
  (validates the 4 library parts; the project's own part is not validated)
$ parts.py --list --project .
  my-own-part            motor-driver     project   My Own Part      ← only with the explicit flag
```

`emit_board.py` *does* find it, so the override is real; the library's own inspection and
validation commands are the ones that cannot see it. The practical cost lands on the fab gate
(see I2/T5).

---

## 2. True only in this repository, or on this machine

### T1 — `check_vendor_pins.py` needs an authenticated `gh`, declared nowhere

`fetch_variant_header` shells out to `gh api` (`check_vendor_pins.py:56-59`). The README's
"Toolchain the skills call" lists Node, tsci, KiCad, Wokwi and a Raspberry Pi — not the GitHub
CLI. Without it the script dies with a raw traceback, not the `could-not-run` its own docstring
promises:

```
$ env PATH=/usr/bin:/bin python3 scripts/check_vendor_pins.py boards/firebeetle2-esp32s3.json
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'gh'
EXIT=1
```

### T2 — vendor-truth cannot run in a new project at all

The cache path is `board_file.parent.parent/.spark/cache/<variant>.pins_arduino.h`. A fresh
project with its own board definition:

```
  [????] vendor-truth       the board definition matches the vendor's own pin header
           ! my-own-board: --offline but no cached header at .spark/cache/XIAO_ESP32C6.pins_arduino.h
  nothing completed. This says nothing about the board.
EXIT=2
```

This is the honest outcome, and it means the plugin's only outside-the-design check is
unavailable to every project that is not this one or `smartbin-local`.

### T3 — the hook is a no-op everywhere except `smartbin-local`

> "`hooks/hooks.json` runs `make check` after a design file is edited, if the project has a
> Makefile with a `check` target — so drift … surfaces in seconds" — `README.md`

The plugin ships no `Makefile` (`ls Makefile` → No such file), and `/spark:init` writes
`.spark/rules.json`, `.spark/project.json` and `boards/active.json` — no Makefile. So the hook
fires the *project's* target or nothing. Additionally the `case` glob only matches a string that
*ends* in `.tsx`, so the hook silently does nothing when more than one path is edited:

```
$ CLAUDE_FILE_PATHS="board.tsx"          sh -c '<the hook, verbatim>'   → MAKE CHECK RAN
$ CLAUDE_FILE_PATHS="board.tsx other.md" sh -c '<the hook, verbatim>'   → (silent), exit 0
```

### T4 — the generated board file points at the author's footprint

See F1(b). `emit_board.py` writes `import { <footprint_export> } from "./<footprint_export>"`
unconditionally. The plugin ships no footprint file for either of its two boards.

### T5 — the fab gate only runs for the four library parts

> "```parts.py --unverified <every part on the board>```" — `spark-review`, "Before fabrication, the gate"

```
$ parts.py --unverified totally-made-up-part
parts.py: no part called 'totally-made-up-part'.
EXIT=1
```

It errors rather than silently passing — good — but the effect is that the gate cannot be run on
any board built from parts outside the shipped four. There is also nothing that derives "every
part on the board" from a `circuit.json` or a design file; the model has to produce the list by
hand, which makes the one gate the skill calls non-optional depend entirely on the model not
forgetting a part.

### T6 — 2 of the 298 tests are the ones that touch a real board, and they skip away from here

`tests/test_check_firmware.py:135` and `tests/test_findings.py:289` read
`ROOT.parent / "smartbin-local" / …`. Copied to a directory with no sibling:

```
$ python3 -m unittest discover -s tests -t tests
Ran 298 tests in 0.089s
OK (skipped=2)
   test_the_real_board_and_its_firmware_agree ... skipped 'no real firmware available to read'
   A real export produces anchors of every kind, and only real ones. ... skipped 'no real design available to read'
```

`OK (skipped=2)` reads as a pass. The suite whose governing rule is "a check that could not look
must never read as a check that passed" has exactly that shape in the two places where it tests
against something real.

### T7 — `boards/README.md` is documentation for the sibling project, shipped as plugin documentation

Its "Switching board" recipe ends in `make check`; step 4 is `python3 tools/boards.py --validate`;
step 5 is "Rework `config.py`'s pin assignments"; step 6 is "Swap the footprint in `board.tsx` …
`make` refuses to export gerbers"; and "Make, the firmware's spec generator and the simulator's
diagram generator all read that single file". None of `Makefile`, `tools/`, `config.py`,
`board.tsx`, a spec generator or a diagram generator exists in the plugin or is created by
`/spark:init`. A first-time user following this file is following instructions for a repository
they do not have.

### T8 — the "complete worked example" is the superseded board

`examples/smartbin.design.json` — "a complete worked example — a real bin with seven modules"
(`commands/check.md`) — is `"board": "xiao-esp32-c6"`. Seven parts: confirmed. Every other
document, including `commands/check.md`'s own inline example three paragraphs earlier, leads with
`firebeetle2-esp32s3`.

### T9 — two things are called "the verified-parts library"

`spark-design` step 2 says "Resolve every part from the verified-parts library first. Read
`references/verified-parts.md`." That file lists the XIAO ESP32-C6, TB6612FNG, MAX98357A,
SSD1306 OLED, RZ7899/TA6586 and a generic IR module. It never mentions `parts/*.json` or
`parts.py`. The README's "Libraries" section means the *other* one. The two disagree about the
project's own history: the markdown library leads with the two parts (`XIAO`, `TB6612`) that the
reference project superseded, and carries an OLED the project says it never had. A model following
`spark-design` literally will not see the JSON parts library, `needs`, or the `verified` flags
that the README calls the backbone of the whole data rule.

---

## 3. Stale

| where | sentence | what is true now |
| --- | --- | --- |
| `README.md:152` | "265 of them" | `Ran 298 tests … OK`. `BACKLOG.md` §4d already says 298. |
| `check_all.py` docstring | "the command in `spark-review`'s own skill leaves two of these seven permanently unasked" / "(That skill's command is still wrong and this does not fix it…)" | The skill now runs `check_all.py --project .`, which asks all seven. With a design file present, `pin-capability` runs (proved in F3). The docstring describes a skill version that no longer exists — and does so in the file that is supposed to be the authority on how many checks ran. |
| `boards/README.md:61`, `scripts/boards.py:5-11` (7×), `boards/*.json` `//vendor` | `python3 tools/boards.py …`, `tools/../check_vendor_pins.py` | `tools/` exists in neither the plugin nor `smartbin-local`. Already reported in `docs/audit-2026-09-24/first-time-user.md:98`; reproduced unchanged a day later. |
| `vendor-knowledge.md:40` | "## Ingest → verified-parts entry (both vendors)" | The file covers Espressif, DFRobot, Seeed and "other maker vendors"; `plugin.json` advertises three. |
| `skills/spark-simulate/references/` | — | `keeping-things-in-sync.md` is never referenced from `SKILL.md`. It is the only orphan reference file across all four skills. |

---

## 4. Misleading, or unfalsifiable as written

**U1 — `design-reviewer.md`'s mechanism argument.** "The rule below used to be prose against a
toolset that could break it, and a prompt is the weaker of the two mechanisms — it is the one a
model talks itself out of." Removing `Glob`/`WebFetch`/`WebSearch` is real. But the rule being
defended — "Do not read README files, handover notes, status documents, or design-rationale
documents" — is still enforced by prose alone: `Read` opens any absolute path, and the caller
hands the reviewer paths. The paragraph reads as "this is now structurally enforced"; what
changed is discovery, not enforcement.

**U2 — `plugin.json`: "AI electronics design."** and "a photo-to-schematic reverse-engineering
procedure". A procedure is prose for a model. Nothing runs; no test, eval or script exercises
`spark-reverse-engineer` at all. Its description ("Fuses copper-trace reading, datasheet pinouts,
and functional reasoning") cannot be contradicted by any command. Not false — untestable.

**U3 — `spark-design`: "grades it against design rules and a verified-parts library."** "Grades"
names no score, no output format and no exit code. The step is a model reading a markdown
checklist. Contrast the README's own standard for the deterministic half ("a script runs in a
second, costs nothing, cannot change its mind").

**U4 — `README.md`: "The reasoning half is here too, and it is useful."** The README itself then
says the reviewer half is "plausible and unproven rather than measured". The two sentences are in
the same document; the first is the one that reads as a claim.

**U5 — "a fact carries a source and whether anyone checked it" (`README.md`).** True of
`parts/*.json` `facts` and of `boards/*.json` `power.*`. Not true of the pin map, which is the
most consequential data in the plugin: `"pins": {"D2": 3, "D3": 38, …}` — bare integers under one
file-level `sources` block. The rule runs through *some* of the data.

**U6 — `assign_pins.py`: the refusal "naming the signal, what it needed, and which pins could have
served it and why each is taken."** It names the signal, the need and the candidate pins. It does
not say what each is taken by:

```
ADC10 needs adc. 10 pin(s) could have served it — A0, A1, A2, A3, A4, D5, D7, SCL, SDA, SS —
and every one is already taken.
```

Small, but it is the difference between a refusal you can act on and one you cannot. (Separately:
`assign_pins.py` raises an unhandled `KeyError: 'name'` on a signals file with a differently-named
key — no `could-not-run`.)

---

## 5. Instructions that do not work if followed literally

I followed each document top to bottom in a scratch directory. Where I stopped:

**I1 — `/spark:init`, step 1. Stops immediately.**

> ## 1. Which board
> ```
> ${CLAUDE_PLUGIN_ROOT}/scripts/boards.py --list
> ```

```
$ mkdir fresh && cd fresh && boards.py --list
boards.py: no project here: nothing up from …/fresh holds boards/active.json or .spark/
EXIT=1
$ boards.py --list --project .
boards.py: no board selection at …/fresh/boards/active.json
EXIT=1
```

The first step of the command whose stated job is to write `boards/active.json` requires
`boards/active.json` to already exist. Steps 2–4 all work once you skip step 1. `commands/check.md`
inherits the same dead end ("`board` is either an id from the library (`boards.py --list`)").

**I2 — `spark-review`: half the fab gate is outside the skill's own `allowed-tools`.**

```
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/findings.py *),
               Bash(${CLAUDE_PLUGIN_ROOT}/scripts/check_all.py *)
```

The body mandates `make` or `tsci build` (step 1), and the gate is:

```
${CLAUDE_PLUGIN_ROOT}/scripts/boards.py --validate --for-fab
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --unverified <every part on the board>
```

Neither `boards.py` nor `parts.py` is allowed. The skill's own words about the gate — "Neither is
advisory" — sit on two commands the skill did not grant itself.

**I3 — `spark-review`, step 1, in a project that has been built but not initialised.**

```
$ findings.py anchors
no .spark/ directory here or above … Run `/spark:init`, or the script behind it …
EXIT=2
```

Good error message; the skill never says `/spark:init` is a prerequisite. Step 1 says only "Build
it … before reviewing anything".

**I4 — `spark-review`, step 2, read literally, overstates what ran.** The step is correct and the
resolution block is genuinely printed first (verified). But the description says "Runs every
deterministic check", and what you get depends entirely on what the project contains: 6 of 7 in
`smartbin-local`, 2 of 7 with only a design, 1 of 7 in a freshly initialised project. See §6.

Everything else in the four skills and two commands that can be executed, was, and worked:
`init_project.py`, `check_design.py`, `check_all.py --project .`, `findings.py anchors/append/
list/status/measure/validate/next`, `boards.py --validate --for-fab`, `parts.py --unverified`.

---

## 6. The numbers in §4d

| claim | verdict | evidence |
| --- | --- | --- |
| "298 tests" | **true** | `Ran 298 tests in 0.083s / OK`. From a directory with no sibling: `OK (skipped=2)` — see T6. |
| "`claude plugin validate` passes" | **true** | passes, and passes `--strict`, for `.`, `./skills`, `./agents`, `./commands`. Note: pointed at the repo root it validates the *marketplace manifest* only. |
| "4 skills, 2 commands, 1 agent, 15 scripts, 2 boards, 4 parts" | **true** | all six counted directly. |
| "scripts a fresh install can run: **0 of 14** (all mode 100644) → 15, all `100755`" | **true, flattering "before"** | `git ls-tree -r d360f05^ \| grep scripts/` → exactly 14 blobs, all `100644`; today 15, all `100755`. But the table is headed *"before and after two days"*, and that state existed for **two hours**: the scripts were written 2026-09-24 18:30–20:23 and chmod'd at 20:29 the same evening. Two days before (2026-09-23) the repo contained **one** script, `check_pins.py`, also `100644`. "0 … can run" also overstates the defect: `python3 scripts/x.py` works fine at 100644; what breaks is the `${CLAUDE_PLUGIN_ROOT}/scripts/x.py` form the skills use. |
| "checks the documented review command runs: **3 of 7** → **6 of 7**" | **true of one project only** | Reproduced exactly in `smartbin-local`: 6 run, `pin-capability` `[--]` because that project has no design file. But the number is a property of the project, not of the command: empty dir → **1 of 7**; freshly `init`ed dir → **1 of 7**; dir with a design file → **2 of 7**. And the one still missing in the reference project is the flagship — the check `plugin.json`'s description leads with has still never run against the author's own board. |
| "skills competing for 'check my design': 3 → 1" | **true** | `git show 47a04c0^` — `spark-check` ("check the wiring… review my pin assignments"), `spark-verify` ("check the design") and `spark-review` ("check my circuit") all claimed it. Today only `spark-review`, and it names `/spark:check` as the cheaper route. |
| "parts a second project can add: **0** (the flag was unreachable) → any" | **half true** | See F8: loadable, not listable, not showable, not validatable without `--project`. |
| "`spark init`: a string inside an error message → `/spark:init`" | **true** | `commands/init.md` exists; `init_project.py --project . --board <id>` writes all three files and ends with the null list, as documented. |
| "README version vs `plugin.json`: 0.1.0 vs 0.6.0 → both 0.6.0" | **true** | both 0.6.0. (The sibling project's `CLAUDE.md` still says v0.4.0, but that is out of scope.) |
| §4d defect table: `check_footprints` "silently skipped 14 of 74 holes" — fixed | **true** | reproduced: the check now prints `[through-hole-drill, NOT EXAMINED] 4 plated hole(s)…` and `[annular-ring, NOT EXAMINED] 10 plated hole(s)…` on the reference board. |
| §4d defect table: `findings.py validate --apply` retiring findings against an empty `circuit.json` — fixed | **true** | reproduced: with `circuit.json` = `[]`, `validate --apply` exits 2 with "this refuses rather than retiring your findings", and the finding survives. |
| §4d defect table: "an empty netlist, everywhere … reported `ok`" — fixed | **partly false** | fixed for `circuit.json`; **not** fixed for the design file. See F3. |
| §4d: "the command in spark-review's own skill leaves two of seven unasked" (as a present-tense statement in `check_all.py`) | **stale** | see §3. |
| N2: "the live store is 11 blocked of 20" | **true** | `.spark/findings.json` → 20 total, `Counter({'blocked': 11, 'open': 8, 'rejected': 1})`. |
| N3: "Every case inlines its design in the prompt and none references a path on disk, so **no case can run a script**" | **true** | four cases, all `schema_version: "1.0"`, `runs:` 1, 1, 2, 3 — matching the README's "n=1–3" — and no path reference in any of them. |

---

## 7. The description fields

These are the interface a model sees. Judged on (a) does the skill do what the description says,
(b) would two of them be confused.

| skill | description accurate? | notes |
| --- | --- | --- |
| `spark-design` | **no, on two counts** | "builds it headless" — the skill tells the model to run `npx tsci build`, which is fine; but "grades it against design rules and a verified-parts library" names no mechanism (U3), and the library it points at is the markdown one, not `parts.py` (T9). It also never calls `emit_board.py`/`assign_pins.py`, the scripts that actually do "describe → tscircuit". |
| `spark-review` | **overstated** | "Runs every deterministic check" is true of the *command it issues* and false of what happens: see §6. The gate it promises ("gate it before fabrication") is two commands it has not allowed itself to run (I2). Everything about the findings store is accurate. |
| `spark-simulate` | **accurate** | Nothing in it is executable, so nothing is falsifiable — but nothing in it overclaims either, and the "honest limits" section is unusually good. One orphan reference file. |
| `spark-reverse-engineer` | **accurate, untestable** | Pure procedure. No script, test or eval touches it. |

**Do any two still overlap enough to pick wrongly?** The "check my design" collision is genuinely
gone: three descriptions claimed it, now one does, and it points at the cheaper command by name.
Two softer collisions remain:

- `spark-design` ("grades it against design rules") vs `spark-review` ("Runs every deterministic
  check"). "Design a board and make sure it's right" matches both. `spark-design` step 6 resolves
  it by handing off — but the *description*, which is what the model selects on, does not say so.
- `spark-review`'s "is about to order or fabricate a board" vs `spark-design`'s step 8 ("PCB layout
  … never fab unattended"). A user about to order will match `spark-review`, which is correct;
  worth keeping an eye on if `spark-design` ever grows its own gate.

`design-reviewer`'s description is accurate and correctly scoped ("Reviews one named dimension per
invocation"), and the agent body's two "do not report what a script already owns" sections are the
clearest boundary-setting in the plugin.

---

## 8. What I tried to break and could not

Reported so the table is not read as a verdict on the whole plugin. Each of these was tested by
mutating an input until the rule had to fire.

- **All five checks in `plugin.json`'s description reproduce.** Wake source on a non-wake pin
  (`D3/GPIO38` → named, with the 21 pins that could have served it); analogue input on a
  digital-only pin; two parts on one GPIO; **one GPIO under two silkscreen names**
  (`A4` and `SS` are both GPIO10 — caught, with the explanation); a `reads_serial` part on `TX`;
  two devices at `0x29` on one bus. Exit 1 each time.
- **All four of the README's headline promises reproduce.** Deleted one capacitor's
  `max_voltage_rating` → `[capacitor-voltage] MotorBulkCap: sits on MOTOR6V (6.4 V) with no stated
  voltage rating`. Shrank a drill to 0.5 mm → `finishes near 0.44 mm after plating … does not go
  in`. Changed `D7` to GPIO99 in a board file → `MISMATCH … D7 is GPIO99 in the board file but
  GPIO9 in the vendor's header`. Fab package vs schematic → the live `Mp3Switch is a sot23 with no
  supplier part` finding on the real board.
- **`findings.py` does everything its docstring claims.** Same dimension + anchors with completely
  different wording → `0 new, 1 already known`. A fabricated anchor → `1 refused … cites
  net:DOES_NOT_EXIST, which the design does not contain`, exit 1. Re-appending a resolved finding
  → `1 regressed`. Empty `circuit.json` → refuses to retire anything.
- **Board library.** A directory containing only `boards/active.json` resolves the full FireBeetle
  definition — **25 pins, 22 wake-capable GPIOs** — with nothing copied (S4's criterion, met). A
  project's own `boards/firebeetle2-esp32s3.json` overrides the library's (`* firebeetle2-esp32s3
  (project)`).
- **`check_firmware.py`** flags a GPIO not on the header and both strapping pins, matched on GPIO.
  **`compare_design.py`** fails a `must_not_float` rule with the net and the fix.
  **`check_physics.py`** refuses to assume a current (`needs-measurement`, not a pass) and sizes a
  trace correctly once told (`0.15 mm, good for 0.60 A at a 10 C rise`).
  **`assign_pins.py`** gives a reason per pin and refuses an unsatisfiable set.
  **`bench_sim.py`** marks everything simulated and prints the `--source simulated` command.
  **`check_footprints.py`** counts what it could not read.
- **"in a second"** — `check_all.py --project .` on the real board: **0.086 s**.

---

## 9. Summary table

| # | claim | where | verdict | one-line evidence |
| --- | --- | --- | --- | --- |
| 1 | "produces a `board.tsx` that `tsci build` compiles, that routes, and that passes the buildability check out of the box" | `BACKLOG.md` §4d/S5; `emit_board.py` docstring | **false** | documented input refused; with `--assume-missing-sizes` the emitted file imports a footprint the plugin does not ship; with it copied in, `Circuits 0 passed 1 failed`, 0 `pcb_trace`, 14 errors |
| 2 | "If EVERY check was skipped, the run exits non-zero as well" | `check_all.py` docstring | **false** | empty dir → `[ok] vendor-truth` … `nothing found by the 1 check(s) that completed`, EXIT=0 |
| 3 | "an empty netlist, everywhere … reported `ok`" — listed as fixed | `BACKLOG.md` §4d | **false (partly)** | `"parts": []` → `[ok] pin-capability`, EXIT=0; `check_design.py` alone → `nothing to fix.`, EXIT=0 |
| 4 | "Every one runs standalone, takes `--json`" | `README.md` | **false** | 5 of 15 have no `--json`; `check_design.py --json` → `no design at --json`, exit 1 |
| 5 | "and is what the skills above actually call" | `README.md` | **false** | `emit_board.py`, `assign_pins.py`, `bench_sim.py` referenced by no skill, command or agent |
| 6 | "Every tool reports four outcomes, not two" | `README.md` | **false** | only `check_all.py`; `check_design.py` returns exit 1 for both "problems" and "could not load the board" |
| 7 | `/plugin marketplace add xmejkal/spark` | `README.md` | **false** | repo is PRIVATE; anonymous clone → `Repository not found` |
| 8 | "the only tool here that consults something outside both the design and the model" | `README.md`; `spark-review` | **false via the front door** | `check_all.py:193` hardcodes `offline=True`; reports `[ok]` with `gh` removed from `PATH` |
| 9 | "a project's own file of the same name wins" (parts) | `README.md`; §4d | **false for `--list/--show/--validate`** | `parts.py --show my-own-part` → "no part called 'my-own-part'" while it sits in `./parts/` |
| 10 | "265 of them" | `README.md:152` | **stale** | `Ran 298 tests … OK` |
| 11 | "That skill's command is still wrong and this does not fix it" | `check_all.py` docstring | **stale** | the skill now runs `check_all.py --project .`, which asks all seven |
| 12 | `python3 tools/boards.py --validate` | `boards/README.md:61`; `boards.py:5-11`; both board JSONs | **stale** | no `tools/` in the plugin or in `smartbin-local`; reported 2026-09-24, unchanged |
| 13 | "Ingest → verified-parts entry (both vendors)" | `vendor-knowledge.md:40` | **stale** | the file covers four vendor families |
| 14 | `check_vendor_pins.py` works standalone | `README.md` scripts list | **true only with `gh`** | `PATH=/usr/bin:/bin` → `FileNotFoundError: 'gh'` traceback; `gh` is declared nowhere |
| 15 | vendor-truth runs in any project | `spark-review` check table | **true only here** | fresh project with own board → `[????] no cached header at .spark/cache/…` |
| 16 | hook "so drift … surfaces in seconds" | `README.md` | **true only here** | plugin ships no Makefile, `/spark:init` writes none; hook also silent for multi-path edits |
| 17 | fab gate `parts.py --unverified <every part>` | `spark-review` | **true only for 4 parts** | any other part → exit 1 "no part called X"; nothing derives the part list from the design |
| 18 | "298 tests" / the rule "a test must RUN the thing" | §4d; `README.md` | **true, with a hole** | 298 pass; the 2 that test against a real board skip off this machine and print `OK (skipped=2)` |
| 19 | `boards/README.md` as plugin documentation | `boards/README.md` | **true only here** | `make check`, `tools/`, `config.py`, `board.tsx`, "the simulator's diagram generator" — none exist in the plugin |
| 20 | "a complete worked example" | `commands/check.md` | **stale** | `examples/smartbin.design.json` is the superseded `xiao-esp32-c6` design |
| 21 | "the verified-parts library" | `README.md`; `spark-design` | **two different things** | `references/verified-parts.md` (markdown, XIAO/TB6612/OLED) vs `parts/*.json` + `parts.py`; neither mentions the other |
| 22 | `/spark:init` step 1 | `commands/init.md` | **false if followed literally** | `boards.py --list` → exit 1 "no project here" in the directory the command exists to initialise |
| 23 | `spark-review`'s `allowed-tools` | `spark-review` frontmatter | **false** | the gate's `boards.py` and `parts.py`, and step 1's `tsci build`, are not in the allowance |
| 24 | "checks the documented review command runs: 3 of 7 → 6 of 7" | §4d | **true of one project** | 6/7 in `smartbin-local`; 1/7 in a freshly `init`ed project; the missing one is the flagship |
| 25 | "scripts a fresh install can run: 0 of 14" | §4d | **true, flattering** | 14 × `100644` confirmed at `d360f05^` — a state that lasted two hours, in a table headed "after two days"; two days earlier there was one script |
| 26 | "skills competing for 'check my design': 3 → 1" | §4d | **true** | `git show 47a04c0^` — `spark-check`, `spark-verify`, `spark-review` all claimed it |
| 27 | "parts a second project can add: 0 → any" | §4d | **half true** | loadable by `emit_board.py`; invisible to `parts.py`'s own commands |
| 28 | N3: "no case can run a script" | `BACKLOG.md` | **true** | 4 cases, all `schema_version: "1.0"`, no path reference, `runs:` 1–3 |
| 29 | N2: "11 blocked of 20" | `BACKLOG.md` | **true** | `Counter({'blocked': 11, 'open': 8, 'rejected': 1})` |
| 30 | `claude plugin validate` passes | §4d | **true** | passes `--strict` for `.`, `./skills`, `./agents`, `./commands` |
| 31 | the five checks in `plugin.json`'s description | `plugin.json` | **true** | all five reproduce on mutated designs, including the two-silkscreen-names alias case |
| 32 | the four promises in the README's opening paragraph | `README.md` | **true** | each fires on a mutated input (cap rating, drill, vendor header, fab package) |
| 33 | findings store: structural identity / anchor refusal / regressed / empty-circuit guard | `findings.py`; `spark-review` | **true** | all four reproduced end to end |
| 34 | "a new directory containing only `boards/active.json` resolves the full definition — 25 pins, 22 wake-capable" | §4d/S4 | **true** | reproduced exactly, nothing copied |
| 35 | `check_footprints` counts unexamined holes | §4d; `README.md` | **true** | `[annular-ring, NOT EXAMINED] 10 plated hole(s)…` on the real board |
| 36 | "in a second" | `README.md` | **true** | 0.086 s on the reference project |
| 37 | "a prompt is the weaker of the two mechanisms" (why Glob/WebFetch were removed) | `design-reviewer.md` | **misleading** | the rule it defends ("do not read README files") is still prose-only; `Read` takes any path |
| 38 | "grades it against design rules and a verified-parts library" | `spark-design` description | **untestable** | no score, no output, no exit code; a model reading a markdown checklist |
| 39 | "a fact carries a source and whether anyone checked it" | `README.md` | **partly true** | true of `parts/*.json` facts; the pin map is bare integers under one file-level `sources` block |
| 40 | "photo-to-schematic reverse-engineering procedure" | `plugin.json`; `spark-reverse-engineer` | **untestable** | pure prose; no script, test or eval touches it |

---

## The pattern, for whoever triages this

Three of the four most serious findings (F2, F3, F7) are the **same defect the plugin was built to
prevent**, in the plugin's own instruments:

- a runner whose "I looked at nothing" guard cannot fire because one check always finds the
  plugin's own files;
- an empty *design* examined and reported `ok`, three weeks after the empty *netlist* was fixed;
- a check whose whole premise is "look outside the project", wired `offline=True` and reporting
  that it matched the vendor's header.

And the fourth (F1) is a capability claim that no test has ever executed, in a suite whose
governing rule is "a test must run the thing, not read it".

The rule holds. The instruments that enforce it were, each time, verified one layer above the
place they fail — `verdict()` tested with a synthetic list rather than a directory, the empty
guard applied to the input the author had rather than the one the check takes, the vendor fetch
proved on a machine with `gh` logged in. That is the same sentence `docs/observations/README.md`
already has: *the builder verifies in the one environment where things work.*

Per `docs/observations/README.md`, these are reviews, not facts — but every row above names the
command that produced it, and each was run in at least one environment that is not this repository.
The forty rows are numbered so they can be logged in `INDEX.md` as separable claims.
