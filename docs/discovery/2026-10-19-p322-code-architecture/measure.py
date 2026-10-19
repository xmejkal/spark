"""Measure the shape of spark's scripts/ code, for the P322 architecture board.

Rerun from the repository root: python3 docs/discovery/2026-10-19-p322-code-architecture/measure.py
Stdlib only. It reads the code and changes nothing.

Definitions, one threshold each:
- A CLI is a module with a top-level main(). Fat CLI: its main() is over FAT_MAIN (80) lines, which means it holds logic.
  Thin CLI: main() is at most THIN_MAIN (40) lines and the module keeps at most THIN_FUNCTIONS (3) other functions.
  Every other CLI is "CLI with library". A module without main() is a library.
- Classes and functions are found at the top level and under a top-level if/try. Class and function lines
  include their decorators. The `if __name__ == "__main__":` block is counted as its own figure, not as a function.
- An outcome literal is a bare outcome word that is compared with (==, !=, in, not in), assigned to a name,
  attribute or keyword called status/verdict/outcome, or stored under a "status"/"verdict" key. Field names, other
  dict keys and display text do not count.
"""
import ast
import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
ROLES = ("Service", "Strategy", "Adapter", "Result", "Error", "Value", "Store",
         "Decorator", "Renderer", "Platform", "Fake", "Pure")
THIN_MAIN = 40       # lines: a main() this long or shorter only parses and prints
THIN_FUNCTIONS = 3   # top-level functions besides main() a thin CLI may keep
FAT_MAIN = 80        # lines: a main() this long holds logic
OUTCOME_WORDS = {"ok", "problems", "could-not-run", "skipped"}  # outcomes.OK, PROBLEMS, ...
OUTCOME_NAMES = {"status", "verdict", "outcome"}
NAMEDTUPLE_API = {"_asdict", "_replace", "_fields", "_make"}  # public API of a namedtuple, not a private name


def code_lines(source):
    """Lines that are neither blank nor a comment (docstrings count as code)."""
    return sum(1 for line in source.splitlines() if line.strip() and not line.strip().startswith("#"))


def span(node):
    """Lines of a def or class, from its first decorator to its last line."""
    first = min([node.lineno] + [d.lineno for d in node.decorator_list])
    return node.end_lineno - first + 1


def node_lines(source_lines, node):
    first = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
    return code_lines("\n".join(source_lines[first - 1:node.end_lineno]))


def is_main_block(node):
    return (isinstance(node, ast.If) and isinstance(node.test, ast.Compare)
            and isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__")


def top_level(body):
    """Statements at the top level and under a top-level if/try, except the `__main__` block."""
    for node in body:
        if is_main_block(node):
            continue
        yield node
        if isinstance(node, ast.If):
            yield from top_level(node.body + node.orelse)
        elif isinstance(node, ast.Try):
            yield from top_level(node.body + node.orelse + node.finalbody
                                 + [s for h in node.handlers for s in h.body])


def role_of(cls):
    """The role from the docstring's first word ('Service:' or 'Value.'), else from the name's suffix, else '?'."""
    first = (ast.get_docstring(cls) or "").split(maxsplit=1)
    word = first[0].rstrip(":.") if first else ""
    if word in ROLES:
        return word
    for role in ROLES:
        if cls.name.endswith(role):
            return role + "(name)"
    return "?"


def private_imports(tree, names):
    """Uses of another script's private name, as {'module._name': count}: `from m import _x` or `m._x`."""
    found = collections.Counter()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in names:
            for a in node.names:
                if a.name.startswith("_") and not a.name.startswith("__"):
                    found[f"{node.module}.{a.name}"] += 1
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id in names and node.attr.startswith("_") and not node.attr.startswith("__") \
                    and node.attr not in NAMEDTUPLE_API:
                found[f"{node.value.id}.{node.attr}"] += 1
    return found


def _constants(expr):
    """The outcome-word constants inside an expression (a Constant, a tuple of them, an if-else of them)."""
    return [n for n in ast.walk(expr) if isinstance(n, ast.Constant) and n.value in OUTCOME_WORDS]


def _name_of(target):
    return target.id if isinstance(target, ast.Name) else target.attr if isinstance(target, ast.Attribute) else None


def outcome_literals(tree):
    """Bare outcome words used as an outcome: compared, assigned to status/verdict/outcome, or under such a key."""
    found = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Compare) and any(isinstance(o, (ast.Eq, ast.NotEq, ast.In, ast.NotIn)) for o in n.ops):
            for side in [n.left] + n.comparators:
                found.update(id(c) for c in _constants(side))
        elif isinstance(n, ast.Assign) and any(_name_of(t) in OUTCOME_NAMES for t in n.targets):
            found.update(id(c) for c in _constants(n.value))
        elif isinstance(n, (ast.AnnAssign, ast.AugAssign)) and n.value is not None and _name_of(n.target) in OUTCOME_NAMES:
            found.update(id(c) for c in _constants(n.value))
        elif isinstance(n, ast.keyword) and n.arg in OUTCOME_NAMES:
            found.update(id(c) for c in _constants(n.value))
        elif isinstance(n, ast.Dict):
            for k, v in zip(n.keys, n.values):
                if isinstance(k, ast.Constant) and k.value in OUTCOME_NAMES:
                    found.update(id(c) for c in _constants(v))
    return len(found)


