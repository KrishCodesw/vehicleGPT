"""Clock abstraction: wall or simulated. All time reads go through here (D12)."""

from __future__ import annotations

import time
from typing import Protocol


class Clock(Protocol):
    def now_ms(self) -> int: ...


class WallClock:
    def now_ms(self) -> int:
        return int(time.time() * 1000)


class SimClock:
    def __init__(self, start_ms: int = 0) -> None:
        self._ms = start_ms

    def now_ms(self) -> int:
        return self._ms

    def advance(self, ms: int) -> None:
        self._ms += ms

    def set(self, ms: int) -> None:
        self._ms = ms