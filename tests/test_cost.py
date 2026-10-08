"""P97: what a project's run cost, from its session transcripts (docs/2026-10-04-store-design.md §6.7, §8 T)."""

import contextlib
import datetime
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import cost  # noqa: E402
import parts  # noqa: E402


def assistant(when, *tools, usage=None, message_id=None):
    """One assistant turn of a transcript, as the harness writes it: its time, its tool calls, its usage."""
    return {"type": "assistant", "timestamp": when,
            "message": {"id": message_id or when, "usage": usage or {},
                        "content": [{"type": "tool_use", "name": name, "input": given} for name, given in tools]}}


def run(argv):
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
        code = parts.main(argv + ["--json"])
    return json.loads(out.getvalue()), code


class WhatATranscriptSaysTest(unittest.TestCase):
    """§6.7's counts, from transcript entries: names and counts, never arguments."""

    def test_what_reached_the_network_what_ran_and_what_was_read(self):
        counted = cost.count([assistant(
            "2026-10-06T10:01:00Z", ("WebSearch", {"query": "q"}), ("WebFetch", {"url": "https://v.example/"}),
            ("mcp__plugin_spark_jlcpcb__component_search", {"query": "jst"}),
            ("Bash", {"command": "curl -sO https://v.example/a.pdf"}), ("Bash", {"command": "python3 scripts/parts.py --sources x-part"}),
            ("Bash", {"command": "ls -la"}), ("Read", {"file_path": "/s/a.PDF"}), ("Read", {"file_path": "/s/a.PDF"}),
            ("Read", {"file_path": "/s/notes.md"}), ("Bash", {"command": "python3 scripts/parts.py --read /s/b.pdf --want x"}),
            ("Agent", {"subagent_type": "spark:part-finder"}))])
        self.assertEqual((counted["requests"], counted["documents"], counted["runs"]), (5, 2, {"spark:part-finder": 1}))
        self.assertEqual(counted["by_tool"], {"WebSearch": 1, "WebFetch": 1, "mcp__plugin_spark_jlcpcb__component_search": 1, "Bash": 2})

    def test_new_tokens_leave_out_cache_reads_and_a_turn_is_counted_once(self):
        usage = {"input_tokens": 10, "cache_creation_input_tokens": 100, "cache_read_input_tokens": 5000, "output_tokens": 7}
        self.assertEqual(cost.count([assistant("2026-10-06T10:01:00Z", usage=usage, message_id="m1"),
                                     assistant("2026-10-06T10:01:01Z", usage=usage, message_id="m1")])["tokens"], 117)

    def test_one_transcript_is_answered_on_its_own(self):
        path = Path(tempfile.mkdtemp()) / "agent-x.jsonl"
        path.write_text("".join(json.dumps(entry) + "\n" for entry in (
            assistant("2026-10-06T10:00:00Z", ("WebFetch", {"url": "u"})), assistant("2026-10-06T10:06:00Z", ("Read", {"file_path": "/d.pdf"})))))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cost.main([str(path)]), 0)
        self.assertIn("requests  1", out.getvalue())
        self.assertIn("minutes   6", out.getvalue())


