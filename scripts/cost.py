#!/usr/bin/env python3
"""
What a project's run cost, read from the session transcripts (P97; docs/2026-10-04-store-design.md §6.7).

Each spine step of a project is a `step` line in the store's history: the session it ran in and when it started. A step
lasts until the next step of the same session starts — of any project — or to that session's last line. The counter
reads the main and the subagent transcripts of each step's session inside its window, and counts what reached the
network (a table of tool names and shell patterns), the runs of each agent type, the documents read, the new tokens
apart from cache reads, and the minutes. It keeps tool names and counts, never arguments. No transcript is
could-not-run, never 0: the harness keeps transcripts for a while, not for ever. The transcript is the harness's format,
not spark's, and may change: a line that is no JSON object (one half written while the session is live, say) is left out
and counted, and a turn shaped oddly is counted for what it holds — never a traceback. This replaced
tools/research_cost.py (W16), and still answers for one transcript:

    cost.py <transcript.jsonl>      what one run cost — a research agent's, for instance
"""

import collections
import datetime
import json
import os
import re
import sys
from pathlib import Path

from outcomes import EXIT_OK, EXIT_COULD_NOT_RUN

#: What reaches the network (§6.7): these tools, every MCP server's tools, and a shell command that names one of these.
NETWORK_TOOLS = ("WebSearch", "WebFetch")
NETWORK_SHELL = re.compile(r"\b(curl|wget)\b|\bgh api\b|--(fetch|sources)\b")
#: What reading a document is: the Read tool, or `parts.py --read`, on one of these.
DOCUMENTS = (".pdf", ".png", ".jpg", ".jpeg", ".webp", ".svg")
#: A project's spine steps (§2): shape, match, choose, research the gap, the part list, the tally; ideas, fit, revive.
STEPS = ("S", "M", "C", "G", "L", "T", "I", "F", "R")
#: Earlier than any transcript: the lower bound for a window that has none.
EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)


class NoTranscript(Exception):
    """A cost that is not known: no step, a step line spark cannot read, no session, or no transcript of it here. Could-not-run, never 0."""


def _when(stamp):
    """The moment a timestamp of a transcript or of the history names; ValueError when it is no time, or names no time zone."""
    moment = datetime.datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
    if moment.tzinfo is None:
        raise ValueError("%r names no time zone" % (stamp,))
    return moment


def _start_of(step):
    """When a step line says it started. NoTranscript when it says nothing spark can read as a time: its window is not known."""
    try:
        return _when(step["start"])
    except (KeyError, ValueError):
        raise NoTranscript("a step line in your history (project %r, step %r) has no start spark can read as a time — fix it by hand"
                           % (step.get("project"), step.get("step"))) from None


def step_event(project, step):
    """The history line a step starts with (§5.7): which project and step, the Claude Code session it runs in, and when."""
    return {"event": "step", "project": project, "step": step, "session": os.environ.get("CLAUDE_CODE_SESSION_ID"),
            "start": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}


def transcripts(session, root=None):
    """The main and the subagent transcripts of one session, wherever the harness filed them."""
    root = Path(root) if root else Path.home() / ".claude" / "projects"
    return sorted(root.glob("*/%s.jsonl" % session)) + sorted(root.glob("*/%s/subagents/*.jsonl" % session))


def _read(paths):
    """
    (entries, unreadable): the JSON object on each line of the transcripts, and how many lines were no JSON object — one half
    written while the session is live, say. A blank line is neither. Left out and counted, so the cost line never rests on a
    line it silently dropped.
    """
    entries, unreadable = [], 0
    for path in paths:
        for text in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not text.strip():
                continue
            try:
                entry = json.loads(text)
            except ValueError:
                entry = None
            if isinstance(entry, dict):
                entries.append(entry)
            else:
                unreadable += 1
    return entries, unreadable


def _inside(entry, start, end):
    """Whether a transcript entry's own time falls in the window [start, end) — end None is open. No readable time is in no window."""
    try:
        when = _when(entry.get("timestamp"))
    except ValueError:
        return False
    return start <= when and (end is None or when < end)


def _number(value):
    """A token count the transcript gives, or 0 when it gives something else: the format is the harness's, not spark's."""
    return value if isinstance(value, int) else 0


