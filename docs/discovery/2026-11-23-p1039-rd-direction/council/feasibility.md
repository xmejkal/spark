# P1039 council: the Feasibility lens

Run 2026-11-23, Opus, read-only on the tree, branch p1039-rd-discovery at e0c0dc77. Every count below was made with a
command quoted beside it. Commands ran from the repository root with `SPARK_HOME=~/.local/share/spark` inline. Scripts
ran only on a copy of `tests/data/breadboard/walk-c6` in a scratch folder (deleted after the run). `git status --short`
was empty after the run.

## 1. Findings

Format: FE-n · claim · tag · pointer · supports only.

### What matters most

- FE-1 · spark-main's reading on #1522 (16:0x CET) is wrong on one point and right on another. Wrong: `tools/check_docs.py`
  does not check that commands, skills and agent pages name only scripts and flags that exist. Its `missing_names` and
  `missing_flags` run only on `doc_files()`, which are README.md, AGENTS.md and `docs/guide/**/*.md`. For
  commands/skills/agents it checks only that a cited `docs/...md` path exists (`stale_doc_paths`) and that each one is
  listed (`unlisted`). Commands are guarded elsewhere. `tests/test_routes.py:88-104` checks that every script in a
  command's `allowed-tools` exists and can be run. It does not check flags. Right: when a new flag, JSON key or code goes untaught, no test fails. There is one reverse guard, at the level of whole scripts only:
  when no page that routes a user names a script, `tests/test_orphans.py:73-80` fails. That test counts README,
  AGENTS.md and every `docs/guide` page as routes, so a script that only a human page names passes. This is how
  `cost.py` passes. · E · tools/check_docs.py:274-287 (`problems`), :61-64 (`doc_files`), :110-120 (`missing_names`), tests/test_orphans.py:28-37, :73-80, tests/test_routes.py:86-104 · supports only: what the guards read today, not how often a gap has hurt an agent.

