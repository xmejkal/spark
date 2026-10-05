# The README and its guides — Implementation Plan (P104)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** a README that leads with spark's journey and what works today, five guides in `docs/guide/`, an `AGENTS.md`,
and a check that fails the suite when the docs name what is not there.

**Architecture:** `tools/check_docs.py` holds the checks as pure functions from Markdown text to the sentences they
fail on, beside `check_backlog.py`. `tests/test_docs.py` feeds them literal Markdown (Task 1), then the real docs
(Task 7). The prose is written from facts gathered by running the journey (Task 2), guides first and the README last.

**Tech Stack:** Python 3 standard library, `unittest`, `tools/mutate.py`, Markdown with Mermaid (GitHub renders it).

**Spec:** `docs/2026-10-05-readme-design.md` (approved by the PO, 2026-10-05).

## Global Constraints

- **Every pasted output comes from a real run.** The line above its ` ```text ` block is
  `<!-- output: run YYYY-MM-DD, spark X.Y.Z -->`.
- **A runnable example** is a ` ```sh ` block with `<!-- runs: exit N -->` on the line above. Only light examples:
  no network and no board build. Its exit is that of its last command.
- **No number that rots:** a count appears only inside a dated output.
- **Nothing new is installed without the PO's yes. No Wokwi minutes are spent.**
- **A step that fails while the docs are written becomes a bug card** (label `bug`, Status Idea, on the spark board),
  and the docs say *not yet*. It is not fixed in P104.
- **The docs are public.** They name no personal path (`/Users/`, `/home/`, `/private/`) and no other checkout
  (`smartbin-local`), and carry no token, email, order number or price.
- **Tests and examples never touch `~/.local/share/spark`:** `SPARK_HOME` points at a temp directory.
- The README is about 120 lines: a target, not a cap. Every term spark uses its own way links to `GLOSSARY.md`.
  The Mermaid diagram has its sentence beside it.
- `GLOSSARY.md` changes only by links. The version line matches `.claude-plugin/plugin.json` (0.6.0 today).
- **Pushing:** branch `p104-readme` was cut after P105 (d4faf06), so it is safe to push. After a push, compare
  GitHub's head (`gh api repos/xmejkal/spark/branches/p104-readme`) with `git rev-parse HEAD`.
- **Commits** end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **A heading with backticks, a slash or a colon,** such as ``## `/spark:build` — one command``, gets GitHub's slug
   `sparkbuild--one-command`. A link to it must pass. *(Task 1:
   `test_an_anchor_follows_github_s_slug`)*
2. **A runnable example that hangs** (waiting for input or the network) is reported as not light; it does not hang
   the suite. *(Task 1: `test_a_runnable_example_that_hangs_is_named`)*
3. **A guide naming a file spark writes into a project** (`pins.py`) is not a missing script. *(Task 1:
   `test_a_file_spark_writes_into_a_project_may_be_named`)*
4. **A link to a folder** (`[parts](../../parts/)`) passes. *(Task 1: `test_a_link_to_a_folder_is_fine`)*
5. **A script whose `--help` fails** (an import error) says its flags could not be checked; it does not report each
   flag as missing. *(Task 1: `test_a_script_whose_help_fails_is_said_so`)*

---

### Task 1: The checks — `tools/check_docs.py`

**Files:**
- Create: `tools/check_docs.py`
- Create: `tests/test_docs.py`
- Create: `tests/mutations/p104-docs.json`

**Interfaces:**
- Produces:
  - `check_docs.problems(root=ROOT) -> list[str]`
  - `check_docs.doc_files(root) -> list[Path]`
  - `missing_names(text, root)`
  - `unlisted(root)`
  - `unknown_in_tables(text, root)`
  - `missing_flags(text, root, helps=None)`
  - `slug(heading)`
  - `broken_links(path, text)`
  - `undated_outputs(text)`
  - `failed_examples(text, root)`
  - `version_mismatch(readme, root)`
  - `personal_paths(path, text)`
  - `RUN_TIMEOUT`, `PROJECT_FILES`

- [ ] **Step 1: Write the failing tests** — `tests/test_docs.py`:

