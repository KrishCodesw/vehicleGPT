"""Entry point: python -m vgpt.core"""

from __future__ import annotations

import asyncio

from vgpt.common.clock import WallClock
from vgpt.common.logging import configure_logging
from vgpt.common.settings import Settings


async def main() -> None:
    settings = Settings()
    configure_logging()
    clock = WallClock() if settings.clock == "wall" else WallClock()
    print(f"VehicleGPT Edge core ready (profile={settings.profile}, clock={clock.now_ms()})")


if __name__ == "__main__":
    asyncio.run(main())