"""Typed models used across the simulation and API.

I keep these as simple dataclasses (instead of ORM-like objects) because the
simulation is a pure computation: configuration goes in, results come out.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class DemandPeak:
    """A temporary multiplier applied to baseline demand.

    This is a simple way to model promotions/seasonality without introducing a
    full forecasting component.
    """

    start_day: int
    end_day: int
    multiplier: float


@dataclass(frozen=True)
class SimulationConfig:
    """Inputs controlling a single simulation run.

    Note: Most fields intentionally use "per day" units to keep the model
    interpretable and to avoid accidental unit drift.
    """

    days: int = 365

    demand_lambda_per_day: float = 20.0
    demand_peaks: Tuple[DemandPeak, ...] = ()

    s_store: int = 80
    S_store: int = 160
    s_dc: int = 300
    S_dc: int = 600

    initial_on_hand_store: int = 120
    initial_on_hand_dc: int = 500

    lead_time_mean_days: float = 7.0
    lead_time_std_days: float = 2.0

    disruption_probability_per_shipment: float = 0.0
    disruption_delay_days: float = 0.0

    holding_cost_per_unit_per_day: float = 0.0

    seed: Optional[int] = None


@dataclass(frozen=True)
class KPIs:
    """KPIs computed from a completed run."""

    service_level: float
    fill_rate: float
    demand_units: int
    fulfilled_units: int
    stockout_days: int
    avg_on_hand_store: float
    avg_on_hand_dc: float
    avg_backorder_store: float
    total_orders_store: int
    total_orders_dc: int


@dataclass(frozen=True)
class SimulationResult:
    """Result of a single simulation run."""

    config: SimulationConfig
    kpis: KPIs
    timeseries: List[Dict[str, Any]]


@dataclass(frozen=True)
class MonteCarloSummary:
    """Aggregate statistics across multiple replications."""

    replications: int
    kpi_mean: Dict[str, float]
    kpi_std: Dict[str, float]


@dataclass(frozen=True)
class MonteCarloResult:
    """Monte Carlo output.

    `samples` is kept optional/compact: the UI only needs the summary, while
    tests and offline analysis may want the raw per-replication KPIs.
    """

    config: SimulationConfig
    summary: MonteCarloSummary
    samples: List[KPIs] = field(default_factory=list)
