#!/bin/sh
# Builds the converter into one file that runs on Node with no node_modules (P82, ends B10).
# Development only: needs bun and `bun install` here. Re-run after any change under lib/ or cli.ts —
# tests/test_check_spine.py fails while dist/converter.sources.sha256 does not match the sources.
set -e
cd "$(dirname "$0")"
bun build cli.ts --target=node --format=esm --outfile=dist/converter.mjs
python3 - <<'PY'
import hashlib
from pathlib import Path
sources = [Path("cli.ts")] + sorted(Path("lib").rglob("*.ts"))
Path("dist/converter.sources.sha256").write_text(hashlib.sha256(b"".join(p.read_bytes() for p in sources)).hexdigest() + "\n")
PY
echo "dist/converter.mjs: $(wc -c < dist/converter.mjs | tr -d ' ') bytes"
