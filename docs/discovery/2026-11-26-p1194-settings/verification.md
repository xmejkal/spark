# Verification
<!-- One line per ★ claim in brief.md; rejected claims stay. refuter: holds · partly · refuted · could not open, with
the line it read, verbatim. result: reproduced · not reproduced · rejected. keep: the words any summary of the claim
must carry (phrases separated by ;), or none; keep comes last on the line.
e.g. `- ★C3 · STATUS.md:84 · refuter: partly — "Shown on the C6, assumed for the S3" · reproduced how: re-read STATUS.md:84 · result: reproduced · keep: assumed for the S3` -->
- ★C1 · tool_finder.py:92 and brief_choices.py:19 · refuter: partly — "The three layers as one list: tools merged field by field, roles key by key, the project winning." · reproduced how: the refuter's read; brief_choices.py:19 not re-run by the facilitator · result: reproduced (by the refuter); claim narrowed · keep: none
- ★C2 · council/po-assistant.md:10, #536, #470 · refuter: holds — "PO-1 · Nobody is blocked without the seam today." · reproduced how: the facilitator read PO-1 · result: reproduced · keep: none
- ★C3 · the count of `sellers` in `.spark/project.json` · refuter: partly — 24 files, `sellers` in 3 · reproduced how: the facilitator's own count, 2026-11-26: 3 of 24 · result: reproduced; claim narrowed · keep: none
- ★C4 · brief.py:25-29, project_setup.py:357 · refuter: partly — "A non-empty list of strings as a lower-cased tuple, else None." · reproduced how: the facilitator read project_setup.py:357-358 · result: reproduced; caveat added · keep: none
- ★C5 · the refuter's scratch project; scenario_run.py:273-274 · refuter: holds — `tool_finder.find('simulator', 'proj')` printed `Tool(name='my-sim', ...)` · reproduced how: the facilitator read tool_finder.py:296-302 and scenario_run.py:270-276 · result: reproduced; caveat added · keep: none
- ★C6 · tool_finder.py:359-362 · refuter: partly — `if entry.get("needs_account") and not os.environ.get(...)` · reproduced how: the refuter's read · result: reproduced (by the refuter); claim narrowed · keep: none
- ★C7 · #1740, tools.py:34,57 · refuter: refuted as written — #1740 "Done when": "at least global, user and project" · reproduced how: the facilitator read #1740's body, lines 7, 13 and 17 · result: rejected as first written; rewritten · keep: none
- ★C8 · scripts/tools.py:10, commands/setup.md:79 · refuter: holds — "A choice is written to the person's file, or to the project's with --project" · reproduced how: the refuter's read · result: reproduced (by the refuter) · keep: none
- ★C9 · project_setup.py:357-358, tools.py --help · refuter: refuted in part — `"prefer": ("a list of texts", texts)` · reproduced how: the facilitator read project_setup.py:357-358 and tools.py --help · result: rejected as first written; rewritten · keep: none
- ★C10 · run_request.py:4-5, 44 · refuter: holds — "The values of the step come from spark's own offer key, never from the request." · reproduced how: the refuter's read; pointer moved to 42-44 · result: reproduced (by the refuter) · keep: none
- ★C11 · core/replies.py:31, replies.md:24-25 · refuter: partly — `YES_NO, VALUE, CHOICE = "yes_no", "value", "choice"` · reproduced how: the refuter's read · result: reproduced (by the refuter); caveat changed · keep: none
- ★C12 · git help config, the VS Code and Claude Code pages · refuter: holds — "For security reasons, certain options are only respected when they are specified in protected configuration" · reproduced how: the refuter's read · result: reproduced (by the refuter) · keep: none
- ★C13 · board_grant.py:98-99, 211-216 · refuter: holds, with a caveat — `except FileNotFoundError: return True` · reproduced how: the facilitator read board_grant.py:209-216 and listed the store's grants folder: no switch file · result: reproduced; the artboard's direct-flashing row was false and is fixed · keep: none
- ★C14 · the plugins reference, read 2026-11-26 · refuter: partly — "The variables aren't present in the environment of commands Claude runs through the Bash tool" · reproduced how: the refuter's read · result: reproduced (by the refuter); claim narrowed · keep: none
- ★C15 · council/tech-lead.md:13-15 · refuter: refuted — "P368's vendor order is on the path but small" · reproduced how: the facilitator read TL-1 · result: rejected as first written; rewritten · keep: none
- ★C16 · council/refuter.md:10-16 · refuter: the refuter's own reading · reproduced how: the facilitator read it · result: reproduced · keep: none <!-- REQUIRED:claims -->

## Agree / split
<!-- Where the lenses and the refuter agree, and where they split; each split becomes a question.
e.g. `- Split: Feasibility says a day, Risks says a week · Q4` -->
- Agree: a new small class beside the tools list, not the tools list stretched (TL-3; PO-5 reuses only its shape)
- Agree in part: TL-15 recommends that each setting lists the layers that may set it; PO-9 shows it is the common pattern; USER-12 asks. The refuter adds that it breaks the documented `--use … --project .` and two walks' overrides · Q3
- Agree: grants and the direct-flashing switch are never settings (physics-1, USER-16, PO-13) · Q10
- Agree: no account code now (PO-10, TL-21, TL-22). Split inside it: PO-10 makes a GitHub sign-in the first candidate; TL-22 would read the identity from git or GitHub and carry values through P1193's store · Q9
- Split: the first setting. The tech lead says the vendor order, then P410; the user lens and the bar point at P410 · Q7
- Split: where a choice with no layer named is written. Today the person's file (USER-1); the user lens asks whether it should be this project · Q2
- Split, settled: the shops count, 2 of 23 (USER-3) against 3 of 23 (PO-2). The facilitator counted 3 of 24 briefs with `find ~/Development -maxdepth 4 -path '*/.spark/project.json'` and a `sellers` test, spark-quickstart included; the refuter repeated it 
- Split: the refuter reads the evidence as three small defects (★C16), the lenses as a missing layered model; the basis is the PO's D1 · Q7, Q16 <!-- REQUIRED:agree-split -->