- FE-2 · How much agent text names the surface, counted with three scratch scripts. "Agent text" here means
  commands/*.md, skills/*/SKILL.md, skills/*/references/*.md, agents/*.md, docs/guide/agents.md and
  docs/guide/agents/*.md.
  - **Scripts:** 26 of 27 `scripts/*.py` are named somewhere in agent text. Only `cost.py` is not, and it is named only
    in human guide pages (map.md, developing.md, patterns-and-names.md, how-it-works.md, research-cost.md). The prompts
    alone (commands, skills, agents) name 20 of 27. Not named there: check_bom, check_physics, check_vendor_pins,
    compare_design, cost, import_firmware, reach.
  - **Flags:** the 27 scripts' `--help`, plus the three `flow.py` verbs, list 192 flags. 13 of 192 appear nowhere in
    agent text: assign_pins --id, boards --id/--path/--paths, check_vendor_pins --repo, flash_image --config/--output,
    import_firmware --timeout, parts --signals/--view, reach --cure-first, run_scenario --timeout-ms, tools --personal.
  - **JSON keys:** the 51 named Operation classes declare 106 distinct `data_keys` (153 op-key pairs). 14 of 106 appear
    nowhere in agent text: board_was, dangling, drafts, from_store, needs_picked, no_driver, no_receiver, no_supply,
    options, pages_read, shelf_copy, unplaced, vendor_order, would_fetch. 26 of 106 never appear in code form (a
    backtick, `data.` or a quote).
  - **Codes:** 135 `Code` values exist in `scripts/spark/**`. 91 of 135 appear nowhere in agent text, and 125 of 135
    appear in no command, skill or agent file.

  · E · method: a regex match of each name as a word in the concatenated agent text, flags read off `python3 scripts/X.py --help` (only cost.py exits 2, because it has no argparse), keys from `Operation.data_keys` and codes from `isinstance(v, Code)` over `pkgutil.walk_packages(spark)` · supports only: a lower bound on gaps. See FE-3 for what the count cannot show.

- FE-3 · What the count in FE-2 cannot show.
  1. A name that is present is not the same as a name that is taught. A word that matches in any page counts as
     covered. This is true also on a line about another script. A stricter rule counts a flag only on a line that names
     its script. It gives 57 of 192. flow.py's EPILOG names other scripts' flags, so that number is noisy.
  2. 11 of 51 named Operations declare no `data_keys`: build-board, check-grant, deploy, disallow-direct-flashing,
     issue-grant, list-boards, live, look, needs-drop, reach, research-part. The 15 scripts off the core declare none
     either. Their keys are invisible to any count, so the real key gap is larger than 14.
  3. A Code carries its own `meaning` and `fix`, so an agent can act on a code that no page names. A missing name is
     therefore not, by itself, a failure (scripts/spark/core/codes.py:9-25).
  4. Nothing shows whether an agent that reads the text succeeds. That needs an eval (FE-16).

  · E · the same commands as FE-2, scripts/spark/core/codes.py · supports only: the limits of the count.

- FE-4 · The plain-script half: 27 scripts in `scripts/`. 19 of 27 take `--json`: 12 through the core's `run_cli`
  (bench, boards, check_all, check_spine, deploy, flow, grant, live, look, parts, reach, research) and 7 with their own
  flag (assign_pins, check_footprints, check_physics, check_vendor_pins, compare_design, emit_footprint,
  import_firmware). 8 of 27 take no `--json`: breadboard, check_bom, cost, emit_board, flash_image, init_project,
  run_scenario, tools. Four of these eight are journey steps: init, the image, the scenario, the tools. Their human text
  is the only answer an agent outside Claude Code gets from them. The hand-written list in docs/guide/agents/json.md:295-298
  agrees with this count (19). No test ties that list to the code. · E · `for f in scripts/*.py, do grep -q run_cli $f || grep -qE "['\"]--json['\"]" $f ...` → "19 yes", 8 NO, docs/guide/agents/json.md:295 · supports only: which scripts any harness can drive by JSON today.

- FE-5 · The Claude-only half.
  - 9 commands, 3 skills and 4 agents. 10 of 12 command and skill files use Claude Code's `allowed-tools` with
    `${CLAUDE_PLUGIN_ROOT}`. 12 of 16 prompt files name `${CLAUDE_PLUGIN_ROOT}`.
  - 4 of 4 agents carry `model:` and `tools:` frontmatter in Claude Code's format: opus ×2, sonnet, haiku.
  - 3 files name MCP tools by Claude Code's `mcp__…` names: page.md (claude-artifacts) and two agents (jlcpcb,
    espressif-docs, declared in `.mcp.json`).
  - 2 commands name the Artifact (build.md, page.md). /spark:page is Claude-only by design: it publishes through
    `mcp__claude-artifacts__*`.
  - Subagent launches sit in 3 files: research.md launches part-finder and datasheet-reader. identify.md and
    research.md launch parts-researcher. spark-review launches design-reviewer "in a single message so they run at once".
  - 0 of 16 files name AskUserQuestion or SendMessage. There is no `hooks/` folder in the plugin.

  · E · `grep -l -- "$t" commands/*.md agents/*.md skills/*/SKILL.md skills/*/references/*.md` for each term, .claude-plugin/plugin.json, .mcp.json · supports only: what needs an adapter or a rewrite in another harness.

- FE-6 · The person's yes for a network operation is given by Claude Code's permission prompt, not by spark. Five
  network operations are left off every `allowed-tools` list: `parts.py --fetch` and `--sources`, `tools.py --install`
  and `--on`, and `check_vendor_pins.py` without `--offline`. The guide gives the reason: "so Claude Code asks the
  person before any of them runs, and their answer is the yes". A harness without that prompt runs them unasked. Deploy
  and grant already have consent in the core (the ASKS effect and `make_consent`). The network operations do not. This is the largest safety cost of running
  elsewhere. · E · docs/guide/agents.md:71-76, tests/test_routes.py:493-519, scripts/spark/core/operation.py:27-31 · supports only: that the gate is the harness's, not how other harnesses gate tools.

- FE-7 · Product logic that lives in Markdown, not in the core. Examples read:
  - idea.md's S step (lines 23-70) holds the order of the step, the rule of "at most three questions, one at a time",
    the wording rules that make a need match a board's own parts, and the double write (`--dry-run` first, then the
    write).
  - The verbs list is said twice: in code (scripts/spark/records/record_kind.py:37) and in idea.md:38.
  - The architect's finding names build.md's hand table of refusals and the next step written in five places.
  - The commands are large: build.md is 404 lines and 6,510 words and names 11 distinct scripts. idea.md names
    scripts 25 times. `--dry-run` appears 12 times in idea.md and 4 in drawer.md.
  - Only 2 pages (commands/deploy.md and docs/guide/agents/scripts.md) carry blocks that `tools/doc_blocks.py`
    renders from an Operation.

  · E · commands/idea.md:23-70, `grep -oE "scripts/[a-z_]+\.py"` per file, `grep -c -- "--dry-run" commands/*.md`, `grep -c "spark:operation\|spark:stages"`, ~/finding-core-gaps-2026-11-23.md in the store · supports only: where logic sits, not how much of it an agent in another harness gets wrong.

- FE-8 · The core's own output names Claude and Claude Code commands. 114 lines in 29 .py files under `scripts/`
  contain the word "Claude", and 42 .py files contain `/spark:`. The flow's roles are `you`, `claude`, `your terminal`
  (scripts/spark/flow/flow_codes.py:17). `flow.py show` prints, for example, "Ask Claude in the chat to build the board"
  and "Ask Claude to look at the board first (/spark:deploy)". `tools.py` runs `claude mcp add/remove`
  (scripts/spark/records/tool_finder.py:393, tool_choices.py:43). So the "plain" scripts are not harness-neutral in
  their words. Piece 6 of the core finding ("sentences say the job, each interface adds its own how") is the piece that
  changes this. · E · `grep -rnw Claude scripts --include="*.py" | wc -l` → 114, `grep -rl "/spark:" scripts | grep .py$ | wc -l` → 42, a run of `flow.py show` on the fixture copy · supports only: the size of a wording pass.

### The core and the order of work

- FE-9 · How far the one core is:
  - 51 named Operation classes, 21 of them direct subclasses of `Operation`.
  - 12 of 27 scripts run through `run_cli`. The 2026-11-23 finding counted 11.
  - The envelope has 11 top keys: envelope, tool, op, status, data, problems, unchecked, next, truncated, notes,
    assumptions.
  - `Operation.input_schema()` and `output_schema()` exist (P605), but no MCP server of spark's own exists. Only the
    core and tests call `input_schema`.
  - P1030 (#1510) is closed: `flow.py show --json` now fills `next` with a step (op build-board, argv, effects,
    needs_yes, env). The finding's "next: []" is outdated.
  - Open: P1034 #1517 (next step for firmware, simulate, look, deploy), P1035 #1518 (one hook adds the now step after a
    write), P1036 #1519 (one Storage under the Stores), P1033 #1515, P417 #545 (a LangGraph-node and MCP-tool spike).

  · E · `grep -rnE "^class \w+\((\w+\.)?Operation\)" scripts/spark | wc -l` → 21, Operation import scan → 51 of 53, run of `flow.py show --json` on the fixture copy, `gh issue list --search "<P> in:title"`, `grep -rln input_schema scripts tests` · supports only: the state on 2026-11-23.

- FE-10 · The event seam is too narrow for the PO's streaming rule. `Event` has 2 kinds, LINE and BEGIN. There is no
  finding, done or next-step event, and BEGIN has no end. There is one Reporter, `TerminalReporter`, and the code has no
  async. 7 modules outside core report events: 5 in bench and 2 in research. The rule names four events: a step started, a step
  done, a finding and the next step. LangGraph, a live page and an SSE MCP server read them. Each of these consumers
  needs new event kinds and a Reporter that is not the terminal's first. · E · scripts/spark/core/events.py:1-75, `grep -rlE "outside\.report|Event\.line|Event\.begin" scripts/spark` → 9 files (2 in core), #1105 comments 12:54 and 12:55 CET · supports only: what exists, the design of the stream is open.

- FE-11 · Which core piece each direction needs first. All of these are H, the lens's reading of the code against the
  core finding's build order (~/finding-core-gaps-2026-11-23.md in the store).
  - **Other harnesses** (J2) need, in order:
    1. Consent in the core for the network operations (FE-6).
    2. The four journey CLIs onto the core (piece 5), so that each step answers in JSON (FE-4).
    3. Neutral sentences (piece 6, FE-8).
    4. A catalogue (piece 4) that another harness or an MCP server lists.
  - **A local model** needs pieces 1 to 3 (one next step, every phase's step, the hook). They shrink each command to
    "run it, read next, relay the lines", so a small model reads less (FE-13).
  - **Evaluation** (J3) needs nothing from the core to start, because the hook and tests exist. An agent eval needs a
    harness that can be scripted: `claude -p` is already assumed in scripts/spark/build/ai_files.py:9. It also needs a
    transcript reader. `cost.py` and `spark/sourcing/run_cost.py` read one.
  - **The agent-knowledge guard** (J4) needs the catalogue (piece 4) and help rendered from the declaration (piece 7).
    A guard can only compare against keys that are declared, and 11 Operations and 15 scripts declare none (FE-3).
  - **A live page or an SSE MCP server** (J5) needs FE-10's event kinds and a second Reporter, after pieces 1 to 3.

  · H · this lens, from the finding's build order and FE-3 to FE-10 · supports only: an order to test, not a plan.

- FE-12 · What each direction touches, in rough size. All of these are H, the lens's own estimate, unmeasured.
  - **Run in another harness, scripts only:** about 0 code. The scripts run with `CLAUDE_PLUGIN_ROOT` set by hand
    (docs/guide/agents/scripts.md:7-14). But "following a command page outside Claude Code was not tried"
    (docs/guide/agents.md:79-81).
  - **Run the commands in another harness:** touches all 9 command files, the 4 agent files, `.mcp.json`, and FE-6's
    consent.
  - **A spark MCP server:** piece 8 of the core finding, size M, after the CLI is whole.
  - **A local model:** no code. It is a test of FE-13's sizes against a model.
  - **The agent-knowledge guard:** one test over `data_keys`, `--help` flags and Codes against agent text, of the kind
    this lens ran (FE-2), plus a decision on what counts as "taught".

  · H · this lens, doc pointers E as given · supports only: an order of magnitude.

### A local model and model choice

- FE-13 · What a driving model must read and handle. All sizes are E. The token figures assume 4 characters per token
  (H).
  - **Prompt text:** the 16 prompt files are 177,003 bytes and 28,511 words, about 44k tokens. The skills' references
    add 45,583 bytes. The agent guides are docs/guide/agents.md (13,042 bytes) plus 9 pages beside it (206,662 bytes):
    json.md is 58,299 and scripts.md 43,747.
  - **The three journey commands:** idea.md (22,325) + build.md (41,022) + deploy.md (19,930) + agents.md (13,042) is
    about 96 KB, about 24k tokens, before any answer.
  - **One --json answer** is small:
    - flow.py show: 3,199 bytes
    - boards.py --list: 443 bytes
    - parts.py --catalog: 2,651 bytes
    - the golden answers (tests/golden*): 1.3 to 5.9 KB. The largest is assign-pins-ok.json at 5,947
    - parts.py --describe --json: 30,226 bytes for 34 operations (7,137 bytes as text)
  - **Calls per step:** a write in idea.md is two calls (`--dry-run`, then the write).
  - **A measured research run:** 14 to 78 tool calls and 0.17 to 5.0 M tokens (docs/guide/research-cost.md:9-11,
    measured 2026-10-03).

  · E · `wc -c` on each file, runs of flow.py show --json, boards.py --list --json, parts.py --catalog --json, parts.py --describe --json, `wc -c tests/golden*/*.json` · supports only: sizes, whether a local model of size X follows a 41 KB command is unknown (—).

- FE-14 · Model choice is set by hand, not measured. The model table in scrum/README.md:263-273 says it is "Claude's
  reading of those words [the PO's], his to change", and "four parts of it stand on no words of his". The agents' own
  models are fixed in their frontmatter: part-finder haiku, datasheet-reader sonnet, design-reviewer and
  parts-researcher opus. No test or ledger compares models on a job. · E · scrum/README.md:251-273, agents/*.md frontmatter · supports only: no measurement exists.

### Evaluation

- FE-15 · What exists to measure spark today:
  - 144 `tests/test_*.py` files.
  - tests/test_journey_basic.py: the button-and-LED project through every stage, with a fake wokwi-cli. Its build stage
    is could-not-run where `tsci` is missing.
  - tests/test_journey.py: only checks that the README's picture follows its table.
  - tests/mutations/ledger.jsonl: 416 lines, plus a rows file per card.
  - Golden envelopes in tests/golden*.
  - ~/.local/share/spark/learned-rules.md: 528 lines, 223 list lines.
  - scrum/RETROSPECTIVES.md: 569 lines, 11 `##` sections.
  - 32 entries in docs/observations, among them the walk councils.
  - `cost.py`, which reads one transcript's requests, by_tool, tokens and minutes.

  No skill has an `evals` folder (`ls -R skills | grep -i eval` → nothing, `find . -type d -iname "*eval*"` → nothing).

  · E · the commands quoted, tests/test_journey_basic.py:1-12, tests/test_journey.py:1 · supports only: what is there, not its quality.

