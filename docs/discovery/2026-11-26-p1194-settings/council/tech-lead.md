# Tech lead: P1194 settings in layers

Read-only, on branch p1194 at 8cafe94b (the code is the same as main 43bea346), 2026-11-26. Every pointer is
relative to the repository. One experiment ran in a scratch folder, which is removed. The coordinator's message of
about 12:45 CET brought D6 (accounts and a GitHub sign-in, optional and later). So the account question here is: what
must the seam look like now, so that an account layer can be added later with no change to callers, and what is the
least that is built now.

## Findings

### Judged by the bar (AGENTS.md: a basic project closer to a breadboard with working firmware)

- TL-1 · Only P410's setting (which check firmware gets before the board) is on the bar's path. It decides whether
  paid Wokwi minutes are spent and whether firmware reaches a breadboard untested. P368's vendor order is on the path
  but small: it orders the part search. P1193's share and author settings, the account layer, the GitHub sign-in and
  the settings page do not move a basic project closer to a working breadboard. They serve the store and the page.
  Recommend: build the seam only as far as the first setting needs it. Pause the account storage and the sign-in, and
  design only their slot (TL-15) · E #536 body, #470 body, #1740 body (read 2026-11-26) · supports only: which card
  serves the bar. The PO decides the order.

### Can the tools list's merge become the general seam?

- TL-2 · The pointers in the brief have drifted. `merged` is at scripts/spark/records/tool_finder.py:91-115, and
  `setter_of` at 264-271 (line 266 is inside it). `choose` is at 508-518. Line 497 is inside `settle_download`. This
  holds on main 43bea346 and on this branch · E `grep -n "^def choose\|^def setter_of\|^def merged"` on both trees ·
  supports only: the line numbers.
- TL-3 · The merge has the shape of a tools list, not of a general settings store. Each top-level key must be an
  object (tool_finder.py:102-103), with a printable name and a `needs` list (104-108). `roles` and `contracts` are
  reserved keys (46, 110-114), and contracts are read only from the plugin's file (113). A setting that is a list
  (the vendor order) or a string (a git identity) would be refused as "the entry … is not an object". Turning
  `merged` into the general seam would change the meaning it has for its 5 caller modules (tool_finder,
  tool_choices, project_setup, image_builder, bench_privacy). Recommend: a new small class beside it, and the tools
  list stays as it is behind it (TL-16) · E tool_finder.py:91-115. The caller count is from
  `grep -rn "setter_of\|merged("` over scripts · supports only: that the merge cannot be stretched without breaking
  its callers. It does not say where the new class lives.
- TL-4 · "Which layer set a value" exists for one field only. `setter_of` reads every file again for each question
  (269) and returns a path. Only `off_sentence` uses it, for `on` (274-282). `status()` rows do not carry the layer
  (328-363). A seam should give a Value from one read: name, value, the layer that set it, the file, and the default ·
  E tool_finder.py:264-282, 328-363 · supports only: what exists today.
- TL-5 · Spark already has a second walk through layers. `store.layers` and `store.records` (scripts/spark/records/store.py:121-142)
  give `(layer, path)` with the nearest winning: project, shelf, library, then catalog. A third walk written by hand
  for settings would repeat it. Reuse its shape: an ordered list of (layer name, source), nearest first · E
  store.py:121-142 · supports only: that the pattern exists. It does not say whether one function can serve both.
- TL-6 · A swappable storage already exists. `Storage` (get, put, keys, where) with the Adapter `FileStorage` and
  `MemoryStorage` is at scripts/spark/records/storage.py:68-180, and it is documented as a Strategy in
  docs/guide/patterns-and-names.md:40. One Storage per layer would give a test Fake for free. It would also be the
  place where a later account layer (a git-synced or a remote one) plugs in · E storage.py:68-180 · supports only:
  that the piece exists. Its fit (namespaces, the git refusal) is H until a plan reads it closely.
- TL-7 · `tool_finder.PERSONAL` is a module constant that is read once at import (tool_finder.py:40-42). `store.home()` is read on
  every call (store.py:53-64), and its docstring says why: tests once had to patch 16 constants. The seam should read
  its layer places per call, as the store does · E those lines · supports only: a rule for the new class.
