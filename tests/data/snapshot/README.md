# Snapshot fixtures

Small projects that `tools/snapshot.py` runs as part of every snapshot (P184, #133), so the baseline records how spark
answers on cases the three real projects do not reach. Each folder is a project: `boards/<id>.json` and
`boards/active.json`, and `requirements.json` when the chain should run too. Its `README.md` says where the case comes
from and what the baseline recorded.

A folder added here joins every later snapshot; against an older baseline it shows as "new in this snapshot". Change a
fixture only on purpose, and say in the card which recorded lines that changes.
