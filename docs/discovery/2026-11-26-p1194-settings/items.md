# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>.
e.g. `- needed by: "I want to know what we should build next" (Lena, 2026-10-06)` -->

## I1 — the settings seam, with the vendor order as its first setting (slice 0)
- type: story <!-- REQUIRED:item-type -->
- needed by: "spark should have a settings /config feature per multiple layer like global/per project/per account logged in" (the PO, 2026-11-26, #1740) <!-- REQUIRED:needed-by -->
- value proven by: `show-settings --json` lists the vendor order with its value, default and layer; a test adds a fake fourth layer with no caller change <!-- REQUIRED:value-proven-by -->
- depends on: D11 to D16, D23 (answered 2026-11-26) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1194 #1740 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): 10 The store <!-- REQUIRED:spark-process:slice -->

## I2 — P1214 #1763 (which replaced P410 #536): the check before the board as a setting (slice 1)
- type: story (an existing card, linked as a sub-issue of P1194, not filed new) · needed by: #536's words, "per project with a personal default", carried by #1763 · value proven by: the deploy's first line names the check and whose word it is · depends on: I1 · status: proposed · label: story · parent: P1194 #1740 · slice: 10 The store

## I3 — set-setting, with the layers each setting allows (slice 2)
- type: story · needed by: D8 and D9 (every feature from the CLI first) · value proven by: A6's refusal test · depends on: I1 · status: proposed · label: story · parent: P1194 #1740 · slice: 10 The store

## I4 — ask once for a setting with no value (slice 3)
- type: story · needed by: "configurable and asks until configured" (the PO, 2026-11-26, #1740) · value proven by: A8's walk · depends on: I3, and P1193's author setting · status: proposed · label: story · parent: P1194 #1740 · slice: 10 The store

## I5 — the settings on the page: one list and each step's fold (slice 4)
- type: story · needed by: "we will also make the ui for it later, or you can already start the epic of config and analyze etc and create the ux/ui" (the PO, 2026-11-26) · value proven by: A1's walk on the built page · depends on: I1, I3 · status: proposed · label: story · parent: P1194 #1740 · slice: 10 The store

## I6 — bug: a brief value spark cannot read falls back to the default in silence
- type: bug · needed by: F2 and ★C4 (smartbin-local's `prefer`, reached only by a hand edit) · value proven by: a run on smartbin-local uses spark's default and its first line names the value it could not read (D14) · depends on: — · status: proposed · label: bug · parent: — · slice: 10 The store

## I7 — bug: a project's tools file can redirect a role and blank account_env
- type: bug · needed by: F1 and ★C5 · value proven by: a scratch project's redirect and an empty `account_env` from a project are both named before use (D12 keeps today's overrides, D15 keeps the merge) · depends on: — · status: proposed · label: bug · parent: — · slice: 10 The store

## I9 — a project's settings move from its brief to its own settings file (D24)
- type: story · needed by: D24 (the PO, 2026-11-26, Q15) · value proven by: `prefer` and `sellers` read from `.spark/settings.json`; the 4 briefs that hold them today (irrigation, spark-quickstart, reaction-game, smartbin-local) move with a first line that names the old field (D14); the brief keeps the goal, the musts and `decided`; `init_project.py --answers` and the spark-review skill still work; his default fills in where a project names none and each run says so · depends on: I1 · status: proposed · label: story · parent: P1194 #1740 · slice: 10 The store

## I10 — not a new card: a comment on P1221 #1770 (the paid-run policy, filed from P1190) with D19 and D12
- type: comment on an existing card · the comment raises one conflict for the PO: #1770 gives `paid_runs` and its threshold the layers user and project, while D12 makes a setting that spends money his alone · needed by: D19 and P1190's D13, "a threshold for example when it should warn and not run the payed ones by default … only running it … for the important releases" (the PO, 2026-11-26) · value proven by: a run inside his rule's limits starts with no per-run yes and names the rule; a run outside it asks; only his own layer may set the rule (D12) · depends on: I3, P1078 (the paid run as an Operation) · status: proposed · label: story · parent: P1194 #1740 · slice: 10 The store

## I8 — chore: the tools list's choices as Operations
- type: chore · needed by: D8 and D9, "everything must be accessible at least from CLI, later it will be MCP" (the PO, 2026-11-26) · value proven by: the catalogue lists the tools list's choices · depends on: — · status: proposed · label: chore · parent: #94 · slice: ask the decider

## Board actions
- file I1, I3 to I9, link I2 (#1763) as a sub-issue, comment I10 on #1770 · pending, needs his yes to this list <!-- REQUIRED:board-actions -->

## Proposed from the PO's words during the discovery

- N1 · epic, later version · accounts with an optional GitHub sign-in: spark creates projects, reaches the parts and suggests edits under an account, and a person manages the account; users, permissions and groups come with it · from D6 and D7 (the PO, 2026-11-26) · slice: — (to ask) · not filed: waits for his yes to this list