- TL-8 · `tools.py` is not on the core. The records area has no `OPERATIONS` table (a grep for `OPERATIONS` in
  scripts/spark/records finds nothing), and patterns-and-names.md:40 says `tools.py` keeps `main` and
  `print_status`. A settings Operation (show the settings, set one) would be the first Operation of the records area,
  or of a new area. Either way it enters `spark.operation_catalogue.TABLES` (operation_catalogue.py:27-30) · E those
  pointers · supports only: where the new Operations go.
- TL-9 · There is a word clash. `tool_choices.choice_file` returns Claude Code's MCP scope, `"user"` or `"project"`
  (scripts/spark/records/tool_choices.py:18-24). `store.layers` already uses the word "layer" for records
  (store.py:121). The plan's names table must give one word for a settings layer that is neither of these ·
  E those lines · supports only: a naming check for the plan.

### A missing value becomes a question

- TL-10 · The core already has the shape of a question.
  - `Question` has the kinds yes_no, value and choice, and is asked of a person, an agent or either
    (scripts/spark/core/replies.py:30-95).
  - Only an Operation that declares ASKS gets `outside.replies` (scripts/spark/core/outside.py:84-87).
  - An open question is a `needs_reply` finding: the run is `could-not-run` and exits 2
    (docs/guide/agents/replies.md, "What a run with open questions prints").

  So "asks until set" maps to a CHOICE or VALUE Question with a key such as `setting.<name>`. Two gaps remain. The
  replies file is research's own, `.spark/research-replies.json` (replies.py:38), and the look already uses a file
  outside the project (replies.md, "The look's question"). And no reply today is written to a lasting layer, except
  the look's known board in the store. The seam needs one Operation that writes an answer to the layer the person
  named, and says which layer · E those pointers · supports only: that the ask path exists. Where an answer is written
  is the decider's question.
- TL-11 · D1 holds a tension: "a default for each setting" and "a setting with no value asks until it is set". If a
  default is used silently, nothing is ever asked. The seam needs two kinds of setting. One kind has a default that
  is used when nothing is set, and the Value says "default". The other kind asks until it is set: its default is only
  named in the question, as with the author identity of P1193 D8 · D the PO 2026-11-26 #1740 and P1193 D8; the split
  is H (mine) · supports only: that the model needs this flag on each setting.

### Where each layer's file lives

- TL-12 · Today the places are:
  - the plugin's defaults in `data/`. They ship read-only, and installing spark copies the whole repository
    (AGENTS.md).
  - the store's `tools.json`, which is not a private place (store.py:110-113, 147-148).
  - the project's `.spark/tools.json`.

  Recommend: one file per layer, `data/settings.json`, `<store>/settings.json` and `.spark/settings.json`, beside the
  tools files and not inside them. The store refuses to write a private place inside a git work tree
  (store.py:145-148, 385-390). So the person's settings file needs a class (private or not) before P1193 syncs any
  of the store · E store.py lines; the file names are H · supports only: the places. The names are the plan's.
