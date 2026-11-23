"""
The deepsleep calls of a project's firmware/ (P1022 slice 3): a fact read from the project's files, never from the board.

A call counts when it calls MicroPython's `machine.deepsleep` (MicroPython v1.29.0 docs/library/machine.rst lines 267-285:
it stops execution, and on wake runs from main again) through a name the file binds to it: `import machine [as m]`,
`from machine import deepsleep [as ds]` or `ds = machine.deepsleep`. A name the file also binds another way (a parameter,
a def, any other assignment) does not count, so a driver's `Epd().deepsleep()` and a local `def deepsleep` are not calls.
`from machine import *`, `umachine` and an annotated alias are misses, which leave the text as it was without them. A
file that does not parse is named in `unparsed`. Light sleep stays out.
"""

import ast
import collections
from pathlib import Path

#: Value: `places` are the calls, "firmware/<file>:<line>", sorted by file then line; `unparsed` the "firmware/<file>"
#: paths that spark could not read or parse, so it does not know whether they call deepsleep.
SleepCalls = collections.namedtuple("SleepCalls", "places unparsed")


def _bound(tree):
    """({names bound to the machine module}, {names bound to machine.deepsleep}) of one file's tree. ast.walk visits a
    node before its children, so an alias's own target is known before its Name is."""
    machines, sleeps, other, aliases = set(), set(), set(), {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                (machines if alias.name == "machine" else other).add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                (sleeps if (node.module, alias.name) == ("machine", "deepsleep") else other).add(alias.asname or alias.name)
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            aliases[node.targets[0]] = node.value
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            other.add(node.name)
        elif isinstance(node, ast.arg) or isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store) and node not in aliases:
            other.add(node.arg if isinstance(node, ast.arg) else node.id)
    machines -= other
    for target, value in aliases.items():
        (sleeps if _is_sleep(value, machines) else other).add(target.id)
    return machines, sleeps - other


def _is_sleep(value, machines):
    """True when `value` is `<name>.deepsleep` and the name is one of `machines`."""
    return (isinstance(value, ast.Attribute) and value.attr == "deepsleep" and isinstance(value.value, ast.Name)
            and value.value.id in machines)


def deep_sleep_calls(project):
    """The SleepCalls of every .py file under `project`/firmware; none without that folder."""
    places, unparsed = [], []
    firmware = Path(project) / "firmware"
    for source in sorted(firmware.rglob("*.py")) if firmware.is_dir() else ():
        name = "firmware/%s" % source.relative_to(firmware).as_posix()
        try:
            tree = ast.parse(source.read_bytes())
        except (SyntaxError, ValueError, OSError):
            unparsed.append(name)
            continue
        machines, sleeps = _bound(tree)
        places += [(name, node.lineno) for node in ast.walk(tree) if isinstance(node, ast.Call)
                   and (_is_sleep(node.func, machines) or isinstance(node.func, ast.Name) and node.func.id in sleeps)]
    return SleepCalls(tuple("%s:%d" % place for place in sorted(places)), tuple(unparsed))
