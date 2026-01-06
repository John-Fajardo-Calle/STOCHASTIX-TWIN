"""Inventory policies.

Policies live in a separate module to keep them easy to test and swap without
touching the SimPy runner.
"""

from __future__ import annotations


def order_up_to_sS(inventory_position: int, s: int, S: int) -> int:
    """(s, S) order-up-to policy.

    Returns the replenishment quantity (possibly zero). Inventory position is
    defined as on-hand + on-order - backorder.
    """

    if s > S:
        raise ValueError("Policy requires s <= S")
    if inventory_position <= s:
        return max(0, S - inventory_position)
    return 0
