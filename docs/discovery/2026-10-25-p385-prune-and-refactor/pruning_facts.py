#!/usr/bin/env python3
"""
The fact table of card P385 (#494): one row per tracked file under scripts/ and tools/. It reads and prints, nothing else.

    python3 docs/discovery/2026-10-25-p385-prune-and-refactor/pruning_facts.py [--walk RECORD ...]

Run it from the repository root. A walk record is a file or a folder. `--walk` adds one column for each record, and
names the column after the record's file name. A record outside the repository prints only its name and sha256.
"""

import argparse
import ast
import hashlib
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from inventory import Inventory  # noqa: E402  (reused, not rewritten)

BUNDLE = "tools/circuit-to-wokwi"
WALKS = {"walk 1": ["docs/observations/2026-10-19-p326-walk1.md", "docs/observations/2026-10-19-p351-walk1-council"],
         "walk 2": ["docs/observations/2026-10-23-p400-walk2-council"]}


def mentions(name, text, folder=""):
    """How many times `text` names `name` whole, alone or after its own folder.

    >>> mentions("board.py", "see emit_board.py and board_look.py")
    0
    >>> mentions("look.py", "board_look.py and look.pyc")
    0
    >>> mentions("design.py", "compare_design.py, my-design.py")
    0
    >>> mentions("board.py", "`board.py`, scripts/board.py and tools/board.py.", "scripts/")
    2
    >>> mentions("board.py", "tools/board.py", "scripts/")
    0
    """
    return len(re.findall(r"(?:(?<![\w/.-])|(?<=%s))%s(?!\w)" % (re.escape(folder) or "(?!)", re.escape(name)), text))


def lines_of(path):
    return (ROOT / path).read_bytes().count(b"\n")  # as `wc -l` counts


def record_text(paths):
    """The text of walk records: each a file, or a folder read through its files in order."""
    files = [f for p in paths for f in ([Path(p)] if Path(p).is_file() else sorted(Path(p).rglob("*"))) if f.is_file()]
    return "\n".join(f.read_text(errors="ignore") for f in files)


def sha256(paths):
    digest = hashlib.sha256()
    for p in paths:
        for f in ([Path(p)] if Path(p).is_file() else sorted(Path(p).rglob("*"))):
            digest.update(f.read_bytes() if f.is_file() else b"")
    return digest.hexdigest()


def tracked(*places):
    out = subprocess.run(["git", "ls-files", *places], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return sorted(out.split("\n")[:-1])


def table(extra):
    inv = Inventory(ROOT)
    texts = {"named in " + label: record_text([ROOT / p for p in paths]) for label, paths in WALKS.items()}
    texts.update({"named in " + Path(p).name: record_text([Path(p).expanduser()]) for p in extra})
    tests = {f: (ROOT / f).read_text(errors="ignore") for f in tracked("tests") if re.fullmatch(r"tests/[^/]+\.py", f)}
    test_imports = {f: {a.name.split(".")[0] for n in ast.walk(ast.parse(t)) if isinstance(n, ast.Import) for a in n.names}
                    | {n.module.split(".")[0] for n in ast.walk(ast.parse(t)) if isinstance(n, ast.ImportFrom) and n.module}
                    for f, t in tests.items()}
    files = tracked("scripts", "tools")
    bundle = [f for f in files if f.startswith(BUNDLE + "/")]
    rows = []
    for rel in sorted([f for f in files if f not in bundle] + [BUNDLE]):
        name, folder = Path(rel).name, rel[: -len(Path(rel).name)]
        known = {s.rel: s for s in inv.scripts}
        script = known.get(rel) or SimpleNamespace(name=name, stem=Path(rel).stem)
        who = sorted(s.name for s in inv.importers(script)) if rel.endswith(".py") else []
        ran = [f for f, t in tests.items() if (script.stem in test_imports[f] and rel.endswith(".py")) or mentions(name, t, folder)]
        size = "%d (%d files)" % (sum(map(lines_of, bundle)), len(bundle)) if rel == BUNDLE else str(lines_of(rel))
        rows.append([rel, size, "%d: %s" % (len(who), ", ".join(who)) if who else "0", str(len(inv.pages_naming(script))),
                     str(len(ran))] + [str(mentions(name, text, folder)) for text in texts.values()])
    head = ["module", "lines", "imported by", "named by", "run by tests"] + list(texts)
    return ["| " + " | ".join(head) + " |", "|" + " --- |" * len(head)] + ["| " + " | ".join(r) + " |" for r in rows]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--walk", action="append", default=[], metavar="RECORD", help="one more walk record, a file or folder")
    args = parser.parse_args(argv)
    lines = table(args.walk) + ["", "Walk records:"]
    for label, paths in WALKS.items():
        lines.append("- %s: %s" % (label, " and ".join("`%s`" % p for p in paths)))
    for p in args.walk:
        full = Path(p).expanduser().resolve()
        inside = full.is_relative_to(ROOT)
        lines.append("- %s: %s" % (full.name, "`%s`" % full.relative_to(ROOT) if inside else "outside the repo, sha256 " + sha256([full])))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
