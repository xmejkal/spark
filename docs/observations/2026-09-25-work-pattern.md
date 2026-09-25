# How this plugin is actually being built — 2026-09-25

Observer: a session given read-only access to `~/Development/spark` and `~/Development/smartbin-local`,
the full git log of both, `BACKLOG.md`, `docs/audit-2026-09-24/`, and permission to run the
plugin's own tooling. It built nothing.

**Claims are numbered O1–O9 so they can be logged in `INDEX.md` one line each.** Each says
whether it was *measured* (something was run and the output is quoted) or *inferred*.

Scope note that frames everything below: the spark repo is **57 commits old and was created at
2026-09-23 17:37**. "These two days" is the entire life of the project. There is no inherited
codebase here. Every defect repaired in this window was introduced in this window, by this author.

---

## O1 — The defect class §4d calls closed is not closed. `check_physics` has an eleventh instance, live right now. *(measured)*

This is the most important thing in the note, so it is first.

`BACKLOG.md:270-288` lists ten places where "every instrument built to say 'this is fine'
reported success when it had not looked", each "now with a test that fails without it and a
mutation run proving so". Two of those ten are `b7afbff` and `5b73287` (2026-09-24 23:03): the
engine moved `footprinter_string` from `pcb_component` to `cad_component`, so
`check_footprints`'s lookup returned `None` for every part and two rules examined nothing.

`scripts/check_physics.py:131-139` still has the old lookup, verbatim:

```python
def footprint_of(self, component_name):
    """The package string, e.g. '0805'. Taken from the PCB side, which is what is built."""
    ...
    for pcb in self.pcb_components.values():
        if pcb.get("source_component_id") == source["source_component_id"]:
            return (pcb.get("footprinter_string") or "").strip() or None
```

Measured against the reference board's real netlist:

```console
$ cd ~/Development/spark && python3 - <<'EOF'
import json, importlib.util
spec = importlib.util.spec_from_file_location('cp', 'scripts/check_physics.py')
cp = importlib.util.module_from_spec(spec); spec.loader.exec_module(cp)
circuit = json.load(open('/Users/petr/Development/smartbin-local/dist/board/circuit.json'))
board = cp.Board(circuit)
names = [e['name'] for e in circuit if e.get('type') == 'source_component']
print("footprint_of non-None:", sum(1 for n in names if board.footprint_of(n)), "of", len(names))
EOF
footprint_of non-None: 0 of 28
```

Zero of twenty-eight. `cad_component` carries the string for 19 of them; `pcb_component` carries
it for **0**.

The consequence, at `scripts/check_physics.py:267-271`:

```python
footprint = board.footprint_of(component_name) or ""
rated = next((w for size, w in PACKAGE_POWER_W.items() if footprint.startswith(size)), None)
...
if rated is None:
    continue
```

`rated` is always `None`, so `check_resistor_power` hits a **bare `continue`** for every resistor
on every board, reports nothing, and `check_all` renders `[ok  ] physics`. The board has eleven
resistors. The rule has examined none of them, ever.

There is a second, independent reason the same rule cannot fire. The engine emits `res0603`,
`res2512`; `PACKAGE_POWER_W` (`check_physics.py:64`) is keyed `"0603"`, `"2512"`, and the match is
`footprint.startswith(size)`. `"res0603".startswith("0603")` is `False`. **Fixing the field alone
will not wake this rule.**

And a third: if it did wake, it is arithmetically wrong. It multiplies the *rail's* maximum
current through *every* resistor on that rail. With the real rules file that computes 25 kW
through a 100 k pull-up on V33 — five libellous findings. The rule has never fired in either
direction, which is why nobody has noticed it is wrong in both.

Why the tests are green: `tests/test_check_physics.py:58-60` builds the fixture as
`{"type": "pcb_component", ..., "footprinter_string": footprint}` and `:200` passes a bare
`"0805"`. That is the exact stale-fixture shape `5b73287` fixed in `test_check_footprints.py`
thirty-three seconds after `b7afbff` — and did not fix here, one file over.

`BACKLOG.md:358-360` (N4) names `check_physics` as unexamined. So this was known to be a risk and
placed fourth on the Now list. It is not fourth. It is the same defect as the two at the top of
§4d's table of ten, in the check the project's own `§4` table calls its physics win.

Also unexamined for the same class, both named in N4 and both confirmed by reading:
`check_physics.py:258` silently skips a rail with no `nominal_volts` (while the trace-current rule
three functions up correctly reports it) — and `/spark:init` writes **every value null**, so a
freshly-initialised project gets a capacitor-voltage rule that examines nothing and says nothing;
`compare_design.py:196` silently skips a pull-up with no resistance value.

