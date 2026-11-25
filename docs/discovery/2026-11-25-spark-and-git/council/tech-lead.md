# Tech lead: feasibility and fit with the core

The tech lead, on Opus, 2026-11-25. Read on branch `discovery-spark-and-git` at 142656a9 (main). Paths are from the
repository's root; the store is `~/.local/share/spark`. Tags: E (evidence, with a pointer), H (a belief, with its
source), D (a decision, with who and when), — (unknown). I decide nothing; order and value are the PO's.

## Findings

- TL-1 · Spark has one git seam today: `ProjectCommit`, an Adapter that commits one named file with `--only`, never
  stages, never reverts, never pushes, never guesses an author, and runs the person's hooks. Its one caller is the brief
  write. · E `scripts/spark/records/project_commit.py:1-7`, `:26-29`, `:80-89`; caller `scripts/spark/build/project_setup.py:406-426`
  · supports: "commit a write" can grow from this class; today it is no slot that a frontend fills.
- TL-2 · That seam sits outside the core's contract. `ProjectCommit` starts git with its own `subprocess.Popen`, not
  through `OutsideWorld.run`, and `init_project.py` is no Operation: the catalogue lists 50 Operations and no init, and
  init's `main` does the work (76 lines in the baseline). · E `project_commit.py:41`; `scripts/spark/core/outside.py:42-57`;
  `python3 -c "…CATALOGUE…"` printed `50 24 3` and `'init' in CATALOGUE` → `False`; `tests/architecture_baseline.json:18`
  · supports: before LangGraph, MCP or a server can start or set up a project, init must move onto the core (#94), and git
  must become an OutsideWorld slot, handed in by the frontend as `fetch` and `replies` are (`outside.py:71-87`).
- TL-3 · No spark code makes a project's folder or runs `git init`. Init refuses a folder that does not exist. `/spark:idea`
  step S says "Pick the project's folder with the person: their project's folder, or a new one", with no command for
  it, and its allowed-tools hold no `mkdir` and no `git`. · E `project_setup.py:523-524`; `commands/idea.md:2`, `:25`;
  `git grep -n -i -E "mkdir|git init|new folder" -- commands agents skills docs/guide` → only `commands/idea.md:25`
  · supports: today Claude makes the folder (or the person does), through Claude's own tool calls and permission prompts. D-q4 has no
  answer in the code.
- TL-4 · On a new repository, init cannot commit the brief. `held_as_is` needs `HEAD:./.spark/project.json`. Init's
  first run writes that file untracked, so the `--answers` run that follows says UNHELD. `git commit --only` refuses an untracked file,
  and P1027 forbids `git add`. · E `project_commit.py:5`, `:71-73`; `project_setup.py:416-423`; spike in a scratch
  folder with git 2.49.0: `error: pathspec './new.json' did not match any file(s) known to git`, exit 1 · supports: the
  brief's outcome ("its brief commit … with no step by hand", `brief.md:17`) needs a "make the repository" step that
  also commits spark's first files. In the same spike, `git add -N new.json` followed by `commit --only -- ./new.json` committed that file
  alone and left the person's staged file staged (`A  mine.txt`). It is a way to keep "one file, nothing of yours", but it is
  a staging command, which P1027's rule forbids today (D-e's card).
- TL-5 · A spark write is often more than one file, and no Operation says which files it wrote. Of 50 Operations, 24 declare WRITES
  (some write only the store: `drawer-set`, `fact-set`), and only 3 name the project they wrote: `pick`, `build-board` and `deploy`.
  The follow-up after a write runs only for those. · E the catalogue run above (`50 24 3`);
  `scripts/spark/core/operation.py:108-112`; `scripts/spark/core/cli.py:139-153` · supports: to commit each write,
  each writing Operation must first report its written files (a new result field). Only then can the core commit after it,
  in `_followed`, the place where the page refresh already happens.
- TL-6 · Spark writes no `.gitignore`. The agents' guide says "`sim/runs/` is gitignored", and that holds in only 1 of
  the 9 listed project repositories. A commit of everything would take `firmware/*secret*.py` and the transient
  `.spark/page-request.json` with it. · E `git grep -n -i gitignore -- scripts` → nothing; `docs/guide/agents/flow.md:317`;
  `scripts/spark/firmware/project_secrets.py:3-4`; `scripts/spark/flow/run_request.py:30`; the store walk in TL-8
  · supports: making a repository must write an ignore list for spark's generated, private and transient files. A
  committed secret is the one case for a history rewrite (D-f, the PO, 2026-11-23).
- TL-7 · The rules file that spark links into every project is the file that holds the spark team's rules.
  `~/Development/spark/CLAUDE.local.md` links to `~/.local/share/spark/rules.md`, and `AiFiles` links each project's
  `CLAUDE.local.md` to `<store>/rules.md`. The neutral rules that spark ships are `data/agents-section.md` (8 lines), in
  AGENTS.md between the markers. · E `ls -la` of the link; `scripts/spark/build/ai_files.py:36`, `:84-97`, `:19-25`, `:42-64`;
  `grep` counted 38 of rules.md's 106 lines that name board, PR, hook, lane or council (a word count: H as a measure)
  · supports: D-q1 touches one path and one method. Moving `rules.md` itself breaks every existing link (TL-15).
