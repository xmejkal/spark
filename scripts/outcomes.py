"""
The three outcomes, defined once.

Every script here answers in one of three ways, never two: `ok` (it looked and found nothing),
`problems` (it looked and found something), `could-not-run` (it could not look — no input, no
toolchain, a file it could not read). The third is the one this plugin is built around: a check
that could not look must never read as a check that passed, and the exit code says which it was.

The codes were spelled `EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN = 0, 1, 2` in fourteen files
and the middle word varied with the script — IMPOSSIBLE, INVALID, MISMATCH, ESCAPED,
NOTHING_TO_DO — which is fine as a local name for "ran, and the answer is no", and not fine as
fourteen places the numbers could drift apart (sprint-4 audit B17). Scripts import the codes from
here and alias the middle one to their own word.
"""

#: What the shell sees.
EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN = 0, 1, 2

#: What `--json` says, and what `check_all` aggregates. `skipped` is `check_all`'s own fourth
#: word for a check that was not asked for, which is not the same as one that could not look.
OK, PROBLEMS, COULD_NOT_RUN = "ok", "problems", "could-not-run"

#: Exit code for each status word, and back again, for the scripts that translate one into the
#: other. `EXIT_FOR` existed here with zero callers while five scripts wrote the same dictionary
#: inline and two wrote its inverse (P42).
EXIT_FOR = {OK: EXIT_OK, PROBLEMS: EXIT_PROBLEMS, COULD_NOT_RUN: EXIT_COULD_NOT_RUN}
STATUS_FOR = {code: status for status, code in EXIT_FOR.items()}


def status_of(problems=(), unchecked=()):
    """
    The three outcomes, decided once.

    This one expression was written out in six places and one of the six omitted
    `could-not-run`, so the physics check answered `ok` and exit 0 over findings that were every
    one of them "I could not look" (P34). The copies were the defect: a rule that every script
    restates is a rule every script can restate wrongly. Asking here instead makes `ok`
    unreachable while anything went unchecked, not by convention but because there is no other
    way to get the word.
    """
    return PROBLEMS if problems else (COULD_NOT_RUN if unchecked else OK)


def answer(problems=(), unchecked=(), unmeasured=()):
    """
    A check's whole result, decided here rather than declared by the check.

    Every check used to decide its own status, and two got it wrong in the same direction: a
    board that could not be read, and a finding whose own severity was `could-not-run`, both
    landed in a notes field while the status stayed `ok`.

    `unchecked` is a property of the RUN: something was asked and did not happen. `unmeasured` is
    a property of the BOARD: a real finding that needs a number nobody has taken. They were one
    field, which meant a caller could not tell "I could not look" from "look at this yourself".
    """
    problems, unchecked = list(problems), list(unchecked)
    result = {"status": status_of(problems, unchecked), "problems": problems, "unchecked": unchecked}
    if unmeasured:
        result["unmeasured"] = list(unmeasured)
    return result
