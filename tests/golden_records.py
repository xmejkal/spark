"""
The records-with-sourcing goldens (P715, #966, W6-R1): what parts.py, boards.py, tools.py and cost.py print today, and
what each write Operation writes, kept in tests/golden-records/.

A helper module beside golden_design.py, no tests in it: tests/test_golden_records.py runs each Case with
golden_firmware's run_script, in its own copy of one project (a bare copy of golden_checks' button-light fixture) and its
own store. `SPARK_ACCEPT=parts python3 -m unittest tests.test_golden_records` writes parts.py's goldens from today's
output and fails, so that a person reads `git diff tests/golden-records`.

No golden reaches the network, a vendor site, an installer or a package manager. A child's PATH is the fakes' folder
alone, which holds a fake pdftotext and nothing else, so no curl, claude or install manager of tools.MANAGERS is found
(GUARDED, and the guard test runs `command -v` for each in a child). Its proxies are a closed port, its HOME an empty
folder, and it carries no secret of the parent (golden_checks.child_env). store.fetch admits `file:` only under
unittest, which a child never imports, so `--sources` and `--fetch` ask a URL at the closed port itself and fail in one
connect. tools.py's `--install` runs with `--dry-run` alone.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden_bench  # noqa: E402
import golden_checks  # noqa: E402
import golden_design  # noqa: E402
import golden_firmware  # noqa: E402
import tools  # noqa: E402
from golden_firmware import LOG_MARK  # noqa: E402

ROOT = golden_bench.ROOT
GOLDEN_DIR = ROOT / "tests" / "golden-records"
PROJECT = golden_firmware.PROJECT
#: The programs no child may find: each install manager's program, the downloader and Claude Code's own CLI.
GUARDED = tuple(program for _, program in tools.MANAGERS if program) + ("curl", "claude")
#: The session id every child runs in (the suite's own, store.py's), so `--step` never names the person's session.
SESSION = "spark-suite"
#: A `written` name that starts with STORE is read from the run's store, not its project.
STORE = "{store}/"
#: The fake pdf-text tool: one canned page for `-f 1`, and exit 1 for any other page, so a read stops after page 1.
PDFTOTEXT = """#!/bin/sh
# The golden net's pdftotext (P715): page 1 is a canned table, every other page is past the end.
[ "$1" = "-v" ] && { echo "pdftotext version 0.0.0-fake" >&2; exit 0; }
case " $* " in
  *" -f 1 "*) printf 'Forward voltage   VF   2.0 V\nForward current   IF   20 mA\n'; exit 0 ;;
esac
exit 1
"""
#: Where `--sources` and `--fetch` look: the closed port itself, so even a child with no proxy reaches nothing.
CLOSED_URL = golden_checks.CLOSED_PROXY + "/datasheet.pdf"
#: The errno of a refused connection differs by platform (61 on macOS, 111 on Linux).
ERRNO = re.compile(r"\[Errno \d+\] Connection refused")


def make_fakes(folder):
    """The fake pdftotext in a `bin` folder in `folder`. Returns the `bin` folder, a child's whole PATH."""
    shims = Path(folder) / "bin"
    shims.mkdir(parents=True, exist_ok=True)
    (shims / "pdftotext").write_text(PDFTOTEXT)
    (shims / "pdftotext").chmod(0o755)
    return shims


def child_env(store, shims):
    """golden_checks' child environment (PATH the fakes' folder alone, proxies closed, empty HOME, no secret) in the
    suite's session."""
    return dict(golden_checks.child_env(store, shims), CLAUDE_CODE_SESSION_ID=SESSION)


#: What a child runs to say which of GUARDED it finds, one path a line.
FIND_GUARDED = 'for name in "$@"; do command -v "$name"; done; exit 0'


def guarded_found(env):
    """The paths of GUARDED programs a child with `env` finds: [] when none."""
    import subprocess
    done = subprocess.run(["/bin/sh", "-c", FIND_GUARDED, "sh", *GUARDED], env=env, stdin=subprocess.DEVNULL,
                          capture_output=True, text=True, timeout=golden_bench.RUN_TIMEOUT_S)
    return done.stdout.split()


Case = golden_design.Case
CASES = []


def run_case(case, project, store, shims):
    """The text of `case` run in `project`, then each of its `written` files after LOG_MARK (STORE ones from `store`),
    and its exit code."""
    code, text = golden_firmware.run_script(case, project, store, child_env(store, shims))
    for name in case.written:
        place = Path(store) / name[len(STORE):] if name.startswith(STORE) else Path(project) / name
        text += LOG_MARK % name + place.read_text()
    return code, ERRNO.sub("[Errno <n>] Connection refused", text)
