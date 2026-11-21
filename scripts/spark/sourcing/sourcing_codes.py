"""
The reasons sourcing refuses, each a Code with its meaning and its fix (P717, W6-S2, P935): part_records' PartError,
run_cost's NoTranscriptError and matching's UnknownMatcherError, wherever they are raised, and research's own.

A leaf: it imports nothing of spark but `spark.core.codes`. Each refusal names its code, so an agent decides on the code
and never on the English sentence (no magic strings, P260). The errors are `errors.CodedMessageError`s, so a raise cannot
leave its code out; a SparkError and `Finding.of` take the fix from the code. A variant is another Code of its parent's
word and meaning, named after it, with a fix of its own; its parent may be the core's. A control character in a value,
such as a project or a matcher name, shows as `?` (P444). No code of CODES is an equal literal of another leaf; the
variant BAD_ARGUMENT_IN_LIBRARY is the core's word.
"""

from spark.core import codes

# --- MVP ---
#: part_records: a part record asked for by name, its contract and a promotion (the JSON a write reads is the core's
#: `codes.INPUT_UNREADABLE` since P726 PR 3).
NO_SUCH_PART = codes.Code("no_such_part", "neither the project nor spark's library has a part record of the id asked for",
                    "parts.py --need <words> finds what exists; a new record starts with parts.py --skeleton")
PART_CONTRACT_BROKEN = codes.Code("part_contract_broken", "a part record does not meet the part contract",
                            "fix each problem the sentence names in the record, then run again")
#: A variant of PART_CONTRACT_BROKEN: research's fold refused a typed value; the fix is a template of the replies file, the
#: command and the replies file again.
PART_CONTRACT_BROKEN_REPLIES = codes.Code(PART_CONTRACT_BROKEN, PART_CONTRACT_BROKEN.meaning,
                                    "fix the value in %s so the record meets its contract (the typed values are kept there), then run %s --replies %s")
PROMOTION_WOULD_OVERWRITE = codes.Code("promotion_would_overwrite", "the library already holds a record of this id, and a promotion never overwrites one",
                                 "keep the record that is there, or move it away by hand first")
#: A variant of the core's BAD_ARGUMENT: research asked for a record of spark's own library (research_part).
BAD_ARGUMENT_IN_LIBRARY = codes.Code(codes.BAD_ARGUMENT, codes.BAD_ARGUMENT.meaning,
                               "spark's library is changed in spark's repository; research a copy of the record in the project's parts/")
#: run_cost: what a project's history and its session transcripts lack, so the cost of its steps is not known.
STEP_LINE_BROKEN = codes.Code("step_line_broken", "a step line in the history has no start spark can read as a time: fix it by hand",
                        "fix the step line the sentence names in the history by hand")
NO_STEP_MARKED = codes.Code("no_step_marked", "the history marks no step of the project, so there is no cost to count",
                      "mark each step with parts.py --step <project> <step> in a Claude Code session")
STEP_WITHOUT_SESSION = codes.Code("step_without_session", "a step was marked in no Claude Code session, so its cost cannot be counted",
                            "mark the step again with parts.py --step <project> <step> in a Claude Code session")
NO_TRANSCRIPT = codes.Code("no_transcript", "no transcript of the step's session is here, so the cost of its steps is not known",
                     "count the cost on the machine that ran the session")
TRANSCRIPT_UNREADABLE = codes.Code("transcript_unreadable", "the session's transcripts cannot be opened, or name no time spark can read",
                             "make the session's transcripts readable, then count again")
TRANSCRIPT_ENDS_EARLY = codes.Code("transcript_ends_early", "the session's transcripts end before one of its steps began, so its cost is not known",
                             "count again once the session has run past the step's start")
#: matching: a matcher name.
UNKNOWN_MATCHER = codes.Code("unknown_matcher", "the name is no matcher, or none that serves this flag; the message lists the names that fit",
                       "give one of the names the sentence lists")
#: research: what the DFRobot wiki source needs and did not find (P737).
NO_SKU = codes.Code("no_sku", "a DFRobot record names no sku, so its wiki page has no address",
              "write the maker's part number as the record's sku (parts.py --skeleton --sku, or by hand), then run again")
NO_DOCUMENT_LIST = codes.Code("no_document_list", "the wiki page holds no document list spark can read (its JSON-LD block), so no document was kept from it",
                        "keep the page's documents by hand: parts.py --fetch after their URLs are in the record's sources")
MORE_DOCUMENTS = codes.Code("more_documents", "the wiki page lists more files than one run takes (twelve); the message names the rest",
                      NO_DOCUMENT_LIST.fix)
#: find_documents: what a board's maker's page did not give (P952). Each fix is the next way to a top view or a drawing.
NO_VENDOR_FINDER = codes.Code("no_vendor_finder", "no finder knows the board's maker: its vendor and its sources name no page spark can read",
                        "take a photo of the board's component side (/spark:identify), then measure it with parts.py --features-set")
NO_TOP_VIEW = codes.Code("no_top_view", "the maker's page has no picture in its \"Board Overview\" section, so no top view was kept",
                   NO_VENDOR_FINDER.fix)
NO_DIMENSION_DRAWING = codes.Code("no_dimension_drawing", "the maker's page lists no document named \"Dimension\" on dfrobot.com, so no dimension drawing was kept",
                            "keep a dimension drawing from another page of the maker with parts.py --keep FILE --url URL")

#: Each code and the one sentence that says what it means.
CODES = {code: code.meaning for code in (
    NO_SUCH_PART, PART_CONTRACT_BROKEN, PROMOTION_WOULD_OVERWRITE, STEP_LINE_BROKEN, NO_STEP_MARKED, STEP_WITHOUT_SESSION,
    NO_TRANSCRIPT, TRANSCRIPT_UNREADABLE, TRANSCRIPT_ENDS_EARLY, UNKNOWN_MATCHER, NO_SKU, NO_DOCUMENT_LIST, MORE_DOCUMENTS,
    NO_VENDOR_FINDER, NO_TOP_VIEW, NO_DIMENSION_DRAWING)}
# --- end MVP ---
