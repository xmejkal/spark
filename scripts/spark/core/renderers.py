"""
The Renderers of an OperationResult's `--json` line (P657): `JsonEnvelope`, the default of `Operation.json_renderer`,
`FlatJsonLine`, which the bench scripts keep, and `FullEnvelope`, parts.py's envelope with every key (P707). `TextReport`,
the text a person reads, stays in cli.py.
"""

import json

from spark.core import outcomes


class JsonEnvelope:
    """Renderer: an OperationResult as the one envelope line a CLI prints with --json. It decides nothing again."""

    @staticmethod
    def render(result, tool, op):
        return outcomes.dumps(result.to_envelope(tool, op))

    @staticmethod
    def render_bad_argument(result, tool, op):
        """The line a bad argument gets under --json: the envelope. A Renderer that has none returns None (FlatJsonLine)."""
        return JsonEnvelope.render(result, tool, op)


class FullEnvelope:
    """Renderer: `JsonEnvelope`'s line with `notes` and `assumptions` as `[]` when the result has none, on a bad argument
    too (P707). parts.py's contract (P124): an agent reads the same eleven keys from every answer, a refusal or a crash
    included, which `run_cli` builds without notes."""

    @staticmethod
    def render(result, tool, op):
        said = result.to_envelope(tool, op)
        return outcomes.dumps(dict({"notes": [], "assumptions": []}, **said))

    @staticmethod
    def render_bad_argument(result, tool, op):
        return FullEnvelope.render(result, tool, op)


class FlatJsonLine:
    """Renderer: an OperationResult as the one flat line of JSON the bench scripts print with --json (P657): its `data` as
    `json.dumps` writes it, with no envelope, and an empty text when `data` is None, so nothing is printed. A bad argument
    gets no line of its own: the usage on stderr, as argparse prints it."""

    @staticmethod
    def render(result, tool, op):
        return "" if result.data is None else json.dumps(result.data)

    @staticmethod
    def render_bad_argument(result, tool, op):
        return None
