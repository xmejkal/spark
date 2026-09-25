# Working agreements

The rules the team actually runs on. Each one names **where it came from**, because a rule whose
origin is forgotten is the first one somebody argues away.

A rule enters this file only from a retro or from Petr. It leaves only by being explicitly
retired, with a reason, in `RETROSPECTIVES.md`.

---

## W1 — A check that could not look must never read as a check that passed

Four outcomes, never two: `ok` · `problems` · `could-not-run` · `skipped`.

**Origin:** the runner reported `ok` for a flagship check that called a function which had never
existed. Six more instances have been found since, in different files, by different people.

**How we know it holds:** `check_all.py` has one function, `answer()`, that decides status, and
`check_spine.py` exits 2 rather than 0 when it could not be exercised.

## W2 — A test must run the thing, not read it

No assertion on source text. No assertion that is an arithmetic identity of the function under
test.

**Origin:** a test asserted `load("check_design")` appeared in the runner's source. The string was
there; the call beneath it named a function that did not exist. The test was green for the entire
life of the defect — it verified the check was *named*, not that it *ran*.

## W3 — Mutation testing is the acceptance bar

Re-introduce the defect; the suite must go red. Before commit, not after somebody finds it again.

**Origin:** repeatedly, a rule was found to have no test at all while its file had many.

**Known weakness, flagged by the scrum master 2026-09-25:** this is enforced by memory. There is
no tooling, no hook and no CI. Until there is, it holds only as long as somebody remembers — and
the first retro's action item is to stop relying on that.

## W4 — Never change a test to make it pass

Change the decision first; the test follows the decision. If the test is wrong, say why in the
docstring and change its *premise*, not its assertion.

**Origin:** Petr, verbatim: *"always never just change the test so that it passes or even just
delete it or similar instead of actually finding everything and be open about everything"*.

**Worked correctly on 2026-09-25:** `test_every_shipped_part_can_produce_signals` required every
part to ask the host for a pin, which a power inlet never does. The premise was wrong for a whole
category, so the rule underneath was restated — a part must ask for a pin *or* carry a rail — and
the docstring records why.

## W5 — State the scope of an assertion

"The FireBeetle" is two power designs. "The VL6180X breakout" is four pinouts. "The DFRobot MP3
one" is four products. An unscoped claim is a defect, not a shorthand.

**Origin:** a board file described one SKU and was true of half of them; a part file described one
carrier and was applied to another.

## W6 — Finish before starting

One PBI in progress at a time, per person. A second is pulled only when the first is Done or
explicitly blocked and written up as blocked.

**Origin:** Petr, twice: *"make sure you often prioritize your work, finish before moving on to
too many things at the same time"* and *"go by priority and concentrate on the goal in mind"*.

## W7 — Don't reinvent what KiCad, Wokwi or tscircuit already do

Check whether it exists before building it. If it exists and works, lift or wrap it.

**Origin:** Petr, explicit. Vindicated immediately: a plan to import KiCad footprints was killed
when 18 of 27 were shown to convert to geometry identical to what already existed.

**Its other edge:** the bin's `circuit-to-wokwi` is 1645 lines of tested TypeScript that spark
does not have. Not reinventing means moving it, not rewriting it.

## W8 — Commit continuously, push often

Every landed piece of work is a commit whose message says what was wrong and why the fix is right.
The log is the team's memory; observers read it to find what nobody wrote down.

**Origin:** Petr, and `git checkout` is not an undo.

## W9 — An observer's claim is a hypothesis until reproduced

Several have been confidently wrong in ways that would have buried real defects. Reproduce, then
act. `rejected` is a real outcome and stays on the record so the same wrong claim is not raised
every run.

**Origin:** one council's central claim changed the roadmap and was right; another's verdict on
two of nine findings was wrong in a way that would have buried both.

## W10 — Simulation minutes are a budget, not a resource

~21 of 50 free Wokwi minutes remain. One scenario per question. Prefer any path that runs locally.

**Origin:** Petr, explicit: *"lets not waste the simulation minutes we already only have 21 of 50
free"*.

## W11 — Nobody but the Product Owner reorders the backlog

Agents and the facilitator propose, ranked, with reasons and costs. Petr decides. An agent that
reports something is "high priority" is reporting its own opinion and must label it as such.

**Origin:** this is what Product Owner means, and it was worth writing down because for two days
the ordering was done by whoever was typing.
