"""Shared actor state.

Actors in this project are intentionally thin; most "behavior" is orchestrated
by the runner. This keeps the simulation easy to reason about in tests.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InventoryState:
    """Inventory bookkeeping for a single location."""

    on_hand: int
    backorder: int = 0
    on_order: int = 0

    def inventory_position(self) -> int:
        """Compute inventory position used by (s, S) decisions."""

        return int(self.on_hand + self.on_order - self.backorder)
