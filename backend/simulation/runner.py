"""Simulation runner.

The runner owns the SimPy environment and orchestrates daily decisions.
Keeping orchestration here (instead of spreading it across many actor methods)
makes it easier to audit and to keep deterministic behavior under seeding.
"""

from __future__ import annotations

from dataclasses import asdict, replace
from typing import Callable, Dict, List, Optional, Protocol

import numpy as np
import simpy

from backend.simulation.actors.base import InventoryState
from backend.simulation.actors.distribution_center import DistributionCenter
from backend.simulation.actors.store import Store
from backend.simulation.chaos.events import disruption_delay
from backend.simulation.distributions import lognormal_days, poisson_demand
from backend.simulation.logic.policy import order_up_to_sS
from backend.simulation.models import KPIs, MonteCarloResult, MonteCarloSummary, SimulationConfig, SimulationResult


class _Receivable(Protocol):
    """Duck-typed interface for any node that can receive a shipment."""

    inventory: InventoryState

    def receive(self, quantity: int) -> None: ...


def _demand_multiplier_for_day(config: SimulationConfig, day: int) -> float:
    """Compute the multiplicative demand factor for a given day."""

    multiplier = 1.0
    for peak in config.demand_peaks:
        if peak.start_day <= day <= peak.end_day:
            multiplier *= float(peak.multiplier)
    return multiplier


def run_single(config: SimulationConfig) -> SimulationResult:
    """Run a single stochastic replication.

    The returned `timeseries` is designed for lightweight dashboards: each entry
    is a dict of numeric values that can be plotted without additional decoding.
    """

    random_generator = np.random.default_rng(config.seed)
    environment = simpy.Environment()

    distribution_center = DistributionCenter(
        env=environment,
        name="DC",
        inventory=InventoryState(on_hand=config.initial_on_hand_dc),
    )
    store = Store(
        env=environment,
        name="Store",
        inventory=InventoryState(on_hand=config.initial_on_hand_store),
    )

    timeseries: List[Dict[str, float]] = []

    def schedule_inbound_shipment(receiver: _Receivable, quantity: int) -> None:
        """Schedule an arrival event and track pipeline inventory.

        I track `on_order` so inventory position includes pipeline stock.
        Without that, the (s, S) policy tends to over-order and inflate
        variability.
        """

        if quantity <= 0:
            return

        receiver.inventory.on_order += quantity

        lead_time_days = lognormal_days(
            random_generator,
            config.lead_time_mean_days,
            config.lead_time_std_days,
        )
        lead_time_days += disruption_delay(
            random_generator,
            config.disruption_probability_per_shipment,
            config.disruption_delay_days,
        )

        def arrival_process() -> simpy.events.Event:
            yield environment.timeout(lead_time_days)
            receiver.inventory.on_order -= quantity
            receiver.receive(quantity)

        environment.process(arrival_process())

    def daily_process() -> simpy.events.Event:
        for day in range(config.days):
            demand_lambda = config.demand_lambda_per_day * _demand_multiplier_for_day(config, day)
            store.consume_demand(poisson_demand(random_generator, demand_lambda))

            if store.inventory.backorder > 0:
                # I prioritize clearing accumulated backorders before placing a new order-up-to,
                # which keeps the behavior closer to "ship what you owe" operations.
                shipped_quantity = distribution_center.ship_to_store(store.inventory.backorder)
                if shipped_quantity > 0:
                    schedule_inbound_shipment(store, shipped_quantity)

            store_inventory_position = store.inventory.inventory_position()
            store_replenishment_quantity = order_up_to_sS(
                store_inventory_position,
                config.s_store,
                config.S_store,
            )
            if store_replenishment_quantity > 0:
                store.orders_placed += 1
                shipped_quantity = distribution_center.ship_to_store(store_replenishment_quantity)
                if shipped_quantity > 0:
                    schedule_inbound_shipment(store, shipped_quantity)

                unshipped_quantity = store_replenishment_quantity - shipped_quantity
                if unshipped_quantity > 0:
                    store.inventory.backorder += unshipped_quantity

            dc_inventory_position = distribution_center.inventory.inventory_position()
            dc_replenishment_quantity = order_up_to_sS(
                dc_inventory_position,
                config.s_dc,
                config.S_dc,
            )
            if dc_replenishment_quantity > 0:
                distribution_center.orders_placed += 1
                schedule_inbound_shipment(distribution_center, dc_replenishment_quantity)

            timeseries.append(
                {
                    "day": float(day),
                    "store_on_hand": float(store.inventory.on_hand),
                    "store_backorder": float(store.inventory.backorder),
                    "store_on_order": float(store.inventory.on_order),
                    "dc_on_hand": float(distribution_center.inventory.on_hand),
                    "dc_on_order": float(distribution_center.inventory.on_order),
                }
            )

            yield environment.timeout(1.0)

    environment.process(daily_process())
    environment.run(until=float(config.days))

    demand_units = int(store.demand_units)
    fulfilled_units = int(store.fulfilled_units)

    service_level = 1.0 - (store.stockout_days / config.days if config.days > 0 else 0.0)
    fill_rate = (fulfilled_units / demand_units) if demand_units > 0 else 1.0

    avg_on_hand_store = float(np.mean([p["store_on_hand"] for p in timeseries])) if timeseries else 0.0
    avg_on_hand_dc = float(np.mean([p["dc_on_hand"] for p in timeseries])) if timeseries else 0.0
    avg_backorder_store = float(np.mean([p["store_backorder"] for p in timeseries])) if timeseries else 0.0

    kpis = KPIs(
        service_level=float(service_level),
        fill_rate=float(fill_rate),
        demand_units=demand_units,
        fulfilled_units=fulfilled_units,
        stockout_days=int(store.stockout_days),
        avg_on_hand_store=avg_on_hand_store,
        avg_on_hand_dc=avg_on_hand_dc,
        avg_backorder_store=avg_backorder_store,
        total_orders_store=int(store.orders_placed),
        total_orders_dc=int(distribution_center.orders_placed),
    )

    return SimulationResult(config=config, kpis=kpis, timeseries=timeseries)


def monte_carlo(
    config: SimulationConfig,
    replications: int,
    progress_cb: Optional[Callable[[float], None]] = None,
) -> MonteCarloResult:
    """Run multiple replications and summarize KPI uncertainty.

    I derive per-replication seeds by offsetting the base seed. This preserves
    repeatability while still producing distinct trajectories.
    """

    if replications <= 0:
        raise ValueError("replications must be > 0")

    samples: List[KPIs] = []
    for i in range(replications):
        seed = None if config.seed is None else int(config.seed) + i
        result = run_single(replace(config, seed=seed))
        samples.append(result.kpis)
        if progress_cb is not None:
            progress_cb((i + 1) / replications)

    kpi_fields = list(asdict(samples[0]).keys()) if samples else []
    matrix = {field: np.array([getattr(k, field) for k in samples], dtype=float) for field in kpi_fields}

    kpi_mean = {k: float(np.mean(v)) for k, v in matrix.items()}
    kpi_std = {k: float(np.std(v, ddof=1)) if replications > 1 else 0.0 for k, v in matrix.items()}

    summary = MonteCarloSummary(replications=replications, kpi_mean=kpi_mean, kpi_std=kpi_std)
    return MonteCarloResult(config=config, summary=summary, samples=samples)
