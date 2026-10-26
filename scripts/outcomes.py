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

import json

#: What the shell sees.
EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN = 0, 1, 2

#: What `--json` says, and what `check_all` aggregates. `skipped` is `check_all`'s own fourth
#: word for a check that was not asked for, which is not the same as one that could not look.
OK, PROBLEMS, COULD_NOT_RUN = "ok", "problems", "could-not-run"
#: A check that was not asked for (check_all), or a stage that does not apply to the design (check_spine, P236: the
#: board alone). Never ok, and never could-not-run.
SKIPPED = "skipped"

# --- MVP ---
#: The states of a reader's Value, and the sentence that says one of them aloud (P428, OC4). The rule for a reader:
#:
#: A reader of one thing that may be absent (a deploy record, a log's step counts) never raises. It returns a Value whose
#: `state` is one of these three. RECORDED: it read the thing, and the Value's own fields hold it ("recorded" for the
#: step counts of scenario text means "read", in one clause). NONE_RECORDED: it looked and the thing is not there, and
#: `why` is None. NOT_CHECKED: it could not look, `why` is one sentence that says what stopped it, and the Value's own
#: fields are empty. A NOT_CHECKED goes into an envelope's `unchecked` list, never to `ok`, and its person text is
#: NOT_CHECKED_MESSAGE % why. The state is lossy through a log: ScenarioSteps.line() prints "not read" for both
#: NONE_RECORDED and NOT_CHECKED, and from_log reads NOT_CHECKED back. A loader of a required thing (design.load,
#: boards.load) raises its Error: that is a refusal, not a reading, and is no reader in this rule. Three phrasings stay
#: outside the template because each names its thing first: "last deploy not checked: %s" (board_look.py,
#: board_envelope.py) and "spark did not read its record of this board: %s" (LastDeploy.in_question). Readers that
#: still wait: boards.read_simulated_part (P397), breadboard_keep.EarlierDiagram.read and
#: breadboard_changes.WiringRecord.read (wave 6); sim_project.firmware_in, which returns whatever the JSON parses to and
#: None for both a missing and an unreadable file (P429); project_image.read_run_logs and firmware_platform.record_of refuse by
#: design. The rule is tested by READERS in tests/test_outcomes.py, one row per reader that follows it.
RECORDED, NONE_RECORDED, NOT_CHECKED = "recorded", "none-recorded", "not-checked"
NOT_CHECKED_MESSAGE = "not checked: %s"
# --- end MVP ---

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


def envelope(tool, op, data=None, problems=(), unchecked=(), next_steps=(), truncated=None, notes=None, assumptions=None):
    """
    The one shape every `--json` run prints (§6.4.1 of docs/2026-10-04-store-design.md), so an agent reads
    `status` and `data` without knowing which command ran. `problems` are {"subject", "sentence", "fix"},
    `unchecked` {"sentence", "fix"}, `next` are `step()`s, `truncated` is {"shown", "total", "next"} or None.
    The status is `status_of`'s, never declared: `ok` stays unreachable while anything went unchecked.
    `notes` (said, never failing) and `assumptions` (what the answer rests on that nobody has checked) are keys only for a
    tool that passes them, and change no status (P124, #58: their names are the next envelope's).
    """
    problems, unchecked = list(problems), list(unchecked)
    said = {"envelope": 1, "tool": tool, "op": op, "status": status_of(problems, unchecked), "data": data,
            "problems": problems, "unchecked": unchecked, "next": list(next_steps), "truncated": truncated}
    said.update({key: list(value) for key, value in (("notes", notes), ("assumptions", assumptions)) if value is not None})
    return said


def step(op, argv, why, effects=(), needs_yes=False):
    """A step an agent may take next (§6.4.2): ids only in `argv` — a label or a reason travels in a file."""
    return {"op": op, "argv": list(argv), "why": why, "effects": list(effects), "needs_yes": needs_yes}


def page(items, start, op, argv, limit=20, budget=3400):
    """
    At most `limit` items and about `budget` bytes of them from `start` (§6.4.4: an agent's answer stays under
    4 KB by default), and the `truncated` note that says how to ask for the rest — None when all were shown.
    Measured as ASCII-escaped JSON, which is never shorter than the UTF-8 the envelope prints.
    """
    shown, size = [], 0
    for item in items[start:start + limit]:
        size += len(json.dumps(item))
        if shown and size > budget:
            break
        shown.append(item)
    end = start + len(shown)
    if start == 0 and end == len(items):
        return shown, None
    following = (step(op, list(argv) + ["--from", str(end), "--json"], "the next of %d" % len(items))
                 if end < len(items) else None)
    return shown, {"shown": len(shown), "total": len(items), "next": following}
