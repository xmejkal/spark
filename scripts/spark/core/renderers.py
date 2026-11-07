"""
The Renderers of an OperationResult's `--json` line (P657): `JsonEnvelope`, the default of `Operation.json_renderer`, and
`FlatJsonLine`, which the bench scripts keep. `TextReport`, the text a person reads, stays in cli.py.
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
