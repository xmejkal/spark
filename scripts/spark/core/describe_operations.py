"""
`--describe` as an Operation (P726 PR 3): what a CLI with several Operations offers, read off the Operation classes
themselves (reflection over the core contract), so what an agent reads cannot drift from what runs (§6.4.3). The registry is
given to the constructor (op name -> class, in the order the CLI lists them); `describe_operations` is not an area's table.
parts.py gives its slice of the Operation catalogue (`operation_catalogue.CATALOGUE`, P1077). The core never imports it,
because it imports the areas. `flag` is the Operation's own `--<op>` argument, or None: piece 7 gives each frontend's own,
`dry_run` says whether a run of the Operation can write nothing (a `dry_run` argument, or an `apply` one: P1124), and
`apply` whether it writes only when `--apply` is given.
"""

from spark.core import outcomes
from spark.core.operation import COMMON_ARGUMENTS, DELETES, FETCHES, JSON_DEST, READS, WRITES, Argument, Operation
from spark.core.renderers import FullEnvelope
from spark.core.result import OperationResult

# --- MVP ---
#: The words `--describe` prints for the effects, in this order: parts.py's older word `network` for FETCHES (the agents' pages
#: and the permission rules read it, §6.4.5), and `reads` is not printed, because every Operation reads.
EFFECT_WORDS = ((FETCHES, "network"), (WRITES, "writes"), (DELETES, "deletes"))
#: One text line per Operation: the flag, the summary, the effects when it has any.
OPERATION_LINE = "  %-18s %s%s"
#: The dest of the Argument that makes an Operation's run a dry run: `dry_run` says whether the Operation has one (P1077).
DRY_RUN_DEST = "dry_run"
#: The dest of the Argument without which an Operation writes nothing (P1124, the plan-first shape): it plans, then writes
#: with `--apply` after the person's yes. `apply` says whether the Operation has one, and such a run is a dry run too.
APPLY_DEST = "apply"


def summary_of(operation):
    """The one sentence of an Operation class: the help of the Argument whose flag is `--<name>`, else its `summary`."""
    flag = "--" + operation.name
    return next((argument.help for argument in operation.arguments if flag in argument.flags), None) or operation.summary


def effect_words_of(operation):
    """The printed effect words of an Operation class, in `EFFECT_WORDS` order."""
    return [word for effect, word in EFFECT_WORDS if effect in operation.effects]


def options_of(registry):
    """The options the Operations of `registry` share: every Argument that is not an Operation's own flag, by its first flag,
    with its help, each once in first-seen order (`--json` included)."""
    options = {}
    for op, cls in registry.items():
        for argument in cls.arguments:
            if "--" + op not in argument.flags:
                options.setdefault(argument.flags[0], argument.help)
    return options


class DescribeOperations(Operation):
    """
    Operation: every Operation of a CLI, its flag, summary, effects, the JSON Schema of its values (`arguments`, with
    `metavar` and `nargs` kept where an Argument has them, the Operation's own flag left out) and the keys of its answer
    (`data`, from `Operation.data_keys`), the options the Operations share (`options`, `options_of`) and the exit codes
    (`exits`); the text is one line per Operation.
    """

    name = "describe"
    data_keys = ('operations', 'options', 'exits')
    arguments = (Argument(("--describe",), "describe", bool, "every operation, its arguments, effects and output — this list"),
                 COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS,)
    json_renderer = FullEnvelope

    def __init__(self, registry):
        self.registry = registry

    def run(self, *, outside, describe=True):
        operations = []
        for op, cls in self.registry.items():
            properties = (self if cls is type(self) else cls()).input_schema()["properties"]
            for argument in cls.arguments:
                if "--" + op in argument.flags and argument.kind is bool:
                    properties.pop(argument.dest, None)  # the Operation's own flag says nothing to a caller that chose it
                elif argument.dest in properties:
                    properties[argument.dest].update({key: value for key, value in (("metavar", argument.metavar), ("nargs", argument.nargs)) if value is not None})
            words = effect_words_of(cls)
            own = any("--" + op in argument.flags for argument in cls.arguments)
            operations.append({"op": op, "flag": ("--" + op) if own else None, "summary": summary_of(cls), "effects": words,
                               "dry_run": any(argument.dest in (DRY_RUN_DEST, APPLY_DEST) for argument in cls.arguments),
                               "apply": any(argument.dest == APPLY_DEST for argument in cls.arguments),
                               "arguments": properties, "data": list(cls.data_keys)})
        exits = {str(code): status for status, code in outcomes.EXIT_FOR.items()}
        lines = [OPERATION_LINE % (one["flag"] or one["op"], one["summary"], "  [%s]" % ", ".join(one["effects"]) if one["effects"] else "") for one in operations]
        return OperationResult({"operations": operations, "options": [{"flag": flag, "summary": help} for flag, help in options_of(self.registry).items()],
                                "exits": exits}, lines=lines)
# --- end MVP ---