```python
"""P104: the docs name only what is there (docs/2026-10-05-readme-design.md §5)."""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import check_docs  # noqa: E402


def page(root, name, text):
    path = Path(root) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


class TheChecksTest(unittest.TestCase):
    def test_a_command_or_script_that_does_not_exist_is_named(self):
        said = check_docs.missing_names("run `/spark:build`, then `/spark:frobnicate`, check_all.py and frob.py")
        self.assertEqual(said, ["/spark:frobnicate names no command", "frob.py names no script"])

    def test_a_file_spark_writes_into_a_project_may_be_named(self):
        self.assertEqual(check_docs.missing_names("the project gets `pins.py`"), [])

    def test_every_command_skill_and_agent_must_be_listed(self):
        with tempfile.TemporaryDirectory() as root:
            for name in ("commands/build.md", "skills/spark-review/SKILL.md", "agents/part-finder.md"):
                page(root, name, "")
            page(root, "README.md", "/spark:build, spark-review, part-finder")
            page(root, "docs/guide/commands.md", "/spark:build, spark-review")
            self.assertEqual(check_docs.unlisted(Path(root)), ["docs/guide/commands.md does not name part-finder"])

    def test_a_table_row_naming_no_skill_or_agent_is_named(self):
        text = ("## Skills\n\n| skill | what |\n| --- | --- |\n| **spark-review** | x |\n| **spark-dream** | y |\n\n"
                "## Agents\n\n| agent | what |\n| --- | --- |\n| `part-finder` | z |\n")
        self.assertEqual(check_docs.unknown_in_tables(text), ["## Skills names spark-dream, which is no skill"])

    def test_a_flag_its_script_does_not_have_is_named(self):
        text = "```sh\npython3 scripts/check_all.py --project . --json --frob\n```\nand `board.py status --when-in DIR`"
        self.assertEqual(check_docs.missing_flags(text), ["check_all.py shows --frob, which its --help does not list"])

    def test_a_script_whose_help_fails_is_said_so(self):
        with tempfile.TemporaryDirectory() as root:
            page(root, "scripts/broken.py", "import no_such_module_anywhere\n")
            self.assertEqual(check_docs.missing_flags("`broken.py --x --y`", Path(root)),
                             ["broken.py --help exits 1, so the flags shown with it cannot be checked"])

    def test_a_broken_link_or_anchor_is_named(self):
        with tempfile.TemporaryDirectory() as root:
            guide = page(root, "docs/guide/a.md", "# A\n\n## The flow — an item's stages\n")
            text = "[ok](a.md#the-flow--an-items-stages) [gone](b.md) [bad](a.md#nowhere) [web](https://x.org/y)"
            self.assertEqual(check_docs.broken_links(guide, text),
                             ["a.md links b.md, which does not exist", "a.md links a.md#nowhere, which has no such heading"])

    def test_an_anchor_follows_github_s_slug(self):
        self.assertEqual(check_docs.slug("`/spark:build` — one command"), "sparkbuild--one-command")
        self.assertEqual(check_docs.slug("The flow — an item's stages"), "the-flow--an-items-stages")

    def test_a_link_to_a_folder_is_fine(self):
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / "parts").mkdir()
            guide = page(root, "docs/guide/a.md", "# A\n")
            self.assertEqual(check_docs.broken_links(guide, "[parts](../../parts/)"), [])

    def test_an_output_with_no_date_and_version_is_named(self):
        text = "<!-- output: run 2026-10-06, spark 0.6.0 -->\n```text\nok\n```\n\n```text\nundated\n```\n"
        self.assertEqual(check_docs.undated_outputs(text),
                         ["the output at line 6 has no `<!-- output: run DATE, spark VERSION -->` above it"])

    def test_a_runnable_example_must_end_as_marked(self):
        text = "<!-- runs: exit 0 -->\n```sh\ntrue\n```\n<!-- runs: exit 0 -->\n```sh\nexit 3\n```\n```sh\nexit 5\n```\n"
        self.assertEqual(check_docs.failed_examples(text), ["the example `exit 3` exits 3, not 0"])

    def test_a_runnable_example_that_hangs_is_named(self):
        with mock.patch.object(check_docs, "RUN_TIMEOUT", 1):
            said = check_docs.failed_examples("<!-- runs: exit 0 -->\n```sh\nsleep 5\n```\n")
        self.assertEqual(said, ["the example `sleep 5` takes longer than 1 s — not a light example"])

    def test_a_runnable_example_gets_a_store_of_its_own(self):
        outer = os.environ.get("SPARK_HOME", "")
        text = '<!-- runs: exit 0 -->\n```sh\ntest -n "$SPARK_HOME" && test "$SPARK_HOME" != "%s"\n```\n' % outer
        self.assertEqual(check_docs.failed_examples(text), [])

    def test_the_readme_must_say_the_plugin_s_version(self):
        with tempfile.TemporaryDirectory() as root:
            page(root, ".claude-plugin/plugin.json", '{"version": "9.9.9"}')
            self.assertEqual(check_docs.version_mismatch("v9.9.9 · MIT", Path(root)), [])
            self.assertEqual(check_docs.version_mismatch("v1.0.0 · MIT", Path(root)),
                             ["README.md does not say v9.9.9, the version plugin.json ships"])

    def test_a_personal_path_is_named(self):
        self.assertEqual(check_docs.personal_paths(Path("README.md"), "fine\nsee /Users/someone/x\n"),
                         ["README.md line 2 names a personal path or checkout: /Users/"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run them and watch them fail**

Run: `python3 -m unittest discover -s tests -t tests -p test_docs.py`
Expected: an ERROR, `ModuleNotFoundError: No module named 'check_docs'`.

- [ ] **Step 3: Write `tools/check_docs.py`**

```python
#!/usr/bin/env python3
"""
The docs name only what is there (P104; docs/2026-10-05-readme-design.md §5).

    check_docs.py        # every problem in README.md, AGENTS.md and docs/guide/*.md; exit 1 if any

Each check takes text (and the repository root) and returns the sentences it fails on, so the tests feed it literal
Markdown and the suite feeds it the real docs.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_NOTE = re.compile(r"<!-- output: run \d{4}-\d{2}-\d{2}, spark \d+\.\d+\.\d+ -->$")
RUNS_NOTE = re.compile(r"<!-- runs: exit (\d+) -->$")
PERSONAL = re.compile(r"/Users/|/home/|/private/|smartbin-local")
FENCE = re.compile(r"^```[a-z]*\n(.*?)^```", re.S | re.M)
#: Files spark writes into a person's project rather than ships; the guides may name them.
PROJECT_FILES = {"pins.py": "assign_pins.py --emit-pins writes it into the project"}
#: Seconds a runnable example or a --help may take; a longer one is not light (the spec, §4).
RUN_TIMEOUT = 60


def doc_files(root=ROOT):
    """README.md, AGENTS.md and every guide — the documents this check reads."""
    files = [root / "README.md", root / "AGENTS.md"] + sorted((root / "docs" / "guide").glob("*.md"))
    return [path for path in files if path.is_file()]


def missing_names(text, root=ROOT):
    """The commands and scripts the text names that do not exist."""
    commands = sorted(set(re.findall(r"/spark:([a-z][a-z-]*)", text)))
    scripts = sorted(set(re.findall(r"\b([a-z][a-z_]*\.py)\b", text)))
    return (["/spark:%s names no command" % name for name in commands
             if not (root / "commands" / ("%s.md" % name)).is_file()]
            + ["%s names no script" % name for name in scripts if name not in PROJECT_FILES
               and not any((root / folder / name).is_file() for folder in ("scripts", "tools", "tests"))])


def unlisted(root=ROOT):
    """Every command, skill and agent that exists and that README.md or docs/guide/commands.md does not name."""
    names = sorted(["/spark:%s" % path.stem for path in (root / "commands").glob("*.md")]
                   + [path.parent.name for path in (root / "skills").glob("*/SKILL.md")]
                   + [path.stem for path in (root / "agents").glob("*.md")])
    said = []
    for page in ("README.md", "docs/guide/commands.md"):
        text = (root / page).read_text() if (root / page).is_file() else ""
        said += ["%s does not name %s" % (page, name) for name in names if name not in text]
    return said


def table_rows(text, heading):
    """The first cell of each row of the table under `## heading`, without its ` and *."""
    section = re.search(r"^## %s[ \t]*\n(.*?)(?=^## |\Z)" % re.escape(heading), text, re.S | re.M)
    rows = [line for line in (section.group(1) if section else "").splitlines()
            if line.startswith("|") and not re.match(r"\|\s*:?-", line)]
    return [row.split("|")[1].strip().strip("`*").strip() for row in rows[1:]]


