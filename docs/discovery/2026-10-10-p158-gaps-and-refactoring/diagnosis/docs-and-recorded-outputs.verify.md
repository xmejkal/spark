# Verification — docs-and-recorded-outputs (P158 part 1, rows K68–K74)

Written 2026-10-10 by a verifier who did not write the diagnosis, against spark 0.8.1 (main `a8aa34d`). Every cited line
was opened and is quoted below; every claim that could be run was run. Setup: a `git archive HEAD` of spark unpacked at
`<scratch>/spark`; a copy of the PO's store at `<scratch>/store` and an empty one at `<scratch>/store-empty`; every spark
command with `SPARK_HOME`, `HOME` and `TMPDIR` as three separate words (checked once with `env | grep SPARK_HOME`),
`CLAUDE_PLUGIN_ROOT` at the copy; `PATH` led by the bin's `node_modules/.bin` for `tsci` 0.0.2621 on the one build.
`gh` read-only (issue #94's comments; one API GET that `check_vendor_pins.py` itself makes). Nothing ran against
`~/.local/share/spark`; nothing was written under spark but this file. Tags: E a pointer, H a claim with its source,
D a decision, — unknown. Line numbers are spark's at `a8aa34d`.

One process note: my first run of the README block was made under zsh, which passes an unquoted `$line` as one word and
has no `PIPESTATUS`; every `parts.py` call failed on its arguments and every exit code came back empty. Those results were
discarded and the block was re-run as a bash script. The numbers below are from the bash run only.

## Verdicts

### RC-docs-and-recorded-outputs-1 — the gate proves a note exists, never that it is current — **holds**

Lines read (E):

- `tools/check_docs.py:20` — `OUTPUT_NOTE = re.compile(r"<!-- output: run \d{4}-\d{2}-\d{2}, spark \d+\.\d+\.\d+ -->$")`
- `tools/check_docs.py:145` — `for number, above, _ in _fenced(text, "text") if not OUTPUT_NOTE.match(above)]`
- `tools/check_docs.py:165-166` — `if done.returncode != int(mark.group(1)):` /
  `said.append("the example `%s` exits %d, not %s" % (first, done.returncode, mark.group(1)))` — an exit code, never
  the output (`done.stdout` is captured at `:160` and never read).
- `tools/check_docs.py:173` — `return [] if "v%s" % version in readme else ["README.md does not say v%s, the version plugin.json ships" % version]`
- `docs/guide/journey.md:195` — "These commands ran from a recording script, not through `/spark:idea` in Claude Code, so the session id that `--step`"
- `scrum/README.md:233-234` — "Nothing mechanical checks it: `tools/check_docs.py` cannot tell whether a status is still
  current, so the council reads it."
- `docs/2026-10-05-readme-design.md:100` — "6. a pasted output block has no `output:` comment with a date and a version;"

Numbers re-measured (E, my runs 2026-10-10): `grep -o 'spark 0\.[0-9]\.[0-9]' docs/guide/*.md README.md | sort | uniq -c`
→ 0.6.0: agents 2, commands 1, developing 1, journey 12 (16); 0.7.0: developing 4, journey 24 (28); 0.8.x: 0. Fenced
```` ```text ```` blocks: agents 2, commands 1, developing 5, journey 34, README 0, AGENTS 0 (42); `<!-- output: run` notes
per page: the same four counts (42); the two prose markers are `journey.md:39-40`. Release commits: `87daf54` (2026-10-08,
0.7.0: 2 files, 2 lines), `36d6998` (2026-10-09, 0.8.0: plugin.json, README, scrum/README), `1fc0909` (2026-10-09, 0.8.1:
2 files, 2 lines) — `git show --stat`. `git ls-files .superpowers | wc -l` → 0; `git log --all --diff-filter=A
--name-only | grep -i record` → nothing was ever committed. `python3 tools/check_docs.py` on the archive copy →
`docs: 7 file(s), nothing named that is not there`, exit 0, 5.5 s wall.

Precision, not a refutation: "the plugin's version is tied to README's footer alone" — the code tests `"v0.8.1" in
readme`, anywhere in README.md, not the footer; the point (README only, no guide) stands. "A one-off script that was never
committed" holds as stated; the script is nevertheless on the PO's disk, untracked — see missed cause M1, which changes
what Change 3 should do.

### RC-docs-and-recorded-outputs-2 — the README's typed block is outside the gate and ends in a step only Claude Code can finish — **holds**

Lines read (E):

- `README.md:123` — "are what let the tally count the cost. The block leaves them out, so its last line exits 2: no step is in the history."
- `README.md:124-125` — a blank line, then "```sh": no `<!-- runs: exit N -->`; `tools/check_docs.py:153-154` —
  `if not mark:` / `continue`.
- `commands/idea.md:13` — "Mark each step below — S, M, C and L — so the cost line can count what it took: M, C and L at their start, and S as soon"
- `commands/idea.md:169` — "what the line's words mean. Say it as it is; "its cost was not counted" is an answer too."
- `scripts/cost.py:225` — `raise NoTranscript("no step of %s is in the history — `parts.py --step <project> <step>` marks each" % project)`
- `scripts/cost.py:232` — `raise NoTranscript("no transcript of session %s here, so the cost of its steps is not known" % session)`
- `docs/guide/journey.md:195-197` — the hand-set `CLAUDE_CODE_SESSION_ID=demo-session`.

Run (E, bash, empty store, archive copy, the README block typed line by line, 2026-10-10): `--needs-set` exit 0; `--match`
exit 0; `--pick` exit 0 (`to get — known, not owned` ×3, `listed proj on your projects`, `wrote to your history: 3 reused`);
`--requirements` exit 0; `check_spine.py requirements.json --keep .` exit 0, 6 s wall, `the chain runs end to end`;
`--tally .` exit 2, `no step of proj is in the history — `parts.py --step <project> <step>` marks each`; after `--step . S`,
`M`, `C`, `L` with a hand-set session id: exit 2, `no transcript of session verifier-session here, so the cost of its steps
is not known`. The diagnosis's five-and-one is reproduced exactly.

One addition: typed before `--pick`, the tally says a third thing — `. is not on your list of projects, so no step of it
was marked — mark a step with parts.py --step <project> <step> in a Claude Code session: that puts it on the list`
(E, my run). README:123's prediction is right only because `--pick` lists the project first; a reader who skips a line
gets a sentence README does not explain.

### RC-docs-and-recorded-outputs-3 — "not run" is prose, about twenty places, no list, no date, no way to retire — **partly**

Lines read (E):

- `README.md:62-64` — "The table says the same in words. Each status comes from runs made for these docs, this README and
  the guides in `docs/guide/`, on 2026-10-05, 2026-10-06 and 2026-10-08; … and what was not run."
- `docs/guide/how-it-works.md:155-156` — "Another board needs its own definition, a JSON file in the project's `boards/`;
  this was / not run for these docs."
- `council/round-0-runner.md:8` — "Wall time 14 minutes." `:29` — "R/project/boards/firebeetle2-esp32c6.json (sha256
  4e5029ac…3872), …"; `find docs/discovery -iname '*c6*'` → nothing (E, my run).