def measure(path, names):
    source = path.read_text()
    lines = source.splitlines()
    tree = ast.parse(source)
    nodes = list(top_level(tree.body))
    classes = [n for n in nodes if isinstance(n, ast.ClassDef)]
    functions = [n for n in nodes if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    main = next((f for f in functions if f.name == "main"), None)
    others = len(functions) - (1 if main else 0)
    main_len = span(main) if main else 0
    if not main:
        kind = "library"
    elif main_len > FAT_MAIN:
        kind = "fat CLI"
    elif main_len <= THIN_MAIN and others <= THIN_FUNCTIONS:
        kind = "thin CLI"
    else:
        kind = "CLI with library"
    private = private_imports(tree, names - {path.stem})
    return {
        "name": path.stem, "lines": code_lines(source),
        "class_lines": sum(node_lines(lines, c) for c in classes),
        "function_lines": sum(node_lines(lines, f) for f in functions),
        "main_block_lines": sum(node_lines(lines, n) for n in tree.body if is_main_block(n)),
        "classes": classes, "functions": len(functions), "function_spans": [(f.name, span(f)) for f in functions],
        "main": main_len, "kind": kind, "private": private,
        "json": '"--json"' in source, "envelope": bool(re.search(r"(outcomes\.envelope|board_envelope\.\w*envelope)\(", source)),
        "literals": 0 if path.stem == "outcomes" else outcome_literals(tree),
        "roles": [f"{c.name}={role_of(c)}" for c in classes],
    }


def main():
    paths = sorted(p for p in SCRIPTS.glob("*.py"))
    names = {p.stem for p in paths}
    rows = [measure(p, names) for p in paths]
    print(f"{'module':24} {'lines':>5} {'cls':>3} {'fns':>3} {'main':>4} {'priv':>4}  kind")
    for r in rows:
        print(f"{r['name']:24} {r['lines']:5} {len(r['classes']):3} {r['functions']:3} "
              f"{r['main']:4} {sum(r['private'].values()):4}  {r['kind']}")
    print("\nClass roles (from the docstring's first word, else '(name)' from the suffix, else '?'):")
    for r in rows:
        if r["roles"]:
            print(f"  {r['name']}: " + ", ".join(r["roles"]))
    total = sum(r["lines"] for r in rows)
    in_classes = sum(r["class_lines"] for r in rows)
    in_functions = sum(r["function_lines"] for r in rows)
    in_main_block = sum(r["main_block_lines"] for r in rows)
    classes = sum(len(r["classes"]) for r in rows)
    roles = [x for r in rows for x in r["roles"]]
    kinds = {k: sum(1 for r in rows if r["kind"] == k) for k in ("library", "thin CLI", "CLI with library", "fat CLI")}
    fat_main = [r for r in rows if r["kind"] == "fat CLI"]
    private = [r for r in rows if r["private"]]
    private_names = sum((r["private"] for r in rows), collections.Counter())
    cli_json = [r for r in rows if r["json"]]
    print(f"\nTotal: {len(rows)} modules, {total} code lines, {classes} classes, "
          f"{sum(r['functions'] for r in rows)} top-level functions.")
    print(f"Code in classes: {in_classes} lines ({100 * in_classes // total}%). "
          f"In top-level functions: {in_functions} lines ({100 * in_functions // total}%). "
          f"In `__main__` blocks: {in_main_block} lines ({100 * in_main_block // total}%). "
          f"The rest ({total - in_classes - in_functions - in_main_block} lines) is module-level code: "
          f"imports, constants, docstrings and class-less statements.")
    print(f"Classes with a stated role: {sum(1 for x in roles if not x.endswith('?'))} of {classes} "
          f"({sum(1 for x in roles if not x.endswith(('?', '(name)')))} by docstring).")
    print("Module kinds: " + ", ".join(f"{v} {k}" for k, v in kinds.items()) + ".")
    print(f"Fat CLIs (main() over {FAT_MAIN} lines): " + ", ".join(f"{r['name']} ({r['main']})" for r in
          sorted(fat_main, key=lambda r: -r["main"])) + ".")
    print(f"Modules that use another script's private name: {len(private)} "
          f"({sum(private_names.values())} uses): " + ", ".join(r["name"] for r in private) + ".")
    print("Private names used: " + ", ".join(f"{k} ({v})" for k, v in private_names.most_common()) + ".")
    print(f"Scripts with --json: {len(cli_json)}; of them {sum(1 for r in cli_json if r['envelope'])} use "
          f"an envelope (outcomes.envelope or board_envelope): " + ", ".join(r["name"] for r in cli_json if r["envelope"]) + ".")
    print("Largest modules (lines, functions): " + ", ".join(f"{r['name']} ({r['lines']}, {r['functions']})" for r in
          sorted(rows, key=lambda r: -r["lines"])[:8]) + ".")
    longest = sorted(((n, f"{r['name']}.{fn}") for r in rows for fn, n in r["function_spans"]), reverse=True)[:8]
    print("Longest top-level functions: " + ", ".join(f"{name} ({n})" for n, name in longest) + ".")
    print(f"Interfaces: {len(list((ROOT / 'commands').glob('*.md')))} commands, "
          f"{len(list((ROOT / 'agents').glob('*.md')))} agents, "
          f"{sum(1 for r in rows if r['main'])} scripts with a main().")
    literals = [r for r in rows if r["literals"]]
    print(f"Outcome words used as an outcome (compared, assigned, status key): {sum(r['literals'] for r in literals)} in {len(literals)} modules: "
          + ", ".join(f"{r['name']} ({r['literals']})" for r in sorted(literals, key=lambda r: -r["literals"])) + ".")
    print(f"\nSCORE classes {100 * in_classes // total}% | fat CLIs {kinds['fat CLI']} | "
          f"thin CLIs {kinds['thin CLI']} | private imports {len(private)} | outcome literals {sum(r['literals'] for r in literals)} | roles stated "
          f"{sum(1 for x in roles if not x.endswith('?'))}/{classes}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
