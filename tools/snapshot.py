#!/usr/bin/env python3
"""
What spark answers in the projects that use it, recorded on copies, never on the originals.

    tools/snapshot.py --out <dir>                        write <dir>/snapshot.json
    tools/snapshot.py --out <dir> --against <old.json>   and print the lines that differ, per command
    tools/snapshot.py --out <dir> --tsci-bin <path>      a toolchain for a project that has no node_modules
    tools/snapshot.py --out <dir> --spark <tree>         the spark whose answers are recorded (default: this one)

Before and after a change that alters an output: main first, then the branch against it.

    tools/snapshot.py --out /tmp/before --spark <main checkout> --tsci-bin ~/Development/smartbin-local/node_modules/.bin
    tools/snapshot.py --out /tmp/after --against /tmp/before/snapshot.json --tsci-bin <the same>

Against the baseline instead, every output change merged since 2026-10-11 shows too.

Why: no change to spark's output merges before its outputs of 2026-10-11 are recorded, so every later change can show
what it changed (P184, #133). The baseline is docs/observations/2026-10-11-baseline.json. A card
that changes an output says which of its lines it changes, and --against shows them.

How: each project is cloned into <dir> (an APFS clone on macOS, so no extra space). Its documented spark commands run
there under a copy of the person's store. Each command's exit, stdout and stderr are kept, with the scratch folders
written as placeholders, so two snapshots of unchanged spark compare equal. The projects and the store are only read.

What it records: the text of boards.py, check_bom.py, check_vendor_pins.py, check_physics.py, check_spine.py and
check_all.py, as the projects run them, with what they call. Not recorded: any --json answer, any command of parts.py,
drawer.py or needs.py, and the ten placeholder channels counted per project (#133). A change that shows only in those
does not show here.

Needs: the bin, irrigation and plant-alarm at ~/Development/<name> (a missing one is skipped and said), the store at
~/.local/share/spark (copied, never used live), and tsci for the chain: a project's own node_modules, or --tsci-bin.
Without either, the chain's steps are recorded as skipped. A full run takes about a minute. --out must lie outside
spark's tree, and a second run into it replaces the first's copies.

A difference is not always spark's: the report says first when the store, a project's pin or spark's pin differs.
Those lines are context: a run on a later commit whose commands all answer as before still exits 0.

Exit 0: a snapshot was taken and, with --against, nothing differs; 1: some lines differ; 2: it could not run.
"""

import argparse
import datetime
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORE = Path.home() / ".local" / "share" / "spark"
FIXTURES = ROOT / "tests" / "data" / "snapshot"
NO_TSCI = "no node_modules in the copy (tsci needed); copy it, never link it"
TIMEOUT = 600  # seconds per command: a chain run builds a board
#: tempfile's random part of a folder name, after a spark prefix: `spark-spine-` + 8 characters of its alphabet.
RANDOM_TEMP = re.compile(r"(<tmp>/spark-[a-z]+(?:-[a-z]+)*-)[a-z0-9_]{8}\b")
#: What a digest of a project outside git leaves out: what it installs and what it builds.
NOT_DIGESTED = {"node_modules", "dist", ".tscircuit", "__pycache__"}


def _spark(script, *args, needs_tsci=False):
    return {"label": " ".join((script,) + args), "argv": ["{spark}/scripts/" + script, *args], "needs_tsci": needs_tsci}


