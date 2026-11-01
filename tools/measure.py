"""Measure the shape of spark's scripts/ code: the P322 figures, and the breaches of the architecture rules.

    python3 tools/measure.py                  # the P322 figures (the code architecture discovery), ending in a SCORE line
    python3 tools/measure.py --rules          # each breach of a rule, one per line: rule:file:name:value
    python3 tools/measure.py --rules --accept # lower tests/architecture_baseline.json: values that fell, entries that are gone
    python3 tools/measure.py --rules --accept-new   # write it whatever it holds, new and risen breaches too (say why in the PR)

Stdlib only. It reads `scripts/` (every folder under it, but `scripts/stand_in/`, the MicroPython stand-in that is not
spark's code) and `tests/`. Only `--accept` and `--accept-new` write, and only the baseline. `tests/test_architecture.py` holds each
breach against that baseline, which may only shrink (P440). The rules are the table in
`docs/discovery/2026-10-19-p323-target-architecture/architecture/notes.md`.

Definitions of the P322 figures, one threshold each:
- A CLI is a module with a top-level main(). Fat CLI: its main() is over FAT_MAIN (80) lines, which means it holds logic.
  Thin CLI: main() is at most THIN_MAIN (40) lines and the module keeps at most THIN_FUNCTIONS (3) other functions.
  Every other CLI is "CLI with library". A module without main() is a library.
- Classes and functions are found at the top level and under a top-level if/try. Class and function lines
  include their decorators. The `if __name__ == "__main__":` block is counted as its own figure, not as a function.
- An outcome literal is a bare outcome word that is compared with (==, !=, in, not in), assigned to a name,
  attribute or keyword called status/verdict/outcome, or stored under a "status"/"verdict" key. Field names, other
  dict keys and display text do not count.
"""
import argparse
import ast
import builtins
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASELINE = "tests/architecture_baseline.json"
#: The role words of `docs/guide/patterns-and-names.md`.
ROLES = ("Service", "Strategy", "Adapter", "Result", "Error", "Value", "Store",
         "Decorator", "Renderer", "Platform", "Fake", "Operation")
THIN_MAIN = 40       # lines: a main() this long or shorter only parses and prints
THIN_FUNCTIONS = 3   # top-level functions besides main() a thin CLI may keep
FAT_MAIN = 80        # lines: a main() this long holds logic
OUTCOME_WORDS = {"ok", "problems", "could-not-run", "skipped"}  # outcomes.OK, PROBLEMS, ...
OUTCOME_NAMES = {"status", "verdict", "outcome"}
NAMEDTUPLE_API = {"_asdict", "_replace", "_fields", "_make"}  # public API of a namedtuple, not a private name


# --- Later, not MVP: the P322 discovery's figures, kept for its score line ---


def code_lines(source):
    """Lines that are neither blank nor a comment (docstrings count as code)."""
    return sum(1 for line in source.splitlines() if line.strip() and not line.strip().startswith("#"))


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
    word = role_word_of(cls)
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


def print_figures(root):
    """Print the P322 figures of `root/scripts`, ending in the SCORE line."""
    paths = script_paths(root)
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
    print(f"Interfaces: {len(list((pathlib.Path(root) / 'commands').glob('*.md')))} commands, "
          f"{len(list((pathlib.Path(root) / 'agents').glob('*.md')))} agents, "
          f"{sum(1 for r in rows if r['main'])} scripts with a main().")
    literals = [r for r in rows if r["literals"]]
    print(f"Outcome words used as an outcome (compared, assigned, status key): {sum(r['literals'] for r in literals)} in {len(literals)} modules: "
          + ", ".join(f"{r['name']} ({r['literals']})" for r in sorted(literals, key=lambda r: -r["literals"])) + ".")
    print(f"\nSCORE classes {100 * in_classes // total}% | fat CLIs {kinds['fat CLI']} | "
          f"thin CLIs {kinds['thin CLI']} | private imports {len(private)} | outcome literals {sum(r['literals'] for r in literals)} | roles stated "
          f"{sum(1 for x in roles if not x.endswith('?'))}/{classes}")


# --- MVP ---
# The rules (P440): each breach is `rule:file:name:value`, held against tests/architecture_baseline.json


