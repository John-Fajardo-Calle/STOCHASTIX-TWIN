"""Random variate helpers used by the simulation.

These wrappers centralize validation and keep the core runner readable.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np


def poisson_demand(rng: np.random.Generator, lam: float) -> int:
    """Sample non-negative integer demand from a Poisson(lambda) process."""

    if lam < 0:
        raise ValueError("demand lambda must be >= 0")
    return int(rng.poisson(lam=lam))


def _lognormal_mu_sigma_from_mean_std(mean: float, std: float) -> tuple[float, float]:
    """Convert mean/std of a lognormal into the underlying normal (mu, sigma).

    Why this exists: domain users tend to reason in “mean lead time” and
    “variability”, while NumPy needs the parameters of the underlying normal.
    """

    if mean <= 0:
        raise ValueError("lognormal mean must be > 0")
    if std < 0:
        raise ValueError("lognormal std must be >= 0")
    if std == 0:
        return math.log(mean), 0.0

    variance = std * std
    sigma2 = math.log(1.0 + variance / (mean * mean))
    mu = math.log(mean) - 0.5 * sigma2
    return mu, math.sqrt(sigma2)


def lognormal_days(rng: np.random.Generator, mean_days: float, std_days: float) -> float:
    """Sample a strictly non-negative lead time in days.

    I use a lognormal to avoid negative lead times while still allowing
    right-skewed delays (a common pattern in supply chains).
    """

    mu, sigma = _lognormal_mu_sigma_from_mean_std(mean_days, std_days)
    if sigma == 0.0:
        return float(mean_days)
    return float(rng.lognormal(mean=mu, sigma=sigma))
