# P213 b2: the bench walk, and the button places in the boot hint

| # | Row | Source | State | Note |
|---|-----|--------|-------|------|
| 1 | A new image needs a new look, because the token holds the image's sha256 prefix (ae7b-f34b, then ae7b-94b2): one extra board restart per redeploy | bench walk, 2026-10-19 | verified | by design |
| 2 | The erase retry and the download-mode hint did not fire, so AT313 stays untested | bench walk, 2026-10-19 | raised | a later walk |
| 3 | The doctor's two button steps and grant.py's esptool read also name BOOT and RESET | plan council, round 1 | acted | in scope |
| 4 | A changed fixture test: test_xiao_record.py compares the record's `physical` with a fixture | plan council, round 1 | acted | the fixture gets the field |
| 5 | The doctor's sentences are read by `describe` and `look_stop_envelope`, not by the service | plan council, round 2 | acted | one `step_sentence` |
| 6 | A shape check in `boards.py --validate` and the PortFinder plumbing are not needed for the card | plan council, round 2 | rejected | cut |
