"""Distribution center actor.

The DC is modeled as a simple inventory buffer that can ship immediately if
stock is available.
"""

from __future__ import annotations

from dataclasses import dataclass

import simpy

from backend.simulation.actors.base import InventoryState


@dataclass
class DistributionCenter:
    """A single-echelon distribution center."""

    env: simpy.Environment
    name: str
    inventory: InventoryState

    orders_placed: int = 0

    def receive(self, quantity: int) -> None:
        """Receive inbound supply into on-hand inventory."""

        if quantity <= 0:
            return
        self.inventory.on_hand += int(quantity)

    def ship_to_store(self, quantity: int) -> int:
        """Attempt to ship requested quantity; returns what actually shipped."""

        if quantity <= 0:
            return 0
        shipped = min(self.inventory.on_hand, int(quantity))
        self.inventory.on_hand -= shipped
        return shipped
