"""
One git commit of one file spark changed in a person's project (P1027, slice 2), so `git revert --no-edit <sha>` takes that
change back. Before its write, the writer asks `held_as_is`: git must hold the file as it is on disk, staged and committed,
with HEAD on a branch. After the write it calls `commit`, which commits that file alone (`--only`), never with a guessed
author, and runs the person's hooks. Spark never stages with `git add`, never runs `revert`, `reset` or `push`, and never
skips a hook. A file git does not hold, a person's own edits or a HEAD off a branch give a reason and no commit.
"""

import os
import signal
import subprocess
from pathlib import Path

# --- MVP ---
#: Why there is no commit: git does not hold the file (no git, no repository, no commit, an untracked file), HEAD is on no
#: branch (detached, or a rebase that stopped), the person has edits git does not hold, or git did not finish in time.
UNHELD, NOT_ON_BRANCH, UNCOMMITTED, UNFINISHED = "unheld", "not-on-branch", "uncommitted", "unfinished"


class ProjectCommit:
    """Adapter: one git commit of one file spark changed in a project, so `git revert` takes that change back. The only
    code in scripts/spark/ that runs git. A name is the file's path from the project folder, which may be a subfolder of
    the repository, so git reads it as `./<name>`."""

    def __init__(self, project, timeout=30):
        self.project, self.timeout = Path(project), timeout

    def _git(self, *args):
        """(exit code, stdout, stderr) of git in the project, with no GIT_* variable: a hook's GIT_DIR must not steer it to
        another repository (P105). No git gives (127, "", why). On a timeout the whole group gets SIGTERM, so git removes
        its own index.lock and a hook's child ends too, and it gives (None, "", UNFINISHED)."""
        own = {name: value for name, value in os.environ.items() if not name.startswith("GIT_")}
        try:
            run = subprocess.Popen(["git", "-C", str(self.project), *args], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, env=own, start_new_session=True)
        except OSError as missing:
            return 127, "", str(missing)
        try:
            out, err = run.communicate(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            os.killpg(run.pid, signal.SIGTERM)
            run.communicate()
            return None, "", UNFINISHED
        return run.returncode, out.strip(), err.strip()

    def held_as_is(self, name):
        """None when git holds `name` as it is: in HEAD, with HEAD on a branch, and the same on disk and staged. Else the
        first reason, in this order: UNHELD, NOT_ON_BRANCH, UNCOMMITTED. The hashes see an edit `assume-unchanged` hides."""
        code, head, _ = self._git("rev-parse", "--verify", "-q", "HEAD:./" + name)
        if code != 0:
            return UNHELD
        if self._git("symbolic-ref", "-q", "HEAD")[0] != 0:
            return NOT_ON_BRANCH
        if self._git("hash-object", "--", name)[1] != head or self._git("rev-parse", "--verify", "-q", ":./" + name)[1] != head:
            return UNCOMMITTED
        return None

    def commit(self, name, message):
        """Commit `name` alone with `message`: (the short sha, None), or (None, git's first line, else its exit code) when git
        refuses, or (None, UNFINISHED). A missing identity is a refusal (`user.useConfigOnly`), never a guessed author."""
        code, out, err = self._git("-c", "user.useConfigOnly=true", "commit", "--quiet", "--only", "-m", message, "--", "./" + name)
        if code is None:
            return None, UNFINISHED
        if code != 0:
            return None, (err or out).splitlines()[0] if err or out else "git exited with %d" % code
        return self._git("rev-parse", "--short", "HEAD")[1], None
# --- end MVP ---
