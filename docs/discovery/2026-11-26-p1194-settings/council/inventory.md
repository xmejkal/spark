# Inventory: where spark keeps its choices today

Read-only sweep by an Explore agent (Sonnet), 2026-11-26, on main at 43bea346. Two pointers were re-read by the
facilitator: `scripts/spark/records/tool_finder.py:40-46,92-110` and `scripts/spark/records/store.py:59-65`. The
file is `records/tool_finder.py`, not `sourcing/`. Every other pointer is the agent's, not yet re-read.

Spark has no settings layer. It has one three-layer mechanism, the tools list, and a set of per-project and per-store
files.

## Where things live

- The store, per machine and per person: `store.home()`, `scripts/spark/records/store.py:59-65`. The order is
  `$SPARK_HOME`, then `$XDG_DATA_HOME/spark`, then `~/.local/share/spark`.
- The store's places: `PLACES`, `store.py:111-114`. Spark refuses a store inside a git tree (`store.py:390`).
- A project's files: `<project>/.spark/` (`project.json`, the brief; `rules.json`; `needs.json`; `needs-basis.json`;
  `requirements-origin.json`; `tools.json`; `cache/`), and `boards/active.json` at the project root.
- The plugin's defaults: `data/tools.json`, the other `data/*.json`, and the `boards/`, `parts/` and `chips/` libraries.

## The settings

| setting | stored in | set by | default | read at | layer today |
| --- | --- | --- | --- | --- | --- |
| store location | env `SPARK_HOME`, then `XDG_DATA_HOME` | the person, or Claude through `next.env` | `~/.local/share/spark` | `store.py:54-87` | per machine |
| a tool's fields (`kind`, `exe`, `install`, `version`, `oldest_version`, `needs`, `meets`) | `data/tools.json`, the store's `tools.json`, `.spark/tools.json` | the plugin, `tools.py --pin`, `--new`, a hand edit | `data/tools.json` | `tool_finder.py:92-110`, merged field by field, the project winning | plugin, store, project |
| `on` (an integration on or off) | the same three files | `tools.py --on`, `--off` (`/spark:setup`) | `on:false` for 3 entries (`data/tools.json:237,251,282`) | `tool_finder.py:306,340,372`; `setter_of` at 264-271 | plugin, store, project |
| `roles` (a job points at a tool, 14 roles) | the same three files | `tools.py --use ROLE=TOOL`, refused unless the tool meets the contract | `data/tools.json:3-18` | `tool_finder.py:524-538` | plugin, store, project |
| pins | `NAME.FIELD` in the same files | `tools.py --pin` | none | `tool_finder.py:517-523` | store or project |
| where a choice is written | `choose()`, `tool_finder.py:508` (corrected by the tech lead) | `--project` writes the project file, else the store file; `--personal` forces the store | n/a | `scripts/tools.py:5-10,56-57` | n/a |
| vendor order (`prefer`) | `.spark/project.json` | the `/spark:init` template or the person | `("dfrobot","seeed")` | `sourcing/brief_choices.py:15-19`, `records/brief.py:62` | per project only (P368 #470's "source order") |
| sellers | `.spark/project.json` | the person | none | `brief_choices.py:22-27` | per project only |
| `goal`, `must` | `.spark/project.json` | the person, through `init_project.py --answers` | empty | `brief.py:44-65` | per project only |
| rules (`i2c_buses`, `must_not_float`, `pulled_by_firmware`, `physics.*`, `fabrication`) | `.spark/rules.json` | `init_project.py` derives it; the person edits it | derived from the netlist | `design/loader.py:50`, `checks/rules_check.py:221-226` | per project only |
| active board | `boards/active.json` | `init_project.py --board` | none | `init_project.py:32-34,97` | per project |
| needs and basis | `.spark/needs.json`, `needs-basis.json` | Claude's `--needs-set`, on the person's words only | none | `design/needs.py:6`, `design/needs_basis.py:70` | per project |
| Wokwi token | env `WOKWI_CLI_TOKEN`, named by `account_env` | the person | none | `data/tools.json:54-55`, `tool_finder.py:359` | per machine, a secret |
| deploy grant (a yes for N minutes per board) | `<store>/grants/<mac>.json` | the person, `grant.py --minutes` | at most 1440 min | `bench/board_grant.py:76,198-208` | per machine |
| direct flashing disallowed | the file `<store>/grants/direct_flashing_disallowed` | the person | absent, so allowed | `board_grant.py:87,208` | per machine |
| `deploy.py --no-simulation`, `--ignore-older-runs` | flags, not kept | the person, per run | off | `board_grant.py:16,81` | none; P410 #536 asks for a kept setting |

## Notes

- `/spark:setup` (`commands/setup.md`) is the only settings interface, and it edits only the tools list.
- No `.spark/settings.json` and no preferences file exist.
- `commands/setup.md` says a project's `.spark/tools.json` can name install commands, so it is untrusted input.
- P368 #470 is a spike: "settings for the part search (source order, match closeness) in one settings class". Match
  closeness has no setting today.
- P410 #536 wants one setting, "per project with a personal default", for the check before the board: simulate,
  deploy and run, or a quick free check.
- The brief is read through one dataclass, `records/brief.py:35-66`.

## Settings that other discoveries asked for on 2026-11-26

- Paid simulation minutes: a threshold to warn at, paid runs off by default, a run only for important releases, or
  always ask. From P1190's D13, the PO's words on branch p1190-simulation, docs/discovery/2026-11-26-p1190-simulation/brief.md:118.
- What leaves the store on a share, and what syncs to the public, none by default; the commit author for the shared
  repository, asked until set. From P1193 #1738's P1, P2 and P4 (this brief's D1 and D2).

## Searches

none
