# Commands, skills and agents

In Claude Code you type a **command**. Claude follows that command's page, a Markdown file in
[`commands/`](../../commands/), and runs spark's scripts.

A **skill** is a longer procedure that Claude picks up when your words match it.

An **agent** is a focused helper that a command or a skill launches. It has its own model and its own short list of
tools.

Every command treats text read from a [record](../../GLOSSARY.md#record--and-the-three-places-one-lives), a drawer
entry, a web or shop page or a datasheet as data about a part. It is never an instruction: if such text asks Claude to
run or change something, Claude quotes it to you and carries on. (Each command page says so in its first paragraph.)

The [journey guide](journey.md) shows these commands on real runs.

## Commands

| command | use it when |
| --- | --- |
| `/spark:init` | in a new project folder, and again after a build |
| `/spark:setup` | after init, or when a tool shows `[????]` |
| `/spark:drawer` | you want spark to know what you own |
| `/spark:idea` | you have a goal in words |
| `/spark:research` | a part the library lacks |
| `/spark:identify` | a module you own, from a photo |
| `/spark:build` | you have a [requirements file](../../GLOSSARY.md#the-requirements-file) |

### `/spark:init`

Sets up a project for spark. It writes:

- `.spark/rules.json`
- `.spark/project.json`
- `boards/active.json`
- a `package.json`, which tscircuit installs into

It also adds the project to your projects list in your store.

If there is a built design, it names the rails from it, so it runs again after the first build, with `--force`
([journey: Checks](journey.md#checks)). `--force` merges what init derives into rules.json and keeps your answers. It
rewrites project.json only if that file has no answers, and it never rewrites package.json.

It leaves every value it cannot know as `null` and lists them. Not every check reports a null yet; see
[what never to assume](agents.md#what-never-to-assume). Page: [`commands/init.md`](../../commands/init.md).

### `/spark:setup`

Shows which tools spark needs and which are missing, and installs them with one yes. Run it after `/spark:init`:
without a `package.json` in the project, npm installs into a parent folder
([P113](https://github.com/xmejkal/spark/issues/47)). First it shows exactly what installing would run:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/tools.py" --install micropython-esp32s3 --project . --dry-run
```

It never runs `sudo`: a line that needs it is printed for you instead.

Each choice writes one line to your `~/.local/share/spark/tools.json` or to the project's `.spark/tools.json`, and the
project's file wins. A choice is turning an integration on or off, pointing a job at another tool, or pinning a
version.

It refuses to point a job at a tool that cannot do that job. Page: [`commands/setup.md`](../../commands/setup.md).

### `/spark:drawer`

What you own, in your own store, never in a repository:

- **See it:** `parts.py --drawer`.
- **Add to it:** say more in plain words, through `--drawer-set` with `--dry-run` first.
- **Import your DFRobot order history** from your logged-in browser.

An entry needs only a label and a count, and adding a part to the drawer never starts research on it.

How the import works:

- Claude drives your logged-in Chrome, and spark's extractor returns only each order's lines.
- Reading the pages no other way, and never typing credentials or solving a challenge, are rules Claude follows from
  the command page.
- The import never stores an order number.
- It refuses an import when the number of order lines it read differs from the number the shop's pages state.

See [journey: Drawer](journey.md#drawer). Page: [`commands/drawer.md`](../../commands/drawer.md).

### `/spark:idea`

Turns a goal in your words into needs, asking at most three questions, one at a time. It then matches each need
against your drawer and spark's records, owned parts first ([journey: Idea](journey.md#idea)). The needs are written
to the project's `.spark/needs.json`.

It stops after matching each need. Not built yet:

- choosing a part per need, and reserving the parts you own
  ([P97](https://github.com/xmejkal/spark/issues/18));
- turning needs into a requirements file ([P76](https://github.com/xmejkal/spark/issues/5)).

Page: [`commands/idea.md`](../../commands/idea.md).

### `/spark:research`

Researches a part the library lacks:

1. **Reuse first,** with no network.
2. **Find the exact part.** For a commodity part (an LED, a button, a connector: one datasheet describes it),
   `part-finder` offers at most two candidates and you pick. `datasheet-reader` then fills the record from the kept
   datasheet. A whole module goes to `parts-researcher`.
3. **Check what came back:**

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --validate --project .
```

`--validate` refuses a record that gives a pin order without saying where it was read, or that cites a document the
record does not include. `parts.py --unverified <id>` lists what nobody has checked, each item with what depends on it.

A candidate not chosen whose datasheet was kept goes to the catalog in your store, with no seller listings. One seen
only in a search is listed in the chosen record's alternatives.

It does not:

- pick for you between two fitting parts;
- verify a pinout;
- track prices.

Page: [`commands/research.md`](../../commands/research.md).

### `/spark:identify`

A photo of a module you own becomes a part record. The chip markings, the silkscreen and the connector are read
before anything is searched. Every fact the photo alone supports is marked unverified.

It does not measure. What the photo cannot show is named in `--unverified`, with how a person checks it: a meter,
the other face, or the chip's datasheet against a pin number. Page: [`commands/identify.md`](../../commands/identify.md).

### `/spark:build`

A requirements file becomes a board that builds, with a Wokwi diagram generated from it, or it names the stage that
stopped it. It runs no simulation. It runs in seconds, with no agents ([journey: Build](journey.md#build)).

With `--keep .` it writes `board.tsx`, its footprint and `dist/` into the project. An existing `board.tsx` is left
alone, edited or not, and `dist/` is then built from the requirements file, not from your `board.tsx`
([P110](https://github.com/xmejkal/spark/issues/44)). To check an edited `board.tsx`, build it with
`npx tsci build board.tsx`; to regenerate it, delete it.

It stops and names the problem when the requirements file:

- lists one part twice without a `name` for each (five unnamed buttons would become one button with five of the dev
  board's pins wired to it);
- uses a pin the part does not have;
- uses a bus line the bus does not have.

Page: [`commands/build.md`](../../commands/build.md).

## Skills

| skill | use it when | what it does |
| --- | --- | --- |
| **spark-design** | "design a board for …", "wire up an ESP32 with …" | generates the board from a requirements file through spark's own chain (parts → pin map → board file → build → simulation); tscircuit is written by hand only where the generator stops ([`SKILL.md`](../../skills/spark-design/SKILL.md)) |
| **spark-review** | "review my design", or before ordering a board | runs every deterministic check, then one `design-reviewer` per dimension (power, signals, thermal-mechanical, manufacturability, firmware-hardware) reading the primary artefacts only, and ends with the fabrication gate ([`SKILL.md`](../../skills/spark-review/SKILL.md)) |
| **spark-reverse-engineer** | a photo of a board, "what's connected to what" | fuses copper-trace reading, datasheet pinouts and functional reasoning into a netlist, then writes a bench protocol to confirm it ([`SKILL.md`](../../skills/spark-reverse-engineer/SKILL.md)) |

## Agents

| agent | launched by | what it does | model · tools |
| --- | --- | --- | --- |
| `part-finder` | `/spark:research`, for a commodity part | finds the exact part for one need: at most two candidates, each with its maker, orderable part number and the maker's datasheet URL. It writes nothing, and you pick ([`part-finder.md`](../../agents/part-finder.md)) | haiku · web search, web fetch, JLCPCB part search |
| `datasheet-reader` | `/spark:research`, once the part is chosen and its datasheet kept | fills one part record from one kept datasheet, reading only the pages that hold the facts asked for. Every fact is cited to its page, with no web search ([`datasheet-reader.md`](../../agents/datasheet-reader.md)) | sonnet · files, shell, Espressif's documentation (a remote search) |
| `parts-researcher` | `/spark:research` for a module, `/spark:identify` | researches one module from primary sources, vendor by vendor, or identifies one from a photo. It marks every fact nobody has confirmed ([`parts-researcher.md`](../../agents/parts-researcher.md)) | opus · files, shell, web search, web fetch |
| `design-reviewer` | the `spark-review` skill, one per dimension | reviews one dimension of a design for what no automated check can catch, and returns findings as JSON. It only reads ([`design-reviewer.md`](../../agents/design-reviewer.md)) | opus · read, grep |

The two MCP servers spark declares serve these agents: **jlcpcb** for `part-finder`, and **espressif-docs** for
`datasheet-reader`.
