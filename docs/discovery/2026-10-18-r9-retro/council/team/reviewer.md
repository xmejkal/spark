# Reviewer: R9 retro voice
Scope: 36 lens, plan-review and code-review runs in the logs (44 min, 30 M input tokens), plus INDEX rows since AT380.
**What helped**
- Cheap diff reviewers on the everyday model (0.3 to 0.9 M tokens each) found real defects: a KeyError on the no-room path (AT422), tests below `unittest.main()` that a direct run skipped (AT382), a read-order bug in the chip read (AT452).
- Plan council round 2 by the PO assistant costs 0.1 to 0.3 M tokens. It caught a missing Value row in developing.md (AT401) and a `choose_flasher` that changed behaviour (AT404), before any code existed.
- The tech lead catches name clashes early: two `BOOT_HINT` names (AT403), `flasher` meaning two things (AT405).
**What slowed or wasted**
- The four Opus lenses (architecture, UX, PO assistant, AI-UX) cost 15 M tokens and 137 tool calls. The architecture lens alone took 51 calls and 5.4 M. A Sonnet diff review takes 4 to 16 calls.
- Names reach round 2 unchecked: AT451 lists factory names that were nouns and a `board_log` clash with `BoardLog`. The lens spends its calls on what the author can check alone.
- The refuter reads the same diff after the reviewer, and 102 of its tool results in 34 runs were errors.
**One change I ask for**
- Size the lenses by the table in the working agreements and write the size in the PR Council section. Under 50 lines or docs only: one Sonnet reviewer, no Opus lens. Opus lenses run only for a design or an epic. Before round 1 the author runs the name check against developing.md.