- TL-8 · The store's `projects.json` lists 28 projects, and 23 of their folders exist. 9 of them have a `.git` folder at the top, 14 have none, and none
  is inside another repository. Of the 9, 6 track `.spark/project.json`, 2 do not, and 1 has no commit. All 9 are on a
  branch. 2 have no `.gitignore`. All 23 hold the `CLAUDE.local.md` link. · E a read-only Python walk over
  `~/.local/share/spark/projects.json`, 2026-11-25 (`git symbolic-ref`, `rev-list --count`, `ls-files --error-unmatch`)
  · caveat: the brief counts 8 with a repository, 15 without and "some inside another"; it reads another set (perhaps walk folders off the
  list). The two counts are not reconciled. · supports: init's brief commit works today in 6 of the 23 folders.
- TL-9 · A project is known by its resolved local path. `projects.json` maps a name to a path, `KnownBoardStore` keys by
  the sha256 of the resolved folder, and `store.home()` reads `SPARK_HOME` from the process environment on each call.
  · E `scripts/spark/records/store.py:452-460`, `:58-64`; `scripts/spark/bench/known_board.py:416-428` · supports: one
  server process cannot serve several people's stores at once without a change (H: an environment variable belongs to the whole
  process). A git repository moves with its folder; the store's records about that folder do not.
- TL-10 · Undo: spark's own code never runs a revert (D-e, P1027), but the core already has a channel for the yes: the
  ASKS effect and `make_consent`, which each frontend fills. · E `commands/idea.md:78-79`; `project_commit.py:5`;
  `outside.py:32-35`, `:74-87`; `operation.py:28-31` · supports: an "undo one write" Operation is feasible on that
  seam, but it reverses D-e. Without that change, undo stays a step that Claude runs in the chat, and LangGraph, MCP and a website have no
  undo.
- TL-11 · The page's click path is already an Operation with an allowlist. `RunRequest` runs only `PickParts`,
  `WriteRequirements` and `BuildBoard`. The transport is the RequestChannel in the page's script, and a server
  swaps the channel, not the Operation. · E `run_request.py:42-44`; `~/.local/share/spark/councils/p1113/architect-page-actions.md:14-15`;
  `docs/discovery/2026-11-15-p820-artifact-interface/mvp-plan.md:146-147` · supports: on every interface, git
  is the same Operation behind another channel. An undo button would be a new kind of offer, which `RunRequest` refuses today.
- TL-12 · The words for the seam are taken. "history" is the store's event log, "Port" is the serial-port Value
  in the names table, and "versions" is the tools' versions. · E `store.py:469-474`; `docs/guide/patterns-and-names.md:20`;
  `scripts/spark/records/versions.py:1-3` · supports: the seam needs another word (one word for one thing). The
  pattern is Strategy plus Adapter, since the names table has no "Port" pattern (`patterns-and-names.md:14-21`).
