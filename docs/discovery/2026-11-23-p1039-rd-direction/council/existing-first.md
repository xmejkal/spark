# Existing-first lens: P1039 #1522

Read 2026-11-23 (Europe/Prague), branch p1039-rd-discovery at e0c0dc77. Lens model: Opus. Tags: E with a pointer,
H with its source, D with who and when. — is unknown. Web pages were read on 2026-11-23 unless a line says otherwise.
"Search summary" means the search tool's summary, not a page I opened. Such a line is H until a page is read. Nothing
here decides anything. A harness is the program that runs an AI agent and gives it tools, for example
Claude Code, Codex CLI or Hermes Agent.

## Findings

### The finding that matters most: what is shared across harnesses, and what of spark is Claude Code only

- EX-1 · Two open formats are now read by many harnesses, and both sit under the Agentic AI Foundation (Linux
  Foundation). AGENTS.md: "a simple, open format for guiding coding agents", stewarded by the Agentic AI Foundation.
  The page lists 23 tools that read it (Codex, Jules, Factory, Aider, goose, opencode, Zed, Warp, VS Code, Devin,
  Junie, Amp, Cursor, RooCode, Gemini CLI, Kilo Code, GitHub Copilot coding agent, Windsurf, Augment Code and others).
  The page does not name Claude Code. Agent Skills: "a folder containing a `SKILL.md` file" with `name` and
  `description` at minimum, plus optional `scripts/`, `references/`, `assets/`, loaded by "progressive disclosure".
  "originally developed by Anthropic, released as an open standard". · E · https://agents.md/ and
  https://agentskills.io/home.md, read 2026-11-23. Licences by `gh api repos/<r> --jq .license.spdx_id`:
  agentsmd/agents.md MIT, agentskills/agentskills Apache-2.0 · supports only: a shared standard exists for project
  instructions and for skills. It does not say how well each harness implements it.
- EX-2 · No shared standard exists for agents (subagents), slash commands or plugin bundles. spark's own research of
  2026-10-13 found each of five tools keeps its own agent format (Claude Code Markdown+YAML, Codex TOML, Cursor and
  Gemini CLI Markdown+YAML in their own folders, Copilot also reads `.claude/agents`), and all five read `SKILL.md`
  folders, the four others also from `.agents/skills/`. A third-party comparison dated 2026-06-26 gives the plugin
  bundles: Claude Code `.claude-plugin/plugin.json` (skills, MCP, hooks, agents, LSP). Codex
  `.codex-plugin/plugin.json` (skills, MCP, hooks, no agents). OpenCode code-first, no manifest, no bundled skills
  or agents. And states "MCP is the universal interop layer". · E · docs/discovery/2026-10-13-p216-formats.md (The
  table, sources 1-16, read by spark on 2026-10-13, not re-read today).
  Https://awslabs.github.io/aidlc-workflows/reference/research/Cross-Tool%20Plugin%20Comparison/ read 2026-11-23 ·
  caveat: the two disagree on Codex agents (P216: `.codex/agents/` TOML exists. AWS page: no agents in a Codex
  plugin), probably because one is about project folders and the other about plugin bundles (H, mine). Neither is
  the vendor's own page for today.