- TL-13 · A project's `.spark/` is meant for git. P1193 P7 commits a named file after the person's yes, and refuses
  where `.gitignore` excludes `.spark/` (#1738 comment of 11:17 UTC). So anything in a project's settings file is
  public once pushed. A personal value (an email, an author identity) or a secret must never be in the project layer
  · E #1738 comment, read 2026-11-26 · supports only: which layer may hold personal values.

### A project's file is untrusted: which settings may it set?

- TL-14 · A project's `.spark/tools.json` can redirect a role to its own script, and it satisfies the role's contract
  by itself. Experiment, in a scratch folder with a scratch SPARK_HOME, removed after. The project's file held
  `{"roles": {"simulator": "my-sim"}, "my-sim": {"exe": "no-such-exe-xyz", "also": ["./evil.sh"], "meets": ["wokwi-project"]}}`.
  `tool_finder.find('simulator', '.')` printed `my-sim ['evil.sh']`, and `setter_of('my-sim', 'meets', '.')`
  printed `.spark/tools.json`. The contract check reads `meets` from the merged entry (tool_finder.py:300-302), so it
  is no trust boundary. Install lines from a project are flagged to the person (`from_project`, 397, 405;
  commands/setup.md). A role pointed elsewhere is not flagged. Whether that command then runs was not tested: `./`
  was dropped from the path, so a run would search PATH. A path with a slash would keep it, but that is H. The same
  file can blank `account_env`, and then the token check is skipped (scripts/spark/firmware/scenario_run.py:273-274)
  · E the experiment's output, 2026-11-26 · supports only: the project layer can set every field of the tools list
  today. It does not show that an exploit runs.
- TL-15 · Recommend: each setting declares the layers that may set it, and the seam refuses a value from any other
  layer, with a sentence that names the file. First split (H, mine, for the decider):
  - project layer allowed: P410's check path, the vendor order, sellers, the project-timeline member.
  - person or account layer only: the author identity, what leaves the store on a share, the central repository,
    and every secret reference.
  - never a setting: the grants (see the physics section).

  The tools list's roles stay as they are until the decider says otherwise (Q2) · H · supports only: a starting
  proposal.

### Secrets

- TL-16 · Today a secret never sits in a spark file. The Wokwi token is only in the environment, named by
  `account_env` (data/tools.json:54-55). Its value is masked as `***` (scripts/spark/bench/bench_privacy.py:27-41,
  scripts/spark/core/privacy.py:20-23). A firmware secrets file is masked by `ProjectSecrets`
  (scripts/spark/firmware/project_secrets.py:1-13), and `run-request` refuses when such a file cannot be read
  (scripts/spark/flow/run_request.py:132-143). Recommend: a setting kind "secret reference", whose value is the name
  of where the secret is (an environment variable). The seam never reads or stores the secret itself. The page and
  `--json` show only "set" or "not set". The reference may not come from the project layer, because of TL-14's
  blanked `account_env` · E those pointers; the kind is H · supports only: how secrets stay out.

### Fit with the core, the page and P1193

- TL-17 · The page cannot set a free value today. `run-request` takes the values of a step from spark's own offer key,
  "never from the request" (run_request.py:1-5). Its allow-list is three Operations: PickParts, WriteRequirements
  and BuildBoard (run_request.py:38-41). A setting with a few choices fits as one offer per choice. A free value, such
  as an identity, does not fit and goes as a sentence to Claude. This matches the standing page rule in the brief
  (councils/p1113) · E run_request.py:1-5, 38-41 · supports only: which setting changes the page can carry.
- TL-18 · P1193 puts its two strategy choices into the tools list now. Its synthesis option D-q6 (a) makes them roles
  `project-timeline` and `shared-records`, with a `none` member. It says "They move into P1194's seam when it
  exists". The caveat is ★C22: a member that is no program needs a seventh kind (tool_finder.py:542 lists six).
  P1151 #1687 is widened to do this. If the seam comes second, those two settings move twice · E
  `git show origin/p1193-change-tracking:docs/discovery/2026-11-26-p1193-change-tracking/brief.md` lines 66, 75,
  141-152 · supports only: an order dependency between the two epics.
- TL-19 · The seam fits the core if it has three parts:
  - a small class in records that holds the declared settings and the layers, and returns a Value.
  - Operations over it, through `OutsideWorld`, with a new slot beside `find_tool` (outside.py:42-43, 71).
  - thin frontends: the CLI with `--json`, and the page's offers.

  Swappable: each layer is a Storage, so a layer is one more list item. DRY: the tools list is shown through the
  same Value, not copied · E the core's shape (operation.py:68-127, outside.py:70-93); the design is H · supports
  only: that no new kind of core piece is needed.

- TL-23 · D8 (the PO, about 13:00 CET: every feature can be reached from other interfaces). The seam needs two
  Operations, both in the catalogue, so the CLI, Claude, the page and a later MCP server reach the same core.
  - `ShowSettings` (op `show-settings`, effects READS). It lists every setting: the value, the default, the layer
    that set it, the file, the layers that may set it, and whether it asks until set. A secret reference shows
    only "set" or "not set". An optional `--name` gives one setting with each layer's value, as
    `git config --show-origin` does. That covers "which layer set it", so no third Operation is needed.
  - `SetSetting` (op `set-setting`, effects WRITES). It takes a name, a value and a layer, and `--unset` returns the
    setting to its default. It refuses a layer the setting does not allow (TL-15), and answers with the new Value and
    its layer. The page reaches it as one offer per choice through `run-request` (TL-17). Claude and the CLI give a
    value.

  Asking is not an Operation of its own. Any Operation that reads a setting which asks until set puts a Question
  through `outside.replies` (ASKS), and the answer is written by `SetSetting`. The seam reaches an Operation through
  a new `OutsideWorld` slot (outside.py:42-43, 71), as `find_tool` does.

  Only these make sense in one interface:
  - the page's layout of the settings (groups, a mark for "changed from the default");
  - `/spark:page`'s carry of a request;
  - the live terminal prompt (`Terminal`, the one class that reads a tty, replies.py:144-148);
  - the words of a slash command.

  Today the tools list's choices (`--on`, `--off`, `--use`, `--pin`, `--new`) are CLI-only, with no Operation
  (TL-8). Under D8 they are a gap: found on the way, for #94's records area · D the PO 2026-11-26 (D8, relayed by the
  coordinator); the Operations are H (mine), on E operation.py:68-127, outside.py:70-93, run_request.py:38-41 ·
  supports only: the Operations a plan starts from. Their names go through the plan's names table.

