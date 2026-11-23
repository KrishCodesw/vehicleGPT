"""Unit conversions. Keep all conversions here and covered by tests."""

from __future__ import annotations


def ms_to_s(ms: int) -> float:
    return ms / 1000.0


def kwh_per_100km_to_wh_per_km(v: float) -> float:
    return v * 10.0  # kWh/100km -> Wh/km