- EX-3 · Hermes, as the PO most likely means it, is Nous Research's Hermes Agent: an MIT agent harness (repository
  NousResearch/hermes-agent, 265,595 stars, pushed 2026-11-23). Its docs: skills "are compatible with the
  agentskills.io open standard". They load from `~/.hermes/skills/`, and from a project's `.hermes/skills/` and
  `.agents/skills/` only after `hermes skills trust`. `~/.claude/skills` is not named. "Every installed skill is
  automatically available as a slash command". Skills install from GitHub, a URL or hubs (skills.sh, ClawHub and
  others), each through a security scan. Frontmatter adds `version`, `platforms`, `metadata.hermes`. Context files
  `.hermes.md`, AGENTS.md, CLAUDE.md, SOUL.md and `.cursorrules` are injected into every conversation. It is an MCP
  client with a tool filter. It has subagents (`delegate_task`), its own plugin system, an "Import from Other
  Agents" page that imports skills, MCP servers and instructions from `~/.claude`, and local models through Ollama,
  llama.cpp or MLX, or "any OpenAI-compatible endpoint". No page says Claude Code plugins run in it. ·
  E · https://hermes-agent.nousresearch.com/docs/llms.txt and
  https://hermes-agent.nousresearch.com/docs/user-guide/features/skills, read 2026-11-23. Licence by `gh api
  repos/NousResearch/hermes-agent` = MIT · caveat: read through a summariser. The MCP-server role is disputed (a
  search summary says it can serve MCP, the docs index names only an OpenAI-compatible API server). "Hermes" is also
  the name of Nous Research's open-weight model family and its tool-call format (H, model knowledge, not read
  today), so the PO's word could mean either. His "harnesses, like Hermes" points to the agent.
- EX-4 · spark's scripts do not depend on any harness or model. No script imports an LLM client: the grep for
  `import anthropic|openai|claude -p` under scripts/ and tools/ hits only text (ai_files.py, tool_choices.py,
  tool_finder.py, flow_codes.py), none a call. `pyproject.toml` has no `[project]` table on purpose ("plugin users
  never pip-install spark, and the commands call the scripts by path"). `CLAUDE_PLUGIN_ROOT` appears in two scripts,
  both in usage docstrings (scripts/breadboard.py:10, scripts/import_firmware.py:9). The Operation already gives an
  MCP tool's `inputSchema` and `outputSchema` (scripts/spark/core/operation.py:106, :116). · E · the greps and lines
  named · supports only: the core is plain Python a harness can call. No other harness has run it.
- EX-5 · spark's plugin layer is Claude Code specific in four places: (1) nine `commands/*.md` with `allowed-tools`
  frontmatter, a Claude Code permission list. (2) four `agents/*.md` with `model:` (opus, sonnet, haiku) and `tools:`
  in Claude Code's agent format. (3) `${CLAUDE_PLUGIN_ROOT}` on 76 lines in 12 of the command, skill and agent files
  (127 occurrences). (4) `/spark:page` needs the claude-artifacts tools. The three skills follow the SKILL.md shape
  (name, description), but spark-review also carries `allowed-tools` with `${CLAUDE_PLUGIN_ROOT}` paths. The agent
  guide says: "following a command page outside Claude Code was not tried for these docs". · E ·
  commands/build.md:2-3, agents/*.md headers, skills/spark-review/SKILL.md:4, `grep -c CLAUDE_PLUGIN_ROOT`,
  commands/page.md:59-105, docs/guide/agents.md:76-81 · supports only: which pieces need an adapter for another
  harness. Hermes turns skills, not Claude commands, into slash commands (EX-3), so the nine commands would need a
  skill form there (H, mine).
- EX-6 · spark already has the adapter seam P216 designed: `/spark:init` writes a marked section into the project's
  AGENTS.md, a `CLAUDE.md` holding `@AGENTS.md`, and a `CLAUDE.local.md` link. The rest of that plan (adapters for
  other tools' private rules and agents, the store naming the AI tools that get files, one refresh command) is open
  as P227 #213. · E · scripts/spark/build/ai_files.py:1-10. Docs/discovery/2026-10-13-p216-claude-files.md (The short
  version). `gh issue view 213` (OPEN) · supports only: the multi-harness question has an open card with the PO's
  words of 2026-10-13 ("works natively great with all kinds of aggentic systems and harnesses").
- EX-7 · Human-facing text in the core names Claude: `IDEA_MESSAGE = "Tell Claude your goal in the chat"`,
  `NO_FIRMWARE_MESSAGE = "... Ask Claude to write it in the chat."`, and the phase actor `BY_CLAUDE = "claude"`. ·
  E · scripts/spark/flow/flow_codes.py:17, :27, :65 · supports only: a harness other than Claude would show these
  words as they are. How many such strings exist: — (I read one file).
- EX-8 · No harness other than Claude Code is installed on the PO's Mac: `command -v` found `claude` (2.1.323) and
  none of codex, gemini, opencode, goose, aider, hermes, ollama, llama-server, lms, vllm, mlx_lm.server, promptfoo,
  inspect, langfuse. · E · the shell, 2026-11-23 15:5x CET · supports only: every cross-harness claim stays H until
  one is installed and tried. The brief's "not checked yet" is now checked.

### (a) The "software factory": what covers which part of the line

- EX-9 · Software factories, as written up in 2026, cover software only and stop short of hardware. Augment's guide
  (2026-08-20, updated 2026-09-15): "an agentic software-delivery operating model in which AI agents write, test, and
  ship code" in five stages (intake, specification, build, verification, shipping), humans keeping spec approval
  and merge approval. It names GitHub Copilot cloud agent, Spec Kit, Codex, Symphony, Jules, Claude Code, Devin and
  others, and mentions hardware only to exclude it. The Agentic AI Foundation's "Glass Town" post (2026-10-14):
  planner, builder, reviewer (a second model), tutorial writer, previewer. AGENTS.md per project. An MCP server for
  cloud machines. No production deploy and no hardware. · E · https://www.augmentcode.com/guides/what-is-a-software-factory
  and https://aaif.io/blog/welcome-to-glass-town-building-a-software-factory-with-a-paper-trail, read 2026-11-23 ·
  supports only: the pattern (brief, plan, build, independent review, human gates) matches spark's team process
  (scrum/README.md), not spark's product. The "deploy" end of a software factory is CI and a preview, not a flash.
- EX-10 · Open-source pieces for a software factory, per secondary sources: Aider, Cline, OpenCode, OpenHands, goose,
  with git worktrees, containers and CI. Licences read: OpenHands MIT, opencode MIT (repository now
  anomalyco/opencode), goose Apache-2.0 (repository now aaif-goose/goose), Aider Apache-2.0 (last push 2026-05-22),
  Codex Apache-2.0, Gemini CLI Apache-2.0. · E for licences: `gh api repos/<r>` 2026-11-23 · H for the factory
  list: search summary of hashnode.com and edenai.co, pages not opened · supports only: free and open agent CLIs
  exist. Each needs a model, paid or local (EX-25).
- EX-11 · Flux is the hardware "prompt-to-board" product: an AI agent in the browser that does schematics, part
  sourcing and routing (search summaries of a 2025-10-07 press release and trade press. The press page refused my
  fetch with 403). Its pricing page: after the trial, "Editing private projects, exporting them, and using AI require
  a paid plan". It runs in the browser. Firmware appears only as a marketing line ("The board, enclosure, and
  firmware designed together"). · E · https://www.flux.ai/p/pricing, read 2026-11-23 · H · the agent's scope, from
  the search summary · supports only: Flux is proprietary, paid for AI and cloud-only, so it fails "free, few and
  local". It aims at a PCB, not at modules on a breadboard with flashed firmware.
- EX-12 · pcbGPT (KIT and Bosch Sensortec, arXiv 2606.01188, 2026): natural-language requirements to an editable
  KiCad schematic. Parts grounded in the local KiCad library (embedding and lexical search) and in each part's
  datasheet, a part "reported as unavailable rather than invented". Deterministic checks (DSL constraints, KiCad
  ERC) and then a validation agent that is "not formal verification". Out of scope: placement, routing, manufacturing,
  firmware, breadboard, simulation. 20 tasks. Gpt-5.3-codex pass@1 0.90 (0.72 on hard), qwen3.5-397b pass@1 0.72. ·
  E · https://arxiv.org/html/2606.01188v1, read 2026-11-23 (first 100,000 of 131,900 characters) · supports only:
  the closest research system shares spark's rule of refusing rather than guessing. It stops at a schematic. Code
  release and licence: —.
- EX-13 · atopile (a declarative language compiled to KiCad, described as MIT) and tscircuit (MIT, 3,064 stars)
  are hardware-as-code tools an agent can drive. Spark already drives tscircuit. · E · tscircuit licence by `gh api
  repos/tscircuit/tscircuit`. Spark's use in README.md:24-43 · H · atopile's licence and the "agent rebuilt a
  50-requirement board" story, search summary of stationx.net and a LinkedIn post, not read.
- EX-14 · No source I read covers spark's whole line (a goal in words, modules from the person's drawer, a
  breadboard sheet, a pin map the firmware imports, a free simulation, a flash with the person's yes, a bench check).
  Software factories stop at a software deploy (EX-9). Flux and pcbGPT stop at a board or a schematic (EX-11, EX-12).
  The embedded benchmarks test firmware or circuits in isolation (EX-20). · H · my comparison of EX-9 to EX-13 and
  EX-20 with README.md "What works today" · supports only: what is left for spark is the hardware half of a factory
  and the hand-over between its stages. It does not show anyone needs it (the hobbyist stays H, scrum/VISION.md).

### (b) Other harnesses: what each reads from a plugin

- EX-15 · What a harness reads, by kind of piece. Project instructions: AGENTS.md by most (EX-1). Claude Code reads
  CLAUDE.md, which imports `@AGENTS.md`. Gemini CLI needs `context.fileName`. Hermes reads AGENTS.md and CLAUDE.md
  both. Skills: SKILL.md folders by Claude Code, Codex, Cursor, Copilot, Gemini CLI (P216) and Hermes (EX-3), from
  different folders. MCP servers: all of them as clients. Subagents and slash commands: each its own format. ·
  E · EX-1, EX-2, EX-3 pointers · supports only: spark's portable layer today is AGENTS.md, the three skills (once
  `${CLAUDE_PLUGIN_ROOT}` is resolved) and the scripts. The nine commands and four agents are not portable as they
  stand.
- EX-16 · Converters from one source to several harnesses exist: `wshobson/agents` writes one Markdown source to
  Claude Code, Codex CLI, Cursor, OpenCode and Gemini CLI, and "Codex conversion turns commands into skills". The
  Compound Engineering CLI converts Claude Code plugins to OpenCode, Codex and Gemini CLI. Gemini CLI takes a
  `gemini-extension.json` with agents, commands and skills at its root. OpenAI ships a Codex plugin for Claude Code. ·
  H · search summary, pages not opened (raw.githubusercontent.com/wshobson/agents/.../docs/harnesses.md,
  mintlify.com/EveryInc/compound-engineering-plugin) · supports only: reuse candidates for P227's adapters, to be
  read before any design.
- EX-17 · CI as a harness: spark has no `.github/workflows/`. Its gate is the local pre-push hook
  (tools/pre-push, tools/check_commit.py). `claude plugin eval` has `--trust-plugin` "for CI". · E · `ls .github`
  (only ISSUE_TEMPLATE), `ls tools`, `claude plugin eval --help` · supports only: no CI runs spark today.

### (c) Evaluation of an agent system and of model choice

- EX-18 · Claude Code 2.1.323 has a plugin eval on this Mac: `claude plugin eval [target]` runs cases
  (`evals/**/case.yaml` or `prompt.md` + `graders/*.md`) against a plugin, with a no-plugin baseline arm and the score
  delta (`--ablation with-without`, the default when a plugin resolves), `--model` to override the model for all
  cases, `--judge-model` (default haiku), `--runs` (default 3), `--threshold`, `--max-cost-usd`, MCP mocks recorded by
  default, `--json`, and `claude plugin eval init` to author a suite by interview. It publishes the HTML report to
  claude.ai by default unless `--no-publish`. spark has no `evals/` folder. · E · `claude plugin eval --help`, `ls
  evals` ("No such file or directory"), 2026-11-23 · supports only: a free (in tool cost. The runs use the person's
  model plan) eval harness for spark's skills and commands exists in the PO's own tool. It runs inside Claude Code
  only, so it cannot compare harnesses. The default publishing would send prompts and grader verdicts to claude.ai
  (H, from the flag text. Spark's privacy rules would want `--no-publish` on runs that touch the store).
- EX-19 · `claude plugin details spark` measures spark's context cost: always-on about 1,676 tokens in every session.
  On invoke, `build` about 14.3k, `idea` 7.6k, `deploy` 7k, `research` 4.5k, `parts-researcher` 4.3k,
  `spark-design` 3.9k. · E · the command's output, 2026-11-23 · supports only: a measured number a model choice or a
  local model's context window can be checked against (EX-25).
- EX-20 · Three embedded-agent benchmarks of 2025-2026. EmbedBench (ICSE, arXiv 2506.11003): 126 cases, 9 components,
  3 platforms (Raspberry Pi Pico with MicroPython, ESP32 with ESP-IDF, Arduino migration), tasks in programming,
  circuit design and migration. Best pass@1 73.8 % on Pico MicroPython and 29.4 % on ESP-IDF. RAG and compiler
  feedback raise DeepSeek-R1 from 55.6 % to 65.1 %. IoT-SkillsBench (arXiv 2603.19583): 3 platforms, 23 peripherals,
  42 tasks on real hardware, each run with no skills, LLM-written skills and human-expert skills. "concise
  human-expert skills enable near-perfect success rates across platforms". Embedded-Arena (NeurIPS 2026 poster):
  hardware-in-the-loop compile, flash and measure. Frontier models at 0 % deployment without hardware feedback. ·
  E · https://arxiv.org/abs/2506.11003 and https://arxiv.org/abs/2603.19583, read 2026-11-23 · H · Embedded-Arena and
  EmbedBench's use of Wokwi, search summary only (the abstract page did not say how solutions are verified) ·
  supports only: published task sets near spark's walks exist. IoT-SkillsBench is evidence that written skills move
  agent success on hardware tasks, which bears on J4 (agent knowledge). Code release of each: —.
- EX-21 · Inspect (UK AI Security Institute and Meridian Labs. Repository UKGovernmentBEIS/inspect_ai, MIT): "an
  open-source framework for large language model evaluations". Built-in ReAct agent, multi-agent primitives, Docker
  and other sandboxes, model-graded and custom scorers, a local log viewer (`inspect view`), local inference through
  HuggingFace, vLLM and SGLang (Ollama not named on the page), and "the ability to run arbitrary external agents like
  Claude Code, Codex CLI, and Gemini CLI". · E · https://inspect.aisi.org.uk/, read 2026-11-23. Licence by `gh api` ·
  supports only: the one free, local tool I read that can run the same task set across harnesses and models.
- EX-22 · promptfoo (MIT): evaluates coding agents as providers: Claude Agent SDK (`anthropic:claude-agent-sdk`,
  read-only unless tools are enabled), Codex SDK and app-server, OpenCode SDK, Open Interpreter. A fresh workspace per
  step (`copy_working_dir`), `is-json` with a schema, file checks in JavaScript, `llm-rubric`, `agent-rubric`,
  trajectory assertions (`trajectory:tool-used`, `trajectory:tool-sequence`, step count), cost and latency
  thresholds, `--repeat 3` for variance. A local judge works through an OpenAI-compatible endpoint for `llm-rubric`
  only. · E · https://promptfoo.dev/docs/guides/evaluate-coding-agents/, read 2026-11-23. Licence by `gh api` · H · the
  local-judge detail, search summary · supports only: a second free tool that can score a walk's trajectory (which
  scripts an agent called, in which order) across harnesses.
- EX-23 · Langfuse: MIT outside its `ee/` folders, which carry their own licence. Self-hostable (P417 #545's card
  says "self-hosted for free or as a cloud service with a free tier", not re-read). LangSmith: not read, licence and
  local use —. · E · LICENSE head by `gh api repos/langfuse/langfuse/contents/LICENSE` · supports only: Langfuse is
  the tracer the PO named in P417. Its core is free to self-host.
- EX-24 · Inside spark, what measures the agent system today: the walks (10 folders under ~/Development/spark-walks:
  p581, p711, p934 and others) with diaries and rows. `tests/test_journey_basic.py` and `tests/test_journey.py`.
  Mutation rows and their ledger. The learned rules (~/.local/share/spark/learned-rules.md, 101,198 bytes, 222 lines
  that start with "- "). `board.py status` with intake against closure (P1020 #1487, closed). The model table in
  scrum/README.md:262-274 is set from the PO's words, and "Four parts of it stand on no words of his". "the table
  and the agents' files are tied by no test" (P925 #1310's closing comment). An eval once existed: `tools/match_eval.py`
  (P211 task 5, #187) was removed under P385's prune (commit f9e0f92f). · E · the paths and commands named · supports
  only: spark measures code and process. Nothing scores an agent's success at a task or compares models on spark's
  jobs.

### (d) Local AI: what can drive tool calls and long JSON today

- EX-25 · Claude Code itself can run on a local model: Ollama v0.14.0 and later speak a subset of the Anthropic
  Messages API (`ANTHROPIC_BASE_URL=http://localhost:11434`, `ANTHROPIC_AUTH_TOKEN=ollama`, `claude --model
  gpt-oss:20b`). Recommended local models `gpt-oss:20b` and `qwen3-coder`. "It is recommended to run a model with at
  least 32K tokens context length." Supported: messages, streaming, system prompts, tools and tool results,
  thinking, base64 images. Not supported: `tool_choice`, token counting, prompt caching (`cache_control`), batches,
  citations, PDF blocks. `budget_tokens` accepted but not enforced. llama.cpp also added the Anthropic Messages API
  (search summary, Hugging Face blog not opened). · E · https://ollama.com/blog/claude (2026-01-16) and
  https://docs.ollama.com/api/anthropic-compatibility, read 2026-11-23. Ollama and llama.cpp MIT by `gh api` ·
  supports only: the plugin as it is (commands, agents, skills) could be tried on a local model without a second
  harness. Whether spark's commands work there: — (EX-8: Ollama is not installed). The 32K minimum is below
  `build`'s 14.3k on invoke plus the always-on 1,676 plus a conversation (EX-19), so a local window needs room (H, mine).
- EX-26 · Local tool calling, one measured study (Docker, 2025-06-30. 3,570 tests, 21 models, five tools, up to five
  rounds. M4 Max with 128 GB): tool-selection F1 qwen3:14B-Q4_K_M 0.971 (gpt-4 hosted 0.974), qwen3:8B 0.919-0.933,
  llama3.1:8B 0.79-0.84, llama3.3:70B-Q4 0.607. About 142 s per interaction for Qwen3 14B and 84 s for Qwen3 8B
  against under 5 s for GPT-4. Quantisation made "no significant difference". · E ·
  https://www.docker.com/blog/local-llm-tool-calling-a-practical-evaluation/, read 2026-11-23 · supports only: an
  old (2025) and small-tool-set data point: local models can pick tools well and are slow. It says nothing about
  long multi-step agent runs or spark's JSON envelopes.
- EX-27 · Ollama enforces a JSON schema on a reply when the schema is passed in `format`. "Ollama's cloud currently
  does not support structured outputs". The docs advise also putting the schema in the prompt and temperature 0. ·
  E · https://docs.ollama.com/capabilities/structured-outputs, read 2026-11-23 · supports only: long JSON answers are
  constrained at the runtime, not only asked for. Reports of tool calls coming back as plain text for Qwen3-Coder 30B
  and Qwen 3.5 27B: H, search summary of issue trackers, not read.
- EX-28 · spark's scripts answer in their own JSON envelope with exit codes, so a local model reads spark's JSON. It
  need not write long JSON except a requirements file, a replies file or a `--fact-set` file. · E ·
  docs/guide/agents.md:13-30 (the contract), commands/build.md (the requirements file) · supports only: what spark
  asks of a model is mostly reading and calling, which is the part EX-26 measured. Writing firmware is the larger ask
  (EX-20: 29.4 % to 73.8 % pass@1 on embedded programming for frontier-class models).

### (e) Inside spark: cards, findings and discoveries that already cover (a) to (d)

Searched by downloading all 973 issues' titles (`gh issue list --state all --limit 1600`) and grepping them.
Bodies read for the cards named in the task and for #213, #401, #345, #1310, #187, #1197, #962, #1346.

- EX-29 · (b) harnesses and generality: P217 #199 OPEN (Claude chat, any AI or agent system, UX for people and AI.
  Notes of 2026-10-13 name AGENTS.md, SKILL.md, MCP, the CLI with `--json`). P227 #213 OPEN (the store names the AI
  tools that get files. One refresh command). P216 #197 CLOSED (init writes AGENTS.md, CLAUDE.md, CLAUDE.local.md.
  Its formats research, EX-2). P793 #1105 OPEN (every interface from one core: CLI, agents, MCP, LangGraph, coloured
  terminal). P158 #94 CLOSED (one core). P481 #660 CLOSED (each Operation described once, as data, for CLI, agents,
  MCP, LangGraph). P154 #89 CLOSED (switch a tool between local CLI and MCP). P834 #1196 OPEN (the page on other
  hosts). P835 #1197 CLOSED (finding: no spark MCP server yet. The rule of ai-interface.md §8 holds: build one "when a
  named host cannot run a shell"). P836 #1198 OPEN (a spark mod in Claude Code). P494 #674 OPEN (which interface
  first). · E · issue states from the title list. Bodies by `gh issue view`. Docs/discovery/2026-11-16-p835-interface-spike/finding.md
- EX-30 · (b) runtimes, boards and frameworks: P356 #457 OPEN (MicroPython, Arduino, ESP-IDF, PlatformIO behind one
  seam) with slices P358 #459, P359 #460, P360 #461 and A0 P361 #462, all OPEN. P221 #203 CLOSED and P528 #730
  CLOSED (platform spikes, with a Rust column). P531 #733 OPEN (Rust esp-hal). P713 #962 OPEN (lower-level code
  through skills and agents, callable from CLI, MCP and the agents). P417 #545 OPEN (LangGraph node, MCP tool and a
  Langfuse trace from the same Operations). P419 #548 OPEN (one RAG case). P1033 #1515 OPEN with P1036 #1519 OPEN
  (storage seam. Its stage 8 is a read-only LangGraph adapter). · E · title list and bodies of #545, #548, #1515
- EX-31 · (c) evaluation and model choice: P943 #1346 OPEN (a list of agentic setups, tools and practices to test one
  by one. Part 1 and 2 of its finding posted 2026-11-20). P289 #345 OPEN (numbers per story for the retro. The PO's
  2026-10-18 shape: number fields on board cards, among them agent tokens). P317 #401 OPEN (how useful is the
  refuter: its own confirmed findings and its tokens per PR). P925 #1310 CLOSED (the model table, set by hand, no
  test). P224 #206 OPEN (where cards wait). P161 #97 and P166 #103 CLOSED (QA trust). P711 #960 OPEN, in Idea since
  2026-11-17 (walks driven only through spark's commands, skills and agents, never a script by hand). P365 #467 OPEN
  (walks). P934 #1323 OPEN (the e-paper walk). P200 #153 OPEN (an inventory of capabilities. Its first guess at
  value: "An agent given only that inventory completes the basic journey without reading source"). P839 #1203
  CLOSED (inventory reads core CLIs' flags). No card names an eval tool (Inspect, promptfoo, `claude plugin eval`) or
  a benchmark. · E · title list grep for "eval|benchmark|measure|score|model". Bodies of #1346, #345, #401, #1310,
  #153, #960
- EX-32 · (c) agent knowledge keeping up with the scripts (J4): only one direction is guarded. tools/check_docs.py
  checks that the docs "name only what is there". Nothing fails when a script is taught nowhere: `scripts/cost.py`
  exists and no file in commands/, skills/, agents/, docs/guide/agents.md or docs/guide/agents/ names `cost.py`.
  Related open cards: P200 #153, P220 #202 OPEN (a project learns when spark changes), P937 #1333 OPEN (generated
  blocks per core CLI). · E · tools/check_docs.py:2-9, `grep -rl cost.py` (no hit), `ls scripts/cost.py`. #1522's
  comment of about 16:0x CET (spark-main's reading, now confirmed for cost.py) · supports only: the gap exists for at
  least one script. How many scripts or flags are untaught: — (`tools/inventory.py` would say. Not run).
- EX-33 · (d) local AI: no card's title names a local model, Ollama, llama.cpp or an offline model (grep "local
  AI|local model|Ollama|llama|offline model" over 973 titles: no hit). The PO's words on #1522 (about 15:5x CET) are
  the first. · E · the title grep · supports only: local AI is new to the board.
- EX-34 · (a) the software factory's later stages: P79 #16 OPEN (breadboard first, PCB only once the circuit and
  firmware work), P203 #163 OPEN (Fusion 360 design and 3D), P277 #313 OPEN (Fusion export), P210 #180 and P371 #473
  OPEN (3D models of parts), P308 #374 OPEN (deploy needs a Wokwi pass). No card uses the words "factory" or names
  an enclosure stage. · E · title list grep "factory|PCB|order a board|enclosure|3D|deploy"

## What I could not check, and why

- Whether any of spark's commands, skills or agents works in Hermes, Codex, Gemini CLI, opencode or on a local
  model: no other harness or runtime is installed (EX-8), and my task was read-only with no installs.
- The vendors' own pages for today's skills, agents and plugin folders of Codex, Gemini CLI, Cursor and Copilot: I
  relied on spark's research of 2026-10-13 (EX-2) and a third-party page of 2026-06-26. The two disagree on Codex
  agents. Re-reading the five vendor pages would settle it. It did not fit the ten-search budget.
- Whether Hermes Agent can also serve as an MCP server, and whether its "Import from Other Agents" carries a Claude
  Code plugin's commands and agents: the docs index and a search summary disagree. The import page was not opened.
- Flux's agent scope (the press release refused the fetch with 403). atopile's licence. The converters of EX-16.
  The llama.cpp Anthropic API post. Embedded-Arena's paper. Whether EmbedBench verifies in Wokwi. All are search
  summaries only.
- LangSmith's licence and self-hosting: not searched (budget).
- Code and data release of pcbGPT, EmbedBench and IoT-SkillsBench: the abstract pages did not say.
- Long multi-step tool use by local models on a task like spark's journey: the one study read (EX-26) is from
  2025-06 with five tools and a shopping cart. Newer comparisons in the search were SEO blogs, not read.
- How many scripts, flags, exit codes or JSON keys no skill or command teaches (EX-32): `tools/inventory.py` would
  answer. I did not run it, to keep the run short and the tree untouched.
- The content of the walks' diaries and the learned rules: I counted them, I did not read them.
- Whether `claude plugin eval` can run with a local model behind `ANTHROPIC_BASE_URL` (EX-18 with EX-25): not tried.

## Questions for the decider

- Q-a · Is "Hermes" Nous Research's Hermes Agent (the harness, EX-3), or the Hermes model family? · decides: whether
  the harness work names Hermes Agent as a target beside Codex and Gemini CLI, or whether Hermes belongs under the
  local-model question (d).
- Q-b · Is a second harness something the PO wants to run himself, or a property spark should have for others? ·
  decides: whether a first step is installing one harness on his Mac and walking spark there (EX-8), or only keeping
  spark's files in the shared formats (EX-1, EX-15) without a trial.
- Q-c · Should spark's nine commands also exist as skills (the portable form, EX-3, EX-5, EX-16), or stay Claude Code
  commands with adapters written per harness (P227 #213)? · decides: the shape of the agent-knowledge layer and how
  many files a change must keep current (J4).
- Q-d · Is an eval of spark's skills and commands wanted inside Claude Code first (`claude plugin eval`, EX-18), or
  across harnesses and models from the start (Inspect or promptfoo, EX-21, EX-22)? · decides: which tool, and
  whether J2 (other harnesses) and J3 (evidence) share one task set.
- Q-e · May eval runs and reports leave the Mac (claude.ai report publishing by default, a hosted tracer), or must
  they stay local? · decides: `--no-publish` and self-hosted Langfuse against hosted options, under spark's privacy
  rules for the store.
- Q-f · What is the model budget for evals (repeated runs per case cost model use, EX-18 `--runs` default 3,
  EX-22 `--repeat 3`)? · decides: how many cases and runs, and whether local models are the cheap arm.
- Q-g · Does "software factory" for spark mean the product (a person's gadget from goal to flashed board) or the
  team's own process (planner, builder, reviewer, human gates, EX-9)? · decides: whether the factory epic sits in the
  product lane or the team-tooling lane.

## Searches

1. "Nous Research Hermes Agent skills MCP AGENTS.md documentation" · which Hermes the PO means and what it reads from
   a plugin (b) · used (EX-3. Pages then fetched: docs/llms.txt and the skills page)
2. "agentskills.io Agent Skills open standard SKILL.md adopted by Codex Gemini CLI opencode goose" · is there a
   shared standard for skills that several harnesses read (b) · used (EX-1. Agentskills.io/home.md fetched. Agents.md
   fetched without a search)
3. "AI agent hardware design from natural language to PCB and firmware 2026 Flux Copilot atopile tscircuit AI" · what
   covers the hardware half of a factory, and is it free and local (a) · used (EX-11, EX-12, EX-13. Flux.ai pricing
   and the pcbGPT paper fetched. The press release refused)
4. "\"software factory\" AI coding agents spec to deployed pipeline 2026 open source" · what part of the line software
   factories cover (a) · used (EX-9, EX-10. Augmentcode.com guide and aaif.io post fetched)
5. "promptfoo evaluate Claude Agent SDK coding agent provider local llm-rubric" · which eval tool can score agents
   across harnesses, free and local (c) · used (EX-22. The coding-agents guide fetched. Inspect's page fetched without
   a search, EX-21)
6. "LLM agent benchmark embedded systems hardware-in-the-loop microcontroller firmware circuit wiring 2026" · whether
   benchmarks near spark's walks exist (c) · used (EX-20. Two arXiv abstracts fetched)
7. "Ollama tool calling structured outputs JSON schema best open-weight models agentic coding 2026 context length
   requirements" · which local models can drive tool calls and long JSON, and what they need (d) · used (EX-26,
   EX-27. Docker's study and Ollama's structured-outputs page fetched)
8. "Codex CLI opencode Gemini CLI install Claude Code plugin .claude-plugin marketplace compatibility commands agents"
   · whether spark's plugin bundle runs as-is in other harnesses (b) · used (EX-2, EX-16. The AWS labs comparison
   fetched)
9. "Ollama Anthropic Messages API compatibility run Claude Code with local model" · whether spark's current harness
   can run on a local model (d) · used (EX-25. Ollama's compatibility page and blog fetched)
10. none further (nine searches made of the ten allowed).
