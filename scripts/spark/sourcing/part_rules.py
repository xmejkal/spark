"""
The rules that judge a part record's facts (W6-S2, P717). So far the pull-up band, which a module's own I2C pull-up
(`facts.i2c_pullup_ohms`, `parts.i2c_pullup_problems`) and a design's pull-ups (`rules_check`) are judged by. The rules
of `parts.py` (`i2c_pullup_problems` and the others) come here in W6-S3a. It imports nothing, so checks reads it along
its arrow down to sourcing.
"""

# --- MVP ---
#: A pull-up weaker than this cannot hold a bus high against its own capacitance; stronger than
#: this and the driving pin cannot pull it down. Wide on purpose — this is a sanity band, not a
#: design calculation, and saying which is which matters.
PULLUP_MIN_OHM = 1000
PULLUP_MAX_OHM = 10000
# --- end MVP ---
