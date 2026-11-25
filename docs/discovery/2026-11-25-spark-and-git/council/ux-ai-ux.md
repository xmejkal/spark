# UX and AI-UX lens: spark and git

The lens reads the person's side and the agent's side of the change, and changes no file but this one. Read on
2026-11-25 at origin/main 142656a9, in the discovery's worktree. The projects list itself is private
(docs/guide/agents/scripts.md:71), so this report calls projects A and B. Other reports name projects that spark's
public docs already name.

## 1. Findings

Format: UX-n · claim · tag · pointer · supports only.

- **UX-1** · The file that every project's agent reads as its rules is the spark team's development rules. init links
  `CLAUDE.local.md` to the store's `rules.md` (scripts/spark/build/ai_files.py:84-97), and all 23 listed project
  folders that still exist carry that link. The spark repository's own `CLAUDE.local.md` links the same file. The
  file's title is "Rules for every spark project" (rules.md:1), but most of its lines are about developing spark.
  Lines that would mislead a gadget-project agent: "Every change reaches main by a PR; commit after each step and push"
  (:51), "You merge when the hook passed" (:65), "you pull the top card of your lane without asking" (:25),
  `check_commit` and `tools/mutate.py --anchors` (:52-53, tools a project does not have), and "~/Development/spark/AGENTS.md"
  (:4, a developer's clone, not an installed plugin). Lines that help it: :71-73 (what cannot be undone waits on the
  person), :92 (never guess a null), :106 (EU shops) · E: rules.md lines cited; `readlink` on each listed folder's
  `CLAUDE.local.md`, 2026-11-25 · supports D-q1 only.
