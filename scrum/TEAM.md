# The team

Cross-functional means one test: **can this team take a PBI from idea to Done without waiting on
anyone outside it?** For the two things this project builds — a design tool and the board it is
proven on — that needs parts research, schematic work, firmware, verification, and somebody whose
job is to ask why.

## The test each member has to pass

An agent exists only if it needs at least one of:

- **isolation** — it must not see what the rest of us have seen,
- **restricted tools** — it is safer or more honest with less,
- **fan-out** — several run at once,
- **context budget** — it reads far more than the main thread should carry.

Anything failing all four is a **script** (one right answer, cheaper and cannot hallucinate), a
**capability** (a thin wrapper over somebody else's tool), or **the main thread** (the thing Petr
argues with). This test is why the roster is small.

## The roster

| member | why it is an agent | works on |
| --- | --- | --- |
| **`design-reviewer`** | isolation + restricted tools + fan-out | one design dimension per run, reading only the design |
| **`hardware-engineer`** | context budget — tscircuit semantics, footprint geometry, netlist shapes | schematics, footprints, the build |
| **`parts-researcher`** | fan-out + context budget — pages of datasheet per part | part records, vendor truth, sourcing |

Three agent files ship with the plugin, because three pass the test above. The process roles —
scrum master, verification, firmware — were agent files too until 2026-09-29 and were cut: nothing
routed to them, and a plugin user has no use for the way its author works. Those roles are played
by the main session and by the audit agent spawned at each sprint's end (R3.3), whose report is a
file in `docs/observations/`.

**Petr** is Product Owner: value and order. **The main session** facilitates, integrates, and is
the one that says Done.

## Why the reviewer must not read our own documents

`design-reviewer` is denied `Glob`, `WebFetch` and `WebSearch` on purpose, and is told to read
only the design. The reason is specific and was measured: this project's own `CLAUDE.md` asserts
*"Idle ≈ 200-400 µA"*, and a reviewer that reads it first never finds the audio module's real idle
current. A handover note that spells out a finding turns a review into a reading comprehension
test.

The same applies to every member: when the question is "is this right?", the project's opinion of
itself is contamination, not context.

## How work reaches a member

The facilitator pulls a PBI from `PRODUCT_BACKLOG.md` — one that names the design that needs it (W14) — and either does it on the main thread or
hands it to the member whose discipline it sits in — with the PBI's `Value proven by:` line, so
the member knows what finishing looks like. Members report; the facilitator integrates, runs the
Definition of Done, and commits.

Members do not commit. One writer, so the history stays legible and two agents cannot half-land
the same change.
