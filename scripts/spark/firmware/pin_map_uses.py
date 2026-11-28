"""
The pin names a project's firmware uses, read against its pin map (P882, #1250): a fact read from the project's files with
`ast`, never from the board. Nothing is imported, compiled or run, so `firmware/pins.py` is read as text like the rest.

The pin map is `firmware/pins.py`, plain `NAME = value` lines that the build writes. A pin name is a name it binds at module level
(an assignment target, a def, a class or an import, also inside an `if` or a `try`). A use is one pin name at one file and
line: `pins.X` where the file did `import pins [as p]`, and each name of `from pins import X [as Y]`, at the import's line. The
files read are every `.py` under firmware/ but the pin map itself, `firmware/lib/` (the drivers' folder) and the secrets files.
What the check cannot compare is a place: `from pins import *`, the module alias used as a value (`p = pins`, `getattr(pins, "X")`),
and a module alias that the file also binds another way (a parameter, a def, an assignment). A file that does not parse, or a map
that takes names it does not show, is not-checked: no name was compared. Spark exports facts: this says whether a name is in the
map, never whether the pin is wired or right.
"""

import ast
import collections
from pathlib import Path

from spark.core.outcomes import NOT_CHECKED, NOT_CHECKED_MESSAGE, RECORDED
from spark.core.text_guards import printable
from spark.firmware.import_probe import PIN_MAP, PIN_MODULE
from spark.firmware.project_secrets import FIRMWARE_FOLDER, is_secret_path
from spark.records.folder_walk import files_under

# --- MVP ---
#: The pin map in the project, as a line says it, and the drivers' folder in firmware/.
PIN_MAP_PATH, LIB_FOLDER = "%s/%s" % (FIRMWARE_FOLDER, PIN_MAP), "lib/"
#: What a place says of itself (`form`), after the file and line it names.
STAR_FORM = "takes every name of pins.py with *, so the names it uses are not compared"
VALUE_FORM = "uses the pin map as a value, so the names it reaches are not compared"
REBOUND_FORM = "also uses the name %s for something else (line %d), so its pin names are not compared"
#: Why a map was not read, one sentence each.
NO_FOLDER_WHY = "no firmware/ folder"
CANNOT_PARSE_WHY, CANNOT_READ_WHY = "%s does not parse%s", "%s cannot be read"
OPEN_MAP_WHY = PIN_MAP_PATH + " takes names that it does not show (%s)"
#: The sentence of a missing use: `<file>:<line> uses pins.X`, or `imports X from pins`, then what the map lacks.
USES_SENTENCE, IMPORTS_SENTENCE = "%s:%d uses %s.%s, and %s has no %s", "%s:%d imports %s from %s, and %s has no %s"
#: The kept line (W3, W4) in its parts.
LINE_FOUND, LINE_NONE = "pin map: %d of %d uses found in " + PIN_MAP_PATH, "pin map: none compared"
LINE_MISSING, LINE_PLACES, LINE_NOT_READ = ", not found: %s", ", not compared in %d place%s, first %s:%d", "pin map: not checked (%s)"
LINE_MISSING_ITEM = "%s (%s:%d)"
#: With no firmware/pins.py the line and the finding say so, for one use and for more (`has_map` is false in the data then).
NO_MAP_ONE = PIN_MAP_PATH + " is not there, and 1 use needs it, first %s:%d"
NO_MAP_MANY = PIN_MAP_PATH + " is not there, and %d uses need it, first %s:%d"
LINE_PREFIX = "pin map: "

Place = collections.namedtuple("Place", "file line form")


class PinUse(collections.namedtuple("PinUse", "name file line imported", defaults=(False,))):
    """Value: one pin name used at `file`:`line`; `imported` is True for a name of `from pins import`."""

    __slots__ = ()

    def sentence(self):
        """What a missing use says: its place, the name and that the pin map lacks it."""
        file = printable(self.file)
        if self.imported:
            return IMPORTS_SENTENCE % (file, self.line, self.name, PIN_MODULE, PIN_MAP_PATH, self.name)
        return USES_SENTENCE % (file, self.line, PIN_MODULE, self.name, PIN_MAP_PATH, self.name)


