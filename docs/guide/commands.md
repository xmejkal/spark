# Commands, skills and agents

In Claude Code you type a **command**. Claude follows that command's page, a Markdown file in
[`commands/`](../../commands/), and runs spark's scripts.

A **skill** is a longer procedure that Claude picks up when your words match it.

An **agent** is a focused helper that a command or a skill launches. It has its own model and its own short list of
tools.

Every command treats text read from a [record](../../GLOSSARY.md#record--and-the-four-places-one-lives), a drawer
entry, a web or shop page or a datasheet as data about a part. It is never an instruction: if such text asks Claude to
run or change something, Claude quotes it to you and carries on. (Each command page says so in its first paragraph.)

A command page's header, `allowed-tools`, lists the operations Claude may run without asking you, each by name. Five
operations that reach the network are on no command's or skill's list:

- `parts.py --fetch` downloads a datasheet;
- `parts.py --sources` asks every URL a record cites whether it answers;
- `tools.py --install` installs a tool;
- `tools.py --on` turns a tool on and installs it;
- `check_vendor_pins.py` without `--offline` fetches a vendor's pin header.

So Claude Code asks you before any of them runs, and your answer there is the yes, unless your own settings answer
first: an allow rule of yours, or auto mode, can let it run without asking. A test holds every list to this rule
(`tests/test_routes.py`); how Claude Code matches a pattern to a command line is an assumption it states, because the
test cannot run Claude Code. `parts.py --describe --json` marks the network operations of `parts.py`.

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

It leaves every value it cannot know as `null` and lists them. After `--force` the list still names fields you
answered ([P114](https://github.com/xmejkal/spark/issues/48)). Not every check reports a null yet; see
[what never to assume](agents.md#what-never-to-assume). Page: [`commands/init.md`](../../commands/init.md).

### `/spark:setup`

Shows which tools spark needs and which are missing, and installs them in one go once you have seen the commands and
said yes. Run it after `/spark:init`: without a `package.json` in the project, npm installs into a parent folder
([P113](https://github.com/xmejkal/spark/issues/47)). First it shows exactly what installing would run:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/tools.py" --install micropython-esp32s3 --project . --dry-run
```

It never runs `sudo`: a line that needs it is printed for you instead.

Each choice writes one line to your `~/.local/share/spark/tools.json` or to the project's `.spark/tools.json`, and the
project's file wins. You say it in a few words:

| you say | it runs |
| --- | --- |
| `add sigrok` | `tools.py --on sigrok`: on, installed, and its MCP server registered |
| `remove sigrok` | `tools.py --off sigrok` |
| `use simulator=my-sim` | `tools.py --use simulator=my-sim`: another tool for a job |
| `pin tscircuit core=0.0.2700` | `tools.py --pin tscircuit.core=0.0.2700 --project .`: a version |
| `new` | `tools.py --new 'NAME={…}'`: a tool of your own |

An MCP server added or removed takes effect after Claude Code restarts. It refuses a tool that is not in its lists, or
whose entry does not say it meets the job's contract; a job without a contract takes any listed tool. Page:
[`commands/setup.md`](../../commands/setup.md).

### `/spark:drawer`

What you own, in your own store, never in a repository:

- **See it:** `parts.py --drawer`.
- **Add to it:** say more in plain words, through `--drawer-set` with `--dry-run` first.
- **Import your DFRobot order history** from your logged-in browser.

An entry needs only a label; with no count it is owned, count unknown, and adding a part to the drawer never starts
research on it.

How the import works:

- Claude drives your logged-in Chrome, and spark's extractor returns only each order's lines.
- Claude follows two rules from the command page, which no code enforces: it reads the order pages no other way (no
  page text, no accessibility tree, no screenshot), and it never types credentials or solves a challenge.
- The import never stores an order number.
- It refuses an import when the number of order lines it read differs from the number the shop's pages state.

See [journey: Drawer](journey.md#drawer). Page: [`commands/drawer.md`](../../commands/drawer.md).

### `/spark:idea`

Turns a goal in your words into needs, asking at most three questions, one at a time. It then matches each need
against your drawer and spark's records, owned parts first ([journey: Idea](journey.md#idea)). The needs are written
to the project's `.spark/needs.json`.

Then it picks a part per need and reserves what you own of it, and the picks become a requirements file
([P97](https://github.com/xmejkal/spark/issues/18)). The run ends with one cost line, from `parts.py --tally`. Its words,
as the code defines them:

- **from the store**: known to spark before this project — its library, your store, your projects;
- **owned**: your drawer holds it;
- **requests**: tool calls that reach the network, every MCP call among them;
- **documents**: the distinct PDFs and images read, with the Read tool or `parts.py --read`;
- **min**: wall-clock minutes of the session between the steps.

`--tally` reads the Claude Code transcripts of the sessions the steps ran in, for tool names and counts only. With no
transcript the line ends `its cost was not counted` and the command exits 2, could-not-run: a missing cost is never a
cost of 0. [A recorded run](journey.md#a-recorded-run-a-button-and-an-led) shows every step with the output it printed,
and [owed facts and gaps](journey.md#owed-facts-and-gaps) says what a record can owe and what follows a gap.

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

**What research has cost.** The agents run on your account, so you pay for their tokens and time. Measured from their
transcripts on 2026-10-03 as tool calls, tokens processed and time (`scripts/cost.py <transcript>` measures one run
today, but counts network requests, documents read, new tokens apart from cache reads and minutes, so its numbers for the
same run differ)
([P80 in the backlog's archive](../../scrum/PRODUCT_BACKLOG.md#p80--parts-research-is-lean-and-professional--slice-4-the-pos-request-of-2026-10-03--done-2026-10-03-581fa8a)):

- the full research protocol P80 replaced: a median of 78 tool calls, about 5.0 M tokens processed and about 25 minutes;
- one LED, the Kingbright L-7113ID, on a lean brief: 19 calls, about 0.55 M tokens, 148 s;
- `part-finder`'s first use: 14 calls, 91 s, about 0.17 M tokens.

Nobody has measured today's route end to end: `datasheet-reader` has not yet run on a real need. Page:
[`commands/research.md`](../../commands/research.md).

### `/spark:identify`

A photo of a module you own becomes a part record. The chip markings, the silkscreen and the connector are read
before anything is searched. Every fact the photo alone supports is marked unverified.

It does not measure. What the photo cannot show is named in `--unverified`, with how a person checks it: a meter,
the other face, or the chip's datasheet against a pin number. On 2026-09-29 one photo through an anti-static bag gave a
record with seven facts marked unverified; when the back was photographed, five were wrong. So it asks for both sides,
out of the bag. Page: [`commands/identify.md`](../../commands/identify.md).

### `/spark:build`

A requirements file becomes a board that builds, with a Wokwi diagram generated from it, or it names the stage that
stopped it. It runs no simulation. It runs in seconds, with no agents ([journey: Build](journey.md#build)).

With `--keep .` it writes `board.tsx`, its footprint and `dist/` into the project. An existing `board.tsx` is left
alone, edited or not, and `dist/` is then built from the requirements file, not from your `board.tsx`
([P110](https://github.com/xmejkal/spark/issues/44)). To check an edited `board.tsx`, build it with
`npx --no tsci build board.tsx`; to regenerate it, delete it. The Wokwi diagram is written to a temporary folder and
deleted unless `--sim-dir DIR` keeps it ([P116](https://github.com/xmejkal/spark/issues/50)).

It refuses rather than guess, and says what to record
([what it refuses](../../commands/build.md#what-it-refuses-and-why)):

- a part with no footprint or no `pin_order` recorded, or one not in the library;
- one part listed twice without a `name` for each (five unnamed buttons would become one button with five of the dev
  board's pins wired to it) — and two names that differ only in capitals are one name (`OpenLid`, `Openlid`), refused
  at the requirements stage, naming both, before anything is emitted;
- a pin the part does not have, or a bus line the bus does not have.

A part with no outline is not refused: it is drawn at a declared placeholder size
([P115](https://github.com/xmejkal/spark/issues/49)). A rail nothing sources is not refused either: the generator notes
it, and the board does not route.

Each stage reads `[ok  ]`, `[!!  ]` for a defect in the design, named, or `[????]` for a stage that could not run,
which is not a pass.

Page: [`commands/build.md`](../../commands/build.md).

## Skills

| skill | use it when | what it does |
| --- | --- | --- |
| **spark-design** | "design a board for …", "wire up an ESP32 with …" | generates the board from a requirements file through spark's own chain (parts → pin map → `board.tsx` → build → simulation); tscircuit is written by hand only where the generator stops ([`SKILL.md`](../../skills/spark-design/SKILL.md)) |
| **spark-review** | "review my design", or before ordering a board | runs every deterministic check, then one `design-reviewer` per dimension (power, signals, thermal-mechanical, manufacturability, firmware-hardware) reading the primary artefacts only, and ends with the fabrication gate ([`SKILL.md`](../../skills/spark-review/SKILL.md)) |
| **spark-reverse-engineer** | a photo of a board, "what's connected to what" | fuses copper-trace reading, datasheet pinouts and functional reasoning into a netlist, then writes a bench protocol to confirm it ([`SKILL.md`](../../skills/spark-reverse-engineer/SKILL.md)) |

`spark-review`'s gate lists what nobody has checked about the parts you name. On the journey's example:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --unverified l9110s-module jst-ph-2-power-inlet tactile-button
```

<!-- output: run 2026-10-06, spark 0.6.0 -->
```text
  5 thing(s) nobody has checked:

  l9110s-module.pin_order = ['BIA', 'BIB', 'GND', 'VCC', 'AIA', 'AIB']
      a pin order read wrong reverses a supply or swaps a signal
  jst-ph-2-power-inlet.pin_order = ['VCC', 'GND']
      a pin order read wrong reverses a supply or swaps a signal
  tactile-button.debounce_ms_typical = 40
      too short double-fires a control, too long makes a remote feel broken. On a driving remote it is the difference between steering and twitching.
  tactile-button.cap_height_mm = None
      the only dimension that decides whether the enclosure closes
  tactile-button.pin_order = ['A', 'B']
      a pin order read wrong reverses a supply or swaps a signal
```

`spark-reverse-engineer` writes its bench protocol from
[a template](../../skills/spark-reverse-engineer/references/test-protocol-template.md) written for the smart bin's
original board. The skills themselves were not run for these pages.

## Agents

| agent | launched by | what it does | model · tools |
| --- | --- | --- | --- |
| `part-finder` | `/spark:research`, for a commodity part | finds the exact part for one need: at most two candidates, each with its maker, orderable part number and the maker's datasheet URL. It writes nothing, and you pick ([`part-finder.md`](../../agents/part-finder.md)) | haiku · web search, web fetch, JLCPCB part search |
| `datasheet-reader` | `/spark:research`, once the part is chosen and its datasheet kept | fills one part record from one kept datasheet, reading only the pages that hold the facts asked for. Every fact is cited to its page, with no web search ([`datasheet-reader.md`](../../agents/datasheet-reader.md)) | sonnet · files, shell, Espressif's documentation (a remote search) |
| `parts-researcher` | `/spark:research` for a module, `/spark:identify` | researches one module from primary sources, vendor by vendor, or identifies one from a photo. It marks every fact nobody has confirmed ([`parts-researcher.md`](../../agents/parts-researcher.md)) | opus · files, shell, web search, web fetch |
| `design-reviewer` | the `spark-review` skill, one per dimension | reviews one dimension of a design for what no automated check can catch, and returns findings as JSON. It only reads ([`design-reviewer.md`](../../agents/design-reviewer.md)) | opus · read, grep |

The two MCP servers spark declares serve these agents: **jlcpcb** for `part-finder`, and **espressif-docs** for
`datasheet-reader`.

How they have done so far:

- `parts-researcher` wrote the Kingbright L-7113ID LED record on 2026-10-03, on a lean brief, before the two smaller
  agents existed. It is the worked example in the design skill's
  [part-data notes](../../skills/spark-design/references/part-data.md).
- `part-finder`'s first use, on 2026-10-03, broke its search budget, returned the wrong variant's part number, and
  stated a current the maker's page does not. Checking its claims against the maker's document caught both, and its
  rules were tightened the same hour.
- `datasheet-reader` has not yet run on a real need.
- `design-reviewer` has been measured only in a few trial runs ([honest limits](../../README.md#honest-limits)).
