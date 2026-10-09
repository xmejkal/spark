# Working agreements

The rules the team actually runs on. Each one names **where it came from**, because a rule whose
origin is forgotten is the first one somebody argues away.

Ten are numbered agreements: W1, W2, W3, W6, W8, W13, W14, W15, W16 and W19. Every other number keeps its heading,
because other pages cite the numbers, and under it one dated line says where its rule went: onto the PO's role card,
into `DECISIONS.md` as a product rule, into another agreement, or into [the habits](#habits--no-command-judges-these)
at the end, which no command can judge. The cut is the process design's §3, accepted by the PO on 2026-10-06
([`docs/2026-10-06-process-design.md`](../docs/2026-10-06-process-design.md)); P146 carried it out on 2026-10-09. How
a rule changes is [the last section](#how-a-rule-changes).

---

## W1 — A check that could not look must never read as a check that passed

Four outcomes, never two: `ok` · `problems` · `could-not-run` · `skipped`. It binds the team's own gates and every
agent's report as much as the product's checks: a gate, a review or a read that could not look says so, with its
cause, and never reports a pass over what it did not see.

**The one written exception is the board check in the pre-push gate.** With no `gh` or no network,
`tools/check_backlog.py` prints `could-not-run` with its cause and lets the push through, because the gate must work
offline. A partial look — the board read, but not its tasks' parent stories, or not the bin's board — is said in a
line with its cause, and does not stop the push either. Both are said, never read as checked (P146).

**Origin:** the runner reported `ok` for a flagship check that called a function which had never
existed. Six more instances have been found since, in different files, by different people.

**How we know it holds:** the status is decided in one place, `answer()` and `status_of()` in `scripts/outcomes.py`
(moved there from `check_all.py` by P42; `check_all.py` imports them), so `ok` cannot be reached while anything went
unchecked; `skipped` is `check_all.py`'s own fourth word, for a check nobody asked for. `check_spine.py` exits 2 rather
than 0 when it could not be exercised.

## W2 — A test must run the thing, not read it

No assertion on source text. No assertion that is an arithmetic identity of the function under
test.

**Origin:** a test asserted `load("check_design")` appeared in the runner's source. The string was
there; the call beneath it named a function that did not exist. The test was green for the entire
life of the defect — it verified the check was *named*, not that it *ran*.

**Mechanical since P54 (2026-10-01):** `tests/test_self_confirmation.py` fails when a test reads a
module-under-test constant that is not shared vocabulary and has no written reason, and when a
shipped file is named by no mutation table and has no written reason. Its first catch:
`test_flash_image` found the filesystem at `flash_image.FILESYSTEM_OFFSET` — and passed with it
moved to an offset MicroPython never reads.

## W3 — Mutation testing is the acceptance bar

Re-introduce the defect; the suite must go red. Before commit, not after somebody finds it again.

The defect goes into a mutation table in `tests/mutations/`. `tools/mutate.py` puts each one back into the code and
names every mutation the suite does not notice — a missing test. The pre-push gate checks, on the tree as committed,
that every mutation's anchor is still there, once (`tools/check_commit.py`), and every table runs in one sweep when an
epic is done ([the Definition of Done](README.md#definition-of-done)).

**A fixture that cannot see the defect is the defect** (W12, merged here 2026-10-09). When a mutation escapes, the
first question is whether the fixture could have seen it at all. Four escapes in Sprint 3 were exactly that — three
LEDs never reached the tie a penalty breaks; a fixture with no placeholder made two swapped sections invisible — and
each was fixed by strengthening the fixture. The mutation stays in the table. Dropping a mutation because "the test
cannot see that" is dropping the test.

**Origin:** repeatedly, a rule was found to have no test at all while its file had many. The fixture clause: R3.1,
2026-09-29 — the tool reports the escape, and this says what to do with it.

## W4 — Never change a test to make it pass

*Moved 2026-10-09 (P146) to [the habits below](#habits--no-command-judges-these).*

## W5 — State the scope of an assertion

*Moved 2026-10-09 (P146) to [DECISIONS.md](../DECISIONS.md#product-rules) — "Product rules".*

## W6 — Finish before starting

The board's limits are the rule: two cards in each working stage — Discovery, Design, Build, Review — five in Ready,
and at most four in flight across the working stages (the PO's call of 2026-10-06 evening, after the first day at the
cap of three). An epic counts in Discovery and Design only, where it is the work itself; a plan's task rides on its
open story, and a task with no open parent story counts as a card; every other card counts. The expedite lane opens
on the PO's word only, for one card at a time across both boards, labelled `expedite`: it may take its working stage,
and the flight, one over its limit — Ready never. The bin's cards in a working stage fly in the same four, except one labelled
`bench`, the PO's own hands; they fill none of spark's stages. `tools/check_backlog.py` reads both boards at every push
and fails it when a limit breaks or two open cards carry `expedite`, so this holds by command, not by memory (P102a,
2026-10-05; the limits raised at the PO's word on 2026-10-06, and again that evening; the counting rules, the lane and
the bin's cards built by P146 on 2026-10-09). One part no command sees: a card stands in its working stage while any
work runs on it (W19). [The flow](README.md#the-flow--an-items-stages) has each stage's entry and exit.

**Origin:** Petr, twice: *"make sure you often prioritize your work, finish before moving on to
too many things at the same time"* and *"go by priority and concentrate on the goal in mind"*.

## W7 — Don't reinvent what KiCad, Wokwi or tscircuit already do

*Merged 2026-10-09 (P146) into [W14](#w14--pull-never-push).*

## W8 — Commit continuously, push often

Every landed piece of work is a commit whose message says what was wrong and why the fix is right.
The log is the team's memory; an outside audit reads it to find what nobody wrote down.

**Every change reaches `main` by a pull request that closes its card** (P146, the process design's §3). It is how the
team has worked since 2026-10-05: since then, every commit on the first-parent line of either repository's `main` is a
pull request's merge. It replaces the PO's rule of 2026-10-04 — big items by pull request, small fixes and scrum
updates straight to `main`. The pull request says `Closes #N` (W19), the council runs on it before the merge, and the
PO merges on Claude's "ready to merge" ([the flow](README.md#the-flow--an-items-stages), Review).

**Branch protection** on the `main` of both repositories, enforced for admins, is decision 1 (a), the PO's of
2026-10-06. Once set, GitHub refuses a direct push to either `main`. It is not set today (checked 2026-10-09 with `gh api`: neither
repository's `main` has a ruleset or branch protection); it is set on the PO's yes — Part C of
[P146's plan](../docs/2026-10-09-p146-process-plan.md#part-c--the-three-guards-and-the-board-field-the-pos-settings-nothing-changes-without-his-yes).
Until then the rule holds by practice, not by a setting.

**Origin:** Petr, and `git checkout` is not an undo.

## W9 — An observer's claim is a hypothesis until reproduced

*Moved 2026-10-09 (P146) to [the habits below](#habits--no-command-judges-these).*

## W10 — Simulation minutes are a budget, not a resource

*Moved 2026-10-09 (P146) to [scrum/TEAM.md](TEAM.md#the-role-cards) — the PO's card.*

## W11 — Nobody but the Product Owner reorders the backlog

*Moved 2026-10-09 (P146) to [scrum/TEAM.md](TEAM.md#the-role-cards) — the PO's card.*

## W12 — A fixture that cannot see the defect is the defect

*Merged 2026-10-09 (P146) into [W3](#w3--mutation-testing-is-the-acceptance-bar).*

## W13 — A number enters a message only after its output is read

A count, a hash, a verdict ("the chain runs end to end") goes into a commit message, a card's comment or a status
update only in a later call than the command that produced it, copied from output that is on the screen — **and
measured on the tree being committed**: `check_commit.py` archives `HEAD` and runs the suite and the anchors there
before every push. A commit's message said 589 OK while the tree it held ran 562 FAILED, because the run was on the
working tree and the file it imported was staged one commit later (close audit C3). The gate measures `HEAD` even when
another branch is pushed; measuring the ref being pushed is [P106](https://github.com/xmejkal/spark/issues/39), not
built yet. And a commit is made only when every step before it exited 0 — a chain that commits after a failed edit
writes a message about edits that never happened (`cdc7c81`). A value proof in a gated chain asserts the verdict
string, never the presence of output.

**A word is checked the way a number is** (W17, merged here 2026-10-09). A closing comment, a status update or a
commit's first line is checked against the diff or the output it summarises: "moved" means the old copy is gone,
"fixed" means the gap's own command now passes, "one home" means a grep finds one, "unchanged" means the file was
regenerated and compared. The v1 close audit found five summary claims false — "one home" (D9), "unchanged" (D13),
"moving" (D19), "fixed" (D21), "six fixed" over a list of seven (D22) — while every count copied from a run held: the
words were the numbers in disguise. Written 2026-09-30 (R5.1).

**An estimate says so** (W20's clause, merged here 2026-10-09): a number that has not been run carries the word
*estimate*, and the measured one replaces it in the same table. `docs/2026-09-30-refactoring-architecture.md` put
**−45 code lines** for P42 in the same table as measured facts; it came to −8. P35 was estimated at −40 and measured
−22, P29 at +20 and measured +22.

**Origin:** R3.5 said this as a rule about care on the morning of 2026-09-29 and was broken three
times before nightfall — 533 for 532, "reaches end to end" over "the chain is broken", 12 and 10 for
11 and 9 — every time by a message composed in the same command as the run. R4.1 makes it a rule
about sequence, which is the form that held for the rest of the day.

## W14 — Pull, never push

**Build only what is pulled, and reuse first.** Nothing enters the plugin unless a real design is blocked without it
that week, and the card names that design in its *Needed by*. A capability designed on paper — a review loop, an eval
harness, a research agent — is not built until a project reaches for it.

**This is Ready's entry policy** ([the flow](README.md#the-flow--an-items-stages)). Ready is the commitment: a card
enters it with a *Needed by* that names the blocked design, a slice and a *Value proven by*. In Idea, Discovery and
Design a card decides whether to build, and is asked for none of them. The push gate reads both boards — spark's
stages and limits, and the bin's cards in the same flight total — and fails the push on a spark card in Ready, Build or
Review with no *Needed by* or no slice (`tools/check_backlog.py`). The bin's cards are asked for neither, and no
command checks a *Value proven by*.

**Reuse first** (W7, merged here 2026-10-09): before building something, check whether KiCad, Wokwi or tscircuit
already does it; if it exists and works, lift or wrap it. Petr's rule, vindicated at once: a plan to import KiCad
footprints was killed when 18 of 27 were shown to convert to geometry identical to what already existed. Its other
edge: the bin's `circuit-to-wokwi` was tested TypeScript that spark did not have, and it was moved, not rewritten — its
1,307 lines of core came into spark as `tools/circuit-to-wokwi` (P32a), while the bin's knowledge of its own board
stayed in the bin.

**Origin:** 2026-09-29, when a third of the repository was deleted as unused. Every piece of it
had been built because it was designed, not because a design needed it.

## W15 — An orphan fails the suite

Every script is named by a command, a skill, an agent, the README or a project's Makefile, or is
imported by another script; every skill and agent is named where a user looks.
`tests/test_orphans.py` holds all of it, so dead code cannot accumulate silently again — every piece
cut on 09-29 had tests, and looked alive.

**The size is said at every push, with its reason; refactor before growing** (W15b, merged here 2026-10-09). The
`scripts/` size counts code lines only: docstrings, comments and blanks are free, because the prose recording why a
fix is shaped as it is, is the most valuable thing in this repository. **It is a number, not a cap (P99, the PO,
2026-10-04)**, and there is no line budget: `tests/test_orphans.py` holds none (amended 2026-10-08). The pre-push gate
prints the size with its growth since `origin/main` (`scripts/: N code lines (+M since origin/main)`); a card's
closing comment quotes that line and says why ([the Definition of Done](README.md#definition-of-done), clause 7), and
the epic's review lists them. The cap it replaced failed the suite: P95 raised it six times, each time to whatever had
been measured, and it prompted one refactor of two lines — what caught bloat there was the reviews and the orphan
tests above. When a card grows a lot, the first question is still whether the same behaviour fits in less code: the
three-outcome verdict was written out in six scripts and one copy was wrong (P34 found it; P42 gave it one home).

## W15b — The size is said at every push, with its reason; refactor before growing

*Merged 2026-10-09 (P146) into [W15](#w15--an-orphan-fails-the-suite).*

## W16 — A replacement deletes what it replaces, in the same commit

When a new path replaces an old one — a file format, a check, a command — the old one goes in the
same commit. Two formats for one thing is a bug, not a transition: `design.json` and `check_design`
lived beside the requirements chain for four days, and the item "the two tools disagree" existed
only because both did.

## W17 — A summary claims no more than what it summarises

*Merged 2026-10-09 (P146) into [W13](#w13--a-number-enters-a-message-only-after-its-output-is-read).*

## W20 — An item's own acceptance line is a hypothesis until reproduced

*Merged 2026-10-09 (P146) into W9, now [a habit below](#habits--no-command-judges-these); its estimate clause into
[W13](#w13--a-number-enters-a-message-only-after-its-output-is-read).*

## W19 — The item exists before the work starts

If work is not on the board, it is not happening; W19 says when. An issue is created on the project, with its
*Needed by* and *Value proven by*, **before** the first command of the work is run, including for work that only
produces a document — an audit, an architecture, a piece of research — and the pull request that delivers it says
`Closes #N` (W8; since 2026-10-05, P102a). The item may be a single paragraph, and it may be refined once the work
reveals its shape, but it exists first, so the work can be tracked, sized, and stopped.

**And the card stands in its working stage before any agent starts on it** (P146): a read moves its card to
Discovery, the spec council runs on a card in Design, the plan's agents on one in Build, the final review on one in
Review — one run per card at a time ([runs](README.md#runs-reads-councils-reviews)). A run on a card in Idea is work
the limits cannot see.

**The launch hook** is decision 1 (a), the PO's of 2026-10-06: a hook that refuses an agent launch unless its
description names a card standing in a working stage. It is not set today (checked 2026-10-09: no `PreToolUse` hook
in the PO's settings); it is set on his yes — Part C of
[P146's plan](../docs/2026-10-09-p146-process-plan.md#part-c--the-three-guards-and-the-board-field-the-pos-settings-nothing-changes-without-his-yes),
which prepares it as a check that the launch names a card. Even set, it cannot see agents inside a workflow.

Written 2026-09-30, at the PO's word — "whenever we want to do something, let's first make sure
the PBI is created, so we can keep track, really just like scrum" — after an architecture review
was set going with no item behind it. The stage clause came with P146: reads had run on Idea cards despite this rule
(the process design's §2).

## W18 — Refinement is the team's, and the PO has the last word before the order is fixed

*Merged 2026-10-09 (P146) into the Design and Ready rows of [the flow](README.md#the-flow--an-items-stages); its "one
sitting" is now the [service level](README.md#the-cadences-and-what-each-one-leaves).*

## W21 — Keep a datum only if a decision rests on it

*Moved 2026-10-09 (P146) to [DECISIONS.md](../DECISIONS.md#product-rules) — "Product rules".*

## Habits — no command judges these

Two rules no command can judge, so they live here, unnumbered. They were W4 and W9 until 2026-10-09 (P146), and those
headings above point here.

**Never change a test to make it pass** (W4). Change the decision first; the test follows the decision. If the test
is wrong, say why in the docstring and change its *premise*, not its assertion. Claude carries it, in the PO's words,
into every implementer's and reviewer's brief.

*Origin:* Petr, verbatim: *"always never just change the test so that it passes or even just
delete it or similar instead of actually finding everything and be open about everything"*. It worked correctly on
2026-09-25: `test_every_shipped_part_can_produce_signals` required every part to ask the host for a pin, which a power
inlet never does. The premise was wrong for a whole category, so the rule underneath was restated — a part must ask
for a pin *or* carry a rail — and the docstring records why.

**Every claim is a hypothesis until reproduced** (W9, with W20) — an observer's, an agent's, a reviewer's, and our
own. Several have been confidently wrong in ways that would have buried real defects. Reproduce, then act. A refuted
claim stays in the run's comment on its card ([runs](README.md#runs-reads-councils-reviews)): `rejected` is a real
outcome, and it stays on the record so the same wrong claim is not raised every run.

*Origin:* one council's central claim changed the roadmap and was right; another's verdict on two of nine findings was
wrong in a way that would have buried both.

**An item's own acceptance line is such a claim** (W20, 2026-09-30); W9 had said it of an observer's only. P45's
line asked `init` to write the DS3231's two bus lines, whose module record says *"Add NO pull-ups: the module carries
4.7 k on SDA and SCL"* — met as written, it would have shipped a check that fires on a **correct** board, the one
failure this product exists to prevent. P33 shipped: its `Value proven by` line, `npm install` in a fresh project,
failed, because `init` pinned `@tscircuit/cli@0.0.2600`, a version of the **`tscircuit`** package, and the item was
marked DONE without its own proof command being run on a machine with no global CLI on PATH. And P50's proof line
asked an isolated agent to rediscover three escapes written down in `scrum/SPRINT.md`, readable by any agent with
`Read`: an open-book exam scored as isolation. So: **before an acceptance line is relied on, reproduce the state it
assumes** — or mark it unverified, the way a part record marks a fact nobody has confirmed. An item may be written with
an unreproduced criterion; it may not be *closed* on one.

## How a rule changes

By a PR whose card quotes the PO's yes, with a dated line on the rule. This replaces 'retired in `RETROSPECTIVES.md`',
which was skipped twice in the week of 2026-10-06.