class TheCostLineTest(unittest.TestCase):
    """§6.7, §8 T: each step of the project, its session's transcripts inside the step's window, one line at the end."""

    PICKS = {"soil": [{"part": "x-soil"}], "alarm": [{"part": "x-amp"}, {"entry": "speaker"}],
             "board": [{"board": "firebeetle2-esp32s3"}], "battery": [{"entry": "lipo"}]}

    def setUp(self):
        self.home, self.claude = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        self.project = Path(tempfile.mkdtemp()) / "plant-alarm"
        (self.project / ".spark").mkdir(parents=True)
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home), "HOME": str(self.claude)})
        patcher.start()
        self.addCleanup(patcher.stop)
        (self.home / "drawer").mkdir()
        for key, entry in {"probe": {"label": "soil probe", "count": 8, "is": {"part": "x-soil"}},
                           "amp": {"label": "an I2S amp", "count": 2, "is": {"part": "x-amp"}},
                           "speaker": {"label": "3 W speaker", "count": 2},
                           "board": {"label": "FireBeetle", "count": 1, "is": {"board": "firebeetle2-esp32s3"}},
                           "lipo": {"label": "1S LiPo", "count": 1}}.items():
            (self.home / "drawer" / (key + ".json")).write_text(json.dumps(dict({"schema": 1}, **entry)))
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [
            {"id": need, "does": "sense", "what": "x", "pick": pick} for need, pick in self.PICKS.items()]}))
        (self.home / "projects.json").write_text(json.dumps({"plant-alarm": str(self.project.resolve())}))
        self.history([dict({"event": "reused", "project": "plant-alarm", "need": need}, **pick)
                      for need, chosen in self.PICKS.items() for pick in chosen])

    def history(self, events):
        with (self.home / "history.jsonl").open("a") as history:
            history.writelines(json.dumps(event) + "\n" for event in events)

    def step(self, session, start, project="plant-alarm"):
        self.history([{"event": "step", "project": project, "step": "C", "session": session, "start": start}])

    def transcript(self, session, *entries):
        folder = self.claude / ".claude" / "projects" / "-Users-someone-plant-alarm"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / (session + ".jsonl")).write_text("".join(json.dumps(entry) + "\n" for entry in entries))

    def test_the_line_counts_a_step_s_requests_documents_and_minutes(self):
        self.step("s1", "2026-10-06T10:00:00+00:00")
        self.transcript("s1", assistant("2026-10-06T09:59:00Z", ("WebFetch", {"url": "https://before.example/"})),
                        assistant("2026-10-06T10:01:00Z", ("Bash", {"command": "python3 scripts/parts.py --fetch max98357a-dfr0954"})),
                        assistant("2026-10-06T10:02:00Z", ("Read", {"file_path": "/store/sources/ab/drawing.pdf"})),
                        assistant("2026-10-06T10:14:00Z", ("Bash", {"command": "python3 scripts/parts.py --tally ."})))
        said, code = run(["--tally", str(self.project)])
        self.assertEqual((code, said["data"]["line"]), (0, "5 picks: 5 from the store (5 owned) — 1 request, 1 document, 14 min"))

    def test_a_subagent_s_work_inside_the_window_counts(self):
        self.step("s1", "2026-10-06T10:00:00+00:00")
        self.transcript("s1", assistant("2026-10-06T10:10:00Z", ("Bash", {"command": "ls"})))
        folder = self.claude / ".claude" / "projects" / "-Users-someone-plant-alarm" / "s1" / "subagents"
        folder.mkdir(parents=True)
        (folder / "agent-a1.jsonl").write_text(json.dumps(assistant("2026-10-06T10:05:00Z", ("WebSearch", {"query": "q"}))) + "\n")
        self.assertEqual(run(["--tally", str(self.project)])[0]["data"]["cost"]["requests"], 1)

    def test_a_step_ends_where_the_next_step_of_its_session_starts(self):
        self.step("s1", "2026-10-06T10:00:00+00:00")
        self.step("s1", "2026-10-06T10:05:00+00:00", project="rc-car")
        self.transcript("s1", assistant("2026-10-06T10:01:00Z", ("WebFetch", {"url": "u"})),
                        assistant("2026-10-06T10:06:00Z", ("WebFetch", {"url": "v"})))
        counted = run(["--tally", str(self.project)])[0]["data"]["cost"]
        self.assertEqual((counted["requests"], counted["minutes"]), (1, 5))

    def test_no_transcript_is_could_not_run_never_zero(self):
        self.step("gone", "2026-10-06T10:00:00+00:00")
        said, code = run(["--tally", str(self.project)])
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertEqual(said["data"]["line"], "5 picks: 5 from the store (5 owned) — its cost was not counted")

    def test_a_pick_the_drawer_does_not_hold_is_not_owned(self):
        (self.home / "drawer" / "lipo.json").unlink()
        self.step("s1", "2026-10-06T10:00:00+00:00")
        self.transcript("s1", assistant("2026-10-06T10:01:00Z"))
        self.assertTrue(run(["--tally", str(self.project)])[0]["data"]["line"].startswith("5 picks: 5 from the store (4 owned)"))

    def test_a_pick_with_no_reused_line_is_not_from_the_store(self):
        lines = (self.home / "history.jsonl").read_text().splitlines()
        (self.home / "history.jsonl").write_text("".join(line + "\n" for line in lines if '"lipo"' not in line))
        self.step("s1", "2026-10-06T10:00:00+00:00")
        self.transcript("s1", assistant("2026-10-06T10:01:00Z"))
        self.assertTrue(run(["--tally", str(self.project)])[0]["data"]["line"].startswith("5 picks: 4 from the store (5 owned)"))


