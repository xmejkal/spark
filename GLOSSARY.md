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

What every command exits with: **0**, **1**, **2**. They live in `scripts/outcomes.py`, which the
command-line scripts import, so no command spells its own. Not every script keeps to them yet: a crash exits 1, and
one script says `mismatch` for `problems` ([the guide for AI agents](docs/guide/agents.md#the-outcomes-and-their-exit-codes), P43).

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

The size of `scripts/`, counted in **code** lines — docstrings, comments and blanks do not count,
because in this repository the prose is the product. It is a number, not a cap (W15b, P99; the PO,
2026-10-04). There was a cap, and it failed the way a ceiling does: P95 raised it six times in one
item, each time to whatever had been measured, and it prompted one refactor of two lines. Now the
pre-push gate prints the size with its growth since `origin/main` (`scripts/: N code lines (+M since
origin/main)`), and an item's Done line says how many lines it added and why. When an item grows a
lot, the first question is whether the same behaviour fits in less code: **refactor before growing**.

### Orphan

A script nothing routes to and nothing imports; a skill or agent named nowhere a user would look.
`tests/test_orphans.py` fails on one, so dead code cannot accumulate quietly. A third of this
repository was cut in one night when this rule arrived.

### Needed by

Every open item on the board names the **design that needs it** — "pull, never push" (W14). No item is
built because it would be nice. `tools/check_backlog.py` fails a push on an open item whose *Needed by* is empty.

---

## Parts and records

### Record — and the four places one lives

A part or board is a JSON file of facts with sources. A part's record can live in four places and
the nearest wins: the **project's** own `parts/`, then the **shelf**, then the plugin's **library**,
then the **catalog**, which is read only when drafts are asked for. A board's record has two places:
the project's own `boards/`, then the library (`layers` in `scripts/store.py`).

### The catalog

Everything research has ever read, chosen or not — a record per candidate, its datasheet and
photo kept in the person's own store (`~/.local/share/spark/sources`, never in the plugin) and
pointed at from the record's `documents`, because links rot. Passing a part over does not throw the work away;
the record stays and names itself as an alternative.

### The shelf

Parts you chose before, copied from wherever they lived so that every project finds them: a `shelf/`
folder in [your store](#the-store), read after the project's own `parts/` and before the library.
A record gets there when a drawer entry links a record that lives only in another of your projects,
and when `parts.py --requirements` writes a file for a pick from the catalog or from another project.
It leaves behind on the way what is one person's story of the part — `owned`, `photo`, `photos`,
`sourcing` and `alternatives` (`SHELF_DROPS` in `scripts/parts.py`) — and, when it came from a
project, says which one and the record's digest (`based_on`). Parts only; a board has no shelf.

### `verified`

`true` means **the vendor's own words at a cited URL**. Anything read off a photo, inferred, or
computed is `false`, with `where` saying how it was arrived at. A null is not a gap in the output;
it *is* the output, and a check reading one should report it as unverifiable rather than pass it. Not
every check does yet ([what never to assume](docs/guide/agents.md#what-never-to-assume), P107).

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

### Owed, and broken

The two ways a record falls short, counted for each place by `parts.py --audit`. A record is **owed**
when it lacks a key every record needs or a fact the chain reads — `footprint`, `pin_order`,
`pin_order_proof`, `body_mm` or `simulation` (null, empty, or for `body_mm` without a numeric width
and height). It is **broken** when a value is present and wrong. A record grows when a stage needs a
fact, not before (W21), so owing is normal for a part nobody has built with yet. What it stops: a pick
that owes anything but `body_mm` stops `parts.py --requirements`, which names where to fill it
(`--fact-set` in the record's own home; spark's library is changed in spark's repository); a pick that
owes only `body_mm` is written with a placeholder-outline warning.

---

## What you own, and what a project picks

### The store

Everything spark keeps for you, in one folder outside every repository: `SPARK_HOME`, else
`XDG_DATA_HOME/spark`, else `~/.local/share/spark` ([what is in it](docs/guide/how-it-works.md#your-store)).
**The failure behind the one place:** its path was spelled out in two scripts and read once at import,
so the tests kept away from the real store only by patching sixteen constants by hand, and a test that
forgot one would have written into the person's store (P88). Now it is read on every call, and a
process running the tests gets a scratch one.

### The drawer

What you own: one small file per item in the store's `drawer/` folder, and a label is enough. It is an
index, not a place records are read from. An entry points at a record (`is`) when spark knows the part
by an exact part number, or when you say which record it is — a near number, two matches or a name
alone is a question for you, never a link — and at nothing otherwise. Owning never triggers research,
and every write sets a value the agent worked out and the dry run showed, so a retried write changes
nothing (`scripts/drawer.py`).
A record carries no `owned` and no `photo`: owning one is your fact, not the part's, and the contract
check refuses a record that holds either (`RETIRED` in `scripts/parts.py`).

### Pick, and reserve

A **pick** is the part, board or drawer entry a project chose for a need, written to its
`.spark/needs.json` and set only by `parts.py --pick`. To **reserve** is to mark how many of an owned
item the project uses (`used_in` on its drawer entry). Every `--pick` works the project's reservations
out again from all its picks, one piece for each, so a re-pick frees what it no longer picks, and it
never reserves past what you own or what another project holds, which it names. A pick you do not own
is "to get"; a pick that is a drawer entry with no record (a speaker, a battery) is reserved and not
placed on the board.

### History

`history.jsonl` in your store: one line for each event, appended and never shared, and an event whose
key is already there is not written again. The events are `step` (a project's step started, with the
Claude Code session it ran in), `reused` (a pick taken from your store, spark's library or another
project — not one from the project's own `parts/` or `boards/`), `passed_over` (a part you passed over,
with your reason, without any URL or price) and `built` (a board of a project on your list that built
end to end, with a digest of the facts the build read). It is there so that a project shows what it
cost and what came from reuse ([the tally](#tally)).

### Tally

`parts.py --tally <project>`: the cost line at the end of a project's run. How many picks, how many
came **from the store** (known to spark before the project — its library, your store, your projects;
that is not "owned", which is counted beside it), and the requests, documents and minutes the steps
cost, read from the Claude Code transcripts of the sessions they ran in, tool names and counts only.
**The failure behind it:** `cost.py`, given a transcript that named no time at all, once printed
`minutes 0` and exited 0 (fixed in f6a8e4d). The tally never turns what it could not read into a 0:
with no transcript of a step's session it says the cost was not counted, and exits 2.

---

## How the work is run

### Working agreement — W1, W2, … W21

Not principles adopted in advance. Each one is a **failure that happened here**, written down with
its evidence so it cannot recur quietly. `scrum/WORKING_AGREEMENTS.md`. When one is inconvenient,
read its evidence before deciding it is bureaucracy.

### The board

The backlog is two GitHub Projects — spark's (https://github.com/users/xmejkal/projects/2) and the bin's
(/projects/1) — since 2026-10-05 (P102a). Each item is an issue; its card moves **Idea → Discovery → Design → Ready
→ Build → Review → Done**, with limits on how many cards a stage may hold and on how many are in flight at once — the
numbers, and what counts toward them, are [the flow's table](scrum/README.md#the-flow--an-items-stages). **The failure
behind it:** the PO added items mid-sprint in 3 of the 6 sprints read closely, and Sprint 10 stayed open from 10-03
after work came in that it never planned — so "what are we doing now" had no answer a command could read (the design's
§9).
`tools/check_backlog.py` fails a push that breaks a limit on spark's board (when online); the Markdown backlog is the
frozen archive.

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
downstream is derived from it, which is why `/spark:init` guesses nothing — a guessed number would
poison the one check that does arithmetic.