### The smallest first slice after the MVP

- TL-20 · The smallest slice that proves the model:
  - the seam class, with a declared table of settings: name, kind, choices, default, the layers allowed, and whether
    it asks until set.
  - three file layers: plugin, store and project.
  - one read Operation that lists each setting with its value, default and layer as `--json`. This is the brief's
    proof command.
  - one real setting.

  Candidates for that setting:
  - P368's vendor order is the smallest. It has one caller, `vendor_order` (scripts/spark/sourcing/brief_choices.py:14-19),
    read only in scripts/spark/design/find_offers.py:58, 65. Today it has a project layer (the brief, scripts/spark/records/brief.py:61)
    and a spark default. Only a personal default is new.
  - P410's check path is on the bar (TL-1). But it needs new behaviour: the commands must follow it and say so
    (#536 "Done when"). Today it is a flag on each run, `deploy.py --no-simulation`
    (scripts/spark/bench/deploy_image.py:370-377).
  - P1193's author identity is the only one that tests the ask-until-set path.

  Recommend the vendor order to prove the seam, then P410 as the first setting a person feels. The tools list stays
  behind its own merge in slice 1, because it must not get worse (brief, start and reach) · E the pointers; the order
  is H · supports only: the size of each candidate. The PO orders.

### The account layer (D6: later, but the seam allows it now)

- TL-21 · The least to build now is three rules, and no account code:
  - Callers ask the seam for a setting by name, and never name a layer or a file.
  - The layers are an ordered list given by a builder, as `store.layers` already is (store.py:121-132), so an
    account layer is one more item.
  - Each setting declares whether it travels with the person, or stays on this machine (the grants, the store's
    place, a tool's path).

  A GitHub sign-in later then fills that one item's Storage, and no caller changes · H (mine), on E store.py:121-132
  and storage.py:68-100 · supports only: the shape. It does not show that a sign-in is cheap.
- TL-22 · What "an account" could be, and what each would cost:
  - (a) The OS user. `getpass.getuser` already names who said a yes (scripts/spark/core/replies.py:13, 59-69;
    scripts/spark/bench/board_grant.py:8). It is free and touches nothing new, but it is the store we have now, per
    machine.
  - (b) The Claude account. In this Agent SDK session the environment holds the names `CLAUDE_CODE_ACCOUNT_UUID`,
    `CLAUDE_CODE_USER_EMAIL` and `CLAUDE_CODE_ORGANIZATION_UUID` (names listed with `env | cut -d= -f1`, values not
    read, 2026-11-26). `claude auth status` exists, with `--json` as its default (`claude auth status --help`). Whether
    a plugin script sees these in a plain terminal session, and whether they are a stable interface, is not known.
    An email is personal data, so it must never reach the project layer (TL-13).
  - (c) The git identity, layered by git itself: system, global, local and worktree. `--show-scope` names the
    layer of a value (`git help config`, line 256, git 2.49.0). This is prior art for TL-4, and it costs nothing.
  - (d) A store synced through git, per P1193. P1193 ★C7 says the store cannot itself be the repository, so a
    separate clone and a copy step are needed. Its cost is P1193's (M to L).
  - (e) A GitHub sign-in (D6). The `gh` login is already present on the PO's Mac, so it is free locally, but it is
    a network service and a later epic.

  Recommend: no account layer yet. When it comes, read its identity from (c) or (e), and carry its values with (d).
  (b) waits for a spike · E as cited per item; the recommendation is H · supports only: the options and what each
  touches.

### electronics-firmware:physics

- electronics-firmware:physics-1 · Grants must never be a setting in any layer that travels or that a project holds.
  The deploy grant lets Claude erase the whole flash and write any passed image of any project, with no yes from the
  person for each deploy (board_grant.py:98-99). It is one file per board MAC in the store's `grants` place
  (board_grant.py:14-17, 196-198). A project layer or a synced account layer that held it would give that yes for a
  board on another bench. Recommend: the seam may show the grants, read-only, and never writes them. They stay
  `grant.py`'s, with the yes typed in the person's own terminal · E board_grant.py lines · supports only: keeping
  grants out of the seam.
- electronics-firmware:physics-2 · The direct-flashing switch fails closed today. Direct flashing is disallowed while the
  file `grants/direct_flashing_disallowed` is there, and also when that file is something odd or the place cannot be read (board_grant.py:86-89,
  206-215). Suppose it moved into the seam with a default of "allowed" and the project layer could set it. Then a
  cloned project could turn direct flashing back on. An image that no simulation tested would then drive the
  breadboard's pins with no simulation first, for example an output wired against another output, or a motor driver
  enabled at reset (H, general electronics). Recommend: person layer only, a missing value means disallowed, and the
  fail-closed reading stays · E board_grant.py lines; the harm is H · supports only: the allowed layer and the
  default's direction.
- electronics-firmware:physics-3 · P410's check path changes hardware behaviour. "Deploy and run" skips the simulation
  that would catch a pin conflict before the parts are wired. #536 wants it "per project with a personal default", so
  the project layer is right. Recommend: the setting may never stand in for the typed yes of `--no-simulation`, nor
  for a grant given with `--no-simulation` (board_grant.py:16-17; deploy_image.py:370-377). It only picks which path
  is offered first · E #536, those lines · supports only: that this setting is subordinate to the yes.
- electronics-firmware:physics-4 · Two tools-list fields that the project layer can already set decide what is written
  to the flash: the `firmware-image` build and its `flash_offset` (scripts/spark/firmware/image_builder.py:228-238,
  290-296; tool_finder.py:581-595; P463). A wrong one gives a board that does not boot. The ESP32's ROM bootloader
  can still reflash it (H, general ESP32 knowledge, not read here). This exists today. The seam must not widen it ·
  E those lines · supports only: an existing exposure, not a new one.

## What I could not check, and why

- Whether a role redirected by a project's file actually runs its script (TL-14). I stopped at `find`, because
  running a planted script is beyond a read-only check.
- Whether the Claude account variables reach a plugin's script in a plain terminal session of Claude Code, and
  whether Anthropic documents them. I saw only their names, in this Agent SDK session, and read no values.
- The P1193 synthesis in full (council/synthesis.md). I read its brief's options and its settings table only.
- docs/guide/map.md, `tools.py --status --json`'s keys, the flow's phase readers, and how the page would show a
  settings section (scripts/spark/flow/page_sections). None were read, for time.
- How a GitHub sign-in works for a CLI, and what it costs. No search was made.
- Whether `storage.Storage`'s namespaces and its git refusal fit a settings file without a change (TL-6).

## Questions for the decider

- Is each setting's default used silently, or does a setting ask until set and only name its default in the
  question? Or is it a flag on each setting? · decides: the seam's two kinds (TL-11) and when Claude stops with exit 2.
- May a project's file still point a tool role at its own executable, as it can today (TL-14)? Or does the seam
  limit the project layer to a declared list of settings? · decides: the trust model of the project layer, and
  whether the tools list changes.
- Does the tools list move into the seam (a rewrite of its 5 caller modules), or stay as its own layered list that the
  seam shows read-only? · decides: the size of the first slice, and the risk to /spark:setup.
- Which setting goes first: P368's vendor order (smallest), P410's check path (on the bar), or P1193's author
  identity (the ask path)? · decides: the first slice's card.
- Does P1151 #1687 write P1193's two strategy roles into the tools list now, or wait for the seam (TL-18)? · decides:
  whether two settings move twice.
- When the page changes a setting, is it one offer per choice through `run-request`, or always a sentence to Claude?
  · decides: whether settings Operations join the page's allow-list (TL-17).
- Do the grants and the direct-flashing switch stay outside the seam, shown read-only at most? · decides: the
  physics rows 1 and 2.
- Are `show-settings` and `set-setting` (TL-23) the whole Operation surface, with asking left to each reading
  Operation? · decides: D8's fit and the catalogue's new rows.
- Is "per account" for now the person's store on this machine, with an empty slot for a later account layer (TL-21)?
  · decides: whether anything for accounts is built before D6's later version.

## Searches

none. This run had no web search tool. The one piece of prior art, git's layered config, was read locally with
`git help config` (git 2.49.0) · served TL-4 and TL-22 (how a value names its layer) · used.