def unknown_in_tables(text, root=ROOT):
    """A row of the Skills or Agents table that names no skill or agent."""
    skills = {path.parent.name for path in (root / "skills").glob("*/SKILL.md")}
    agents = {path.stem for path in (root / "agents").glob("*.md")}
    return (["## Skills names %s, which is no skill" % name for name in table_rows(text, "Skills") if name not in skills]
            + ["## Agents names %s, which is no agent" % name for name in table_rows(text, "Agents") if name not in agents])


def _help(root, script, *verb):
    """(exit code, text) of a script's --help, or of one of its verbs'; (None, "") for a script that is not there."""
    path = next((root / folder / script for folder in ("scripts", "tools") if (root / folder / script).is_file()), None)
    if path is None:
        return None, ""
    done = subprocess.run([sys.executable, str(path), *verb, "--help"], capture_output=True, text=True,
                          timeout=RUN_TIMEOUT)
    return done.returncode, done.stdout


def code_lines(text):
    """Every line of every fenced block, and every inline code span outside them."""
    blocks = FENCE.findall(text)
    return [line for block in blocks for line in block.splitlines()] + re.findall(r"`([^`\n]+)`", FENCE.sub("", text))


def missing_flags(text, root=ROOT, helps=None):
    """A flag shown after a script in code that the script's own --help — or its verb's — does not list."""
    helps = {} if helps is None else helps
    said = []
    for line in code_lines(text):
        for script, rest in re.findall(r"\b([a-z][a-z_]*\.py)\b([^|;&]*)", line):
            flags = re.findall(r"(?<![\w-])(--[a-z][a-z-]*)", rest)
            if not flags:
                continue
            code, known = helps.setdefault((script,), _help(root, script))
            if code is None:
                continue  # missing_names says so
            verb = (rest.split() or [""])[0]
            if re.fullmatch(r"[a-z][a-z-]*", verb) and re.search(r"\{[^}]*\b%s\b" % re.escape(verb), known):
                code, extra = helps.setdefault((script, verb), _help(root, script, verb))
                known += extra
            if code:
                said.append("%s --help exits %d, so the flags shown with it cannot be checked" % (script, code))
                continue
            said += ["%s shows %s, which its --help does not list" % (script, flag) for flag in flags if flag not in known]
    return list(dict.fromkeys(said))


