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

#: Exit code for each status word, for the scripts that translate one into the other.
EXIT_FOR = {OK: EXIT_OK, PROBLEMS: EXIT_PROBLEMS, COULD_NOT_RUN: EXIT_COULD_NOT_RUN}