class TheStepTest(unittest.TestCase):
    """§5.7, §6.7: a step is one line when it starts — its project, its letter, its session, its start."""

    def setUp(self):
        self.home, self.project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "plant-alarm"
        (self.project / ".spark").mkdir(parents=True)
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_step_says_its_session_and_when_it_started(self):
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": "s9"}):
            _, code = run(["--step", str(self.project), "C"])
        event = json.loads((self.home / "history.jsonl").read_text().splitlines()[-1])
        self.assertEqual((code, event["event"], event["project"], event["step"], event["session"]), (0, "step", "plant-alarm", "C", "s9"))

    def test_a_step_outside_claude_code_says_its_cost_cannot_be_counted(self):
        out = io.StringIO()
        with mock.patch.dict(os.environ), contextlib.redirect_stdout(out):
            os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
            parts.main(["--step", str(self.project), "C"])
        self.assertIn("no Claude Code session here", out.getvalue())

    def test_a_step_is_one_of_the_spine_s_letters(self):
        said, code = run(["--step", str(self.project), "X"])
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertFalse((self.home / "history.jsonl").exists())

    def test_a_dry_run_of_a_step_writes_nothing(self):
        said, code = run(["--step", str(self.project), "C", "--dry-run"])
        self.assertEqual((code, said["data"]["written"]), (0, False))
        self.assertFalse((self.home / "history.jsonl").exists())


class AStepStartsWhenItIsMarkedTest(unittest.TestCase):
    """§2, §5.7: a step line says when it started — the moment it was marked, with its zone — and every letter of the spine may be marked."""

    def setUp(self):
        self.home, self.project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "plant-alarm"
        self.project.mkdir()
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home), "CLAUDE_CODE_SESSION_ID": "s9"})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_step_starts_at_the_moment_it_is_marked(self):
        before = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        run(["--step", str(self.project), "M"])
        after = datetime.datetime.now(datetime.timezone.utc)
        started = datetime.datetime.fromisoformat(json.loads((self.home / "history.jsonl").read_text())["start"])
        self.assertTrue(before <= started <= after, started)

    def test_every_letter_of_the_spine_is_a_step(self):
        for letter in "SMCGLTIFR":
            with self.subTest(letter=letter):
                said, code = run(["--step", str(self.project), letter, "--dry-run"])
                self.assertEqual((code, said["data"]["step"]["step"]), (0, letter))

    def test_a_step_says_what_it_started_or_would_start(self):
        for argv, said in ((["--step", str(self.project), "L"], "started step L of plant-alarm"),
                           (["--step", str(self.project), "L", "--dry-run"], "would start step L of plant-alarm")):
            with self.subTest(argv=argv):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    self.assertEqual(parts.main(argv), 0)
                self.assertEqual(out.getvalue().strip(), said)


class AScratchStore(unittest.TestCase):
    """A scratch store and a scratch ~/.claude, and a listed project "plant-alarm" with no picks: what the tests below share."""

    STEP = {"event": "step", "project": "plant-alarm", "step": "C", "session": "s1", "start": "2026-10-06T10:00:00+00:00"}

    def setUp(self):
        self.home, self.claude = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        self.project = Path(tempfile.mkdtemp()) / "plant-alarm"
        self.project.mkdir()
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home), "HOME": str(self.claude)})
        patcher.start()
        self.addCleanup(patcher.stop)
        (self.home / "projects.json").write_text(json.dumps({"plant-alarm": str(self.project.resolve())}))

    def history(self, *events):
        (self.home / "history.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events))

    def transcript(self, session, *lines):
        folder = self.claude / ".claude" / "projects" / "-Users-someone-plant-alarm"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / (session + ".jsonl")).write_text("".join(line + "\n" for line in lines))

    def fetch_at(self, when):
        return json.dumps(assistant(when, ("WebFetch", {"url": "u"})))


class TheWindowOfAStepTest(AScratchStore):
    """§6.7: a step lasts until the next step of ITS OWN session starts — a step of another session, running beside it, does not end it."""

    def test_a_step_of_another_session_does_not_end_the_window(self):
        self.history(self.STEP, dict(self.STEP, project="rc-car", session="s2", start="2026-10-06T10:05:00+00:00"))
        self.transcript("s1", self.fetch_at("2026-10-06T10:01:00Z"), self.fetch_at("2026-10-06T10:06:00Z"))
        counted = run(["--tally", str(self.project)])[0]["data"]["cost"]
        self.assertEqual((counted["requests"], counted["minutes"]), (2, 6))

    def test_two_steps_of_a_project_in_one_session_are_each_counted_in_their_own_window(self):
        self.history(self.STEP, dict(self.STEP, step="L", start="2026-10-06T10:05:00+00:00"))
        self.transcript("s1", self.fetch_at("2026-10-06T09:59:00Z"), self.fetch_at("2026-10-06T10:01:00Z"),
                        self.fetch_at("2026-10-06T10:06:00Z"), self.fetch_at("2026-10-06T10:09:00Z"))
        counted = run(["--tally", str(self.project)])[0]["data"]["cost"]
        self.assertEqual((counted["requests"], counted["minutes"]), (3, 9))

    def test_two_steps_of_a_project_that_start_together_are_counted_once(self):
        self.history(self.STEP, dict(self.STEP, step="L"))
        self.transcript("s1", self.fetch_at("2026-10-06T10:01:00Z"))
        counted = run(["--tally", str(self.project)])[0]["data"]["cost"]
        self.assertEqual((counted["requests"], counted["minutes"]), (1, 1))