- FE-16 · An eval harness existed and was deleted. tests/test_orphans.py:4-6 records that on 2026-09-29 "a third of
  this repository was deleted: … an eval harness nobody re-ran …". Any eval direction meets that history and the
  orphan test: an eval that nothing calls fails the suite. · E · tests/test_orphans.py:4-6 · supports only: a precedent, not why it went unrun.

- FE-17 · What an eval of an agent that reads spark's skills takes (H, this lens):
  - A fixed task set. The fixtures exist: tests/data/breadboard/* holds 10 requirements projects.
  - A headless harness run, `claude -p` or another CLI. Each run costs tokens: the 2026-10-06 council measured about
    90M input tokens for 6 agents (brief.md, Depth).
  - A grader that reads results, not prose. spark's exit codes, `status` and the flow's phases (`flow.py show --json`)
    can be that grader with no new logic.
  - A transcript reader for calls and tokens: `cost.py`.
  - A budget and a schedule, because the hook cannot run paid model calls.

  What a read of the code cannot settle: the cost per run, the variance between runs, and whether a pass in the eval
  predicts a good walk. Only a spike that runs it settles them.

  · H · this lens, pointers E as given · supports only: a shape to test.

### Fit with the technical direction

- FE-18 · Fit with AGENTS.md's principles, per direction (H, this lens, read against AGENTS.md "Principles"):
  - **Other harnesses:** if they stay adapters over the Operations, they fit "one core, many interfaces" and "free, few
    and local". While the commands hold logic (FE-7), they do not fit, because each harness then copies it.
  - **A local model:** fits "free and local". It costs nothing in code, but the prompt sizes (FE-13) are against it
    until pieces 1 to 3 land.
  - **Evaluation with paid model runs:** meets "name any cost and ask first".
  - **The agent-knowledge guard:** fits "records grow by need" and the docs-in-the-same-PR rule. It is a test, with no
    new runtime.
  - **The PO's streaming rule of 2026-11-23:** none of the directions conflicts with it, but every live consumer is
    blocked on FE-10.

  · H · AGENTS.md "Principles for changing spark", #1105 12:54/12:55 CET · supports only: a reading to test.

- FE-19 · A project written by `/spark:init` already gets an `AGENTS.md` section. Its `CLAUDE.md` is only
  `@AGENTS.md`, so a harness that reads AGENTS.md finds spark's section with no new code. · E · scripts/spark/build/ai_files.py:1-28 · supports only: the project side, not the plugin side.

- FE-20 · The SKILL.md format is now an open, multi-vendor standard. Anthropic says it donated Agent Skills to the
  Agentic AI Foundation. Blog sources name Codex, Gemini CLI and Cursor as readers, but they contradict each other on
  the details. Its docs site, as seen in search results, says three things about Hermes Agent (Nous Research). It reads SKILL.md
  skills from `~/.hermes/skills/`. It connects to MCP servers over stdio and HTTP. It runs on OpenAI-compatible local
  endpoints. spark's 3
  skills are folders in that shape. Its 9 commands and 4 agents are Claude Code formats. · H · search results, 2026-11-23: anthropic.com/news/donating-agent-skills-to-the-agentic-ai-foundation, hermes-agent.nousresearch.com/docs/user-guide/features/skills (snippets only, pages not fetched) · supports only: that a skills-folder path can carry over, per-tool support is unverified.

- FE-21 · A `next` step embeds absolute paths. `flow.py show --json` put the project's absolute path into `argv` and an
  absolute `SPARK_HOME` into `env`. A remote client, such as an SSE MCP client or a hosted page, gets the person's
  paths. · E · a run of `flow.py show --json` on the fixture copy, `next[0].env` · supports only: one field in one answer, the privacy rules of other Operations were not checked.

## 2. What I could not check, and why

- Whether any command page works outside Claude Code: no other harness is installed here (brief, Start and reach). I
  read no harness docs beyond the search snippets.
- How many tool calls a journey step takes today: no walk transcript was counted. `cost.py` can count one, but I did
  not open the PO's session logs.
- How a local model handles a 41 KB command or a 30 KB `--describe`: this needs a model run (—).
- The keys of the 11 Operations and 15 scripts that declare no `data_keys` (FE-3), so the real key gap is unknown.
- The check_spine/build and check_all answers on a real build: these need `tsci`, and a build writes. I used the golden
  files instead.
- Whether Codex, Gemini CLI or Cursor read SKILL.md from a plugin folder: the sources contradict each other (FE-20).
- The test suite, mutate.py runs and walk diaries' scores: not run or read, per the order.

## 3. Questions for the decider

- Does the agent-knowledge guard fail on a name that is missing, or on a name that is untaught (on a line about its
  script)? · decides: whether FE-2's 13 flags and 14 keys are the backlog or 57 and more are.
- Is the person's yes for network operations spark's job (in the core) or the harness's (Claude Code's prompt)? ·
  decides: whether running in another harness first needs FE-6's consent piece.
- Do the core's sentences keep naming Claude and `/spark:` commands, or does piece 6 move that wording to each
  interface? · decides: whether the scripts are harness-neutral (FE-8).
- Can an eval spend paid model runs, with what monthly ceiling, and run outside the hook? · decides: whether J3's agent
  eval is a spike or waits (FE-16, FE-17).
- Which model table rows are measured first? · decides: the scope of a model-choice eval (FE-14).
- Must every Operation declare its `data_keys` before a guard or an MCP catalogue is built? · decides: the first piece of
  the agent-knowledge and MCP directions (FE-3, FE-11).

## 4. Searches

- "Agent Skills open standard SKILL.md supported by Codex Gemini CLI Cursor" · served: whether skills as folders of
  text (option 7 on #1522) carry to other harnesses without a rewrite · used, as H (FE-20): blog sources contradict
  each other. The one authoritative page found (anthropic.com/news/donating-agent-skills-to-the-agentic-ai-foundation)
  lists no per-tool support.
- "Hermes Agent Nous Research skills SKILL.md MCP servers local models" · served: whether Hermes, the harness the PO
  named, can run spark's skills, MCP tools and a local model · used, as H (FE-20): snippets from
  hermes-agent.nousresearch.com/docs. No page was fetched.
