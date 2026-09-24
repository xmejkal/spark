---
name: spark-review
description: Review an electronics design for problems, gate it before fabrication, and keep track of what was found. Runs every deterministic check, then reviews power, signals, thermal-mechanical, manufacturability and firmware-hardware agreement, and records findings so they survive between sessions. Use when the user asks to "review my design", "what's wrong with this board", "check my circuit", "verify this", "run ERC or DRC", is about to order or fabricate a board, or has just changed a design and wants to know what it broke. For a quick deterministic pass with no agents, /spark:check is cheaper.
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/findings.py *), Bash(${CLAUDE_PLUGIN_ROOT}/scripts/check_all.py *)
---

# spark-review

Find what is wrong with a design, and remember it.

Three sources feed one list: the deterministic checks catch known classes, the reviewers catch
what nobody thought to check for, and a person's own decisions retire what does not apply. The
list is a file in the project, so it survives closing the terminal.

## 1. Build first, so findings can name things

Findings refer to design elements by anchor, and anchors are validated against the built design.
Build it (`make`, or `tsci build board.tsx`) before reviewing anything, or every finding will be
refused for citing components that — as far as the store can tell — do not exist.

Then get the namespace:

```
${CLAUDE_PLUGIN_ROOT}/scripts/findings.py anchors
```

## 2. Run the checks

One command, one argument. It finds the circuit, the rules, the fab package, the firmware, the
board definitions and the design file inside the project, and **prints every path it resolved**
before it reports anything.

```
${CLAUDE_PLUGIN_ROOT}/scripts/check_all.py --project .
```

Read the resolution block first, every time. Anything shown as `not found` is a check that will
be skipped, and it says where it looked. Anything shown as `AMBIGUOUS` is two candidates it
refused to choose between — name that one with its own flag (`--circuit`, `--rules`, `--package`,
`--firmware`, `--design`, `--board-file`), which always beats the convention.

This step used to list five explicit paths, and two were wrong in a way nothing announced: it
globbed `boards/*.json`, which matches the project's board *selection* file rather than a board
definition, and it never passed `--design` or `--firmware` at all. So the flagship check was
permanently unasked, a board that could not be read still showed a tick, and the review called
itself complete having run three of seven checks.

Cheap, deterministic, and they own their ground:

| check | owns |
| --- | --- |
| vendor-truth | the pin map, re-derived from the vendor's own header |
| buildability | drill vs the pin that goes in it, annular ring, via class, package vs value, cross-pluggable connectors |
| the-order | the BOM against the schematic it came from |
| physics | trace current, capacitor derating, resistor dissipation, I²C rise time |
| rules-vs-netlist | written rules against the design that was built |
| pin-capability | wake, ADC, exclusivity by GPIO, the console UART, I²C address clashes |
| firmware-vs-board | every pin the firmware drives against the board and the agreed pin map |

**Do not ask a reviewer to look at anything in that table.** A reviewer pointed at a dimension a
script already covers produces false positives and nothing else — and these are faster, free,
and cannot change their mind.

**Read the three outcomes separately.** `FAIL` is a problem. `????` means a check was given what
it needs and still could not look, which is not a clean board. `?` lines are things the design
does not know yet — an unmeasured rail is not a passing rail, and a project whose worst risk is a
number nobody has taken should be told that rather than given a tick.

## 3. Review the dimensions, in parallel

Launch one `design-reviewer` agent per dimension, **in a single message so they run at once**:

- `power` · `signals` · `thermal-mechanical` · `manufacturability` · `firmware-hardware`

Each agent needs, in its prompt: its dimension, the paths it may read, the anchor namespace from
step 1, and the brief's `must` list from `.spark/project.json`.

**`firmware-hardware` is narrower than its name.** `check_firmware.py` already owns pin agreement
— every constant against what the board brings out, against its strapping pins, and against the
pin map that was agreed, matched on GPIO rather than on name. Do not ask a reviewer for any of
that. What is left for it is what a number cannot settle: whether the firmware's behaviour is
possible on this hardware at all. Does a power policy assume a wake source the board cannot
provide? Does a timeout assume a stroke the motor cannot finish? Does the code assume a peripheral
that is shared with something else?

