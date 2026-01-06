"""Supplier placeholder.

The current model replenishes the DC via an abstract external supplier.
I keep this as a named entity to make it easy to evolve into a richer
multi-supplier or capacity-constrained model later.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Supplier:
    """A minimal supplier representation."""

    name: str = "Supplier"
