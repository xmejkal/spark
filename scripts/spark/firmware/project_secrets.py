"""
A project's secrets (P1060, #1558): the values of the files that hold the firmware's Wi-Fi passwords and tokens, which
spark masks as `***` wherever it shows the project. The rule that names such a file is `is_secret_file`: a file
directly in `firmware/` whose name, in lower case, matches `*secret*.py`, such as `wifi_secrets.py`. It asks no `git`
and looks in no nested folder, so `firmware/lib/x_secret.py` and a `config.py` are not named.

`ProjectSecrets.read` parses each file with `ast` and never imports it, so no line of it runs. It takes values only:
the right side of an assignment, typed or not, the value of a keyword argument of a call, and dict values and
list, tuple and set items, walked down. A dict key and a bare string, such as a docstring, are no values. A file
that cannot be read or parsed is named, never shown: the text of a parse error holds the line, and the line holds
the secret.
"""

import ast
import fnmatch
import warnings
from collections import namedtuple
from pathlib import Path

from spark.core.privacy import MIN_SECRET

# --- MVP ---
#: The folder of the firmware, and the name of a secrets file in it, in lower case.
FIRMWARE_FOLDER, SECRET_FILE_PATTERN = "firmware", "*secret*.py"
#: Value: one read of a project's secrets: the values, MIN_SECRET characters or more, and the names of the secrets files
#: that could not be read or parsed. What a caller does with an unreadable file is its own choice.
SecretsReading = namedtuple("SecretsReading", "values unreadable")
#: The statements whose right side is a value.
ASSIGNMENTS = (ast.Assign, ast.AnnAssign, ast.AugAssign)


def is_secret_file(name):
    """True for the name of a file that the rule names: in lower case, it matches `*secret*.py`."""
    return fnmatch.fnmatchcase(name.lower(), SECRET_FILE_PATTERN)


def strings_of(node):
    """The str constants of the value `node`: itself, or a dict's values and a list's, tuple's or set's items, walked
    down. A dict key is no value."""
    if isinstance(node, ast.Constant):
        return [node.value] if isinstance(node.value, str) else []
    if isinstance(node, ast.Dict):
        children = node.values
    elif isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        children = node.elts
    else:
        children = []
    return [text for child in children for text in strings_of(child)]


def values_of(node):
    """The value nodes of one node: the right side of an assignment, or the keyword values of a call."""
    if isinstance(node, ASSIGNMENTS) and node.value is not None:
        return [node.value]
    if isinstance(node, ast.Call):
        return [keyword.value for keyword in node.keywords]
    return []


def values_in(source):
    """The str values that the assignments and the keyword arguments of `source` hold. It raises what `ast.parse` raises.
    The parse shows no warning, as a warning can print the line it is about."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        tree = ast.parse(source)
    return [text for node in ast.walk(tree) for value in values_of(node) for text in strings_of(value)]


class ProjectSecrets:
    """Adapter: the secret values of a project's secrets files, read with `ast`. `read` never raises."""

    @staticmethod
    def files(project):
        """The files the rule names, in the order of their names."""
        folder = Path(project) / FIRMWARE_FOLDER
        if not folder.is_dir():
            return []
        return sorted((file for file in folder.iterdir() if is_secret_file(file.name) and file.is_file()), key=lambda file: file.name)

    @staticmethod
    def read(project):
        """The SecretsReading of `project`: each value of MIN_SECRET characters or more, once, and the name of each file
        that could not be read or parsed. No exception and no text of one reaches the result."""
        values, unreadable = [], []
        try:
            files = ProjectSecrets.files(project)
        except Exception:
            return SecretsReading((), (FIRMWARE_FOLDER,))
        for file in files:
            try:
                found = values_in(file.read_bytes())
            except Exception:
                unreadable.append(file.name)
                continue
            values += [text for text in found if len(text) >= MIN_SECRET]
        return SecretsReading(tuple(dict.fromkeys(values)), tuple(unreadable))
# --- end MVP ---
