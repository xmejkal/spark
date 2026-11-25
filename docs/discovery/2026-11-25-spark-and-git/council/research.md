# Research: existing practice outside spark (spark and git)

This is the researcher's report for the discovery "spark and git: whose rules, which repository, which folder". It
answers six questions from primary documents. All pages were read on 2026-11-25.

Tags: **E** is evidence, read at the URL on that date. **H** is a hypothesis or model knowledge, with its origin.
**D** is a decision on record. The word "unknown" marks a gap. Quotes are one short line per source at most. Nothing
here decides anything.

## 1. Findings

Most important first. The last column names the spark decisions that the finding bears on. **R** is rules per
audience. **P** is a project's repository. **G** is spark's use of git. **F** is who makes the folder. **I** is the
interfaces (CLI, code, MCP, hosted).

| ID | Claim | Tag | Pointer | Supports |
|---|---|---|---|---|
| RES-1 | Claude Code (v2.1.277 or later) reads `AGENTS.md` directly. By default it reads it only with no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in the working folder or above it. A `CLAUDE.local.md` counts. So a `CLAUDE.local.md` stops the default reading of `AGENTS.md`. The user can change this with the Project instructions setting `claude-md-and-agents-md`. Claude Code reads that setting only from user or managed settings, not from project or local settings. | E | https://code.claude.com/docs/en/memory#agents-md | R, F |
| RES-2 | The documented way to keep one file for all tools is a `CLAUDE.md` that holds `@AGENTS.md`, with Claude-specific lines below it. The import never makes Claude read `AGENTS.md` twice. A symlink from `CLAUDE.md` to `AGENTS.md` also works. But the symlink breaks on Windows clones, and the Edit tool refuses to write through it. | E | https://code.claude.com/docs/en/memory#share-one-file-with-other-coding-tools | R |
| RES-3 | Anthropic names four memory scopes. Managed policy has an OS path. User is `~/.claude/CLAUDE.md`. Project is `./CLAUDE.md` or `./.claude/CLAUDE.md`, shared through source control. Local is `./CLAUDE.local.md`, for personal preferences in one project, and the docs say to add it to `.gitignore`. `CLAUDE.local.md` is current, not deprecated. Claude Code joins all found files, root first. In one folder, `CLAUDE.local.md` comes after `CLAUDE.md`. | E | https://code.claude.com/docs/en/memory | R, P |
| RES-4 | A gitignored `CLAUDE.local.md` exists only in the worktree where it was made. To share personal rules across worktrees, the docs say to import a file from the home folder. An import outside the working folder starts a one-time approval dialog per project. A decline turns those imports off for good. User-scope files (`~/.claude/CLAUDE.md`, `~/.claude/rules/`) load their imports with no dialog. Cowork sessions are the exception: they skip such imports. | E | https://code.claude.com/docs/en/memory#import-additional-files | R, P, F |
| RES-5 | A plugin cannot ship project instructions as a file. A `CLAUDE.md` at the plugin root does not load as context, and `claude plugin validate` warns about it. The docs say to put instructions that load into context in a skill. The plugin parts are skills, commands (skills are preferred for new plugins), agents, hooks, MCP and LSP servers, output styles, monitors and `bin/`. | E | https://code.claude.com/docs/en/plugins-reference#standard-layout | R, I |
| RES-6 | Plugins get three path variables. `${CLAUDE_PLUGIN_ROOT}` is the installed version. It changes on each update, and the docs say not to keep state there. `${CLAUDE_PLUGIN_DATA}` is `~/.claude/plugins/data/<id>/`. It stays across updates and goes away on uninstall by default. `${CLAUDE_PROJECT_DIR}` is the project root. Commands that Claude runs through the Bash tool do not get these variables. Skill and agent text gets them as inline text. | E | https://code.claude.com/docs/en/plugins-reference#environment-variables | F, I, G |
| RES-7 | No Anthropic page that was read says whether or how a plugin writes instruction files (CLAUDE.md, AGENTS.md, rules) into a user's project. | unknown | The memory, plugins-reference and best-practices pages | R, F |
| RES-8 | Checkpoints (`/rewind`, also `/undo`) copy the files that Claude edits with its own file tools, before each prompt. Claude Code keeps the 100 latest checkpoints. A sweep removes them about 30 days after the session last saved one. Checkpoints do not cover files that only Bash changed, edits by background subagents, outside edits or symlinks. The page sends lasting history to Git: "Not a replacement for version control". | E | https://code.claude.com/docs/en/checkpointing | G |
| RES-9 | In auto mode, a classifier blocks some git actions by default. It blocks force push. It blocks commands that it presumes discard uncommitted work, such as `git reset --hard`, `git restore .` and `git clean -fd`. It blocks `git commit --amend` on a commit from an earlier session or a pushed commit. It blocks changes to the push target and merges of unapproved PRs. It allows a push to any branch of the current repository, the default branch too. To make a push need a person, add `permissions.ask` rules. The docs say auto mode does not guarantee safety. | E | https://code.claude.com/docs/en/permission-modes (first 100,000 of 121,905 characters) | G |
| RES-10 | The best-practices page puts a rule with zero exceptions in a hook, a deny rule or a managed setting. CLAUDE.md is for guidance, and Claude can decide that a guideline does not apply. Keep CLAUDE.md short, under 200 lines. Personal preferences go in `CLAUDE.local.md`, gitignored. One example ask rule is `Bash(git push *)`. | E | https://code.claude.com/docs/en/best-practices | R, G |
| RES-11 | Worktrees need a git repository with at least one commit. In a folder with no git, the error says to run `git init` and make a first commit. Another VCS needs a `WorktreeCreate` hook. Claude Code makes worktrees under `.claude/worktrees/<name>/`, on the branch `worktree-<name>`. On exit it removes a clean worktree and asks about one with work in it. The docs say to add `.claude/worktrees/` to `.gitignore`. | E | https://code.claude.com/docs/en/worktrees | G, P, F |
| RES-12 | In the Agent SDK, the `cwd` option (or the process folder) sets where project inputs come from. With no `settingSources`, the SDK reads user, project and local sources, as the CLI does. So CLAUDE.md, CLAUDE.local.md and `.claude/` load. An empty list turns them off. Managed settings, `~/.claude.json` and auto memory load in all cases. The docs warn against the defaults for multi-tenant isolation. | E | https://code.claude.com/docs/en/agent-sdk/claude-code-features | I, F |
| RES-13 | MCP revision 2026-07-28 deprecates Roots, with Sampling and Logging. New implementations are told not to add them. The suggested change: pass folders or files as tool parameters, as resource URIs or in the server settings. This revision also removes the `initialize` handshake and `notifications/roots/list_changed`. Requests from the server, such as `roots/list`, move to a multi round-trip pattern. A deprecated feature stays for at least twelve months. | E | https://modelcontextprotocol.io/specification/2026-07-28/changelog | I |
| RES-14 | MCP 2025-06-18 Roots: a client with roots support declares the capability. Each root URI is a `file://` URI. Clients are told to get the user's consent before they show roots to servers. Servers are told to stay inside root boundaries and to check paths against the roots. The page says nothing about a server that writes files. | E | https://modelcontextprotocol.io/specification/2025-06-18/client/roots | I |
| RES-15 | The reference MCP filesystem server gets its allowed folders as command-line arguments. Its README calls this "the only method that works on every protocol version". By default, roots from a client replace those folders. With `--confine-roots`, roots can only make the list smaller. `--read-only` and `--read-only-dir` remove or limit the write tools (`write_file`, `edit_file`, `move_file` and others). Roots cannot lift those limits. | E | https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem | I, F |
| RES-16 | The AGENTS.md site calls the file "a README for agents". The Agentic AI Foundation under the Linux Foundation keeps it. The site lists about 23 tools, among them Codex, Jules, Cursor, Gemini CLI, GitHub Copilot coding agent, VS Code, Zed, Aider, Devin and Windsurf. Claude Code is not on that list. With nested files, the nearest file wins. Chat prompts override all files. The file has no required fields. | E | https://agents.md/ | R |
| RES-17 | Cursor reads `AGENTS.md` at the root and in subfolders. It also has project rules in `.cursor/rules` (`.mdc` files). User rules and team rules sit outside the repository. The docs say to check project rules into git. | E | https://cursor.com/docs/context/rules | R, P |
| RES-18 | Gemini CLI reads a global `~/.gemini/GEMINI.md`. Then it reads GEMINI.md files in workspace folders and their parents. It reads subfolder files only as it needs them. The setting `context.fileName` can add `AGENTS.md`. The page also says that Antigravity CLI replaced Gemini CLI on 2026-06-18 for unpaid and Google One users. | E | https://geminicli.com/docs/cli/gemini-md/ | R |
| RES-19 | Claude Code's `/init` (with `CLAUDE_CODE_NEW_INIT=1`) reads the files of other tools. Among them are Cursor rules, `.github/copilot-instructions.md`, `AGENTS.md`, `.windsurf/rules/` and `.clinerules`. `/import` adds a one-time copy of such files to CLAUDE.md. | E | https://code.claude.com/docs/en/memory | R |
| RES-20 | LangGraph keeps the state of each thread through a checkpointer. The checkpointers are `InMemorySaver`, `SqliteSaver` (for development) and `PostgresSaver`. A separate store keeps memory across threads. The persistence page names no workspace and no files on disk. | E | https://docs.langchain.com/oss/python/langgraph/persistence | G, I |
| RES-21 | Deep Agents (LangChain) choose a workspace through a backend. The default backend keeps files in graph state, through the checkpointer. `FilesystemBackend(root_dir=...)` writes to the real disk. Only `virtual_mode=True` keeps paths inside the root. Other backends write to a store, or as commits in a LangSmith Context Hub repository. The docs warn that real-disk changes are permanent. They advise human review and a sandbox in production. | E | https://docs.langchain.com/oss/python/deepagents/backends | G, F, I |
| RES-22 | Replit Agent makes checkpoints at milestones. A rollback restores the code, the agent's chat and the environment settings. It restores the development database only on request. "Each checkpoint creates a corresponding Git commit." The Git pane shows checkpoints as commits. New changes after a rollback turn later checkpoints into a separate branch. | E | https://docs.replit.com/replitai/checkpoints-and-rollbacks | G, I |
| RES-23 | Lovable saves a version for each change. It has no save button. The person sees a History panel with previews, diffs, bookmarks and a revert of a full version. A revert keeps the chat and does not roll back database data. The page does not say whether git is underneath. | E | https://docs.lovable.dev/features/projects/history | G, I |
| RES-24 | Lovable's GitHub link syncs one branch, both ways, with one repository. Lovable makes that repository in the account that the person picks. It is private by default. On disconnect, the repository and its history stay on GitHub. | E | https://docs.lovable.dev/integrations/github | P, I |
| RES-25 | Wokwi's FAQ: a project saved by a signed-out person belongs to that device and browser. A signed-in person sees saved projects on the dashboard on any device. The pages read describe no version history and no undo. Offline work goes through the VS Code extension. | E | https://docs.wokwi.com/faq | I |
| RES-26 | In Wokwi for VS Code, a project is two files at the root of the person's own project folder: `wokwi.toml` and `diagram.json`. Wokwi does not compile. It runs the built firmware that the toml file points to. The page gives no advice on git for these files. | E | https://docs.wokwi.com/vscode/project-config | P, F |
| RES-27 | In the sessions this researcher saw, Claude Code's own tool text says to commit or push only on the user's request. No public docs page that was read states this rule. | H (this session's tool descriptions, not a docs page) | unknown | G |
| RES-28 | Hosted tools keep history in one of two ways. Some put git underneath and show it in their own words (Replit: checkpoints as commits). Others keep their own version list and offer git only as a sync (Lovable). Wokwi online shows no history on the pages read. | H (from RES-22 to RES-25) | unknown | G, I |

## 2. What each source means for spark's five decisions

All of this part is **H**. These are readings of the findings, not decisions.

**Rules per audience.**
- Anthropic's split matches three audiences. The person has `~/.claude/CLAUDE.md` and `~/.claude/rules/`. The
  project, shared with others, has `CLAUDE.md` or `AGENTS.md`, committed. The person in one project has
  `CLAUDE.local.md`, gitignored (RES-3).
- Suppose spark writes its rules as `CLAUDE.local.md` beside an `AGENTS.md`. Then by default Claude Code stops
  reading the `AGENTS.md` (RES-1). A committed `CLAUDE.md` with `@AGENTS.md` is the documented bridge (RES-2). What
  `/spark:init` writes today was not checked (part 3).
- Rules that reach a project through an import from the home folder start an approval dialog once per project. A
  decline is permanent (RES-4). Rules in `~/.claude/rules/` need no approval. But they apply to all projects on the
  machine, spark projects and others.
- A plugin has no file of its own that loads as project context at all times (RES-5). So spark's standing rules can
  live in a skill, in a hook, or in files written into the project (RES-7).
- Anthropic's advice puts rules with no exceptions in hooks or deny rules (RES-10). Two examples are "never commit a
  home path" and "never force-push".
- `AGENTS.md` is read by Cursor, Codex, Gemini CLI (through a setting) and about twenty other tools (RES-16 to
  RES-18). Each tool also keeps its own user layer outside the repository. Examples are Cursor user rules,
  `~/.gemini/GEMINI.md` and `~/.claude/CLAUDE.md`. So the person's own rules have no tool-neutral home.

**A project's repository.**
- Anthropic's model assumes that the project folder is a repository that the person owns. The project CLAUDE.md is
  shared through source control, and local files are gitignored (RES-3).
- Lovable makes the repository in the person's account and leaves it with them on disconnect (RES-24). Wokwi for VS
  Code puts its files in the person's own folder and says nothing about git (RES-26). Neither tool takes ownership of
  the project's history.

**Spark's use of git.**
- Anthropic treats checkpoints as session undo and git as the lasting history (RES-8).
- Checkpoints do not cover Bash changes. Spark's scripts run through Bash. So `/rewind` does not restore a file that a
  spark script wrote, unless Claude edited that file earlier in the session (RES-8).
- Claude Code itself guards destructive git actions in auto mode. For a push that needs a person, it points to
  `permissions.ask` rules (RES-9). Spark does not need to repeat those guards in its text. Hooks of its own are an
  open choice.
- Claude Code uses worktrees for parallel sessions and isolated subagents. Worktrees need git and a first commit
  (RES-11). A project folder with no git loses that feature.
- Replit shows that git history can sit under a word the person knows, "checkpoint" (RES-22).

**Who makes the folder.**
- Claude Code works in any folder, also one with no code. Its project root is the launch folder (RES-6, RES-12).
  Neither Claude Code nor the Agent SDK makes a project folder. The person or the caller picks `cwd`.
- `${CLAUDE_PLUGIN_DATA}` is the plugin's own lasting place, and uninstall removes it by default (RES-6). It is not a
  home for a person's projects.
- Deep Agents shows the pattern of code frameworks. The caller gives a root folder, and confinement is opt-in
  (RES-21).

**Interfaces (CLI, code, MCP, hosted).**
- MCP moves away from Roots. A later spark MCP server can take the project folder as a tool parameter or a server
  setting, not from roots (RES-13, RES-15). Roots still work in clients of 2025 during the twelve-month window.
- The Agent SDK loads the same CLAUDE.md, local and user files as the CLI, unless the caller narrows `settingSources`
  (RES-12). So rules written for Claude Code also reach an SDK frontend.
- LangGraph keeps run state in a checkpointer, apart from any files (RES-20). For a code frontend, the history of a
  run and the git history of a project are two separate things.
- Hosted tools show history as a list of versions with one-click revert. None of the pages read shows git words to
  the person (RES-22, RES-23, RES-25).

## 3. What could not be checked, and why

- What `/spark:init` writes today (`CLAUDE.local.md`, `AGENTS.md`, `CLAUDE.md`, an import). The brief forbids
  reading the repositories. This tells whether RES-1 already affects spark projects.
- Anthropic advice on a plugin that writes instruction files into a user's project (RES-7). The pages read had none.
  For time, the plugin "components" and "create" pages and the hooks page (`SessionStart` context) were not read.
- A public Claude Code docs line on "commit only on request" (RES-27). The best-practices and common-workflows
  pages do not have one.
- The last 21,905 characters of the permission-modes page. The fetch read only the first 100,000.
- The 2026-07-28 MCP Roots page and the multi round-trip page. Only the changelog was read. Whether Claude Code, as
  an MCP client, still sends roots was not checked.
- LangGraph time travel, replay and fork. The persistence page does not cover them.
- Wokwi's online version history, forks and undo. Two searches found no official page. Only the FAQ and the VS Code
  project page were read.
- Whether Lovable's own history uses git. Neither Lovable page says.
- Per-project git in other hosted electronics tools (Flux, EasyEDA, Tinkercad). A search result named Flux's
  "History and Version Control" page, which was not read.
- The full list of supported agents on agents.md. The site links to it, and it was not read.

## 4. Questions for the decider

| Question | What it decides |
|---|---|
| Do a spark project's rules for Claude go in `CLAUDE.local.md` (personal, gitignored), in a committed `CLAUDE.md` that imports `AGENTS.md`, or in both? | Whether Claude Code still reads the project's `AGENTS.md` by default (RES-1, RES-2), and whether other tools see the same rules. |
| How do the person's standing rules reach each spark project: a home-folder import, `~/.claude/rules/`, or a spark skill or hook? | Whether each new project shows an approval dialog (RES-4), whether the rules reach projects that are not spark's, and whether they work in worktrees. |
| Which rules hold with no exceptions, and do those become hooks or deny rules instead of text? | Anthropic's split between guidance and enforcement (RES-10, RES-9). |
| Does each spark project start as a git repository with a first commit? | Whether worktrees, undo through git, and recovery of Bash changes work in that project (RES-8, RES-11). |
| Does spark ever commit in the person's project, or does it only leave files for the person or the conversation to commit? | Spark's use of git, and its fit with "commit only on request" (RES-27) and with auto mode's defaults (RES-9). |
| Who makes the project folder, and where: the person, `/spark:init`, or a spark CLI with a path argument? | Who owns the folder and its history, and what an SDK, MCP or hosted frontend gets as input (RES-12, RES-13, RES-21). |
| For a later MCP server, is the project folder a tool parameter, a server setting, or both? | Fit with MCP 2026-07-28, which deprecates Roots (RES-13, RES-15). |
| For a hosted spark, does the person see history as spark's own versions, as git commits, or as a git repository in their own account? | The history model of a hosted interface (RES-22 to RES-24, RES-28). |

## 5. Searches

The limit was ten searches. Three were run. The page fetches follow the table.

| Query, verbatim | Question served | Used |
|---|---|---|
| `Wokwi project version history undo save project docs` | (6) hosted tools | Not used. It returned no Wokwi page. It named Lovable's history page, which was then fetched. |
| `site:docs.wokwi.com save project share link versions` | (6) hosted tools | Used. It led to https://docs.wokwi.com/faq. |
| `Gemini CLI GEMINI.md context file name AGENTS.md configuration docs` | (3) tool-neutral conventions | Used. It led to https://geminicli.com/docs/cli/gemini-md/. |

## 6. Pages fetched (not searches)

Pages fetched directly, all on 2026-11-25:

- (1) https://code.claude.com/docs/en/memory
- (1) https://code.claude.com/docs/en/plugins-reference
- (1, 2) https://code.claude.com/docs/en/best-practices
- (2) https://code.claude.com/docs/en/checkpointing
- (2) https://code.claude.com/docs/en/worktrees
- (2) https://code.claude.com/docs/en/common-workflows (no git rules beyond PR creation and worktrees)
- (2) https://code.claude.com/docs/en/permission-modes
- (2) https://code.claude.com/docs/en/agent-sdk/overview (it points to the next page)
- (2) https://code.claude.com/docs/en/agent-sdk/claude-code-features
- (3) https://agents.md/
- (3) https://cursor.com/docs/context/rules
- (4) https://modelcontextprotocol.io/specification/2025-06-18/client/roots
- (4) https://modelcontextprotocol.io/specification/2026-07-28/changelog
- (4) https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem
- (5) https://docs.langchain.com/oss/python/langgraph/persistence
- (5) https://docs.langchain.com/oss/python/deepagents/backends
- (6) https://docs.replit.com/replitai/checkpoints-and-rollbacks
- (6) https://docs.lovable.dev/features/projects/history
- (6) https://docs.lovable.dev/integrations/github
- (6) https://docs.wokwi.com/faq
- (6) https://docs.wokwi.com/vscode/project-config
