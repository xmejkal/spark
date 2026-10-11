#!/usr/bin/env python3
"""
What spark answers today in the projects that use it, recorded on copies, never on the originals.

    tools/snapshot.py --out <dir>                        write <dir>/snapshot.json
    tools/snapshot.py --out <dir> --against <old.json>   and print the lines that differ, per command
    tools/snapshot.py --out <dir> --tsci-bin <path>      a toolchain for a project that has no node_modules
    tools/snapshot.py --out <dir> --spark <tree>         the spark whose answers are recorded (default: this one)

Why: nothing that changes an output may merge before today's outputs are recorded, so that every later change is a
diff against them (P184; P158's design §10.1 and §12.3, H0a). Each project is cloned into <dir> (APFS clones on
macOS: instant, no extra space), its documented spark commands run there under a copy of the person's store, and each
command's exit, stdout and stderr are kept with the scratch folders written as placeholders, so two snapshots of
unchanged spark are equal line for line. The project and the store are only read.

The baseline P158's plan measures against: docs/observations/2026-10-11-baseline.json (spark 684ed01, the store's
sha256 482bd310…). A card that changes an output says which of its lines it changes, and --against shows them.

Exit: 0 a snapshot was taken and, with --against, nothing differs · 1 lines differ · 2 it could not run.
"""

import argparse
import datetime
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


def _spark(script, *args, needs_tsci=False, label=None):
    return {"label": label or " ".join((script,) + args), "argv": ["{spark}/scripts/" + script, *args],
            "needs_tsci": needs_tsci}


def projects():
    """The projects a snapshot covers, and for each the spark commands it is documented to run."""
    circuit, gerbers = "dist/board/circuit.json", "board-gerbers.zip"
    found = [
        {"name": "smartbin-local", "source": str(Path.home() / "Development" / "smartbin-local"),
         # The spark lines of the bin's Makefile: :49-53, :96, :182, :186 and :212, :220, :228, :232.
         "commands": [_spark("boards.py", "--path"), _spark("boards.py", "--id"), _spark("boards.py", "--paths"),
                      _spark("boards.py", "--get", "chip"), _spark("boards.py", "--get", "micropython_port"),
                      _spark("boards.py", "--resolve"), _spark("boards.py", "--validate", "--for-fab"),
                      _spark("check_bom.py", gerbers, "--circuit", circuit),
                      _spark("check_vendor_pins.py", "{boards.py --paths}", "--offline"),
                      _spark("check_physics.py", circuit, "--rules", ".spark/rules.json"),
                      _spark("boards.py", "--validate")],
         "left_out": {"check_vendor_pins.py (live)": "Makefile:223 fetches from GitHub; a snapshot stays offline"}},
        {"name": "irrigation", "source": str(Path.home() / "Development" / "irrigation"),
         "commands": [_spark("check_spine.py", "irrigation.requirements.json", needs_tsci=True),
                      _spark("check_all.py", "--project", ".")], "left_out": {}},
        {"name": "plant-alarm", "source": str(Path.home() / "Development" / "plant-alarm"),
         "commands": [_spark("check_spine.py", "requirements.json", needs_tsci=True)], "left_out": {}},
    ]
    for fixture in sorted(p for p in FIXTURES.iterdir() if p.is_dir()) if FIXTURES.is_dir() else []:
        commands = [_spark("boards.py", "--validate", "--project", "."),
                    _spark("boards.py", "--validate", "--for-fab", "--project", ".")]
        if (fixture / "requirements.json").is_file():
            commands.append(_spark("check_spine.py", "requirements.json", needs_tsci=True))
        found.append({"name": fixture.name, "source": str(fixture), "commands": commands, "left_out": {}})
    return found


def _clone(source: Path, target: Path):
    """A copy of `source` at `target`: an APFS clone where the system has one, else a plain copy."""
    if sys.platform == "darwin" and subprocess.run(["cp", "-c", "-R", str(source), str(target)],
                                                   capture_output=True).returncode == 0:
        return
    shutil.copytree(source, target, symlinks=True)


def _digest(folder: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(folder.rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(folder)).encode()); h.update(p.read_bytes())
    return h.hexdigest()


#: tempfile's random part of a folder name (8 characters of its alphabet), right after a prefix in the temp folder.
RANDOM_TEMP = re.compile(r"(<tmp>/[A-Za-z][A-Za-z_-]*?)[a-z0-9_]{8}(?=[/\s'\")]|$)", re.M)


def _placeholders(text: str, names: dict) -> str:
    """The scratch folders and the home written as `<copy>`, `<spark>`, `<store>`, `~`, and tempfile's random part of
    a folder name as `<random>`, so two runs of unchanged spark compare equal."""
    for path, name in sorted(names.items(), key=lambda kv: -len(kv[0])):
        text = text.replace(path, name)
    return RANDOM_TEMP.sub(r"\1<random>", text)


