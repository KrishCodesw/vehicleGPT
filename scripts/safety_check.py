"""Runtime/static safety check: no transmit paths in core packages."""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FORBIDDEN = re.compile(r"\b(send|transmit|write_frame|can_send)\b", re.I)
bad = []
for pkg in ["vgpt/ingest", "vgpt/store", "vgpt/insight", "vgpt/ask", "vgpt/api"]:
    for p in (ROOT / pkg).rglob("*.py"):
        text = p.read_text()
        for i, line in enumerate(text.splitlines(), 1):
            if FORBIDDEN.search(line) and "guard" not in line.lower():
                bad.append(f"{p}:{i}: {line.strip()}")
if bad:
    print("\n".join(bad))
    sys.exit(1)
print("safety: ok")