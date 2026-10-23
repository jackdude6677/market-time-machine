"""Break tests for accounting default risk limits.

The current implementation uses very permissive defaults (100% limits),
whereas the specification expects stricter defaults (e.g. 5 % position
limit, 10 % sector limit, 50 % gross exposure).  These tests assert that
the stricter limits are enforced; they will therefore FAIL with the
existing code, proving the bug.
"""

import pytest

from market_time_machine.accounting import Portfolio, Order


def test_default_position_limit_is_enforced():
    """Buying beyond a 5 % position of equity should raise.

    With default limits the position limit is 5 % of equity ($50 for a
    $1000 portfolio).  Buying 6 shares at $10 ($60) exceeds this and must
    raise ``ValueError`` with the appropriate message.
    """
    p = Portfolio()
    order = Order(asset="AAA", quantity=6, price=10.0)
    with pytest.raises(ValueError, match="Position size exceeds limit"):
        p.apply_order(order)


def test_default_sector_limit_is_enforced():
    """Sector exposure beyond 10 % of equity should raise.

    Two orders in the same sector each cost $30, total $60 > 10 % of
    $1000 equity.  The second order should trigger a sector limit
    violation.
    """
    p = Portfolio()
    # First order within sector limit (3 shares × $10 = $30)
    order1 = Order(asset="BBB", quantity=3, price=10.0, sector="Energy")
    p.apply_order(order1)
    # Second order pushes sector exposure to $60 > $100 (10% of $1000)
    order2 = Order(asset="CCC", quantity=3, price=10.0, sector="Energy")
    with pytest.raises(ValueError, match="Sector exposure exceeds limit"):
        p.apply_order(order2)


def test_default_gross_exposure_limit_is_enforced():
    """Gross exposure beyond 50 % of equity should raise.

    Buying $600 worth of a single asset exceeds a 50 % gross exposure
    limit on a $1000 portfolio.
    """
    p = Portfolio()
    order = Order(asset="DDD", quantity=60, price=10.0, sector="Finance")
    with pytest.raises(ValueError, match="Gross exposure exceeds limit"):
        p.apply_order(order)
