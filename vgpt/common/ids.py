"""ID helpers."""

from __future__ import annotations

import uuid


def new_id(prefix: str = "") -> str:
    u = uuid.uuid4().hex
    return f"{prefix}{u}" if prefix else u