- TL-13 · `AiFiles` writes the exclude line into the `.git/info/exclude` of the first `.git` it finds walking up. A
  worktree (a `.git` file) gets a note instead, and a project inside another repository has its line written into the outer
  repository. `ProjectCommit` already handles a project in a subfolder of a repository. · E `ai_files.py:99-112`;
  `store.py:202-208`; mutation row `tests/mutations/p1027-dropped-need.json:16` · supports: D-q2 must say whether
  a project inside a repository gets its own. A `git init` there makes a nested repository, which the outer one sees as
  an untracked embedded repository (H, git's documented behaviour, not run here).
- TL-14 · `ProjectCommit` refuses to commit without a git identity (`user.useConfigOnly`). The PO's global identity is set. · E
  `project_commit.py:82-85`; `git config --global user.email` exit 0 · supports: on a server or in a LangGraph run
  with no identity, every commit is refused until the frontend supplies one (whose name goes on spark's commits is a choice).
- TL-15 · A `CLAUDE.local.md` that links anywhere else stops init's link step with "remove it and run init again". · E
  `ai_files.py:86-90` · supports: if D-q1 moves or splits the file the 23 links point to, each project needs one step by
  hand, unless the old path stays and is the file the projects need.

## What each decision would touch, and a proposed order

**D-q1, whose rules go where.** Code: `AiFiles.rules` and `claude_local_md` (`ai_files.py:36`, `:84-112`),
`data/agents-section.md`, `commands/init.md` (the CLAUDE.local.md bullet), `tests/test_ai_files.py`, and the golden
init output. No code changes if the team's rules move out of `rules.md` (to `scrum/`, D-a) and `rules.md` keeps only what
a project's agent needs. A new path for the project rules means 23 links to fix by hand (TL-15). This one is independent of git.

**D-q2, a repository per project.** Code: a "make the repository" step (`git init`, an ignore list (TL-6), and one first
commit of the files spark wrote) in init's library (`project_setup.py`) or in a new Operation, and `ProjectCommit` grown to commit
named new files (TL-4). Docs: `commands/init.md`, `commands/idea.md` S item 0. Tests: `tests/test_project_commit.py`,
`tests/test_init_project.py`, `tests/golden-design/init-project-ok-brief.txt`, and mutation rows next to
`tests/mutations/p1027-dropped-need.json`. Open within it: its own repository or the enclosing one (TL-13), and what happens
when the person has no git identity (TL-14).

**D-q3, what spark does with git.** (a) Commit after a write: each writing Operation reports the files it wrote, and the
core commits them in `_followed` (`cli.py:139-153`) through a new OutsideWorld slot and effect word (`outside.py:42`,
`:71`; `operation.py:28-31`), with a Fake in `tests/fakes.py`. This changes the core, so the architecture lens on Opus applies
(rules.md, 2026-11-25). (b) Show history: one read-only Operation over spark's own commits (their messages start
`spark: `, `project_setup.py:400`). (c) Undo: an Operation with ASKS, feasible (TL-10), and only after the PO changes D-e.
All three add to `docs/guide/agents/json.md`, `scripts.md` and the catalogue's test.

**D-q4, who makes the folder.** Today Claude in `/spark:idea` makes it (TL-3). A spark agent would call an Operation
anyway: "an agent prompt never repeats its logic" (AGENTS.md). Only a core Operation ("start a project": the folder,
the repository, init's files) holds on every interface. It needs init on the core first (TL-2). For a folder it did not
make, the core needs one Value that reads: does it exist, is it listed (`store.plan_listed_name`), does it hold a brief, which
repository holds it (`store.inside_git`), what git says of the brief (`held_as_is`), and whether there is an identity. Most of
these exist as functions today.

**D-q5, the four interfaces.** CLI: the git Adapter with the person's identity. LangGraph: `run_operation` in
process, and the graph hands in the slots. MCP: the catalogue and `input_schema` exist (`operation.py:113-127`), and the
yes for an undo needs that host's way of asking (—). A server: one folder per person, an identity per account, and a store per person
(TL-9). The page's RequestChannel becomes HTTP to the server, which runs the same `RunRequest` (TL-11). Nothing to
build now (D-d).

**Against the one bar** (AGENTS.md): a project reaches a breadboard with working firmware without git today, so none of
this is on that path. D-q2 and the commit of the brief keep P1027's "way back" working for a new person. That serves the walk's
"no step by hand". D-q3 (b) and (c) are tooling: candidates to pause until a walk shows the need.

**Proposed order, a proposal only:** (0) the spikes below; (1) D-q1 as a docs and rules move with no code; (2) init onto the
core as an Operation, inside #94's build PR; (3) D-q2's "make the repository" in that Operation, with the ignore list;
(4) D-q3 (a), the written files and the commit after a write; (5) D-q3 (b); (6) D-q3 (c) only on the PO's word on D-e.
D-q5 is checked in each card's architecture lens and never built.

## What I could not check, and the spike that would settle it

- Anthropic's advice and the conventions for AGENTS.md: the web was out of my scope (the researcher's job).
- Why the brief's count of folders (8 / 15 / some inside another) differs from mine (9 / 14 / 0): which set the brief read. A
  read of the brief's source settles it.
- How long a commit per write takes, and how many commits a walk makes: a build writes many files, and the person's hooks run.
  A 30-minute spike: replay one fixture walk with a commit after each Operation that writes, and count and time the commits.
- `git init` in a folder inside another repository, and what the outer repository's `status` then shows: a 15-minute spike.
- Whether `git add -N` is acceptable under P1027's "never stages": not a spike, the PO's word.
- How MCP, LangGraph and a hosted server would ask for the yes before an undo, and whether a server would use git at all: H, not
  settled by reading this code. A spike after a host exists.
- Whether `page.html` and the generated build outputs belong in a project's repository: the PO's choice. The code
  does not say.

## Questions for the decider

- Q · Does a project inside another repository get its own repository, or does spark commit into the one that holds it?
  · decides: D-q2, and whether TL-13's nested-repository case exists.
- Q · May spark run `git add -N` (intent to add) for a file it made, so that its commit holds that file alone? · decides:
  whether D-q2 and D-q3 (a) can keep P1027's rule of one file and nothing of the person's.
- Q · Does D-e still hold ("spark's own code never runs a revert"), or may an undo Operation run on the person's yes through
  the core's consent? · decides: D-q3 (c), and whether interfaces other than Claude have an undo.
- Q · Does every writing Operation commit, or only the brief and the files the person decided (needs, picks,
  requirements)? · decides: how big D-q3 (a) is, and how many commits a walk makes.
- Q · Do the team's rules leave `rules.md`, so that the 23 links keep working, or does the project rules file move? ·
  decides: D-q1, and whether 23 folders need a step by hand.
- Q · Whose name goes on a commit when the person has no git identity (on a server, in LangGraph)? · decides:
  D-q5's identity rule.

## Searches

None.