def span(node):
    """Lines of a def or class, from its first decorator to its last line."""
    first = min([node.lineno] + [d.lineno for d in node.decorator_list])
    return node.end_lineno - first + 1


def role_word_of(cls):
    """The first word of a class's docstring without its ':' or '.', or '' when it has none."""
    first = (ast.get_docstring(cls) or "").split(maxsplit=1)
    return first[0].rstrip(":.") if first else ""


def script_paths(root):
    """Every `.py` under `root/scripts`, in folders too, but not the MicroPython stand-in."""
    scripts = pathlib.Path(root) / "scripts"
    return sorted(path for path in scripts.rglob("*.py") if "stand_in" not in path.relative_to(scripts).parts)


FUNCTION_LINES = {"spark": 40, "old": 60}  # R1: a function in scripts/spark/, and in a script not yet moved there
MODULE_LINES = 600                          # R1: a module
MAIN_LINES = 15                             # R1: a `main`, which only parses and prints
NESTING = 3                                 # R2
PARAMETERS = 5                              # R3, without self or cls
#: U1: the modules that import nothing of spark, so that every reader can use them without importing another reader.
LEAVES = ("board_codes", "outcomes", "provenance", "text_guards", "zone_time")
#: U1: the names OC8 (P418) moved into `text_guards`, by the module that held them. No script reads them from there again.
MOVED_GUARDS = {"drawer": {"clean", "CONTROL", "LABEL_MAX", "TEXT_MAX", "TAGS_MAX"}, "parts": {"one_line", "COMMENT_UNSAFE"}}
#: X2: a class that may print, read and exit in `scripts/spark/`: the Renderers (by role word) and the terminal consent.
TERMINAL_CLASSES = ("TerminalConsentStrategy",)
#: X2: the one function that prints in `scripts/spark/`, by file and top-level name: the CLI frontend, which prints what a
#: Renderer rendered (P442). A nested def or a method of that name elsewhere is counted.
TERMINAL_FUNCTIONS = (("scripts/spark/core/cli.py", "run_cli"),)
EXCEPTION_NAMES = {name for name, value in vars(builtins).items() if isinstance(value, type) and issubclass(value, BaseException)}
#: T1: the calls of `time` that read the clock or sleep.
CLOCK_CALLS = {"time", "time_ns", "monotonic", "monotonic_ns", "perf_counter", "perf_counter_ns", "process_time", "sleep",
               "localtime", "gmtime"}
#: T1: the calls of `time` that read the clock only when they get fewer arguments than this (no time tuple); with a tuple they are pure.
CLOCK_WHEN_BARE = {"strftime": 2, "asctime": 1, "ctime": 1}
#: T1 and X2: the modules an `import X as Y` may hide.
TRACKED = ("subprocess", "time", "urllib", "os", "datetime", "sys")

#: Each rule in a sentence. The failure messages, the docstrings of the test methods and `--rules` read this one table.
RULES = {
    "R1": "a function, a module and a main are short (a function %d lines in scripts/spark/ and %d elsewhere, a module %d, a main %d)"
          % (FUNCTION_LINES["spark"], FUNCTION_LINES["old"], MODULE_LINES, MAIN_LINES),
    "R2": "nesting is at most %d deep, and an elif is no level" % NESTING,
    "R3": "a function takes at most %d parameters, without self" % PARAMETERS,
    "R6": "a class docstring starts with a role word of docs/guide/patterns-and-names.md",
    "T1": "only an Adapter runs a program, reads the clock or the environment, calls the network or writes a file",
    "T2": "a test file never adds a mock.patch (mock.patch.dict on os.environ is the exception)",
    "T4": "code never branches on what is imported, as in `\"unittest\" in sys.modules`",
    "X2": "scripts/spark/ holds no main, print, input, stdin, stdout, stderr or exit outside a Renderer, the terminal consent and run_cli",
    "U1": "a leaf imports nothing of spark, matching imports no drawer, and no script reads a moved guard from its old module",
    "C1": "a file name under scripts/ is unique, and an exception name ends in Error",
    "C3": "an exit code has no second name (no EXIT_ alias)",
    "V1": "a call of a ValueMessageError or a subclass gives a constant string as the template and the values as arguments (P444)",
}

