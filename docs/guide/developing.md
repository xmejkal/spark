# Developing spark

How spark's own code is tested and gated, and where the work is planned.

## The tests

```sh
python3 -m unittest discover -s tests -t tests
```

The count is whatever that prints. A number written into the README rotted three times in four days, so none is
written here.

**The rule the tests follow: a test must run the thing, not read it.**

- No assertion on source text.
- None that is an arithmetic identity of the function under test.
- Every check is exercised through the runner, with an input that makes it fail.

The rule exists because of one test, written to catch "a check nobody invokes". It asserted that a string appeared
in the runner's source. That verified the check was named, not that it ran, and it stayed green for the whole life of
the bug it was written to prevent.

**The second rule: every fix is mutation-tested.**

```sh
python3 tools/mutate.py tests/mutations/p104-docs.json
```

[`tools/mutate.py`](../../tools/mutate.py) puts each defect in a table back into the code, and must report every one
caught. A mutation the suite does not notice is a missing test. A fixture too weak to see one is fixed, rather than the
mutation dropped. The [glossary](../../GLOSSARY.md#mutation-and-the-mutation-table) has the words.

## The gate before every push

[`tools/pre-push`](../../tools/pre-push) runs [`tools/check_commit.py`](../../tools/check_commit.py) on the tree as
committed, not the working tree. It measures `HEAD` even when another branch is pushed; that is
[P106](https://github.com/xmejkal/spark/issues/39). Install it once per clone:

```sh
ln -sf ../../tools/pre-push .git/hooks/pre-push
```

It reports:

- the suite and every mutation anchor, as committed;
- the size of `scripts/`;
- the board's limits ([`tools/check_backlog.py`](../../tools/check_backlog.py)).

From a push on 2026-10-05:

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
264a9b7 as committed: Ran 1144 tests in 22.777s / OK (skipped=1); 562 mutation(s) in 93 table(s): every anchor present, once
  scripts/: 5,529 code lines (+0 since origin/main)
  backlog: 28 open, the limits hold
```

## The docs say only what is there

[`tools/check_docs.py`](../../tools/check_docs.py) reads `README.md`, `AGENTS.md` and these guides. The suite runs it
as `tests/test_docs.py`. It fails when the docs:

- name a command, script, skill or agent that does not exist;
- leave one that exists unlisted;
- show a flag its script's `--help` lacks;
- link a file or heading that is not there;
- paste an output without the date and version it ran on;
- carry a personal path;
- give a version other than the one `.claude-plugin/plugin.json` ships.

A ` ```sh ` block marked `<!-- runs: exit N -->` is run in an empty project, with a store of its own, and must exit
`N`.

When a step of the [journey](journey.md) changes what it does, the change that does it also updates the journey guide
and the README's *What works today*.

## Where the work is planned

Every item is an issue on [spark's board](https://github.com/users/xmejkal/projects/2). The flow, the stages and their
limits, and the cadences are in [`scrum/README.md`](../../scrum/README.md). The words the team uses its own way are
in the [glossary](../../GLOSSARY.md).

The team's own tools sit beside the gate:

- [`tools/board.py`](../../tools/board.py): the state of the work at every session start, and the day-close;
- [`tools/research_cost.py`](../../tools/research_cost.py): the cost of one research run, read from its transcript.
