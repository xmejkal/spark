"""
The flow area (P825): where a project stands, phase by phase from the idea to the deploy, read from the files each stage
wrote, so that a person and Claude move the project from one place (P820). `show_flow` holds the Operation, `phase_readers`
the nine readers and `flow_codes` the words. The CLI `flow.py` stays in `scripts/`. This file imports nothing, because an
`__init__` that imports its modules made the cycles of wave 5; the table of Operations is `flow_operations`.
"""