- **UX-2** · Today's undo never fires on the walk that /spark:idea prescribes. Step S runs init with no board, which
  writes an untracked brief, then right after it runs `--answers` (commands/idea.md:25-35). That gives `UNHELD` ("not
  committed: git does not hold .spark/project.json here…"). The golden test shows this line on a first brief
  (tests/golden-design/init-project-ok-brief.txt). Nothing in spark runs `git init` or a first commit
  (`git grep "git init"` in commands, scripts and docs/guide: none). Of 9 listed projects with their own repository, 0
  hold a `spark: ` commit, 3 do not track the brief and 1 has no commit at all · E: commands and files cited;
  `git log --grep '^spark: '` and `git ls-files .spark/project.json` per project · caveat: P1027 slice 2 is days old ·
  supports D-q2, D-q3.
- **UX-3** · git can take back only half of a pick. `--pick` writes the project and also reserves what the person owns
  in the store (`used_in` on the drawer entry; commands/idea.md:168-169). The store is never inside a git work tree, by
  design (docs/guide/agents/scripts.md:71). So "undo that" after a pick, done by `git revert`, would bring back
  needs.json and leave the hold. The person would see "held by <this project>" on a part they took back · E: pointers
  cited; 13 drawer files hold `used_in` · supports D-q3 (what an undo covers).
- **UX-4** · A person meets five ways back, under five sets of words, and none is called "undo":
  - `git revert` for the brief (scripts/spark/build/project_setup.py:383);
  - `.spark/previous/requirements.json.txt`, one level deep: "a second removal replaces it" (commands/idea.md:237);
  - `.spark/previous/board.tsx.txt`, and "to regenerate it, delete it" (docs/guide/commands.md:190-191);
  - the old lines said in the chat: "Ask Claude, and Claude puts the old lines back" (project_setup.py:386;
    commands/idea.md:74-75);
  - fixing needs.json by hand (commands/idea.md:41-42).

  The page canvas turned its way back into "Copy a line for Claude" (councils/p1113/finding.md §6) · E · supports D-q3.
- **UX-5** · Four words name two things each, against "one word for one thing" (rules.md:38):
  - **history**: the store's private `history.jsonl` (commands/idea.md:20, :182) and git's history of the project;
  - **rules**: `.spark/rules.json`, the physics answers (commands/init.md:80), and `rules.md`, how agents work.
    init's note "write your rules for spark projects there" (the golden file) points a maker at the second while
    `rules.json` lists their nulls;
  - **spark project**: a project that uses spark, and spark itself (rules.md:1 against AGENTS.md);
  - **init**: `/spark:init`, and `git init`.

  E: pointers cited · supports D-q1, D-q3 (naming).
- **UX-6** · The git lines a maker reads use git's own vocabulary and give no next step. "a detached HEAD or a rebase
  that stopped", "Commit them first" with no how, and `<sha>` (project_setup.py:385-391). The flow's sentence says the
  same thing in plain words: "git keeps each change, so it can be taken back" (scripts/spark/flow/flow_codes.py:377).
  `UNHELD` folds four causes into one sentence: no git, no repository, no commit yet, an untracked brief
  (scripts/spark/records/project_commit.py:16-18). Neither the person nor an agent can tell whether to install git,
  make a repository or commit, and the line never offers to make one · E · supports D-q2, D-q3 (words).
- **UX-7** · The revert's yes is guarded only by a Claude Code feature, and its fallback is the one destructive step.
  - spark has four kinds of yes: a flash yes typed in the person's own terminal, where a relayed yes is refused
    (docs/guide/agents/never-assume.md:153-162); a replies file that holds `true` and counts for one run
    (docs/guide/agents/replies.md:62-65); `needs_yes` on a next step (scripts/spark/core/outcomes.py:114-118); and the
    revert, a chat yes plus Claude Code's permission prompt (commands/idea.md:78, :87).
  - An allow rule or auto mode removes that prompt (docs/guide/agents.md:73-75). MCP, LangGraph and a server have no
    such prompt at all.
  - `git restore --source=<sha>~1 -- .spark/project.json` (commands/idea.md:82-83) overwrites the person's uncommitted
    edits to the brief, and no yes of its own is written for it.

  E: pointers cited; that restore discards those edits is git's documented behaviour, H · supports D-q3, D-q5.
- **UX-8** · An agent outside Claude Code cannot read from data whether a write can be taken back.
  - init and the brief step are no Operation in the catalogue: listing `CATALOGUE` gives 50 ops and none is init.
  - `init_project.py` takes no `--json` (docs/guide/agents/json.md:298), so the sha and the reason for no commit exist
    only as English text.
  - The effect words are `reads runs board deletes writes asks fetches` (scripts/spark/core/operation.py:31). `writes`
    does not say where (the project, the store, the board) and does not say whether git holds it.
  - An MCP tool description or a LangGraph node built from the catalogue therefore cannot mark a tool as reversible.

  E: python listing of `spark.operation_catalogue.CATALOGUE` · supports D-q5.
- **UX-9** · The core's person-facing text assumes Claude is the interface. `git grep "Ask Claude" -- scripts/spark`
  finds 29 lines, flow_codes.py alone has 55 string lines that name Claude, and the line when no commit is made says
  "Ask Claude, and Claude puts the old lines back". The PO's message 6 says a hosted site's buttons "should go through
  the server, probably, not directly to Claude". There, and in LangGraph, these sentences are false · E: grep counts ·
  supports D-q5.
- **UX-10** · No moment picks the folder, nothing makes a new one, and nothing helps the person find a project again.
  - README.md:88 and docs/guide/commands.md:35 assume the person is already "in a project folder". commands/idea.md:25
    says "their project's folder, or a new one", then runs `--project .` (:34). A new folder elsewhere leaves the
    session in the wrong place.
  - init refuses a missing folder ("no directory at", project_setup.py:524). No `allowed-tools` entry makes one, and
    /spark:page needs `/add-dir` for a folder outside the session (commands/page.md:27-29).
  - The projects list holds 28 entries. 5 point to deleted session scratch folders, and names come from folder
    basenames (one-letter names among them). No command lists projects with their folders: the search for
    `--projects`, `list-projects` and `projects.json` in scripts and commands found none.

  E: pointers cited; projects.json read 2026-11-25 · supports D-q4.
- **UX-11** · The AGENTS.md section that init writes, the one file every agent tool reads, says nothing about git,
  commits, undo, the person's yes, or which files are spark's and which are the person's. It has three bullets on nulls
  and on injected text (data/agents-section.md:1-8). The undo rule lives only in commands/idea.md, which a non-Claude
  agent never reads. It links the guide on `main`, not the installed version (:4) · E · supports D-q1, D-q5.
- **UX-12** · Some of the PO's own gadget projects already run the team process. Project A has 44 PR merges and 26
  commit subjects with "PO". Project B has 7 commit subjects with "PO", commits with "(#12)", a GitHub remote, and its
  own GitHub issues read by the page (P1038 D19). rules.md:11-12 names a second lane ("sound") of gadget slices. So
  there are three readers, not two: spark's developers, the PO's lane projects, and a maker's project · E: `git log
  --oneline | grep` counts; that the rules caused the wording is H · supports D-q1.
- **UX-13** · A tracked `page.html` changes after every write that touches the project. The core hook writes it again
  on disk (P1038 D16), it is tracked (P1038 C18), and project B shows ` M page.html`. `sim/runs/` is gitignored (P1038
  C16), so deploys are outside git. A rule of one commit per write would fill history with page churn or leave the
  tree always dirty. Today's one-file commit avoids this only because it checks the brief alone
  (project_commit.py:76-86) · E for the facts; the consequence is H (this lens) · supports D-q3.
- **UX-14** · The dry run is already the moment before every write: "Run each `parts.py` write with `--dry-run` first"
  (scripts.md:83; commands/idea.md:21). It says what would be written. It never says whether the write can be taken
  back, or which part would not be (the store's holds, a flash) · E for the dry run; using it for this is H (this
  lens) · supports D-q3, D-q5.
- **UX-15** · Two rule sets would fix UX-1 and UX-5's "spark project", and keep the project's own AGENTS.md as the
  tool-neutral home (UX-11). They would cause new confusions:
  - which set the spark repo's session reads, when a dev session walks a project folder in scratch (the projects list
    shows 5 such);
  - which set applies to the PO's lane projects (UX-12);
  - two homes for one rule. "never fill a null" is already in both data/agents-section.md:6 and rules.md:92.

  H (this lens), from the pointers · supports D-q1.

## 2. Crude sketches (proposals, H)

### The folder pick, for a person (Claude Code or the CLI)

```
spark  > Where should this project live?
         1  a new folder:  ~/spark-projects/thirsty-plant        (default home, named from your goal)
         2  this folder:   ~/Downloads                         (! not empty: 214 files)
         3  another folder you name
you    > 1
spark  > made ~/spark-projects/thirsty-plant
         It keeps a history of every change spark makes, so you can take one back.  [git: yes]
         Find it again any time:  spark projects   (or /spark:projects)
```

```
spark projects
  thirsty-plant     ~/spark-projects/thirsty-plant      last change 25 Nov 18:40   next: pick parts
  door-bell       ~/spark-projects/door-bell     last change 20 Nov 09:12   next: wire it
  test-run        (folder gone: was in a session scratch folder)   forget it? y/N
```

### A write with its line, for a person

```
spark  > Pick: soil = capacitive-soil-v2, board = xiao-esp32-c6
         would write  needs.json, requirements.json      can be taken back: yes
         would hold   1 XIAO from your drawer            taken back with it: yes (spark releases it)
         Go?  y/N
you    > y
spark  > done. Saved as change 7 "picked parts for soil, board".  Undo: say "undo that"
```

Without a repository (the person chose "no history"):

```
spark  > done. Not saved as a change: this project keeps no history.
         Keep one from now on?  y/N
```

### An undo, for a person

```
you    > undo that
spark  > The last change was 7 "picked parts for soil, board" (25 Nov 18:40).
         Taking it back restores needs.json, requirements.json and releases 1 XIAO.
         Your own edit to firmware/main.py stays as it is.
         Take it back?  y/N
you    > y
spark  > taken back (change 8). To redo: say "redo that".
```

### The same for an agent (an envelope, any interface)

```json
{"op": "pick", "status": "ok",
 "data": {"written": ["needs.json", "requirements.json"], "held": [{"entry": "<key>", "count": 1}]},
 "change": {"id": "a1b2c3d", "files": [".spark/needs.json", "requirements.json"],
            "takes_back": {"op": "undo-change", "argv": ["--change", "a1b2c3d"], "needs_yes": true,
                           "also_releases": ["<key>"]}},
 "not_changed": null}
```

and, with no repository: `"change": null, "not_changed": {"code": "no_repository", "fix": {"op": "start-history",
"needs_yes": true}}`, a code for each of today's four causes, not one sentence.

### An MCP tool description (generated from the catalogue)

```
pick — picks a part for each need and holds what the person owns.
  effects: writes project, writes store (holds)
  reversible: yes, by undo-change with the person's yes
  ask the person before: the real run (run with dry_run first)
```

### A hosted site (message 6: the button goes to the server)

```
[ Pick these parts ]  -> server runs op "pick" -> page shows "Saved as change 7"   [ Undo ]
[ Undo ]              -> server shows the confirm text from takes_back, the person clicks "Take it back"
                         -> server runs op "undo-change" (the yes is the click on that page, by the signed-in owner)
[ Flash the board ]   -> not on the site: the board is on the person's USB; the yes stays in their terminal
```

## 3. What I could not check, and why

- That Claude Code really asks before `git revert` under commands/idea.md's `allowed-tools`, and how nested
  `CLAUDE.md` and `AGENTS.md` files load when the session starts in a parent folder. No web, and no Claude Code run.
- MCP's tool annotations (read-only and destructive hints), LangGraph's human-in-the-loop interrupt, and what
  Anthropic recommends for CLAUDE.md and memory. These are model knowledge (H) and the researcher's job.
- How a maker who has never used git reads any of these lines. No maker can be reached (brief: users none beyond the
  PO).
- Whether the "PO" wording and the PRs in projects A and B came from rules.md or from the PO's own choice.
- My count of the listed projects that exist (23: 9 with their own repository, 14 without) differs from the brief's
  (8 and 15). The cause is not checked: perhaps another date or another set.
- The P1113 lens-ux report and the canvas files. Only finding.md was read.

## 4. Questions for the decider

- Does a gadget project's agent read the spark team's rules.md at all, or a separate project rules file, and which do
  your lane projects (UX-12) read? · decides D-q1 and the target of init's `CLAUDE.local.md` link.
- What does a maker see of git: its name and words, spark's own words ("change", "take back") with git hidden, or
  history as an opt-in? · decides D-q2 and D-q3's vocabulary (UX-5, UX-6).
- Does "undo" take back the store's side of a write (holds, drawer), or only the project's files? · decides D-q3's
  scope (UX-3).
- Who makes the repository and its first commit: init always, init after a yes, or the person? · decides D-q2, D-q4
  (UX-2).
- Does spark have a default home for projects and a command that lists them? · decides D-q4 (UX-10).
- Is a revert, which is itself reversible, a chat-level yes on every interface, or does it need the stronger yes that
  a flash needs? And who may run it when "spark's own code never runs it" (D-e) and a server presses the button? ·
  decides D-q3, D-q5 (UX-7).
- Does the core's text name "Claude", or a neutral word that each interface fills in? · decides D-q5 (UX-9).
- Does spark ever push a person's project? rules.md:51 says push; project_commit.py:5 says never · decides D-q3.

## 5. Searches

None.
