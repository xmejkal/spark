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
before acting on it. Anything promoted out of here into `BACKLOG.md` should have been verified
first, and should say so.
