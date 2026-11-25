# PO assistant: Existing first, and Risks and assumptions

Lens: the PO assistant, on Opus, read-only, 2026-11-25 (Europe/Prague). Pointers are to the tree at 142656a9 (the worktree
of this discovery), to the store (`~/.local/share/spark/`), and to read-only git commands run on the person's folders.
Home paths are written as `~/...`. Private repository addresses, board addresses and port names are not copied.

## Findings

### (a) Existing first: what does each decision today

- PO-1 · Spark's agents and a person's project agents read one rules file today. `rules.md` is titled "Rules for every spark project" and its line 3 says "for the projects that use spark", but init links it into every project. 29 `CLAUDE.local.md` links point at it: 22 project folders, `~/Development/plant-alarm` (a `.spark/` with no `project.json`), spark itself and 5 spark worktrees (spark-ask-claude, spark-asleep-fix, spark-p1002, spark-p1038, spark-p1039). So the board, lanes, hook, `tools/mutate.py` and journey-table rules load into the session of a breadboard walk. · E · `~/.local/share/spark/rules.md:1-6`; `scripts/spark/build/ai_files.py:84-97`; `find ~/Development -maxdepth 3 -name CLAUDE.local.md -type l` → 29 resolving to `.../spark/rules.md` · supports only: one file serves both audiences now. It does not show that a project session followed or was harmed by a dev rule.