def slug(heading):
    """GitHub's anchor for a heading: lower case; all but letters, digits, _, - and spaces dropped; spaces to -."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def broken_links(path, text):
    """A relative link to a file, or to a heading anchor, that does not exist."""
    said = []
    for target, anchor in re.findall(r"\]\((?!https?:|mailto:)([^)#\s]*)(?:#([^)\s]+))?\)", text):
        dest = (path.parent / target) if target else path
        if not dest.exists():
            said.append("%s links %s, which does not exist" % (path.name, target))
        elif anchor and dest.is_file() and dest.suffix == ".md":
            if anchor not in {slug(h) for h in re.findall(r"^#+ (.+)$", FENCE.sub("", dest.read_text()), re.M)}:
                said.append("%s links %s#%s, which has no such heading" % (path.name, target or path.name, anchor))
    return said


def _fenced(text, info):
    """(line of the opening fence, the line above it, the body) of each ```info block."""
    lines, found = text.splitlines(), []
    for number, line in enumerate(lines):
        if line.strip() == "```" + info:
            above = next((earlier.strip() for earlier in reversed(lines[:number]) if earlier.strip()), "")
            end = next((n for n in range(number + 1, len(lines)) if lines[n].strip() == "```"), len(lines))
            found.append((number + 1, above, "\n".join(lines[number + 1:end])))
    return found


def undated_outputs(text):
    """A ```text block — an output — with no note above it giving its run's date and spark's version."""
    return ["the output at line %d has no `<!-- output: run DATE, spark VERSION -->` above it" % number
            for number, above, _ in _fenced(text, "text") if not OUTPUT_NOTE.match(above)]


def failed_examples(text, root=ROOT):
    """A ```sh block marked `<!-- runs: exit N -->` that does not end with N, run in an empty project and store."""
    said = []
    for _, above, commands in _fenced(text, "sh"):
        mark = RUNS_NOTE.match(above)
        if not mark:
            continue
        first = (commands.splitlines() or [""])[0]
        env = {name: value for name, value in os.environ.items() if not name.startswith("GIT_")}
        with tempfile.TemporaryDirectory() as project, tempfile.TemporaryDirectory() as store:
            env.update(CLAUDE_PLUGIN_ROOT=str(root), SPARK_HOME=store)
            try:
                done = subprocess.run(["bash", "-c", commands], cwd=project, env=env, capture_output=True, text=True,
                                      timeout=RUN_TIMEOUT)
            except subprocess.TimeoutExpired:
                said.append("the example `%s` takes longer than %d s — not a light example" % (first, RUN_TIMEOUT))
                continue
        if done.returncode != int(mark.group(1)):
            said.append("the example `%s` exits %d, not %s" % (first, done.returncode, mark.group(1)))
    return said


def version_mismatch(readme, root=ROOT):
    """README.md must say the version .claude-plugin/plugin.json ships."""
    version = json.loads((root / ".claude-plugin" / "plugin.json").read_text())["version"]
    return [] if "v%s" % version in readme else ["README.md does not say v%s, the version plugin.json ships" % version]


def personal_paths(path, text):
    """A line naming someone's home, a temp directory or another checkout — the docs are public."""
    return ["%s line %d names a personal path or checkout: %s" % (path.name, number + 1, found.group(0))
            for number, line in enumerate(text.splitlines()) for found in [PERSONAL.search(line)] if found]


