# The architecture the refactor should aim at

Written for P40, 2026-09-30, by a council of five technical lenses — Python engineering, the
domain model, agent-system design, test and change-safety, and migration planning — each reading
all 3,552 code lines and probing the product. Every claim below was reproduced by the session that
wrote this document before it was written down (W9). **No code moved to produce it.**

## The verdict: this is not a refactoring project

`scripts/` is 3,552 code lines against a 4,000 ceiling, 596 tests green, and **no design is
blocked by the shape of this code**. Three designs are blocked by its *behaviour*, and those are
already items: P34, P35, P29. So the refactor is not a project to schedule. It is the shape those
three items take, plus one safety net in front of them, plus one cluster of agent-facing fixes.

A perfect de-duplication of the check family recovers about 45 lines, 1.2% of the budget, and
disturbs 20 of the 132 mutation anchors. The whole plan below nets about **−85 code lines** and
closes three defect classes. Anything beyond it is ceremony this team would delete in a month.

## The evidence

### One live defect, reproduced

```
$ echo '{"physics":{}}' > /tmp/empty-rules.json
$ python3 scripts/check_physics.py <a real circuit> --rules /tmp/empty-rules.json --json
  "status": "ok"        every finding's severity: could-not-run        exit=0
```

`check_physics.py:498` builds its status from `problem`-severity findings alone, where
`check_footprints.py:524` builds it from all three. It is the only one of six copies that is
wrong, and it is the file whose own docstring says an unchecked rail must never look like a
passing one. `check_all` hides it, because its wrapper splits the severities itself — so the
defect is only visible where `smartbin-local/Makefile:202` calls the script directly.

### One missing type, reproduced

One circuit: `U1.GND` wired pin-to-pin to `U2.GND` (a trace naming no net, which is how spark's
own generator wires every signal), and `U2.GND` also on the named net `GND`.

| walker | answer |
| --- | --- |
| `compare_design.Netlist` | `U1.GND` sits on `trace:k1` — connected |
| `check_physics.Board` | members `{GND: [U2]}` — **U1 does not exist** |
| `check_spine.components_not_on_ground` | **`['U1']`** — a false problem that aborts the chain |

Three answers, one circuit. Only `compare_design` learned P8's lesson last night; the other two
did not. There is no netlist type in a codebase whose whole job is netlists.

### The duplication ledger

| idea | copies | agree? |
| --- | --- | --- |
| status from problems / unchecked / else ok | 6 | **no** — `check_physics` omits could-not-run |
| status → exit code | 5, and `outcomes.EXIT_FOR` has **zero callers** | yes, but the shared one is dead |
| netlist connectivity walk | 3 | **no** — see above |
| `Finding` record | 2 identical classes | fields agree, argument order does not |
| unguarded `json.loads(path.read_text())` | 8 raw against 3 guarded | **no** — an unreadable file exits 1, "problems", in three scripts |
| project/library record resolution | 2 (`boards`, `parts`) | same four names, arguments reversed |
| `main()` scaffolding | 16, 607 lines | shape agrees, outcomes do not |

## The target

Four things get one home. Nothing else moves.

1. **`outcomes.verdict(problems, unchecked, unmeasured) -> dict` and `outcomes.report(payload,
   as_json, render) -> int`.** `check_all.answer` moves verbatim, prose intact; the six copies and
   the five inline exit dicts become calls; `EXIT_FOR` comes alive. A `main` can no longer invent
   a status, so the defect class is unrepeatable rather than fixed.
2. **`scripts/netlist.py`, a library.** One walk, built with the pin-to-pin fallback and
   `.get("type")` rather than `e["type"]`. `check_physics.Board` subclasses it for the two methods
   only it needs; `compare_design.Netlist` becomes an alias; `check_spine`'s ground walk takes one.
   Every docstring from the three walkers moves in verbatim: they are the argument for each rule.
3. **`outcomes.read_json(path, what)`** raising a could-not-run, retiring the exit-1-for-an-
   unreadable-file class at eight sites.
4. **`check_bom` gets `--json` and a `run()`**, so `check_all` stops reaching into its internals.

Stays exactly as it is: every script's `main(argv)`, its three exit codes, its own `render()`, its
own argparse. The per-script standalone design is right and no framework is coming.

## The safety net, first

79% of the 596 tests reach into a module by symbol, so a move breaks tests at import level rather
than at behaviour level. Two gaps must be closed **before** the first move:

- **`boards.py`'s command line is a cross-repo contract with zero tests.** `smartbin-local`'s
  Makefile calls eight distinct invocations; none is exercised, and that Makefile records this
  exact break happening before. Six tests, about 60 lines.
- **Ten scripts declare `--json`; one test passes the flag, and it asserts only the exit code.** A
  refactor can rename any key in any payload and the suite stays green. Ten tests asserting the
  top-level key set and that `status` is one of the three words, about 120 lines.

Tests are not budgeted, and these are at the CLI boundary, which is the only boundary a
move-functions refactor cannot disturb. Do not add internal unit tests: the 471 existing
symbol-level assertions already over-specify the internals.

## The order

