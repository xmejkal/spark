# Developing spark

How spark's own code is tested and gated, and where the work is planned.

## The tests

```sh
python3 -m unittest discover -s tests
```

The count is whatever that prints. A count written into the README rotted three times in four days, so a count
appears only inside a dated output, like the push below.

**The rule the tests follow: a test must run the thing, not read it.**

- A test that finds a string in source proves the thing was named, not that it ran, so behaviour is proven by running
  it. `tests/test_check_all.py` forbids source-text assertions outright.
- None is an arithmetic identity of the function under test.
- Every check is run through the runner with an input whose answer is known, and each check's own suite gives it an
  input that makes it find a problem.

The rule exists because of one test, written to catch "a check nobody invokes". It asserted that a string appeared
in the runner's source. That verified the check was named, not that it ran, and it stayed green for the whole life of
the bug it was written to prevent.

The suite still reads source for rules about the code itself:

- no script imports unittest;
- only `store.py` spells the store's path;
- only `tools.py` names a tool's executable;
- no script restates a number that `data/fabrication.json` holds;
- every script a command runs starts with its shebang;
- every test module has, after its standard-library imports and before anything else, these two lines
  ([P172](https://github.com/xmejkal/spark/issues/112)):

  ```python
  sys.path.insert(0, str(Path(__file__).resolve().parent))
  import suite_temp
  ```

  `tests/suite_temp.py` gives the test process one temp folder and removes it when the process exits, so a test's
  `tempfile.mkdtemp()` needs no cleanup of its own. The first line lets `python3 -m unittest tests.test_x` find it.

`test_converter.py` also checks the converter's TypeScript, comments stripped, for default paths it must not have.

**The second rule: every fix is mutation-tested.**

```sh
python3 tools/mutate.py tests/mutations/p104-docs.json
```

[`tools/mutate.py`](../../tools/mutate.py) puts each defect in a table back into the code, and must report every one
caught. A mutation the suite does not notice is a missing test. A fixture too weak to see one is fixed, rather than the
mutation dropped. The [glossary](../../GLOSSARY.md#mutation-and-the-mutation-table) has the words.

## The commit gate, before every push

[`tools/pre-push`](../../tools/pre-push) runs [`tools/check_commit.py`](../../tools/check_commit.py) on the tree as
committed, not the working tree. It measures `HEAD` even when another branch is pushed; that is
[P106](https://github.com/xmejkal/spark/issues/39). The [glossary](../../GLOSSARY.md#the-commit-gate--toolspre-push)
has its story. Install it once per clone:

```sh
ln -sf ../../tools/pre-push .git/hooks/pre-push
```

It reports:

- the suite and every mutation anchor, as committed;
- what the suite left behind ([P172](https://github.com/xmejkal/spark/issues/112)): the suite runs with an empty temp
  folder of the gate's own, and anything left in it fails the push with one line,
  `temp: the suite left N entries behind (…) — P172`. A folder the gate cannot list is could-not-run, which exits 2
  and stops the push, unlike the board's could-not-run below. One run of the suite had left 2,291 entries, 26 MB, and
  the hook ran it at every push. The gate also removes its own archive of the commit, 6.2 MB, when it ends;
- the size of `scripts/`;
- the work board — spark's and the bin's, through your `gh` login ([the board](../../GLOSSARY.md#the-board)). It fails
  the push on:
  - a stage over its limit, or more than four cards in flight across both boards — the numbers and the counting rules
    are [the flow's table](../../scrum/README.md#the-flow--an-items-stages);
  - two open cards labelled `expedite`: the lane takes one card at a time;
  - a card that waits on someone (*Waiting on*) with no *Waiting since*, on either board, in any open stage;
  - a card of spark's in Ready, Build or Review with no *Needed by* or no slice.

  With no `gh` login or no network, the board part says could-not-run, with `gh`'s own reason, and passes. Two more
  looks it will not make ([P168](https://github.com/xmejkal/spark/issues/106), [P167](https://github.com/xmejkal/spark/issues/105)),
  each could-not-run that passes, never "the limits hold": it reads a board whole or judges nothing — `gh` stops at its
  `--limit`, so a board past the first ask's 500 is asked again with its own count, and one still short is
  `backlog: could-not-run — the spark board holds 501 items, 500 were read; the limits were not checked` (the bin's,
  read in part, is its unread line) — and it knows seven stages, Idea, Discovery, Design, Ready, Build, Review and Done,
  so a card in any other is `backlog: could-not-run — #4 P4 — x is in a stage the gate does not know: "Doing"; the
  limits were not checked`: a renamed stage is a decision, not a silent skip. A card with no *Status* (GitHub's "No
  status" column) is in Idea and said, `backlog: 3 card(s) have no stage: #3, #5, bin #20`; a board with no *Status* on
  any card is a changed field, could-not-run naming the shape.

From a push on 2026-10-05 (the gate's wording has changed since; the lines are a dated record, not today's output):

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
264a9b7 as committed: Ran 1144 tests in 22.777s / OK (skipped=1); 562 mutation(s) in 93 table(s): every anchor present, once
  scripts/: 5,529 code lines (+0 since origin/main)
  backlog: 28 open, the limits hold
```

Run the board part yourself — `--help` lists its rules and exit codes — and the status and the day-close beside it
(`--dry-run` posts nothing):

```sh
python3 tools/check_backlog.py
python3 tools/board.py status
python3 tools/board.py close --dry-run "the day's one line"
```

The gate on the live boards, then the status (the last close's line cut short here):

<!-- output: run 2026-10-09, spark 0.7.0 -->
```text
  backlog: 84 open, the limits hold; the bin: 22 open
```

<!-- output: run 2026-10-09, spark 0.7.0 -->
```text
spark — 84 open, the limits hold · trial check 2026-11-02
  in flight: Build P146 (#80) 3 d, Discovery P136 (#70) 3 d, Discovery P158 (#94) 1 d
  waits on the PO: R2.6 (#15) since 2026-10-05, 4 d !, P136 (#70) since 2026-10-06, 3 d, P146 (#80) since 2026-10-09, 0 d
  Ready: P143 (#77)
  ! Ready is down to 1 — propose an order for the PO
  open PRs: spark #104 P146: the process fits how we work — the gate's  (draft)
  last close 2026-10-08: P97 (store 1c) finished subagent-driven: …
```

A refusal: the gate's rules run on the board as `gh` printed it at the migration of 2026-10-05 (the suite's recording,
`tests/data/p102a-items.json`, with an empty bin board). Its one wait was never dated, so the gate exits 1 and a push would fail:

<!-- output: run 2026-10-09, spark 0.7.0 -->
```text
  backlog: 27 open, 1 problem(s); the bin: 0 open
    #15 R2.6 — A fourth cold test: waits on the PO since nobody knows — set Waiting since
```

The other refusals read the same way, one line each, as the suite expects them: `Build holds 3 (#1, #2, #3) — its
limit is 2: finish one before starting another`, `5 in flight (#1, #2, #3, #4, bin #19) — at most 4: finish one before
starting another`, `2 cards labelled expedite (#1, #2) — one at a time, on the PO's word`, and for a card with no slice
`#8 P8 — x: on no slice of the story map`. With no `gh` login:

<!-- output: run 2026-10-09, spark 0.7.0 -->
```text
  backlog: could-not-run — gh or the network could not be reached (To get started with GitHub CLI, please run:  gh auth login); the limits were not checked
```

## The docs name only what is there

[`tools/check_docs.py`](../../tools/check_docs.py) reads `README.md`, `AGENTS.md` and these guides. The suite runs it
as `tests/test_docs.py`. It fails when the docs:

- name a `/spark:` command or a `.py` script that does not exist;
- have a row in the commands guide's Skills or Agents table that names none;
- leave a command, skill or agent out of README.md or the commands guide;
- show a flag that its script's `--help` lacks;
- link a relative file or heading that is not there;
- paste an output without the date and version it ran on;
- carry a personal path;
- leave out of README.md the version that `.claude-plugin/plugin.json` ships.

A ` ```sh ` block marked `<!-- runs: exit N -->` is run in an empty project, with a store of its own, and must exit
`N`.

Nothing mechanical checks a skill or agent named in prose, an absolute link, or a second, wrong version; the council
reads those. Nor can it tell whether a step's status is still current. So when a step of the [journey](journey.md)
changes what it does, the change updates the journey guide and the README's *What works today*: item 8 of the
[Definition of Done](../../scrum/README.md#definition-of-done).

## Where the work is planned

Every item is an issue on [spark's board](https://github.com/users/xmejkal/projects/2). The flow, the stages and their
limits, and the cadences are in [`scrum/README.md`](../../scrum/README.md). The words the team uses its own way are
in the [glossary](../../GLOSSARY.md).

One more team tool sits beside the gate: [`tools/board.py`](../../tools/board.py). `python3 tools/board.py status`
prints the state of both boards at every session start (the PO's session-start hook runs it; it always exits 0). It
reads each board whole, 100 cards a page, and judges where a card stands by the gate's one rule: a board read in part,
or a card in a stage the gate does not know, makes the status one could-not-run line naming it, and a card with no
*Status* is said. `python3 tools/board.py close "the day's one line"` posts the day-close as a status update on spark's board — one a
day, a second refused with exit 1; `--dry-run` prints it and posts nothing. Each verb's `--help` says what it prints,
posts and refuses.

[`scripts/cost.py`](../../scripts/cost.py) is not a team tool. It ships with the plugin: `parts.py --step` and `--tally`
import it to count what a project's run cost, and on one transcript it says what that run cost
([how it works](how-it-works.md#the-libraries)).