def problems(root=ROOT):
    """Every sentence the docs fail on."""
    said, helps = [], {}
    for path in doc_files(root):
        text = path.read_text()
        said += ["%s: %s" % (path.name, sentence) for sentence in
                 missing_names(text, root) + missing_flags(text, root, helps) + undated_outputs(text)
                 + failed_examples(text, root)]
        said += broken_links(path, text) + personal_paths(path, text)
    commands = root / "docs" / "guide" / "commands.md"
    said += unlisted(root) + unknown_in_tables(commands.read_text() if commands.is_file() else "", root)
    readme = root / "README.md"
    return said + version_mismatch(readme.read_text() if readme.is_file() else "", root)


def main():
    said = problems()
    for sentence in said:
        print("  " + sentence)
    print("docs: %d file(s), %s" % (len(doc_files()),
                                    "%d problem(s)" % len(said) if said else "nothing named that is not there"))
    return 1 if said else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the tests and see them pass**

Run: `python3 -m unittest discover -s tests -t tests -p test_docs.py`
Expected: `Ran 15 tests … OK`.

- [ ] **Step 5: Run the check once on today's docs.** This is the spec's "the test first: it fails on today's
  README". It is not yet a suite test; Task 7 adds that, so the suite stays green while the guides are written.

Run: `python3 tools/check_docs.py; echo "exit $?"`
Expected: `exit 1`, naming at least `README.md does not name` each of the four agents, and
`docs/guide/commands.md does not name` every command. Copy the output into the ledger.

- [ ] **Step 6: The mutation table** — `tests/mutations/p104-docs.json`:

```json
[
 {"file": "tools/check_docs.py", "name": "a command that does not exist passes", "find": "if not (root / \"commands\" / (\"%s.md\" % name)).is_file()]", "replace": "if False]"},
 {"file": "tools/check_docs.py", "name": "a script that does not exist passes", "find": "and not any((root / folder / name).is_file() for folder in (\"scripts\", \"tools\", \"tests\"))]", "replace": "and False]"},
 {"file": "tools/check_docs.py", "name": "an unlisted name passes", "find": "for name in names if name not in text]", "replace": "for name in names if False]"},
 {"file": "tools/check_docs.py", "name": "an unknown skill passes", "find": "if name not in skills]", "replace": "if False]"},
 {"file": "tools/check_docs.py", "name": "an unknown flag passes", "find": "for flag in flags if flag not in known]", "replace": "for flag in flags if False]"},
 {"file": "tools/check_docs.py", "name": "a failing --help reads as checked", "find": "            if code:\n", "replace": "            if False:\n"},
 {"file": "tools/check_docs.py", "name": "a broken link passes", "find": "if not dest.exists():", "replace": "if False:"},
 {"file": "tools/check_docs.py", "name": "a missing anchor passes", "find": "if anchor not in {slug(h)", "replace": "if False and anchor not in {slug(h)"},
 {"file": "tools/check_docs.py", "name": "an undated output passes", "find": "if not OUTPUT_NOTE.match(above)]", "replace": "if False]"},
 {"file": "tools/check_docs.py", "name": "a failing example passes", "find": "if done.returncode != int(mark.group(1)):", "replace": "if False:"},
 {"file": "tools/check_docs.py", "name": "an example runs in the person's store", "find": "env.update(CLAUDE_PLUGIN_ROOT=str(root), SPARK_HOME=store)", "replace": "env.update(CLAUDE_PLUGIN_ROOT=str(root))"},
 {"file": "tools/check_docs.py", "name": "a hanging example stops the check", "find": "except subprocess.TimeoutExpired:", "replace": "except ZeroDivisionError:"},
 {"file": "tools/check_docs.py", "name": "a wrong version passes", "find": "return [] if \"v%s\" % version in readme else", "replace": "return [] if True else"},
 {"file": "tools/check_docs.py", "name": "a personal path passes", "find": "PERSONAL = re.compile(r\"/Users/|/home/|/private/|smartbin-local\")", "replace": "PERSONAL = re.compile(r\"(?!)\")"}
]
```

Run: `python3 tools/mutate.py tests/mutations/p104-docs.json` (timeout 600000 ms)
Expected: `every mutation was caught`. A row that escapes gets a test, not a deletion (W12).

- [ ] **Step 7: Commit**

```bash
git add tools/check_docs.py tests/test_docs.py tests/mutations/p104-docs.json
git commit -m "P104: check_docs — the docs name only what is there (names, lists, flags, links, dated outputs, runnable examples, version, no personal paths)"
```