---

## O2 — By commit count, more of these two days was repair than was new capability. *(measured; the classification is my judgement)*

I classified all 57 commits by primary intent and summed the diffs:

| | commits | insertions | deletions |
| --- | --- | --- | --- |
| new capability | 19 | 8,204 | 182 |
| **defect repair** | **22** | **4,072** | **857** |
| reference data (parts/boards facts) | 8 | 337 | 34 |
| docs / bookkeeping | 8 | 1,157 | 104 |

**Repair is the largest single category by commit count — 22 of 57, 39%.** By lines, new
capability is about 2× repair, but that number flatters: `b05775f`'s 1,147 lines of initial skills
include `spark-verify` and `spark-check`, both **deleted** 27 hours later in `47a04c0`, and a
README rewritten twice.

So, plainly: **roughly two-fifths of the work of these two days was the author repairing damage
the author had caused in the previous few hours.** Not inherited damage. Not third-party damage.
There is no third party — the repo is 41 hours old.

The median age of a defect at the moment it was repaired is about **two and a quarter hours**
(inferred: I took the introducing commit from the repair commit's own message). Six of the 22
were under forty minutes:

| repair | fixes | age |
| --- | --- | --- |
| `5b73287` | `b7afbff` | **33 seconds** |
| `a2e0c74` | `2b8ddb4` | 5 min |
| `76f27cb` | `8d55a8e` | 8 min |
| `80934c0` | `0220bbd` | 15 min |
| `312b541` | `02250ee` | 23 min |
| `010ba78` | `02250ee` | 39 min |

Three of those are a *partial fix shipped as a complete one*:

- `8d55a8e` "Let a project extend the parts library, which it could not" made `--project` reach the
  library. `76f27cb`, eight minutes later, made it reach the two callers that consume it — "Half a
  use case is worse than none".
- `2b8ddb4` split outputs from rails. `a2e0c74`, five minutes later: "It said half of it."
- `b7afbff` fixed the moved field. `5b73287`, thirty-three seconds later, added the test that the
  mutation run showed was missing — i.e. the fix shipped untested and was caught only by running
  mutation afterwards.

The mutation runs are doing real work and should stay. But a repair rate this high with a median
age of two hours is not a sign of good hygiene; it is a sign that things are being declared done
before they are exercised. Each of these commits carries a confident message saying what was
achieved. In three cases the next commit contradicts it.

---

## O3 — The single-defect-class story is about three-quarters true, and the missing quarter is not being hunted. *(measured against the full list)*

The claim, stated absolutely in `086fe86`, `BACKLOG.md:272` and `docs/observations/README.md:11`:
*every instrument built to say "this is fine" reported success when it had not looked.*

Tested against all 22 repairs, it fits roughly **17**, counting `eec9572`'s six sub-defects
separately. It is a real pattern, not a story imposed afterwards. The evidence is strong: three
independent reviewers opened on the same defect (`249a33a`), and the same shape recurs in the
bin's repo (`3cba5ac`: "`make check` said … all describe the same bin while four categories of
board-specific fact had rotted").

But about a quarter of the repairs are a **different class that the §4d table does not name at
all: the instrument that cries wolf.**

| commit | what it actually was |
| --- | --- |
| `ce71b27` | two I²C devices sharing SDA/SCL reported as a collision — "a stranger's first design came back with two errors" for the commonest wiring pattern in the domain |
| `7bbfa6b` | first version reported four JST connectors and a radial capacitor as unbuildable |
| `b7afbff` | geometry-only cross-plug rule: "twenty findings for one real hazard, which is how a check gets switched off" |
| `d13fc43` | a plugin test that "reports a correct change as a defect" |
| `c62a8dc` | `check_trace_currents` abandoned the whole check when nothing was routed |

Two more fit neither class: `d360f05` (mode 0644 — the tool cannot run *at all*, loudly) and
`65afadb` (missing manifest field).

Why this matters: the false-negative class is being hunted systematically (mutation runs, the
"a test must run the thing" rule, N4). The false-positive class has bitten at least five times,
the commit messages each recognise it in isolation ("which is how a check gets switched off"), and
it has **no rule, no checklist entry and no backlog item**. A plugin whose thesis is "deterministic
checks are the product" dies faster from noise than from silence, because noise is what makes
someone stop running it.

---

## O4 — Promises in docs that the code does not keep. *(measured — each was run or read)*

| claim | where | what is true |
| --- | --- | --- |
| "Every one runs standalone, takes `--json`" | `README.md:56` | **5 of 15 scripts do not.** `check_design.py` has no `argparse` at all — `./scripts/check_design.py --help` prints `no design at --help`. Also `check_bom.py`, `boards.py`, `emit_board.py`, `init_project.py`. `55d2368` ("The agent door… an agent cannot parse prose") built this for two scripts and skipped the flagship. |
| "Runs all seven deterministic checks" | `README.md:49`, and `skills/spark-review/SKILL.md:3` says "Runs every deterministic check" | **6 of 7** on the reference project — `pin-capability` is `[--]` not asked, because no `*.design.json` exists there. §4d is honest about this ("6 of 7"); the README and the skill description are not. |
| "265 of them" | `README.md:152` | 298. One day stale. |
| "216 tests, 6 skills, 14 scripts" | `BACKLOG.md:89` (§4 "Done", subtitled *Evidence, not assertion*) | Contradicted by `BACKLOG.md:256` (§4d) in the same file: 298 tests, 4 skills, 15 scripts. §4's own table at `:104` still says `check_all.py — six checks`; there are seven. |
| "a verification gate that refuses to emit a board with unverified part pins" | `.claude-plugin/plugin.json` description — the marketplace pitch | No such gate exists. `emit_board.py` refuses only on a missing `body_mm` (`:351`). `47a04c0` deleted `spark-verify` and noted its load-bearing idea "was enforced by no code"; it is still enforced by no code, now as skill prose. |
| the fab gate | `skills/spark-review/SKILL.md:175-176` tells the model to run `boards.py --validate --for-fab` and `parts.py --unverified` | `SKILL.md:4`'s `allowed-tools` grants only `findings.py` and `check_all.py`. The two commands that implement the gate fall outside the grant and will prompt — the exact failure `d360f05` described for the mode bits. In an unattended run that is a stop. |
| "the spark plugin (v0.4.0)" | `smartbin-local/CLAUDE.md:148` | 0.6.0. |
| "`~/Development/spark` is a git repo now, at v0.5.0, with no remote" — listed as blocked on Petr | `smartbin-local/STATUS.md` item 8 | `git remote -v` → `origin https://github.com/xmejkal/spark.git`, nothing unpushed. §4d (`086fe86`, 10:51) says "Everything pushed"; `b4a77f7` (10:52, **one minute later**) still lists it as waiting on Petr. Two handover documents written a minute apart disagree. |

Pattern: the claims that are *checked by a script* are accurate. The claims that live in prose —
README, skill descriptions, the marketplace pitch, §4's summary line — go stale within hours and
nothing compares them to anything. This is the project's own central thesis pointed at its own
documentation, and it has not been applied there.

---

## O5 — The findings store: 1,307 lines, the most-rewritten file in the repo, 0 resolved findings, 0 measurements, 45% of its contents about a board that no longer exists. *(measured)*

`scripts/findings.py` + `tests/test_findings.py` are 1,307 insertions / 190 deletions — the
largest and by some distance the *most rewritten* thing in the repo. It received five separate
repair passes (`312b541`, `010ba78`, `45b5c2d`, `55d2368`, `61e4ffc`) plus `47b4e29`.

The live store, `smartbin-local/.spark/findings.json`, last written **2026-09-24 12:09** — 47
commits ago:

```text
20 findings: blocked 11, open 8, rejected 1, resolved 0
measurements: 0
```

`10eea53` states this and is right. What it does not state is the second half, which I measured by
running the tool:

```console
$ cd ~/Development/smartbin-local && ~/Development/spark/scripts/findings.py validate
...
9 would go stale. Re-run with --apply.
```

**Nine of twenty findings cite design elements that no longer exist** — `net:VBAT`, `comp:XIAO`,
`port:XIAO.TOF_INT`, `comp:LipoBattery`, "CurrentShunt is 0.33R" (it is 0.1 R now). The board
changed from the XIAO to the FireBeetle on 09-24 and the store was never revalidated. The one
operation that would retire them is the one `61e4ffc` had to guard because it destroys work.

Meanwhile the six fab-blocking defects found by the adversarial re-check at ~22:30 on 09-24 were
written into `STATUS.md` prose, not into the store. **The author does not use the store.** The
eleven `blocked` findings rest on eleven named measurements, of which zero have been recorded —
including `mp3-idle-current`, which `312b541` was written about and `bench_sim.py` was built to
demonstrate.

This is the strongest single piece of evidence for the project's own conclusion, and it is
stronger than the conclusion states: the reviewer half is not merely *unproven*, its durable
artefact is **unused by the one person with access to it**, and has been for two days.

---

## O6 — Effort does follow the stated belief. The correction to that belief does not. *(measured)*

`2aad767` (09-24 19:41) concluded from one eval that reviewer work should stop. `249a33a` (20:04,
**23 minutes later**) retracted the reasoning — "§4b drew its conclusion from one arm of one run…
The reviewers are unfrozen" — and that retraction survives today at `BACKLOG.md:160`:
*"The reviewers are **not** frozen — nothing measured says they should be."*

Churn split at 19:41:

| | before 19:41 | after 19:41 |
| --- | --- | --- |
| `findings.py` | 772 ins | **23 ins** |
| `tests/test_findings.py` | 446 ins | 66 ins |
| `evals/*` | ~780 ins | **0 ins** |
| top of the "after" list | — | `check_all` 258, `init_project` 217, `check_footprints` 183, `check_firmware` 180, BACKLOG 318 |

So the commit history **confirms** the belief that the deterministic checks carry the product —
about 3:1 by lines over the whole repo, and near-total after the pivot. It does not contradict it.

What it contradicts is the *retraction*. The document says the reviewers are unfrozen; the
behaviour froze them 23 minutes before the document said so, and they have stayed frozen for 33
commits. One of those two statements should be withdrawn. Right now a reader of `BACKLOG.md` gets
§4b's "not frozen" and a Now list with nothing about reviewers in it, and has to guess.

---

## O7 — What is being avoided. *(measured)*

**N3, rebuilding the evals.** Named in `2aad767` ("evals should stop grading review quality"), in
§4b ("The evals need rebuilding before they are cited again"), and as `N3` in the Now list.
Measured state today: all four cases are still `schema_version: "1.0"`, no `context.add_dirs`, no
`tool_used` graders, and two are still `runs: 1` — every specific thing N3 asks for is absent. The
last eval run in `evals/results/` is `2026-09-24T17-16`. **47 of 57 commits landed after the last
eval run.** The project's own validation ladder has a rung-3 that has not been climbed since
two-thirds of the code was written.

**N4, auditing the other leaf checks.** Created on 09-25 and, as O1 shows, it is not a
housekeeping item — it is hiding a live instance of the defect the whole two days were spent on.

**Real placement in `emit_board`.** §5/S5: "*Remaining, and it is a design activity rather than a
gap.*" That sentence is doing work. The generator emits a column layout and says so honestly,
which is good; calling the remainder "a design activity" moves it off the list without deciding
anything.

**Plugin prose length.** In Debt since `4067b4f`. ~1,100 lines then, more now.

**Hardware.** `README.md`: "Nothing here has been validated on hardware by its author." Every
number in both repos that matters is still unmeasured.

The common shape: the avoided items are all ones whose *output is a number that could be
disappointing*. The eval rebuild would produce a delta that might be zero. N4 would produce a
count of rules that have never fired. Hardware would produce a motor current that invalidates the
driver. The work that gets done instead — new checks, new parts, new libraries — produces
artefacts whose success is self-evident on inspection. That is an inference, but the sorting is
consistent across all four.

---

## O8 — How the human is used: four questions parked for two days, three of them parked wrongly. *(measured)*

`smartbin-local/STATUS.md` has carried a **"Waiting on Petr (everything else is blocked behind
these)"** list since the first version at `1e2173e`, 2026-09-23 12:33. Items 1–4 — button height,
bin connector pitch, a photo of the VL6180X breakout, motor current — are **unchanged, verbatim,
in today's version**. Two days, no answers, and the list is described as blocking everything.

