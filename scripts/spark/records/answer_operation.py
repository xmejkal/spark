"""
The base of an Operation that answers as a parts.py handler does (P726): `run` is the skeleton and `build_answer` the step a
subclass fills with the handler's body (a Template Method). It keeps `parts.main`'s rules for every handler on the core: a
write holds the store's lock from its plan to its last byte, a file the disk would not give or that is not JSON and a
coded refusal are could-not-run items, never a traceback, and the Answer becomes the core's result through
`Answer.to_result`. The design area's six goal Operations are its first subclasses; the sourcing area's follow.
"""

import contextlib
import json
from pathlib import Path

from spark.core.errors import CodedMessageError, SparkError
from spark.core.operation import READS, WRITES, Operation
from spark.core.renderers import FullEnvelope
from spark.records import records_codes, store
from spark.records.record_kind import Answer, _cannot

# --- MVP ---
#: The fix of a negative --from, for every listing on the core.
START_FIX = "--from takes a whole number from 0 up"
#: The sentence of a negative --from.
START_SENTENCE = "--from %d: a listing cannot start before its first item"


class AnswerOperation(Operation):
    """
    Operation: a parts.py handler on the core. A subclass gives `name`, `arguments`, `effects` and `build_answer(**values)`,
    the handler's body, which returns an `Answer`. `run` resolves a `project` that is a Path (a str project is a
    selector's text and stays as typed), holds `store.locked()` around a write (the dry run included, as `parts.main`
    did), turns an OSError or a JSON error into a could-not-run item with `records_codes.FILE_UNREADABLE` and a
    `CodedMessageError` into one with its own code, and returns `answer.to_result()`. A SparkError passes through to
    `run_operation`, which answers it as every Operation's.
    """

    effects = (READS,)
    json_renderer = FullEnvelope

    def run(self, *, outside, **values):
        if isinstance(values.get("project"), Path):
            values["project"] = values["project"].resolve()
        try:
            with store.locked() if WRITES in self.effects else contextlib.nullcontext():
                answer = self.build_answer(**values)
        except SparkError:
            raise
        except (OSError, json.JSONDecodeError) as unreadable:
            answer = Answer(unchecked=[_cannot("--%s: %s" % (self.name, unreadable), code=records_codes.FILE_UNREADABLE)])
        except CodedMessageError as broken:  # a store's refusal, an unreadable input: could-not-run, never a traceback
            answer = Answer(unchecked=[_cannot(str(broken), code=broken.code)])
        return answer.to_result()

    def build_answer(self, **values):
        raise NotImplementedError
# --- end MVP ---
