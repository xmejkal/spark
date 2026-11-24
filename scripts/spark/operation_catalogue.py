"""
The Operation catalogue (P1077, P793 piece 4): every OPERATIONS table, in the journey's order, as one map from the op
each prints to its class. It sits above the areas, outside the core: it imports their tables, and no module of the
core or of an area imports it (tests/test_operation_catalogue.py). A frontend hands it, or its slice, to the core's
DescribeOperations through the constructor. A later MCP server lists it.

Every entry builds with no argument, so a frontend that lists it needs nothing else, and a frontend that runs it hands
the area's outside builder. A dependency comes from the frontend through `outside`, or as a constructor keyword with a
harmless default (each entry builds with no argument and no SPARK_HOME, and writes nothing). DescribeOperations, which
needs a registry, is the one exception and is no entry.

The word is not parts.py's --catalog, catalog_records or CATALOG_KEYS: those are the part records research kept.
"""

from spark.bench import OPERATIONS as BENCH
from spark.build.build_operations import OPERATIONS as BUILD
from spark.checks.checks_operations import OPERATIONS as CHECKS
from spark.core.operation import FETCHES
from spark.design.design_operations import OPERATIONS as DESIGN
from spark.flow.flow_operations import OPERATIONS as FLOW
from spark.idea import OPERATIONS as IDEA
from spark.sourcing.research.research_operations import OPERATIONS as RESEARCH
from spark.sourcing.sourcing_operations import OPERATIONS as SOURCING

# --- MVP ---
#: Each table by the package under spark that holds it, in the journey's order (AGENTS.md).
TABLES = (("idea", IDEA), ("sourcing", SOURCING), ("sourcing.research", RESEARCH), ("design", DESIGN),
          ("build", BUILD), ("checks", CHECKS), ("bench", BENCH), ("flow", FLOW))
#: Every Operation on the core, by the op it prints. A name in two tables keeps only the later one, so the test counts.
CATALOGUE = {op: operation for _, table in TABLES for op, operation in table.items()}
#: The ops whose declared effects hold `fetches` (S2): they reach the network. parts.py --describe says `network`.
NETWORK = tuple(op for op, operation in CATALOGUE.items() if FETCHES in operation.effects)
# --- end MVP ---
