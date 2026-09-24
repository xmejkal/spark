# Is `spark` usable by an unattended agent? Tested, not read.

**Verdict: the claim does not hold today.** Not because the design is wrong — the design is unusually good — but because the two pieces an unattended caller depends on most, `check_all.py` and the `spark-review` skill's own documented command, both report a clean board on a project where they checked almost nothing. I reproduced this against the author's own reference project. The scripts are individually strong; the *agent door* into them is the weakest part of the plugin.

Everything below was run, not inferred.

---

## The headline: the documented review command returns "clean" while checking a third of what it claims

I ran the command literally as `skills/spark-review/SKILL.md:31-37` writes it, in `/Users/petr/Development/smartbin-local`:

```
check_all.py --circuit dist/board/circuit.json --rules .spark/rules.json \
             --boards boards/*.json --package board-gerbers.zip
```

Exit **0**. Every line `ok`. What actually happened, of 7 checks:

| check | reported | reality |
|---|---|---|
| vendor-truth | `ok` | **checked nothing** — see below |
| buildability | `ok` | genuinely ran |
| the-order | `ok` | genuinely ran |
| physics | `ok` | genuinely ran |
| rules-vs-netlist | `ok` | genuinely ran |
| firmware-vs-board | `skipped` | the skill's command never passes `--firmware`/`--board-file` |
| pin-capability | `skipped` | never passed `--design` — and **it is broken anyway** |

### 1. `vendor-truth` prints a tick for a check that could not look

`scripts/check_all.py:121-133`:

```python
if result["status"] == "could-not-run":
    unchecked.append(...)          # <- goes into "unmeasured"
else:
    problems += ...
return {"status": PROBLEMS if problems else OK, ...}
```

A board that could not be checked never reaches `problems`, so the check returns **`ok`**. On the reference project `boards/` holds only `active.json` — a *selection* file, not a definition — so `boards/*.json` hands it a file with no `vendor.arduino_variant`, it returns `could-not-run`, and `check_all` renders `[ok  ]` with a `?` note.

This is precisely the failure the plugin exists to prevent, inside the aggregator whose docstring is a 15-line essay about it, on the check whose own docstring (`scripts/check_vendor_pins.py:24-27`) says *"A verification tool that silently degrades to 'no news is good news' ... is worse than no tool, because it still prints a tick."*

Compounding it: `unmeasured` now carries two incompatible meanings — physics uses it for *a rail nobody measured* (a real property of the board), vendor-truth uses it for *a check that did not run*. A caller cannot distinguish them from the field.

### 2. `pin-capability` — the plugin's flagship — has never worked through `check_all.py`

`scripts/check_all.py:86` calls `check_design.check(...)`. That function does not exist; `scripts/check_design.py:224` exports `run(design, board)`. It also passes a *path string* where a parsed dict is expected, expects a dict back where a list is returned, and never calls `resolve_board()`. Three independent breaks.

Result, verified with a valid design file:

```json
{"check": "pin-capability", "status": "could-not-run",
 "reason": "AttributeError: module 'check_design' has no attribute 'check'"}
```

`Check.run`'s broad `except Exception` (`check_all.py:73`) converts the bug into `could-not-run` — a status that reads to an agent as *environmental*, not *this plugin is broken*. An agent would retry or report a bad environment; it would never conclude there's a defect.

**The 216 tests pass.** `tests/test_check_all.py:110-127` is the test written specifically to catch "a script nobody invokes" — and it asserts that the *string* `load("check_design")` appears in the source. It verifies the check is named, not that it runs. No test in the suite ever passes a valid `design` input to `check_all`.

This is worth dwelling on: the plugin's rung-1 rule is *"Every check must have a design that violates it."* The runner is exempt from its own rule, and that is exactly where the defect is.

---

## 1. Can an agent drive the loop unattended?

The sequence a machine must execute, and where it stops:

| # | step | status |
|---|---|---|
| 1 | bootstrap `.spark/` | **tooling gap** |
| 2 | write `.spark/rules.json`, `.spark/project.json` | **tooling gap** |
| 3 | `parts.py --signals` → `assign_pins.py` | **works well** |
| 4 | `emit_board.py` → `board.tsx` | **tooling gap — output does not build** |
| 5 | `tsci build` | works (external) |
| 6 | `check_all.py` | **broken as above** |
| 7 | checks → findings store | **tooling gap — no bridge exists** |
| 8 | reviewer agents → `findings.py append` | works, human-shaped |
| 9 | `findings.py next` | **works, but always returns something unactionable** |
| 10 | decide the finding | *legitimate* human gate |
| 11 | change the design | *legitimate* human gate |

