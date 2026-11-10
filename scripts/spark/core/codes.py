"""
The codes the core writes in an envelope item for every Operation (P442, W3-3). A leaf: it imports nothing. An area's
own codes stay in its table (`spark/bench/board_codes.py` for the bench); these are the ones `run_operation` and
`run_cli` give whatever the Operation. `CODES` says each in one sentence, as `board_codes.CODES` does, and
`docs/guide/agents/json.md` names each.
"""

# --- MVP ---
#: An argument the Operation cannot run with: `run_cli` answers it for every Operation (it was board_codes.BAD_ARGUMENT).
BAD_ARGUMENT = "bad_argument"
#: The Operation raised an exception it did not turn into a Finding: a defect in spark, never in the project.
CRASH = "crash"
#: The Operation reached an outside its `effects` do not declare (it ran a program without `runs`): a defect in spark.
UNDECLARED_EFFECT = "undeclared_effect"
#: A question the Operation could not answer itself and nobody answered yet (P737): the run is unchecked until a reply comes.
NEEDS_REPLY = "needs_reply"
#: A reply to a key that no open question has, or to a fact the record already holds (P737).
UNKNOWN_REPLY = "unknown_reply"
#: A reply whose value does not fit its question's kind: not a yes or no, not one of the choices, empty, or not a finite number (P737).
BAD_REPLY = "bad_reply"

#: Each code and the one sentence that says what it means.
CODES = {
    BAD_ARGUMENT: "an argument that the script cannot run with",
    CRASH: "the operation crashed, a defect in spark: the traceback is on stderr",
    UNDECLARED_EFFECT: "the operation reached an outside that its effects do not declare, a defect in spark",
    NEEDS_REPLY: "a question nobody answered yet: run again with --replies once the file is filled",
    UNKNOWN_REPLY: "a reply to a key that no open question has, or to a fact already filled",
    BAD_REPLY: "a reply whose value does not fit its question's kind",
}
# --- end MVP ---
