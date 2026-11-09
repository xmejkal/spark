"""
The reasons sourcing refuses, each a code with one sentence (P717, W6-S2): part_records' PartError, parts.py's
unreadable input, run_cost's NoTranscript and matching's UnknownMatcher, wherever they are raised.

A leaf: it imports nothing of spark. Each refusal names its code, so an agent decides on the code and never on the
English sentence (no magic strings, P260). The errors are `errors.CodedMessageError`s, so a raise cannot leave its code
out. Exit codes and the text of printable values stay as they were; a control character in a value, such as a project
or a matcher name, now shows as `?` (P444). No sourcing CLI writes a code yet: an envelope's item has no `code` key, and
the codes wait in the library for the Operation that comes later. No code is an equal literal of another leaf.
"""


# --- MVP ---
#: part_records: a part record asked for by name, its contract, a promotion, and the JSON a write reads.
NO_SUCH_PART, PART_CONTRACT_BROKEN = "no_such_part", "part_contract_broken"
PROMOTION_WOULD_OVERWRITE, INPUT_UNREADABLE = "promotion_would_overwrite", "input_unreadable"
#: run_cost: what a project's history and its session transcripts lack, so the cost of its steps is not known.
STEP_LINE_BROKEN, NO_STEP_MARKED, STEP_WITHOUT_SESSION = "step_line_broken", "no_step_marked", "step_without_session"
NO_TRANSCRIPT, TRANSCRIPT_UNREADABLE = "no_transcript", "transcript_unreadable"
TRANSCRIPT_ENDS_EARLY = "transcript_ends_early"
#: matching: a matcher name.
UNKNOWN_MATCHER = "unknown_matcher"

#: Each code and the one sentence that says what it means.
CODES = {
    NO_SUCH_PART: "neither the project nor spark's library has a part record of the id asked for",
    PART_CONTRACT_BROKEN: "a part record does not meet the part contract",
    PROMOTION_WOULD_OVERWRITE: "the library already holds a record of this id, and a promotion never overwrites one",
    INPUT_UNREADABLE: "the JSON a write reads, from a file or from stdin, cannot be read or is not JSON",
    STEP_LINE_BROKEN: "a step line in the history has no start spark can read as a time: fix it by hand",
    NO_STEP_MARKED: "the history marks no step of the project, so there is no cost to count",
    STEP_WITHOUT_SESSION: "a step was marked in no Claude Code session, so its cost cannot be counted",
    NO_TRANSCRIPT: "no transcript of the step's session is here, so the cost of its steps is not known",
    TRANSCRIPT_UNREADABLE: "the session's transcripts cannot be opened, or name no time spark can read",
    TRANSCRIPT_ENDS_EARLY: "the session's transcripts end before one of its steps began, so its cost is not known",
    UNKNOWN_MATCHER: "the name is no matcher, or none that serves this flag; the message lists the names that fit",
}
# --- end MVP ---
