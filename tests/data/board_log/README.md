# A board log in the real layout (P1043)

`2026-11-23T14-09-49.log` is a board log as `deploy.py` writes it to `sim/runs/board/` after a flash, written by
`spark.bench.board_log.BoardLog` itself in the layout from before P1043's reason line. Every value is made up: the
port is a generic macOS name, the image and facts hashes are the sha256 of made-up bytes, and there is no MAC and no
home path. The sentence is the one the newest real log of the P934 walk held on 2026-11-23 (the P1043 plan's refuter
quoted it): `mpremote could not read the board's files: ...TransportError: could not enter raw repl`.

`tests/test_flow.py`'s `TheDeployReaderTest` copies it into a project, beside a newer log that holds markers, and
checks that no port, facts line, console text or tool text reaches `flow.py show`'s answer.
