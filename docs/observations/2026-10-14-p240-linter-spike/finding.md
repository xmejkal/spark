# P240 spike: a linter for spark and for MicroPython projects

Issue: https://github.com/xmejkal/spark/issues/242. Run on 2026-10-14 with ruff 0.17.0 in a throwaway venv.

## Short version

Use ruff. It is one free local tool that lints and formats, and it reads its settings from `pyproject.toml`.
Add it as a small gate with a narrow rule set (`F`, `E9`, `B`) so it passes today, and widen the rules one code at a time. Leave MicroPython type stubs for later, because ruff already lints firmware files well enough.

## 1. The tool for spark's Python

Ruff replaces flake8, isort, pyupgrade and Black in one binary, with 800+ rules and config in `pyproject.toml`
(https://pypi.org/project/ruff/, https://github.com/astral-sh/ruff). One `pip install ruff` or `brew install ruff` adds it.
Pylint is slow and needs plugins. Flake8 only lints, so spark would need Black and isort too. That is three tools for
one job, which breaks the "one tool per job" rule.

## 2. MicroPython

Ruff treats firmware as plain Python. `import machine` and `micropython.const` are only imports to it. Decorators such as
`@micropython.native` are only decorators. The one firmware file in the repo
(`tests/data/breadboard/button-light/firmware/main.py`) gave 2 findings with the small rule set: import sorting only.
Ruff reports no false positives for MicroPython names, because it does not resolve imports.

Type stubs exist. Jos Verlinde's `micropython-stubs` ships PEP 561 stub packages on PyPI, such as `micropython-esp32-stubs`,
and its docs cover Pyright, mypy and Ruff setups (https://github.com/Josverl/micropython-stubs,
https://micropython-stubs.readthedocs.io/en/main/11_install_stubs.html). They need a type checker plus a `typings`
folder per project. That is heavy for a first step. It earns its place only once spark's firmware grows past a few
files. Not now.

## 3. The real run

Command base: `ruff check --isolated --no-cache --target-version py310` on `scripts tools tests`
(105 `.py` files, `node_modules` excluded). No repo file changed.

| Run | Result |
|---|---|
| Ruff 0.17 default rules | 1,940 findings. Top: UP031 1,277 (printf strings), RUF100 197, F401 96, I001 84, PLW1510 62, RUF059 53 |
| Small set E,F,W,I,B,UP at 120 | 3,147 findings. E501 1,579, UP031 1,277, F401 96, I001 84, E702 39, B904 20, E401 18, B905 9, E741 8, B023 7, small rest |
| Same set minus E501 and UP031 | 291 findings, 199 auto-fixable |
| `F` only | 98 findings: F401 96, F841 2 |
| Real-bug codes (E9, F63, F7, F82, F811, F821) | 0 findings, All checks passed |
| Firmware `main.py`, default and small set | 2 findings (I001), both fixable |
| `ruff format --check` at 120 | 99 of 117 files would change (117 files; the count differs from 105 because the formatter also counts other Python files) |
| `ruff format --check` at 88 | 103 of 117 files would change |

Reading: the code has no real bugs of the undefined-name kind. The noise is style. spark writes `%` formatting
(UP031), long lines (1,673 lines over 120) and `# noqa: E402 - reason` comments that ruff warns it cannot parse.
Do not adopt the formatter now. It would rewrite 99 files and bury `git blame`. Do not adopt line length or UP031.

## 4. The cost to add it

Config, in a new `pyproject.toml` (6 lines):

```toml
[tool.ruff]
target-version = "py310"
line-length = 120
extend-exclude = ["tools/circuit-to-wokwi/node_modules"]
[tool.ruff.lint]
select = ["E9", "F", "B"]
```

Day one needs the 96 F401 and 2 F841 fixed. Most F401 are test imports that exist for side effects, so mark them
with `# noqa: F401` where intended (`ruff check --fix` removes the rest). B is optional until B904 (20) is triaged.

Push hook: `tools/check_commit.py` runs `python -m unittest discover` in `measure()` on the archived tree. Add one
`subprocess.run([sys.executable, "-m", "ruff", "check", "."], cwd=tree)` beside it and fold its verdict into the gate
line. If ruff is not installed, report "could not run", never a pass (the rule in `docs/guide/agents.md`).

Projects from `/spark:init`: init writes rules and brief files today and no tool config. Ruff for a project is a
small `ruff.toml` (target py310 is wrong there: MicroPython, so `select = ["E9", "F"]` only) that init could write
when the project holds a `firmware/` folder. Offer it, do not force it.

`data/tools.json`: yes, name it. Add a `linter` role pointing to a `ruff` entry (`kind: path`, `exe: ruff`,
`install`: `brew install ruff`, `pip install ruff`), so `/spark:setup` can show and install it and a person can swap
the tool. Optional, never required for a build.

## Proposed follow-up story: "Spark lints its own Python with ruff"

Done when: a push fails on an undefined name or an unused import, and says so in one line.

1. Add `pyproject.toml` with the lines above. Fix or mark the 98 `F` findings. One PR.
2. Add the ruff step to `tools/check_commit.py` with a test for "ruff missing" = could-not-run.
3. Add the `ruff` entry and `linter` role to `data/tools.json`, and a line in `docs/guide/developing.md`, the README table and `--help`.
4. Widen: B (triage B904, B905, B023), then I001 with `--fix`. Each code is its own small PR.
5. Later, own stories: a `ruff.toml` written by `/spark:init` for firmware folders. Then the MicroPython stubs with Pyright.
