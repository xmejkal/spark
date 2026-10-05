# The words this repository uses

Six sprints built a private vocabulary. Most of these words are ordinary English somewhere else
and mean something narrower here, and the person most likely to need them is the one who has read
none of the commit messages.

Each entry gives the **failure that produced the word**, not a definition in the abstract. That is
the same standard as `scrum/WORKING_AGREEMENTS.md`: a word without its scar is not memorable, and
worse, it is not persuasive — you will delete the rule the first time it is inconvenient.

---

## The checks

### The three outcomes — `ok`, `problems`, `could-not-run`

What every command exits with: **0**, **1**, **2**. They live in `scripts/outcomes.py`, which is
the only place a verdict is decided, so no command can invent its own.

The third one is most of this product's reason for existing. **A check that could not look must
never read as a check that passed.** Before this was one rule in one file, `check_physics` would
print `status: ok`, exit 0, and hand you a board where every finding it emitted was
`could-not-run` — it had examined nothing and said "fine". That is worse than no check at all,
because you now believe something.

### `skipped` — the fourth word, and only `check_all` has it

"I was not asked" is not "I was asked and could not look". A check whose inputs were never
supplied is `skipped`; a check that was given what it needs and still could not examine the thing
is `could-not-run`. Conflating them is how a review calls itself complete while its flagship check
was never run — which happened here, because a documented command passed five paths and got two
wrong.

### `needs-measurement` and `advisory` — findings that do not change the outcome

Both reach `check_all` as a `?` line and leave the status where it was. **`needs-measurement`**: a
real question about the board that needs a number nobody has taken — a rail's current, a pour's
continuity. **`advisory`**: something the board house will make, but under what it recommends — a
0.225 mm ring on a 2 mm-pitch JST PH, over JLCPCB's 0.18 mm minimum and under its 0.25 mm
recommendation. It was a FAIL until P57, which is how the documented example failed spark's own
check on a real connector: a recommendation enforced as a limit is a false alarm with a source.

### The spine, or the chain — `scripts/check_spine.py`

The whole flow, end to end, stopping at the first stage that cannot produce input for the next:

```
idea -> parts -> pin map -> schematic -> footprint -> build -> simulation
```

It exists because every stage passing on its own proves nothing about the stages fitting together.
The defect that prompted it: a board that built, routed, and reported zero errors, with a
microcontroller sharing a net with **none of its 32 pins**.

### `make check` — a project's own gate

Not this repository's; the board project's. In the smart bin it is: the board definitions meet
their contract, they match the vendor's own pin header, the board builds, it is fabricable, the
fab package exports, the order matches the schematic, physics holds, and the written rules hold in
the netlist that was built.

It is allowed to be red for a stated reason. The bin's is red today on exactly one line: nobody
has measured the motor's current, so the rules file states the driver's *limit*, which is not a
measurement, and the check says so rather than passing it.

---

## Proving the tests are real

### Mutation, and the mutation table

The ordinary question a suite answers is *does the code work*. A mutation asks the harder one:
**would these tests notice if it stopped working?**

After a fix, you write down how to put that exact defect **back**, and the tool checks the suite
goes **red**. A table is JSON, one entry per defect, in `tests/mutations/<item>.json` (tables written before 2026-10-05 carry their sprint: `sprint-10-p96-…`):

```json
{"file":    "scripts/emit_board.py",
 "name":    "a receiving pad is wired whether or not anything drives its rail",
 "find":    "        yield pad, net, bool(net) and (not receives or net in driven)",
 "replace": "        yield pad, net, bool(net)"}
```

`tools/mutate.py` applies each one, runs the suite, restores the file, and reports. It was
enforced by memory for two sprints, which failed the way memory fails: about thirty mutations run
by hand in one sprint, and **two escaped** — each surviving a green suite until somebody happened
to try it.

### Anchor, and re-anchoring

The `find` line is the **anchor**: the exact text the mutation attaches to. It must occur
**exactly once**, or the mutation is refused before anything runs — a substitution that silently
matched nothing would run an unmutated suite and report on a change it never made, which reads
like a pass.

**When you refactor, the anchor stops matching, and that is the point.** Rewriting a function
breaks every mutation pointed at it; `mutate.py --anchors` fails and names them, and you must
**re-anchor** — point the old guard at the new code and re-run it to prove it still bites. Without
that, a refactor quietly deletes your guards while the suite stays green. It is the single thing
that makes moving this code around safe, and it fired three times in one day during Sprint 6.

### Caught, escaped, refused

| | means | what to do |
| --- | --- | --- |
| **caught** | the suite went red | nothing — the test is real |
| **escaped** | the suite stayed **green** | **a missing test.** Strengthen the fixture |
| **refused** | the anchor did not match exactly once | fix the table; nothing ran |

And one line at the end: *the suite is green with the files restored*. Without it the whole run is
untrustworthy — something is left mutated, or was already broken.

**An escape is never closed by deleting the mutation** (W12). The defect was real; a fixture that
cannot see it is itself the defect.

### Fixture

The small fake circuit, record or project a test is built on. Most escapes are a weak fixture
rather than a missing test file — the test existed, ran, and passed both before and after, because
its circuit never contained the thing the defect breaks.

### Characterisation test