**Give each one the primary artefacts only** — the schematic, the board definition, the firmware
config. Not the README, not the handover note, not the design-rationale document. Those hold the
project's conclusions about itself, and a reviewer that reads them adopts them instead of testing
them. This is the single most important instruction in this skill: a project document here claimed
an idle current that was wrong by roughly forty times, and it had been believed for weeks because
it was written down.

Do not show a reviewer the existing findings. Deduplication happens in step 4, where it is exact;
showing them the list only makes them less likely to find things independently.

## 4. Append, serially

Collect every agent's JSON into one file and append it in a single call:

```
${CLAUDE_PLUGIN_ROOT}/scripts/findings.py append /tmp/review.json
```

One writer, so nothing gets clobbered. The store does the rest:

- **identity is structural** — same dimension and anchors means the same finding, however it is
  worded, so a second run does not duplicate the first
- **an anchor that does not resolve refuses the finding** — a free filter on the most common
  hallucination
- **a resolved finding that reappears becomes `regressed`** — something undid a fix; that is a
  person's call and never an automatic re-fix

Report what came back honestly, refusals included. A refused finding usually means a reviewer
invented a component name, which is worth knowing.

## 5. Say what to do now

```
${CLAUDE_PLUGIN_ROOT}/scripts/findings.py next
```

Show the open findings and propose **one** action. Not a plan, not a list — the single next thing.

If it is blocked on a measurement, say what to measure and how; those are usually minutes of
someone's time and they unblock everything behind them.

## Working a finding

You are in the conversation, so this is a conversation, not a subagent.

1. Read the finding. Propose options **with their consequences** — an option whose consequences
   are not stated is not an option, it is a trap. A load switch on an always-powered module is a
   real fix, and it also needs a spare GPIO, brings inrush into whatever bulk capacitance is
   downstream, must default off at reset, and back-powers the module through its input protection
   unless the driving pin is set high-impedance first. All four belong in the proposal.
2. Let the person decide, and record it:

```
findings.py status <key> resolved --reason "..."   # fixed; say what changed
findings.py status <key> accepted --reason "..."   # real, living with it, and why
findings.py status <key> rejected --reason "..."   # the reviewer was wrong, and how
findings.py status <key> blocked  --reason "..."   # needs a measurement first
```

**`rejected` matters more than it looks.** Reviewers are confidently wrong as a matter of course.
A wrong finding that cannot be retired comes back every run, and a list that cries wolf is a list
nobody reads.

3. When a number arrives, feed it back:

```
findings.py measure <measurement-id> --value <what you read> --unit mA \
    --source measured --instrument "how you read it"
```

Every number says where it came from — `measured`, `datasheet` or `estimate` — and a measured
one must name the instrument, because a reading without one is not reproducible. Everything
blocked on it reopens; anything already *resolved* on the strength of a different number
regresses, because a fix justified by a number that has since moved needs looking at again.

**Never paste an example value into a real store.** That has already happened once here: the
sample figure from this document ended up in a live project, indistinguishable from a reading,
while the handover note still said the number had never been taken.

## Before fabrication, the gate

The one rule that separates a real design from plausible-but-dead output: **never emit
fabrication files while something load-bearing is unverified.** Rigour scales with stakes — at
the schematic stage warnings are fine and you just show them; at the ordering stage they are not.

Two commands enforce it, and they are the ones this gate used to describe in prose without
naming:

```
${CLAUDE_PLUGIN_ROOT}/scripts/boards.py --validate --for-fab
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --unverified <every part on the board>
```

The first refuses a board definition missing what a PCB actually needs. The second lists every
number nobody has checked, each with what depends on it. Neither is advisory: an open one is a
thing to settle or to accept out loud, not to scroll past.

If KiCad is installed, `kicad-cli sch erc --format json --exit-code-violations` is the
authoritative electrical-rules check (exit 0 clean, 5 violations), and `kicad-cli pcb drc` is
what catches an autorouter short or an unmanufacturable via before the fab house does. If it is
not installed, say so rather than skipping it silently — an ERC that did not run is not an ERC
that passed.

**Ground truth is the bench.** Breadboard the modules before ordering a PCB. Auto-routing is the
weakest link in this whole pipeline and human review before fabrication is not optional; say so
plainly rather than implying the checks have covered it.

## What this does not do

It does not edit the design. It finds things, records them, and proposes; you decide and you
change. A review that rewrites the board on its own reasoning is a different and much riskier
tool than this one.

A clean run means these dimensions found nothing this time. It does not mean the design works.
