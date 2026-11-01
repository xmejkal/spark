# P479 event seam: plan council, round 1

Card [P479 #657](https://github.com/xmejkal/spark/issues/657). The plan is
`docs/discovery/2026-10-19-p323-target-architecture/architecture/event-seam-plan.md`. Five lenses read the draft on
2026-11-01: architecture, UX and AI-UX, tech lead and PO assistant on the everyday model, and the refuter on the
strongest model. The synthesis ran on the strongest model. It merged `origin/main` (P482 and P468) into the branch at
d375c017 and checked each finding in the code there. Every finding has a row in `docs/observations/rows/p479-event-seam.md`.

## Architecture

Findings: one rule for a line that deploy shows mid-run against a result line. Name the builder change in `run_cli`.
Drop `PROGRESS` until a Reporter draws it. Move the child output change to E2. List every `show_line` hit in the plans,
with a check that finds none after E2. Say that `report` takes facts, and where E1 sits in the waves.

What the plan did: rule 1 "one line, one place", with E2's test. The builder section names the new line after
`cli.py:108` and the three builders. The extracted `reporter_for` became `TerminalReporter.for_json`, because a new
top-level function in `cli.py` that reads `sys.stdout` breaks rule X2 (`tools/measure.py:252` names `run_cli` only).
`PROGRESS` and its counts are gone. Section 3 is a table of every hit, with the grep check. The reviewer's
`wave4-plan.md:191` and `:195` hold no `show_line`. They hold the W4-2 sequence, which gains a report arrow. The
reviewer missed `refactor-plan.md:127-128`, `:188`, `:194`, `:201-202`, `:627` and `areas/bench.md`, and the table
holds them.

## UX and AI-UX

Findings: the goldens compare stdout only, while agents.md promises stderr text. Pin the order of the lines and the
report. Write the stderr contract now. Say there is no visible gain before P478. Make the step codes a public list.
Let Reporters decide on the step, never on text.

What the plan did: E2's first commit adds a text golden of deploy that reaches the gate and a stderr golden of the
`--json` case. Rule 2 pins the order on both streams, in E1's toy test. Rule 4 is the stderr contract, with an
agents.md sentence in E1. Decision 4 says the seam brings no visible change before P478. A Reporter decides on `kind`
and `code`. The public list is rejected for now: deploy's phase codes are already public as the envelope's `stage`, and
P481 #660 describes each phase as data later.

## Tech lead

Findings: the field `step` and the constructor `Event.step` clash. The goldens prove too little: add a subprocess test
in E1 and a stderr test in E2. E1 is too big: `echo_to` is deploy only. `FakeOutsideWorld` makes a `FakeReporter` by
default. The R1 and R3 baselines of deploy. Rows in the names table, and the Adapter label.

What the plan did: the field is `code` and the constructors are `Event.line` and `Event.begin`, because "step" also
names wiring steps and scenario steps. A unit test reads every field. The child output change moved to E2. The Fake
default, the baseline numbers (72, 9, 7, verified in `tests/architecture_baseline.json`) and a `Reporter` row are in.
`TerminalReporter` is a Strategy case, not an Adapter, because it wraps a stream, not an outside program. The
subprocess test in E1 is rejected: E1 has no child and no fd-level write, and the in-process test through a builder runs
the real `run_cli` and `TerminalReporter`. The fd-level proof comes in E2, where the deploy goldens run as children and
compare both streams.

## PO assistant

Findings: a "You decide" box with three or four yes or no questions. One line on what approving means. The short
version first, section 3 as a table, the map as an appendix. E3 and E5 in one line each. Each other output place with
the wave that moves it.

What the plan did: all of these. The box holds four questions: the word `report`, E1 as its own PR after P480, plain
stderr under `--json` until P477, and no visible change until P478. The other open questions of the draft are rows,
decided by the council.

## Refuter

Findings, all verified by the synthesis: three wrong counts (`emit_board.py` 16, `grant.py` 8, `deploy.py` 3). A missed
mid-run line at `deploy.py:152`. The indent: the Event drops it, but the terminal printed `event.text`. E4 put the
build's stderr lines on stdout. The deploy goldens never reach a mid-run line. E1's toy test passes `outside`, so it
never reaches the stream choice in `run_cli`.

What the plan did: the map has the right counts and the seventh line. `TerminalReporter` adds the two spaces. Rule 3
keeps every stderr line a diagnostic, so no Event needs a stream. E2 adds the goldens that reach the gate before its code.
E1's stream test goes through a builder, and the plan lists the builders, the two `build_outside_world` calls and the
mutation row that change.
