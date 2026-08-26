"""Thrust-to-weight and hover throttle.

Rule of thumb for multirotors:
  TWR < 1.5  will not leave the ground reliably
  TWR ~ 2.0  minimum flyable, sluggish
  TWR ~ 3-4  normal FPV freestyle
  TWR > 6    racing
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass
class ThrustReport:
    total_thrust_g: float
    auw_g: float
    twr: float
    hover_throttle_pct: float
    payload_headroom_g: float   # extra grams you could still add at min TWR
    verdict: str


def build(p: dict[str, Any], auw_g: float) -> ThrustReport:
    n = int(p["motors"]["count"])
    per = float(p["motors"]["max_thrust_g"])
    total = n * per
    twr = total / auw_g

    # Thrust scales roughly with throttle^2, so hover sits near 1/sqrt(TWR).
    hover = 100.0 / math.sqrt(twr) if twr > 0 else 100.0

    min_twr = float(p["limits"]["min_twr"])
    target = float(p["limits"]["target_twr"])
    headroom = total / min_twr - auw_g

    if twr >= target:
        verdict = "good"
    elif twr >= min_twr:
        verdict = "marginal"
    else:
        verdict = "will not fly"

    return ThrustReport(
        total_thrust_g=total,
        auw_g=auw_g,
        twr=twr,
        hover_throttle_pct=min(hover, 100.0),
        payload_headroom_g=headroom,
        verdict=verdict,
    )