class PinMapUses(collections.namedtuple("PinMapUses", "state why where has_map used missing places names",
                                        defaults=(None, None, True, 0, (), (), ()))):
    """
    Value: the pin names of a project's firmware against its pin map. `state` is `recorded` (`used` uses were compared,
    `missing` holds those whose name the map lacks, `places` what could not be compared, `names` the map's names, and
    `has_map` is False when firmware/pins.py is not there, so every use is missing) or `not-checked`, with `why` and `where`, the file
    that it names (None without a firmware/ folder). It never raises: `read` gives not-checked for what it cannot read.
    """

    __slots__ = ()

    @classmethod
    def read(cls, project):
        """The PinMapUses of `project`: the files under firmware/ read with `ast`, none run."""
        firmware = Path(project) / FIRMWARE_FOLDER
        if not firmware.is_dir():
            return cls(NOT_CHECKED, NO_FOLDER_WHY)
        names, has_map = (), False
        pins = firmware / PIN_MAP
        if pins.is_file():
            tree, failure = _parse(pins, PIN_MAP_PATH)
            if failure:
                return cls(NOT_CHECKED, failure, PIN_MAP_PATH)
            names, open_why = _map_names(tree)
            if open_why:
                return cls(NOT_CHECKED, OPEN_MAP_WHY % open_why, PIN_MAP_PATH)
            has_map = True
        uses, places = set(), set()
        for source in files_under(firmware):
            relative = source.relative_to(firmware).as_posix()
            name = "%s/%s" % (FIRMWARE_FOLDER, relative)
            if source.suffix != ".py" or relative == PIN_MAP or relative.startswith(LIB_FOLDER) or is_secret_path(name):
                continue
            tree, failure = _parse(source, name)
            if failure:
                return cls(NOT_CHECKED, failure, name)
            found, not_compared = _uses_in(tree)
            uses.update(PinUse(each, name, line, imported) for each, line, imported in found)
            places.update(Place(name, line, form) for line, form in not_compared)
        uses = _one_per_place(sorted(uses))
        missing = tuple(each for each in uses if each.name not in names)
        return cls(RECORDED, None, None, has_map, len(uses), missing, tuple(sorted(places)), tuple(sorted(names)))

    def to_data(self):
        """The `pin_map` of the answer and of the check record, JSON values. `has_map` is `false` only when firmware/pins.py is not there."""
        if self.state != RECORDED:
            return {"state": self.state, "why": self.why}
        data = {"state": self.state, "used": self.used,
                "missing": [{"name": each.name, "file": each.file, "line": each.line} for each in self.missing],
                "not_compared": [place._asdict() for place in self.places], "names": list(self.names)}
        return data if self.has_map else dict(data, has_map=False)

    def changed_since(self, kept):
        """(gained, lost), the map's names now against `kept`, the `pin_map` data of an earlier record, each a sorted tuple
        (P1270). None when this Value is not recorded or has no map, and when `kept` holds no list of strings at `names`
        (a record from before the key, never guessed). It compares names only, so a pin that moved keeps its name."""
        before = kept.get("names") if isinstance(kept, dict) else None
        if self.state != RECORDED or not self.has_map or not isinstance(before, list) or not all(isinstance(one, str) for one in before):
            return None
        return tuple(sorted(set(self.names) - set(before))), tuple(sorted(set(before) - set(self.names)))

    def assumptions(self):
        """One `not checked: ...` sentence for each place the check could not compare."""
        return [NOT_CHECKED_MESSAGE % ("%s:%d %s" % (printable(each.file), each.line, each.form)) for each in self.places]

    @staticmethod
    def line_from(data, missing_only=False):
        """The kept result line of a `pin_map` (what `to_data` gives, or the record's copy). Never raises.
        None when the map has no use and no place.
        None when the data is of any other shape.
        None when `missing_only` and the map lacks no name."""
        recorded = _shape_of(data)
        if recorded is None:
            return None
        if recorded is False:  # not-checked, with its why
            return None if missing_only else printable(LINE_NOT_READ % data["why"])
        missing, places = data["missing"], data["not_compared"]
        if missing_only and not missing or not data["used"] and not places:
            return None
        if data.get("has_map") is False and missing:  # every use is missing: the map is not there
            first = min(missing, key=lambda each: (each["file"], each["line"]))
            line = LINE_PREFIX + no_map_sentence(len(missing), first["file"], first["line"])
        else:
            line = LINE_FOUND % (data["used"] - len(missing), data["used"]) if data["used"] else LINE_NONE
        if missing and data.get("has_map") is not False:
            line += LINE_MISSING % ", ".join(LINE_MISSING_ITEM % (each["name"], each["file"], each["line"]) for each in missing)
        if places:
            first = min(places, key=lambda each: (each["file"], each["line"]))
            line += LINE_PLACES % (len(places), "" if len(places) == 1 else "s", first["file"], first["line"])
        return printable(line)