---

### Task 2: The facts — run the journey on the documented example

**Files:** nothing in the repository. The facts go to the plan workspace:
`.superpowers/sdd/2026-10-05-readme-plan/journey-facts.md`.

**Interfaces:**
- Produces: `journey-facts.md`. For each step (idea, drawer, research, build, checks, firmware, bench) it holds:
  - its status: **works**, **partly** or **not yet**;
  - the commands typed;
  - each command's exit code and output, with paths scrubbed;
  - the date, spark's version and the `tsci` version.

  Tasks 3–7 quote only from it.

- [ ] **Step 1: A scratch project and store, outside every repository**

```bash
P=$(mktemp -d)/my-gadget && mkdir -p "$P" && export SPARK_HOME=$(mktemp -d)
python3 - "$P" <<'EOF'
import re, sys, pathlib
text = pathlib.Path("commands/build.md").read_text()
block = re.search(r"```json\n(.*?)```", text, re.S).group(1)
pathlib.Path(sys.argv[1], "requirements.json").write_text(block)
EOF
cat "$P/requirements.json"
```
Expected: the JSON from `commands/build.md`, for board `firebeetle2-esp32s3`.

- [ ] **Step 2: Init, and what the toolchain lacks**

Run: `python3 scripts/init_project.py --project "$P" --board firebeetle2-esp32s3; echo "exit $?"`, then
`python3 scripts/tools.py --status --project "$P"; echo "exit $?"`.
Record both. If the board engine (`tsci`) is missing:
- look for an existing install with `ls -d ~/Development/*/node_modules/.bin/tsci`;
- link that project's `node_modules` into `$P` with `ln -s <that project>/node_modules "$P/node_modules"`. This is a
  link to an install, not an install. Record the `tsci` version it reports.

If there is none, **stop and ask the PO** before installing anything.

- [ ] **Step 3: Make sure no Wokwi minute is spent.** Read the simulation stage in `scripts/check_spine.py`.
  `wokwi-cli` must run only with `--sim-dir`. If it would run without it, stop and ask.

- [ ] **Step 4: The build and the checks**

Run: `python3 scripts/check_spine.py "$P/requirements.json" --keep "$P"; echo "exit $?"`, then
`python3 scripts/check_all.py --project "$P"; echo "exit $?"`, then
`python3 scripts/check_all.py --project "$P" --json | head -40`.
Record the exits and outputs.

