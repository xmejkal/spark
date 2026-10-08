---
name: spark-review
description: Review an electronics design for problems and gate it before fabrication. Runs every deterministic check, then one reviewer per dimension (power, signals, thermal-mechanical, manufacturability, firmware-hardware) reading the primary artefacts only, and ends with the fabrication gate. Use when the user asks to "review my design", "what's wrong with this board", "verify this", is about to order a board, or has just changed a design and wants to know what it broke.
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/check_all.py *), Bash(${CLAUDE_PLUGIN_ROOT}/scripts/boards.py *), Bash(${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --unverified *)
---

# spark-review

Find what is wrong with a design, say it plainly, and refuse to call it ready while something
load-bearing is unverified.

## 1. Build first

Every check reads the built netlist. Build it (`/spark:build`, or `npx --no tsci build board.tsx`) before
reviewing anything.

## 2. Run the checks

One command, one argument. It finds the circuit, the rules, the fab package and the board
definitions inside the project, and **prints every path it resolved** before it reports anything.

```
${CLAUDE_PLUGIN_ROOT}/scripts/check_all.py --project .
```

Read the resolution block first, every time. `not found` is a check that will be skipped, and it
says where it looked. `AMBIGUOUS` is two candidates it refused to choose between — name that one
with its own flag (`--circuit`, `--rules`, `--package`), which always beats the convention.

| check | owns |
| --- | --- |
| vendor-truth | the pin map, re-derived from the vendor's own header |
| buildability | drill vs the pin that goes in it, annular ring, via class, package vs value |
| the-order | the BOM against the schematic it came from |
| physics | trace current, capacitor derating, resistor dissipation, I²C rise time |
| rules-vs-netlist | written rules against the design that was built |

**Do not ask a reviewer to look at anything in that table.** A reviewer pointed at a dimension a
script already covers produces false positives and nothing else.

**Read the three outcomes separately.** `FAIL` is a problem. `????` means a check was given what
it needs and still could not look, which is not a clean board. `?` lines are things the design
does not know yet — an unmeasured rail is not a passing rail.

## 3. Review the dimensions, in parallel

Launch one `design-reviewer` agent per dimension, **in a single message so they run at once**:
`power` · `signals` · `thermal-mechanical` · `manufacturability` · `firmware-hardware`.

Each agent gets its dimension, the paths it may read, and the brief's `must` list from
`.spark/project.json`. **Give each one the primary artefacts only** — the schematic, the board
definition, the firmware config. Not the README, not the handover note, not the design-rationale
document. Those hold the project's conclusions about itself, and a reviewer that reads them
adopts them instead of testing them: a project document here claimed an idle current that was
wrong by roughly forty times, and it was believed for weeks because it was written down.

## 4. Report, then one action

Collect the reviewers' findings into one list in the conversation — each with what it rests on
and its severity — drop duplicates, and propose **one** next action. Not a plan; the single next
thing. If it is blocked on a measurement, say what to measure and how.

When the person decides a finding is wrong, say so and move on. Reviewers are confidently wrong
as a matter of course; a list that cries wolf is a list nobody reads.

## 5. Before fabrication, the gate

**Never emit fabrication files while something load-bearing is unverified.**

```
${CLAUDE_PLUGIN_ROOT}/scripts/boards.py --validate --for-fab
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --unverified <every part on the board>
```

The first refuses a board definition missing what a PCB needs. The second lists every number
nobody has checked, each with what depends on it. An open one is a thing to settle or to accept
out loud, not to scroll past. If KiCad is installed, `kicad-cli sch erc` and `kicad-cli pcb drc`
are the authoritative electrical and layout checks; if it is not, say so rather than skipping them
silently.

**Ground truth is the bench.** Breadboard the modules before ordering a PCB; auto-routing is the
weakest link in this pipeline, and human review before fabrication is not optional.

## What this does not do

It does not edit the design, and it does not remember between sessions: what was found and what
was decided about it belongs in the project's own notes, in the person's words. A clean run means
these dimensions found nothing this time. It does not mean the design works.
