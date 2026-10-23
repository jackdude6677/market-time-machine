"""Tests for default risk limits enforcement in Portfolio.

The specification (section 4) defines default limits:
- max individual position: 5% of portfolio equity
- max sector exposure: 25% of equity
- max gross exposure: 100% of equity
- no short selling
- no leverage
- orders cannot exceed available cash
"""

import pytest

from market_time_machine.accounting import Portfolio, Order, RiskLimits


def test_default_risk_limits_values():
    # The default RiskLimits instance should reflect the spec defaults.
    defaults = RiskLimits()
    assert defaults.max_position_pct == 0.05, "Default max_position_pct should be 5%"
    assert defaults.max_sector_pct == 0.25, "Default max_sector_pct should be 25%"
    assert defaults.max_gross_exposure_pct == 1.0, "Default max_gross_exposure_pct should be 100%"
    assert defaults.allow_short is False, "Short selling should be disabled by default"
    assert defaults.allow_leverage is False, "Leverage should be disabled by default"

def test_position_limit_enforced():
    # Start with $1000 cash, default limits (5% => $50 max position)
    p = Portfolio(initial_cash=1000.0)
    # Attempt to buy a position costing $60 (>5% of equity)
    order = Order(asset="BIG", quantity=1, price=60.0, sector="Tech")
    with pytest.raises(ValueError):
        p.apply_order(order)

def test_sector_limit_enforced():
    # Increase position limit to allow first order, but sector limit should still trigger on second.
    limits = RiskLimits(max_position_pct=0.2)  # 20% of equity per asset
    p = Portfolio(initial_cash=1000.0, risk_limits=limits)
    # Two orders in same sector, each $30 per share.
    order1 = Order(asset="A1", quantity=3, price=30.0, sector="Health")  # $90
    order2 = Order(asset="A2", quantity=8, price=30.0, sector="Health")  # $240 total $330 > 25% of equity ($250)
    p.apply_order(order1)
    with pytest.raises(ValueError):
        p.apply_order(order2)

def test_gross_exposure_limit_enforced():
    # Increase position limit to avoid triggering position limit before gross exposure.
    limits = RiskLimits(max_position_pct=1.0)  # 100% per asset
    p = Portfolio(initial_cash=1000.0, risk_limits=limits)
    # Gross exposure limit is 100% of equity, i.e., $1000.
    # Create two positions totalling $1100.
    order1 = Order(asset="X1", quantity=5, price=80.0, sector="Tech")   # $400
    order2 = Order(asset="X2", quantity=7, price=100.0, sector="Energy")  # $700 total $1100
    p.apply_order(order1)
    with pytest.raises(ValueError):
        p.apply_order(order2)

def test_short_selling_not_allowed():
    p = Portfolio(initial_cash=1000.0)
    # Attempt to sell short without holding position.
    order = Order(asset="SHORT", quantity=-1, price=50.0, sector="Tech")
    with pytest.raises(ValueError):
        p.apply_order(order)

def test_leverage_not_allowed():
    p = Portfolio(initial_cash=1000.0)
    # Attempt to buy exceeding cash (requires leverage).
    order = Order(asset="LEVER", quantity=20, price=60.0, sector="Tech")  # cost $1200 + tx
    with pytest.raises(ValueError):
        p.apply_order(order)