Escalations that worked, and they are the best work in the window:

- **The audio module's identity.** `2e14bb6` (09-24 22:43) "Nobody has checked which MP3 module
  this actually is" → `b4a77f7` (09-25 10:52) "Petr has chosen the I2S route". One question,
  correctly framed with a five-second test ("does it have a memory-card slot?"), produced a
  decision that removes four of the six fab-blocking defects. That is the highest-value thing
  either repo did in two days, and it cost one paragraph.
- **The plugin's name**, item 5 of the original list, "Asked several times; still unanswered" —
  eventually resolved; the plugin exists and is published.

Escalations that should not have been made — and the author caught this themselves, which is to
their credit:

- `3a43821`: "I said six open questions all needed an instrument. That was wrong for at least two
  of them." `db4a7e4`: "The library's open questions are down from six to three, and **none of the
  three closed needed an instrument** — two came out of Pololu's schematic and one out of a
  photograph." `fafbd47` then separated "needs a meter" from "needs a download", because
  "conflating the two makes a downloadable answer look like a bench trip."

**Three of six questions parked on the human were answerable from published documents.** Nobody
had tried. The sixth item still on the list, the MP3 module's idle current, is described as "five
minutes with a meter, module in your drawer" — and became moot when the I2S decision landed.

Decisions taken unilaterally that were large enough to warrant a sentence of warning first:
deleting two skills and changing the public command surface (`47a04c0`), declaring a line of work
dead on one eval arm and writing it into the backlog as settled (`2aad767`, reversed 23 minutes
later), and committing with `--no-verify` against a red gate (`b4a77f7` — correctly reasoned and
stated, so this one is fine).

