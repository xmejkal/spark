# P1194 settings in layers: the refuter

The refuter, on Opus, 2026-11-26, read-only. The worktree is at 1f57256e (the code is main 43bea346). Experiments ran
with `SPARK_HOME` set to an empty folder under /private/tmp/claude-501/p1194-refuter, which is deleted at the end.
The projects under ~/Development and the store were read, never written. Bytecode that my Python runs left in the
worktree's `scripts/` was deleted, and `git status` is clean. Nothing here is decided.

## Check first: the existing product

Does the change address the observed problem? Only in part. The evidence shows three separate small defects, not a
missing layered model:
- a hand-written brief value that spark drops without a word (smartbin-local, ★C4). The fix is I6 alone.
- a project's tools file that can redirect a role and blank `account_env` (★C5). The fix is I7 alone.
- one choice made run by run (P410 #536). One kept setting fixes it.
The one piece of evidence for a person layer (★C3, the shops) is a rule that already works through CLAUDE.local.md.
No observed case shows a person who could not find whose word a value is (A1 is H).

What breaks for current users if the options are taken as proposed:
- /spark:setup and tools.py. Q2 (a) drops "personal" and the PO's "global" for new words. Then `tools.py --personal`,
  the status header "personal: <store>" (scripts/tools.py:34, 57) and commands/setup.md:79 ("A choice is the
  person's own by default") all need new words in the same change, or two words name one thing. If the default write
  layer flips to "this project" (verification.md, the second split), setup.md:79-82 is wrong.
- The tools list. I7 and Q3 (a) refuse or flag a project-set role or field. Then the documented
  `use simulator=my-sim --project .` and "A pin is usually the project's" (setup.md:70, 80) change. Two walks set a
  MicroPython download in their own `.spark/tools.json` today (spark-walks/walk4 and p581-sound-joystick: `file`,
  `url`, `sha256` of an octal-SPIRAM build). A rule that limits a project's tool fields breaks both. Nothing in Q3 or
  Q6 names them.
- The brief's `prefer` and `sellers`. Q5 (a), "refuse", stops smartbin-local's part search. Today it runs on the
  default. Slice 5 gives the person layer the five shops. Then the 21 of 24 briefs with no `sellers` change their
  answer from "no sellers named" (brief_choices.py:24-27) to his five shops, with no line in their own files. That is
  the J3 harm that the epic is meant to stop.
- No question asks where a project's vendor order and shops live after the move. Today they are fields of
  `.spark/project.json`. That file is the brief: PROJECT_TEMPLATE, `answers_in` (project_setup.py:343-377), P1027's
  commit and the spark-review skill read it. TL-12 proposes `.spark/settings.json` beside it. If `prefer` stays in the
  brief and the seam reads a settings file too, one value has two homes. Open question 4 of the frame ("beside
  .spark/tools.json or inside it") does not cover project.json.

## 1. Claims

Each line: the claim, the line I read (verbatim), the verdict, and the change for partly or refuted.

- ★C1 · scripts/spark/records/tool_finder.py:92: `"""The three layers as one list: tools merged field by field,
  roles key by key, the project winning."""` and :102-103: `raise ToolError("%s: the entry %r is not an object", ...)`.
  Verdict: partly. The merge and its refusal hold. "One layered setting" does not: the vendor order is already two
  layers, the project's brief over spark's default (brief_choices.py:19: `return
  Brief.from_project(project).prefer or DEFAULT_VENDOR_ORDER`), and TL-20 says so. Change to: "The tools list is
  spark's only setting with a person layer: three files merged field by field, the project winning. The vendor order
  has two layers, the brief over spark's default."
- ★C2 · council/po-assistant.md:10: "PO-1 · Nobody is blocked without the seam today." #1752 body: "the settings the
  discovery names, which move into P1194 #1740 when it exists". #536 and #470: state OPEN (created 2026-10-25 and
  2026-10-20). Verdict: holds, as a statement about the backlog. Caveat kept: #536 says "Needed by v0.10, between
  Simulate and Bench", and USER-15 shows the choice made by Claude at the bench, so "not blocked" is not "no friction".
- ★C3 · My count, read-only, of every `.spark/project.json` to depth 4 under ~/Development: 24 files, and `sellers`
  in 3: irrigation `['laskakit', 'gme', 'hadex', 'botland', 'tme']`, spark-quickstart (the same), spark-walks/
  reaction-game `['gme', 'hadex', 'laskakit', 'botland', 'tme']`. `ls ~/.local/share/spark/tools.json`: "No such file
  or directory". Verdict: partly. The count reproduces. "The PO repeats" is not shown. irrigation's commit da6b0c7
  (2026-09-29) is titled "Research launched; the PO's local-sellers rule, and I2", so the list came from his rule,
  which CLAUDE.local.md holds, and likely Claude typed it. 14 of the 24 are spark-walks, and spark-quickstart is a
  walk of the quickstart. Change to: "3 of 24 briefs found under ~/Development (14 of them walks) carry the same five
  shops, the list his CLAUDE.local.md gives Claude; who typed them is not known, and his store has no personal tools
  list."
- ★C4 · scripts/spark/records/brief.py:25-29: `"""A non-empty list of strings as a lower-cased tuple, else None."""`.
  smartbin-local/.spark/project.json: `"prefer": "reuse what I already own before buying"`. Verdict: partly. The drop
  is real. But spark's own write path already refuses that value: project_setup.py:357, `"prefer": ("a list of
  texts", texts)` in `answers_in`. The brief was written by hand on 2026-09-24 (commit 0e8f8d8, "The bin gets a brief
  and a findings file"), before that check. Change the caveat to: "one project, written by hand before
  `init_project.py --answers` refused such a value; only a hand edit reaches it today."
- ★C5 · My scratch project, `.spark/tools.json` = `{"roles": {"simulator": "my-sim"}, "my-sim": {"kind": "path",
  "exe": "sh", "meets": ["wokwi-project"]}}`. `tool_finder.find('simulator', 'proj')` printed `Tool(name='my-sim',
  role='simulator', entry={...}, command=['/bin/sh'])`. scenario_run.py:273-274: `token =
  simulator.entry.get("account_env", "WOKWI_CLI_TOKEN")` / `if token and not os.environ.get(token):`. Verdict: holds.
  Two narrowings the line should carry: the redirect is the documented `use simulator=my-sim --project .`
  (setup.md:70, 79-82), and an entry with no `account_env` still gets the token check (the default is
  WOKWI_CLI_TOKEN); only an explicit empty string skips it.
- ★C6 · tool_finder.py:359-362: `if entry.get("needs_account") and not os.environ.get(entry.get("account_env") or "",
  ""):` / `rows.append(("person", label, "needs " + entry["needs_account"]))` / `if entry.get("needs_hardware"):` /
  `rows.append(("person", label, "needs " + entry["needs_hardware"]))`. Verdict: partly. The `[!   ]` rows are two
  kinds, an account and an instrument (data/tools.json:258, sigrok). Every `[????]` row also repeats on each status
  until the tool is installed, and setup.md:39 asks once before an install. USER-14 says the precedent "covers missing
  tools, not missing choices"; the brief narrows it to one row. And "every other missing value takes the default" is
  wrong for sellers: a missing `sellers` gives `()`, "no sellers named" (brief_choices.py:24-27), not a default.
  Change to: "'Asks until set, like the tools list' holds for missing tools and for a missing account or instrument,
  never for a missing choice: a tools-list field falls back to data/tools.json, and nothing asks."
- ★C7 · #1740 title: "one settings seam with layers (global, user, project, more to refine)". #1740 "Done when": "at
  least global, user and project". The PO on #1738 P2: "some general settings and some per user settings, per
  project". VS Code page: "These settings apply globally to any instance of VS Code you open." git help config
  (2.49.0), line 344: 'These are also called "global" configuration files.' Verdict: refuted as written. "Global" and
  "user" are two names from the card, not spark's product, and the card lists them as two layers. PO-8 itself says
  "whether 'global' means spark's defaults, the machine or the person is the decider's". In the product the names are
  three: "personal" (tools.py:34, 57), "the person's" (setup.md:11, 79) and "the store" (store.py). Also, git's and VS
  Code's "global" mean the same thing (one user's settings), so outside it is two meanings, not three. Change to:
  "Spark's product names the person's layer three ways (personal, the person's, the store). The card adds 'global'
  and 'user' as two layers, and it is not known whether 'global' means spark's defaults, the machine or the person.
  Outside, 'global' is one user's file in git and VS Code and the machine in npm."
- ★C8 · scripts/tools.py:10: "A choice is written to the person's file, or to the project's with --project
  (--personal overrides)." commands/setup.md:79: "A choice is the person's own by default." Verdict: holds, with one
  narrowing: it reaches every project whose own `.spark/tools.json` does not set the same field (setup.md:80-81).
- ★C9 · `SPARK_HOME=<empty> scripts/tools.py --status --json`: "tools.py: error: unrecognized arguments: --json",
  exit 2. scripts/init_project.py:7: `init_project.py --project . --answers answers.json   # the brief's answers, in
  the person's words`; project_setup.py:357: `"prefer": ("a list of texts", texts)`, and :358 `"sellers"`. Verdict:
  refuted in part. The `--json` half holds. "The vendor order, the shops ... have no command" is false: `init_project.py
  --answers` writes `prefer` and `sellers` from the terminal, at the project layer. USER-23, which the claim cites,
  says so: "The brief changes only through `init_project.py --answers` with a temp file". P410's check has a per-run
  flag, `deploy.py --no-simulation`, and no kept value. Change to: "`tools.py` has no `--json`. The vendor order and
  the shops change only per project, through `init_project.py --answers`; P410's check is a flag per run with no kept
  value; no command writes a personal default for any of them."
- ★C10 · scripts/spark/flow/run_request.py:4-5: "The values of the step come from spark's own offer key, never from
  the request." :44: `STEP_OPERATIONS = {operation.name: operation for operation in (PickParts, WriteRequirements,
  BuildBoard)}`. Verdict: holds. The pointer has drifted: the allow-list is at 42-44, not 38-41. Change "1-5,38-41" to
  "1-5,42-44".
- ★C11 · scripts/spark/core/replies.py:31: `YES_NO, VALUE, CHOICE = "yes_no", "value", "choice"`;
  docs/guide/agents/replies.md:24-25: "The status is `could-not-run` and the exit is 2 while a question is open."
  Verdict: partly, on the caveat. replies.md:5-6 says `look.py` asks too, and deploy, grant and live ask through the
  same kind of reply (replies.md:97, 117, 143). So the replies file is not "research's own". The look keeps its board
  in the store after the answer ("asks once and keeps the board", replies.md:93), so one answer is already written to
  a lasting place; TL-10 names that exception and the brief drops it. Change the caveat to: "the project's replies
  file is research's; the look, deploy, grant and live ask too, and only the look keeps an answer (the known board in
  the store)."
- ★C12 · git help config, Protected configuration: "For security reasons, certain options are only respected when they
  are specified in protected configuration, and ignored otherwise." VS Code page: "application-wide settings related
  to updates and security can not be overridden by Workspace settings." Claude Code settings reference, `modelPicker`:
  "ignores it in project and local settings so a repository you clone can't relabel the picker." Verdict: holds.
- ★C13 · board_grant.py:98-99: `DEPLOY_QUESTION = ("let Claude erase ALL of the flash of the board %s (token %s) and
  write any passed image of any " "project, with no yes from you for each deploy, for %d minutes from your yes?")`.
  :211-212: `"""True only when no file is at grants/direct_flashing_disallowed (P1029). It fails closed: a file, a
  folder or a dangling link there, or a grants place spark cannot search, disallows direct flashing."""`. Verdict:
  holds. Caveat to add: "fails closed" covers an odd file or an unreadable place only. With no file, direct flashing is
  allowed (`except FileNotFoundError: return True`), and that is the default (inventory row, "absent, so allowed"). The
  artboard gets this wrong (part 5).
- ★C14 · plugins-reference, read 2026-11-26: "The variables aren't present in the environment of commands Claude runs
  through the Bash tool, in the main session or in a subagent." That sentence closes the section on the three path
  variables (CLAUDE_PLUGIN_ROOT, CLAUDE_PLUGIN_DATA, CLAUDE_PROJECT_DIR). On option values the page says:
  "`${user_config.KEY}`: substituted in MCP server config, LSP server config, exec-form hook `args`, and skill and
  agent content", and "`CLAUDE_PLUGIN_OPTION_<KEY>`: exported to hook processes for every option". Verdict: partly.
  Option values are not exported to Bash, which holds. But a skill can write a non-sensitive value into the command
  line it gives Claude, so a script can receive it as an argument. PO-14 says the values "reach skill and agent text";
  the brief drops that. The lasting reason is the other one: spark's scripts must run outside Claude Code
  (docs/guide/agents/scripts.md). Change to: "Claude Code's plugin `userConfig` values are not in the environment of a
  Bash command; a skill could pass a non-sensitive one as an argument, but a script run outside Claude Code gets none,
  so it cannot be spark's store."
- ★C15 · council/tech-lead.md:13-15: "TL-1 · Only P410's setting (which check firmware gets before the board) is on the
  bar's path. ... P368's vendor order is on the path but small: it orders the part search." Verdict: refuted. The
  source names two settings on the path, and the claim keeps one. Change to: "Of the candidate settings, P410's check
  is on the bar's path, and P368's vendor order is on it but small (H, the tech lead, TL-1)." Q7 (a)'s caveat "not on
  the bar" changes with it.

## 2. Summaries

What the brief dropped or made stronger than its source.

- D1 (Frame and Decisions) drops two of the PO's words. #1738 P2 and #1740 say "global/per project/per account" and
  "some general settings and some per user settings", and "Done when" says "at least global, user and project". D1
  says "global, per project, per account". The "user" layer and "for new projects" are gone. P1193's D8 records
  "(global, user, project, account, more to refine)".
- D2 is stronger than its source. "What syncs to the public is a setting, none by default" is not the PO's word. On P4
  he wrote "Most probably 1, but also, why not vendor images? ... its another great example aof configurable settings"
  (#1738 comment), with no default. P1193's merged brief then decided the default (D10, D11): "records and drawn
  pictures, including drawings traced from his own or a vendor's photo, and no photos" (origin/main,
  docs/discovery/2026-11-26-p1193-change-tracking/brief.md, the settings table). D2 contradicts that table.
- Outcome drops PO-16: "the walk needs all three built or moved first; it cannot run on today's code." The outcome
  reads as if the walk can run.
- ★C3 drops USER-3's other reading ("or Claude carries it from memory") and the walk share of the 24.
- ★C6 drops USER-14's "the 'like today' precedent covers missing tools, not missing choices".
- ★C7 drops PO-8's "#1740's 'Done when' lists 'global, user and project' as separate layers" and "is the decider's".
- ★C11 drops TL-10's exception, the look's known board in the store.
- ★C14 drops PO-14's "The values reach skill and agent text, hooks and MCP or LSP config".
- ★C15 drops TL-1's "P368's vendor order is on the path but small".
- Options, Q2 (a): "opinion (the user lens, USER-10; the PO assistant, PO-8)". PO-8 proposes no words; it says
  "whether 'global' means ... is the decider's". USER-10 is H from model knowledge, "Search budget: none".
- Options, Q3 (a): "opinion (all three lenses: USER-12, TL-15, PO-9)". Only TL-15 recommends. PO-9 "supports only: a
  per-setting list ... is the common pattern; which spark settings get it is open". USER-12 ends in a question.
- Options, Q4 (b): "opinion (none)". That option is the PO's own D1 ("asks until set"). Q4 (a) reopens D1, and the
  brief does not say so.
- Options, Q7 (b): USER-15 is an account (n = 1, one bench), not an opinion that P410 goes first. Q7 (c): TL-20 says the
  author identity "is the only one that tests the ask-until-set path"; it does not recommend it first.
- Options, Q9 (a) and verification.md "Agree": TL-22 recommends "no account layer yet. When it comes, read its
  identity from (c) [git] or (e) [GitHub], and carry its values with (d)". It does not make a GitHub sign-in the first
  candidate. Only PO-10 does.
- Options, Q11 (b): "opinion (the tech lead, TL-18)". TL-18 "supports only: an order dependency"; it recommends nothing.
- Options, Q6 (b): "large (5 caller modules)". The grep in TL-3 finds 5 files, and one is tool_finder.py itself, so 4
  callers. 32 files under scripts/ name tool_finder. "5 caller modules" is neither count.
- Proposed no-gos: "no word 'global'". It is the PO's own word in #1740 and in P1193 D8. As a no-go it decides Q2.
- Riskiest test, task 2: "say why smartbin-local used DFRobot". Its premise is not shown. smartbin-local's DFRobot
  parts are in its `decided` list from owned parts ("the board is a DFRobot FireBeetle 2 ESP32-S3, not the XIAO
  ESP32-C6 on hand"; "B1 confirmed the DFR0954 on 2026-10-06 from the DFRobot order history"), not from the vendor
  order. A walk graded on "the default vendor order" would mark a right answer wrong.
- risks-and-tests.md, A2: the pass line "3 or more projects repeat a personal choice, set 2026-11-26" was set on the
  day the count of 3 was already seen (★C3). It is not "dated before any result"; it passes by construction.
- jobs-and-journeys.md, J5's "today": "E the inventory in council/ (to come)". The inventory exists; the line is stale.
- jobs-and-journeys.md, J1's "today" cites tool_finder.py:92 for "the tools list sits in the store". Line 92 is the
  docstring of the merge; the store's file is PERSONAL at :42.
- items.md, I7's proof, "a scratch project's redirect is refused or named before use", sits beside Q6 (a), which keeps
  the tools list as it is. "Refused" breaks the documented `--use ... --project .`; only "named before use" fits Q6 (a).
- verification.md, "Split, settled: ... The facilitator counted 3 of 24 briefs". No command or depth is recorded, so the
  settle cannot be rerun at the decision as A2 asks.
- Found on the way, F1 and ★C5 are the same claim twice. F2 rests on ★C4 and needs ★C4's new caveat (a hand edit only).

## 3. Rival explanations

- ★C3 and A2 (a personal layer saves repeats). Rival: Claude copied the shop rule from CLAUDE.local.md into three
  briefs. The person layer already exists as that file, and it works. 21 of 24 briefs name no shops, so shops may
  matter only in the few projects that bought parts. Not ruled out: no commit or session shows who typed the lists.
- The two MicroPython overrides (USER-3, PO-2). Rival: they are a per-board choice (an S3 with octal SPIRAM), so they
  belong in the project layer. They are evidence for the project layer, not for a missing person layer.
- ★C4 and I6. Rival: a legacy, hand-written field from before P1027's check, and a field misuse (a reuse wish in a
  vendor field, which the drawer serves). It is not a live path by which a person's value is lost. Not ruled out: no
  second project shows it.
- ★C5, Q3 and A6. Rival: a cloned project is already trusted far more than its tools file. Its firmware is flashed, and
  its `package.json` can run npm scripts on install. The role redirect is the documented `--use ... --project .`. The
  marginal exposure may be small next to that. Not weighed anywhere in the folder.
- ★C7 and Q2. Rival: "global" in the PO's words means spark's defaults or "general settings", and "user" means the
  person. Then there is no naming clash to fix; the card already has two names for two layers.
- ★C8, USER-1 and USER-2. Rival: the person default is a deliberate rule (setup.md:79), and nothing shows it bit him.
  His `--scope local` rule is for Claude Code's MCP servers, not for spark's tools list.
- A1 (a person looks on a page). Rival from the folder's own evidence: he asks Claude, and Claude chose at the bench
  (USER-15). show-settings in the chat may serve J3 with no page. The riskiest test can only show the artboard is
  readable, not that he would open it.
- ★C2 (nobody blocked). Rival: P410 is needed by v0.10 (#536) and was not pulled because nothing made the run-by-run
  choice visible as a problem. "Not pulled" may mean "not seen", not "not needed".
- The epic as a whole. Rival: the observed evidence is three small defects (I6, I7, one P410 setting), each fixable
  without a layered seam. The seam's need rests on D1 (the PO's word), not on observed failure. That is a valid basis,
  but the brief should say it is the basis.
- ★C15. Rival: the vendor order is on the bar too (TL-1), so Q7 (a) is not "off the bar".

## 4. Numbers

- "3 of his 24 project briefs" (★C3, A2, the artboard). Population: `.spark/project.json` files found under
  ~/Development and spark-walks, depth not recorded (I found 24 at depth 4). 14 are walks. Period: briefs written from
  2026-09-24 on, not stated. Provenance: "the facilitator's count", no command. PO-2 counts 23 present of 28 in
  projects.json; USER-3 counts 2 of 23.
- "28 projects, 23 folders present" (PO-2): no date range; the projects.json read is not quoted.
- "5 caller modules" (Q6 b, TL-3): 4 callers plus tool_finder itself, by `grep "setter_of\|merged("`; no unit says
  "modules that call the merge" against "modules that call find".
- "14 roles" (inventory) and "14 jobs" (artboard): reproduced, 14 keys in data/tools.json's `roles`. Holds.
- "8 H" (Stands on): eight assumptions, A1 to A8; the H is a tag, not a unit. Fine, but none is rated.
- A1's "3 of 3", A3's "4 of 4", A8's "3 runs": n = 1 (the PO), one sitting, no period. A2's "3 or more": see part 2.
- "about 90M input tokens", "6 agents, 499 calls" (brief comment): one rehearsal on 2026-10-06; fine as a one-off.
- "1440 minutes" (PO-13): the cap, MAX_MINUTES = 24 * 60 (board_grant.py:76). Holds.
- PO-4's "P1193's table holds 7, of which 6 are proposed for the user layer": reproduced from origin/main's table.
- The artboard's "25 minutes left", "more than 5 minutes" and "six rules": see part 5. The first two have no source.

## 5. The artboard

Settings.dc.html (in the session's scratchpad, modified 12:49, before D7 to D9). Each item: the words, what is wrong,
and the change.

- Line 123: "The values are examples from your projects." Several are not. No project has P410's check set (it does
  not exist), no store holds a personal shop list (★C3: none), the grant's "25 minutes left" and the token's "Set" are
  invented. Change to: "The values are made up to show the layout; only smartbin-local's vendor order is read from a
  project."
- Line 205: `['clock', 'The clock (p934-epaper)']`. p934-epaper's brief goal is "a drawing app that uses joystick to
  paint n the eink display". The clock is p934-display and p934-display2 ("It should just display clock"). Change the
  label to the project it names, or the project to the clock.
- Line 182: "If the switch is missing or cannot be read, the answer stays 'not allowed'." False. With no file,
  direct flashing is allowed (board_grant.py:215-216, `except FileNotFoundError: return True`). His grants folder holds
  two deploy grants and no `direct_flashing_disallowed`, so his value today is "allowed", and line 181's "Not allowed"
  is not his state. Change the note to: "Direct flashing is allowed until you turn it off. If the switch is there but
  odd, or its folder cannot be read, it reads as not allowed." Change the value to "Allowed" or mark it an example.
- Lines 166-169: "Pictures on the shared side", value "None", who spark's default, and "Whether a drawing traced from
  your photo may be shared is still your question in P1193." Both refuted by P1193's merged D10 and D11: a drawing
  traced from his own or a vendor's photo can be shared by default, and photos stay local. Change the value to
  "Drawings spark made, also traced from a photo; never a photo" and drop "still your question".
- Lines 28-31 (the four layer cards) and 33 ("The nearest word wins: this project, then yours, then spark's default").
  This decides Q2 (a) and drops "global" and "user", the PO's words in #1740. Q2 is queued. Mark the four words "a
  proposal for Q2", or show the card's words beside them.
- Line 31, "your account: Later, after a sign-in: it follows you", and line 119, "for example with GitHub". This
  decides Q9 (queued), and Q12 (a second computer) is unasked. D6 supports "later" and "GitHub, optionally". It does
  not support "it follows you" as the account's job. Add "a proposal for Q9".
- Line 33: "A setting that spends your money or shares your data is yours alone. A project cannot set it". Line 120:
  "It never lets a project widen what is shared or spent." The rows' "allowed" cells (lines 142, 147, 154, 159, 164,
  168, 173). Together they decide Q3 (a) and TL-15's per-setting split, which is H. Mark them "proposed (Q3)".