| step | item | what | delta | anchors disturbed |
| --- | --- | --- | --- | --- |
| 0 | **P41** | the safety net above | +180 test lines | 0 |
| 1 | **P34** | fix `check_physics` in place; zero rules compared becomes could-not-run | +6 | 0 |
| 2 | **P42** | `outcomes.verdict` and `report`; six callers converted | −45 estimated, **−8 measured** | 0, with `answer` kept as an alias |
| 3 | **P35** | `netlist.py`; three callers | −40 | 2, re-anchored in the same commit |
| 4 | **P29** | the supply walk joins as a third caller | +20 estimated, **+22 measured** | 2, re-anchored |
| — | stop | | | |

P34 goes before any move so the fix is one line in the log and not hidden inside a refactor. P29
follows P35 so the shared walker is proven on two callers before a third joins.

## Do not refactor

- **The 16 `render()` blocks and the argparse blocks**, 154 lines and every `help=` string. A
  table-driven renderer trades prose for indirection, and the prose is the product (W15b).
- **`parts.py`, `emit_board.py`, `assign_pins.py`** — 1,273 code lines, 36% of the budget, and
  **72 of the 132 mutation anchors**. A silent re-anchor failure there costs the mutation regime's
  whole value while the suite still reads green. No item needs them restructured.
- **The two `Finding` classes.** They live in files carrying one and zero anchors, so nothing would
  catch a regression. Make the signatures agree instead: one line each, no move.
- **Merging `boards`/`parts` resolution.** Genuinely 57 duplicated lines, but the blast radius
  exceeds the saving. Take the JSON guard there and leave the rest.
- **`check_spine.run`'s simulation stage.** No test on this machine reaches it. Refactor it only
  with a simulator run in the loop, or not at all.

## The stopping rule

Stop when one command's behaviour has one home: the verdict, and the netlist walk. Concretely,
after step 3 a `grep` for the trace fallback returns one file, and P29 joins the walker without a
fourth copy appearing. The warning signs of going further, in this repository's own dialect: a base
class for `Finding`, a `checks/` package (the route tests key on filenames in five places), or any
diff touching the three big files without an item behind it.

## Separately: the plugin names one person's machine

Not a refactor, but found by the same reading and cheap to fix (**P44**). The chain looks for the
simulation converter at `../smartbin-local/tools/circuit-to-wokwi` (P32 owns this); a shipped agent
file names an absolute path under one home directory for the catalog; and two shipped files
hard-code Czech sellers as prose while the brief already carries a sellers list.

## Separately: what an agent reads (P43)

Five different JSON shapes across the scripts, plus a fourth status word (`"mismatch"`), plus
`--catalog --json` ignoring the flag. `check_all` flattens each check's findings to
`subject: detail`, throwing away `rule` and `fix` — so an agent that reads the aggregate must re-run
a second command to learn how to fix anything. And `assign_pins --json` is 35,852 bytes, of which
28,739 is a list of unverified part facts that has its own command; the answer is 8%.

## Postscript, 2026-09-30: what step 2 actually cost

P42 came to **−8 code lines**, not the −45 estimated above. The six copies of the rule were one
expression each, not the blocks they looked like from a distance, and `outcomes` grew six lines
taking them in. The estimate was wrong in the direction that matters least: the reason to do it
was never the lines. It was that one mutation now sits in `outcomes.status_of` and guards all six
callers, where before it guarded one, and three exit codes that no test had ever asserted now have
tests. Read the remaining estimates in the table above as the same kind of guess.

## Postscript, 2026-09-30: the stopping rule held, and what the shared type then found

Step 4 landed at +22 code lines against +20 estimated — the first estimate in this table that was
close, and only because it was the one adding a rule rather than merging copies. `grep` for the
trace fallback returns one file. No fourth walker appeared. Stop.

The part worth recording is what the shared type found once it existed. P29 asked it a question
none of the three private walkers had asked — "is this pin on the net the design says feeds it" —
and the answer came back wrong about a pad that was correctly wired. tscircuit names a port after
its label only for a component built from `pinLabels`; one built from a FOOTPRINT, which every
microcontroller module in this plugin is, gets ports called `pin17` and `pin32` with the
silkscreen label only in `port_hints`. Membership had been keyed on the name alone in all three
copies, so every rule naming a pad of the processor missed — `compare_design` with
`must_not_float: [["Mcu", "D11"]]` reported a pin the irrigation board wires to a valve as
connected to nothing.

That defect was three years of nobody noticing away from being found by reading. It surfaced
within an hour of the three walks becoming one, because a shared type gets asked questions its
private copies never were. That is the argument for this kind of refactor, and it is not the one
this document made: the lines were never the point, and neither was the tidiness.

**P46 was not in this plan** and belongs beside it. The same reading that produced this document
missed that `PACKAGE_POWER_W` is a second copy rather than an import in two checkers, that the
header pin and the hole plating are likewise duplicated, and that the annular ring is 0.25 mm in
the checker and 0.35 in the generator, related by a sentence in a comment. The duplication ledger
above counted ideas and missed data. A ledger of literals would have found all four in a minute.
