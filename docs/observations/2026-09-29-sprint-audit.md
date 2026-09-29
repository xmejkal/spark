# Sprint audit — 2026-09-29

An outside read of the sprint that closed the cold-test findings. Three questions, in the order
they were asked: does the plan score, is the code sound after nine fixes in three days, is the
backlog honest. Every claim below was run or read; the command or the line number is beside it.

**Revision.** The audit started against `7e84315` (09:40). `997b756` landed at 09:47 and six
files were modified in the working tree from 09:49 (backlog P3, the `spi` role). Line numbers
are at `7e84315` unless stated; the runs marked "pristine copy" were made on a `git archive` of
`997b756` in a scratch directory so the moving tree could not contaminate them.

---

## 1. The plan, scored against the diary

`rc-car/PLAN.md` §"What I expect to go wrong" made five predictions. `DIARY.md` holds fifteen
entries, G1–G15; G14 was reproduced and rejected, leaving fourteen valid findings.

| # | prediction | hit? | what the diary found |
| --- | --- | --- | --- |
| 1 | two boards, one project — `active.json` is the gap | **hit, three times** | G9 (`active.json` accepts a list — the predicted place), G8 (`check_all` turns green by losing its inputs — "not in the place predicted"), G10 (`init_project` picks one in silence). All three BUGs; predicted as a GAP |
| 2 | no servo / regulator / button / LED parts; tests whether the schema generalises | **hit as inventory, wrong on the interesting half** | the schema generalised without a change (diary "What WORKED"); the finding was G1 — nothing signposts the absence |
| 3 | no notion of PWM, so it is not checked | **hit, worse than predicted** | G12: a *stated* requirement refuses the whole design. BUG, not GAP |
| 4 | nothing models a link between two boards | **hit exactly** | G11 |
| 5 | the 5 V rail has no source and "`emit_board` refuses" | **miss on mechanism** | `emit_board` does not refuse an unsourced rail; it prints a `note:` and exits 0 (`emit_board.py:691-693`). What actually happened is G2: the pins on that rail were dropped without a note |

**Score: 4 of 5 by area, 0 of 5 by mechanism.** Every prediction described an absence and
assumed the tool would say "cannot". Where the tool was reached, it said "ok".

**Not predicted: 8 of 14** — G2, G3, G4, G5, G6, G7, G13, G15. Four BUGs (G2, G3, G7, G15), four
GAPs (G4, G5, G6, G13).