class WhatIsCountedTest(unittest.TestCase):
    """§6.7: the shell patterns that reach the network, and the agent runs, as the table names them."""

    def test_every_shell_pattern_that_reaches_the_network_counts(self):
        counted = cost.count([assistant("2026-10-06T10:01:00Z", ("Bash", {"command": "wget -q https://v.example/a"}),
                                        ("Bash", {"command": "gh api repos/x/y"}), ("Bash", {"command": "git status"}))])
        self.assertEqual((counted["requests"], counted["by_tool"]), (2, {"Bash": 2}))

    def test_an_agent_run_is_counted_by_its_type_and_a_general_one_by_its_name(self):
        counted = cost.count([assistant("2026-10-06T10:01:00Z", ("Task", {"subagent_type": "spark:part-finder"}),
                                        ("Agent", {}), ("Agent", {"subagent_type": "spark:part-finder"}))])
        self.assertEqual(counted["runs"], {"spark:part-finder": 2, "general-purpose": 1})


class WhatCannotBeReadIsSaidNeverATracebackTest(AScratchStore):
    """
    The transcript is the harness's format and may change, a session's last line may be half written while it is live, and
    the history can be edited by hand: what spark cannot read is counted or named, and the answer is still an envelope.
    """

    def test_a_line_that_is_no_json_object_is_left_out_and_counted(self):
        self.history(self.STEP)
        self.transcript("s1", self.fetch_at("2026-10-06T10:01:00Z"), "[1, 2]", "", self.fetch_at("2026-10-06T10:02:00Z")[:30])
        said, code = run(["--tally", str(self.project)])
        counted = said["data"]["cost"]
        self.assertEqual((code, counted["requests"], counted["unreadable_lines"]), (0, 1, 2))

    def test_the_unreadable_lines_are_said_in_words_too(self):
        self.history(self.STEP)
        for unreadable, said in ((["{not json"], "1 line of the transcripts could not be read and is left out of the count"),
                                 (["{not json", "[1]"], "2 lines of the transcripts could not be read and are left out of the count")):
            with self.subTest(unreadable=unreadable):
                self.transcript("s1", self.fetch_at("2026-10-06T10:01:00Z"), *unreadable)
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    code = parts.main(["--tally", str(self.project)])
                self.assertEqual(code, 0)
                self.assertIn(said, out.getvalue())

    def test_a_tally_with_every_line_readable_says_nothing_of_lines(self):
        self.history(self.STEP)
        self.transcript("s1", self.fetch_at("2026-10-06T10:01:00Z"))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--tally", str(self.project)])
        self.assertNotIn("could not be read", out.getvalue())

    def test_a_session_that_held_two_steps_is_read_once_and_its_unreadable_lines_counted_once(self):
        self.history(self.STEP, dict(self.STEP, step="L", start="2026-10-06T10:05:00+00:00"))
        self.transcript("s1", self.fetch_at("2026-10-06T10:01:00Z"), "{not json", self.fetch_at("2026-10-06T10:06:00Z"))
        with mock.patch.object(Path, "read_text", autospec=True, side_effect=Path.read_text) as reading:
            counted = run(["--tally", str(self.project)])[0]["data"]["cost"]
        self.assertEqual((counted["requests"], counted["unreadable_lines"]), (2, 1))
        self.assertEqual([call.args[0].name for call in reading.call_args_list].count("s1.jsonl"), 1)

    def test_a_time_naming_no_zone_is_left_out_not_a_traceback(self):
        self.history(self.STEP)
        self.transcript("s1", self.fetch_at("2026-10-06T10:01:00"), self.fetch_at("2026-10-06T10:02:00Z"))
        said, code = run(["--tally", str(self.project)])
        self.assertEqual((code, said["data"]["cost"]["requests"]), (0, 1))

    def test_one_transcript_with_a_time_naming_no_zone_is_answered_too(self):
        path = Path(tempfile.mkdtemp()) / "agent-x.jsonl"
        path.write_text(self.fetch_at("2026-10-06T10:00:00") + "\n" + self.fetch_at("2026-10-06T10:06:00Z") + "\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cost.main([str(path)]), 0)
        self.assertIn("requests  2", out.getvalue())
        self.assertIn("minutes   0", out.getvalue())

    def test_one_transcript_says_how_many_lines_it_could_not_read(self):
        path = Path(tempfile.mkdtemp()) / "agent-x.jsonl"
        path.write_text(self.fetch_at("2026-10-06T10:00:00Z") + "\n{not json\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cost.main([str(path)]), 0)
        self.assertIn("unreadable_lines 1", out.getvalue())

    def test_one_transcript_that_cannot_be_opened_is_named_not_a_traceback(self):
        path = Path(tempfile.mkdtemp()) / "agent-x.jsonl"
        path.write_text("{}\n")
        err = io.StringIO()
        with mock.patch.object(Path, "read_text", side_effect=PermissionError("denied")), contextlib.redirect_stderr(err):
            self.assertEqual(cost.main([str(path)]), 2)
        self.assertIn("cost.py: denied", err.getvalue())

    def test_a_transcript_naming_no_time_spark_can_read_is_could_not_run_never_zero(self):
        self.history(self.STEP)
        for lines in ([], [json.dumps({"type": "assistant", "when": "2026-10-06T10:01:00Z", "message": {"id": "m", "content": []}})],
                      ["{not json"], [json.dumps(assistant("soon", ("WebFetch", {"url": "u"})))]):
            with self.subTest(lines=lines):
                self.transcript("s1", *lines)
                said, code = run(["--tally", str(self.project)])
                self.assertEqual((said["status"], code), ("could-not-run", 2))
                self.assertEqual(said["data"]["line"], "0 picks: 0 from the store (0 owned) — its cost was not counted")
                self.assertEqual(said["unchecked"][0]["sentence"],
                                 "the transcripts of session s1 name no time spark can read, so the cost of its steps is not known")

    def test_a_step_line_with_no_readable_start_is_could_not_run_naming_it(self):
        for broken in ({"event": "step", "project": "plant-alarm", "step": "C", "session": "s1"},
                       dict(self.STEP, start="soon"), dict(self.STEP, start="2026-10-06T10:00:00"),
                       {"event": "step", "project": "rc-car", "step": "S", "session": "s1"}):
            with self.subTest(broken=broken):
                self.history(self.STEP, broken)
                self.transcript("s1", self.fetch_at("2026-10-06T10:01:00Z"))
                said, code = run(["--tally", str(self.project)])
                self.assertEqual((said["status"], code), ("could-not-run", 2))
                self.assertIn("has no start spark can read as a time", said["unchecked"][0]["sentence"])

    def test_a_step_marked_in_no_session_says_so_and_does_not_call_it_none(self):
        self.history(dict(self.STEP, session=None))
        said, code = run(["--tally", str(self.project)])
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertEqual(said["unchecked"][0]["sentence"],
                         "a step of plant-alarm was marked in no Claude Code session, so its cost cannot be counted")

    def test_a_project_no_step_names_is_not_called_none(self):
        said, code = run(["--tally", str(self.project / "elsewhere")])
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertEqual(said["unchecked"][0]["sentence"],
                         "no step of this project is in the history — `parts.py --step <project> <step>` marks each")

    def test_the_reason_a_cost_was_not_counted_is_said_in_words_too(self):
        self.history(dict(self.STEP, session="gone"))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = parts.main(["--tally", str(self.project)])
        self.assertEqual(code, 2)
        self.assertIn("its cost was not counted", out.getvalue())
        self.assertIn("no transcript of session gone here, so the cost of its steps is not known", out.getvalue())

    def test_a_turn_shaped_oddly_is_counted_for_what_it_holds_not_a_traceback(self):
        oddly = [assistant("2026-10-06T10:01:00Z", usage="oops"),
                 {"type": "assistant", "timestamp": "2026-10-06T10:02:00Z",
                  "message": {"id": "m2", "usage": {"input_tokens": "5", "output_tokens": 7}, "content": 5}},
                 {"type": "assistant", "timestamp": "2026-10-06T10:03:00Z",
                  "message": {"id": "m3", "usage": None, "content": [None, "text", {"type": "tool_use", "name": "WebFetch", "input": None}]}}]
        counted = cost.count(oddly)
        self.assertEqual((counted["requests"], counted["tokens"]), (1, 7))


if __name__ == "__main__":
    unittest.main()
