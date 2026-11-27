# Gate A, for AI agents

Part of the [guide for AI agents](../agents.md) and of [where a project stands](flow.md).

Gate A is the condition before a permanent build (a perfboard, a PCB). It is not the deploy's gate. Its one condition today
is the free one ([P1220](https://github.com/xmejkal/spark/issues/1769), D10): no failed run on the current image. Its other
conditions are not built: the last deploy wrote the current image, and the person says it works. So spark can say that gate A is
shut. It never says that gate A is open.

`flow.py show --json` holds it as `data.guide.gate_a`, and the page prints it as the row TESTED BEFORE THE BOARD in the NOW box.
It is `null` before the On the board station: the deploy has no board log and is not now. From there on it is
`{shut_by, fact, says}`. `shut_by` is `["run-failed"]` while a run failed on the image `sim/wokwi.toml` names, `[]` when none
did, and `null` when spark cannot read the runs. `says` is the row's sentence: relay it as it is, and add no word of
permission. Spark reads `sim/runs/` and runs nothing, so the row costs no Wokwi minutes. It is data only: no code refuses
on it.

| `fact` | `shut_by` | What Claude does |
| --- | --- | --- |
| `run-failed` | `["run-failed"]` | Go through the failed log with the person before any permanent build. Gate A is shut. |
| `image-tested`, `image-older`, `image-untested`, `no-sim-files` | `[]` | Say the row. No failed run is seen, but gate A is not open: its other conditions are not built. |
| `no-model` | `[]` | Say the row. No simulator covers this board, and no failed run is seen on its default image. Gate A is not open. |
| `null` | `null` | Say that spark cannot tell, and read the simulation phase for why. Never fill the value in. |

An empty `shut_by` never means that gate A is open. A `null` `shut_by` means that spark cannot read the runs, not that none failed.

A board with no Wokwi model has no `sim/wokwi.toml` and keeps `sim/flash-with-firmware.bin`. Spark reads that image as `deploy.py` does. A failed run on it gives `run-failed`, and a log that cannot be read gives `null`, as the deploy refuses on both.

On any other board, a failed log of an image with no `sim/wokwi.toml` is not seen: `fact` is `no-sim-files` and `shut_by` is `[]`, though
`deploy.py --no-simulation` still refuses that image.
