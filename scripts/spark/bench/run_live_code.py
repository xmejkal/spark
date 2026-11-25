"""
The live try as an Operation on the core (P657, W4-3): run a short piece of code on the running board inside a grant, say
whether the board ran it, and reset it. live.py is its CLI, and its `--json` line is the flat one with `fix` (`FixFlatJsonLine`):
every field of the LiveTryResult, the port and the fix (P1055). The status comes from `board_live.exit_code`, so a failed reset
stays exit 2 whatever the answer was; a stop has the same fields, empty, with the answer `could-not-run`.
"""

from spark.bench import board_codes
from spark.bench import board_doctor
from spark.bench import board_envelope
from spark.bench import board_grant
from spark.bench import board_live
from spark.bench import board_look
from spark.bench import known_board
from spark.records import board_records
from spark.records import tool_finder
from spark.bench.firmware_platform import MicroPythonPlatform
from spark.design.restricted_pins import BrokenRecordError
from spark.bench import bench_privacy
from spark.bench import stops
from spark.core import outcomes
from spark.core.errors import SparkError
from spark.core.renderers import FixFlatJsonLine
from spark.core.operation import ASKS, BOARD, COMMON_ARGUMENTS, READS, RUNS, Argument, Operation
from spark.core.result import Finding, OperationResult
from spark.core.text_guards import printable

# --- MVP ---
#: The lines of a stop name the script that printed them before the core, so they read the same from every frontend.
SCRIPT = "live.py"
REPLIES_HELP = ("your own file with the yes to the board question (P892): its true value lets live.py run the code on a board "
                "that spark cannot tell from another board. One yes is for one run")


def describe(result, places=board_records.ButtonPlaces.EMPTY):
    """The lines a person reads, for a LiveTryResult, each guarded (P430). `places` names the buttons the doctor's steps mention."""
    out = ["answer  %s" % result.answer]
    out += ["why     %s" % result.why] if result.why else []
    out += ["output  %s" % line for line in result.output.splitlines()]
    out += ["reset   %s" % result.reset] if result.reset else []
    out += ["pins    %s" % board_live.NO_RESTRICTED_PINS_MESSAGE] if not result.pins_checked else []
    if result.gpio_numbers_in_code:
        out.append("gpio    the code writes %s, each a GPIO of this board"
                   % ", ".join(str(gpio) for gpio in result.gpio_numbers_in_code))
    if result.doctor:
        out += board_doctor.describe(result.doctor, places)
    # P430: the board's reply and the doctor's lines are data, one line each
    return ["  " + printable(line) for line in out]


def data_of(port, result):
    """The data of a LiveTryResult, with the port: every field, null where it has none."""
    fields = result._asdict()
    fields["cure"] = result.cure._asdict() if result.cure is not None else None
    fields["doctor"] = board_doctor.as_dict(result.doctor) if result.doctor is not None else None
    return dict(fields, port=port)


#: What the live try does, the paragraphs of live.py's `--help` before its `--json` and exit codes, line breaks and
#: all (P855).
DETAILS = """live.py --code 'print(1)' runs the code on the board on USB with mpremote's exec, after two checks that do not
touch the board. First, the board must have a grant now: the person runs %s in their own terminal,
and live.py checks it with `mpremote devs` only. Second, the code must not write a number that the project's board
record names as a usb or flash pin (pin_roles), so time.sleep(12) is refused on a XIAO ESP32-C6 too. A refusal sends
nothing to the board.

If mpremote cannot enter the board's raw REPL, live.py cures the board once, as reach.py does, and tries again. When
it still cannot get in, it names both causes: a dead USB output, or firmware that does not read its console. The exec
stops the firmware that ran. So unless mpremote said it could not open the port or enter the raw REPL, live.py restarts the chip with
`mpremote reset`, even after code that never ends, and the firmware starts from boot. A pin that the code set and the firmware never sets
can keep its value through that reset (P252's bench), so live.py lists the GPIO numbers written in the code. That list
over-claims: print(1) lists GPIO1.

The board record is the project's board: the board requirements.json names, else boards/active.json's (P988). live.py
does not match that record against the board on USB. The board question below compares the board on USB with another
record: the board that spark keeps for the project in your store, which look.py writes.

After the two checks and just before the code runs, live.py asks the board question (P892). A board with no grant is
refused first, with no question. On the board that spark keeps for the project, known by its USB serial, it asks
nothing. Another board, told apart by its USB serial, stops with other_board, and a board with a USB serial in a
project that keeps no board stops with no_known_board. Both name look.py, and nothing ran on the board. A board that
spark cannot tell by its USB serial is asked on every run, in your terminal, or by --replies with your own file that
holds {"replies": {"live.run_on_board.<id>": true}}. With a grant that grant.py gave, that happens only while the kept
board's record trusts no USB serial (it showed none, or one that its firmware set) and the board on USB is on
Espressif's own USB with a serial that does not start with the kept MAC, for example a board granted in another
project: grant.py gives no live grant to a board with no serial. One yes or one no is for one run. A no is
answered_no, and nothing ran on the board. A --port that the list does not hold stops with port_not_listed, and a
/dev/tty. port is its /dev/cu. port.

If no board is on USB, or the port is not (the one you named, or the one spark found, after the doctor too), and
firmware/ calls deepsleep, the stop's last line, the fix, says that the board can be in deep sleep, as look.py's does
(P1057). Its first step puts the board in download mode. There it runs no firmware, so live.py cannot reach its REPL:
use download mode for look.py or a deploy, then press RESET with BOOT not held. To run code, wait until the firmware
wakes. --json carries the fix as `fix` (P1055), and `next` then holds the look step, which needs the person.

When mpremote cannot open the port or enter the board's REPL, the board doctor (P282) runs two checks: whether `mpremote devs` lists the
port, and two seconds of the console with the port's lock. It prints mpremote's own error, each check's fact,
and one next step for your hands, as the last line. Its look at the console can restart the board. --json carries it as doctor.""" % board_grant.GRANT_COMMAND


