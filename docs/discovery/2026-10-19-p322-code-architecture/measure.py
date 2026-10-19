"""Measure the shape of spark's scripts/ code, for the P322 architecture board.

Rerun from the repository root: python3 docs/discovery/2026-10-19-p322-code-architecture/measure.py
Stdlib only. It reads the code and changes nothing.
"""
import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
ROLES = ("Service", "Strategy", "Adapter", "Result", "Error", "Value", "Store",
         "Decorator", "Renderer", "Platform", "Fake", "Pure")
THIN_MAIN = 40       # lines: a main() this long or shorter only parses and prints
THIN_FUNCTIONS = 3   # top-level functions besides main() a thin CLI may keep
FAT_MAIN = 80        # lines: a main() this long holds logic
OUTCOME_WORDS = {"ok", "problems", "could-not-run", "skipped"}  # outcomes.OK, PROBLEMS, ...
NAMEDTUPLE_API = {"_asdict", "_replace", "_fields", "_make"}  # public API of a namedtuple, not a private name


def code_lines(source):
    """Lines that are neither blank nor a comment (docstrings count as code)."""
    return sum(1 for line in source.splitlines() if line.strip() and not line.strip().startswith("#"))


def span(node):
    return node.end_lineno - node.lineno + 1


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
    """Count uses of another script's private name: `from m import _x` or `m._x`."""
    found = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in names:
            found += sum(1 for a in node.names if a.name.startswith("_") and not a.name.startswith("__"))
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id in names and node.attr.startswith("_") and not node.attr.startswith("__") \
                    and node.attr not in NAMEDTUPLE_API:
                found += 1
    return found


def outcome_literals(tree):
    """Bare outcome words ("ok", "problems", ...) in code, not docstrings, where outcomes.py has constants."""
    docs = {id(n.body[0].value) for n in ast.walk(tree)
            if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef)) and n.body
            and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)}
    return sum(1 for n in ast.walk(tree) if isinstance(n, ast.Constant) and id(n) not in docs
               and n.value in OUTCOME_WORDS)


def measure(path, names):
    source = path.read_text()
    tree = ast.parse(source)
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    functions = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    main = next((f for f in functions if f.name == "main"), None)
    class_lines = sum(code_lines(ast.get_source_segment(source, c) or "") for c in classes)
    function_lines = sum(code_lines(ast.get_source_segment(source, f) or "") for f in functions)
    others = len(functions) - (1 if main else 0)
    main_len = span(main) if main else 0
    if not main:
        kind = "library"
    elif main_len <= THIN_MAIN and others <= THIN_FUNCTIONS:
        kind = "thin CLI"
    elif main_len <= THIN_MAIN:
        kind = "CLI with library"
    else:
        kind = "fat CLI"
    return {
        "name": path.stem, "lines": code_lines(source), "class_lines": class_lines,
        "function_lines": function_lines, "classes": classes, "functions": len(functions),
        "main": main_len, "kind": kind, "private": private_imports(tree, names - {path.stem}),
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
              f"{r['main']:4} {r['private']:4}  {r['kind']}")
    print("\nClass roles (from the docstring's first word, else '(name)' from the suffix, else '?'):")
    for r in rows:
        if r["roles"]:
            print(f"  {r['name']}: " + ", ".join(r["roles"]))
    total = sum(r["lines"] for r in rows)
    in_classes = sum(r["class_lines"] for r in rows)
    in_functions = sum(r["function_lines"] for r in rows)
    classes = sum(len(r["classes"]) for r in rows)
    roles = [x for r in rows for x in r["roles"]]
    kinds = {k: sum(1 for r in rows if r["kind"] == k) for k in ("library", "thin CLI", "CLI with library", "fat CLI")}
    fat_main = [r for r in rows if r["main"] > FAT_MAIN]
    private = [r for r in rows if r["private"]]
    print(f"\nTotal: {len(rows)} modules, {total} code lines, {classes} classes, "
          f"{sum(r['functions'] for r in rows)} top-level functions.")
    print(f"Code in classes: {in_classes} lines ({100 * in_classes // total}%). "
          f"In top-level functions: {in_functions} lines ({100 * in_functions // total}%). "
          f"The rest is module-level constants and imports.")
    print(f"Classes with a stated role: {sum(1 for x in roles if not x.endswith('?'))} of {classes} "
          f"({sum(1 for x in roles if not x.endswith(('?', '(name)')))} by docstring).")
    print("Module kinds: " + ", ".join(f"{v} {k}" for k, v in kinds.items()) + ".")
    print(f"A main() over {FAT_MAIN} lines: " + ", ".join(f"{r['name']} ({r['main']})" for r in
          sorted(fat_main, key=lambda r: -r["main"])) + ".")
    print(f"Modules that use another script's private name: {len(private)} "
          f"({sum(r['private'] for r in private)} uses): " + ", ".join(r["name"] for r in private) + ".")
    print("Largest modules: " + ", ".join(f"{r['name']} ({r['lines']})" for r in
          sorted(rows, key=lambda r: -r["lines"])[:8]) + ".")
    literals = [r for r in rows if r["literals"]]
    print(f"Bare outcome words in code: {sum(r['literals'] for r in literals)} in {len(literals)} modules: "
          + ", ".join(f"{r['name']} ({r['literals']})" for r in sorted(literals, key=lambda r: -r["literals"])) + ".")
    print(f"\nSCORE classes {100 * in_classes // total}% | fat CLIs {kinds['fat CLI']} | "
          f"thin CLIs {kinds['thin CLI']} | private imports {len(private)} | outcome literals {sum(r['literals'] for r in literals)} | roles stated "
          f"{sum(1 for x in roles if not x.endswith('?'))}/{classes}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
