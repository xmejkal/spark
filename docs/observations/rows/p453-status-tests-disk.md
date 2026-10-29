# P453 status tests and the disk line: findings rows

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Five status tests failed with under 10 GB free, because #608 added the `disk:` line and its review ran with more than 10 GB free | #611 | acted | every test that compares exact status output goes through `without_disk` |