#: V1: the class whose raises give a template and its values.
VALUE_MESSAGE = "ValueMessageError"
Breach = collections.namedtuple("Breach", "rule file name value")
#: One source file: its path under the root (with `/`), its tree and its text.
SourceFile = collections.namedtuple("SourceFile", "file tree text")
#: What a rule needs to know of the other scripts: their stems and the names of the exceptions they define.
ScriptNames = collections.namedtuple("ScriptNames", "stems exceptions value_messages", defaults=(frozenset(),))
#: One difference between the breaches and the baseline. `kind` is one of NEW, ROSE, FELL and GONE.
Drift = collections.namedtuple("Drift", "key kind found allowed")
NEW, ROSE, FELL, GONE = "new-breach", "value-rose", "value-fell", "entry-gone"
#: The kinds that fail the test. A value that fell passes: `--rules --accept` writes it back.
FAILING = (NEW, ROSE, GONE)


def functions_of(tree, prefix=""):
    """Every def under `tree` as (qualified name, node): a method is `Class.method`, a nested def `outer.inner`."""
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield prefix + node.name, node
            yield from functions_of(node, prefix + node.name + ".")
        elif isinstance(node, ast.ClassDef):
            yield from functions_of(node, prefix + node.name + ".")
        else:
            yield from functions_of(node, prefix)


def classes_of(tree, prefix=""):
    """Every class under `tree` as (qualified name, node): a nested class is `Outer.Inner`."""
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            yield prefix + node.name, node
            yield from classes_of(node, prefix + node.name + ".")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield from classes_of(node, prefix + node.name + ".")
        else:
            yield from classes_of(node, prefix)


def imports_of(tree):
    """Every module the tree imports, at the top or inside a function, by its first name."""
    names = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    return names | {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}


def _is_elif(node):
    """True for the else of an If that holds one If and nothing else: that is an `elif`."""
    return len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If)


def depth_of(function):
    """How deep the function nests if, for, while, try and with: 0 for a body of plain statements. An `elif` is no level."""
    def deepest(body, level):
        found = level
        for node in body:
            if isinstance(node, ast.If):
                found = max(found, deepest(node.body, level + 1),
                            deepest(node.orelse, level if _is_elif(node) else level + 1))
            elif isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
                found = max(found, deepest(node.body + node.orelse, level + 1))
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                found = max(found, deepest(node.body, level + 1))
            elif isinstance(node, ast.Try):
                found = max(found, deepest(node.body + node.orelse + node.finalbody + [s for h in node.handlers for s in h.body], level + 1))
        return found
    return deepest(function.body, 0)


def walk_outside(node, skipped):
    """Every node under `node` except those under a node for which `skipped(node)` is true."""
    for child in ast.iter_child_nodes(node):
        if skipped(child):
            continue
        yield child
        yield from walk_outside(child, skipped)


def _is_adapter(node):
    return isinstance(node, ast.ClassDef) and role_word_of(node) == "Adapter"


def _may_print(node):
    return isinstance(node, ast.ClassDef) and (role_word_of(node) == "Renderer" or node.name in TERMINAL_CLASSES)


def _terminal_functions(source):
    """The top-level defs of `source` that X2 names in TERMINAL_FUNCTIONS, by id."""
    return {id(node) for node in source.tree.body if isinstance(node, ast.FunctionDef) and (source.file, node.name) in TERMINAL_FUNCTIONS}