- Lines 37-38: "Who signs your shared parts? ... Spark asks once and keeps your answer for all your projects on this
  computer." Line 170: "Not set: spark asks once". This decides Q4 (a) against D1's "asks until set". P1193 D8 says
  his git identity signs "by default ... and spark asks until it is set". It also puts an Idea-stage feature (P1203
  #1752, sharing) in the "Now" slot as if it existed. Change to "Spark will ask before your first share (Q4: once, or
  until set)" and label the panel "an example".
- Line 43: "Claude shows the change first and writes it after your yes. Your answer is never written into a project."
  The first sentence is Q8 (a), which the brief and line 121 keep open. The second decides TL-13's layer rule. Mark
  both proposals.
- Line 140-143: the check before the board. Default "Free checks, then ask" (`l1`) and the clock's "Put it on the
  board: no simulator covers it" are shown as values. #536 says the default is "To refine with the PO", and no
  project holds this setting. Line 99 repeats it in the fold. Mark "example" and "default to decide (#536)".
- Lines 144-148: "Paid simulation minutes", default "Ask before every paid run", project "not allowed", "you only: it
  spends money". This decides Q10 (queued). P1190's D13 is in a draft PR (#1742) and may still change (PO assistant,
  "could not check"). The sentence's "more than 5 minutes" has no source. Mark it.
