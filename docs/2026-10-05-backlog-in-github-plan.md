# The backlog in GitHub (P102a) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (recommended here) or superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** spark's and the bin's open work lives in two public GitHub projects run Kanban, with WIP limits enforced at
push, and the Markdown backlog is frozen as the archive (P102a, taking in P70).

**Architecture:**
1. A W14 lens proposes what happens to each open item, and the PO confirms the table.
2. A one-off script, kept in this plan's git-ignored workspace and never shipped, turns the confirmed table into
   labels, issues, sub-issues and two projects with their fields. It runs as a dry run first, and for real only with
   the PO's yes.
3. One shipped check, `tools/check_backlog.py`, reads the spark project at push. It enforces *Needed by*, Slice and
   the WIP limits, and passes with a "skipped" line when offline.
4. The Markdown files are frozen and the working agreements rewritten, in the same commits as the things they
   describe.

**Tech Stack:** Python 3 standard library, `gh` (GitHub CLI, the PO's own login, `project` scope present), GitHub's
GraphQL API through `gh api graphql`, `unittest`, `tools/mutate.py`.

**Spec:** `docs/2026-10-05-backlog-in-github-design.md` (approved by the PO, 2026-10-05).

## Global Constraints

- **Branch `p102-tools-chore`, PR #4.** The PO merges.
- **Nothing is created on GitHub before the PO's yes to the dry run** (Task 3). Every issue and project is public.
- **No token is stored or written anywhere.** `gh` uses the PO's keyring login; no secret goes to GitHub (his rule).
- **The stages:** Idea, Discovery, Design, Ready, Build, Review, Done.
  - WIP limits: Discovery 1, Design 1, Ready 3, Build 1, Review 1.
  - At most 2 in flight across Discovery, Design, Build and Review.
- **Item facts live in the issue body,** under `### Needed by`, `### Value proven by`, `### Proof` and `### Archive`.
  This is the issue form's rendering, and the migration writes the same.
- **Labels:** `epic`, `story`, `task`, `chore`, `bug`.
- **Fields:** Status (the stages), Waiting on (the PO / hardware / outside), Waiting since (a date), Slice.
- **The suite stays offline.** `check_backlog`'s tests feed it data; only `main()` calls `gh`.
- **Mutation tables only for verdict code** (P72's cut): `tools/check_backlog.py` gets one; the docs and the one-off
  script do not.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`, and their numbers come only
  from output already shown (W13).
- **Shell rules:**
  - use `/usr/bin/grep`;
  - never name a zsh loop variable `path`;
  - write `${VAR}:x`, never `$VAR:x`, because zsh reads `:x` as a modifier.

## Review Focus

1. **A second run of the migration** must create nothing and change nothing. Test: Task 3, Step 6.
2. **The gate offline** (no network, or `gh` logged out) prints that the check was skipped and passes. Test: Task 4.
3. **An open item whose body was edited by hand** so that `### Needed by` is empty, or reads `_No response_`, is
   caught. Test: Task 4.
4. **A card dragged into Build while another is there** fails the next push, with a sentence naming both. Test: Task 4.
5. **An archive heading left unmarked after the freeze** fails the suite. Test: Task 5.

---

## File structure

| file | responsibility |
| --- | --- |
| `docs/2026-10-05-backlog-revalidation.md` (new) | the W14 lens's table and the PO's confirmation — the migration's only input |
| `.github/ISSUE_TEMPLATE/item.yml` (new) | the issue form: Needed by, Value proven by, Proof, Archive |
| `<workspace>/migrate.py`, `<workspace>/table.json` (git-ignored, not shipped) | the one-off migration and its machine-readable input |
| `tools/check_backlog.py` (new) | W14 and the WIP limits on the spark project, at push |
| `tools/check_commit.py` | calls `check_backlog` after the suite |
| `tests/test_check_backlog.py`, `tests/data/p102a-items.json` (new) | the check's tests; a recorded `gh project item-list` answer |
| `tests/mutations/p102a-check-backlog.json` (new) | the check's mutation table |
| `scrum/PRODUCT_BACKLOG.md`, `scrum/STORY_MAP.md`, `scrum/SPRINT.md` | frozen, mapped and closed as the spec's §7 and §9 say |
| `scrum/WORKING_AGREEMENTS.md`, `scrum/README.md` | W6, W11, W18 and W19, the ceremonies, and the Definition of Done's sweep moved to the epic |
| `tests/test_orphans.py` | the two Markdown-backlog checks become one archive check |

---

### Task 1: The revalidation table — the lens proposes, the PO confirms

**Files:** Create `docs/2026-10-05-backlog-revalidation.md`.

- [ ] **Step 1.** Dispatch one W14 lens (mid-tier model, read-only on the repo, no web). Its input:
  - `scrum/PRODUCT_BACKLOG.md`'s open items, those whose heading matches none of
    `DONE|ANSWERED|CLOSED|PARKED|MERGED|DELETED|SPLIT|~~` (35 on 2026-10-05);
  - `scrum/STORY_MAP.md`;
  - `git log`.

  It proposes for each item one of:
  - **keep:** a type label, a Slice, a parent epic or none, a repository (`spark`, or `bin` for B-items), a Status
    stage, and Waiting on with its date if any;
  - **close as done:** the commit that proves it;
  - **park:** what pulls it back;
  - **merge into:** the item it joins.

  Each proposal carries one line of reason. **Statuses must respect the limits:** at most 3 in Ready, 1 in Build, 2 in
  flight. Everything else that is kept waits in **Idea**, which serves as the backlog: recorded, not yet pulled into
  Discovery. Epics carry no limit; their stories do. P102 is kept as an epic. Its sub-items a–f are added as stories:
  P102a in Build, P102c in Ready, the rest in Idea. Their *Needed by* and *Value proven by* come from P102's entry and
  the spec.
- [ ] **Step 2.** The lens writes the table to `docs/2026-10-05-backlog-revalidation.md`, one row per item, with
  these columns:

  `| id | proposal | type | slice | parent | repo | status | waiting | reason | evidence |`

  Slice is one of these names (the story map's slices, plus two):
  - 1 Public
  - 1b From a vague idea
  - 2 First copper
  - 3 Firmware on a Mac
  - 4 v1 on two projects
  - 5 A real stranger
  - 6 Shared, not copied
  - 7 Perfboard to PCB
  - 8 A board you can order
  - 9 An enclosure
  - 10 The store
  - team tools
  - desk lane
- [ ] **Step 3.** Show the PO the table, grouped by proposal: closes first, then parks and merges, then keeps by
  slice. He confirms or changes it in one pass. His changes are written into the table, and a closing line records
  *"Confirmed by the PO, <date>"*.
- [ ] **Step 4.** Commit:
  `P102a: the revalidation table — the W14 lens's proposals, confirmed by the PO` (trailer).

---

### Task 2: The issue form

**Files:** Create `.github/ISSUE_TEMPLATE/item.yml`.

- [ ] **Step 1.** Write the form:

```yaml
name: Backlog item
description: An epic, story, task, chore or bug — with the design that needs it and the command that proves it.
body:
  - type: textarea
    id: needed-by
    attributes:
      label: Needed by
      description: The design, project or person that needs this, in their words where possible (W14 — pull, never push).
    validations:
      required: true
  - type: textarea
    id: value
    attributes:
      label: Value proven by
      description: What will be true when it is done, readable by the Product Owner.
    validations:
      required: true
  - type: textarea
    id: proof
    attributes:
      label: Proof
      description: The command that proves it (from P102d on). Leave empty until there is one.
      render: shell
  - type: input
    id: archive
    attributes:
      label: Archive
      description: For an item moved from scrum/PRODUCT_BACKLOG.md — its id there.
```

- [ ] **Step 2.** Commit:
  `P102a: the issue form — Needed by, Value proven by, Proof, Archive` (trailer).

---

### Task 3: The migration — dry run, the PO's yes, the real run, a second run that changes nothing

**Files (git-ignored, never committed):**
- `<workspace>/table.json`, written from Task 1's confirmed table;
- `<workspace>/migrate.py`;
- `<workspace>/dry-run.txt` and `<workspace>/real-run.txt`.

`<workspace>` is this plan's `.superpowers/sdd/2026-10-05-backlog-in-github-plan/`.

**Interfaces:**
- Produces `tests/data/p102a-items.json`, a recorded `gh project item-list` answer for spark's project, which Task 4
  consumes.
- Produces `<workspace>/issues.json`, a map from id to `{"repo", "number", "url"}`, which Task 5 consumes.

- [ ] **Step 1.** Write `table.json` from the confirmed table: one object per **kept** item.

```json
[{"id": "P102", "title": "The tools chore: …", "repo": "spark", "type": "epic", "parent": null,
  "status": "Build", "slice": "team tools", "waiting_on": null, "waiting_since": null}]
```

  `title` is the heading's text after `P102 — ` and before ` — **`, so it holds the name only.
- [ ] **Step 2.** Write `migrate.py`. Note `field-create --single-select-options` takes one comma-separated list,
  so no option name may contain a comma: the slice names above contain none, and the Waiting on options none either.

```python
#!/usr/bin/env python3
"""
P102a's one-off migration (docs/2026-10-05-backlog-in-github-plan.md, Task 3) — not shipped, run once.
    migrate.py table.json            # a dry run: reads GitHub, prints what it would do, writes nothing
    migrate.py table.json --real     # with the PO's yes: does it; a second run creates and changes nothing
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

OWNER = "xmejkal"
REPOS = {"spark": "xmejkal/spark", "bin": "xmejkal/sisuo-brain-transplant"}
TITLES = {"spark": "spark", "bin": "the bin"}
LABELS = {"epic": "5319e7", "story": "0e8a16", "task": "c5def5", "chore": "fbca04", "bug": "d73a4a"}
STAGES = ["Idea", "Discovery", "Design", "Ready", "Build", "Review", "Done"]
WAITING = ["the PO", "hardware", "outside"]
SLICES = ["1 Public", "1b From a vague idea", "2 First copper", "3 Firmware on a Mac", "4 v1 on two projects",
          "5 A real stranger", "6 Shared, not copied", "7 Perfboard to PCB", "8 A board you can order",
          "9 An enclosure", "10 The store", "team tools", "desk lane"]
BACKLOG = Path(__file__).resolve().parents[3] / "scrum" / "PRODUCT_BACKLOG.md"
REAL = "--real" in sys.argv


def gh(*args, write=False):
    """Run gh; a write in a dry run is printed, not run."""
    if write and not REAL:
        print("  would run: gh " + " ".join(args))
        return ""
    done = subprocess.run(["gh", *args], capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit("gh %s failed: %s" % (" ".join(args[:3]), done.stderr.strip()))
    return done.stdout


def sections():
    """{id: section text} of every heading in the backlog."""
    found = {}
    for section in re.split(r"\n(?=### )", BACKLOG.read_text()):
        if section.startswith("### "):
            found[section.split()[1]] = section
    return found


def labelled(section, label):
    """The paragraph after **<label>:**, up to the next bold label or blank line — or a dash."""
    match = re.search(r"\*\*%s:\*\*(.*?)(?=\n\*\*[A-Z]|\n\n|\Z)" % re.escape(label), section, re.S)
    return " ".join(match.group(1).split()) if match else "—"


def body(item, section):
    return ("### Needed by\n\n%s\n\n### Value proven by\n\n%s\n\n### Proof\n\n_No response_\n\n### Archive\n\n"
            "`scrum/PRODUCT_BACKLOG.md`, heading %s\n" % (labelled(section, "Needed by"),
                                                           labelled(section, "Value proven by"), item["id"]))


def ensure_labels(repo):
    have = {entry["name"] for entry in json.loads(gh("label", "list", "-R", repo, "--json", "name", "--limit", "100"))}
    for name, colour in LABELS.items():
        if name not in have:
            gh("label", "create", name, "-R", repo, "--color", colour, write=True)


def existing(repo):
    """{id: issue} for issues whose title starts with an id and ' — '."""
    issues = json.loads(gh("issue", "list", "-R", repo, "--state", "all", "--limit", "500", "--json", "number,title,url,id"))
    return {issue["title"].split(" — ")[0]: issue for issue in issues if " — " in issue["title"]}


def ensure_issues(table, found):
    made = {}
    for item in table:
        repo = REPOS[item["repo"]]
        have = existing(repo)
        if item["id"] in have:
            made[item["id"]] = dict(have[item["id"]], repo=repo)
            continue
        note = Path(tempfile.mkdtemp()) / "body.md"
        note.write_text(body(item, found.get(item["id"], "")))
        out = gh("issue", "create", "-R", repo, "--title", "%s — %s" % (item["id"], item["title"]),
                 "--body-file", str(note), "--label", item["type"], write=True)
        print("  issue %s %s" % (item["id"], out.strip() or "(dry run)"))
        if REAL:
            made[item["id"]] = dict(existing(repo)[item["id"]], repo=repo)
    return made


def ensure_sub_issues(table, made):
    for item in table:
        parent, child = made.get(item["parent"] or ""), made.get(item["id"])
        if not (parent and child):
            if item["parent"]:
                print("  would link %s under %s" % (item["id"], item["parent"]))
            continue
        linked = json.loads(gh("api", "graphql", "-f", "query=query($id:ID!){node(id:$id){... on Issue{subIssues(first:100){nodes{id}}}}}",
                               "-f", "id=%s" % parent["id"]))["data"]["node"]["subIssues"]["nodes"]
        if child["id"] not in {node["id"] for node in linked}:
            gh("api", "graphql", "-f", "query=mutation($p:ID!,$c:ID!){addSubIssue(input:{issueId:$p,subIssueId:$c}){issue{number}}}",
               "-f", "p=%s" % parent["id"], "-f", "c=%s" % child["id"], write=True)


def ensure_project(key):
    """(number, node id) of the public project with this title, made if missing; None in a dry run that would make it."""
    projects = json.loads(gh("project", "list", "--owner", OWNER, "--format", "json"))["projects"]
    found = next((p for p in projects if p["title"] == TITLES[key]), None)
    if found is None:
        gh("project", "create", "--owner", OWNER, "--title", TITLES[key], write=True)
        if not REAL:
            return None
        projects = json.loads(gh("project", "list", "--owner", OWNER, "--format", "json"))["projects"]
        found = next(p for p in projects if p["title"] == TITLES[key])
    number = str(found["number"])
    gh("project", "link", number, "--owner", OWNER, "--repo", REPOS[key], write=True)
    gh("project", "edit", number, "--owner", OWNER, "--visibility", "PUBLIC", write=True)
    return number, found["id"]


def ensure_fields(number, project_id):
    fields = {f["name"]: f for f in json.loads(gh("project", "field-list", number, "--owner", OWNER, "--format", "json"))["fields"]}
    status = fields["Status"]
    if [o["name"] for o in status.get("options", [])] != STAGES:
        options = ",".join('{name:"%s",color:GRAY,description:""}' % stage for stage in STAGES)
        gh("api", "graphql", "-f", "query=mutation{updateProjectV2Field(input:{fieldId:\"%s\",singleSelectOptions:[%s]}){projectV2Field{... on ProjectV2SingleSelectField{name}}}}"
           % (status["id"], options), write=True)
    for name, kind, options in (("Slice", "SINGLE_SELECT", SLICES), ("Waiting on", "SINGLE_SELECT", WAITING),
                                ("Waiting since", "DATE", None)):
        if name not in fields:
            gh("project", "field-create", number, "--owner", OWNER, "--name", name, "--data-type", kind,
               *(["--single-select-options", ",".join(options)] if options else []), write=True)
    return {f["name"]: f for f in json.loads(gh("project", "field-list", number, "--owner", OWNER, "--format", "json"))["fields"]}


def set_fields(number, project_id, fields, item, url):
    added = gh("project", "item-add", number, "--owner", OWNER, "--url", url, "--format", "json", write=True)
    if not REAL:
        return
    item_id = json.loads(added)["id"]
    for name, value in (("Status", item["status"]), ("Slice", item["slice"]), ("Waiting on", item["waiting_on"])):
        if value:
            option = next(o["id"] for o in fields[name]["options"] if o["name"] == value)
            gh("project", "item-edit", "--id", item_id, "--project-id", project_id, "--field-id", fields[name]["id"],
               "--single-select-option-id", option, write=True)
    if item["waiting_since"]:
        gh("project", "item-edit", "--id", item_id, "--project-id", project_id, "--field-id",
           fields["Waiting since"]["id"], "--date", item["waiting_since"], write=True)


def main():
    table = json.loads(Path(sys.argv[1]).read_text())
    found = sections()
    for key in {item["repo"] for item in table}:
        ensure_labels(REPOS[key])
    made = ensure_issues(table, found)
    ensure_sub_issues(table, made)
    for key in sorted({item["repo"] for item in table}):
        project = ensure_project(key)
        if project is None:
            print("  would add %d items to the %s project and set their fields" % (sum(i["repo"] == key for i in table), key))
            continue
        fields = ensure_fields(*project)
        for item in (i for i in table if i["repo"] == key and i["id"] in made):
            set_fields(project[0], project[1], fields, item, made[item["id"]]["url"])
    out = Path(__file__).with_name("issues.json")
    out.write_text(json.dumps({k: {"repo": v["repo"], "number": v["number"], "url": v["url"]} for k, v in made.items()}, indent=1))
    print("done" if REAL else "dry run done — nothing was written")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Dry run.** Run `python3 <workspace>/migrate.py <workspace>/table.json > <workspace>/dry-run.txt 2>&1`,
  then read it. Expected: a `would run: gh label create …` line per missing label, one per new issue, the project
  creates, and the closing line `dry run done — nothing was written`. A `gh … failed` line is a defect in the script:
  fix it and run again.
- [ ] **Step 4: The PO's yes.** Show him the counts from `dry-run.txt` and three sample issue bodies. Nothing runs for
  real without his explicit yes.
- [ ] **Step 5: Real run.** Run `python3 <workspace>/migrate.py <workspace>/table.json --real > <workspace>/real-run.txt 2>&1`.
  Expected: `done`, and `<workspace>/issues.json` written.
  - If `updateProjectV2Field` refuses `singleSelectOptions`, rename the Status options by hand in the project's
    field settings, a one-minute browser step (by the PO, or by Claude with his go). Record it as a ruling.
- [ ] **Step 6: Second run** (Review Focus 1). Run the same command again. Expected: no `issue … https://` line and no
  `would run`, ending in `done`. Then:
  - `gh issue list -R xmejkal/spark --state open --json number --jq length` matches the table's spark count;
  - `gh project item-list <n> --owner xmejkal --format json --limit 500 > tests/data/p102a-items.json` records spark's
    answer for Task 4.
- [ ] **Step 7.** Commit `tests/data/p102a-items.json` alone:
  `P102a: the spark project's items, recorded for check_backlog's test` (trailer). The data is public already.

---

### Task 4: `tools/check_backlog.py` — W14 and the WIP limits at push

**Files:**
- Create `tools/check_backlog.py`, `tests/test_check_backlog.py` and `tests/mutations/p102a-check-backlog.json`.
- Modify `tools/check_commit.py` (`main`).

**Interfaces:**
- Produces `check_backlog.problems(items) -> [sentence]`, a pure function.
- Produces `check_backlog.fetch() -> items | None`, where None means it could not look.
- Produces `check_backlog.main() -> exit code`.

- [ ] **Step 0.** Read `tests/data/p102a-items.json` and note the keys `gh` used: the Status key, the Slice key, the
  labels, and where the body sits (`content.body`). The code below assumes `item["status"]`, `item["slice"]`,
  `item["labels"]` and `item["content"]["body"]`. If the recording differs, use the recorded keys everywhere below
  and record a ruling.
- [ ] **Step 1: Failing tests** — `tests/test_check_backlog.py`:

```python
"""P102a: the spark project's open items name what needs them, sit on a slice, and respect the WIP limits."""

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import check_backlog  # noqa: E402

BODY = "### Needed by\n\n%s\n\n### Value proven by\n\nx\n\n### Proof\n\n_No response_\n"


def item(number, status="Ready", slice_="10 The store", needed="the PO's walking skeleton", labels=("story",)):
    return {"status": status, "slice": slice_, "labels": list(labels),
            "content": {"number": number, "title": "P%d — x" % number, "body": BODY % needed}}


class TheBacklogCheckTest(unittest.TestCase):
    def test_a_well_formed_board_has_no_problems(self):
        self.assertEqual(check_backlog.problems([item(1, "Build"), item(2, "Review"), item(3), item(4, "Done")]), [])

    def test_an_item_with_no_needed_by_is_named(self):
        for empty in ("", "_No response_", "   "):
            with self.subTest(empty=empty):
                self.assertEqual(check_backlog.problems([item(7, needed=empty)]),
                                 ["#7 P7 — x: no `Needed by` — W14: an item names the design that needs it"])

    def test_an_item_on_no_slice_is_named(self):
        self.assertEqual(check_backlog.problems([item(8, slice_=None)]), ["#8 P8 — x: on no slice of the story map"])

    def test_a_second_item_in_build_is_named_with_both(self):
        self.assertEqual(check_backlog.problems([item(1, "Build"), item(2, "Build")]),
                         ["Build holds 2 (#1, #2) — its limit is 1: finish one before starting another"])

    def test_three_in_flight_is_too_many_even_one_per_stage(self):
        self.assertEqual(check_backlog.problems([item(1, "Discovery"), item(2, "Build"), item(3, "Review")]),
                         ["3 in flight (#1, #2, #3) — at most 2: one being worked, one waiting"])

    def test_an_epic_carries_no_limit_its_stories_do(self):
        self.assertEqual(check_backlog.problems([item(1, "Build", labels=("epic",)), item(2, "Build")]), [])

    def test_done_and_idea_carry_no_limit(self):
        self.assertEqual(check_backlog.problems([item(n, "Done") for n in range(9)] + [item(20 + n, "Idea") for n in range(9)]), [])

    def test_the_recorded_board_reads(self):
        items = json.loads((ROOT / "tests" / "data" / "p102a-items.json").read_text())["items"]
        self.assertTrue(items)
        self.assertIsInstance(check_backlog.problems(items), list)

    def test_offline_the_gate_says_it_could_not_look_and_passes(self):
        with mock.patch.object(check_backlog, "fetch", return_value=None), mock.patch("sys.stdout") as out:
            self.assertEqual(check_backlog.main(), 0)
        self.assertIn("skipped", "".join(call.args[0] for call in out.write.call_args_list))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2.** Run `python3 -m unittest discover -s tests -t tests -p 'test_check_backlog.py'`. Expected: an ERROR,
  `No module named 'check_backlog'`.
- [ ] **Step 3: Implement** `tools/check_backlog.py`:

```python
#!/usr/bin/env python3
"""
W14 and the WIP limits on the spark project's open items (P102a; docs/2026-10-05-backlog-in-github-design.md §8).
Run by tools/check_commit.py at every push. With no network or no gh it says it could not look, and passes: the gate
must work offline.
"""

import json
import re
import subprocess
import sys

OWNER, TITLE = "xmejkal", "spark"
#: The stages that carry a limit (§3); Idea and Done carry none.
LIMITS = {"Discovery": 1, "Design": 1, "Ready": 3, "Build": 1, "Review": 1}
IN_FLIGHT = ("Discovery", "Design", "Build", "Review")
MOST_IN_FLIGHT = 2


def _section(body, name):
    match = re.search(r"### %s\s*\n(.*?)(?=\n### |\Z)" % re.escape(name), body or "", re.S)
    text = match.group(1).strip() if match else ""
    return "" if text == "_No response_" else text


def _name(entry):
    return "#%s %s" % (entry["content"].get("number"), entry["content"].get("title", ""))


def problems(items):
    """Every sentence the gate fails on: an item with no Needed by or no slice, and a broken WIP limit (epics carry none)."""
    said, by_stage = [], {}
    for entry in items:
        status = entry.get("status")
        if status == "Done":
            continue
        if "epic" not in (entry.get("labels") or []):
            by_stage.setdefault(status, []).append(entry)
        if not _section(entry["content"].get("body"), "Needed by"):
            said.append("%s: no `Needed by` — W14: an item names the design that needs it" % _name(entry))
        if not entry.get("slice"):
            said.append("%s: on no slice of the story map" % _name(entry))
    for stage, limit in LIMITS.items():
        held = by_stage.get(stage, [])
        if len(held) > limit:
            said.append("%s holds %d (%s) — its limit is %d: finish one before starting another"
                        % (stage, len(held), ", ".join("#%s" % e["content"].get("number") for e in held), limit))
    flying = [e for stage in IN_FLIGHT for e in by_stage.get(stage, [])]
    if len(flying) > MOST_IN_FLIGHT:
        said.append("%d in flight (%s) — at most %d: one being worked, one waiting"
                    % (len(flying), ", ".join("#%s" % e["content"].get("number") for e in flying), MOST_IN_FLIGHT))
    return said


def fetch():
    """The spark project's items, or None when gh or the network cannot be reached."""
    try:
        projects = json.loads(subprocess.run(["gh", "project", "list", "--owner", OWNER, "--format", "json"],
                                             capture_output=True, text=True, timeout=30, check=True).stdout)["projects"]
        number = next(p["number"] for p in projects if p["title"] == TITLE)
        return json.loads(subprocess.run(["gh", "project", "item-list", str(number), "--owner", OWNER, "--format", "json",
                                          "--limit", "500"], capture_output=True, text=True, timeout=60, check=True).stdout)["items"]
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, StopIteration):
        return None


def main():
    items = fetch()
    if items is None:
        print("  backlog: skipped — gh or the network could not be reached")
        return 0
    said = problems(items)
    print("  backlog: %d open, %s" % (sum(1 for e in items if e.get("status") != "Done"),
                                      "the limits hold" if not said else "%d problem(s)" % len(said)))
    for sentence in said:
        print("    " + sentence)
    return 1 if said else 0


if __name__ == "__main__":
    sys.exit(main())
```

  `tools/check_commit.py` `main`, after the size line, in place of its last `return`:

```python
    sys.path.insert(0, str(ROOT / "tools"))
    import check_backlog
    backlog = check_backlog.main()
    return EXIT_OK if ok and backlog == 0 else EXIT_PROBLEMS
```
- [ ] **Step 4.** Run the Step 2 command, then the suite. Expected: PASS; the suite `OK`.
- [ ] **Step 5: Mutation table** `tests/mutations/p102a-check-backlog.json`:

```json
[
 {"file": "tools/check_backlog.py", "name": "Done items are checked", "find": "        if status == \"Done\":\n            continue\n", "replace": ""},
 {"file": "tools/check_backlog.py", "name": "_No response_ counts as an answer", "find": "return \"\" if text == \"_No response_\" else text", "replace": "return text"},
 {"file": "tools/check_backlog.py", "name": "the slice is not checked", "find": "        if not entry.get(\"slice\"):\n", "replace": "        if False:\n"},
 {"file": "tools/check_backlog.py", "name": "a stage's limit is ignored", "find": "        if len(held) > limit:\n", "replace": "        if False:\n"},
 {"file": "tools/check_backlog.py", "name": "in flight has no cap", "find": "    if len(flying) > MOST_IN_FLIGHT:\n", "replace": "    if False:\n"},
 {"file": "tools/check_backlog.py", "name": "an epic counts against the limits", "find": "        if \"epic\" not in (entry.get(\"labels\") or []):\n            by_stage", "replace": "        if True:\n            by_stage"},
 {"file": "tools/check_backlog.py", "name": "offline fails the gate", "find": "        print(\"  backlog: skipped — gh or the network could not be reached\")\n        return 0\n", "replace": "        return 1\n"}
]
```

  Run `python3 tools/mutate.py tests/mutations/p102a-check-backlog.json` (in the foreground, with a 600000 ms
  timeout). Expected: every mutation caught. Then run `--anchors`: clean.
- [ ] **Step 6.** Commit:
  `P102a: check_backlog — W14 and the WIP limits on the spark project, at every push; offline it says so and passes`
  (trailer). The pre-push gate now prints the backlog line.

---

### Task 5: The archive frozen, the map by issue number, the suite's archive check

**Files:** Modify `scrum/PRODUCT_BACKLOG.md`, `scrum/STORY_MAP.md`, `scrum/SPRINT.md` and `tests/test_orphans.py`.

**Interfaces:**
- Consumes `<workspace>/issues.json` (Task 3), the map from id to `{"repo", "number", "url"}`.
- Consumes Task 1's table: the closes, parks and merges.

- [ ] **Step 1: Failing test.** In `tests/test_orphans.py`, replace `test_every_open_backlog_item_names_the_design_that_needs_it`
  and `test_every_open_backlog_item_sits_on_the_story_map` with:

```python
    def test_the_archive_holds_no_open_item(self):
        # P102a: the backlog lives in GitHub Projects; the Markdown file is the frozen archive, and every heading in it
        # says where its item went (MOVED to an issue) or how it ended.
        closed = re.compile(r"MOVED|DONE|ANSWERED|CLOSED|PARKED|MERGED|DELETED|SPLIT|~~")
        text = (ROOT / "scrum" / "PRODUCT_BACKLOG.md").read_text()
        self.assertIn("This is the archive", text.split("\n### ")[0])
        unmarked = [line[4:60] for line in text.splitlines() if line.startswith("### ") and not closed.search(line)]
        self.assertEqual(unmarked, [], "archive headings with no MOVED/closed marker: %s" % unmarked)
```

  Run `python3 -m unittest discover -s tests -t tests -p 'test_orphans.py' -k archive`. Expected: FAIL (no banner,
  and about 35 unmarked).
- [ ] **Step 2: Freeze.** A short script in `<workspace>` applies the table and `issues.json` to `PRODUCT_BACKLOG.md`:
  - each kept item's heading gains ` — MOVED to xmejkal/<repo>#<number>`;
  - each close gains ` — DONE <date of its evidence commit>`;
  - each park gains ` — PARKED <today>: <what pulls it back>`;
  - each merge gains ` — MERGED into <id>`.

  The file then opens with:

```markdown
> **This is the archive, frozen 2026-10-05.** The backlog lives in GitHub Projects: **spark**
> (https://github.com/users/xmejkal/projects/<n>) and **the bin** (https://github.com/users/xmejkal/projects/<m>).
> Every heading below says where its item went (MOVED to an issue) or how it ended. Nothing is added here.
```

- [ ] **Step 3: The map.** In `scrum/STORY_MAP.md`:
  - each bold item id becomes `**<id>** (#<number>)` for moved items, in the slice table and the lines below it;
  - the order lines (from "**First, the PO's call of 2026-10-05**" to "**Merged:**") become one line:
    *"Order and status live in the projects (links above); this map keeps the slices and which items sit in each,
    as text for P102b to draw."*
- [ ] **Step 4.** `scrum/SPRINT.md` opens with:
  *"Sprint 10 closed 2026-10-05 with the move to Kanban (P102a): the board is the spark project; this file is the
  history of Sprints 1–10."*
- [ ] **Step 5.** Run the Step 1 command and then the suite. Expected: PASS; the suite `OK`. The anchors are clean
  (no table anchors these files).
- [ ] **Step 6.** Commit:
  `P102a: the Markdown backlog frozen as the archive, every heading marked; the map by issue number; Sprint 10 closed with the move to Kanban`
  (trailer).

---

### Task 6: How we work — the working agreements, the ceremonies, the Definition of Done

**Files:** Modify `scrum/WORKING_AGREEMENTS.md` (W6, W11, W18, W19) and `scrum/README.md` (the ceremonies table, the
`SPRINT.md` row, the Definition of Done's sweep).

- [ ] **Step 1.** Rewrite each agreement's rule paragraph. Keep its **Origin** line as it is.
  - **W6 — Finish before starting:** *"The board's limits are the rule: one item in each working stage, at most two in
    flight (one being worked, one waiting), three in Ready. `tools/check_backlog.py` fails the push when a limit is
    broken, so this holds by command, not by memory."*
  - **W11 — Nobody but the Product Owner reorders the backlog:** *"…Petr decides, by the row order of the Ready
    column; refilling Ready is when he chooses what comes next."* Keep the rest of the paragraph.
  - **W18 — Refinement is the team's, and the PO has the last word:** replace *"before a sprint is planned around it"*
    with *"before it enters Ready"*.
  - **W19 — The item exists before the work starts:** replace *"An item is written and ordered"* with *"An issue is
    created on the project, with its Needed by and Value proven by,"*. A feature's PR says `Closes #N`.
- [ ] **Step 2.** `scrum/README.md`'s ceremonies table becomes:

  | cadence | when | what it produces |
  | --- | --- | --- |
  | **Replenish** | Ready runs low | the PO orders Ready |
  | **Day-close** | the end of each working day | one dated line: moved, proven, aging, next card (where: P102c) |
  | **Weekly look** | once a week | the PO's look at the board: waiting over 3 days, epics started and finished |
  | **Epic done** | an epic's last story is Done | its review (validated value), the outside audit, then the retro — one change with the check that tells us later whether it stuck |

  Also:
  - the `SPRINT.md` row reads *"the history of Sprints 1–10"*;
  - the Definition of Done's *"At each sprint's close"* sweep reads *"When an epic is done"*.
- [ ] **Step 3.** Run the suite. Expected: `OK`.
- [ ] **Step 4.** Commit:
  `P102a: how we work — the limits are W6, the Ready column is W11's order, an issue is W19's item, the epic is the unit of review, audit and retro`
  (trailer).

---

### Task 7: The views, the proof, the close

- [ ] **Step 1: The views,** made by hand. GitHub's API cannot create views or column limits. For each project:
  - a Board by Status, with column limits Discovery 1, Design 1, Ready 3, Build 1, Review 1;
  - a Table;
  - a Roadmap grouped by Slice.

  Done by the PO, or by Claude in his browser with his go.
- [ ] **Step 2: Value proven by.** P70's line:
  - `gh project item-list <n> --owner xmejkal --format json --limit 500` lists every open spark item, with *Needed by*
    filled in its body;
  - `tools/check_backlog.py` prints `the limits hold`;
  - `test_orphans` passes on the frozen file.

  Write the output into P102a's issue as a comment, and move P102a to Review.
- [ ] **Step 3: Review.** One fresh reviewer on the most capable model reads the branch's range, together with
  `real-run.txt` and the projects. Important findings get one fix pass.
- [ ] **Step 4: Close.** Push, then the PO merges PR #4 (which says `Closes #<P102a>`). Move P102a to Done. P102c is
  next, the first item of the Ready column.