def count(entries):
    """What a run of transcript entries did (§6.7): {requests, by_tool, runs, documents, tokens} — names and counts only."""
    by_tool, runs, documents, seen, tokens = collections.Counter(), collections.Counter(), set(), set(), 0
    for entry in entries:
        message = entry.get("message")
        if entry.get("type") != "assistant" or not isinstance(message, dict):
            continue
        if message.get("id") is None or message["id"] not in seen:
            seen.add(message.get("id"))
            usage = message.get("usage") if isinstance(message.get("usage"), dict) else {}
            tokens += sum(_number(usage.get(key)) for key in ("input_tokens", "cache_creation_input_tokens", "output_tokens"))
        blocks = message.get("content")
        for block in blocks if isinstance(blocks, list) else []:
            if not (isinstance(block, dict) and block.get("type") == "tool_use"):
                continue
            name, given = str(block.get("name")), block.get("input") if isinstance(block.get("input"), dict) else {}
            command = str(given.get("command") or "") if name.lower() == "bash" else ""
            if name in NETWORK_TOOLS or name.startswith("mcp__") or NETWORK_SHELL.search(command):
                by_tool[name] += 1
            if name in ("Agent", "Task"):
                runs[str(given.get("subagent_type") or "general-purpose")] += 1
            reading = re.search(r"--read\s+(\S+)", command)
            read = given.get("file_path") if name == "Read" else (reading.group(1) if reading else None)
            if isinstance(read, str) and read.lower().endswith(DOCUMENTS):
                documents.add(read)
    return {"requests": sum(by_tool.values()), "by_tool": dict(by_tool), "runs": dict(runs), "documents": len(documents),
            "tokens": tokens}


def windows(steps, project):
    """
    (session, start, end or None) of each of a project's steps (§6.7): a step ends where the next step of its session starts.
    Two steps of a project that start at the same moment have the one window, which is counted once.
    """
    said = []
    for step in steps:
        if step.get("project") == project:
            start = _start_of(step)
            later = [_start_of(other) for other in steps
                     if other.get("session") == step.get("session") and _start_of(other) > start]
            said.append((step.get("session"), start, min(later) if later else None))
    return [window for number, window in enumerate(said) if window not in said[:number]]  # steps that start together share one


def cost(steps, project, root=None):
    """
    What a project's steps cost (§6.7): `count` over every step's window, the minutes the windows span, and how many
    transcript lines could not be read (each session is read once, however many steps it held). NoTranscript — never a 0 —
    when no step was recorded, a step line cannot be read, a step has no session, or its session's transcript is not here or
    names no time spark can read (the harness's format may change, and a cost of 0 must never be what a change looks like).
    """
    found = windows(steps, project)
    if not found:
        raise NoTranscript("no step of %s is in the history — `parts.py --step <project> <step>` marks each" % (project or "this project"))
    inside, minutes, read = [], 0.0, {}
    for session, start, end in found:
        if not session:
            raise NoTranscript("a step of %s was marked in no Claude Code session, so its cost cannot be counted" % project)
        paths = transcripts(session, root)
        if not paths:
            raise NoTranscript("no transcript of session %s here, so the cost of its steps is not known" % session)
        if session not in read:
            read[session] = _read(paths)
            if not any(_inside(entry, EPOCH, None) for entry in read[session][0]):
                raise NoTranscript("the transcripts of session %s name no time spark can read, so the cost of its steps is not known" % session)
        here = [entry for entry in read[session][0] if _inside(entry, start, end)]
        inside += here
        minutes += ((end or max([_when(entry["timestamp"]) for entry in here], default=start)) - start).total_seconds() / 60
    return dict(count(inside), minutes=round(minutes), unreadable_lines=sum(bad for _, bad in read.values()))


def line(picks, from_store, owned, counted):
    """The cost line (§6.7): "5 picks: 5 from the store (5 owned) — 1 request, 1 document, 14 min"."""
    said = "%d pick%s: %d from the store (%d owned)" % (picks, "" if picks == 1 else "s", from_store, owned)
    if counted is None:
        return said + " — its cost was not counted"
    return said + " — %d request%s, %d document%s, %d min" % (
        counted["requests"], "" if counted["requests"] == 1 else "s", counted["documents"],
        "" if counted["documents"] == 1 else "s", counted["minutes"])


def unreadable_note(counted):
    """The sentence that goes with the line when transcript lines could not be read, or None when every line could be."""
    bad = (counted or {}).get("unreadable_lines", 0)
    if not bad:
        return None
    return "%d line%s of the transcripts could not be read and %s left out of the count" % (
        bad, "" if bad == 1 else "s", "is" if bad == 1 else "are")


def main(argv=None):
    given = sys.argv[1:] if argv is None else list(argv)
    if len(given) != 1 or not Path(given[0]).is_file():
        print("usage: cost.py <transcript.jsonl> — what one run cost, from its transcript", file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    try:
        entries, unreadable = _read([Path(given[0])])
    except OSError as cannot:
        print("cost.py: %s" % cannot, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    counted = count(entries)
    stamps = sorted(_when(entry["timestamp"]) for entry in entries if _inside(entry, EPOCH, None))
    counted["minutes"] = round((stamps[-1] - stamps[0]).total_seconds() / 60) if stamps else 0
    for key in ("requests", "by_tool", "runs", "documents", "tokens", "minutes"):
        print("%-9s %s" % (key, counted[key]))
    if unreadable:
        print("%-9s %s" % ("unreadable_lines", unreadable))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
