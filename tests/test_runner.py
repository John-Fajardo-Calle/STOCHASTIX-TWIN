"""Runner-level tests.

These tests focus on determinism under seeding and basic output sanity.
"""

from backend.simulation.models import DemandPeak, SimulationConfig
from backend.simulation.runner import monte_carlo, run_single


def test_run_single_kpis_sane_ranges():
    cfg = SimulationConfig(
        days=60,
        demand_lambda_per_day=15,
        s_store=50,
        S_store=100,
        s_dc=150,
        S_dc=300,
        initial_on_hand_store=80,
        initial_on_hand_dc=200,
        lead_time_mean_days=4,
        lead_time_std_days=1,
        seed=42,
    )
    r = run_single(cfg)

    assert 0.0 <= r.kpis.service_level <= 1.0
    assert 0.0 <= r.kpis.fill_rate <= 1.0
    assert r.kpis.demand_units >= 0
    assert 0 <= r.kpis.fulfilled_units <= r.kpis.demand_units


def test_run_single_deterministic_with_seed():
    cfg = SimulationConfig(days=30, demand_lambda_per_day=10, seed=123)
    r1 = run_single(cfg)
    r2 = run_single(cfg)
    assert r1.kpis == r2.kpis


def test_monte_carlo_supports_demand_peaks():
    cfg = SimulationConfig(
        days=30,
        demand_lambda_per_day=10,
        demand_peaks=(DemandPeak(start_day=5, end_day=10, multiplier=2.0),),
        seed=10,
    )
    mc = monte_carlo(cfg, replications=3)
    assert mc.summary.replications == 3
    assert 0.0 <= mc.summary.kpi_mean["service_level"] <= 1.0