def no_map_sentence(count, file, line):
    """The sentence for `count` uses that need the pin map when it is not there, `file`:`line` the first of them."""
    return NO_MAP_ONE % (file, line) if count == 1 else NO_MAP_MANY % (count, file, line)


def _is_count(value):
    return type(value) is int and value >= 0


def _shape_of(data):
    """True for the data of a recorded map, False for one that was not read, None for any other shape."""
    if not isinstance(data, dict):
        return None
    if data.get("state") == NOT_CHECKED:
        return False if isinstance(data.get("why"), str) else None
    missing, places = data.get("missing"), data.get("not_compared")
    if data.get("state") != RECORDED or not _is_count(data.get("used")) or not isinstance(missing, list) or not isinstance(places, list):
        return None
    if len(missing) > data["used"] or "has_map" in data and not isinstance(data["has_map"], bool):
        return None
    well_made = (all(isinstance(each, dict) and isinstance(each.get("name"), str) and isinstance(each.get("file"), str)
                     and _is_count(each.get("line")) for each in missing)
                 and all(isinstance(each, dict) and isinstance(each.get("file"), str) and _is_count(each.get("line"))
                         and isinstance(each.get("form"), str) for each in places))
    return True if well_made else None


def _one_per_place(uses):
    """`uses`, sorted, with one use for each name, file and line (the same name by `import` and by `from` counts once)."""
    kept = {}
    for each in uses:
        kept.setdefault((each.file, each.line, each.name), each)
    return [kept[key] for key in sorted(kept)]


def _parse(source, name):
    """(the tree of the file `source`, None), or (None, why) for one that cannot be read or parsed."""
    try:
        return ast.parse(source.read_bytes()), None
    except OSError:
        return None, CANNOT_READ_WHY % name
    except (SyntaxError, ValueError) as failed:
        line = getattr(failed, "lineno", None)
        return None, CANNOT_PARSE_WHY % (name, " (line %d)" % line if isinstance(line, int) else "")


def _targets(node):
    """The names that the assignment target `node` binds."""
    if isinstance(node, ast.Name):
        return [node.id]
    if isinstance(node, (ast.Tuple, ast.List)):
        return [name for each in node.elts for name in _targets(each)]
    return _targets(node.value) if isinstance(node, ast.Starred) else []