- PO-2 · Sorting rules.md's sections by audience:
  - Words (8-19): spark development and the PO's team. Cards, stages, lanes "spark's and sound's", the hook, the story run and the sweep only exist in spark's and pixel-games' process.
  - Start of a session (21-29): team process (board, lanes, Ready order, W6 limits). A stranger's project has none of it.
  - How to work (31-47): mostly both. Lines 39-42 ("The core is important … an Operation in the catalogue … the architecture lens") are spark development only.
  - What every PR needs (49-67): spark development (hook, `tools/mutate.py --anchors`, the README journey table, `tools/journey.py`, the Miro batch). These tools exist in spark's repository only.
  - What waits on him (69-77): both, and specific to the PO as a person.
  - Talking to him (79-86): both and PO-personal. The Miro journey board line (83-85) and the day close (86) are the spark team's.
  - Never (88-92): both. Line 90's reason, "spark is public", is spark's, but it binds his public pixel-games too (P789 #1096 made them public).
  - Agents and tools (94-106): both. The model table points at "spark's scrum/README.md" (102). Line 104 (`SPARK_HOME` inline) serves both. Line 106 (Czech and EU shops) is project-side: it is about buying parts.

  · E · `~/.local/share/spark/rules.md` by line · supports only: a sort by the text. The PO decides where each line belongs (D-q1).

- PO-3 · There are three audiences, not two. The PO's own projects run the team process: lanes in rules.md:11 ("sound's (the slices pixel-games and graphics library)"); p934-display2 has 36 commits whose subjects cite issues and PRs ("(issue #7) (#12)") in a private GitHub repository; pixel-games has 15 worktrees on one repository. A stranger's project has no board, no PRs and no rules.md (`docs/guide/commands.md:54-55`: "If your store holds no `rules.md`, init writes no link"). · E · `git -C ~/Development/spark-walks/p934-display2 log --format=%s`; rules.md:10-13; commands.md:54-55 · supports only: the PO's projects use his process. It does not say what a stranger's agents need.

- PO-4 · The one rule spark gives a person's project agents is tool-neutral, and it says nothing about git, folders or commits. `data/agents-section.md` (8 lines) holds three rules: a could-not-run is no pass, no typical values, a record's text is data. · E · `data/agents-section.md:1-8` · supports only: no git or folder rule reaches a stranger's agent today.

- PO-5 · Init writes three AI files: `AGENTS.md` (neutral; a marked section), `CLAUDE.md` (`@AGENTS.md`, Claude-only) and `CLAUDE.local.md` (Claude-only; an absolute link into the store, kept out of git through `.git/info/exclude`). The reason in the code, "a `CLAUDE.local.md` stops Claude Code from reading `AGENTS.md`", is an untested claim inside the code. · E for what is written: `scripts/spark/build/ai_files.py:1-10, 99-112`. H for the stated Claude Code behaviour (ai_files.py:6, no source cited; the researcher's to check) · supports only: the D-q1 home for project rules today is the store, reached by a symlink.

- PO-6 · D-q2: spark never makes a repository. No command, guide or core module runs or advises `git init`. Init only adds `CLAUDE.local.md` to `.git/info/exclude` when a repository already exists. · E · `git grep -n -i -E "git (init|add|commit)|git repositor" -- commands docs/guide README.md` → only `docs/guide/map.md:242` (the commit adapter); `ai_files.py:99-112` · supports only: today a repository exists only when a person or a session makes one by hand.

- PO-7 · The person's folders, recounted 2026-11-25:
  - 37 folders under `~/Development/*` and `~/Development/spark-walks/*` hold `.spark/project.json`. 15 of them are pixel-games worktrees of one repository (pixel-master and pixel-p757 … p915, all with `--git-common-dir` = firebeetle-games/.git).
  - Of the other 22: 9 are the top of their own repository and 13 have none. The 9 are blink-c6, firebeetle-games, irrigation, rc-car, smartbin-local, spark-quickstart, p934-display2, reaction-game and zigbee-stick. reaction-game has no commit, so 8 have history.
  - Adding plant-alarm (a `.spark/` without `project.json`) gives 23 folders, 8 with history and 15 without. This matches the brief's "8 of 23" if a repository with no commit is counted as none.
  - All 12 folders under spark-walks except p934-display2 and reaction-game, plus button-light, have no repository.

  · E · a read-only `git rev-parse --show-toplevel` and `--git-common-dir` over each folder, 2026-11-25 · supports only: the count, if it is read the way stated.

- PO-8 · D-q3: spark's use of git is one file on one path. `project_commit.ProjectCommit` is "The only code in scripts/spark/ that runs git" (project_commit.py:27-28). Its only caller is `write_brief` (project_setup.py:421), so only `.spark/project.json` written by `init_project.py --answers` is ever committed. These writes are never committed: needs.json, needs-basis.json, requirements.json, rules.json, boards/active.json, AGENTS.md, CLAUDE.md, package.json and every other `--needs-set`/`--pick`/`--requirements` write. Spark never stages, reverts, resets or pushes (project_commit.py:5). It refuses a missing identity (`user.useConfigOnly=true`, :82-85), runs the person's hooks, and commits on any branch (only "on a branch" is checked, :74). · E · `git grep -n "project_commit\|ProjectCommit" -- scripts` → project_setup.py only · supports only: what the code does. "Spark uses git" today means one commit kind.

- PO-9 · Since P1027's adapter landed (2026-11-23 16:56 CET, last change 17:56 CET), none of the 9 repositories holds a `spark:` commit. A read-only replay of `held_as_is` today:
  - 6 would commit: blink-c6, irrigation, rc-car, smartbin-local, spark-quickstart, p934-display2.
  - 3 would not, because git does not hold the brief: firebeetle-games's main checkout never added it; reaction-game has no commit; zigbee-stick's `.gitignore` ignores `.spark/` entirely.
  - pixel-master's worktree is on no branch.
  - Every repository has a user.email.

  · E · `git log --grep='^spark: '` count 0 in each; the probe replays project_commit.py:69-77 with `git --no-optional-locks` · supports only: the state of today's checkouts. Two days is too short to say how often brief writes happen.

- PO-10 · Claude already runs git in the PO's projects outside spark. p934-display2 has 36 commits with 43 `Co-Authored-By: Claude` lines; its first commit (2026-11-22) is "Start the P934 e-paper clock project repo". zigbee-stick's single commit (2026-11-12) holds "spark's init files", co-authored by Claude. So the de facto answer to "who makes the repository" is the session, by hand, case by case. · E · `git -C ~/Development/<repo> log` · supports only: the PO's own practice. It does not show what a stranger wants.

- PO-11 · D-q4: no one in spark makes the folder. `/spark:idea` S item 0 says "Pick the project's folder with the person: their project's folder, or a new one" and runs `/spark:init` in it, but it never says who creates a new one. Init refuses a missing folder ("no directory at", `no_project_folder`), and `/spark:idea`'s allowed-tools hold no `mkdir`. So today Claude makes the folder with a plain shell call, under a permission prompt. `parts.py --step <project> S` runs before init and lists the project in the store. · E · `commands/idea.md:13-14, 25-28`; `commands/idea.md:3` (allowed-tools); `scripts/spark/build/project_setup.py:520-524`; `build_codes.py:92`; `scripts/spark/sourcing/mark_step.py:1-5` · supports only: the folder's start is unowned in the text.

- PO-12 · D-q5: the folder's start, init, the brief write, the commit and the undo are all missing from the core's catalogue. `spark.operation_catalogue.CATALOGUE` holds 50 ops. None of them is init, a brief write, a commit, history or an undo; `build` holds only `build-board`, and `idea` only `needs-drop`. `init_project.py` is a fat `main()` with no `--json`, and the brief's commit runs inside it. So an MCP server or a LangGraph node that reads the catalogue cannot start a project or write a brief today. · E · `python3 -I -c 'import spark.operation_catalogue as c; print(sorted(c.CATALOGUE))'` → 50 ops; `scripts/init_project.py:44-119`; `scripts/spark/build/build_operations.py:9`; `scripts/spark/idea/__init__.py:10` · supports only: what exists. It does not say how hard the move is.

- PO-13 · D-q5: the undo's safety rests on Claude Code. idea.md:78-79 says "offer to run `git revert --no-edit <sha>` … run it only after their yes. Spark's own code never runs it", and idea.md:87 says "Claude's permission prompt for git revert is expected; do not widen allowed-tools" (D-e). Over MCP, in LangGraph or on a hosted site there is no Claude permission prompt and no Claude to run the revert, so D-e names no holder of the yes there. · E for the text · H for the consequence (this lens) · supports only: D-e is written for the Claude Code frontend.

- PO-14 · An undo without git already exists, so no one is blocked without a repository. Before a must-line change, Claude says the old list in the chat ("so that it is in the conversation even without git"), and without git it puts the old lines back with `--answers` on the person's word. The flow page says the same ("git keeps each change", flow_codes.py:377). · E · `commands/idea.md:74-77, 84-85`; `scripts/spark/flow/flow_codes.py:376-383` · supports only: a fallback is written. Whether it is used is not shown.

- PO-15 · One existing design already depends on a project's own repository and a GitHub remote. P1065 #1563 (open) refuses `flow.py issues` as could-not-run when the project folder is not the git top folder. The P1038 page design shows the issues box only from `gh issue list`. A folder without its own repository, or with no GitHub remote, gets "not read". · E · `gh issue view 1563`; `docs/discovery/2026-11-23-p1038-page-design/design.md:154, 248` · supports only: one consumer that a per-project repository with a remote would serve. A remote is out of this discovery's scope (brief.md:20).

- PO-16 · D-q1, "where each set lives": rules.md and learned-rules.md live in the store, and the store refuses to sit inside any git work tree ("what you own stays out of every repository"). So D-a ("the rules go into git") means they leave the store; they cannot be in git and in the store. The store also serves as the spark team's notebook: 59 top-level `.md` files, such as day-close-*, handoff-*, council-brief-*, morning-* and finding-*, sit beside the person's drawer, boards and grants. · E · `scripts/spark/records/store.py:145-146, 386-390`; `ls ~/.local/share/spark` → 83 entries, 59 `.md` at top level · supports only: the conflict in homes. The split of those 59 notes is by name only (H).

- PO-17 · The learned rules are the development team's. Their 14 categories cover tests, mutation, refactors, AI slop and tools that change the tree; rule 14.1 is "read `git diff` before the next commit". Their log mixes spark and pixel-games entries (`git submodule update --init --recursive` for pixel-games worktrees). None of them addresses a stranger's project. · E · `~/.local/share/spark/learned-rules.md:15-108, 416-419, 474` · supports only: their audience by their text.

- PO-18 · Spark's development tools already read project repositories: `tools/board.py:145` runs `git log --all --since` over folders, and `tools/snapshot.py:128` reads a project folder with `--no-optional-locks`. A change to where project repositories are, or whether they exist, touches team tooling too. · E · those lines · supports only: a dependency exists. Its purpose was not read in full (H).

### (b) Risks and assumptions

- PO-19 · Secrets, images and board logs are the largest present risk of "every project has a repository". Spark writes no `.gitignore` (`git grep -i gitignore -- scripts` finds none). P1004 #1463 is open ("spark keeps nothing out of git"); its sketch has `/spark:init` write `.gitignore` lines for the image and the secrets file. Today:
  - blink-c6 tracks 3 files under `sim/runs/` and 1 `.bin`;
  - firebeetle-games tracks 80 `.bin` although its `.gitignore` lists `*.bin`;
  - p934-display2's hand-written `.gitignore` (wifi_secrets.py, the flash image, sim/runs/, CLAUDE.local.md) is P1004's sketch done by hand.
  - No secret file is tracked in any of the 9 repositories.

  D-f says history is rewritten only for secrets, so one committed Wi-Fi password forces exactly that. · E · `git ls-files` per repository (names only; no file opened); `gh issue view 1463` · supports only: the exposure exists without a `.gitignore`. It does not say how often a secret is written.

- PO-20 · For "every spark project has its own git repository and spark uses git" to be good, these must hold (each H, this lens, unless tagged):
  - A1, value: a person wants their project's history and an undo through spark, and a stranger is "at home in a terminal" with git. VISION:38 says the primary persona is a hypothesis, and no outsider has installed spark (E).
  - A2, feasibility: spark's commits are taken in practice: the brief is held as-is, HEAD is on a branch, an identity is set. PO-9 shows 6 of 9 repositories would, 3 would not, and 0 commits so far (E).
  - A3, safety: what spark commits holds no secret, image or private log. PO-19 shows that is not true today without a `.gitignore` (E).
  - A4, usability: spark's commits do not cut across the person's own git flow (PRs, branches, hooks). p934-display2 works by PRs on a private repository whose local `main` is checked out (E), so a brief commit would land on local `main` beside PR merges.
  - A5, feasibility: a project folder is never inside another work tree. A `git init` there makes a nested repository; `store.inside_git` walks up and would see the outer one (store.py:202-208).
  - A6, interfaces: one seam serves the CLI, LangGraph, MCP and a server. Init, the commit and the undo first need to be Operations (PO-12), and the undo needs a yes that is not Claude's prompt (PO-13).
  - A7, viability: on a hosted site, a git repository per person and per project is acceptable in cost and isolation. The PO is "not sure" about the site (brief message 5); VISION:83's non-goal ("Anything designed on paper before a design needs it") and AGENTS.md:60 (free, few, local) bear on how far to design for it.

- PO-21 · The riskiest belief, proposed by this lens and pending Q1: A2 with A3, "the commits spark makes in a person's repository happen and are safe". Each decision D-q2 to D-q5 rests on it. Evidence is 0 field commits, 3 of 9 repositories that cannot commit the brief at all, and no `.gitignore` from spark. · H, this lens, from PO-9 and PO-19 · supports only: a ranking proposal. The decider rates it.

- PO-22 · The cheapest tests, proposed. The decider sets each pass line before any result.
  1. Re-run PO-9's read-only probe over the 9 repositories daily for a week of real walks, and count the `committed as` and `not committed:` lines that init prints in those walks. Cost: minutes, no write.
  2. Run `init_project.py --answers` once in a fresh temporary repository with `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1` and a temporary `SPARK_HOME`. This shows what a stranger with no git identity sees (useConfigOnly makes it a refusal; whether the line is clear to a person is the open part). Cost: one command, a temp folder.
  3. Run `git ls-files` in each repository against P1004's ignore list. That shows how much a spark-written `.gitignore` would have kept out.

  · H, this lens · supports only: the test designs.

- PO-23 · Pre-mortem: "It is 2027-05, six months after this shipped, and it failed." Why, each H (this lens):
  - (1) A Wi-Fi password or a board log with a device's address was committed and pushed, because the repository came before the ignore list (PO-19), and history had to be rewritten (D-f).
  - (2) Spark's commits rarely happened. The brief had the person's edits, the folder ignored `.spark/`, or the HEAD was detached (PO-9). People then asked for an undo that was not there, and trust dropped more than with no undo at all.
  - (3) Spark's commits landed on `main` beside a person's PR flow (PO-4's p934-display2 case), and the person reverted or squashed them away.
  - (4) The rules split into two or three files that drifted. The 29 symlinks (PO-1) kept pointing at the old file, and project sessions still read development rules, or lost the PO-personal ones (PO-2).
  - (5) MCP or LangGraph shipped with no project start or undo, because init stayed a CLI `main()` (PO-12). Or the server ran `git revert` itself, which breaks D-e (PO-13).
  - (6) Spark grew into a git client (history views, undo UI) against "one tool per job" (AGENTS.md:60), while Claude, which already runs git in the projects (PO-10), would have done it.
  - (7) Folders made inside another repository became nested repositories (A5).
  - (8) The hosted site never came, and the seams built for it cost more than they served (VISION:83).

- PO-24 · Is anyone blocked now? No one, on the evidence:
  - 13 of 22 project folders have no repository and their walks went on;
  - the brief undo has a no-git fallback (PO-14);
  - the only consumer that needs a repository is P1065's issues box, which is open and not built (PO-15).

  The pressure is the PO's wish ("I would definitely like the Spark projects to have a Git repository", brief message 1) and P1004's open secret exposure. · E for the counts and cards · H for "no one is blocked", since no person outside the PO was asked · supports only: a sequencing argument. It does not argue against doing it.

## What I could not check, and why

- Whether any brief write since 2026-11-23 17:56 CET printed `not committed:`. Init's line is not kept in the store's `history.jsonl`, and session transcripts were not read (time).
- How Claude Code loads `CLAUDE.local.md`, `CLAUDE.md` and `AGENTS.md` (ai_files.py:6's claim). This needs the web, which is the researcher's.
- A stranger's machine: whether git is installed and an identity set. Init was not run (it writes to the store's projects list), so PO-22 test 2 stays a design.
- What the tracked `sim/runs/` files and `.bin` images hold. They were not opened (they may hold port names or secrets, which the brief forbids copying); only names were counted.
- The branch state of the 14 pixel worktrees other than pixel-master.
- GitHub rulesets on the PO's private project repositories: the API answers 403 on this plan.
- How LangGraph, MCP or a hosted site would carry a person's yes. None of them exists in the tree.
- Why tools/board.py and tools/snapshot.py read project repositories, beyond their lines.

## Questions for the decider

- Q-a · Are the PO's own projects (pixel-games, the walks) governed by the development rules, the project rules, or a third set of "the PO's team rules"? · decides D-q1: two homes or three (PO-2, PO-3).
- Q-b · Does spark commit only the brief (P1027 today), or every write it makes in a project? · decides D-q3's scope, and whether a `.gitignore` (P1004) must come first (PO-8, PO-19).
- Q-c · Does a spark-made repository come before or after spark writes the ignore list for secrets, images and board logs? · decides order: P1004 before D-q2, or with it (PO-19).
- Q-d · Outside Claude Code (MCP, LangGraph, a server), who gives and who carries out the yes to an undo, given D-e ("Spark's own code never runs it")? · decides D-q5 for the undo, and whether D-e is restated per frontend (PO-13).
- Q-e · When the chosen folder is already inside another repository, does spark make a nested repository, use the outer one, or refuse? · decides D-q2's edge (A5).
- Q-f · Does init (and the brief write) become an Operation on the core before any git work, so that every frontend can start a project? · decides D-q4 and D-q5 order (PO-12).
- Q-g · Does spark's commit go to the branch that is checked out, or to a branch of its own, in a project that works by PRs? · decides D-q3's fit with a person's git flow (PO-20 A4).
- Q-h · Which pass lines do PO-22's three tests have to meet, and which assumption is rated high? · decides Q1 and the riskiest test.
- Q-i · Do the 59 team notes in the store move with the rules into git, stay private in the store, or split? · decides D-q1's "where each set lives" beyond rules.md (PO-16).

## Searches

none.
