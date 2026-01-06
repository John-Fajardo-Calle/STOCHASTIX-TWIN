"""Distribution-level sanity checks.

These are not strict statistical proofs; they are smoke tests to catch obvious
parameterization mistakes.
"""

import numpy as np

from backend.simulation.distributions import lognormal_days, poisson_demand


def test_poisson_demand_mean_approx():
    rng = np.random.default_rng(123)
    lam = 20.0
    n = 20_000
    samples = np.array([poisson_demand(rng, lam) for _ in range(n)], dtype=float)

    mean = float(samples.mean())
    assert abs(mean - lam) / lam < 0.05


def test_lognormal_days_mean_approx():
    rng = np.random.default_rng(123)
    mean_days = 7.0
    std_days = 2.0
    n = 30_000
    samples = np.array([lognormal_days(rng, mean_days, std_days) for _ in range(n)], dtype=float)

    mean = float(samples.mean())
    assert abs(mean - mean_days) / mean_days < 0.06


def test_lognormal_days_non_negative():
    rng = np.random.default_rng(1)
    for _ in range(1000):
        assert lognormal_days(rng, 3.0, 1.0) >= 0.0