**The pattern, counted.** The five predictions are all derivable from the inventory without
running anything: `ls parts/` (#2), one `active.json` (#1), `CAPABILITIES = ("wake", "adc")`
(#3), the absence of any link schema (#4), the rail vocabulary (#5). The eight unpredicted
findings are all behaviours of *existing* code under a new input: a loop's `continue` (G2), a
selector's character set (G3), a field with no provenance (G4), a design decision inside a part
record (G5), a default the generator never questioned (G6), a name derived from an id (G7),
skills that describe an older product (G13), a validator that crashes on what it reports (G15).
The dividing line is not GAP versus BUG. It is *visible in the inventory* versus *visible only by
running* — and of the six findings that did land in predicted areas, four (G8, G9, G10, G12)
were BUGs predicted as GAPs. Pointing at the right place did not predict what the tool would do
there. The "less than asked, exit 0" family (G2, G7, G8, G10) splits two and two across predicted
and unpredicted areas; that class was unforeseeable from the plan whichever way it pointed.

**The plan's own definition of done, checked:**

| # | DoD | met? | evidence |
| --- | --- | --- | --- |
| 1 | both boards build, zero errors, traces > 0 | yes | `dist/car/circuit.json`: 13 `pcb_trace`, 0 errors; remote 12 / 0 (counted) |
| 2 | `check_spine` reaches `simulation` for one of them | **no** | from inside `rc-car` with the bin's tsci: build 13 / 0, then `[!!] simulation — no Wokwi part is mapped to Sg90Servo, Mp1584Buck5v, Xt30TractionInlet`, exit 1. From anywhere else it stops earlier: `no part called 'sg90-servo'` (§2, item 10) |
| 3 | `check_all` completes, could-not-run reported | yes, with `--circuit` | exit 2, `????  buildability` for the placeholder, `physics ok` |
| 4 | firmware both sides, failsafe test that fails without it | **not started** | `rc-car/` holds no firmware directory and no `.py` |
| 5 | diary records every gap | yes | |

Three of five.

---

## 2. Is the code well-architected after nine fixes?

### `emit()` and `main()` — `scripts/emit_board.py`

- `emit()` is **:403-588, 186 lines, 32 top-level statements, 39 branch nodes** (counted with
  `ast`). It builds the header, the component list, signal traces, the unclaimed block, MCU
  power, five diagnostic comment blocks, module power, the unjustified-width block, the
  placeholder block and the host-requirements block. Each is a section; none is a function.
  Too long, yes — but the length is a symptom of the next item.
- `main()` is **:591-694, 104 lines, 21 branch nodes**, with four refusal blocks of one shape
  (:635-674). **No test calls it**: `grep -rn "emit_board.main" tests/` is empty and
  `test_check_spine.py` mentions no `emit_board`. Everything in it — project resolution, the
  refusals, the rules lookup, the stderr notes — is exercised only by the diary.
- Growth: 458 lines at `21156b4` (09-25) → 698 at `7e84315` (09-29), +52 % over six fix commits
  (`git show <c>:scripts/emit_board.py | wc -l`).

### A live defect in the function nothing tests — R5 holds only with `--project`

`emit_board.py:609` resolves `project` (the flag, else `boards.project_root()`). **`:678` passes
`args.project`** — `None` when the flag is absent — to `rules_in`, which returns `{}`. Run from
inside `rc-car` exactly as the module's own docstring documents (`:5`, no `--project`):

```
$ emit_board.py car.requirements.json --board firebeetle2-esp32s3   # inside rc-car
exit 0;  trace thickness= attributes: 14 with --project . → 1 without (the board's own 1.6 mm)
"THE WIDTH OF THE TRACES ABOVE ON net.GND, net.SERVO, net.TRACTION, net.V33 IS UNJUSTIFIED"
```

while `.spark/rules.json` two directories down states 2.9 A, 1.2 A and 2.9 A. The board is
emitted unsized, exit 0, and the file blames the reader. That is the sixth instance of "the
generator emits less than it was asked and exits 0", inside the commit (`dd01824`) that closed
the fifth. The sizing tests call `emit()` with a rules dict (`test_emit_board.py:229-232`);
`rules_in`, `trace_width_mm` and `power_trace` have no test of their own; the mutation
"generator stops sizing traces" (`tests/mutations/sprint-2.json`) replaces `trace_width_mm`'s
return, which the `_emit` tests catch — `:678` is outside its reach.

### Rules written at more than one use site

1. **`parts.py:191-195` and `:304-305`** both report a `power` entry without `pin`. Reproduced:
   one malformation, two problems (`"power[0] has no pin, so nothing can say where it connects"`
   and `"power[0] has no pin"`). `git show 3b5f38f -- scripts/parts.py` added the first and left
   the second. The commit message says "fixed at the cause"; the use-site copy survived — the
   patch-not-audit pattern inside the commit that names it.
2. **`parts.py:120`, `:200`, `:260`** — `("needs", "power", "unused_pins")` three times, no
   constant. G15 was precisely about which lists hold pins.
3. **`emit_board.py:359-362`, `:387-390`, `:551-555`** — `for part / for power /
   net = net_for(power) / if not net: continue`, three times; `:96-98` is a fourth walk of the
   same list.
4. **`emit_board.py:299-300` and `:567-568`** — the placeholder filter, twice.
5. **`emit_board.py:614-618` and `check_all.py:206-210`** — load the part, tag `_instance`. Two
   modules. `check_all.py:185-190` says it uses "the GENERATOR's own functions" so the checker is
   not "a second derivation"; the loading step *is* a second derivation, and `:212-213`
   `except Exception: return ()` turns any drift into "measure every placeholder" in silence —
   the exact escape backlog R6 records ("the wiring passes nothing through").
6. **`check_all.py:173-175` and `:222-224`** — identical `of(severity)` closures.
7. **`check_all.py:308` and `init_project.py:42`** — the circuit glob pair in two files. G10's
   fix made both refuse two matches; neither knows the other's list exists.
8. **`emit_board.py:518-520`** — the MCU `power_pads` loop keeps the `if not net: continue` that
   G2 removed for parts. Low risk (the board file is spark's own), same shape.
9. **`emit_board.py:607`** reads the requirements JSON outside the `try`; **`:270`** reads
   `entry["part"]`; **`check_spine.py:322`** the same as `:607`. Reproduced: three raw
   tracebacks, exit 1 — which in a three-valued tool means "problems found". INDEX row M2
   raised this for `check_spine` on 09-25; unchanged. `c1537b2` fixed it in `emit_footprint` only.
10. **`check_spine.py:177`** resolves the project from `cwd`; **`:328` + `:80-93`** resolve the
    toolchain from the requirements file's directory. One script, two rules for "where is the
    context". Reproduced: `check_spine.py <abs>/car.requirements.json` from outside `rc-car` →
    `[????] schematic  cannot emit a board: no part called 'sg90-servo'`; from inside → builds.

### Two modules sharing a concern

- `emit_board.main` ↔ `check_all.placeholder_components_in` (item 5) — should be one function.
- `check_all.CONVENTIONS` ↔ `init_project.CIRCUIT_PATHS` (item 7).
- `copper` ↔ `check_physics` — correctly shared now: `grep "0.048\|0.725" check_physics.py` finds
  nothing outside `copper.py`. This is the refactor done right, and it is the one the diary
  praised itself for.

### `importlib.util.spec_from_file_location`

`check_all.py:56-61` `load()` — nine call sites (`:147, :159, :169, :201, :202, :218, :234,
:251, :264, :356`) — and `check_physics.py:45-50` `_sibling` (`:57`) load siblings by file path.
Eight scripts do `sys.path.insert(0, SCRIPTS)` + a plain import, **including `check_physics.py`
itself at `:40-42`**, three lines above its `_sibling`. `load()` never registers in
`sys.modules`; verified in one process:

```
load("parts") registered in sys.modules:            False
load("parts") is the parts emit_board imports:       False
PartError classes identical:                         False
```

Two `parts` modules, two `PartError` classes. The justification at `check_all.py:57` — "so this
file is the only place they are named" — is served equally by `import check_design`.
`copper.py:9-11` argues against the pattern in its own docstring. All ten sites could be plain
imports.

### Functions with no test

By name over `tests/`, then read to rule out indirect coverage:

| module | untested | note |
| --- | --- | --- |
| `emit_board` | `main`, `rules_in`, `trace_width_mm`, `power_trace`, `has_an_outline`, `parts_without_an_outline`, `parts_without_a_footprint` | no test asserts "no footprint recorded" or "no outline recorded"; the defect above lives in `main` |
| `parts` | `search_path` | trivial. `_show` IS tested (`test_parts.py:370, 374`) — a first grep missed it |
| `check_all` | none that matters | `circuit_of`, `findings_result` and the five `Check` subclasses are unnamed in tests but driven by `test_every_check_in_the_runner_has_a_case_here` (`:163`) |
| `copper` | none | all five functions, 17 tests |

**Test count.** `python3 -m unittest discover -s tests` → **458 OK** at `7e84315` (start of
audit); **472 OK, 2 skipped** at `997b756` (pristine copy). The `tail -3` in the brief catches a
test's stdout, not the summary — redirect stdout to see it.

---

## 3. Is the backlog honest?

### Two random verifications

`random.sample` over the nine items marked DONE or struck through picked **G2** and **G7**.

**G2 — rails outside the vocabulary dropped (`cc94dd1`).** Ran, inside `rc-car`:
`emit_board.py car.requirements.json --project . --board firebeetle2-esp32s3`. The four part
records declare **10** power pins (listed from the JSON: 3 on `traction`, 2 on `servo`, 5 on
`ground`); the output carries **10** module power traces, `net.TRACTION` and `net.SERVO` among
them, and the block "Rails this design INVENTED" names both with their pins. **Holds.**

**G7 — identical parts collapse (`0201d6d`).** Three runs on the remote:
the committed `remote.requirements.json` (five named instances) → five distinct
`<chip name="Btn…">`, five signal traces, exit 0; the same part five times unnamed → **exit 2,
0 bytes on stdout**, message names `TactileButton`; two entries both named `BtnForward` →
exit 2. **Holds.**

Also run while there, all holding: **G8** on the two-board project — exit 2, `--json` status
`could-not-run`, 4 of 7 completed, three checks name both candidates and `--circuit`; with
`--circuit dist/car/circuit.json` the ambiguity clears. **R6/G4** — `????  buildability:
Xt30TractionInlet: its footprint is a stand-in`. **R5** — `physics ok` on the committed car
build. **R3/G12** — `assign_pins.py:55  CAPABILITIES = parts_library.CAPABILITIES`. R5's "17
tests of its own" — `test_copper.py` has 17. **P4** — `mutate.py tests/mutations/sprint-2.json`
on the pristine copy: 10 of 10 caught, files restored.

### Claimed fixed, not fixed

- **R5** — sized only with `--project` (§2). The documented invocation is unsized.
- **"The whole spine runs … exit 0"** (`PRODUCT_BACKLOG.md:31-33`, and P1) — true only when a
  project-local `tsci` precedes the global one. spark ships no `node_modules`, so
  `find_toolchain` (`check_spine.py:80-93`) falls through to `PATH`. A/B on the pristine copy
  with only `PATH` differing: nvm's `tsci 0.0.2600` → `[!!] build  no circuit.json was
  produced` (`Cannot find package 'react'`), **exit 1, "the chain is broken"**; the bin's
  `0.0.2621` → `build 12 trace(s), 0 errors`. From the real spark directory with the bin's tsci
  first: exit 0. So the claim has an unstated precondition, and a toolchain fault is classified
  as a design fault — the tool's own three-outcome rule, broken at the `build` stage.
- **G15 "fixed at the cause"** — the cause was fixed and the use-site copy left in; the fix now
  double-reports (§2, item 1).

### Open, but already done or moved

- **P4** (mutation tool) — delivered in `997b756` at 09:47: `scripts/mutate.py`,
  `tests/mutations/sprint-2.json`, `tests/test_mutate.py`, 424 lines; it runs. That commit did
  not touch the backlog; P4 still reads as open.
- **P3** (`spi` role) — in the working tree at 09:49, uncommitted, in `boards.py`,
  `assign_pins.py` and both board files. Observed mid-change through `check_spine`: the shipped
  board file failed its own contract (`pin_roles.spi is not a role any script reads`) and every
  consumer refused, until the `boards.py` half landed. Transient, and the same "two halves
  disagree" shape as G12 — a board file and its vocabulary should land in one commit.
- **P9** — three of four checks already keep the subject (`check_all.py:174`, `:223`, `:241`);
  only rules-vs-netlist (`:164`, `p["detail"]`) drops the `subject` that `compare_design.py:58`
  provides. The item reads as untouched.

### Stale prose

- `PRODUCT_BACKLOG.md:73` "**Three are fixed**" — above a four-row table and five more
  struck-through DONE items. Nine fixed, ten with G15 inside R1's text.
- `:80` G9's fix column says "**this change**"; the hash is `3b5f38f`.
- `:114` "Tier 2 is closed. That was the trigger for the audit." — a sentence with no tier.
- `INDEX.md` — **zero of the fifteen cold-test claims were logged** (`README.md` step 1: "Log
  every claim in INDEX.md as raised"). The intake the project built after the findings store
  failed was bypassed for the one sprint it is now auditing. Rows R3 (`verified`; fixed by
  `244feb1`), M1 (`raised`; `21156b4` + `check_spine.components_not_on_ground`), M7
  (`raised`; P1 done) are stale. O4b/S5 remain true: `README.md:56` "every one … takes
  `--json`"; `emit_board.py` has no `--json` flag.

---

## What I would change first

**One `load_design()`**. Make the loading of a design one function that `emit_board.main`,
`check_all.placeholder_components_in` and `check_spine.run` all call:
`load_design(requirements_path, project) -> (board, part_list, assignments, rules)`, with
`project` resolved exactly once and the JSON read inside its `try`. Evidence that this, not
splitting `emit()`, is the highest-value change: the live defect (`:609` resolves, `:678`
ignores), the cross-module copy with a silent fallback (`check_all.py:206-213`), and the three
tracebacks (`:607`, `:270`, `check_spine.py:322`) are all consequences of `main()` loading inline.

Then: split `emit()` by section — each block that begins `lines.append("    {/* …")` is a
function returning lines; collapse the four power-pin walks into one
`power_connections(part_list)` generator; replace `check_all.load()` with plain imports. And add
the test the mutation table cannot express: call `emit_board.main([...])` from inside a temp
project holding `.spark/rules.json`, **without** `--project`, and assert a `thickness=` on a
trace. That test fails today.