def projects():
    """The projects a snapshot covers, and for each the spark commands it is documented to run."""
    circuit, gerbers = "dist/board/circuit.json", "board-gerbers.zip"
    found = [
        {"name": "smartbin-local", "source": str(Path.home() / "Development" / "smartbin-local"),
         # The spark lines of the bin's Makefile, in its order.
         "commands": [_spark("boards.py", "--path"), _spark("boards.py", "--id"), _spark("boards.py", "--paths"),
                      _spark("boards.py", "--get", "chip"), _spark("boards.py", "--get", "micropython_port"),
                      _spark("boards.py", "--resolve"), _spark("boards.py", "--validate", "--for-fab"),
                      _spark("check_bom.py", gerbers, "--circuit", circuit),
                      _spark("check_vendor_pins.py", "{boards.py --paths}", "--offline"),
                      _spark("check_physics.py", circuit, "--rules", ".spark/rules.json"),
                      _spark("boards.py", "--validate")],
         "left_out": {"check_vendor_pins.py (live)": "the Makefile's refresh fetches from GitHub; a snapshot stays offline"}},
        {"name": "irrigation", "source": str(Path.home() / "Development" / "irrigation"),
         "commands": [_spark("check_spine.py", "irrigation.requirements.json", needs_tsci=True),
                      _spark("check_all.py", "--project", ".")], "left_out": {}},
        {"name": "plant-alarm", "source": str(Path.home() / "Development" / "plant-alarm"),
         "commands": [_spark("check_spine.py", "requirements.json", needs_tsci=True)], "left_out": {}},
    ]
    fixtures = sorted(p for p in FIXTURES.iterdir() if p.is_dir()) if FIXTURES.is_dir() else []
    for fixture in fixtures:
        commands = [_spark("boards.py", "--validate", "--project", "."),
                    _spark("boards.py", "--validate", "--for-fab", "--project", ".")]
        if (fixture / "requirements.json").is_file():
            commands.append(_spark("check_spine.py", "requirements.json", needs_tsci=True))
        found.append({"name": fixture.name, "source": str(fixture), "commands": commands, "left_out": {}})
    return found


def shown(path) -> str:
    """A path as a record shows it: inside this repository relative to it, under the home as `~`."""
    path = str(path)
    if path.startswith(str(ROOT) + os.sep):
        return path[len(str(ROOT)) + 1:]
    return path.replace(str(Path.home()), "~", 1) if path.startswith(str(Path.home())) else path


def _clone(source: Path, target: Path):
    """A copy of `source` at `target`: an APFS clone where the system has one, else a plain copy."""
    if sys.platform == "darwin" and subprocess.run(["cp", "-c", "-R", str(source), str(target)],
                                                   capture_output=True).returncode == 0:
        return
    shutil.rmtree(target, ignore_errors=True)  # a clone that stopped halfway leaves a partial target
    shutil.copytree(source, target, symlinks=True)


def _digest(folder: Path, skip=frozenset()) -> str:
    """Every file under `folder`, path and bytes, as one sha256, leaving out the folders and files named in `skip`."""
    h = hashlib.sha256()
    for p in sorted(folder.rglob("*")):
        if p.is_file() and not skip.intersection(p.relative_to(folder).parts):
            h.update(str(p.relative_to(folder)).encode()); h.update(p.read_bytes())
    return h.hexdigest()


