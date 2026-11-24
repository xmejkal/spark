"""
The research Operation on the core by the op it prints, for the Operation catalogue (P1077): `research.py --part` runs
`ResearchPart` (op `research-part`). It is its own table, not sourcing's, because sourcing's table is parts.py's flags.
"""

from spark.sourcing.research.research_part import ResearchPart

# --- MVP ---
OPERATIONS = {ResearchPart.name: ResearchPart}
# --- end MVP ---