- Line 153: Vendor order, "The order in which spark looks at sellers' catalogues for a part." Wrong. The vendors are
  module makers whose wikis spark reads ("Whose modules to research first", PROJECT_TEMPLATE; "DFRobot first because
  its wiki carries a pinout table", brief_choices.py:11-12). Sellers are the shops of the next row. One word for one
  thing breaks here. Change to: "Whose modules spark researches first, in order."
- Lines 150-151 and 155 (smartbin-local): "this project: not used", "so spark used its default", and the sentence "my
  words about reuse are a wish, not a vendor list. Keep spark's vendor order and note the wish." This shows Q5 (b), use
  the default and say so, while the PO assistant proposed (a), refuse. Q5 is queued. It also puts words in his mouth
  about his own intent. Mark "Q5 open" and drop the interpretation from the sentence.
- Lines 156-158: Shops, value "GME, Hadex, LaskaKit, Botland, TME", who "yours". No person layer holds this today;
  it is CLAUDE.local.md. "3 of your 24 project briefs repeat it" carries ★C3's missing population (14 walks) and who
  typed them. "Here it is one setting for every project" decides slice 5 and Q7's order. Mark the value "example"; say
  "3 of 24 briefs found, 14 of them walks".
- Lines 179-184: who "this computer" on three rows. That is a fifth word beside the four layer cards (line 29 says
  "yours, on this computer"). It is Q2 (c)'s fourth layer in effect, while the cards show (a). Use one word.
- Line 177: "It moves onto this page later." Q6 asks only about the first slice; this decides the later move. Mark it
  a proposal.
- Line 108: "Two Operations do all of it." The Operations do not exist, and TL-23's question "Are show-settings and
  set-setting the whole Operation surface" is not in brief.md's queue at all. Change to "Two Operations are proposed
  to do all of it", and add the question to the brief.
- Line 115: "A setting with no value asks through spark's usual question (exit 2), in each interface in its own way."
  This decides how asking works (TL-23, H). Fine as a proposal; mark it.
- Line 123: "the user and tech lead lenses are read, the rest of the council follows." Stale: the PO assistant's
  report and D7 to D9 came after. Update the line.

## Searches

none
