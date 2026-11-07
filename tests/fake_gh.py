"""
A stand-in for the GitHub CLI gh in the tests (P687), so no golden run reaches GitHub. It answers `gh api ... --jq
.content` as gh does, with a file's content in base64: spark's kept header of the FireBeetle 2 ESP32-S3, with
FAKE_GH_FIND replaced by FAKE_GH_REPLACE. With FAKE_GH_EXIT set, it prints gh's 404 on stderr and exits with it.
"""

import base64
import os
import sys
from pathlib import Path

HEADER = Path(__file__).resolve().parent.parent / ".spark" / "cache" / "dfrobot_firebeetle2_esp32s3.pins_arduino.h"

if os.environ.get("FAKE_GH_EXIT"):
    print("HTTP 404: Not Found (fake gh)", file=sys.stderr)
    sys.exit(int(os.environ["FAKE_GH_EXIT"]))
text = HEADER.read_text()
if os.environ.get("FAKE_GH_FIND"):
    text = text.replace(os.environ["FAKE_GH_FIND"], os.environ.get("FAKE_GH_REPLACE", ""))
print(base64.b64encode(text.encode()).decode())
