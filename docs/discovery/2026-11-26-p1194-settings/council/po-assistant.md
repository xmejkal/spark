# P1194 settings in layers: the PO assistant's findings

The PO assistant, on Opus, 2026-11-26, read-only. Main at 43bea346 in the worktree `spark-p1194-settings`; P1193's and
P1190's discovery files read on `origin/main` and `origin/p1190-simulation`. The person's store was read, never
changed. D6 (the PO, about 12:45 CET, relayed by the coordinator) arrived during the work and is answered in PO-10 to
PO-12. Tags: E with a pointer, H with its source, D with who and when, — for an unknown. Nothing here is decided.

## 1. Findings

PO-1 · Nobody is blocked without the seam today. P1193 lists seven settings with a proposed layer and says "Today the
tools list's roles hold the first two … They move into P1194's seam when it exists". P1203 #1752 says the same ("move
into P1194 #1740 when it exists"). P410 #536 (open since 2026-10-25) and P368 #470 (open since 2026-10-20) were never
pulled. · E · `origin/main:docs/discovery/2026-11-26-p1193-change-tracking/brief.md:141-153`; `gh issue view 1752`
body; `gh issue view 536`, `470` state OPEN, read 2026-11-26 · supports only: the seam is not on the MVP's critical
path; the cost of waiting is more places to move later, not a stopped feature.

PO-2 · The person repeats the same personal choice project by project, which is J1's pain, seen in his own data. In
the store's `projects.json` (28 projects, 23 folders present), 3 projects carry a `sellers` list in
`.spark/project.json`, each the same five Czech and EU shops (in two orders), the list his `CLAUDE.local.md` states
for every project ("prefer Czech and EU shops: GME, Hadex, LaskaKit, Botland, TME"). One project sets `prefer` to
spark's own default. No personal `tools.json` exists in the store: he never set a personal tool choice. Two projects
override one tool entry each (the same MicroPython build). · E · a read-only Python count over the store's
`projects.json` and each project's `.spark/project.json` and `.spark/tools.json`, 2026-11-26;
`ls <store>/tools.json`: "No such file or directory" · supports only: a personal default for sellers would have saved
three repeats for n = 1; the per-project layer was used twice in 23 projects; nothing about the hobbyist.

PO-3 · A value of the wrong shape is ignored without a word, so the person's choice silently becomes the default. In one
project `prefer` holds a sentence ("reuse what I already own before buying"); `Brief._names` keeps only a non-empty
list of strings and returns None otherwise, so `vendor_order` answers spark's default `("dfrobot", "seeed")` and
nothing says the brief's words were dropped. · E · `scripts/spark/records/brief.py:25-29,62`;
`scripts/spark/sourcing/brief_choices.py:13-19`; the count in PO-2 · supports only: the seam needs a rule for a value
it cannot read (refuse and say, never fall back in silence). Also filed under "found on the way" by the facilitator if
wanted; this report files nothing.

