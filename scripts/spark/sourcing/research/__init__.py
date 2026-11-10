"""
The research area (P737): `ResearchPart` runs ordered, swappable `ResearchSource`s over one part record, and
`research.py` is its CLI. `build_research_outside_world` is that CLI's outside builder: the frontend picks the
ReplyStrategy from `--replies` and hands the store's `fetch` over, so the Operation never builds its own and
`outside.replies` and `outside.fetch` stay the slots a Fake or, in step R2, a terminal fills.
"""

from spark.core.errors import SparkError
from spark.core.events import Event
from spark.core.outside import build_outside_world
from spark.core.replies import DeferringReplyStrategy, GivenReplyStrategy, RepliesStore
from spark.records import store

#: The code of a research run's Events, and the line a refusal says before it is raised (the bench's pattern: a text run
#: reads it on stdout, a --json run on stderr), because a raised SparkError prints no line of its own.
PHASE, REFUSED_LINE = "research", "%s: %s. %s"


# --- MVP ---
def reply_strategy_for(path):
    """The replies given ahead in the file at `path`, or, with no file named, nothing answered now."""
    return GivenReplyStrategy(RepliesStore(path).load()) if path else DeferringReplyStrategy()


def build_research_outside_world(project, effects, reporter, values):
    """Core's OutsideWorld for a research run: `replies` answers from the `--replies` file in `values`, and `fetch` is the
    store's one door to the network (`store.fetch`, P737 step 5), given only when the effects hold FETCHES. A replies file
    that cannot be read is `RepliesStore.load`'s SparkError `bad_argument`, said once through the Reporter (a text run reads
    it) and then raised, which `run_operation` answers as one Finding."""
    try:
        strategy = reply_strategy_for(values.get("replies"))
    except SparkError as refused:
        reporter.report(Event.line(PHASE, REFUSED_LINE % (refused.code, str(refused), refused.fix)))
        raise
    return build_outside_world(effects, reporter, replies=strategy, fetch=store.fetch)
# --- end MVP ---
