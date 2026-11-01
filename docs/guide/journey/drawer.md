## Drawer

**Partly.** [`/spark:drawer`](../../../commands/drawer.md) keeps what you own in your own store, never in a repository.

You say what you own in plain words. Claude writes the entries to a file and shows what would change:

```json
[
  {"label": "FireBeetle 2 ESP32-S3", "count": 1, "is": {"board": "firebeetle2-esp32s3"}},
  {"label": "red LEDs, pack of 10", "count": 10, "function": [{"does": "indicate", "what": "light"}]}
]
```

The conversation was not run for this page. These entries were written by hand; the commands below are real runs.

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --drawer-set ../drawer.json --dry-run
```

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  would add firebeetle-2-esp32-s3: FireBeetle 2 ESP32-S3 × 1 — is board firebeetle2-esp32s3
  would add red-leds-pack-of-10: red LEDs, pack of 10 × 10
```

Without `--dry-run` it writes them. Then the drawer lists them:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --drawer
```

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  FireBeetle 2 ESP32-S3                             1  board firebeetle2-esp32s3
  red LEDs, pack of 10                             10  —
  2 entries
```

Your DFRobot order history can also come in from your logged-in browser, through Claude in Chrome:

- Claude drives your Chrome on dfrobot.com/account/order.
- spark's extractor reads each order page there and hands back only each line's SKU, name and count: no page text,
  address or price.
- Two things are rules Claude follows from the drawer's page, not something code enforces: it reads the order pages no
  other way (no page text, no accessibility tree, no screenshot), and it never types credentials or solves a challenge.
- The same page also lets Claude adapt the extractor when DFRobot changes its pages.

This path was not run here.