def _git(folder: Path) -> str:
    out = subprocess.run(["git", "-C", str(folder), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    if out.returncode:
        return "not a git repository: this copy is its pin"
    dirty = subprocess.run(["git", "-C", str(folder), "status", "--porcelain"], capture_output=True, text=True).stdout
    return out.stdout.strip() + (" with uncommitted changes" if dirty.strip() else "")


def _run_project(project, work: Path, spark: Path, store: Path, tsci_bin, env_extra):
    copy = work / project["name"]
    _clone(Path(project["source"]), copy)
    home, tmp = work / ".home", work / ".tmp"
    home.mkdir(exist_ok=True); tmp.mkdir(exist_ok=True)
    tools = copy / "node_modules" / ".bin"
    toolchain = tools if tools.is_dir() else (Path(tsci_bin) if tsci_bin else None)
    env = dict(os.environ, SPARK_HOME=str(store), HOME=str(home), TMPDIR=str(tmp), **(env_extra or {}))
    if toolchain:
        env["PATH"] = str(toolchain) + os.pathsep + env.get("PATH", "")
    names = {str(copy.resolve()): "<copy>", str(copy): "<copy>", str(spark): "<spark>", str(store.resolve()): "<store>",
             str(store): "<store>", str(home): "<home>", str(tmp.resolve()): "<tmp>", str(tmp): "<tmp>",
             str(Path.home()): "~"}
    if toolchain:
        names[str(toolchain)] = "<tsci-bin>"
    outputs, results = {}, []
    for command in project["commands"]:
        row = {"label": command["label"]}
        if command["needs_tsci"] and toolchain is None:
            row.update(exit=None, stdout="", stderr="", skipped=NO_TSCI)
            results.append(row)
            continue
        argv = []
        for word in command["argv"]:
            if word.startswith("{") and word.endswith("}") and word[1:-1] in outputs:
                argv += outputs[word[1:-1]].split()  # an earlier command's output, as the Makefile's $(...) does
            else:
                argv.append(word.replace("{spark}", str(spark)))
        done = subprocess.run([sys.executable] + argv, cwd=copy, env=env, capture_output=True, text=True,
                              timeout=TIMEOUT)
        outputs[command["label"]] = done.stdout
        row.update(exit=done.returncode, stdout=_placeholders(done.stdout, names),
                   stderr=_placeholders(done.stderr, names))
        results.append(row)
    return {"source": _placeholders(project["source"], {str(Path.home()): "~"}), "pin": _git(Path(project["source"])),
            "commands": results, "left_out": project.get("left_out", {})}


def take(project_list, out, spark=ROOT, store=STORE, tsci_bin=None, env=None):
    """One snapshot: every project's commands, run on copies under a copy of `store`. Returns the record."""
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    store_copy = out / ".store"
    if store_copy.exists():
        shutil.rmtree(store_copy)
    _clone(Path(store), store_copy)
    record = {"taken": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
              "spark": {"pin": _git(Path(spark))},
              "store": {"source": _placeholders(str(store), {str(Path.home()): "~"}), "sha256": _digest(store_copy)},
              "projects": {}}
    for project in project_list:
        work = out / "copies"
        target = work / project["name"]
        if target.exists():
            shutil.rmtree(target)
        work.mkdir(exist_ok=True)
        record["projects"][project["name"]] = _run_project(project, work, Path(spark), store_copy, tsci_bin, env)
    return record


def report(old, new):
    """The lines that differ between two snapshots, under each command that printed them; [] when none do."""
    lines = []
    for name, project in new["projects"].items():
        before = {c["label"]: c for c in old.get("projects", {}).get(name, {}).get("commands", [])}
        for command in project["commands"]:
            was = before.get(command["label"])
            if was is None:
                lines.append("%s: %s — new in this snapshot" % (name, command["label"]))
                continue
            changed = []
            if was.get("exit") != command.get("exit"):
                changed.append("  exit %s → %s" % (was.get("exit"), command.get("exit")))
            for stream in ("stdout", "stderr"):
                a, b = was.get(stream, "").splitlines(), command.get(stream, "").splitlines()
                changed += ["  - " + l for l in a if l not in b] + ["  + " + l for l in b if l not in a]
            if changed:
                lines.append("%s: %s — %d line(s) differ from the snapshot of %s" % (
                    name, command["label"], len(changed), old.get("taken", "an older run")))
                lines += changed
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(prog="snapshot.py", description=__doc__.strip().splitlines()[0])
    parser.add_argument("--out", required=True, help="the folder for the copies and snapshot.json")
    parser.add_argument("--against", help="an older snapshot.json to compare with")
    parser.add_argument("--tsci-bin", help="a node_modules/.bin for projects that have none (never linked into them)")
    parser.add_argument("--spark", default=str(ROOT), help="the spark tree whose answers are recorded (default: %(default)s)")
    args = parser.parse_args(argv)
    try:
        record = take(projects(), args.out, spark=Path(args.spark), store=STORE, tsci_bin=args.tsci_bin)
    except (OSError, subprocess.SubprocessError) as broken:
        print("snapshot.py: could not run — %s" % broken, file=sys.stderr)
        return 2
    path = Path(args.out) / "snapshot.json"
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    for name, project in record["projects"].items():
        exits = ", ".join("%s %s" % (c["label"], "skipped" if c.get("skipped") else "exit %d" % c["exit"])
                          for c in project["commands"])
        print("%s (%s): %s" % (name, project["pin"], exits))
    print("wrote %s" % path)
    if not args.against:
        return 0
    lines = report(json.loads(Path(args.against).read_text()), record)
    print("\n".join(lines) if lines else "nothing differs from %s" % args.against)
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main())
