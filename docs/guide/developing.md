# Developing spark

How spark's own code is tested and gated, and where the work is planned.

## The tests

```sh
python3 -m unittest discover -s tests -t tests
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
- every script a command runs starts with its shebang.

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
- the size of `scripts/`;
- the work board's limits, which [the flow's table](../../scrum/README.md#the-flow--an-items-stages) holds
  ([the board](../../GLOSSARY.md#the-board)), and that every open item has a Needed by and a slice. With no `gh` or
  network, the board part says skipped and passes.

From a push on 2026-10-05:

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
264a9b7 as committed: Ran 1144 tests in 22.777s / OK (skipped=1); 562 mutation(s) in 93 table(s): every anchor present, once
  scripts/: 5,529 code lines (+0 since origin/main)
  backlog: 28 open, the limits hold
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

The team's own tools sit beside the gate:

- [`tools/board.py`](../../tools/board.py): the state of the work at every session start, and the day-close;
- [`scripts/cost.py`](../../scripts/cost.py): the cost of one research run, read from its transcript; `parts.py --tally`
  says a whole project's.