Net assessment: the human is **under-used for decisions and over-used for lookups**. The one
genuine decision escalated in two days changed the project's direction inside twelve hours. Four
measurement requests have sat unanswered for two days and are blocking nothing that could not be
worked around, because the design changed underneath three of them anyway (`net:VBAT` is gone, the
shunt changed, the battery pads are gone).

---

## O9 — Small things, offered without evidence of harm

- `docs/audit-2026-09-24/` (581 lines, three reports, ~60 findings) has no index of which findings
  were reproduced, which were rejected and which were never looked at. §4c promotes a verified
  subset; the rest is a pile. `10eea53` built exactly the right mechanism for this one directory
  away and did not apply it backwards to the audit that motivated it.
- `check_all.py` prints `[ok  ] physics` with a `needs-measurement` note attached. Given O1, "ok"
  is currently the wrong word for that check specifically.
- `.gitignore` contains `evals/results/`, so the seven eval runs that §4b's table is built from
  are **not under version control** and exist only on this machine. The one piece of evidence the
  roadmap's central argument was corrected against is unbacked-up and unreviewable by anyone else.

---

## What I would tell the author

### Stop

1. **Stop writing the commit message before the mutation run.** Three commits in this window were
   contradicted by the very next commit, one of them 33 seconds later, and each of the three
   asserted completeness in prose. The mutation runs are catching what the tests miss — run them
   *before* the message claims the class is closed, not after. `086fe86`'s "Ten places, each now
   with a test that fails without it" was written while an eleventh was live in `check_physics`.

