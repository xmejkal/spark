# P1039 council: the UX and AI-UX lens

2026-11-23, branch p1039-rd-discovery at e0c0dc77, read-only. Opus. Paths are relative to the repository. `<store>` is the
person's spark store (SPARK_HOME). "A sibling project" is a project folder beside the repository, run read-only. A
harness is an agent tool that runs a model with its tools, such as Claude Code or Hermes (the PO's word on #1522).

## 1. Findings

Most important first. Tags: E (evidence, with a pointer), H (hypothesis, with its source), D (decision, who and when),
— (an unknown).

- **UX-1 · Nothing guards the direction "a new script, flag, code or key reaches the agents".** `scripts/cost.py` is named
  in no command, skill or agent file and in no page of the agents' guide (grep of commands/*.md, skills/*/SKILL.md,
  agents/*.md, docs/guide/agents.md and docs/guide/agents/*.md: 0 and 0). `tools/inventory.py` counts what reaches each
  script. It counts any page, also the developers' pages. Thus it lists cost.py as reached through
  `docs/guide/developing.md`, `how-it-works.md` and `map.md` (inventory output, its line 27). It also reports
  "202 flags, 16 named on no page", among them `reach.py --cure-first`, `run_scenario.py --timeout-ms`, `parts.py --view`
  and `tools.py --personal` (inventory output, lines 3 and 14-48). Only `tests/test_inventory.py` tests the tool. Nothing
  makes a PR fail on its count. `tools/check_docs.py` guards the other direction: a page names only what exists
  (check_docs.py:3-6). · E: grep and `python3 tools/inventory.py`, run 2026-11-23, tools/check_docs.py:1-8,
  tests/test_inventory.py:2 · supports only: the PO's question of about 16:0x CET (#1522) has a partial measure today.
  The measure does not separate the pages an agent reads from the pages a developer reads, and it is no gate.

- **UX-2 · The agents' entry page is out of date, and it never names the one call that says where a project stands.**
  `docs/guide/agents.md:5` says "This guide has four pages", but `docs/guide/agents/` holds eight files.
  `docs/guide/agents.md:185` says "There is no bench step yet.", but `docs/guide/agents/bench.md` documents `bench.py`,
  and `deploy.py` flashes boards. `flow.py` appears 0 times in AGENTS.md and in docs/guide/agents.md. `flow.py show
  --json` is the call that returns the phases, the "now" phase and its next step. An agent reaches `flow.md` and
  `bench.md` only through two table rows in json.md (json.md:141-142). · E: grep counts, 2026-11-23, agents.md:5, :185 ·
  supports only: an agent that follows AGENTS.md ("read docs/guide/agents.md first") starts from a page that misses
  the "what now" call and says the bench does not exist. This is example 1 for question (d).

- **UX-3 · The agents' knowledge is too large and too dense for a smaller model's context.** The files an agent is
  pointed to hold 64,430 words: AGENTS.md, the agents' guide, the 9 commands, the 3 skills and the 4 agent files. The
  agents' guide alone holds 34,997 words. 53 lines in the guide are longer than 400 characters, and the longest line in
  json.md is 2,300 characters. `check_docs.py` sets each page's budget in lines (BUDGETS, check_docs.py:33-58).
  The budget of json.md is 427, its line count today. A line budget cannot catch a line that grows. The Agent Skills format
  loads only each skill's name and description first, and the body on activation ("progressive disclosure",
  agentskills.io/home, read 2026-11-23). spark's guide has no such layer below the 185-line entry page. · E for the
  counts (`wc -w`, awk, 2026-11-23), H for the effect on a local or weaker model: model knowledge, not tested · supports
  only: a local or weaker model cannot hold today's guide. That model is the PO's later target on #1522, about 15:5x CET.

- **UX-4 · The next step is not complete in the answer alone.** `flow.py show --json` on a sibling project answered
  `next: [{"op": "build-board", "argv": ["<project>/requirements.json", "--keep", "<project>"], "why": "Build the board",
  "effects": ["reads","runs","writes"], "needs_yes": false, "env": {...}}]`. The step names no script. The op-to-script
  map is a table in `docs/guide/agents/flow.md:300-305` ("Run the step with the script that answers its op"). Only
  `parts.py` has `--describe`. It returns 34 operations, each with typed `arguments` (`type`, `description`, `default`),
  `effects` and `data` keys (`parts.py --describe --json`, 30,174 bytes). No other CLI describes itself this way (grep for
  `describe_operations`). · E: command output, 2026-11-23, flow.md:292-310, scripts/spark/core/describe_operations.py:1-5 ·
  supports only: "a next step in every answer" holds today only with a lookup table that the agent must remember. A
  typed manifest that can feed an MCP adapter exists for parts.py only.

- **UX-5 · The core's own sentences name Claude and Claude Code.** `scripts/spark/flow/flow_codes.py` holds "Ask Claude
  in the chat to build the board" (:239), "Ask Claude to look at the board first (/spark:deploy)." (:68), "Sent at %s.
  Nothing has run yet. To run it, type /spark:page in Claude Code." (:160), and "Claude runs it at your next /spark:page"
  (:167). The phases' `by` field takes the values "you", "claude" and "your terminal" (flow.py text output:
  "(claude)", `data.phases[].by: "claude"`). Both the person on the page and an agent under `--json` read these words.
  · E: flow_codes.py lines cited, `flow.py --json` output, 2026-11-23 · supports only: in another harness, or with a
  local model, the person reads "Ask Claude" and a slash command that does not exist there. The coupling sits in the
  data of the core, not only in the commands.

- **UX-6 · The line's last step never shows as done, to the person or to the agent.** `DeployReader` returns
  `NOT_STARTED` in every case ("the deploy is done in the person's terminal ... so it is not started here",
  scripts/spark/flow/phase_readers.py:554-560). Yet `bench.py show` reads "the deploys (boards/)" from the store
  (bench.py --help). So `flow.py show`, the page and `--json` all say "deploy: not started" after a deploy. `flow.py
  --help` also says "The page does not know whether the board is wired or flashed." · E: phase_readers.py:554-560,
  `bench.py --help` and `flow.py --help`, 2026-11-23 · supports only: for the software factory line, "deployed" is the
  end state, and neither interface shows it today. The fact exists in the store.

- **UX-7 · The text a person reads can lack the status, the fix and the next step that `--json` holds.**
  `TextReport.render` returns `"\n".join(result.lines)` (scripts/spark/core/cli.py:47-52). The finding on #1511 says that
  it "never prints the status, a finding's fix or the next step". It adds: "each Operation lays out its own lines by
  hand".
  P1032 (#1512) builds the shared layout for `look.py` first and the other CLIs later ("The other CLIs, one per PR",
  the finding's card 5). Some scripts print these by hand: `flow.py` ends with a "NOW (build): ... [build]" line, and
  json.md says that for parts.py "every item's fix and every next step is printed under the answer's lines". · E:
  cli.py:47-52, #1511 finding comment, 2026-11-23, #1512 body · supports only: the human/AI drift is in the structure.
  Whether the text shows the next step depends on each Operation until P1032's layout covers every CLI.

- **UX-8 · Most of the journey's knowledge lives in Claude Code formats that other harnesses do not read.** The 9
  commands hold 1,479 lines, the 3 skills 300 and the 4 agent files 385 (`wc -l`). The commands are Claude Code slash
  commands. Their `allowed-tools` frontmatter decides what runs without a prompt, and they use `${CLAUDE_PLUGIN_ROOT}`
  25 times (idea.md), 23 (build.md) and 21 (research.md). The agent files carry `model: opus` and `tools: Read, Grep`
  (agents/design-reviewer.md:1-6). Agent Skills need only a folder with SKILL.md and its `name` and `description`
  (agentskills.io/home, read 2026-11-23). Hermes's skills page says that its skills are "compatible with the
  agentskills.io open standard". It also says: "Every installed skill is automatically available as a slash command".
  Its SKILL.md frontmatter has no model or tool-list field (hermes-agent.nousresearch.com/docs/user-guide/features/skills,
  read 2026-11-23). The guide says: "following a command page outside Claude Code was not tried for these docs"
  (docs/guide/agents.md:79-81). · E for the counts and the quotes, H for the work of a port: not tried · supports only: spark's 3 skills
  are close to the open format. The 9 commands, which carry the journey from idea to deploy, and the 4 agents are not,
  as written. The command bodies are Markdown that names scripts, so a port is mainly the frontmatter and the
  variables (H).

- **UX-9 · The page is a second human surface, but it depends on Claude Code and its loop waits on a typed message.** A
  click writes one row to the Artifact's database. Nothing runs "until the person types `/spark:page`"
  (commands/page.md, body). The waiting text is "Sent at %s. Nothing has run yet. To run it, type /spark:page in Claude
  Code." (flow_codes.py:160). The page's carrier uses the `mcp__claude-artifacts__*` tools (commands/page.md,
  `allowed-tools`). `run-request` runs only the kinds `pick`, `requirements` and `build` (flow.py --help). The look, the
  deploy and the simulation stay in the chat or the terminal. P829's acceptance line (its "Done when") accepts this wait: "sent at <time>, waits for
  your next message to Claude" (#1187). · E: page.md, flow_codes.py:160, flow.py --help, #1187 body · supports only: the
  page serves reading and three kinds of click. It cannot drive the bench steps, and it has no carrier outside Claude
  Code with the Artifacts connector.

- **UX-10 · The open-questions seam is spark's most portable typed interface, and its shape is close to MCP
  elicitation.** `data.open` items are `{key, text, kind, asked_of, why, unit, answer_form, example, choices, cites}`.
  `kind` is `yes_no`, `value` or `choice`, and `asked_of` is `agent`, `person` or `either`. Each open question is an
  `unchecked` item with code `needs_reply`, the run exits 2, and `next[0]` is the same run with `--replies <file>`
  (docs/guide/agents/replies.md:11-26). A terminal with no `--json` asks the `person` and `either` questions live
  (replies.md:42-53). In MCP's form mode elicitation, a server sends `elicitation/create` with a `message` and a
  `requestedSchema`. The schema is "limited to flat objects with primitive properties only" (string, number, boolean,
  enum). The user answers `accept`, `decline` or `cancel`. A server "MUST NOT" ask for sensitive information in form
  mode. The client must "Provide UI that makes it clear which server is requesting information"
  (modelcontextprotocol.io/specification/2025-11-25/client/elicitation, read 2026-11-23). · E for both shapes. H for
  the mapping: yes_no to boolean, choice to enum, value to string or number with `unit`. A `person` question maps to an
  elicitation, and an `agent` question to the tool's own result · supports only: one seam already serves a person in a terminal and an agent under
  `--json`. An MCP adapter can possibly carry it as elicitation without a new shape (H). The look's question is `person`, and the
  deploy's yes stays the person's own typed word (never-assume.md, rule 7). The decider, not this lens, says whether an
  elicitation "accept" can stand for that yes.

- **UX-11 · A weaker model must learn many exceptions to the contract.** The contract is three words and three exit
  codes (agents.md:16-17). The page then lists the cases that are "Not yet true everywhere" (agents.md:99-116) and the
  crash cases (agents.md:124-146). `scripts/spark/core/renderers.py` has four envelope renderers (`JsonEnvelope`,
  `FullEnvelope`, `FlatJsonLine`, `JsonDocument`). The flat line of `grant.py`, `live.py` and `reach.py` "has no `code`"
  (json.md, look and deploy section). `check_vendor_pins.py --json` "prints a bare list and says `mismatch`"
  (agents.md:101, P43). Eight scripts take no `--json` (json.md, "Which scripts take --json"). `parts.py` puts 34
  operations behind one CLI. Some names are near: `--need`, `--needs`, `--needs-set` and `--needs-drop`. Its flags
  match by prefix (parts.py:98). · E: lines cited, `parts.py --describe --json` · H: near names and many exceptions cost a weaker
  model more than they cost Claude (model knowledge, not tested) · supports only: "fewer and typed tools, one envelope"
  is not true today. The exceptions are written down, but each one is a rule to remember.

- **UX-12 · Claude knows steps that the person never sees.** `/spark:idea` marks the steps S, M, C and L with
  `parts.py --step`, so that the cost line can count them (commands/idea.md:13-17). The cost line ("5 picks: ... 1
  request, 1 document, 14 min") is counted from "the transcripts of the steps' Claude Code sessions" (idea.md:247-248).
  A command's `allowed-tools` lets some operations run with no prompt. The person sees a prompt only for the others
  (agents.md:71-75). · E: lines cited · supports only: in another harness the cost line has no transcript to read. The
  person cannot see which steps ran without a question unless the agent tells them.

- **UX-13 · The bench has three human surfaces today. The terminal is the one where the person must act.** The deploy's
  yes is typed in the person's own terminal, or given as a grant there (deploy.py --help, never-assume.md, rule 7). The
  sibling project's breadboard sheet is a Markdown file. Its part "Before you power it" mixes a wiring warning with a
  long note on MicroPython deep-sleep wake levels and their source paths. The sheet ends with CLI commands
  (`parts.py --show led-red-5mm`). The sheet is the sibling project's breadboard.md, from an older build. The page draws "the wiring of a
  built project": the lines before power, then the steps, "one at a time or all at once" (flow.py --help). · E: help
  texts and the sheet · H: at the bench, the maker's hands are on a breadboard. A step-by-step view (the page) and a
  terminal that reads well (P1032) can serve the maker more than the sheet. The PO's walk diaries can test this. This lens did not
  read them for it. A TUI, an IDE panel, a local web page or a phone: — (this lens found no evidence in the repository or the issues).

- **UX-14 · The PO has no number that says whether spark got better for an agent or at the bench.** Today:
  - The README's "What works today" statuses "come from runs made for these docs, up to 2026-11-01" (README.md:114).
    They are written by hand and are three weeks old.
  - `parts.py --tally` gives a cost line per run, from Claude Code transcripts only (idea.md:247).
  - `tools/measure.py` ends in a SCORE line about the shape of the code, not about an agent's success
    (measure.py:1-5).
  - The walk diaries are prose in the store (`<store>/bench-2026-11-20.md`).
  - P711 (#960, open): "after the refactor, nobody walked spark end to end through its own agents and skills".
  - P200 (#153) and P217 (#199) are open.

  · E: lines and issue titles cited, 2026-11-23 · H: one possible shape for the PO's view is one row per release and per
  journey step. The row holds four values. First: did the agent reach the step with spark's own pages only (yes, no or
  not tried)? Second: how many times did the person step in? Third: the minutes. Fourth: the cost line. The journey
  picture can show the row beside today's status (tools/journey.py draws that picture, README.md:109). This shape comes
  from the facts above. Nobody checked it · supports only: evaluation as UX needs a walk that only spark's own pages drive (P711) and a place where its
  result shows up. Neither exists as a number today.

- **UX-15 · The docs keep up only by the PR author's memory.** PR #1516 (P1022 slice 2) changed
  `commands/deploy.md`, `docs/guide/agents/json.md` and `never-assume.md` beside the code (`git show --stat e521db8f`).
  · E · supports only: the practice works, and UX-1 and UX-2 show where it slips. What is missing is a guard, not the
  habit. This is example 2 for question (d), set against example 1 in UX-2.

- **UX-16 · Some answers mask paths for the person and give raw paths to the agent, by design.** `data` is masked,
  while a `next` step's `argv` and `env` are raw (flow.md:296-297, agents.md:32-35). The flow output above carried the
  whole home path in `argv` and in `env.SPARK_HOME`. · E · supports only: an adapter that shows `next` to a person (a
  button label, a TUI line) must use `why` and `label`, never `argv`. This is part of the contract to keep for every
  new interface.

### Question (a) in short: what each side does, sees, reads and calls, per direction

| direction | the person does and sees | the AI reads and calls | where they drift today |
| --- | --- | --- | --- |
| the factory line, from idea to a deployed gadget | chat, the page (phases, wiring, three kinds of click), the sheet, their own terminal for the deploy yes | commands and skills, `flow.py show --json`, `parts.py`, `check_spine.py`, `look.py`, `deploy.py --json` | the deploy never shows as done (UX-6), the text lacks the next step that `--json` has (UX-7), the next step lacks its script (UX-4) |
| other harnesses | the same chat in another tool, reads "Ask Claude" (UX-5) | the scripts and Markdown, no slash commands, no `allowed-tools`, no agent files (UX-8) | the knowledge sits in Claude Code formats, the page has no carrier (UX-9) |
| a local AI | the same as above, with a smaller model | must fit a 64k-word guide into a small context (UX-3), many exceptions (UX-11) | the knowledge has no short layer, this is H until a local model is tried |
| evaluation and self-improvement | wants to see whether spark got better (UX-14) | no eval reads whether an agent succeeds from the pages alone (#1522 comment, 16:0x CET, P711) | the inventory counts the wrong audience and is no gate (UX-1) |

## 2. What I could not check, and why

- I did not run `look.py`, `deploy.py`, `grant.py`, `reach.py` or `live.py`. They touch a board on USB, and the order
  was read-only, with no flash. I read their `--help` and the guide.
- I did not open a published page Artifact, so I did not compare the page with `flow.py page --json` field by field.
  The comparison rests on `flow.py --help` and `commands/page.md`.
- I did not try any harness other than Claude Code, or any local model, on spark's pages. Whether a weaker model
  follows them is H.
- I counted words, not tokens.
- I read `commands/idea.md`, `commands/page.md`, `skills/spark-design/SKILL.md` and `docs/guide/agents.md` in full. I
  read the other command, skill and agent files by grep and in parts.
- I did not read the walk diaries of P934 (#1323) for the bench surfaces, so UX-13's judgement about which surface
  serves best stays H.
- I did not check whether `bench.py`'s deploy records name the sibling project, so UX-6 says only that `flow.py`
  cannot show a deploy, not that this project was deployed.
- I read the MCP elicitation page at version 2025-11-25. The search also listed a 2026-07-28 page, which I did not read.

## 3. Questions for the decider

- Which pages count as the agents' knowledge (commands, skills, agent files, AGENTS.md, docs/guide/agents*)? Do you want
  the hook to fail on a new script, flag, exit code, `code` or JSON key until one of these pages names it? · decides: the guard in the
  other direction for theme 3, and whether `tools/inventory.py` becomes a gate with the audience split.
- What is the floor model for the AI interface: Claude Sonnet, a local model of a stated context size, or "any MCP
  client"? · decides: the size of the guide's short layer, whether every CLI gets `--describe`, and how many
  exceptions in the envelope must go.
- Do you want the core's sentences to name a role ("your assistant", "the agent") instead of "Claude" and
  "/spark:page"? Each harness adapter then fills in its own words. · decides: whether flow_codes.py and the `by` values are a seam of the
  core or of the interface.
- Do you want a recorded deploy to count as the deploy phase done in `flow.py`, the page and `--json`? · decides: whether the
  factory line's end state is visible to both the person and the agent.
- At the bench, which surface comes first: the terminal (P1032 and its follow-ups), the page's wiring steps, or the
  sheet? · decides: the order of human-interface work after P1032.
- Can an MCP elicitation "accept", or a click on the page, ever stand for the person's yes to a flash? Or does that yes
  stay a word typed in the person's own terminal? · decides: how far the page and an MCP adapter reach into the bench.
- What number does the PO want to see per release: steps reached through spark's own pages alone, the count of
  interventions, minutes, cost, or a mix, and where does it show (the journey picture, a page, the README)? · decides:
  the shape of the evaluation epic and what P711's walk records.

## 4. Searches

- "MCP specification elicitation requestedSchema server asks user structured input" · the decision it served: whether
  an MCP adapter can carry spark's `needs_reply` questions without a new shape (question c) · used (UX-10), page read:
  https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation, 2026-11-23.
- "Agent Skills open standard SKILL.md supported agents list" · the decision it served: whether spark's skills and
  commands are readable by harnesses other than Claude Code (questions c and d) · used (UX-3, UX-8), page read:
  https://agentskills.io/home, 2026-11-23.
- "Hermes Agent Nous Research skills SKILL.md agentskills.io compatible" · the decision it served: whether Hermes, the
  harness the PO named on #1522, reads spark's skills, commands or agent files · used (UX-8), page read:
  https://hermes-agent.nousresearch.com/docs/user-guide/features/skills, 2026-11-23.
