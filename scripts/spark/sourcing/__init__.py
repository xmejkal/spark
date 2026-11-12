"""
The sourcing area (W6-S2 P717, W6-S3a P720): what the person owns and what spark knows about each part. It holds the
rules that judge a part record's facts (`part_rules`), the part records read and checked (`part_records`), the
matchers (`matching`), the cost of a run (`run_cost`) and the leaf `sourcing_codes`. The drawer and the datasheets come
with W6-S3b, the fifteen part Operations on the core with P726 PR 2 (one module each, on `part_operation.PartOperation`,
listed in `sourcing_operations`), and the CLIs `parts.py` and `cost.py` stay in `scripts/`. This file imports nothing, because an
`__init__` that imports its modules made the cycles of wave 5.
"""
