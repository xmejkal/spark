"""
The Operation (P442, W3-3): one job, with one public method, `run`. A CLI, an agent or an MCP tool calls it through
`spark.core.cli`, which parses its `arguments` and renders its result. The Operation itself parses and prints nothing.
"""

from collections import namedtuple
from pathlib import Path

from spark.core.renderers import JsonEnvelope
from spark.core.replies import REPLIES_FILE
from spark.core.result import output_schema

# --- MVP ---
#: Value: one argument of an Operation, as argparse adds it. `flags` are its option strings, `dest` the keyword `run`
#: takes, `kind` the type of the value (`Path`, `str`) or `bool` for a flag that is on when given, `group` the name of
#: the group whose arguments exclude each other, or None, `required` whether the person must give it, `choices` the
#: values it may take, or None, `nargs` argparse's count of values (`"+"`, `"*"` or an int; None for one value, P726),
#: `metavar` the word `--help` shows for the value (`PROJECT`), or None for argparse's, `repeats` whether the flag may
#: be given more than once, each value kept in a list (`--label a=x --label b=y`; argparse's `append`, P726 PR 2), and
#: `payload` the index of the token that names a JSON file the frontend reads for the Operation (0 for a one-value flag,
#: 1 for `--function-set PART FILE`; None for none): the CLI reads the file, or stdin for `-`, and hands the Operation the
#: parsed value (`cli.load_payloads`), an MCP frontend hands it the object (P726 PR 3).
Argument = namedtuple("Argument", "flags dest kind help default group required choices nargs metavar repeats payload",
                      defaults=(None, None, False, None, None, None, False, None))

#: What an Operation does outside spark: it reads the project's files, runs a program, touches the board, erases what is
#: on it, writes to it, asks the person for a yes, fetches a URL. They are the words of a step's `effects` (`outcomes.step`); DELETES and
#: WRITES came with deploy (P655), ASKS with grant (P657), FETCHES with research (P737): `build_outside_world` gives `make_consent`,
#: `replies` and `fetch` only to an Operation that declares the effect.
READS, RUNS, BOARD, DELETES, WRITES, ASKS, FETCHES = "reads", "runs", "board", "deletes", "writes", "asks", "fetches"
#: The flag that asks for the envelope. `run_cli` reads it, and the Operation never sees it.
JSON_FLAG, JSON_DEST = "--json", "json"
#: The arguments every Operation on a project takes, by `dest`, with the words of the first Operation, look.py. An
#: Operation that says one differently `_replace`s its `help`.
COMMON_ARGUMENTS = {
    "project": Argument(("--project",), "project", Path, "the project folder with requirements.json and sim/ (default: here)", Path(".")),
    "port": Argument(("--port",), "port", str, "the board's serial port, e.g. /dev/cu.usbmodem1101. Needed with two or more boards on USB "
                     "(one board on two nodes named by its serial counts once)"),
    JSON_DEST: Argument((JSON_FLAG,), JSON_DEST, bool, "print one envelope on stdout (docs/guide/agents/json.md)"),
    "replies": Argument(("--replies",), "replies", Path, "the replies file a run that left questions open wrote (%s): its filled values "
                        "answer them (P737)" % REPLIES_FILE),
}


#: The JSON Schema `type` of each Argument kind (P605). A kind enters with its first Operation.
JSON_TYPE_OF_KIND = {Path: "string", str: "string", bool: "boolean", int: "integer"}
#: The JSON Schema of a payload token: the parsed JSON, an object or a list (P726 PR 3).
PAYLOAD_SCHEMA = {"type": ["object", "array"]}


def _argument_schema(argument):
    """One Argument as a JSON Schema property: its type (an array of it when `nargs` takes several values or the flag
    `repeats`), its help, its `enum` when it has choices, and its default when it has one (a flag's is False)."""
    default = False if argument.kind is bool else argument.default
    kind = {"type": JSON_TYPE_OF_KIND[argument.kind]}
    if argument.payload is not None and argument.nargs is None:
        kind = dict(PAYLOAD_SCHEMA)
    said = dict({"type": "array", "items": kind} if argument.nargs is not None or argument.repeats else kind, description=argument.help)
    if argument.payload is not None and isinstance(argument.nargs, int):  # the payload token among the others (JSON Schema 2020-12)
        said = dict(said, prefixItems=[dict(PAYLOAD_SCHEMA) if i == argument.payload else dict(kind) for i in range(argument.nargs)])
    said.update({"enum": list(argument.choices)} if argument.choices else {})
    return said if default is None else dict(said, default=str(default) if isinstance(default, Path) else default)


class Operation:
    """
    Operation: one job, with one public method, `run`. A subclass gives `name` (the `op` the envelope prints), `arguments`
    (its Arguments, in the order the usage lists them) and `effects` (READS, RUNS, BOARD: what `build_outside_world` lets
    it reach). `run` takes each argument's `dest` as a keyword, except `json`, which is the frontend's, and `outside`, an
    OutsideWorld, and returns an OperationResult. It raises SparkError to answer with one Finding; anything else is a crash.
    """

    name = None
    #: The one sentence a catalogue or an MCP tool description prints (P726 PR 3); None takes the help of the Argument whose
    #: flag is `--<name>`, which every parts.py Operation has.
    summary = None
    arguments = ()
    effects = ()
    #: The Renderer of the `--json` line: `JsonEnvelope`, or a class with `render` and `render_bad_argument`, such as
    #: `renderers.FlatJsonLine`. A class attribute, not a flag (P657).
    json_renderer = JsonEnvelope
    #: `privacy_for(project)` gives the Privacy of a run on `project` (P677), or None: the run passes everything through.
    privacy_for = None

    def run(self, *, outside, **values):
        raise NotImplementedError

    def effects_of(self, values):
        """The effects of a run with these `values` (the keywords `run` takes): `effects`, unless a flag narrows them, as
        deploy's `--dry-run` does (P655). `run_operation` builds the outside from this, so every frontend declares the same."""
        return self.effects

    def input_schema(self):
        """The JSON Schema of `run`'s values, an MCP tool's `inputSchema` (P605): a property per Argument but `json`,
        which is the frontend's, and `required` lists the dests the person must give (left out when none, as draft 4 asks). A
        group of arguments that exclude each other is not in it yet."""
        shown = [argument for argument in self.arguments if argument.dest != JSON_DEST]
        schema = {"type": "object", "properties": {argument.dest: _argument_schema(argument) for argument in shown},
                  "additionalProperties": False}
        required = [argument.dest for argument in shown if argument.required]
        return dict(schema, required=required) if required else schema

    def output_schema(self):
        """The JSON Schema of the envelope, an MCP tool's `outputSchema` (P605): the same for every Operation."""
        return output_schema()
# --- end MVP ---
