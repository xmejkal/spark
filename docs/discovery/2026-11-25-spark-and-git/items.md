# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>.
e.g. `- needed by: "I want to know what we should build next" (Lena, 2026-10-06)` -->

None is filed. The P-numbers were read on 2026-11-25 (the highest was P1148 #1683) and are read again at filing.

## P1149 — one rules file reaches spark's developers, the PO's lane projects and every gadget session → the team's process moves to `scrum/`, the PO's own lines to a file of his in `scrum/`, and the store's `rules.md` links to it (replaces the on-hold rules move)
- type: chore <!-- REQUIRED:item-type -->
- needed by: "Is it for the agents working on Spark, or are they rules that also apply to agents working on the projects?" and "shouldn't we save the rules somewhere more findable and also like so that we have it in Git?" (the PO, 2026-11-25), D3, D4 <!-- REQUIRED:needed-by -->
- value proven by: A4's table read by the PO. `find ~/Development -maxdepth 3 -name CLAUDE.local.md -type l` still gives 29 that resolve. A grep finds no card, lane, hook or PR in the file a gadget session loads <!-- REQUIRED:value-proven-by -->
- depends on: Q16 (spark's own sessions), Q17 (the spark-rules worktree) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): chore <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P794 #1106 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): team tools <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## P1150 — spark writes no ignore list, so a later `git init` can commit the rules link, a flash image or run files → init writes a marked section into the project's `.gitignore`, with or without a repository (the first half of P1004 #1463)
- type: story <!-- REQUIRED:item-type -->
- needed by: "I think we should actually instruct Spark generally to make the projects with a Git" (the PO, 2026-11-25), D6 ("with an ignore list first") <!-- REQUIRED:needed-by -->
- value proven by: a scratch init: `git check-ignore` names `CLAUDE.local.md`, the flash image and `sim/runs/`, and A1's pass line, 0 tracked files the list covers <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P820 #1173 (P1004 #1463's parent) <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (P1004 #1463's slice is a candidate) <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## P1151 — no step makes a project's folder, and init and the brief write are no Operations → init is a core Operation that calls the exchangeable project strategy, and the strategy makes the folder: the git strategy makes it in the projects home with its repository, and a human strategy leaves it to the person (with P793 #1105)
- type: story <!-- REQUIRED:item-type -->
- needed by: "maybe it should be Sparks agents that create the folder and call the init?" and "the init operation calls it I would say" (the PO, 2026-11-25), D5, D10 <!-- REQUIRED:needed-by -->
- value proven by: `--json` of one init in a scratch home with the git strategy: the folder and its repository made, the project listed only after the folder exists, and the same Operation listed by `--describe`. With a Fake human strategy: no folder made, and one line that asks the person for it <!-- REQUIRED:value-proven-by -->
- depends on: P1150, and P1152's first slice, built together with this item <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P793 #1105 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## P1152 — the git adapter is built inside `write_brief`, so no interface can swap it, and only the brief is ever kept → an exchangeable project-history strategy, git first: init makes the repository and a first commit, each decided record is kept as one step, a read-only history lists the steps, and a take-back runs after the person's yes through the core, with a preview of what goes back, file by file, and never answered by auto mode (D14)
- type: epic <!-- REQUIRED:item-type -->
- needed by: "it should again be a good architecture so that the strategy of the revert and init and all these are exchangable, but the first one we implement for spark is going to be git" (the PO, 2026-11-25), D5 to D9 <!-- REQUIRED:needed-by -->
- value proven by: A1's pass line (D13), then A2, A6 and A7 in scratch, each quoted in its PR <!-- REQUIRED:value-proven-by -->
- first slice: the strategy's seam and the git strategy's init: it makes the folder and the repository, writes the ignore list (P1150) and makes a first commit of the files spark wrote, called by init (P1151). A setting in the person's store turns the repository off once (D6), and then the strategy keeps nothing and says so in one line
- later slices: each decided record kept as one step (D8), the read-only history (D9) and the take-back after the yes (D7). A take-back of a pick also releases or restores the pick's hold in the store, which is outside the project's git (D8's caveat, UX-3). These slices wait on P1155's result
- depends on: the first slice on P1150 and P1157 (the seam's word), built with P1151. The later slices on P1155's result (the A1 test) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): epic <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## P1153 — 29 lines in `scripts/spark` say "Ask Claude" and the brief's line names `git revert` → plain words after a kept step ("Kept. To take it back, say: undo that."), each interface adds its own how, and the id stays in the JSON
- type: story <!-- REQUIRED:item-type -->
- needed by: D11 (the PO, 2026-11-25: plain words) <!-- REQUIRED:needed-by -->
- value proven by: `git grep "Ask Claude" -- scripts/spark` gives 0, and A7's grep finds no "git" in an area's line, and the golden file shows the new line <!-- REQUIRED:value-proven-by -->
- depends on: P1152 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1152 (the epic above) <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## P1154 — the projects list holds 5 entries whose folders are gone, and no command lists the projects or takes one off → a command lists the person's projects and takes a gone one off
- type: story <!-- REQUIRED:item-type -->
- needed by: D10 ("a command can then list the person's projects", the PO, 2026-11-25) <!-- REQUIRED:needed-by -->
- value proven by: its `--json` on the PO's store lists 28 entries and marks the 5 gone (the store as read by the refuter's second pass, 2026-11-25 19:18 CET). After the take-off, 23 remain <!-- REQUIRED:value-proven-by -->
- depends on: P1151 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P793 #1105 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): 10 The store <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## P1155 — nobody has seen spark's commits on a new project or counted the tracked files an ignore list would cover → the A1 scratch walk and a read-only count, against D13's pass line
- type: spike <!-- REQUIRED:item-type -->
- needed by: D13 (the PO, 2026-11-25: "A1, spark's commits happen and are safe, in a scratch folder") <!-- REQUIRED:needed-by -->
- value proven by: the run's lines quoted: 3 of 3 kept lines, 0 tracked files the list covers, and the count in the 9 repositories <!-- REQUIRED:value-proven-by -->
- depends on: P1150, and P1152's first slice (init makes the repository and a first commit, through P1151), because with today's code a brief not in HEAD is never committed (brief ★C14) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1152 (the epic above) <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## P1156 — a `git init` after init commits `CLAUDE.local.md`, a link whose content holds the home path → the link's line is in the ignore list from init on, and a check says when a repository already tracks it
- type: story <!-- REQUIRED:item-type -->
- needed by: "Never commit a vendor file, a home path" (AGENTS.md, the PO's principle). Walk 2 raised it on 2026-10-23 <!-- REQUIRED:needed-by -->
- value proven by: a scratch `git init` and `git add -A` after init leaves `CLAUDE.local.md` untracked, and the check run on the 9 repositories says 0 track it <!-- REQUIRED:value-proven-by -->
- depends on: P1150 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): bug <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P820 #1173 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## P1157 — the seam's words collide (history, commit, revision, change) → one entry in the names table for the project-history strategy and the kept step, before any plan
- type: chore <!-- REQUIRED:item-type -->
- needed by: "Every plan checks its names: one word for one thing" (the PO's rules) <!-- REQUIRED:needed-by -->
- value proven by: the names table's new row in `docs/guide/patterns-and-names.md`, and a grep that finds no second meaning <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): chore <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1152 (the epic above) <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## Board actions
<!-- Each action, taken or pending, with its D. e.g. `- move the item to Discovery · pending` -->
- The discovery card P1148 #1683 · taken: filed by spark-main, Discovery, slice team tools, 2026-11-25 <!-- REQUIRED:board-actions -->
- A comment on P1148 #1683 linking the brief · pending
- Filing P1149 to P1157 · pending, needs the PO's yes to this list
