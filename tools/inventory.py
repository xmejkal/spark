#!/usr/bin/env python3
"""
What spark can do, read from spark itself: every script, what it is for, who reaches it, and the flags no page names.

    tools/inventory.py               the inventory of this spark, as Markdown
    tools/inventory.py --spark DIR   the inventory of another spark tree

Why: spark has some 530 functions in some 40 scripts, and nothing said what each script is for or which ones
nobody reaches (P200, #153). A script is reached when a page that a person or an agent reads names it: a command,
a skill, an agent, the README, a guide page or a team page. A library is also reached through the scripts that
import it. A flag counts as named when a page that names its script also names the flag.

It runs only `--help`, and only of the scripts that use argparse, so a parser built at run time counts too. It
writes nothing.
"""

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
#: The pages a person or an agent reads. A script that none of them names is reached only by reading source.
PAGES = ("commands/*.md", "skills/**/*.md", "agents/*.md", ".claude/agents/*.md", "README.md", "docs/guide/**/*.md",
         "scrum/*.md")
FLAG = re.compile(r"(?<![\w-])--[a-z][a-z0-9-]*")
#: How many pages a row names before it says how many more.
SHOWN = 3


class Script:
    """One script: what its docstring says it is for, whether it runs as a command, what it imports, its flags."""

    def __init__(self, path, root):
        source = path.read_text()
        tree = ast.parse(source)
        self.path, self.name, self.stem = path, path.name, path.stem
        self.rel = path.relative_to(root).as_posix()
        self.purpose = ((ast.get_docstring(tree) or "").strip().splitlines() or ["(no docstring)"])[0]
        self.is_command = re.search(r"__name__ == ['\"]__main__['\"]", source) is not None
        self.imports = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)
                        for alias in node.names}
        froms = [node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module]
        self.imports |= {node.module.split(".")[0] for node in froms}
        self.imports |= {node.module.split(".")[-1] for node in froms}  # from spark.core.outcomes import X
        self.imports |= {alias.name for node in froms if node.module.split(".")[0] == "spark" for alias in node.names}
        self.flags = self._flags() if self.is_command and "argparse" in self.imports else []

    def _flags(self):
        """The flags its own --help prints."""
        try:
            shown = subprocess.run([sys.executable, str(self.path), "--help"], capture_output=True, text=True,
                                   timeout=30).stdout
        except subprocess.TimeoutExpired:
            return []
        return sorted(set(FLAG.findall(shown)) - {"--help"})


class Inventory:
    """Every script of one spark tree, with the pages that name it and the scripts that import it."""

    def __init__(self, root=ROOT):
        self.root = Path(root)
        self.scripts = [Script(path, self.root) for path in self._files()]
        self.pages = {path.relative_to(self.root).as_posix(): path.read_text(errors="ignore")
                      for pattern in PAGES for path in sorted(self.root.glob(pattern)) if path.is_file()}

    def _files(self):
        """The scripts, in the spark package too but not the MicroPython stand-in, then the tools beside each other."""
        scripts = self.root / "scripts"
        return sorted(path for path in scripts.rglob("*.py") if "stand_in" not in path.relative_to(scripts).parts
                      and path.name != "__init__.py") + sorted((self.root / "tools").glob("*.py"))

    def pages_naming(self, script):
        return [page for page, text in self.pages.items() if script.name in text]

    def importers(self, script):
        return [other for other in self.scripts if script.stem in other.imports and other is not script]

    def unnamed_flags(self, script):
        said = "\n".join(self.pages[page] for page in self.pages_naming(script))
        return [flag for flag in script.flags if not re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(flag), said)]

    def reached(self, script):
        return bool(self.pages_naming(script) or self.importers(script))

    def markdown(self):
        commands = [script for script in self.scripts if script.is_command]
        libraries = [script for script in self.scripts if not script.is_command]
        flags = sum(len(script.flags) for script in commands)
        unnamed = sum(len(self.unnamed_flags(script)) for script in commands)
        nobody = [script for script in self.scripts if not self.reached(script)]
        lines = ["# What spark can do", "",
                 "%d scripts: %d commands, %d %s. %d reached by nothing. %d flags, %d named on no page."
                 % (len(self.scripts), len(commands), len(libraries), "library" if len(libraries) == 1 else "libraries",
                    len(nobody), flags, unnamed),
                 "", "## Nothing reaches these", "",
                 "No page names them and no script imports them.", ""]
        lines += ["- `%s`: %s" % (script.rel, script.purpose) for script in nobody] or ["- none"]
        lines += ["", "## Commands", "", "| script | what it is for | named by | flags no page names |",
                  "| --- | --- | --- | --- |"]
        for script in commands:
            lines.append("| `%s` | %s | %s | %s |" % (script.rel, script.purpose, self._few(self.pages_naming(script)),
                                                    " ".join(self.unnamed_flags(script)) or "-"))
        lines += ["", "## Libraries", "", "| script | what it is for | imported by | named by |", "| --- | --- | --- | --- |"]
        for script in libraries:
            lines.append("| `%s` | %s | %s | %s |" % (script.rel, script.purpose,
                                                    self._few([s.name for s in self.importers(script)]),
                                                    self._few(self.pages_naming(script))))
        return "\n".join(lines) + "\n"

    @staticmethod
    def _few(names):
        if not names:
            return "nothing"
        return ", ".join(names[:SHOWN]) + (" and %d more" % (len(names) - SHOWN) if len(names) > SHOWN else "")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--spark", default=str(ROOT), help="the spark tree to read (default: this one)")
    args = parser.parse_args(argv)
    sys.stdout.write(Inventory(args.spark).markdown())
    return 0


if __name__ == "__main__":
    sys.exit(main())