class RunLiveCode(Operation):
    """
    Operation: the live try. `platform_for(project, find_tool)` builds the FirmwarePlatform (default: MicroPythonPlatform).
    It lists the boards once and keeps the row, builds the LiveTryService over the grant check (the outside's clock), the
    connection, the probe and the board record, and runs it with the board question of the LIVE touch (P892, `known` the
    KnownBoardStore, None: the store's own), which the service asks just before the code runs. An answer that is no `ran`,
    or a reset that failed, is one Finding of the status of `board_live.exit_code`, with the answer for its code
    (`reset_failed` after a failed reset). A tool, the look, the board record, the kept board's record or the board
    question that stops is one unchecked item, and its data holds the empty fields. A stop of the board question adds
    `open`, `port`, `product` and `known_board`.
    """

    name = "live"
    summary = "Run a short piece of code on the running board inside a grant, say whether the board ran it, and reset it (P247)."
    details = DETAILS
    arguments = (Argument(("--code",), "code", str, "the code to run on the board, e.g. 'print(1)'", required=True),
                 COMMON_ARGUMENTS["project"]._replace(help="the project folder whose board (the board requirements.json names, else "
                                                      "boards/active.json's) is checked and whose tools list "
                                                      "names mpremote (default: here)"),
                 COMMON_ARGUMENTS["port"], COMMON_ARGUMENTS["json"]._replace(help="print one line of JSON"),
                 COMMON_ARGUMENTS["replies"]._replace(help=REPLIES_HELP))
    effects = (READS, RUNS, BOARD, ASKS)
    privacy_for = staticmethod(bench_privacy.privacy_for)
    json_renderer = FixFlatJsonLine

    def __init__(self, platform_for=None, known=None):
        self.platform_for = platform_for or MicroPythonPlatform
        self.board_question = known_board.KnownBoardService(known or known_board.KnownBoardStore(), known_board.LIVE)  # P892

    def run(self, code, project, port, replies=None, *, outside):
        platform = self.platform_for(project, outside.find_tool)
        empty, named = dict.fromkeys(board_live.LiveTryResult._fields), port
        try:
            finder = platform.make_port_finder(outside.run)
            row = finder.require_one_board(SCRIPT, port)  # P892: the row the board question judges
            port = port or row.device
            probe = platform.make_console_probe(port, outside.run)
            service = board_live.LiveTryService(board_grant.GrantService(finder, now=outside.clock.now),
                                                platform.make_connection(platform.make_shell_command(), port, outside.run, row.usb), probe,
                                                board_records.load(project),
                                                board_doctor.BoardDoctorService.for_board(finder, probe),
                                                platform.find_tool("board-shell"))
            result = service.run(code, port, board_question=lambda: self.board_question.require(project, named, row, outside.replies, replies))
        except known_board.BoardQuestionError as stopped:  # P892: after the pin check; the line names the question, the product and the kept board
            facts = board_live.pin_facts(code, service.board)
            return stops.question_result(stopped, SCRIPT, dict(empty, answer=outcomes.COULD_NOT_RUN, why=str(stopped), **facts, **stopped.data))
        except SparkError as unreadable:  # P892: the kept record or the replies file, read in the board question after the pin check
            return stops.stop_result(unreadable, SCRIPT, project, port)._replace(
                data=dict(empty, answer=outcomes.COULD_NOT_RUN, why=str(unreadable), port=port, **board_live.pin_facts(code, service.board)))
        except (tool_finder.ToolError, board_look.LookStopError, board_records.BoardError, BrokenRecordError) as cannot:
            # P1057: the asleep fix says "the port you named" only of the person's own port, so `named`, never the picked one
            stopped = stops.stop_result(cannot, SCRIPT, project, named, stops.undoctored(SCRIPT))
            return stopped._replace(data=dict(empty, answer=outcomes.COULD_NOT_RUN, why=stopped.findings[0].sentence, port=port))
        places = board_records.ButtonPlaces.of_project(project)
        # P1057 PR 2: after the doctor's plug_in step, the asleep fix of the port the person named or spark found, and the look
        said, fix = board_envelope.doctor_said(describe(result, places), result.doctor, named, project, places)
        return OperationResult(data_of(port, result), self._findings(result, fix), board_envelope.asleep_next(fix, project.resolve()),
                               lines=[printable(line) for line in said])

    @staticmethod
    def _findings(result, fix):
        """No Finding for a clean run; else one of the status of the exit code, coded by the answer or `reset_failed`, with
        `fix`, which board_envelope.doctor_said gave."""
        status = outcomes.STATUS_FOR[board_live.exit_code(result)]
        if status == outcomes.OK:
            return []
        code = board_codes.RESET_FAILED if result.reset == board_live.RESET_FAILED_STATE else result.answer
        return [Finding(status, None, code, result.why or result.answer, fix)]
# --- end MVP ---
