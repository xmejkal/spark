# Retrospectives

One entry per retro. Each carries **the change it produced** and **a check that tells us later
whether it stuck** — because an action nobody verifies is the thing retros are famous for.

The check is run at the *next* retro and its result written into the previous entry. An action
that did not stick is not quietly dropped; it is recorded as not having stuck, and we ask why.

---

## R1 — 2026-09-25, on the two days before the team existed

**Present:** facilitator, scrum-master agent (reported independently, having read the commit log
and run the tooling itself).

### What happened

The product goal was reached on one axis and not started on the other. `idea → parts → schema`
went from never having been run end to end to exit 0 with 8 traces. `→ simulation` is untouched.

### What went well, with evidence

- **Outside eyes found what the tests could not.** The scrum-master agent found the root cause of
  the zero-trace board — a part file whose footprint said 5 pads beside a pinout naming 7 — that
  350 green tests did not. That is the fourth time a reader has beaten the suite.
- **The honest-reporting rule paid out in cash.** Teaching `check_footprints` to read pill holes
  took a few lines and immediately found two real fab blockers on a board declared ready to order.
  The rule that a check which could not look must not read as a pass is now load-bearing, not
  aspirational.
- **Two councils killed a week of work correctly.** A KiCad footprint-import pipeline was proposed
  and abandoned when 18 of 27 footprints were shown to convert to geometry identical to what
  already existed.

### What did not

- **A claim was overstated in a commit message.** "The emitted board now BUILDS" was written while
  `tsci build` exited 1. The schematic built; the build did not. Written by the person who wrote
  the rule against exactly this, and caught by an agent, not by the author.
- **Every link was tested and the chain was not.** Each component did precisely what its own tests
  asked, and the product produced a board with no copper for weeks. Unit tests cannot see this
  class of defect; only running the whole thing and counting the output can.
- **Work was scattered across three queues** — `BACKLOG.md` §5, `docs/observations/INDEX.md`, and
  a findings store — which between them resolved nothing. Two parallel lists is a backlog; three
  is a graveyard.
- **The rework rate is real.** A measured ~39% of commits repaired damage hours old. Mostly caught
  by readers rather than by the suite, which points at the discipline, not the people.

### Actions — the changes this retro produced

| # | change | check that it stuck | result |
| --- | --- | --- | --- |
| **R1.1** | The chain gets one gate that runs it end to end and counts traces, not exceptions. **Done same day** — `scripts/check_spine.py`, and it is clause 3 of the Definition of Done. | At R2: has any PBI been called Done while `check_spine.py` was red or unrun? | *pending* |
| **R1.2** | One backlog. `scrum/PRODUCT_BACKLOG.md` is the only queue; `BACKLOG.md` becomes narrative and `INDEX.md` becomes intake. A claim becomes work only by being promoted to a PBI. | At R2: count rows added to `INDEX.md` vs rows promoted or **rejected**. If `rejected` is still zero, this did not stick. | *pending* |
| **R1.3** | Mutation testing stops being enforced by memory. → **P4** in the backlog. | At R2: does `scripts/mutate.py` exist and is it used in a commit? | *pending* |
| **R1.4** | Every PBI names a `Value proven by:` command before it can be pulled, and review runs it. Aimed squarely at the gap between Done and valuable, which cost this project the most time. | At R2: was any PBI pulled without one? Did review actually run them? | *pending* |
| **R1.5** | Keep an outside reader running. The evidence is now four-for-four: every serious defect came from someone not doing the work. | At R2: did an observer run during the sprint, and was its report reproduced before being acted on (W9)? | *pending* |

### What we are deliberately not changing

The rework rate, directly. Two of the five actions above (R1.1, R1.3) attack its causes — no
end-to-end gate, and a discipline held only in memory. Adding a rule that says "make fewer
mistakes" would be the kind of action that cannot be checked, which is what this table exists to
prevent.