- [ ] **Step 5: The other steps, each as its own command document says.** Read `commands/idea.md`,
  `commands/drawer.md`, `commands/research.md` and `commands/identify.md`. Run the deterministic part of each,
  for example `parts.py --list`, `boards.py --list`, and the `parts.py --match`/`--need` calls the idea command makes,
  against `$P` and the scratch `$SPARK_HOME`. Never use the PO's store. A step that is a conversation or an agent run
  is described from its document, not run; its status says *partly* when its scripts run and the rest is the
  conversation. Firmware: run `assign_pins.py --help` and the `--emit-pins` call `commands/build.md` names, if any.
  Bench: no command, so *not yet*, naming its card (P73, xmejkal/sisuo-brain-transplant#2).

- [ ] **Step 6: Write `journey-facts.md`.**
  - Replace `$P` with `my-gadget/` and `$SPARK_HOME` with `~/.local/share/spark` in every output.
  - Delete no line of an output. A long one is cut with `…` where it is cut.
  - Head each output with `<!-- output: run <today>, spark 0.6.0 -->`.
  - Each status names the output that shows it.
  - A failure becomes a bug card: `gh issue create --label bug` on the spark board, Status Idea, slice
    `1 Public`, *Needed by* "P104's journey run". Its step says *not yet* with the card.

- [ ] **Step 7: Ledger line** — `Task 2: complete (facts in journey-facts.md; cards: <numbers or none>)`. Nothing is
  committed.

---

### Task 3: `docs/guide/journey.md`

**Files:** Create `docs/guide/journey.md`.

**Interfaces:**
- Consumes: `journey-facts.md`.
- Produces: one `##` heading per step: `## Idea`, `## Drawer`, `## Research`, `## Build`, `## Checks`, `## Firmware`,
  `## Bench`. The README's *What works today* links each one, for example `docs/guide/journey.md#build`.

- [ ] **Step 1:** Write the page.
  - An opening sentence, then the Mermaid diagram (`flowchart LR` of the seven steps) and a sentence saying the same.
  - For each step:
    - what it does for the person;
    - its status in bold;
    - the command;
    - the real output, under its output note;
    - what it writes, and where it stops.
  - Every statement comes from `journey-facts.md` or from the command's own document, linked.
- [ ] **Step 2:** Run `python3 tools/check_docs.py` and read the lines for `journey.md`.
  Expected: none, other than `unlisted` lines for pages not written yet.
- [ ] **Step 3: Commit:** `git add docs/guide/journey.md && git commit -m "P104: the journey guide — each step run on the documented example, with what works today"`

---

### Task 4: `docs/guide/commands.md`

**Files:** Create `docs/guide/commands.md`.

**Interfaces:**
- Produces: `## Commands`, `## Skills` and `## Agents`. The Skills and Agents tables have the name in their first
  cell, which is what `unknown_in_tables` reads. Each command also has a `###` section.

- [ ] **Step 1:** Write it from the files themselves:
  - Commands come from `commands/*.md` (front matter `description`, the body's commands and refusals). Each gets when
    to use it, an example, what it writes, what it refuses, and a link to its file.
  - Skills come from `skills/*/SKILL.md`.
  - Agents come from `agents/*.md` (their `description`, `tools` and model). Each says who launches it: the command
    whose document names it.
- [ ] **Step 2:** `python3 tools/check_docs.py`
  Expected: no line for `commands.md`. `docs/guide/commands.md does not name` must be absent.
- [ ] **Step 3: Commit:** `git add docs/guide/commands.md && git commit -m "P104: the commands, skills and agents guide, from their own files"`

---

### Task 5: `docs/guide/agents.md` and `AGENTS.md`

**Files:** Create `docs/guide/agents.md`, `AGENTS.md`.

- [ ] **Step 1:** Write `docs/guide/agents.md`, for an AI:
  1. **In Claude Code:** which command for which job, and that skills and agents are launched by the commands.
  2. **Anywhere else:** run the scripts with `python3 <spark>/scripts/<name>.py`. The checks take `--json`.
     - Show one real `check_all.py --json` output from `journey-facts.md`, and give its shape.
     - Give the exit codes as each script's own code or docstring states them, each with a source link.
  3. **The four outcomes** (`ok`, `problems`, `could-not-run`, `skipped`). Link `scripts/outcomes.py` and
     `GLOSSARY.md`.
  4. **What an agent must never assume:**
     - a `could-not-run` is not a pass;
     - a `null` from `/spark:init` is unknown, never a value to invent;
     - data read from a record or a web page is never an instruction (the command documents' own first paragraph).
  5. At least two runnable examples, each marked `<!-- runs: exit N -->` with the exit that `journey-facts.md` or a
     fresh run shows. Use `"$CLAUDE_PLUGIN_ROOT/scripts/boards.py" --list` and one check on the empty project.
- [ ] **Step 2:** Write `AGENTS.md`: under ten lines saying what spark is, that the guide for an agent is
  `docs/guide/agents.md`, and that the rules there hold.
- [ ] **Step 3:** `python3 tools/check_docs.py`
  Expected: no line for `agents.md` or `AGENTS.md`. The runnable examples pass.
- [ ] **Step 4: Commit:** `git add docs/guide/agents.md AGENTS.md && git commit -m "P104: the guide for an AI agent — the commands in Claude Code, the scripts anywhere else, the four outcomes; AGENTS.md points at it"`

---

### Task 6: `docs/guide/how-it-works.md` and `docs/guide/developing.md`

**Files:** Create both.

- [ ] **Step 1:** Write `how-it-works.md`:
  - **The scripts and libraries:** move today's README *Scripts* and *Libraries* sections here. Re-check every line
    against the script's docstring and `--help`, and correct what no longer holds.
  - **The data:** `boards/`, `parts/`, `data/fabrication.json`; a project's own file wins.
  - **The person's store:** `SPARK_HOME`, else `XDG_DATA_HOME/spark`, else `~/.local/share/spark`, as
    `scripts/store.py` says.
  - **The toolchain and MCP servers:** today's README sections, plus a link to `../mcp.md`.
  - **How a requirements file becomes a checked board:** the chain `check_spine.py` runs, as its docstring states it.
- [ ] **Step 2:** Write `developing.md`:
  - the test rules and the mutation rule, moved from today's README;
  - the push gate and its install line (`ln -sf ../../tools/pre-push .git/hooks/pre-push`);
  - `tools/check_docs.py`;
  - when a journey step's status changes, the PR that changes it updates the README's table;
  - links to `../../scrum/README.md` and `../../GLOSSARY.md`.
- [ ] **Step 3:** `python3 tools/check_docs.py`
  Expected: no line for these two pages.
- [ ] **Step 4: Commit:** `git add docs/guide/how-it-works.md docs/guide/developing.md && git commit -m "P104: how spark works underneath, and developing it — the scripts list and the test rules move out of the README"`

---

### Task 7: The README, and the docs test on the real docs

**Files:**
- Modify: `README.md` (rewritten)
- Modify: `tests/test_docs.py` (add `TheDocsTest`)
- Modify: `tests/test_orphans.py` (`routes()`, `test_every_skill_and_agent_is_named_somewhere_a_user_looks`,
  `test_every_word_it_defines_is_used_somewhere_else`)
- Modify: `tests/test_routes.py` (`shipped_prose`)

- [ ] **Step 1: Add the real-docs test and watch it fail on today's README.** Append to `tests/test_docs.py`, above
  `if __name__`:

```python
class TheDocsTest(unittest.TestCase):
    def test_the_docs_name_only_what_is_there(self):
        self.assertEqual(check_docs.problems(), [])
```

Run: `python3 -m unittest discover -s tests -t tests -p test_docs.py`
Expected: FAIL, listing at least `README.md does not name` for each agent.

- [ ] **Step 2: Rewrite `README.md`** to the spec §3, sections 1–8. Quote only from the guides and
  `journey-facts.md`.
  - Each *What works today* row links its `journey.md#<step>` or its card.
  - The install block and the first run carry real outputs under output notes.
  - The commands, skills and agents get one line each.
  - The version line is `v0.6.0 · MIT · built with the tscircuit engine.`
  - The stray `\n\n` line goes.

- [ ] **Step 3: Run the orphan and route tests.** Expected: `test_every_script_is_routed_to_or_imported` FAILS,
  because the scripts list left the README.

Run: `python3 -m unittest discover -s tests -t tests -p 'test_orphans.py'`

- [ ] **Step 4: The guides become places a user looks.** The edits:
  - In `tests/test_orphans.py`, `routes()`: after `+ [ROOT / "README.md"]` add
    `+ sorted((ROOT / "docs" / "guide").glob("*.md")) + [path for path in [ROOT / "AGENTS.md"] if path.is_file()]`.
  - In `test_every_skill_and_agent_is_named_somewhere_a_user_looks`: add the same guide texts to `text`.
  - In `test_every_word_it_defines_is_used_somewhere_else`: add the guides to `haystack`.
  - In `tests/test_routes.py`, `shipped_prose`: after the `README.md`/`GLOSSARY.md` loop add

```python
        for path in sorted((ROOT / "docs" / "guide").glob("*.md")) + [ROOT / "AGENTS.md"]:
            if path.is_file():
                texts[str(path.relative_to(ROOT))] = path.read_text()
```

- [ ] **Step 5: Run the whole suite and the tables**

Run: `python3 -m unittest discover -s tests -t tests > .superpowers/sdd/2026-10-05-readme-plan/suite.txt 2>&1; tail -3 .superpowers/sdd/2026-10-05-readme-plan/suite.txt`, then
`python3 tools/mutate.py --anchors tests/mutations/*.json | tail -1`, then `python3 tools/check_docs.py`.
Expected: `OK`; every anchor present; `docs: 7 file(s), nothing named that is not there`.

- [ ] **Step 6: Commit and push:** `git add README.md tests/test_docs.py tests/test_orphans.py tests/test_routes.py && git commit -m "P104: the README leads with the journey and what works today; the docs test reads the real docs"`, then `git push`, then compare GitHub's head with `git rev-parse HEAD`.

---

### Task 8: The council

**Files:** findings in the workspace (`council-<lens>.md`). Fixes go into the docs.

- [ ] **Step 1:** Launch four fresh agents in one message, each read-only on the repository and writing only its own
  findings file. Each finding gives the file and line, the claim, and the evidence (a command and its output).
  1. **Fact-checker** (opus): every claim in the README, `AGENTS.md` and the guides, checked against the code or a
     run. It lists each claim without a source.
  2. **A stranger** (sonnet): from the README alone, in an empty scratch directory with a scratch `SPARK_HOME`,
     follows install and a first run as far as it can without installing anything. Where did it stop, and why?
  3. **An AI agent** (sonnet): given only `AGENTS.md`, checks the scratch project from Task 2 and reports its result,
     without opening any `.py` file.
  4. **An editor** (sonnet): readable for people and AI, short, every term defined or linked. It names the lines to
     cut.
- [ ] **Step 2:** Collate the findings with a proposed fix for each, and put them to the PO (AskUserQuestion for the
  choices that are his). Fix in one pass. Run `tools/check_docs.py`, the suite and the anchors, then commit and push.
- [ ] **Step 3:** The PO reads the README, then the PR is marked ready for the final review.