def _pin(folder: Path) -> str:
    """What fixes a source's content: its commit and any uncommitted files, or, outside git, a digest."""
    if FIXTURES.resolve() in folder.resolve().parents:  # a fixture: its own content, not the repository's
        return "in this repository: sha256 %s" % _digest(folder, {"README.md"})[:12]  # what spark reads
    git = ["git", "--no-optional-locks", "-C", str(folder)]  # never refresh the project's index: it is only read
    head = subprocess.run(git + ["rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    if head.returncode:
        return "not a git repository: sha256 %s" % _digest(folder, NOT_DIGESTED)[:12]
    dirty = subprocess.run(git + ["status", "--porcelain"], capture_output=True, text=True).stdout.split("\n")
    names = sorted(line[3:] for line in dirty if line.strip())
    return head.stdout.strip() + (" with uncommitted changes: " + ", ".join(names) if names else "")


def _placeholders(text: str, names: dict) -> str:
    """The scratch folders and the home written as `<copy>`, `<spark>`, `<store>`, `~`, and tempfile's random part of
    a spark folder's name as `<random>`, so two runs of unchanged spark compare equal."""
    for path, name in sorted(names.items(), key=lambda kv: -len(kv[0])):
        text = text.replace(path, name)
    return RANDOM_TEMP.sub(r"\1<random>", text)


def _argv(command, spark: Path, outputs: dict):
    """The command line, an earlier command's output put in where `{label}` asks for it; None, and why, when missing."""
    argv = []
    for word in command["argv"]:
        if word.startswith("{") and word.endswith("}") and word != "{spark}":
            label = word[1:-1]
            if label not in outputs:
                return None, "needs the output of `%s`, which this project did not run" % label
            if outputs[label].returncode:
                return None, "needs the output of `%s`, which exited %d" % (label, outputs[label].returncode)
            argv += outputs[label].stdout.split()  # as the Makefile's $(shell ...) does
        else:
            argv.append(word.replace("{spark}", str(spark)))
    return argv, None


def _run_project(project, work: Path, spark: Path, store: Path, tsci_bin, env_extra):
    source = Path(project["source"])
    record = {"source": shown(source), "left_out": project.get("left_out", {})}
    if not source.is_dir():
        return dict(record, skipped="its folder is not there", commands=[])
    copy, home, tmp = work / project["name"], work / ".home", work / ".tmp"
    for folder in (copy, home, tmp):  # nothing from an earlier project or run is read again
        shutil.rmtree(folder, ignore_errors=True)
    home.mkdir(); tmp.mkdir()
    record["pin"] = _pin(source)
    _clone(source, copy)
    own = copy / "node_modules" / ".bin"
    toolchain = own if own.is_dir() else (Path(tsci_bin) if tsci_bin else None)
    record["toolchain"] = "the project's node_modules" if own.is_dir() else ("--tsci-bin" if toolchain else "none")
    env = dict(os.environ, SPARK_HOME=str(store), HOME=str(home), TMPDIR=str(tmp), **(env_extra or {}))
    if toolchain:
        env["PATH"] = str(toolchain) + os.pathsep + env.get("PATH", "")
    names = {str(copy.resolve()): "<copy>", str(copy): "<copy>", str(spark): "<spark>", str(store.resolve()): "<store>",
             str(store): "<store>", str(home): "<home>", str(tmp.resolve()): "<tmp>", str(tmp): "<tmp>",
             str(Path.home()): "~", **({str(toolchain): "<tsci-bin>"} if toolchain else {})}
    outputs, results = {}, []
    for command in project["commands"]:
        row = {"label": command["label"], "exit": None, "stdout": "", "stderr": ""}
        argv, why = _argv(command, spark, outputs)
        if command["needs_tsci"] and toolchain is None:
            why = NO_TSCI
        if why:
            results.append(dict(row, skipped=why))
            continue
        try:
            done = subprocess.run([sys.executable] + argv, cwd=copy, env=env, capture_output=True, text=True,
                                  timeout=TIMEOUT)
        except subprocess.TimeoutExpired as late:  # what it printed before it was stopped is kept
            partial = {stream: _placeholders((text or b"").decode(errors="replace"), names)
                       for stream, text in (("stdout", late.stdout), ("stderr", late.stderr))}
            results.append(dict(row, skipped="timed out after %s s" % TIMEOUT, **partial))
            continue
        outputs[command["label"]] = done
        results.append(dict(row, exit=done.returncode, stdout=_placeholders(done.stdout, names),
                            stderr=_placeholders(done.stderr, names)))
    return dict(record, commands=results)


def take(project_list, out, spark=ROOT, store=STORE, tsci_bin=None, env=None):
    """One snapshot: every project's commands, run on copies under a copy of `store`. Returns the record."""
    out = Path(out).resolve(); out.mkdir(parents=True, exist_ok=True)
    store_copy, work = out / ".store", out / "copies"
    shutil.rmtree(store_copy, ignore_errors=True)
    _clone(Path(store), store_copy)
    work.mkdir(exist_ok=True)
    record = {"taken": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
              "spark": {"pin": _pin(Path(spark))},
              "store": {"source": shown(store), "sha256": _digest(store_copy)}, "projects": {}}
    for project in project_list:
        record["projects"][project["name"]] = _run_project(project, work, Path(spark), store_copy, tsci_bin, env)
    return record


def _said(command):
    """A command's outcome for a comparison: its exit, or `skipped:` and why, so a changed reason shows."""
    return "skipped: " + command["skipped"] if command.get("skipped") else command.get("exit")


def context(old, new):
    """What changed around the commands: the store, spark's pin, a project's pin. Said first, so a reader knows whose a
    difference may be; never a difference itself, since a card's own branch always moves spark's pin."""
    lines = []
    if old.get("store", {}).get("sha256") != new["store"]["sha256"]:
        lines.append("the store differs from the one of %s: some lines may be the store's, not spark's"
                     % old.get("taken", "the older run"))
    if old.get("spark", {}).get("pin") != new["spark"]["pin"]:
        lines.append("spark: %s → %s" % (old.get("spark", {}).get("pin"), new["spark"]["pin"]))
    for name, project in new["projects"].items():
        was = old.get("projects", {}).get(name)
        if was and was.get("pin") != project.get("pin"):
            lines.append("%s: pin %s → %s" % (name, was.get("pin"), project.get("pin")))
    return lines


def report(old, new):
    """The lines that differ between two snapshots, under each command that printed them; [] when none do."""
    lines = []
    for name, project in new["projects"].items():
        before = {c["label"]: c for c in old.get("projects", {}).get(name, {}).get("commands", [])}
        for command in project.get("commands", []):
            was = before.get(command["label"])
            if was is None:
                lines.append("%s: %s — new in this snapshot" % (name, command["label"]))
                continue
            changed = []
            if _said(was) != _said(command):
                changed.append("  exit %s → %s" % (_said(was), _said(command)))
            for stream in ("stdout", "stderr"):
                diff = [l for l in difflib.unified_diff(was.get(stream, "").splitlines(),
                                                        command.get(stream, "").splitlines(), lineterm="", n=0)
                        if not l.startswith(("---", "+++", "@@"))]
                if diff:
                    changed += ["  %s:" % stream] + ["    %s %s" % (l[0], l[1:]) for l in diff]
            if changed:
                lines.append("%s: %s — differs from the snapshot of %s"
                             % (name, command["label"], old.get("taken", "an older run")))
                lines += changed
        names = {c["label"] for c in project.get("commands", [])}
        lines += ["%s: %s — missing from this snapshot" % (name, label) for label in before if label not in names]
    lines += ["%s — missing from this snapshot" % name for name in old.get("projects", {}) if name not in new["projects"]]
    return lines


def _summary(record):
    """The human lines a run prints: one per command, then what was skipped for want of tsci."""
    for name, project in record["projects"].items():
        if project.get("skipped"):
            yield "%s: skipped — %s" % (name, project["skipped"])
            continue
        yield "%s (%s; toolchain %s):" % (name, project["pin"], project["toolchain"])
        for c in project["commands"]:
            yield "  %-48s %s" % (c["label"], "skipped: " + c["skipped"] if c.get("skipped") else "exit %d" % c["exit"])
    skipped = sum(1 for p in record["projects"].values() for c in p.get("commands", []) if c.get("skipped") == NO_TSCI)
    if skipped:
        yield "%d command(s) skipped for want of tsci: pass --tsci-bin" % skipped
    yield "the exits are recorded, not judged: a 1 or a 2 here is what spark answers today"


def main(argv=None):
    parser = argparse.ArgumentParser(prog="snapshot.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True, help="a folder outside the repository: snapshot.json, copies/, .store/")
    parser.add_argument("--against", help="an older snapshot.json: print the lines that differ, and exit 1 if any do")
    parser.add_argument("--tsci-bin", help="a node_modules/.bin for projects that have none (never linked into them); "
                                           "without it their chain steps are recorded as skipped")
    parser.add_argument("--spark", default=str(ROOT), help="the spark tree whose answers are recorded (default: this tree)")
    args = parser.parse_args(argv)
    out, spark = Path(args.out).resolve(), Path(args.spark).resolve()
    try:
        for tree in {ROOT, spark}:  # its copies there would be read as fixtures, or committed
            if out == tree or tree in out.parents:
                raise ValueError("%s is inside spark's tree %s; take the snapshot outside it" % (out, tree))
        if not (spark / "scripts" / "boards.py").is_file():
            raise ValueError("%s is not a spark tree: it has no scripts/boards.py" % spark)
        older = None
        if args.against:
            against = Path(args.against).resolve()
            if against == out / "snapshot.json":
                raise ValueError("%s is the snapshot this run would write; take the new one elsewhere" % against)
            older = json.loads(against.read_text())
        record = take(projects(), out, spark=spark, store=STORE, tsci_bin=args.tsci_bin)
    except (OSError, ValueError, subprocess.SubprocessError) as broken:
        print("snapshot.py: could not run — %s" % broken, file=sys.stderr)
        return 2
    path = out / "snapshot.json"
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    print("\n".join(_summary(record)))
    print("wrote %s" % path)
    if older is None:
        return 0
    lines = report(older, record)
    print("\n".join(context(older, record) + (lines or ["nothing differs from %s" % args.against])))
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main())
