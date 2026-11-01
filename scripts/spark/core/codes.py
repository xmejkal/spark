"""
The codes the core writes in an envelope item for every Operation (P442, W3-3). A leaf: it imports nothing. An area's own
codes stay in its table (`board_codes.py` for the bench); these are the ones `run_operation` and `run_cli` give whatever
the Operation. `CODES` says each in one sentence, as `board_codes.CODES` does, and `docs/guide/agents/json.md` names each.
"""

# --- MVP ---
#: An argument the Operation cannot run with: `run_cli` answers it for every Operation (it was board_codes.BAD_ARGUMENT).
BAD_ARGUMENT = "bad_argument"
#: The Operation raised an exception it did not turn into a Finding: a defect in spark, never in the project.
CRASH = "crash"
#: The Operation reached an outside its `effects` do not declare (it ran a program without `runs`): a defect in spark.
UNDECLARED_EFFECT = "undeclared_effect"

#: Each code and the one sentence that says what it means.
CODES = {
    BAD_ARGUMENT: "an argument that the script cannot run with",
    CRASH: "the operation crashed, a defect in spark: the traceback is on stderr",
    UNDECLARED_EFFECT: "the operation reached an outside that its effects do not declare, a defect in spark",
}
# --- end MVP ---
