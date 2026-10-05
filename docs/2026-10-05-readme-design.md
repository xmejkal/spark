# The README and its guides — design (P104)

**Status:** the spec, for the PO's review (2026-10-05). Issue: xmejkal/spark#33, slice 1 (*Public*: a stranger can
install and use spark).

## 1. What it is for

The PO, 2026-10-05: *"rewrite the readme, so that the spark github really describes well what its about, how to use
it, how to have claude code or other ai use the plugin, what functionality there is, with examples, what agents,
skills, but really mostly first the value, what it does and maybe what it uses underneath, how it connects it … a good
no hallucination readme, maybe with subpages that it links to where there are details for the subsections … well
readable for both ai and humans."*

Today's README (175 lines) opens with *"checks for a board made of modules"*. It lists every script, and its last
line holds a literal `\n\n`. It never says what the journey is or which of its steps work.

**Done means:**
- `README.md`, five guides in `docs/guide/` and `AGENTS.md` are merged.
- `tests/test_docs.py` is green, with a mutation table for its verdicts.
- Every finding of the council is fixed, or carded with the docs saying *not yet*.
- The PO has read the README before the merge.

## 2. Who reads it

- **The hobbyist** (the vision's primary persona, a hypothesis): has an idea in words, an ESP32 board in the drawer
  and some modules, and works in a terminal.
- **An AI agent in Claude Code.** Every logged run so far was one. It must act on what the docs and a script's answer
  say, without reading source.
- **Another AI** (Codex, Cursor, a custom agent). It cannot load a Claude Code plugin, but spark's scripts run on their
  own, and the checks answer in JSON.

Readable by both means:
- plain Markdown with headings that name their content;
- nothing said only in a picture: the Mermaid diagram has its sentence beside it;
- every term spark uses differently from everyone else is linked to `GLOSSARY.md`.

## 3. The document set

### `README.md` — about 120 lines, value first

1. **What spark is: the journey.** In a few sentences: a gadget described in words becomes the needs and the kinds
   of module that meet them; spark researches each part from the vendor's documents, assigns every pin with a reason,
   generates a board that builds and simulates, and checks it, refusing rather than guessing and saying when a check
   could not look. A Mermaid diagram of the journey.
2. **What works today.** One row per step: idea, drawer, research, build, checks, firmware, bench.
   - Each row is marked **works**, **partly** or **not yet**, with the command that does it.
   - *Partly* and *not yet* say where the step stops, for example that `/spark:idea` stops after matching your parts.
   - Every row links its evidence: a section of `docs/guide/journey.md` that ran it, or the card that will build it.
3. **Install and a first run:** three commands, with output from a real run.
4. **Commands, skills, agents:** one line each, linking `docs/guide/commands.md`.
5. **For AI agents:** two lines, linking `docs/guide/agents.md`.
6. **What it uses underneath:** one line each, linking `docs/guide/how-it-works.md`.
   - tscircuit, KiCad, Wokwi, MicroPython;
   - the two MCP servers, jlcpcb and espressif-docs;
   - the person's own store in `~/.local/share/spark`.
7. **Honest limits.**
8. **Links:** the glossary, `docs/guide/developing.md`, the version and the licence.

### `docs/guide/` — five pages

| page | what it holds |
| --- | --- |
| `journey.md` | each step of the journey with its commands, run on the documented example (the requirements file in `commands/build.md`). Every pasted output comes from a real run, dated, with spark's version |
| `commands.md` | every command, skill and agent: when to use it, an example, what it writes, what it refuses |
| `agents.md` | for an AI. In Claude Code: the commands. Anywhere else: the scripts directly — their inputs, `--json` shapes, exit codes, the four outcomes (`ok`, `problems`, `could-not-run`, `skipped`), and what an agent must never assume |
| `how-it-works.md` | the scripts and libraries; the data (boards, parts, fabrication); the person's store; the toolchain and MCP servers (linking `docs/mcp.md`); how a requirements file becomes a checked board |
| `developing.md` | the tests and their rules, mutation tables, the push gate, a link to the process in `scrum/` |

`AGENTS.md` at the repository root is a short pointer to `docs/guide/agents.md`. Several AI coding tools read a file
of that name; it holds no rules of its own.

**What moves out of today's README:**
- the scripts list goes to `how-it-works.md`;
- the test rules go to `developing.md`;
- the stray `\n\n` line is dropped.

## 4. The rules for a claim

- **Every claim has a source a reader can follow:** a command and its output, a file, a test, or a card for what is
  not built.
- **A pasted output is real.** An HTML comment above it says when it was run and on which version, for example
  `<!-- output: run 2026-10-06, spark 0.6.0 -->`. It is invisible on GitHub and read by the test.
- **A runnable example says how it ends,** with a comment such as `<!-- runs: exit 0 -->` above its block. Only light
  examples are marked runnable: no network and no board build.
- **No number that rots.** Today's README, under *Tests*, says its test count *"rotted three times in four days"*.
  A count appears only inside a dated output.
- **If a step fails while the docs are written,** the docs say *not yet*, and the failure becomes a bug card. It is not
  fixed inside P104.

## 5. The docs test — `tests/test_docs.py`

It reads `README.md`, `AGENTS.md` and `docs/guide/*.md`, and fails when:

1. a `/spark:<name>` the docs name has no `commands/<name>.md`;
2. a script (`<name>.py`) the docs name is not in `scripts/` or `tools/`;
3. the command, skill and agent tables in `commands.md` and the README do not list exactly the commands, skills and
   agents that exist — none missing and none extra;
4. a flag shown with a script in code is not in that script's own `--help` output;
5. a relative link points to a file, or a heading anchor, that does not exist;
6. a pasted output block has no `output:` comment with a date and a version;
7. a block marked `runs:` does not end as it says when run in a temporary project (a timeout bounds it);
8. the README's version differs from `.claude-plugin/plugin.json`'s.

**Two existing tests change too.** `tests/test_orphans.py` and `tests/test_routes.py` check that every script and
skill is named where a user looks, and today they read only `README.md`. The scripts list moves to
`how-it-works.md`, so both also read `docs/guide/*.md`.

**A mutation table**, `tests/mutations/p104-docs.json`, takes one row per verdict above.

## 6. The council

One round, on the finished drafts, before the PR. Four lenses, each a fresh agent:

1. **Fact-checker:** every claim against the code or a run. It returns each claim without a source.
2. **A stranger:** from the README alone, installs and runs the first steps in an empty scratch directory.
3. **An AI agent:** given only `AGENTS.md`, does a real job — checks a board and reports its result — without
   reading source.
4. **An editor:** readable for people and AI, short, every term defined or linked.

Their findings go to the PO with the proposed fixes. The PO reads the README before the merge.

## 7. Order of work, and its limits

1. **The test first.** It fails on today's README, which has no guides or `AGENTS.md`.
2. **Facts before prose.** Each journey step is run on the documented example in a scratch project, and its output
   kept.
   - **Nothing new is installed without the PO's yes:** the tscircuit and toolchain already on this Mac are reused.
   - **No Wokwi minutes are spent:** the simulation step shows its command and a dated earlier run, or says it was not
     run here.
3. **The guides,** written from the files themselves (command, skill and agent files, `--help`, the scripts). Then
   **the README**, distilled from them. Then **`AGENTS.md`**.
4. **The council,** then the PO's read, the PR, the final review and the merge. All of P104 is one PR.

## 8. Not in this spec

- Fixing what the docs reveal: those become bug cards.
- A documentation site.
- The story-map drawings (P102b).
- Translations.
- Restructuring `GLOSSARY.md` beyond links.

## 9. Decisions (the PO, 2026-10-05)

1. The opening leads with **the journey**, each step marked by what works today.
2. **A page for agents,** `docs/guide/agents.md`, with `AGENTS.md` pointing at it.
3. **Truth is kept by the council and a test.** The test fails on anything named that does not exist, a broken link, a
   flag missing from `--help`, an undated output, or a failing runnable example.
4. **A short README with five guides** in `docs/guide/`.
5. Sections 1–3 of the design as presented: the document set, the test and council, and the order and scope.

### The council round (the PO, 2026-10-05)

The council (fact-check in two halves, a stranger, an AI agent, an editor; every finding put to an adversarial
verifier) returned 110 findings: 93 confirmed, 17 partly, none refuted, collated into 61 fixes. The PO decided:

6. **Simulation gets its own row,** marked partly: the build generates a Wokwi diagram; a run needs firmware, a
   scenario and Wokwi minutes. §3.1's "builds and simulates" now reads "builds, with a Wokwi diagram generated".
7. **Drawer is partly** (the plain-words entries and the DFRobot import were not run for these pages). **Checks is
   scoped to `check_all.py`** and stays works; `spark-review` is named as the next step, not run here.
8. **The headline says what works today,** a list of modules to a checked board; the idea is where it is going.
9. **Drawer comes before Idea** in the journey, the README's table and both diagrams — the order the runs were made in.
10. **Uncarded "not yet"s become facts:** scripts that do not take `--json` are said not to (P92 for `tools.py`), and
    research from `/spark:idea` is dropped until it has a story.
11. **The Bench row links P79** (spark#16), naming the bin's P73 and B14 as the first bench, with a sentence on what
    the bin is.
12. **A change to a journey step updates the journey guide and the README's table** — a Definition-of-Done item.
13. **Cards, not docs, for what spark does wrong** (§4): check_physics's silent skip on a null rail voltage and its
    crash on a null bus capacitance; a null `max_current_a` stays a `?` line and `check_all` says how many unmeasured
    values its answer rests on; `check_all` reports the generator's CONFLICT lines — a problem on verified facts, a
    `?` line otherwise; `--keep .` builds the kept `board.tsx` into `dist/`; an explicit not-applicable value for
    fields a design does not need; both MCP packages pinned and their rows labelled "declared, not checked" (the
    README names `@jlcpcb/mcp` as a community package now).
