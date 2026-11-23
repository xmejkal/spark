# P1039: spark past the MVP, the R&D discovery in short

> Short version: spark needs no second architecture to grow past the MVP, in the opinion of the lenses and the
> architect. The proposal is seams in the core work now (P793 #1105) and no new epic. A direction gets a first spike
> only after the PO's own answers show a pull for it. The PO confirmed this understanding (D5) and then answered every
> question of his own (D8 to D21). Only the line past the breadboard has a pull: one spike for a permanent build, on a
> perfboard or a PCB, which spark-main files (D21).

This folder is the discovery of the epic P1039 (#1522), run on 2026-11-23 at full depth. Six lenses on Opus read the
product. The architect on Fable wrote the synthesis, and the refuter on Fable read it twice. A council of three
answered the questions while the PO was away. The PO confirmed the understanding on 2026-11-23 (D5) and answered his own questions the same evening (D6 to D21). Ready for: an experiment, the permanent-build spike. The skill's output test passes.

## The picture

```mermaid
flowchart LR
  subgraph now["Today"]
    core["one core, Operations, calls no model"]
    cc["Claude Code: commands, skills, agents"]
    cli["CLI with --json, 12 of 27 on the core"]
  end
  subgraph seams["Seams now, on P793 #1105"]
    s["S1 to S7: neutral sentences, consent for the network, a catalogue, one envelope, events, a trace hook, no absolute paths"]
  end
  subgraph later["Later, each only after a pull"]
    h["a second harness"]:::later
    m["MCP and LangGraph, P417"]:::later
    e["one measured eval row"]:::later
    l["a local model"]:::later
    f["the line past the breadboard: perfboard, PCB, one spike (D21)"]
  end
  cc --> cli --> core
  core --> s
  s --> h
  s --> m
  s --> e
  s --> l
  s --> f
  classDef later stroke-dasharray: 5 5
```

## What the discovery found

- The core is plain Python that calls no model, and an Operation already describes itself as a tool (★C1, ★C9). No
  second interface has run, but one 20-line probe ran a read-only Operation with 0 core lines changed.
- What ties spark to Claude is the agent layer's frontmatter and variables, Claude names in the code, and at least
  seven network operations whose only yes is Claude Code's prompt (★C2, ★C3, ★C11).
- A second agent harness is installed on the PO's computer. Nothing of spark has run in it (★C6).
- The line has no end: the flow never shows a deploy as done, and the gadget's later work is outside the flow's phases
  (★C19, ★C20). Past the breadboard the line is thin (★C21).
- Nothing measures whether an agent succeeds. One eval once scored the plugin against a baseline (2026-09-24) and was
  cut five days later (★C17).
- No check makes sure that the agent pages teach a new script or flag. `cost.py` is on none of them (★C13, ★C14).
- Nobody outside the project uses spark yet, and the backlog grows faster than it closes (★C23, ★C24).

## What is decided

- D1, the PO: the frame, full depth.
- D5, the PO: the understanding, with D2 and D3 as the council answered them.
- D2 and D3, delegated to the council and the PO's to change: the ratings of the assumptions, A1 as the riskiest with
  a three-arm test, and an answer for each of Q2 to Q12 (mostly option a: seams only, no new epic, no rewrite now).

- D8 to D21, the PO's own answers on the evening of 2026-11-23:
  - His own use as a hobbyist decides a first spike, not the showcase (D8).
  - "Software factory" is the gadget's line, made longer (D12). P934's bench run proves the MVP (D14).
  - No trial in another harness, no eval and no local model now (D10, D15, D16). "Hermes" is the agent harness (D13).
  - The clock and the bin needed a permanent build, "including the perfboard optional step, not just pcb" (D11).
  - He did not know `live.py` and `grant.py` when he asked for a REPL (D17). He read none of the walk's rows (D18).
  - The folder keeps the installed programs unnamed (D20).

## What comes next, and what is open for the PO

1. spark-main files one spike under #1522: the clock or the bin from the breadboard to a perfboard (optional) and a PCB, and where spark stops (D21, [items.md](items.md)).
2. Nothing else is open for the PO in this discovery. The other directions wait as lines under "later".

## The files

- [direction.md](direction.md): the one-page picture, with the factory line, the architecture today and the target, the interface options and the use cases.
- [diagrams.md](diagrams.md): the factory line as a process, the seams, the decision path, the team's loop, the story map and crude interface sketches.
- [brief.md](brief.md): the frame, every claim with its source, the options, the questions and the decisions.
- [jobs-and-journeys.md](jobs-and-journeys.md), [story-map.md](story-map.md), [risks-and-tests.md](risks-and-tests.md), [items.md](items.md), [verification.md](verification.md).
- [council/](council/): the six lens reports, the two refuter passes and the council's answers, with their tally in [council/delegated-answers.md](council/delegated-answers.md).
