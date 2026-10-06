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
