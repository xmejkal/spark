"""
The record of a deploy as an Operation on the core (P920, #1302): a registered project's own tool says that it deployed,
and spark's store adds one entry to the record of the board on USB. `bench.py record` is its CLI. It runs only
`mpremote devs`, which opens no port, and takes the MAC from the USB serial's own MAC part: a board whose serial holds no
MAC is not recorded, and no kept board is read, so a deploy never lands in another board's record.
"""

from spark.bench import bench_privacy
from spark.bench import board_codes
from spark.bench import board_look
from spark.bench import known_board
from spark.bench import ready_probe
from spark.bench.firmware_platform import MicroPythonPlatform
from spark.bench.stops import stop_result
from spark.core.errors import SparkError
from spark.core.operation import COMMON_ARGUMENTS, READS, RUNS, WRITES, Argument, Operation
from spark.core.result import OperationResult
from spark.core.text_guards import printable
from spark.records import records_codes
from spark.records import store
from spark.records import tool_finder
from spark.records.deploy_record_store import DeployRecordStore, outside_deploy
from spark.records.registered_project_store import RegisteredProjectStore

# --- MVP ---
SCRIPT = "bench.py"
NOTHING_WRITTEN = "Nothing was written."
NAME_HELP = "the name the project registered with bench.py register"
#: The fix of each stop that names no fix of its own: the next command, for the name.
AGAIN_FIX = "fix what the line above says, then run bench.py record %s again (with --port PORT when two boards are on USB)"
NO_MAC_FIX = "deploy this board with spark's deploy.py, which reads its MAC from the chip: bench.py record needs a serial that holds it"
RECORDED_LINE = "recorded: %s, made by %s, %s, on %s, MAC ends %s. No port was opened."


class RecordDeploy(Operation):
    """
    Operation: record one deploy of a registered project. `registered` and `records` are the RegisteredProjectStore and the
    DeployRecordStore (None: the store's own), and `platform_for(project, find_tool)` builds the FirmwarePlatform (default:
    MicroPythonPlatform), whose port finder alone it asks for. `--project` only finds the tools list. Each stop is one
    unchecked item, and nothing is written.
    """

    name = "record-deploy"
    summary = ("record one deploy of a registered project in spark's store, for the board on USB; it opens no port and reads "
               "nothing from the board")
    arguments = (Argument(("name",), "name", str, NAME_HELP, metavar="NAME"), COMMON_ARGUMENTS["port"],
                 COMMON_ARGUMENTS["project"]._replace(help="the folder whose tools list names mpremote (default: here; any folder runs)"),
                 COMMON_ARGUMENTS["json"])
    effects = (READS, RUNS, WRITES)
    data_keys = ("entry", "mac", "device")
    privacy_for = staticmethod(bench_privacy.privacy_for)

    def __init__(self, registered=None, records=None, platform_for=None):
        self.registered, self.records = registered or RegisteredProjectStore(), records or DeployRecordStore()
        self.platform_for = platform_for or MicroPythonPlatform

    def run(self, project, name, port=None, *, outside):
        try:
            registered = self.registered.read(name)
            if registered is None:
                raise SparkError("%s is not registered in spark's store. %s", name, NOTHING_WRITTEN, code=records_codes.NOT_REGISTERED,
                                 fix=records_codes.NOT_REGISTERED.fix % (name, name))
            finder = self.platform_for(project, outside.find_tool).make_port_finder(outside.run)
            row = finder.require_one_board("%s record %s" % (SCRIPT, name), port)
            mac = known_board.mac_part_of(row)
            if mac is None:
                raise SparkError("%s: %s, so its MAC is not known. %s", row.device, board_codes.CODES[board_codes.CANNOT_TELL_BOARD],
                                 NOTHING_WRITTEN, code=board_codes.CANNOT_TELL_BOARD, fix=NO_MAC_FIX)
            entry = outside_deploy(name, registered.tool, outside.clock.now().isoformat(timespec="seconds"), ready_probe.NOT_READ)
            self.records.append_deploy(mac, entry)
        except SparkError as refused:
            return stop_result(refused, SCRIPT, project, port)
        except (tool_finder.ToolError, board_look.LookStopError, store.StoreError) as cannot:
            return self._stopped(cannot, project, port, AGAIN_FIX % name)
        line = RECORDED_LINE % (name, registered.tool, entry["deployed"], row.device, known_board.mac_ends(mac))
        return OperationResult({"entry": entry, "mac": mac, "device": row.device}, lines=[printable(line)])

    @staticmethod
    def _stopped(cannot, project, port, fix):
        """stop_result's answer, with `fix` where the stop names none, and a last line that says nothing was written."""
        stopped = stop_result(cannot, SCRIPT, project, port)
        return stopped._replace(findings=[found._replace(fix=found.fix or fix) for found in stopped.findings],
                                diagnostics=list(stopped.diagnostics) + ["%s: %s %s" % (SCRIPT, NOTHING_WRITTEN, fix)])
# --- end MVP ---