A test that records what the code does **today**, not what it should do, so that a refactor cannot
change the answer without somebody noticing. `tests/test_json_contracts.py` is all of them: before
it, ten scripts offered `--json` and exactly one test passed the flag, asserting only the exit
code — any key in any payload could have been renamed with the suite still green.

### The commit gate — `tools/pre-push`

A git hook, installed once per clone, that runs `tools/check_commit.py` before a push leaves the
machine. It archives **the committed tree** and runs the suite and every mutation anchor against
*that*, not against your working copy — so uncommitted files cannot make it pass. It produces the
line quoted in every commit:

```
bec7b88 as committed: Ran 689 tests in 9.332s / OK; 176 mutation(s) in 37 table(s): every anchor present, once
```

`ln -sf ../../tools/pre-push .git/hooks/pre-push`. It exists because "runs at every commit" was,
for two sprints, enforced by nothing.

---

## Keeping the thing small

### The budget

`scripts/` must stay under a stated ceiling of **code** lines — docstrings, comments and blanks do
not count, because in this repository the prose is the product. When it pinches the order is
fixed: **refactor, then delete, then raise with a reason** (W15b). Raising it is allowed; raising
it silently is not.

### Orphan

A script nothing routes to and nothing imports; a skill or agent named nowhere a user would look.
`tests/test_orphans.py` fails on one, so dead code cannot accumulate quietly. A third of this
repository was cut in one night when this rule arrived.

### Needed by

Every open item on the board names the **design that needs it** — "pull, never push" (W14). No item is
built because it would be nice. `tools/check_backlog.py` fails a push on an open item whose *Needed by* is empty.

---

## Parts and records

### Record — and the three places one lives

A part or board is a JSON file of facts with sources. The same name can live in three places and
the nearest wins: the **project's** own `parts/`, then the plugin's **library**, then the
**catalog**.

### The catalog

Everything research has ever read, chosen or not — a record per candidate, its datasheet and
photo kept in the person's own store (`~/.local/share/spark/sources`, never in the plugin) and
pointed at from the record's `documents`, because links rot. Passing a part over does not throw the work away;
the record stays and names itself as an alternative.

### `verified`

`true` means **the vendor's own words at a cited URL**. Anything read off a photo, inferred, or
computed is `false`, with `where` saying how it was arrived at. A null is not a gap in the output;
it *is* the output, and a check reading one reports it as unverifiable rather than passing it.

### Stand-in, placeholder

A footprint, a Wokwi part or a chip that is **not the real thing**, recorded as such. An XT30 inlet
drawn as a JST because nobody had drawn the XT30 was once *measured*, and the tool reported a real
sounding defect about a part that is not on the board. A placeholder's findings are not dropped —
they become one `could-not-run` each, which is the difference between "not yet" and "fine".

### `host_parts` and `host_requirements`

What a module demands of the board it plugs into. `host_parts` is the **structured** half —
a pull-down here, a pull-up there, with resistance and reason — and the generator places and wires
them. `host_requirements` is the prose half, printed under the board for a human. The split
matters: it is how the tool knows an I2C bus is *this* board's to pull up rather than one the
module already handles itself.

---

## How the work is run

### Working agreement — W1, W2, … W21

Not principles adopted in advance. Each one is a **failure that happened here**, written down with
its evidence so it cannot recur quietly. `scrum/WORKING_AGREEMENTS.md`. When one is inconvenient,
read its evidence before deciding it is bureaucracy.

### The board

The backlog is two GitHub Projects — spark's (https://github.com/users/xmejkal/projects/2) and the bin's
(/projects/1) — since 2026-10-05 (P102a). Each item is an issue; its card moves **Idea → Discovery → Design → Ready
→ Build → Review → Done**, one item per working stage, at most two in flight, three in Ready. **The failure behind
it:** ten sprints, each re-planned around the items the PO added mid-sprint, and a sprint (10) that never closed
while other items were built in it — so "what are we doing now" had no answer a command could read.
`tools/check_backlog.py` fails a push that breaks a limit; the Markdown backlog is the frozen archive.

### Epic, story, task

An **epic** is an issue whose stories are its sub-issues; its progress bar is how an unfinished epic shows. A
**story** is what a person can do afterwards, proven by its *Value proven by*. A **task** is one step of a story's
plan — a sub-issue that rides on its story, with no slice or limit of its own.

### Day-close

One dated line at the end of each working day — what moved, what was proven, what is aging, the next card —
posted as a status update on the spark board (`tools/board.py close`, P102c). **The failure behind it:** sessions
that were compacted or interrupted restarted from memory; the close is the restart point, and a session that opens
with a working day unclosed writes it first.

### Cold test

Building an entirely new project with the plugin, the way a stranger would — the RC car, the
irrigation controller. They found 13 and 12 gaps, and **ten of the twelve were invisible to every
test in this repository**. Nothing else has that hit rate, because a test written by the author
tests what the author thought of.

### Intake, observation, audit

An outside reading — an agent that has not seen this conversation — writes a report into
`docs/observations/`, and every claim lands in that folder's `INDEX.md` as `raised`. **A claim is
a hypothesis until reproduced** (W9), and it earns its way onto the backlog by being reproduced,
with its need named. This is not ceremony: the v1 close audit made 33 claims and **11 were false**.

### The requirements file

The input to the whole chain: a board, a list of parts, and what the design has to do. Everything
downstream is derived from it, which is why `spark init` guesses nothing — a guessed number would
poison the one check that does arithmetic.
