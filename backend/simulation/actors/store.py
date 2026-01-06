"""Store actor.

The store is where demand is realized and where service metrics are measured.
"""

from __future__ import annotations

from dataclasses import dataclass

import simpy

from backend.simulation.actors.base import InventoryState


@dataclass
class Store:
    """A retail location consuming demand and receiving replenishments."""

    env: simpy.Environment
    name: str
    inventory: InventoryState

    demand_units: int = 0
    fulfilled_units: int = 0
    stockout_days: int = 0
    orders_placed: int = 0

    def consume_demand(self, demand_qty: int) -> None:
        """Consume demand from on-hand stock; unmet demand becomes backorder."""

        demand_qty = int(max(0, demand_qty))
        self.demand_units += demand_qty

        fulfilled = min(self.inventory.on_hand, demand_qty)
        self.inventory.on_hand -= fulfilled
        self.fulfilled_units += fulfilled

        unmet = demand_qty - fulfilled
        if unmet > 0:
            self.inventory.backorder += unmet
            self.stockout_days += 1

    def receive(self, quantity: int) -> None:
        """Receive inbound shipment; backorders are satisfied first."""

        if quantity <= 0:
            return
        quantity = int(quantity)

        if self.inventory.backorder > 0:
            used = min(self.inventory.backorder, quantity)
            self.inventory.backorder -= used
            quantity -= used

        self.inventory.on_hand += quantity
