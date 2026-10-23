
"""Break tests for risk‑limit enforcement.

Both the sector‑exposure limit and the per‑asset position‑size limit are
supposed to raise a ``ValueError`` when exceeded.  The current
implementation silently allows the orders, so these tests fail.
"""

import pytest
from market_time_machine.accounting import Portfolio, Order, RiskLimits


def test_position_limit_is_enforced():
    # Default max_position_pct = 1.0 (100 % of equity) – we set a tighter limit.
    limits = RiskLimits(max_position_pct=0.05)  # 5 % of equity
    p = Portfolio(risk_limits=limits)
    # Equity is $1000, so $50 is the max position value.
    # Buying $60 worth should raise.
    order = Order(asset="OVER", quantity=6, price=10.0, sector="Tech")
    with pytest.raises(ValueError, match="Position size exceeds limit"):
        p.apply_order(order)


def test_sector_limit_is_enforced():
    limits = RiskLimits(max_sector_pct=0.04)  # 4 % sector limit (40$)
    p = Portfolio(risk_limits=limits)
    # First order stays within the limit.
    order1 = Order(asset="AAA", quantity=3, price=10.0, sector="Energy")
    p.apply_order(order1)
    # Second order would push sector exposure to $70 (> $1000 × 0.04 = $40).
    order2 = Order(asset="BBB", quantity=4, price=10.0, sector="Energy")
    with pytest.raises(ValueError, match="Sector exposure exceeds limit"):
        p.apply_order(order2)