**Legitimate human gates** (these are right, keep them): taking a measurement with an instrument; `accepted`/`rejected` on a finding; signing off before fab; real PCB placement. The plugin is admirably clear about all four.

**Tooling gaps** (these are not decisions, they're missing work):

- **No bootstrap.** `scripts/findings.py:138` tells the caller to *"Run `spark init`"*. **There is no `spark init`** — no `commands/` directory, no such script, the string appears exactly once in the repo, in that error message. An agent that follows the remedy fails.
- **`rules.json` and `project.json` are undocumented inputs with no schema and no generator.** They are mentioned in exactly one place each — as a CLI argument at `spark-review/SKILL.md:35` and a phrase at `:67`. Two of six checks (`physics`, `rules-vs-netlist`) and all five reviewer agents require them. The one that exists in the reference project is clearly hand-written prose-in-JSON. An agent starting fresh cannot produce these.
- **`assign_pins.py` and `emit_board.py` refuse to run outside an existing project** even when `requirements.json` names a board from the plugin's own library. Verified: `could not load the board: no project here: nothing up from ... holds boards/active.json or .spark/`, exit 2. Honest error, right exit code — but combined with the missing `spark init`, use case B cannot start.
- **`emit_board.py` produces a file that does not build.** `scripts/emit_board.py:125` unconditionally emits `import { X } from "./X"` where `X` is `physical.footprint_export`. **The plugin ships zero `.tsx` files.** I ran it end to end:

  ```
  error: Cannot find module './XiaoRealFootprint' from '.../board.tsx'
  Fatal error [circuit_generation_failed]
  ```

  `emit_board.py` never checks the file exists, and exits **0**. `BACKLOG.md` S5 claims it *"produces a `board.tsx` that `tsci build` compiles, that routes, and that passes the buildability check out of the box."* That was true in a project that already contained a hand-written footprint module — `boards/README.md:64` even instructs a *human* to supply it. It is not true of the shipped library.
- **`emit_board.py` does not refuse, it whispers.** BACKLOG: *"It refuses usefully too: ... it says that instead of emitting a file that silently fails to route."* It does not refuse. It prints `note: nothing sources net.MOTOR6V ... the board will not route` **to stderr** and exits **0**, with no `--json`. An agent doing `emit_board.py req.json > board.tsx` and checking the exit code sees success and proceeds to a build it has been told will fail.
- **Nothing converts a check result into a finding.** Grepped: only `findings.py` and `check_footprints.py` mention `dimension`/`anchors`, and `check_footprints` doesn't emit store-shaped records. `check_all` returns prose strings; the store needs `{dimension, anchors, what, consequence, severity}` with anchors validated against `circuit.json`. **Bridging them requires an LLM to invent four fields from a sentence** — in a plugin whose stated conclusion is that the LLM half adds nothing. This is the single most consequential structural gap for autonomy.

---

## 2. Are the machine-readable outputs good enough to act on?

**Consistency: no.** Four different envelopes, verified by running each:

| tool | shape |
|---|---|
| `check_physics.py` | `{tool, status, design, findings[]}` |
| `check_footprints.py` | `{tool, status, findings[]}` |
| `compare_design.py` | `{tool, status, design, checked, problems[]}` ← `problems`, not `findings` |
| `check_vendor_pins.py` | **a bare JSON list** — no envelope, no top-level status |
| `check_all.py` | `{tool, results[]}` — **no top-level `status`**, the one tool explicitly built for a non-human caller |
| `findings.py` | `{tool, status, rendered, ...}` — the best of them |
| `check_bom.py`, `check_design.py`, `emit_board.py`, `boards.py` | **no `--json` at all** |

`parts.py` is worse than missing: `--json` is honoured for `--unverified`, **silently ignored** for `--list`, `--show` and `--validate`, and `--signals` prints JSON whether you ask or not (`scripts/parts.py`, `main`). Three different meanings for one flag.

**`--json` is not honoured on error paths.** `check_footprints.py` main prints `no built design at ... — build it first` as prose and returns 2, even with `--json`. Same in `check_firmware.py` (verified: exit 2, prose). An agent doing `json.loads(stdout)` crashes precisely when something went wrong.

**Can a caller tell the four outcomes apart? By exit code, no.** Measured:

| situation | tool | exit | means |
|---|---|---|---|
| missing board file | `check_vendor_pins.py` | **1** + Python traceback | **1 = `EXIT_MISMATCH`** |
| missing design | `check_design.py` | **1** | 1 = problems |
| `--json` (unsupported flag) | `check_design.py` | **1** | 1 = problems |
| bad flag | argparse tools | **2** | 2 = `EXIT_COULD_NOT_RUN` |

`check_vendor_pins.check_board` does `json.loads(path.read_text())` with no guard, so an unreadable board file escapes as an uncaught `FileNotFoundError` → exit 1 → **"your board disagrees with its vendor"**, the most alarming result the tool can give, for a file that simply isn't there. `check_design.py`'s `main` raises `SystemExit(usage)` on any argv mismatch → exit 1 → indistinguishable from a bad board. The `spark-check` skill documents *"Exit 0 means sound, 1 means problems"*; that contract is wrong in both directions.

(Inside `check_all` these degrade correctly, because `Check.run` wraps them. Standalone — which is how the `spark-check` skill invokes them — they do not.)

**Is there enough in a finding to know what to DO?** Individually, yes and it's good: `check_physics` returns `{rule, subject, detail, severity, fix}` with a genuinely actionable `fix`. **Through `check_all`, no.** It flattens every finding to a string — `"%s: %s" % (f.subject, f.detail)` (`check_all.py:109, 118`) — discarding `fix`, `severity` and `rule`. The aggregator built for agents is the one that throws away the machine-readable structure its own checks produce.

---

## 3. State and memory

**This is the strongest part of the plugin, and the locking is genuinely correct.** I tried hard to break it: 12 concurrent read-modify-write processes (6 `append` + 6 `status`) against one store, plus an 8-way concurrent append. **Zero lost writes, every worker reported its own result, the file stayed valid, no stray `.tmp`.** `fcntl.flock` around the full load→modify→save in `Store.locked()` (`findings.py:156-173`) plus `os.replace` in `save()` is the right design and it works. (I initially thought I'd found a lost-write bug; it was zsh not word-splitting my test variable. Retested properly — the store is fine.)

**Can an agent resume?** Yes for *what was decided*: `list --status <s>` and per-finding `decisions[]` with reason and date. Structural dedupe means re-running reviewers is safe and cheap.

**What resume is missing:**

- **`found_against` is always `null`.** `merge()` accepts it (`findings.py:212, 247`) but `_run` never passes it (`:502-503`). Every finding in the live store has `"found_against": null`. So an agent cannot tell whether a finding was raised against the current design or three revisions ago — the one field that would make resume-across-changes safe is inert.
- **`next` always hands back something an agent cannot do.** `PRIORITY = {BLOCKED: 0, ...}` (`findings.py:67`) ranks blocked first, by design, because for a human "clearing one is minutes of someone's time." The live store has **11 blocked of 20**, and `next` returns a finding blocked on `lid-stroke-time` — a number that only exists once someone puts a stopwatch on a motor. There is no `--actionable` and no way to ask for the next *unblocked* item. **An unattended loop calling `next` deadlocks on turn one, permanently.** The JSON does expose `waiting_on`, so an agent can *detect* the deadlock — it just has no next move.
- No `--store` isolation in practice: `spark-review/SKILL.md:44` writes the collected review to the hardcoded `/tmp/review.json`. Two reviews in parallel clobber each other, outside the flock that protects everything else.
- Dead code in the store: duplicate `_show`/`_measurement` definitions (lines 373/388 and 381/396, first pair unreachable), and `_circuit()` at `:367` references an undefined global `CIRCUIT` — a latent `NameError` nothing currently calls.

**Two agents at once:** safe for the store. Unsafe for `/tmp/review.json`. And `flock` has no timeout — a wedged process blocks every other caller silently and forever.

---

## 4. The skills as agent instructions

`agents/design-reviewer.md` is the best-written file here — tight, bounded output contract, an explicit "return an empty list" escape, and a genuinely sharp rule about not reading the project's own conclusions. One structural flaw: it is granted `Glob` and `WebSearch` while being told *"do not go looking for them."* The plugin's own doctrine (BACKLOG §1) says an agent earns its place through **restricted tools**; here the restriction is prompt-level, which is the weaker of the two mechanisms available and the one a model can talk itself out of.

Problems that would make two runs differ, or cost money:

- **`spark-review` step 2's command is incomplete** and produces the false-clean above. It never passes `--design`, `--firmware` or `--board-file`, so 2 of 7 checks are permanently `skipped` — in a skill whose entire premise is that `skipped` must not read as clean.
- **`--boards boards/*.json` is wrong for the reference project's own layout** — it globs the selection file. The fix is `boards.py --paths`, which exists and is what the Makefile uses (`smartbin-local/Makefile:41`).
- **Step 3 launches five Opus agents in one message** with no budget guard, no subset option, no ordering. That is the expensive instruction, and it is unconditional.
- **Step 3 says "the paths it may read" without saying how to determine them.** "The schematic, the board definition, the firmware config" — the agent must guess filenames. Non-deterministic across runs and across projects.
- **Step 4 says "collect every agent's JSON into one file"** — five JSON blobs returned as prose, merged by hand into one document. No tool does this; it is the least reliable step in the loop and it sits between the reviewers and the only durable state.
- **`spark-check/SKILL.md:74` points at `boards/README.md` "in the smart-bin project"** — a different repository. The plugin has its own `boards/README.md`. An agent following this reads the wrong repo or nothing.
- **`spark-design` step 5, "Fix and rebuild until clean"** — unbounded loop, no iteration cap, no definition of clean.
- **"Working a finding" is explicitly human-only**: *"You are in the conversation, so this is a conversation, not a subagent"* and *"Let the person decide."* That is a legitimate gate, but stated absolutely it means an unattended agent following this skill can never advance a single finding, even the ones that are pure arithmetic.

---

## 5. Failure and recovery

Good: `check_all`'s per-check `try/except` means one broken check never hides the others; `findings.py`'s `except SystemExit` (`:472-474`) turns every refusal into a structured `could-not-run` answer rather than a traceback — that pattern is right and should be copied to the other twelve scripts.

**The one way an agent can make things materially worse: `findings.py validate --apply`.**

Verified. Against an empty `[]` circuit — which is what a failed or partial `tsci build` can leave, and which `Store.circuit()` accepts because it only checks the file *exists* — it retired every live finding as `stale`. The exit codes are inverted for an autonomous caller:

| operation | status | **exit** |
|---|---|---|
| `validate` (safe preview) | `problems` | **1** |
| `validate --apply` (destructive) | `ok` | **0** |

An agent following "non-zero means stop" reads the safe preview as a failure and the mass-retirement as a clean pass. The only guard is that `--apply` must be typed; nothing verifies the circuit is current, non-empty, or the same board. The docstring at `:571-572` names this risk exactly and then relies on a single flag against it.

One piece of good news the author appears not to know: this **is** recoverable. `status <key> open --reason "..."` un-stales a finding (verified), and `validate --apply --json` returns the full `went_stale` key list. The docstring's *"with no way back"* is pessimistic. But nothing tells a caller that.

---

## 6. What is missing for full autonomy — and is S10 the right next step?

**S10 is the right *shape* and the wrong *next* item.** The author's gate — "only once 1–3 are trusted" — is correct, and the checks are not yet trustworthy: the one command an unattended loop would call returns a clean exit on a project where one check crashed, one lied, and two never ran. Building the loop on top of that ships the false-clean at scale.

Ordered by what actually blocks autonomy:

1. **Fix `check_all.py:86`** (`check_design.check` → `run`, parse the files, resolve the board) and **add the test that would have caught it** — `check_all.run({"design": <a design with a real defect>})` must return `problems`. The existing source-grep test cannot fail.
2. **Make `could-not-run` propagate through `check_all`.** A check that could not look must not report `ok`. Split `unmeasured` into `unmeasured` (a property of the board) and `unchecked` (a property of the run), and let the latter set the status.
3. **One envelope, enforced by a test.** `{tool, status, problems[], unchecked[], reason}` for every script, `--json` honoured on *every* path including errors, one documented exit-code contract, and `check_all` carrying a top-level `status`. Then fix `check_vendor_pins`'s unguarded `json.loads` and `check_design`'s usage-error-as-exit-1.
4. **Build the checks→findings bridge.** Each check emits store-shaped findings with anchors it can derive itself (it already knows the net and component names). This is the item that decides whether the autonomous story survives the eval result, because it is the one that removes the LLM from the load-bearing path.
5. **`spark init`.** Create `.spark/`, write a schema-checked `rules.json` and `project.json` template with every unknown explicitly `null`. Document both schemas. Two of six checks and all five reviewers depend on files with no schema anywhere.
6. **`emit_board.py`: emit or fetch the footprint module, or refuse.** Today it emits an unbuildable import and exits 0. Also make the "nothing sources this net" note a non-zero exit or a `--json` field.
7. **`findings.py next --actionable`**, so an unattended loop has a move when everything at the top is blocked on a human with a multimeter.
8. Then S10.

---

## On the eval, and the reprioritisation it drove

You asked me to factor this in. **I think the conclusion may be right, but the cited evidence does not support it — and the stronger evidence points the other way.**

Every result file, parsed:

| run | case | with | without | delta |
|---|---|---|---|---|
| 07:52 | deep-sleep-pins | [1,1,1] | [1,0] | **+0.50** |
| 09:19 | deep-sleep-pins | [1,1,1] | [1,1,1] | 0 |
| 09:19 | testing-without-hardware | [1,1,1] | [0,1,0] | **+0.67** |
| 09:27 | finds-unswitched-power | [0,0,0] | [0,0,0] | 0 |
| 09:30 | finds-unswitched-power | [1,1,1] | [1,1,0] | **+0.33** |
| 16:59 | finds-assembly-problems | [0,0,1] | [0] | **+0.33** |
| 17:16 | finds-assembly-problems | [1,1,0] | [1,1,1] | **−0.33** |

`BACKLOG.md` §4b cites **only the last row**, and describes it as *"the second eval to say the same thing."* The corpus says something different:

- **Five of six two-armed runs are ≥ 0.** Mean delta ≈ **+0.30**.
- **`testing-without-hardware` at +0.67 is the largest effect measured and is not mentioned in the backlog at all.**
- **The same case flipped +0.33 → −0.33 in 17 minutes**, n=3 per arm. With n=3, one run's difference *is* 0.33. The swing is at the resolution of the instrument.
- The 16:59 baseline that "scored perfect" is **n=1**. The 17:16 baseline is n=3.
- `finds-unswitched-power` scored all-zero in *both* arms at 09:27 and all-one at 09:30 — a total flip three minutes later, which means the harness itself was not stable in that window.

So: *"the model does not need help reviewing"* — the sentence that killed a line of work, froze the reviewers, and is the commit message on `2aad767` — rests on one arm of one run of one case, selected from a corpus trending the other way.

I want to be fair: **the strategic direction is probably still correct**, for reasons that have nothing to do with this eval. A script runs in a second, costs nothing, and cannot change its mind; the defect list in §4b showing what *only* a script found is a far better argument than any delta. But the argument as written is "the eval said so," and the eval did not say so. If the reviewers are going to stay frozen, freeze them on the cost-and-determinism argument, which is sound — not on a −0.33 that is noise.

And the deeper implication cuts the other way than the backlog assumes. **If the LLM half adds nothing, the autonomous story rests entirely on the scripts and the state — and the scripts' front door is the part that is broken.** The state layer genuinely holds up: structural identity, the anchor filter, `rejected` as a durable answer, provenance on every measurement, and a lock that survived everything I threw at it. That half is real engineering. The deterministic half is real too, script by script — `check_physics`, `check_footprints`, `check_bom`, `assign_pins` are all excellent, and `assign_pins --json` is the best machine interface in the repo. What does not yet exist is the *seam*: the one call that runs them honestly, the one shape they all answer in, and the pipe from what they find into what the project remembers.

**Solid:** the individual checks and their unit tests; the findings store's rules, identity model and locking; `assign_pins`; the measurement-provenance discipline; the honesty about what is a draft; `design-reviewer`'s prompt.

**Aspiration:** "one call for all of it"; "modules in, board out" producing something that builds; the three-outcomes guarantee (it is implemented in the runner and defeated by two of its own checks); and "every tool answers with data and a distinct exit code" — four tools have no `--json`, four envelopes disagree, and three distinct conditions all exit 1.