- `scrum/README.md:233-234` as above.

Count re-measured (E): the diagnosis's grep → 26 lines (README 12, agents 2, commands 2, how-it-works 1, journey 9);
six define the words or describe behaviour (README:64, :65, journey:32, agents.md:126 "never run it unasked", :462,
commands.md:67 "It never runs `sudo`") → 20 admissions, as the diagnosis says. The grep misses one, split over two lines:
`journey.md:384-385` "in Claude Code and not / recorded for this page" → 21. "About twenty" stands.

What is weaker than written: "**no way to retire one**". A way exists and is the convention's own — record the run for
the docs and delete the sentence; Change 4 does exactly that. What is missing is anything that *prompts* or *dates* a
retirement. Change the sentence to: "no list, no date, and nothing that prompts a re-run or a retirement; retiring one is
an edit after a recorded run". And K70's word "stale" (catalogue row K70: "stale since round 0 ran it") misreads the
convention the README states at :62-63 — a status is "runs made for these docs"; round 0 ran in a scratch folder, by an
agent, its board file is not in the repository and its results are in a discovery folder, so by the docs' own definition it
is not a run for these docs. The diagnosis half-says this ("still literally true … and still misleads"); the catalogue's
severity "misleads" holds only for a reader who reads "for these docs" as "ever". The rival explanation — the docs, not
the tool — is the right one here, and RC-3's kind ("documentation, on a design limit that is honest") already says so.

