"""
One git commit of one file spark changed in a person's project (P1027, slice 2), so `git revert --no-edit <sha>` takes that
change back. Before its write, the writer asks `held_as_is`: git must hold the file as it is on disk, staged and committed,
with HEAD on a branch. After the write it calls `commit`, which commits that file alone (`--only`), never with a guessed
author, and runs the person's hooks. Spark never stages with `git add`, never runs `revert`, `reset` or `push`, and never
skips a hook. A file git does not hold, a person's own edits or a HEAD off a branch give a reason and no commit. It also
reads which files git tracks, and changes nothing by it.
"""

import os
import signal
import subprocess
import tempfile
from pathlib import Path

# --- MVP ---
#: Why there is no commit: git does not hold the file (no git, no repository, no commit, an untracked file), HEAD is on no
#: branch (detached, or a rebase that stopped), the person has edits git does not hold, or git did not finish in time.
UNHELD, NOT_ON_BRANCH, UNCOMMITTED, UNFINISHED = "unheld", "not-on-branch", "uncommitted", "unfinished"
#: The GIT_* variables kept for spark's git: they only say where git reads its config (the person's global file, or no
#: system file), never which repository it works on, so git reads the config it reads for the person.
KEPT = ("GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM")
#: Seconds git has to end after SIGTERM, before its group gets SIGKILL.
STOP_WAIT = 5


class ProjectCommit:
    """Adapter: one git commit of one file spark changed in a project, so `git revert` takes that change back. The only
    code in scripts/spark/ that runs git. A name is the file's path from the project folder, which may be a subfolder of
    the repository, so git reads it as `./<name>`."""

    def __init__(self, project, timeout=30):
        self.project, self.timeout = Path(project), timeout

    def _git(self, *args):
        """(exit code, stdout, stderr) of git in the project, with no GIT_* variable but KEPT: a hook's GIT_DIR must not
        steer it to another repository (P105). No git gives (127, "", why). Its output goes to files, so a hook's child
        that keeps them open never holds spark. On a timeout it stops the group (`_stop`) and gives (None, "", UNFINISHED)."""
        own = {name: value for name, value in os.environ.items() if not name.startswith("GIT_") or name in KEPT}
        with tempfile.TemporaryFile("w+") as out, tempfile.TemporaryFile("w+") as err:
            try:
                run = subprocess.Popen(["git", "-C", str(self.project), *args], stdin=subprocess.DEVNULL, stdout=out,
                                       stderr=err, text=True, env=own, start_new_session=True)
            except OSError as missing:
                return 127, "", str(missing)
            try:
                code = run.wait(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                self._stop(run)
                return None, "", UNFINISHED
            out.seek(0)
            err.seek(0)
            return code, out.read().strip(), err.read().strip()

    def _stop(self, run):
        """SIGTERM to git's whole group, so git removes its own index.lock; then, after STOP_WAIT seconds at most, SIGKILL
        to what is left of the group (a hook that ignores SIGTERM, or its child), and wait for git."""
        os.killpg(run.pid, signal.SIGTERM)
        try:
            run.wait(timeout=STOP_WAIT)
        except subprocess.TimeoutExpired:
            pass
        try:
            os.killpg(run.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        run.wait()

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

    def tracks(self, name):
        """Whether git's index holds `name` (P1150): True or False, and None when git cannot say: no git, no repository, a
        folder git refuses, or a timeout. The index, not HEAD: a file added and not yet committed is tracked."""
        code = self._git("ls-files", "--error-unmatch", "--", "./" + name)[0]
        return {0: True, 1: False}.get(code)

    def tracked_files(self, patterns):
        """The files in git's index under the project that `patterns` cover, as paths from the project folder; [] when git
        cannot say. A pattern is a glob where `*` stays inside one folder, as in a `.gitignore`; one that ends in `/` covers
        everything below that folder."""
        specs = [":(glob)./" + (pattern + "**" if pattern.endswith("/") else pattern) for pattern in patterns]
        code, out, _ = self._git("ls-files", "-c", "-z", "--", *specs)
        return [name for name in out.split("\0") if name] if code == 0 else []

    def commit(self, name, message):
        """Commit `name` alone with `message`: (the short sha, None), or (None, git's first line, else its exit code) when git
        refuses, or (None, UNFINISHED). A missing identity is a refusal (`user.useConfigOnly`), never a guessed author. A
        commit git made before it was stopped or refused (a slow post-commit hook) is still the commit (`_landed`)."""
        before = self._git("rev-parse", "-q", "--verify", "HEAD")[1]
        code, out, err = self._git("-c", "user.useConfigOnly=true", "commit", "--quiet", "--only", "-m", message, "--", "./" + name)
        landed = self._landed(name, before) if code != 0 else self._git("rev-parse", "--short", "HEAD")[1]
        if landed or code is None:
            return landed, None if landed else UNFINISHED
        return None, (err or out).splitlines()[0] if err or out else "git exited with %d" % code

    def _landed(self, name, before):
        """The short sha of HEAD when HEAD moved from `before` and what it changes since is `name` alone; else None."""
        if not before or self._git("diff", "--name-only", before, "HEAD")[1] != self._git("rev-parse", "--show-prefix")[1] + name:
            return None
        return self._git("rev-parse", "--short", "HEAD")[1]
# --- end MVP ---