def _dotted(node):
    """`a.b.c` for a Name or an Attribute chain, else ''."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute) and _dotted(node.value):
        return _dotted(node.value) + "." + node.attr
    return ""


def aliases_of(tree):
    """{name: what it stands for} for `import subprocess as sp` and `from datetime import datetime as dt`, of the modules in TRACKED."""
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update({a.asname: a.name for a in node.names if a.asname and a.name.split(".")[0] in TRACKED})
        elif isinstance(node, ast.ImportFrom) and node.module in ("datetime", "urllib"):
            found.update({a.asname: node.module + "." + a.name for a in node.names if a.asname})
    return found


def _resolved(node, aliases):
    """`_dotted(node)` with its first name replaced by what an alias stands for."""
    first, _, rest = _dotted(node).partition(".")
    return (aliases.get(first, first) + ("." + rest if rest else "")) if first else ""


def _writes_a_file(call):
    """True for write_text, write_bytes and an open() whose mode writes, appends or creates."""
    if isinstance(call.func, ast.Attribute) and call.func.attr in ("write_text", "write_bytes"):
        return True
    on_name = isinstance(call.func, ast.Name) and call.func.id == "open"
    if not on_name and not (isinstance(call.func, ast.Attribute) and call.func.attr == "open"):
        return False
    mode = next((k.value for k in call.keywords if k.arg == "mode"), None)
    place = 1 if on_name else 0  # open(path, mode) against path.open(mode)
    if mode is None and len(call.args) > place:
        mode = call.args[place]
    return isinstance(mode, ast.Constant) and isinstance(mode.value, str) and any(c in mode.value for c in "wax+")


def _effect(node, aliases):
    """The outside that T1 sees `node` reach: subprocess, time, urllib, datetime, os.environ, os.getenv or file-write, else ''."""
    if isinstance(node, ast.ImportFrom):
        module, imported = node.module or "", {a.name for a in node.names}
        if module == "subprocess" or module == "time" and imported & CLOCK_CALLS:
            return module
        if module.startswith("urllib.request") or module == "urllib" and "request" in imported:
            return "urllib"
        if module == "os":
            return "os.environ" if "environ" in imported else "os.getenv" if "getenv" in imported else ""
    elif isinstance(node, ast.Attribute):
        whole, base = _resolved(node, aliases), _resolved(node.value, aliases)
        if base == "subprocess" or base == "time" and node.attr in CLOCK_CALLS:
            return base
        if whole in ("urllib.request", "os.environ", "os.getenv"):
            return "urllib" if whole == "urllib.request" else whole
        if node.attr in ("now", "utcnow", "today") and base.split(".")[-1] in ("datetime", "date"):
            return "datetime"
    elif isinstance(node, ast.Call):
        if _writes_a_file(node):
            return "file-write"
        if isinstance(node.func, ast.Attribute) and _resolved(node.func.value, aliases) == "time" \
                and len(node.args) + len(node.keywords) < CLOCK_WHEN_BARE.get(node.func.attr, 0):
            return "time"
    return ""


def _count(rule, source, seen):
    """One Breach per name in the Counter `seen` that was counted at least once."""
    return [Breach(rule, source.file, name, count) for name, count in sorted(seen.items()) if count]


def long_code(source, known):
    """R1 (see RULES): a function, a module or a main over its limit; a `main` is one entry."""
    limit = FUNCTION_LINES["spark" if source.file.startswith("scripts/spark/") else "old"]
    found = []
    for name, node in functions_of(source.tree):
        if span(node) > (MAIN_LINES if name == "main" else limit):
            found.append(Breach("R1", source.file, name, span(node)))
    lines = len(source.text.splitlines())
    if lines > MODULE_LINES:
        found.append(Breach("R1", source.file, "<module>", lines))
    return found


def deep_nesting(source, known):
    """R2 (see RULES): a function that nests too deep."""
    return [Breach("R2", source.file, name, depth_of(node)) for name, node in functions_of(source.tree) if depth_of(node) > NESTING]


def many_parameters(source, known):
    """R3 (see RULES): a function with too many parameters, not counting self or cls."""
    found = []
    for name, node in functions_of(source.tree):
        args = node.args
        names = [a.arg for a in args.posonlyargs + args.args + args.kwonlyargs] + [a.arg for a in (args.vararg, args.kwarg) if a]
        count = len(names) - (1 if names and names[0] in ("self", "cls") else 0)
        if count > PARAMETERS:
            found.append(Breach("R3", source.file, name, count))
    return found


def class_without_role(source, known):
    """R6: a class whose docstring does not start with a role word. The count is per qualified name."""
    return _count("R6", source, collections.Counter(name for name, node in classes_of(source.tree) if role_word_of(node) not in ROLES))


def effect_outside_adapter(source, known):
    """T1: subprocess, time, urllib, datetime, os.environ, os.getenv or a file write, outside a class whose docstring says Adapter."""
    aliases = aliases_of(source.tree)
    seen = collections.Counter(_effect(node, aliases) for node in walk_outside(source.tree, _is_adapter))
    del seen[""]  # a node that reaches nothing outside
    return _count("T1", source, seen)


def branch_on_imports(source, known):
    """T4: a branch whose test reads `sys.modules`, like `"unittest" in sys.modules`. Each read counts once."""
    reads = set()
    for node in ast.walk(source.tree):
        if isinstance(node, (ast.If, ast.IfExp, ast.While)):
            reads |= {id(n) for n in ast.walk(node.test) if _dotted(n) == "sys.modules"}
    return _count("T4", source, collections.Counter({"sys.modules": len(reads)}))


def output_in_spark(source, known):
    """X2: main, print, input, sys.stdin, sys.stdout, sys.stderr, sys.exit, readline or SystemExit in scripts/spark/, outside the Renderers, the terminal consent and `run_cli`."""
    if not source.file.startswith("scripts/spark/"):
        return []
    aliases, seen, exempt = aliases_of(source.tree), collections.Counter(), _terminal_functions(source)
    for node in walk_outside(source.tree, lambda node: _may_print(node) or id(node) in exempt):
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            seen["main"] += 1
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("print", "input"):
            seen[node.func.id] += 1
        elif isinstance(node, ast.Attribute) and _resolved(node, aliases) in ("sys.stdin", "sys.stdout", "sys.stderr", "sys.exit"):
            seen[_resolved(node, aliases)] += 1
        elif isinstance(node, ast.Attribute) and node.attr == "readline":
            seen["readline"] += 1
        elif isinstance(node, ast.Raise) and _dotted(node.exc.func if isinstance(node.exc, ast.Call) else node.exc) == "SystemExit":
            seen["SystemExit"] += 1
    return _count("X2", source, seen)


def old_reads(tree):
    """Each moved name the tree reaches through its old module: `drawer.clean`, `parts_library.one_line`, `from drawer import clean`."""
    bound = {alias.asname or alias.name: alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
             for alias in node.names if alias.name in MOVED_GUARDS}
    reads = {"%s.%s" % (bound[node.value.id], node.attr) for node in ast.walk(tree)
             if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id in bound
             and node.attr in MOVED_GUARDS[bound[node.value.id]]}
    return reads | {"%s.%s" % (node.module, alias.name) for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom) and node.module in MOVED_GUARDS
                    for alias in node.names if alias.name in MOVED_GUARDS[node.module]}


def leaf_imports(source, known):
    """U1: a leaf that imports a script or `spark`, `matching` that imports `drawer`, a script that reads a moved guard from its old module."""
    stem = pathlib.PurePosixPath(source.file).stem
    imported = imports_of(source.tree)
    found = []
    if stem in LEAVES:
        found += [Breach("U1", source.file, "imports-" + name, 1) for name in sorted(imported & (known.stems | {"spark"}) - {stem})]
    if stem == "matching" and "drawer" in imported:
        found.append(Breach("U1", source.file, "imports-drawer", 1))
    return found + [Breach("U1", source.file, "reads-" + name, 1) for name in sorted(old_reads(source.tree))]


def unnamed_error(source, known):
    """C1: an exception class whose name does not end in Error. The count is per qualified name."""
    return _count("C1", source, collections.Counter(name for name, node in classes_of(source.tree)
                                                   if node.name in known.exceptions and not node.name.endswith("Error")))


def raw_value_message(source, known):
    """
    V1: a call of a ValueMessageError or a subclass, in a raise or before it, whose template (the first argument, or the
    keyword `template`) is no string constant, such as a `%`, an f-string, a name or a call, or whose arguments hold a `**`.
    Only `scripts/spark/core/text_guards.py`, where the helpers hand their own `template` on, may pass the bare name
    `template`. The count is per class name. Known limits: a class under another name (`import ToolProblem as SP`,
    `P = ToolProblem`) is not seen; `X.of_lines(...)` is not counted, because it is safe by construction; a helper
    `def f(template)` outside text_guards is counted, so the baseline or a fix covers it.
    """
    seen = collections.Counter()
    handing_on = source.file.endswith("spark/core/text_guards.py")
    for node in ast.walk(source.tree):
        name = _dotted(node.func).split(".")[-1] if isinstance(node, ast.Call) and isinstance(node.func, (ast.Name, ast.Attribute)) else ""
        if name not in known.value_messages:
            continue
        first = node.args[0] if node.args else next((each.value for each in node.keywords if each.arg == "template"), None)
        constant = isinstance(first, ast.Constant) and isinstance(first.value, str)
        passed_on = handing_on and isinstance(first, ast.Name) and first.id == "template"
        if (first is not None and not constant and not passed_on) or (not handing_on and any(each.arg is None for each in node.keywords)):
            seen[name] += 1
    return _count("V1", source, seen)


def exit_alias(source, known):
    """C3: `from outcomes import X as EXIT_Y` with another name, or `EXIT_Y = ...EXIT_X`: a second name for an exit code."""
    seen = collections.Counter()
    for node in ast.walk(source.tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.asname and alias.asname.startswith("EXIT_") and alias.asname != alias.name:
                    seen[alias.asname] += 1
        elif isinstance(node, ast.Assign) and _dotted(node.value).split(".")[-1].startswith("EXIT_"):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.startswith("EXIT_"):
                    seen[target.id] += 1
    return _count("C3", source, seen)


#: The rules that read one script. T2 reads the tests and the two clauses on the whole tree (C1 file names, U1 leaves) are in `breaches`.
#: T1, T2, T4, X2 and C3 count the breaches of a file under one key: they say how many, not where.
SCRIPT_RULES = (long_code, deep_nesting, many_parameters, class_without_role, effect_outside_adapter, branch_on_imports,
                output_in_spark, leaf_imports, unnamed_error, exit_alias, raw_value_message)


def mock_patches(source):
    """T2: the `mock.patch` calls of a test file, without `mock.patch.dict(os.environ, ...)`."""
    count = 0
    for node in ast.walk(source.tree):
        name = _dotted(node.func) if isinstance(node, ast.Call) else ""
        if name == "patch" or name.startswith(("mock.patch", "unittest.mock.patch", "patch.")):
            on_environ = name.endswith(".dict") and node.args and _dotted(node.args[0]) == "os.environ"
            count += 0 if on_environ else 1
    return [Breach("T2", source.file, "mock.patch", count)] if count else []


def sources_of(root, paths):
    """The SourceFile of each path under `root`."""
    found = []
    for path in paths:
        text = path.read_text()
        found.append(SourceFile(path.relative_to(root).as_posix(), ast.parse(text), text))
    return found


def subclasses_of(scripts, roots):
    """The names of the classes the scripts define that have one of `roots` for a base, found until no more turn up, `roots` included."""
    classes = [(node.name, {_dotted(b).split(".")[-1] for b in node.bases})
               for source in scripts for node in ast.walk(source.tree) if isinstance(node, ast.ClassDef)]
    known = set(roots)
    while True:
        more = {name for name, bases in classes if bases & known} - known
        if not more:
            return known
        known |= more


def exceptions_of(scripts):
    """The names of the exception classes the scripts define: a class with an exception for a base, found until no more turn up."""
    return subclasses_of(scripts, EXCEPTION_NAMES) - EXCEPTION_NAMES


def breaches(root=ROOT):
    """Every breach under `root`, as {'rule:file:name': value}; a name met twice in a file keeps the larger value."""
    root = pathlib.Path(root)
    scripts = sources_of(root, script_paths(root))
    stems = {pathlib.PurePosixPath(s.file).stem for s in scripts}
    known = ScriptNames(stems, exceptions_of(scripts), subclasses_of(scripts, {VALUE_MESSAGE}))
    found = [b for source in scripts for rule in SCRIPT_RULES for b in rule(source, known)]
    found += [b for source in sources_of(root, sorted((root / "tests").glob("test_*.py"))) for b in mock_patches(source)]
    names = collections.Counter(pathlib.PurePosixPath(s.file).name for s in scripts if not s.file.endswith("__init__.py"))
    found += [Breach("C1", s.file, "basename", 1) for s in scripts if names[pathlib.PurePosixPath(s.file).name] > 1]
    found += [Breach("U1", "scripts", "no-leaf-" + leaf, 1) for leaf in LEAVES if leaf not in stems]
    kept = {}
    for b in found:
        key = "%s:%s:%s" % (b.rule, b.file, b.name)
        kept[key] = max(b.value, kept.get(key, 0))
    return dict(sorted(kept.items()))


def compare(found, baseline, rule=None):
    """Where the breaches `found` differ from the `baseline` (both {key: value}), for one rule or all: a list of Drift."""
    said = []
    for key in sorted(set(found) | set(baseline)):
        if rule and key.split(":")[0] != rule:
            continue
        if key not in baseline:
            said.append(Drift(key, NEW, found[key], None))
        elif key not in found:
            said.append(Drift(key, GONE, None, baseline[key]))
        elif found[key] != baseline[key]:
            said.append(Drift(key, ROSE if found[key] > baseline[key] else FELL, found[key], baseline[key]))
    return said


def explain(drift):
    """One sentence for a Drift: the rule and its limit, the file, the name and the values, and what to do."""
    rule, file, name = drift.key.split(":", 2)
    where = "%s: %s" % (rule, RULES[rule])
    lists = "`python3 tools/measure.py --rules` lists every breach"
    return {
        NEW: "%s -- %s in %s is %s and the baseline does not list it. Fix it; %s" % (where, name, file, drift.found, lists),
        ROSE: "%s -- %s in %s rose from %s to %s. Fix it; %s" % (where, name, file, drift.allowed, drift.found, lists),
        GONE: "%s -- the baseline lists %s in %s at %s and the code no longer has it. Remove the entry with `python3 tools/measure.py --rules --accept`"
              % (where, name, file, drift.allowed),
        FELL: "%s -- %s in %s fell from %s to %s. Write it back with `python3 tools/measure.py --rules --accept`"
              % (where, name, file, drift.allowed, drift.found),
    }[drift.kind]


def read_baseline(root=ROOT):
    """The baseline under `root` as {key: value}; {} when there is no file."""
    path = pathlib.Path(root) / BASELINE
    return json.loads(path.read_text()) if path.is_file() else {}


def write_baseline(found, root=ROOT):
    """Write the baseline: valid JSON, one sorted line per entry, so that two branches merge line by line."""
    path = pathlib.Path(root) / BASELINE
    path.parent.mkdir(parents=True, exist_ok=True)
    entries = ["%s: %d" % (json.dumps(key), found[key]) for key in sorted(found)]
    path.write_text("{\n" + ",\n".join(entries) + ("\n" if entries else "") + "}\n")


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--rules", action="store_true", help="print each breach of the architecture rules, one per line: rule:file:name:value")
    parser.add_argument("--accept", action="store_true",
                        help="with --rules: write the breaches as the new tests/architecture_baseline.json, for values that fell "
                             "and entries that are gone. It refuses a new or risen breach")
    parser.add_argument("--accept-new", action="store_true",
                        help="with --rules: write the baseline whatever it holds, new and risen breaches too. Give the reason in the PR")
    args = parser.parse_args(argv)
    if (args.accept or args.accept_new) and not args.rules:
        parser.error("--accept and --accept-new go with --rules")
    if not args.rules:
        print_figures(root)
        return 0
    found = breaches(root)
    for key, value in found.items():
        print("%s:%d" % (key, value))
    for rule in sorted({key.split(":")[0] for key in found}):
        print("%s: %s" % (rule, RULES[rule]), file=sys.stderr)
    if args.accept or args.accept_new:
        worse = [d for d in compare(found, read_baseline(root)) if d.kind in (NEW, ROSE)]
        if worse and not args.accept_new:
            for drift in worse:
                print(explain(drift), file=sys.stderr)
            print("not written: --accept takes only values that fell and entries that are gone. Fix the breaches above, or use "
                  "--accept-new and give the reason in the PR", file=sys.stderr)
            return 1
        write_baseline(found, root)
        print("wrote %s: %d entries" % (BASELINE, len(found)), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
