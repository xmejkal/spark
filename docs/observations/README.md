# Observations

Notes from agents whose job is to watch how this plugin is used rather than to build it.

They accumulate here because a session's context is cleared and its findings should not be. Each
file is dated and names what it looked at.

## Why this exists

Every serious defect this project has found came from someone looking who was not the person
doing the work. The runner that reported `ok` without looking, the footprint field the engine had
moved so two rules examined nothing, the fabrication-blocking MOSFET pad mapping, the module whose
identity nobody had ever checked — none of those were found by the person who wrote the code. They
were found by councils, by a first-time user, by an adversarial re-check, and by a cold rebuild.

The pattern was identical every time: the builder verifies in the one environment where things
work.

## How to read these

**They are reviews, not facts.** Several have been confidently wrong — one council's central
claim about the evals was right, another's verdict on two findings was not. Reproduce a claim
before acting on it. Anything promoted out of here into `scrum/PRODUCT_BACKLOG.md` should have
been verified first, and should say so.

## What to do when a report lands

1. **Log every claim in `INDEX.md` as `raised`.** One line each. A report is not a list of
   findings until its claims are separable and countable.
2. **Reproduce, or reject.** Run something. A claim that cannot be reproduced is `rejected` with
   that as the reason — which is useful, because it says the observer's method was wrong.
3. **Promote what survives** into `scrum/PRODUCT_BACKLOG.md` with the evidence attached — an item
   that names the design needing it (W14) — and mark the row `acted`.
4. **Keep rejected rows.** An observer that is confidently wrong will be wrong the same way next
   time.

This is four steps because the alternative was demonstrated here: a findings store that held
twenty findings and resolved none of them, cut on 2026-09-29. Good mechanism, no closing move.

The reports here are the sprint audits since 09-29 and, since 2026-10-08, the council's report on
PR #98 (`2026-10-08-p97-store-1c-council.md`). The four essays of 09-25 that fed the first rows are
in git history; every claim they made is a row in `INDEX.md`, which is what survives.

## What good observations look like over time

Not a pile of essays. The point is that the same gap named by three independent observers on
three different days is a much stronger signal than any one of them, and that only shows up if
the claims are separable and counted. Over time this table should answer: what does the plugin
actually need, which use cases are real, which gaps keep being rediscovered, and which of its own
claims it cannot support.
