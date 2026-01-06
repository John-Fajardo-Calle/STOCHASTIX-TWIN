"""Stochastic disruption events.

These helpers intentionally return additive effects (e.g., extra delay days)
so the runner can compose multiple sources of uncertainty.
"""

from __future__ import annotations

import numpy as np


def disruption_delay(
    rng: np.random.Generator,
    probability_per_shipment: float,
    delay_days: float,
) -> float:
    """Optionally add a fixed delay to a shipment.

    Why fixed delay: it keeps the effect interpretable when toggling scenarios.
    If you later want richer disruption behavior, you can replace this with a
    distribution without changing the runner’s call sites.
    """

    if probability_per_shipment < 0 or probability_per_shipment > 1:
        raise ValueError("disruption_probability_per_shipment must be in [0,1]")
    if delay_days < 0:
        raise ValueError("disruption_delay_days must be >= 0")

    if probability_per_shipment == 0 or delay_days == 0:
        return 0.0

    return float(delay_days if rng.random() < probability_per_shipment else 0.0)