### RC-docs-and-recorded-outputs-4 — the own-board pages are the bin's workflow and omit three facts the scripts hold — **partly**

Lines read (E):

- `boards/README.md:3` — "> The schema and the contract are spark's. The steps are the smart bin's: they name a Makefile, `make check` and `config.py`,"
- `boards/README.md:60` — "`espressif/arduino-esp32` → `variants/<board>/pins_arduino.h`. Pinout diagrams are drawn by"
- `docs/guide/how-it-works.md:171-172` — "4. **`check_vendor_pins.py boards/<id>.json`** compares the pin map with the
  vendor's header that / `vendor.arduino_variant` names, fetched through the GitHub CLI `gh`."
- `scripts/check_vendor_pins.py:62-63` — `raise RuntimeError("could not fetch %s from %s: %s" / % (path, repo, result.stderr.strip()[:200]))`;
  `:117` — `variant = (board.get("vendor") or {}).get("arduino_variant")`; `:136` — `return {"board": path.stem, "status": "could-not-run", "reason": str(broken)}`;
  `:169` — `print("  %-24s could not run: %s" % (result["board"], result["reason"]))`.
- `scripts/parts.py:968` — `found = store.records("parts", LIBRARY, project, drafts=True).get(part_id)` (parts layers only);
  `:1148` — `paths += [path for _, path in boards.records(project).values()]` (boards' documents are read);
  `:1674` — `raise PartError("no record called %r to fetch for" % args.fetch)`, and `fetch_documents` (`:1245-1256`) raises the
  same sentence for a non-dry run; `:2204-2207` — `except PartError as broken:` → `Answer(problems=[…])`;
  `scripts/outcomes.py:19` — `EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN = 0, 1, 2`.
- `boards/firebeetle2-esp32s3.json` — `documents` holds `url`, `sha256`, `file`, `retrieved`, `title`, `version`,
  `private_only`; `member` at `:335` and `:344`; `boards/xiao-esp32-c6.json` has no `documents` (E, `python3 -I`).

Runs (E, 2026-10-10): `parts.py --fetch firebeetle2-esp32s3 --dry-run` on the store copy → `parts.py: no record called
'firebeetle2-esp32s3' to fetch for`, exit 1. `boards.py --list` → `firebeetle2-esp32s3 (library)`. `parts.py --kept wroom`
→ the WROOM-1 v1.1 datasheet, `present`, cited by `power.module_peak_a — Table 11, page 15`, `power.deep_sleep_ua —
Table 12, page 15`, `power.io_volts — Table 9, page 14`. A board file with `arduino_variant` set to
`dfrobot_no_such_variant`, authenticated (`GH_TOKEN` from `gh auth token`): `mystery-board could not run: could not fetch
variants/dfrobot_no_such_variant/pins_arduino.h from espressif/arduino-esp32: gh: Not Found (HTTP 404)`, exit 2;
unauthenticated: the same sentence ending `gh auth login`, exit 2. Two causes, one shape — as the diagnosis says.

What is narrower than written: the "where" says "the page gives the path pattern and the record gives the field", and
Change 4 (1) proposes to add "that `vendor.arduino_variant` is the field `check_vendor_pins.py` reads". That sentence is
already on the page, at `how-it-works.md:172`. The gap is only how a person finds the folder's *name*; cut the second half
of Change 4 (1). The 409-folder count is the diagnosis's fetch (H); I did not repeat it. The exit code: `PartError →
problems → 1` is parts.py's rule for every unknown id, not a slip in `--fetch`; the diagnosis's "refusal tells the truth,
exit 2" is implementable consistently only through the argument-refusal path (`parts.py:2193-2195`, `_cannot` → unchecked
→ 2), which is where "a board id is not a part" belongs.

### RC-docs-and-recorded-outputs-5 — the gate's scope is a list of three places; style has no rule — **holds**

Lines read (E):

- `tools/check_docs.py:32` — `files = [root / "README.md", root / "AGENTS.md"] + sorted((root / "docs" / "guide").glob("*.md"))`
- `tools/check_docs.py:201` — `print("docs: %d file(s), %s" % (len(doc_files()),`
- `docs/2026-10-05-readme-design.md:92` — "It reads `README.md`, `AGENTS.md` and `docs/guide/*.md`, and fails when:";
  `:39` — "### `README.md` — about 120 lines, value first"
- `docs/guide/developing.md:157` — "[`tools/check_docs.py`](../../tools/check_docs.py) reads `README.md`, `AGENTS.md` and these guides. The suite runs it"
- `tests/test_orphans.py:27-31` — `def routes():` … `files = list((ROOT / "commands").glob("*.md")) + list((ROOT / "skills").glob("*/SKILL.md")) \`
  `+ list((ROOT / "agents").glob("*.md")) + [ROOT / "README.md"] \` `+ sorted((ROOT / "docs" / "guide").glob("*.md")) + …`
- #94, comment of 2026-10-08 (E, `gh issue view 94 --comments`, read-only): "C-36: The docs gate does not read the pages
  agents follow … — fix: widen `doc_files`, then the edits · est. ~5 code + ~40 doc lines"; "C-36's `check_docs.py`
  widening stays here"; the style parts "DOC-39's first half (README's density — 231 lines against its design's ~120),
  DOC-47 (jargon at idea.md:11/14/52, build.md:65, research.md:99), DOC-48, DOC-49's remainder, DOC-50, DOC-51 (long
  lines), with the `check_docs.py` widening (DOC-37)". The diagnosis's jargon list omits idea.md:52 and build.md:65.

Run (E, 2026-10-10): the five per-page functions (`missing_names`, `missing_flags`, `undated_outputs`, `broken_links`,
`personal_paths`) over the 14 agent pages (7 commands, 3 skills, 4 agents) → 0 problems; over `boards/README.md` → 2:
`README.md: config.py names no script` and `README.md: the output at line 15 has no `<!-- output: run DATE, spark VERSION
-->` above it`. Both as the diagnosis says. Note the prefix: the gate names a page by `path.name`, so `boards/README.md`
reads as `README.md` — see Change 5 below.

Long lines (E, `awk 'length($0) > 120'`): README 10 (longest 586), how-it-works 16, journey 32, agents 13, commands 11,
idea.md 23 (653), build.md 23 (691) — the diagnosis's numbers. awk on macOS counts bytes: in characters journey has 30
(two lines cross 120 only by their em dashes). By kind (characters): README 8 table rows + 2 prose (lines 208, 216);
journey 27 lines inside fences (recorded output) + 3 prose; how-it-works 13 table + 2 prose; idea.md 1 code + 13 prose;
build.md 6 table + 3 code + 14 prose. So the long lines of README and how-it-works are table rows Markdown cannot wrap, the
journey's are recorded outputs, and the prose offenders are the two command pages — which matters for Change 6.

### RC-docs-and-recorded-outputs-6 — the "menu" is a planning artefact; README's answer is three sentences apart — **holds**

Lines read (E):

- `scrum/SPRINT.md:611` — "**R2.5 — three domains; the PO's answer can be one letter.** Each is unlike both the bin and the"
- `scrum/PRODUCT_BACKLOG.md:1568-1569` — "them were invisible to every test in this repository. Two domains from the
  earlier menu are / unchosen — a battery sensor node, a USB MIDI foot controller — and the PO may name another."
- `README.md:25` — "On 2026-10-08 the library defined two dev boards and held 8 parts (`boards.py --list`, `parts.py --list`). Only the"
- `README.md:39` — "On the documented example (a FireBeetle 2 ESP32-S3, an L9110S motor driver, a power inlet and two buttons), from the"
- `README.md:145` — `{"board": "firebeetle2-esp32s3", "parts": ["tactile-button", "led-red-5mm"]}`
- `council/user.md:21` (USER-13) — "The library holds 13 parts and 2 boards (`parts.py --list`, `boards.py --list`), one board builds."

Run (E): `parts.py --list` → 8 lines in the empty store, 13 on the PO's store copy; `ls parts/*.json | wc -l` → 8. USER-13's
13 is the PO's shelf and catalog on top of the library. So "what spark can serve" has no one answer: it is per store, and a
README sentence can only point at the command — which is what Change 7 proposes. The diagnosis's "`parts.py --list` on
0.8.1 prints the same 8 rows as the recording" holds for an empty store, which is what the recording used.

## Missed root causes

- **M1 — the recorder exists, gitignored, path-bound and never promoted** (E). `.gitignore:8` is `.superpowers/`; under it
  sit `.superpowers/discovery-inputs/2026-10-08/council-p97/fix-docs-recorded/record.sh` (102 lines),
  `journey/record-journey.sh` (176), `journey/blocks.py` (22 — prints each ```` ```text ```` block of journey.md with
  "whether it equals one of my recorded outputs") and the recorded outputs themselves (`journey/out`: 46 files; `rec-out`:
  29). Both scripts hard-code a worktree that no longer exists (`~/Development/spark-p97/scripts`) and one session's
  scratchpad. Nothing in them writes into a page (no `sed`, no `write_text`): the outputs went into journey.md by hand.
  So the mechanism behind K68 is sharper than "re-recording was a one-off script": a recorder and a comparer were built as
  discovery scratch, in a folder the repository is told to ignore, and the one step that was manual — the paste — is the
  one that did not happen at the next release. Change 3 proposes to write a recorder (A: cog; B: ~100 lines); remove
  before add says: promote or delete what is there first. The diagnosis's "the 'recording script' nobody has" (Change 3) is
  false for the PO's machine; "in no commit" is true.
- **M2 — not every recorded block has a command to re-run** (E, my fence walk over the guides, 2026-10-10). Of the 42
  blocks, 8 are not directly under a ```` ```sh ```` block: `journey.md:439` (under a `json` block; the command is in
  prose, "`--match .` then offered the record"), `:466`, `:495`, `:507` (second and third outputs of a command named in
  prose or in parentheses); `developing.md:103` (a push's gate line, which the page itself calls "a dated record, not
  today's output" at `:100`), `:121` and `:126` (two outputs of one three-command block), `:140` (a run on a suite
  recording, command in prose), `:151` (the no-`gh`-login case). Change 3 (B) — "running each ```` ```sh ```` block in page
  order and replacing the ```` ```text ```` block under it" — has no rule for these 8; Change 1 would mark
  `developing.md:103` stale for ever, against the page's own words.
- **M3 — several recorded outputs are not functions of (plugin, store, project)** (E, read from the pages).
  `developing.md:120-134`: `check_backlog.py` and `board.py status` read the live GitHub boards ("84 open", "in flight:
  Build P146 (#80) 3 d"); `:151` depends on whether `gh` is logged in; the build line carries the `tsci` version
  (`journey.md:39`, `0.0.2621`); `--pick` and `--step` outputs carry a session id and dates. A `--check` that diffs
  re-recorded text (Change 3) fails on another machine or another day for these, whatever the plugin did. The diagnosis's
  §4 names `tools.py --status` only. Any recorder needs two classes of block — re-recordable, and recorded-only (dated, kept
  as history) — and the note should say which.
- **M4 — there is no release gate** (E). `tools/pre-push` is `exec python3 …/tools/check_commit.py`; `check_commit.py`
  archives the commit and runs the suite (`:135`) and the mutation anchors (`:143`) — nothing about a version, a tag or the
  docs' notes. DoD 10 (`scrum/README.md:236-242`) is prose. Change 3's "`cog --check` … in the release gate, not the suite"
  names a place that does not exist — the same failure as `journey.md:195` naming a recording script: prose naming a
  mechanism nobody has. If the check is to run, it runs in `check_commit.py` when the commit changes `plugin.json`'s
  version, or it is a sentence.
- **M5 — `version_mismatch` keys on "v0.8.1 anywhere in README"** (E, `tools/check_docs.py:173`). A README that mentions
  the shipped version in any sentence passes while its footer says another. Small, but the diagnosis builds Change 1 on
  "the one currency rule that exists works" (§2): it works for a two-line release edit, not against drift inside README.
- **M6 — `failed_examples` isolates `SPARK_HOME` only** (E, `tools/check_docs.py:156-158`: `env = {… os.environ …}`,
  `env.update(CLAUDE_PLUGIN_ROOT=str(root), SPARK_HOME=store)`). `HOME`, `TMPDIR` and `PATH` are the developer's. A
  `runs:` block that reads `~/.claude/projects` (the tally) or `~/.config/gh` runs against the real home, and its exit code
  depends on the machine (logged in or not). Today's three blocks are listings and are safe; Changes 2, 4 and 5 widen what
  is marked `runs:` and must stay inside that bound. The mutation "an example runs in the person's store" covers
  `SPARK_HOME` only, so nothing would notice a block that reaches the real home.
- **M7 — the gate's sentences name a page by its file name** (E, `tools/check_docs.py:187`: `"%s: %s" % (path.name,
  sentence)`; my run printed `README.md: config.py names no script` for `boards/README.md`). With Change 5's scope the three
  `skills/*/SKILL.md` pages all read as `SKILL.md: …` and two READMEs as `README.md: …` — a failure that no longer names
  where. The fix is `path.relative_to(root)`, one token; it belongs in Change 5 or the widening makes diagnosability worse.
- **M8 — README shows no output at all** (E, 0 ```` ```text ```` blocks in README.md). The design asked for "Install and a
  first run: three commands, with output from a real run" (`readme-design.md:49`); the typed block at `README.md:125-132` has
  no recorded output, so a reader cannot compare what they see with what the docs saw. K69's rival explanation is also
  worth stating: the tally is `/spark:idea`'s T step and `idea.md:169` says "'its cost was not counted' is an answer too" —
  the author may have kept the line deliberately so a reader meets the honest refusal; Change 2 drops it from the block and
  keeps a sentence, so the refusal is told, never shown.

## The changes, judged

Against the PO's criteria of 2026-10-10 — testable; a failure names where and why, to a person and to an agent; remove
before add.

**Change 1 — the gate counts recorded outputs behind the shipped version.** Symptom, not mechanism: the number is K68's
measure; nothing re-records (Change 3 is the mechanism). The named test (literal Markdown, `spark 0.6.0` against a
plugin.json of `9.9.9`; a mutation row) would catch a regression of the function. The sentence proposed names page, line,
versions and the next action — good. But as a *failing* check it is wrong by design: (a) the key is the version, so a patch
that changes no output (0.8.1 changed component-name casing — `1fc0909`'s subject) makes 44 blocks "stale" at once, 44
false alarms the person must clear by re-recording or by hand marks; (b) `developing.md:103` is declared a dated record by
its own page (M2) and `developing.md:120-153` cannot be re-recorded to equality (M3), so exemptions are needed from day one.
As a report line it is harmless and tells the agent what the gate's summary now hides. Proposal: keep it as a report line
(the diagnosis's own interim), and let Change 3's diff be the only thing that fails — a version is provenance, a diff is
currency; or drop Change 1 and let the recorder's `--check` print the count. Breaks nothing for the bin, irrigation or
plant-alarm.

**Change 2 — the README block ends where a shell can finish it; the gate runs it.** Mechanism, confirmed by my run: four
lines exit 0 in an empty store; the build takes 6 s and needs `tsci`, so leaving it out of the gate-run block is right. The
gate's existing comparison and its mutation row cover it; adding the stdout tail to the failure sentence is the one thing
that makes it name *why*. Three gaps: (a) `README.md:119-120` says `/spark:idea` writes the needs "outside any repository,
here `../button-needs.json`" — a heredoc into the project contradicts the sentence above the block, so the sentence changes
with it; (b) the file in `../` lands in the suite's temp folder (P172 counts leftovers) unless the block keeps it in the
project — the diagnosis sees this; keep it in the project, the simpler of its two options; (c) M8 — give the block a
recorded ```` ```text ```` output with its note, and show the tally's refusal as a recorded block beside the sentence that
explains it, so README keeps the one place a stranger sees the honest exit 2. Cost: four more subprocesses per gate run
(`check_docs.py` took 5.5 s for 7 files on this machine). Nothing in the bin, irrigation or plant-alarm reads README's
block (E, `grep -rl` over the three repositories → none).

**Change 3 — one recorder at each release; drift fails a check.** The mechanism, and L is honest. Judged against what
exists: (a) M1 — a recorder, a comparer and 75 recorded outputs are on disk; promote them (de-path, commit, give them the
two scratch stores they expect) or delete them before writing a third; (b) M2 — 8 of 42 blocks have no `sh` block above,
so B's pairing heuristic fails on them; A's markers carry the command, which is the real argument for cog — but 3 marker
lines × 42 blocks is 126 lines in pages that agents read raw (HTML comments hide only in rendered Markdown; the diagnosis
lists this as untried), and the agent guide is one of those pages; (c) M3 — the `--check` is deterministic only for blocks
that depend on nothing but the plugin, the store and the project; the live-board and `gh`-state blocks need a
"recorded-only" class, and `retrieved` dates, session ids and the `tsci` line need redaction beyond paths; (d) M4 — "the
release gate" does not exist; the check runs in `check_commit.py` on a commit that changes `plugin.json`'s version, or
it is DoD prose again, which is exactly the failure being fixed. The named test (redaction unit test; `--check` at release)
catches drift only once (d) is real. The diagnostic — a unified diff per block — names where and what; the note's date
says when. Proposal: split L into (i) promote the existing recorder with an explicit per-block binding (the command and its
store, in the note or a marker), (ii) classify the 42 blocks, (iii) hook `--check` into `check_commit.py` on a version
change. cog's `--check`, `--diff` and comment markers are H from the diagnosis's reading of its pages; I did not verify them.

**Change 4 — the own-board route recorded on 0.8.1; three facts written where the steps are.** Mostly mechanism. (1)'s
first half (how to list the variant folders) is the gap; its second half is already on the page (`how-it-works.md:172`) —
cut it. (2) is right and verified: `--keep` prints the entry, `--kept` already reads boards' documents. (3) the recorded run:
`boards.py --validate --project .` on an unedited copy exits 1 with the id sentence (round-0-runner.md:18) — a
`<!-- runs: exit 1 -->` block that copies `$CLAUDE_PLUGIN_ROOT/boards/firebeetle2-esp32s3.json` into the temp project's
`boards/` is offline and fits the gate; `check_vendor_pins.py` must stay recorded, not gate-run: it reaches the network,
exits 2 with no `gh` login (M6), and a live run writes the header into the plugin's `.spark/cache` (G0.7, another area —
the two library boards' headers are tracked there: `git ls-files .spark` → `XIAO_ESP32C6.pins_arduino.h`,
`dfrobot_firebeetle2_esp32s3.pins_arduino.h`, which is why `--offline` works for them and for no new board). The code
fixes: the 404 sentence naming the field and the listing command — no test pins the old text (E, `grep -rn 'could not
fetch' tests/` → none), `tests/test_check_vendor_pins.py` exists to take a fake-`gh` case; `--fetch` on a board id — the
"refusal tells the truth, exit 2" variant is the one to take, through the argument-refusal path (RC-4 above); the
"`record_home` also looks in `boards/`" variant is not one line, since `fetch_plan` reads a parts record's cited URLs and a
board's `sources` and `documents` have another shape. The deletion of "this was not run for these docs" is right only once
the run is recorded on the page — the convention, not a date, retires it (RC-3). Proof as proposed (a second person makes
a board file from the page alone) is a test with a person in it; the two `runs:` blocks are the mechanical part.

**Change 5 — the gate reads the pages agents follow.** Mechanism (the list), verified silent today (0 problems over 14
pages). The named test and mutation row catch a shrunk scope. One defect to fix in the same change: M7 — the sentences
must name the page by its path, or three `SKILL.md`s and two `README.md`s are one name. Sharing one list with
`tests/test_orphans.py::routes()` is right in principle, but `routes()` also appends sibling projects' Makefiles
(`test_orphans.py:32-35`: `ROOT.parent / project / "Makefile"` for `smartbin-local` and `rc-car`) — that part must not
enter `doc_files`, or the gate reads another repository. `boards/README.md` deferred to P127 is right (2 problems today, one
a false positive of the ```` ```text ```` convention). Cost: `missing_flags` runs `--help` per script and verb, cached in
`helps`; 14 pages add lookups but no new scripts. Nothing breaks for current users; the smart bin's own `boards/README.md`
is in its repository, not spark's.

**Change 6 — density and long lines: one measured rule, or none.** The diagnosis's framing is right; its numbers are not.
"Lines over 120 columns outside tables and code (README 10, idea.md 23, build.md 23 today)" are the raw counts; by the
change's own definition they are README 2, idea.md 13, build.md 14 (characters; awk counted bytes). README's long lines are
8 table rows out of 10 — Markdown cannot wrap a table row — so README's "long lines" is a non-finding; the density figure
(231 against ~120) is real but `readme-design.md:39` is a wish, not a rule, and the PO decides whether it becomes one. A
report line nobody reads is the noise "remove before add" warns about: a rule that fails, or nothing. The edits overlap
Change 2: both touch `README.md:111-158`; cutting "Two roads to a board" to a pointer removes K69's block altogether, which
is the simplest fix for K69 — but it also removes the only typed commands a stranger sees in README, against
`readme-design.md:49`. The PO picks one shape for that section; the two changes should be one card.

**Change 7 — one sentence on what spark has built and where the library is listed.** A sentence; no mechanism needed, as
the diagnosis says. Add the per-store fact: the library holds 8, and `parts.py --list` adds what the person's store holds
(13 on the PO's copy), so the sentence does not promise a number the command will contradict.

## What breaks for current users

- **The smart bin** (`~/Development/smartbin-local`): its `CLAUDE.md` names `parts.py --kept <word>` three times
  (`wroom`, `dfr0975`, `dfr0534-datasheet`); no change here touches `--kept`'s output. It calls neither `--fetch` on a
  board id nor the README block. Change 4's `check_vendor_pins.py` sentence changes only the 404 case; the bin's `make check`
  runs the vendor check on its own board file, which has a valid variant (E, `boards/firebeetle2-esp32s3.json`
  `arduino_variant = dfrobot_firebeetle2_esp32s3`). Nothing breaks.
- **irrigation, plant-alarm**: neither reads `docs/guide/journey.md`, the README block, `button-needs.json` or
  `check_docs.py` (E, `grep -rl` over both, 2026-10-10 → none). Nothing breaks.
- **The maintainer** (the PO): Change 1 as a failing check adds 44 items to clear at the next release; Change 3 (A) adds a
  dependency (`cogapp`) and 126 marker lines to pages agents read raw; Change 2 and 5 lengthen the pre-push gate by a few
  seconds (the whole docs gate was 5.5 s here); Change 4's deletion of the "not run" sentence is honest only with the
  recorded blocks beside it.
- **Tests**: `tests/test_needs.py:1277` asserts "no record called x-gone any more" — a different sentence from `--fetch`'s;
  no test asserts `could not fetch` (E, grep). The mutation table `tests/mutations/p104-docs.json` (14 rows) needs new rows
  for each new function (Changes 1, 5, 6), or `tools/mutate.py --anchors` in `check_commit.py` will not know them.

## Searches

- No web search. cog's `--check`, `--diff` and comment markers are the diagnosis's claims (H, its reading of
  cog.readthedocs.io, 2026-10-10), not verified here.
- `gh issue view 94 -R xmejkal/spark --comments` (read-only, 2026-10-10) · decision served: whether C-36's text says "widen
  `doc_files`" and which style items it names · used.
- One GitHub API GET made by `check_vendor_pins.py` itself (`gh api repos/espressif/arduino-esp32/contents/variants/
  dfrobot_no_such_variant/pins_arduino.h`), once with `GH_TOKEN` from `gh auth token`, once without · decision served: the
  refusal's wording and exit code for a wrong variant name, authenticated and not · used (404, exit 2; `gh auth login`,
  exit 2). The 409-folder listing was not repeated (H, the diagnosis's).
- `gh auth status` (read-only) · to know whether a 404 could be told from "not logged in" · used.
