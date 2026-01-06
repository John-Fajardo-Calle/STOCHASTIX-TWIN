"""Unit tests for policy helpers."""

import pytest

from backend.simulation.logic.policy import order_up_to_sS


def test_order_up_to_sS_orders_when_below_s():
    assert order_up_to_sS(inventory_position=50, s=80, S=160) == 110


def test_order_up_to_sS_no_order_when_above_s():
    assert order_up_to_sS(inventory_position=81, s=80, S=160) == 0


def test_order_up_to_sS_guard_invalid():
    with pytest.raises(ValueError):
        order_up_to_sS(inventory_position=0, s=10, S=5)
