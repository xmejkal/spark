"""
The sourcing area (W6-S2, P717): what the person owns and what spark knows about each part. So far it holds the rules
that judge a part record's facts (`part_rules`). The drawer, the matchers, the datasheets and the cost of a run come with
the sourcing moves (W6-S3a, W6-S3b), and the CLIs `parts.py` and `cost.py` stay in `scripts/`. This file imports
nothing, because an `__init__` that imports its modules made the cycles of wave 5.
"""
