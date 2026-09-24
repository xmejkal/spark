---
name: spark-review
description: Review an electronics design for problems and keep track of what was found. Runs the deterministic checks, then reviews power, signals, thermal-mechanical and firmware-hardware agreement, and records findings so they survive between sessions. Use when the user asks to "review my design", "what's wrong with this board", "check my circuit", or has just changed a design and wants to know what it broke.
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

One command runs all of them. Pass whatever the project has; anything you leave out is reported
as not asked for rather than quietly passed.

```
${CLAUDE_PLUGIN_ROOT}/scripts/check_all.py \
  --circuit dist/board/circuit.json \
  --rules .spark/rules.json \
  --boards boards/*.json \
  --package board-gerbers.zip
```

Cheap, deterministic, and they own their ground:

| check | owns |
| --- | --- |
| vendor-truth | the pin map, re-derived from the vendor's own header |
| buildability | drill vs the pin that goes in it, annular ring, via class, package vs value, cross-pluggable connectors |
| the-order | the BOM against the schematic it came from |
| physics | trace current, capacitor derating, resistor dissipation, I²C rise time |
| rules-vs-netlist | written rules against the design that was built |
| pin-capability | wake, ADC, exclusivity, the boot-log UART, I²C address clashes |

**Do not ask a reviewer to look at anything in that table.** A reviewer pointed at a dimension a
script already covers produces false positives and nothing else — and these are faster, free,
and cannot change their mind.

**Read the three outcomes separately.** `FAIL` is a problem. `????` means a check was given what
it needs and still could not look, which is not a clean board. `?` lines are things the design
does not know yet — an unmeasured rail is not a passing rail, and a project whose worst risk is a
number nobody has taken should be told that rather than given a tick.

## 3. Review the dimensions, in parallel

Launch one `design-reviewer` agent per dimension, **in a single message so they run at once**:

- `power` · `signals` · `thermal-mechanical` · `firmware-hardware`

Each agent needs, in its prompt: its dimension, the paths it may read, the anchor namespace from
step 1, and the brief's `must` list from `.spark/project.json`.

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

## What this does not do

It does not edit the design. It finds things, records them, and proposes; you decide and you
change. A review that rewrites the board on its own reasoning is a different and much riskier
tool than this one.

A clean run means these dimensions found nothing this time. It does not mean the design works.
