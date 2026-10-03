#!/usr/bin/env python3
"""Cost of one subagent run, read from its harness transcript (no network) — backlog P80.

The token count a finished agent's notification reports is its LAST turn's context, not what the run
processed: for the lean L-7113ID research it said 46,396 against ~0.55 M actually processed, and a
stopped run reports nothing. The harness's own transcript records every turn, so this reads that.
Written by the research council's cost lens on 2026-10-03; kept so every research run is measured the
same way. The transcript format is the harness's, not spark's, and may change.

Usage: research_cost.py <agent-*.jsonl> [--steps]
       (transcripts: ~/.claude/projects/<project>/<session>/subagents/agent-*.jsonl)

Prints: tool calls by tool, tool-result bytes by tool, model, token usage summed
over assistant turns (input / cache-creation / cache-read / output), and wall time
from first to last timestamp. --steps lists every tool call with its result size.
"""
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime


def parse_time(stamp):
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def result_text_bytes(content):
    if isinstance(content, str):
        return len(content.encode())
    total = 0
    for block in content or []:
        if block.get("type") == "text":
            total += len(block.get("text", "").encode())
        elif block.get("type") == "image":
            total += len(json.dumps(block).encode())
        else:
            total += len(json.dumps(block).encode())
    return total


def main():
    transcript = sys.argv[1]
    list_steps = "--steps" in sys.argv
    calls = Counter()
    result_bytes = defaultdict(int)
    tool_by_id = {}
    detail_by_id = {}
    usage = Counter()
    models = Counter()
    seen_message_ids = set()
    stamps = []
    steps = []
    with open(transcript) as handle:
        for line in handle:
            entry = json.loads(line)
            if entry.get("timestamp"):
                stamps.append(parse_time(entry["timestamp"]))
            message = entry.get("message") or {}
            if entry.get("type") == "assistant":
                message_id = message.get("id")
                if message_id not in seen_message_ids:
                    seen_message_ids.add(message_id)
                    for key, value in (message.get("usage") or {}).items():
                        if isinstance(value, int):
                            usage[key] += value
                    models[message.get("model")] += 1
                for block in message.get("content") or []:
                    if block.get("type") == "tool_use":
                        name = block["name"]
                        calls[name] += 1
                        tool_by_id[block["id"]] = name
                        arg = block.get("input", {})
                        detail_by_id[block["id"]] = (
                            arg.get("command") or arg.get("url") or arg.get("query")
                            or arg.get("file_path") or arg.get("pattern") or ""
                        )
            elif entry.get("type") == "user":
                for block in message.get("content") or [] if isinstance(message.get("content"), list) else []:
                    if block.get("type") == "tool_result":
                        name = tool_by_id.get(block.get("tool_use_id"), "?")
                        size = result_text_bytes(block.get("content"))
                        result_bytes[name] += size
                        steps.append((name, size, detail_by_id.get(block.get("tool_use_id"), "")))
    print("transcript:", transcript)
    print("models:", dict(models))
    print("assistant turns (unique message ids):", len(seen_message_ids))
    print("tool calls:", sum(calls.values()), dict(calls))
    print("tool-result bytes:", sum(result_bytes.values()), dict(result_bytes))
    for key in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"):
        print(f"{key}: {usage[key]}")
    if stamps:
        print("wall seconds:", round((max(stamps) - min(stamps)).total_seconds()))
    if list_steps:
        for name, size, detail in steps:
            print(f"  {name:10s} {size:>8d}  {str(detail)[:110]}")


if __name__ == "__main__":
    main()
