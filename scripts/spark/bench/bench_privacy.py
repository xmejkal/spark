"""
The bench's Privacy (S10, P677): what a bench run may show outside spark. Each bench Operation names `privacy_for` as its
own, so `run_cli` masks its result and its Events: its paths, the store's and the home folder's, and the account tokens
of the tools lists, but the lines a person pastes (`board_codes.PASTED_CODES`, `board_envelope.PASTED_KEYS`). A new
bench Operation declares it as the six do:

    from spark.bench import bench_privacy

    class NewBenchOp(Operation):
        privacy_for = staticmethod(bench_privacy.privacy_for)

How to mark a raw place is in `spark.core.privacy`'s docstring.
"""

import os
from pathlib import Path

from spark.bench import board_codes
from spark.bench import board_envelope
from spark.records import store
from spark.records import tool_finder
from spark.core.privacy import Pasted, Privacy

# --- MVP ---

#: A token shorter than this is not masked: it would mask the same characters wherever they stand, in every line.
MIN_SECRET = 8


class AccountSecrets:
    """Adapter: the account tokens a run may hold: the value of each `account_env` the tool lists name, read from the
    environment, MIN_SECRET characters or more. A project's list that cannot be read falls back to the shared lists, and
    those to none, because the run's own tool lookup says what is wrong with them."""

    @staticmethod
    def read(project):
        entries = ()
        for layers in (project, None):
            try:
                entries = tool_finder.merged(layers)["tools"].values()
                break
            except tool_finder.ToolError:
                continue
        names = [entry.get("account_env") for entry in entries]
        return [os.environ[name] for name in names if isinstance(name, str) and len(os.environ.get(name, "")) >= MIN_SECRET]


def privacy_for(project):
    """The Privacy of a bench run on `project` (P677): its paths, the store's and the home folder's masked, the account
    tokens too, and the lines a person pastes as they are."""
    return Privacy.of(project, store.home(), Path.home(), AccountSecrets.read(project),
                      Pasted(board_codes.PASTED_CODES, board_envelope.PASTED_KEYS))
# --- end MVP ---