2. **Stop letting prose make claims that no script checks.** Five of the seven stale claims in O4
   are in README/SKILL frontmatter/plugin.json. This project's entire thesis is that a written
   rule nothing compares to the artefact is not a rule. A twenty-line test asserting that
   `README.md`'s test count, the `CHECKS` length, the script count and `plugin.json`'s version
   match reality would have caught six of them, and it belongs in the suite alongside the
   coverage guard that already refuses an unwired check.

3. **Stop escalating to Petr anything you have not first tried to answer from a document.** Three
   of six "needs an instrument" questions were downloads. You found that yourself and wrote
   `fafbd47` about it — now make it a precondition: no item enters "Waiting on Petr" until the
   vendor's file server, the chip's datasheet and the product photographs have been checked and
   the attempt recorded.

### Keep

1. **Keep the adversarial re-checks and the outside reviewers.** Every serious defect in both
   repos came from one — the three-reviewer audit, the first-time-user run, the nine-finding
   re-check, the cold rebuild. `b32422a` makes this standing practice, which is the right
   response. The measured hit rate justifies the cost.

2. **Keep the four-outcome discipline, and push it down to the leaves.** `could-not-run` vs `ok`
   is the best idea in this plugin and it is what makes O1 a bug report rather than an opinion.
   `b14dffb` took it one level down into `check_footprints` and it immediately found 14 unread
   holes. N4 is the same move again; do it before the next new check.

3. **Keep escalating real decisions the way you escalated the audio module.** One paragraph, three
   candidates in a table, a five-second physical test, and the consequence of each branch spelled
   out. It got an answer in twelve hours and removed four fab-blocking defects. Nothing else in
   two days had that return.

---

*Measured with: `python3 -m unittest discover -s tests -t tests` (298, OK), `./scripts/check_all.py
--project ~/Development/smartbin-local` (exit 1, 6 of 7), `./scripts/findings.py validate` in the
bin repo (9 would go stale), `./scripts/check_physics.py <circuit> --rules <rules>`, and the
`footprint_of` reproducer in O1. Classification in O2 and the defect ages in O2/O3 are my
judgement from commit messages, not machine-derived — treat those two tables as arguable and the
rest as reproducible.*