PO-4 · Demand for settings grew sharply in one day, all from one person. On 2026-11-26 three discoveries named
settings: P1193's table holds 7, of which 6 are proposed for the "user" layer and 1 for "project, then user"; P1190's
D13 adds a paid-run policy ("a threshold for example when it should warn and not run the payed ones by default … or
it can always ask"); P1194 itself. Before that day two cards asked (P368, P410). · E · P1193 brief.md:141-153 as in
PO-1; `origin/p1190-simulation:docs/discovery/2026-11-26-p1190-simulation/brief.md:21,102,118` · supports only: the
count of candidate settings and their proposed layers; not that anyone but the PO wants them.

PO-5 · Spark already has a working three-layer model, the tools list: spark's defaults (`data/tools.json`), the
person's (`<store>/tools.json`), the project's (`.spark/tools.json`), merged field by field with the project winning;
one field is written to one file; `setter_of` names the file whose value wins; the status line prints both file
paths; `off_sentence` tells the person where to change it. · E · `scripts/spark/records/tool_finder.py:39-44,91-120,
264-282,508-518,531-538`; `scripts/tools.py:10,34,56-57` · supports only: the merge, the "which layer set it" answer
and the one-field write can be reused as the seam's shape; it holds tools only.

PO-6 · "Asks until set, like the tools list of /spark:setup does today" (#1740's body) is true for one row only. A
tool field with no value falls back to `data/tools.json`; nothing asks. The nearest is the `[!   ]` row: while
`WOKWI_CLI_TOKEN` is empty, every `--status` repeats "needs a Wokwi token …". · E · `tool_finder.py:359-362`;
`data/tools.json:54-55`; `commands/setup.md:20-21`; `gh issue view 1740` body, read 2026-11-26 · supports only: "ask
until set" is new behaviour to design, not a move of existing behaviour.

PO-7 · Git has the exact precedent for "asks until configured": with `user.useConfigOnly` true, git does not guess the
author and "will prompt you to set up an email before making new commits in a newly cloned repository". P1193's
author setting (default "the person's git identity, asked until set") can lean on it. On this Mac `user.name` and
`user.email` are set at global scope only. · E · `git help -m config` (git 2.49.0), lines 7132-7139 of the rendered
page, read 2026-11-26; `git config --show-scope --get-all user.name` → `global`; P1193 brief.md:148 · supports only:
one setting's ask can be git's own; it says nothing of the other settings.

PO-8 · "Global" means three different things in the tools the PO uses, and #1740's "Done when" lists "global, user
and project" as separate layers. Git's "global" is the person's file (`~/.gitconfig`, "also called global"); npm's
"global" is machine-wide (`$PREFIX/etc/npmrc`), with a separate "per-user" `~/.npmrc` and an unchangeable "builtin"
file; VS Code says user settings "apply globally". In spark today there is no machine-wide layer apart from the
person: the store is per OS user (`$SPARK_HOME`, then `$XDG_DATA_HOME/spark`, then `~/.local/share/spark`), and
spark's defaults live in the plugin. · E · git help config, FILES and SCOPES, lines 332-405; npm 10.9.8's own
`docs/content/configuring-npm/npmrc.md` (installed with npm), "Files"; https://code.visualstudio.com/docs/configure/settings,
read 2026-11-26; `scripts/spark/records/store.py:59-65`; `gh issue view 1740` · supports only: a names check (one
word for one thing) before any design; whether "global" means spark's defaults, the machine or the person is the
decider's.

PO-9 · Every outside tool limits what a project's file may set, and spark's tools list does not. Git respects some
options only in "protected configuration" (system, global, command), "This prevents untrusted repositories from
tampering". VS Code: "application-wide settings related to updates and security can not be overridden by Workspace
settings"; `git.path` and `terminal.external` "can only be defined in user settings"; Restricted Mode disables
workspace settings that point to executables. Claude Code ignores `modelPicker` in project and local settings "so a
repository you clone can't relabel the picker", and `pluginConfigs` has scope "User or managed". Spark lets
`.spark/tools.json` name install commands and win over the person, and guards it only by a sentence before the yes. ·
E · git help config lines 410-421, 6191-6193; https://code.visualstudio.com/docs/configure/settings and the search
result for Workspace Trust, read 2026-11-26; https://code.claude.com/docs/en/settings-reference (first 100,000
characters), read 2026-11-26; `commands/setup.md:39-41,79-82` · supports only: a per-setting list of the layers that
may set it is the common pattern; which spark settings get it is open.

PO-10 · The account layer (D6: a seam now, sign-in and account management later). Four readings of "per account
logged in", what each lets a setting follow, and what it costs:
- (a) The OS user. Exists today: the store is per OS user (`store.py:59-65`). Follows nothing to another machine. No
  new service, no sign-in, nothing to manage. · E
- (b) A GitHub sign-in. `gh` is signed in on this Mac, token in the keyring (`gh auth status`, 2026-11-26). P1193
  already puts the shared records in "a new public repository under the person's account, made by spark" and signs
  commits with the person's git identity (P1193 brief.md:148,150; #1738 comment of 2026-11-26 11:17, P3 to P5). A
  private repository or the same git strategy could carry personal settings to a second machine. No new service and
  free; GitHub keeps the password, 2FA and deletion. It matches D6's words ("github sign in, optionally … create
  projects, access the parts, suggest edits"). Costs: a second, private place (the shared repository is public), a
  network step, and a hobbyist with no GitHub account (H, scrum/VISION.md: the hobbyist is a hypothesis). · E for what
  exists, H for the use
- (c) The Claude account. Claude Code already follows it for plugins and skills (`syncClaudeAiPlugins`,
  `syncClaudeAiSkills`, settings reference; the folder `~/.claude/plugins/synced` exists here). The page read says
  nothing of syncing `pluginConfigs` values (it was cut at 100,000 characters: —). Artifacts keep data per claude.ai
  account, but no spark script can write it (`docs/discovery/2026-11-16-p835-interface-spike/artifacts-and-plugin.md:42`).
  Spark controls none of it, and it reaches only Claude frontends. · E for what exists, — for value sync
- (d) A spark account. A new service: hosting, sign-in, account management and personal data. Nothing exists, and it
  goes against "free, few and local" (AGENTS.md, Principles). · E for the principle, H for the cost
- Most room at least cost now (H, the PO assistant's reading of the above): name the layer "account" in the seam with
  no member, keep the person's layer as the OS user's store, and make (b) the first candidate member, because P1193
  already depends on the person's GitHub identity and D6 names GitHub. (c) costs nothing but spark cannot write to it;
  (d) costs the most.
- supports only: a choice among readings; no reading is tested with a second machine or a second person.

PO-11 · What a person would manage in an account, from D6 and P1193's settings (H, derived, not asked): which sign-in
is linked, and unlinking it; the author identity of public commits; the central repository; what syncs to the public
(D2: none by default); which of their settings follow them; seeing and deleting what spark sent under their name. For
reading (b), the account itself (password, 2FA, deleting it) stays GitHub's. · H, D6 and P1193 brief.md:141-153 ·
supports only: a list for the decider to cut; nothing here was asked of him.

PO-12 · Candidate settings by layer, from the inventory, P1193 and P1190 (layers as proposed by their sources; no
layer is decided):
- spark's defaults (the plugin): `data/tools.json` entries and roles; `DEFAULT_VENDOR_ORDER`; 3 integrations off by
  default (`data/tools.json:237,251,282`). · E
- the person (store, or later an account): sellers (PO-2), vendor order as a personal default (P368), P410's check as a
  personal default, P1193's six user-layer settings (texts that leave on a share, author identity, what syncs, the
  central repository, who sends, the shared records' member). · E for the sources, H for the layer
- the machine: the store's place (`SPARK_HOME`), where the Wokwi token is read from (`account_env`), the downloads, the
  file `grants/direct_flashing_disallowed`. · E (`board_grant.py:87,203-208`)
- the project: P410's check, the project timeline's member (P1193 "project, then user"), tool pins, `prefer`, the
  active board. · E
- probably records, not settings (H, for the decider): goal and must, needs and their basis (written "on the person's
  words only"), `rules.json` (derived from the netlist). Moving them would blur "one word for one thing".
- never a setting (E for the rules, H for the list): a secret's value (spark names the variable, `account_env`; npm
  "must" scope auth to one registry; Claude Code stores a `sensitive` value in the OS secure store, not
  `settings.json`); a yes that spends money or erases a board (see PO-13); behaviour such as thresholds, timings or
  drivers in firmware ("Spark exports facts, never behaviour", AGENTS.md).

PO-13 · Spark keeps a consent as a grant, not as a setting, and P1190's D13 asks for a paid-run policy that is
configurable. The deploy grant is a typed yes per board, at most 1440 minutes, refused when relayed
(`WHY_RELAYED_YES`), kept under `grants/`; `direct_flashing_disallowed` is a file that only tightens and fails closed.
D13 wants "a threshold … when it should warn and not run the payed ones by default", runs "only for the important
releases", or "it can always ask". CLAUDE.local.md's "Never: run a paid simulation" and "anything that costs money
(name the cost first)" stand beside it. · E · `scripts/spark/bench/board_grant.py:70-100,195-212`; P1190 brief.md:118;
`CLAUDE.local.md`, "Never" and "What waits on him" · supports only: a split between a setting that narrows when spark
asks (may be a setting) and a yes that spends or erases (a grant). Where the line falls is the decider's.

PO-14 · Claude Code's plugin `userConfig` is a ready per-user settings store, but spark's scripts cannot read it.
It has types, `default`, `options`, `required`, `sensitive` (masked, "stores the value in secure storage instead of
`settings.json`"), and a row per option in `/config`; values go under `pluginConfigs` in the user's `settings.json`
(scope "User or managed", so no project layer). The values reach skill and agent text, hooks and MCP or LSP config,
but "The variables aren't present in the environment of commands Claude runs through the Bash tool", which is how
spark's scripts run, and spark's scripts must also run outside Claude Code (`docs/guide/agents/scripts.md:5`, "Anywhere
else: the scripts"). Free; `options` needs Claude Code 2.1.271 or later. · E · https://code.claude.com/docs/en/plugins-reference,
"User configuration" and "Environment variables", read 2026-11-26; spark's `plugin.json` has no `userConfig` · supports
only: a candidate home for a secret such as the Wokwi token, or a mirror in `/config`; not the seam's store.

PO-15 · Licence and cost of the patterns. A pattern (layer names, last-wins merge, `--show-scope`, protected scopes,
`useConfigOnly`) is an idea and carries no licence; only copied code would. Git is GPL-2.0, npm Artistic-2.0, VS Code's
source (Code - OSS) MIT, so copying code from git would not fit spark's MIT (H, from model knowledge of the projects'
licences; not read today). Reusing git itself as P1193's carrier for settings costs nothing new: spark already depends
on git. · H · — for the licence texts · supports only: reuse the pattern, write the code.

PO-16 · The outcome walk's three settings (P410's check, P368's vendor order, P1193's author) do not yet exist as
settings with a personal value: P410's is a flag per run, the vendor order is per project only, the author is new. ·
E · `council/inventory.md` rows "vendor order" and "`deploy.py --no-simulation`"; P1193 brief.md:148 · supports only:
the walk needs all three built or moved first; it cannot run on today's code.

PO-17 · Pre-mortem, "six months after it shipped, it failed. Why?" (H, the PO assistant, from PO-1 to PO-16):
- The page was built, and nobody opened it: the person tells Claude in the chat, and `/spark:setup` already shows the
  tools. The page duplicated a conversation.
- People could not tell why a value applied: too many layers, and "which layer set it" was shown as a colour or not at
  all (VS Code shows a coloured bar and `@modified`; git needs `--show-origin`).
- A cloned project's file changed the person's behaviour unseen: an install line, a share, a sync to the public.
- The move stalled halfway: the tools list and the seam both held roles, two words for one thing.
- The account layer was built for n = 1 on one Mac, and nobody used it.
- A setting turned a consent into a standing yes, and a paid run or a share happened unasked.
- It was designed before a design needed it, against W14 ("the 09-29 cut deleted 5,962 lines built that way").
- A value of the wrong shape fell back to the default in silence, as `prefer` does today (PO-3).

PO-18 · The riskiest belief and its cheapest test (proposed, H, the PO assistant's opinion): that a layer beyond
"spark's default, the person, the project" earns its cost, the account layer above all. Evidence now: one person, one
Mac, no outside user (scrum/VISION.md, "Who it is for"), and no personal `tools.json` in his store (PO-2). Cheapest
test: one account question to the PO, "In the last 30 days, did you run spark on a second machine or as another OS
user, or want one of your choices to follow you there?" (kind: account, n = 1), plus the count in PO-2 rerun at the
decision. A pass line is the decider's to set before the answer.

## 2. What I could not check, and why

- Whether Claude Code syncs `pluginConfigs` values with the claude.ai account: the settings reference was read only to
  100,000 of 462,469 characters, and the visible part does not say. —
- VS Code's full scope list (machine, window, resource) and its Settings Sync account kinds: the settings page read
  does not list them, and the search found only secondary sources. —
- How the hobbyist would choose a layer, or whether they have a GitHub account: no outside person has installed spark
  (scrum/VISION.md). —
- Whether the PO uses spark on a second machine: no record of it in the store read; only he can say. —
- The licence texts of git, npm and VS Code: not read today (PO-15 is H).
- The inventory's pointers that the facilitator did not re-read: I re-read `tool_finder.py`, `store.py:59-65`,
  `brief_choices.py:13-19`, `brief.py:25-62` and `board_grant.py:70-100,195-212` only.
- P1190's discovery is a draft PR (#1742, open); its D13 may still change.

## 3. Questions for the decider

- Does "global" mean spark's defaults, the machine, or the person (git's "global")? · decides: the layer names and how
  many layers there are (PO-8).
- Which reading of "account" fills the account seam first: the OS user only for now, a GitHub sign-in, the Claude
  account, or a spark account? · decides: what the seam must leave room for, and what a later epic builds (PO-10).
- May a project's file set every setting, or does each setting list the layers that may set it (as git, VS Code and
  Claude Code do)? · decides: how far a cloned project is trusted (PO-9).
- Is a paid-run policy a setting that only narrows when spark asks, with the yes kept as a grant, or may a setting
  answer the yes itself? · decides: the line between settings and consents (PO-13), and how it fits CLAUDE.local.md's
  "Never".
- Are goal, must, needs and `rules.json` records or settings? · decides: the seam's scope (PO-12).
- When a setting's value cannot be read, does spark refuse and say so, or use the default and say so? · decides: the
  rule PO-3 shows is missing.
- In the last 30 days, did you run spark on a second machine or as another OS user, or want a choice to follow you
  there? (kind: account) · decides: whether the account layer is built soon or stays a named empty seam (PO-18).

## 4. Searches

- "VS Code settings scope machine application window resource workspace trust restricted settings documentation" · served how far a project layer is trusted, and which settings a project file may not set · used (PO-9); caveat: the full scope list was not found
- none further: pages read without a search · https://code.claude.com/docs/en/plugins-reference (PO-14), https://code.claude.com/docs/en/settings-reference, first 100,000 characters (PO-9, PO-10), https://code.visualstudio.com/docs/configure/settings (PO-8, PO-9); git's and npm's documentation were read from the copies installed on this Mac