def _bound_by(statement):
    """(the names a module-level statement binds, the statements inside it that run at module level)."""
    if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return [statement.name], []
    if isinstance(statement, ast.Import):
        return [each.asname or each.name.split(".")[0] for each in statement.names], []
    if isinstance(statement, ast.ImportFrom):
        return [each.asname or each.name for each in statement.names], []
    if isinstance(statement, ast.Assign):
        return [name for target in statement.targets for name in _targets(target)], []
    if isinstance(statement, (ast.AnnAssign, ast.AugAssign)):
        return _targets(statement.target), []
    inside = [each for field in ("body", "orelse", "finalbody") for each in getattr(statement, field, [])]
    names = _targets(statement.target) if isinstance(statement, (ast.For, ast.AsyncFor)) else []
    for handler in getattr(statement, "handlers", []):
        names += [handler.name] if handler.name else []
        inside += handler.body
    for item in getattr(statement, "items", []):
        names += _targets(item.optional_vars) if item.optional_vars else []
    return names, inside


def _map_names(tree):
    """(the names the pin map binds at module level, why the map is open or None). Open: `from x import *`, or `__getattr__`."""
    names, pending = set(), list(tree.body)
    while pending:
        statement = pending.pop()
        if isinstance(statement, ast.ImportFrom) and any(each.name == "*" for each in statement.names):
            return names, "from %s import *" % ("." * statement.level + (statement.module or ""))
        bound, inside = _bound_by(statement)
        names.update(bound)
        pending += inside
    return names, "a __getattr__" if "__getattr__" in names else None


def _is_dunder(name):
    return name.startswith("__") and name.endswith("__")


def _other_bindings(tree):
    """{name: the first line that binds it other than by `import pins [as x]`} of one file's tree."""
    lines = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.arg):
            bound = [node.arg]
        elif isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load):
            bound = [node.id]
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound = [node.name]
        elif isinstance(node, ast.ExceptHandler) and node.name:
            bound = [node.name]
        elif isinstance(node, ast.Import):
            bound = [each.asname or each.name.split(".")[0] for each in node.names if each.name != PIN_MODULE]
        elif isinstance(node, ast.ImportFrom):
            bound = [each.asname or each.name for each in node.names]
        else:
            continue
        for name in bound:
            lines[name] = min(lines.get(name, node.lineno), node.lineno)
    return lines


def _imports_of(tree):
    """({(name, line, imported)} the names of `from pins import`, {(line, form)} its `*`, {alias: the line of its `import pins`})."""
    uses, places, aliases = set(), set(), {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for each in (each for each in node.names if each.name == PIN_MODULE):
                aliases[each.asname or each.name] = min(aliases.get(each.asname or each.name, node.lineno), node.lineno)
        elif isinstance(node, ast.ImportFrom) and node.module == PIN_MODULE and node.level == 0:
            places.update((node.lineno, STAR_FORM) for each in node.names if each.name == "*")
            uses.update((each.name, node.lineno, True) for each in node.names if each.name != "*" and not _is_dunder(each.name))
    return uses, places, aliases


def _guarded(tree, aliases):
    """{the names that the file asks the module about}: `hasattr(pins, "X")` and `getattr(pins, "X", default)`. The file
    guards such a name itself, so a read of it is not a missing use."""
    guards = {"hasattr": 2, "getattr": 3}
    return {node.args[1].value for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and len(node.args) == guards.get(node.func.id, 99)
            and isinstance(node.args[0], ast.Name) and node.args[0].id in aliases
            and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str)}


def _uses_in(tree):
    """({(name, line, imported)} the uses of one file, {(line, form)} the places it cannot compare)."""
    uses, places, aliases = _imports_of(tree)
    other = _other_bindings(tree)
    places.update((line, REBOUND_FORM % (alias, other[alias])) for alias, line in aliases.items() if alias in other)
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id in aliases and node.id not in other):
            continue
        parent = parents[node]
        if not (isinstance(parent, ast.Attribute) and parent.value is node and isinstance(parent.ctx, ast.Load)):
            places.add((node.lineno, VALUE_FORM))
        elif not _is_dunder(parent.attr):
            uses.add((parent.attr, node.lineno, False))
    guarded = _guarded(tree, aliases)
    return {each for each in uses if each[2] or each[0] not in guarded}, places
# --- end MVP ---
