"""
The reasons sourcing refuses, each a code with one sentence (P717, W6-S2): parts.py's PartError, cost.py's NoTranscript and
matching.py's UnknownMatcher, wherever they are raised.

A leaf: it imports nothing of spark. Each refusal names its code, so an agent decides on the code and never on the English
sentence (no magic strings, P260). The three errors are `errors.CodedMessageError`s, so a raise cannot leave its code out,
and every text and exit code stays byte-equal. No sourcing CLI writes a code yet: an envelope's item has no `code` key,
and the codes wait in the library for the Operation that comes later. No code is an equal literal of another leaf.
"""


# --- MVP ---
#: parts.py: a part record asked for by name, its contract, and a promotion.
NO_SUCH_PART, PART_CONTRACT_BROKEN, PROMOTION_WOULD_OVERWRITE = "no_such_part", "part_contract_broken", "promotion_would_overwrite"
#: cost.py: what a project's history and its session transcripts lack, so the cost of its steps is not known.
STEP_LINE_BROKEN, NO_STEP_MARKED, STEP_WITHOUT_SESSION = "step_line_broken", "no_step_marked", "step_without_session"
NO_TRANSCRIPT, TRANSCRIPT_UNREADABLE, TRANSCRIPT_ENDS_EARLY = "no_transcript", "transcript_unreadable", "transcript_ends_early"
#: matching.py: a matcher name.
UNKNOWN_MATCHER = "unknown_matcher"

#: Each code and the one sentence that says what it means.
CODES = {
    NO_SUCH_PART: "neither the project nor spark's library has a part record of the id asked for",
    PART_CONTRACT_BROKEN: "a part record does not meet the part contract",
    PROMOTION_WOULD_OVERWRITE: "the library already holds a record of this id, and a promotion never overwrites one",
    STEP_LINE_BROKEN: "a step line in the history has no start spark can read as a time: fix it by hand",
    NO_STEP_MARKED: "the history marks no step of the project, so there is no cost to count",
    STEP_WITHOUT_SESSION: "a step was marked in no Claude Code session, so its cost cannot be counted",
    NO_TRANSCRIPT: "no transcript of the step's session is here, so the cost of its steps is not known",
    TRANSCRIPT_UNREADABLE: "the session's transcripts cannot be opened, or name no time spark can read",
    TRANSCRIPT_ENDS_EARLY: "the session's transcripts end before one of its steps began, so its cost is not known",
    UNKNOWN_MATCHER: "the name is no matcher, or no matcher that serves this flag; the message lists the names that fit",
}
# --- end MVP ---
