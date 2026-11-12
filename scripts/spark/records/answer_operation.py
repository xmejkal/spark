"""
The base of an Operation that answers as a parts.py handler does (P726): `run` is the skeleton and `build_answer` the step a
subclass fills with the handler's body (a Template Method). It keeps `parts.main`'s rules for every handler on the core: a
write holds the store's lock from its plan to its last byte, a file the disk refused (a read or a write) or that is not JSON and a
coded refusal are could-not-run items, never a traceback, a listing's negative `--from` is refused before the body runs,
and the Answer becomes the core's result through `Answer.to_result`. `ANSWER_ARGUMENTS` holds the option Arguments the
Operations share. The design area's six goal Operations were its first subclasses (PR 1); the sourcing area's fifteen
follow on `sourcing.part_operation.PartOperation` (PR 2), which fills the `answer_refusal` hook.
"""

import contextlib
import json
from pathlib import Path

from spark.core import codes
from spark.core.errors import CodedMessageError, SparkError
from spark.core.operation import READS, WRITES, Argument, Operation
from spark.core.renderers import FullEnvelope
from spark.records import records_codes, store
from spark.records.record_kind import Answer, _cannot

# --- MVP ---
#: The fix of a negative --from, for every listing on the core.
START_FIX = "--from takes a whole number from 0 up"
#: The sentence of a negative --from.
START_SENTENCE = "--from %d: a listing cannot start before its first item"
#: The help of the options the Operations on the core share, worded as parts.py's OPTIONS rows (parts.py reads them here).
PROJECT_HELP = "a project whose own parts/ beats the shipped library"
START_HELP = "with a listing: start at item N (truncated.next says where)"
DRY_RUN_HELP = "with an operation that has an effect: say what it would do, and do nothing"
#: The option Arguments the Operations on the core share, by `dest`, as the core's `COMMON_ARGUMENTS`: a project whose
#: parts/ come first (None: the library alone), a listing's start and a write's dry run.
ANSWER_ARGUMENTS = {
    "project": Argument(("--project",), "project", Path, PROJECT_HELP),
    "start": Argument(("--from",), "start", int, START_HELP, 0, metavar="N"),
    "dry_run": Argument(("--dry-run",), "dry_run", bool, DRY_RUN_HELP),
}


class AnswerOperation(Operation):
    """
    Operation: a parts.py handler on the core. A subclass gives `name`, `arguments`, `effects` and `build_answer(**values)`,
    the handler's body, which returns an `Answer`. `run` resolves a `project` that is a Path (a str project is a
    selector's text and stays as typed), holds `store.locked()` around a write (the dry run included, as `parts.main`
    did), refuses a negative `start` (the `--from` of a listing, by its dest) before the body runs, turns an OSError or a
    JSON error into a could-not-run item with `records_codes.FILE_REFUSED` and a `CodedMessageError` into
    `answer_refusal`'s Answer (a could-not-run item with the error's code, unless a subclass answers it otherwise), and
    returns `answer.to_result()`. A SparkError passes through to `run_operation`, which answers it as every Operation's.
    The first Argument of a subclass is its flag: the one `parts.py` routes by, and the subject of a refusal about it.
    """

    effects = (READS,)
    json_renderer = FullEnvelope

    def run(self, *, outside, **values):
        if isinstance(values.get("project"), Path):
            values["project"] = values["project"].resolve()
        start = values.get("start")
        if start is not None and start < 0:
            return Answer(unchecked=[_cannot(START_SENTENCE % start, START_FIX, code=codes.BAD_ARGUMENT)]).to_result()
        try:
            with store.locked() if WRITES in self.effects else contextlib.nullcontext():
                answer = self.build_answer(**values)
        except SparkError:
            raise
        except (OSError, json.JSONDecodeError) as unreadable:
            answer = Answer(unchecked=[_cannot("--%s: %s" % (self.name, unreadable), code=records_codes.FILE_REFUSED)])
        except CodedMessageError as broken:  # a store's refusal, an unreadable input: could-not-run, never a traceback
            answer = self.answer_refusal(broken, values)
        return answer.to_result()

    def build_answer(self, **values):
        raise NotImplementedError

    def answer_refusal(self, broken, values):
        """The Answer of a coded refusal `build_answer` raised, given the run's `values`: a could-not-run item with the
        error's code. A subclass answers a class of its own differently (sourcing's `PartError` is a problem on the part)."""
        return Answer(unchecked=[_cannot(str(broken), code=broken.code)])
# --- end MVP ---
