# The boards on USB, for AI agents

Part of the [guide for AI agents](../agents.md). [P919](https://github.com/xmejkal/spark/issues/1301) added
`bench.py show`, which lists the boards on USB. For each board it gives the deploys by project, the last deploy, the
projects that keep it and its grants. It runs only `mpremote devs`, which never opens a port, so a
running program goes on. It asks no question and writes nothing. `bench.py` with no verb shows too. `--project` only
finds the tools list, so it runs from any folder. [P920](https://github.com/xmejkal/spark/issues/1302) added
`bench.py register` and `bench.py record`, so that a project that is not spark's records its deploys. They are below.

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/bench.py" show --json
```

With `--json` it prints the envelope, as `parts.py` does, with `tool` `bench` and `op` `show-bench`. Its `data` holds
`boards`: one row per board, in the order `mpremote devs` lists them. `[]` is no board on USB, a complete answer.
`null` is a list that did not run, or a store that cannot be read. It is never "no board", and `unchecked` holds
`list_failed`, `tool_missing` or `store_problem`.

| key | holds |
| --- | --- |
| `device`, `also_on` | the port the board is used on, and its other nodes |
| `usb_serial`, `usb_id`, `product` | as `mpremote devs` lists them. `usb_serial` is `null` for a board that shows none |
| `mac`, `mac_from` | the MAC in the stores' form, such as `dc:da:0c:xx:xx:xx`, and where it came from: `kept_board` (a kept record names the board) or `usb_serial` (the MAC part of a serial on Espressif's own USB, not read from the chip). When spark cannot tell the board, both are `null` |
| `board` | the board record's id that the kept record or the deploy record names, or `null` |
| `kept_for` | `[{project, at}]`, each project folder whose look kept this board, and when. `[]` is none. `null` is not known: a kept file cannot be read, or the store keeps boards and this one shows no serial or one its firmware set |
| `last_deploy` | `{state, why, project, verdict, deployed, micropython_banner, made_by}`, as in `look.py`'s envelope |
| `deploys_from` | `[{project, made_by, deploys, last}]`: each project name and maker the deploys recorded, the newest first, with its count and the `deployed` text of its last entry, as stored. `made_by` is the tool of a registered project, and `null` for spark's own deploys. `[]` is no deploy. `null` is not checked |
| `grants` | `[{scope, state, granted_by, granted_at, expires_at}]`, the `deploy` scope then the `live` one. `state` is `live`, `ended`, `none`, `not_a_grant`, `no_zone` or `not_checked` |
| `unchecked` | the keys of the parts that were not checked |

A grant row's state says `not_checked`, with an underscore. `last_deploy.state` says `not-checked`, with a hyphen, as in
the look's envelope.

The deploy grant is found by the MAC and the live grant by the USB serial, as `grant.py --check` finds it. A project name
of spark's own deploy is the folder name as the deploy recorded it, so a worktree shows under its own name. A registered
name comes with its tool, and a folder name and a registered name never merge into one group. Two clone boards with one bridge
chip's serial are named alike. The deploy's board question names them alike too.

Each part that was not checked is one `unchecked` item, with the port as its `subject`, and the exit is 2. Its `code` is
one of these. `data` still holds what was read.

| code | means | fix |
| --- | --- | --- |
| `cannot_tell_board` | spark cannot tell the board by its USB serial: it shows none, one its firmware set, or a bridge's serial that no project keeps, or two kept records with two MACs name it | run look.py in the project that uses the board: it reads the board and keeps it |
| `known_board_unreadable` | a file in the store's `known-boards/` cannot be read. It can be any board's | repair or remove the file the sentence names |
| `last_deploy_not_checked` | the board's deploy record cannot be read, or one of its entries has no `project` or no `deployed` | repair or remove the file the sentence names |
| `not_a_grant` | a grant file of this board is not a grant spark can use | remove the file, or give a new grant with grant.py |

Exit codes: 0 when the list ran and every part of every board was read, also with no board. 2 when the list did not
run, a part was not checked, or an argument is wrong. Never 1: the view finds no problem.

## Register a project that is not spark's

A project that deploys with its own tool, such as pixel-games with its own deploy tool, registers once. Run it from a spark
checkout that stays, because the launcher runs this Python and this `bench.py`:

```sh
python3 $CLAUDE_PLUGIN_ROOT/scripts/bench.py register pixel-games --origin https://github.com/xmejkal/pixel-games.git --tool TOOL --json
```

`--origin` is any text that every worktree of the project shares: the origin remote, or the git common folder of a project
with no remote. The same name with the same origin changes nothing and exits 0. With another `--tool` it replaces the
tool. A name with another origin is `name_taken`. A name on spark's projects list is `name_taken` too, with or without its
folder. A name that is not plain is `key_not_plain`. A blank, space-only or unprintable `--origin` or `--tool` is `blank_value`.
These refusals say "Not registered." in their sentence and exit 2. A store that refuses is `store_problem`, and its last
line on stderr says "Not registered." Each fix names the next command. The envelope has `op` `register-project` and
`data` `{registered: {name, origin, tool, registered}, changed, launcher}`. When the name was written and the launcher
was not, the exit is 2. `data` holds the registration with `launcher` `null`. Stderr says that the name is registered
and the launcher was not written. Run the same command again after the repair.

## Record a deploy

After each deploy, the project's tool runs `record` once. It runs only `mpremote devs`, opens no port and reads nothing
from the board. The MAC is the first 12 hex digits of the USB serial of a board on Espressif's own USB. Any other board is
`cannot_tell_board`, and no kept board is read.

```sh
python3 $CLAUDE_PLUGIN_ROOT/scripts/bench.py record pixel-games --json
```

The envelope has `op` `record-deploy` and `data` `{entry, mac, device}`. The entry is
`{project, made_by, deployed, verdict, image_sha256, simulation, yes, micropython_banner}`. `deployed` is spark's clock
at the call, with its zone. `verdict` is `ready not read`. Each `null` means that spark read nothing. Each stop writes
nothing, exits 2, and its fix names the next command. The sentence of `not_registered` and `cannot_tell_board` says
"Nothing was written." The last line on stderr says it for these codes: `no_port`, `two_boards` (give `--port`),
`port_not_listed`, `tool_missing`, `list_failed` and `store_problem`.

The deploy tool of pixel-games records since P921 (#1303). When the launcher file is there, its deploy runs the
launcher once, after the last copy and before the reset. It prints one line that starts with `spark's store:`. The line
ends with `recorded pixel-games, <deployed>`, `not recorded (<a code or a short reason>)`, or
`not known (time limit of 30 s)`. With no launcher file, nothing runs and the line says so. The deploy goes on whatever
the line says. After a recorded line, `bench.py show` lists `pixel-games` with "by" and the `--tool` text of its
registration, while the board is on USB.

## The launcher, for a tool outside spark

`register` writes `<store>/launcher/bench.py`. The store is `SPARK_HOME`, else `XDG_DATA_HOME/spark`, else
`~/.local/share/spark`. The launcher always runs `bench.py` on the store it lives in, whatever store the caller's
environment names. A tool outside
spark runs it with any `python3`, from any folder, with the same arguments as `bench.py`:

```sh
python3 ~/.local/share/spark/launcher/bench.py record pixel-games --json
```

It answers in about one second, as `bench.py` does. When the Python or the `bench.py` it runs is gone, it prints one
envelope line with the code `launcher_stale` and exits 2. Its fix is to run `register` again. No JSON on stdout means
that the launcher itself is missing, or the Python that runs it is gone. A stale launcher is a could-not-run, and the tool's deploy goes on.

Known limits: no path to spark's code stays valid after a plugin update or a removed worktree, so register from a
checkout that stays. A serial that a firmware set and that starts with 12 hex digits passes as a MAC. The store's lock
file is in the temp folder, so a process with another `TMPDIR` does not share it.
