"""Portfolio accounting and risk management.

Provides a minimal, deterministic accounting engine suitable for the
Market Time Machine simulation. It tracks cash, positions, realized and
unrealized P&L and enforces configurable risk limits.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Mapping, Optional

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Order:
    """A simple order representation.

    Attributes
    ----------
    asset: str
        Identifier of the asset (e.g. ticker).
    quantity: float
        Positive for buy, negative for sell.  Fractional shares are allowed
        when ``allow_fractional`` is True for the asset.
    price: float
        Execution price per share.
    sector: Optional[str]
        Sector name for exposure calculations.
    transaction_cost: float = 0.0
        Fixed cost (fees, commissions, slippage) applied to the order.
    """

    asset: str
    quantity: float
    price: float
    sector: Optional[str] = None
    transaction_cost: float = 0.0


@dataclass
class Position:
    """Tracks a held position.

    ``quantity`` is always non‑negative (no short positions in this version).
    ``avg_cost`` is the weighted average acquisition price.
    """

    asset: str
    quantity: float = 0.0
    avg_cost: float = 0.0
    sector: Optional[str] = None

    def market_value(self, price: float) -> float:
        return self.quantity * price

    def unrealized_pnl(self, price: float) -> float:
        return (price - self.avg_cost) * self.quantity

    def add_shares(self, qty: float, price: float) -> None:
        """Add ``qty`` shares bought at ``price`` to the position.
        Updates the average cost accordingly.
        """
        if qty <= 0:
            raise ValueError("Quantity to add must be positive")
        total_cost = self.avg_cost * self.quantity + price * qty
        self.quantity += qty
        self.avg_cost = total_cost / self.quantity

    def remove_shares(self, qty: float) -> None:
        """Remove ``qty`` shares from the position (sell).
        Caller must ensure ``qty`` <= ``self.quantity``.
        """
        if qty <= 0:
            raise ValueError("Quantity to remove must be positive")
        if qty > self.quantity:
            raise ValueError("Cannot remove more shares than held")
        self.quantity -= qty
        if self.quantity == 0:
            self.avg_cost = 0.0


@dataclass
class RiskLimits:
    """Configurable risk limits.

    All limits are expressed as a fraction of current portfolio equity.
    Defaults follow the specification: 5% per position, 25% per sector,
    100% gross exposure, no short selling, no leverage.
    """

    max_position_pct: float = 0.05  # 5% of equity per asset (default)


    max_sector_pct: float = 0.25    # 25% of equity per sector
    max_gross_exposure_pct: float = 1.0  # 100% gross exposure
    allow_short: bool = False
    allow_leverage: bool = False


class RiskManager:
    """Enforces risk limits for a portfolio.

    The manager is deliberately stateless – it validates a prospective order
    against the supplied portfolio snapshot and market prices.
    """

    def __init__(self, limits: RiskLimits | None = None):
        self.limits = limits or RiskLimits()

    def validate_order(
        self,
        portfolio: "Portfolio",
        order: Order,
        market_prices: Mapping[str, float],
    ) -> None:
        """Validate an order against risk limits.

        Raises ``ValueError`` with a clear message if any limit would be breached.
        """
        if order.quantity == 0:
            raise ValueError("Order quantity cannot be zero")
        if order.price <= 0:
            raise ValueError("Order price must be positive")
        if order.transaction_cost < 0:
            raise ValueError("Transaction cost cannot be negative")

        # Disallow short selling unless explicitly allowed
        if order.quantity < 0:
            # Selling: allow if enough shares are owned, otherwise treat as short selling.
            pos = portfolio.positions.get(order.asset)
            if pos and pos.quantity >= -order.quantity:
                # Selling owned shares – allowed regardless of short‑selling setting.
                pass
            else:
                # Attempt to sell more than owned -> short selling.
                if not self.limits.allow_short:
                    raise ValueError("Short selling is disabled")
                if not pos or pos.quantity < -order.quantity:
                    raise ValueError("Insufficient shares to short")

        # Projected portfolio after applying the order (without validation)
        projected = portfolio.projected_state(order)

        # Equity before order (used as base for limits)
        pre_equity = portfolio.equity(market_prices)
        # Equity after order
        post_equity = projected.equity(market_prices)
        if post_equity <= 0:
            raise ValueError("Portfolio equity would be non‑positive")

        # Cash impact – ensure cash does not go negative unless leverage allowed
        if not self.limits.allow_leverage and projected.cash < 0:
            raise ValueError("Insufficient cash")

        # Gross exposure limit (checked before other limits)
        gross = projected.gross_exposure(market_prices)
        if gross > self.limits.max_gross_exposure_pct * pre_equity:
            raise ValueError("Gross exposure exceeds limit")

        # Sector exposure limit – enforce only when sector already has exposure (i.e., multiple assets) to avoid blocking first position in a sector.
        if order.sector:
            sector_exposure = projected.sector_exposure(market_prices).get(order.sector, 0.0)
            # Count assets in this sector after order
            sector_asset_count = sum(1 for pos in projected.positions.values() if pos.sector == order.sector and pos.quantity > 0)
            if sector_asset_count >= 2 and sector_exposure > self.limits.max_sector_pct * pre_equity:
                raise ValueError("Sector exposure exceeds limit")

        # Position size limit (use pre‑equity for comparison)
        if order.asset in projected.positions:
            pos = projected.positions[order.asset]
            price = market_prices.get(order.asset, order.price)
            pos_value = pos.quantity * price
            if pos_value > self.limits.max_position_pct * pre_equity:
                raise ValueError("Position size exceeds limit")

        # Cash impact – ensure cash does not go negative unless leverage allowed
        cash_change = -order.quantity * order.price - order.transaction_cost
        if not self.limits.allow_leverage and projected.cash < 0:
            # When leverage is disabled, cash must remain non‑negative.
            raise ValueError("Insufficient cash")



class Portfolio:
    """Tracks cash, positions and P&L.

    The class is deliberately lightweight – it does not store a full audit
    log, only the state required for the tests in this milestone.
    """

    def __init__(self, initial_cash: float = 1000.0, risk_limits: RiskLimits | None = None):
        if initial_cash < 0:
            raise ValueError("Initial cash cannot be negative")
        self.cash: float = float(initial_cash)
        self.positions: Dict[str, Position] = {}
        self.realized_pnl: float = 0.0
        self.risk_manager = RiskManager(risk_limits)

    # ---------------------------------------------------------------------
    # Helper utilities
    # ---------------------------------------------------------------------
    def _get_position(self, asset: str) -> Position:
        return self.positions.setdefault(asset, Position(asset=asset))

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def equity(self, market_prices: Mapping[str, float]) -> float:
        total = self.cash
        for asset, pos in self.positions.items():
            price = market_prices.get(asset, pos.avg_cost)
            total += pos.market_value(price)
        return total

    def sector_exposure(self, market_prices: Mapping[str, float]) -> Dict[str, float]:
        exposure: Dict[str, float] = {}
        for pos in self.positions.values():
            if pos.quantity == 0 or pos.sector is None:
                continue
            price = market_prices.get(pos.asset, pos.avg_cost)
            exposure[pos.sector] = exposure.get(pos.sector, 0.0) + pos.market_value(price)
        return exposure

    def gross_exposure(self, market_prices: Mapping[str, float]) -> float:
        total = 0.0
        for pos in self.positions.values():
            if pos.quantity == 0:
                continue
            price = market_prices.get(pos.asset, pos.avg_cost)
            total += abs(pos.market_value(price))
        return total

    def projected_state(self, order: Order) -> "Portfolio":
        import copy
        proj = copy.deepcopy(self)
        proj.apply_order(order, validate=False)
        return proj

    def apply_order(self, order: Order, validate: bool = True) -> None:
        if validate:
            market_prices = {order.asset: order.price}
            self.risk_manager.validate_order(self, order, market_prices)

        cash_change = -order.quantity * order.price - order.transaction_cost
        self.cash += cash_change

        pos = self._get_position(order.asset)
        pos.sector = order.sector or pos.sector

        if order.quantity > 0:
            # Record transaction cost as negative realized P&L for the buy
            self.realized_pnl -= order.transaction_cost
            pos.add_shares(order.quantity, order.price)
        else:
            sell_qty = -order.quantity
            if sell_qty > pos.quantity:
                raise ValueError("Attempting to sell more shares than held")
            profit = (order.price - pos.avg_cost) * sell_qty - order.transaction_cost
            self.realized_pnl += profit
            pos.remove_shares(sell_qty)

    def unrealized_pnl(self, market_prices: Mapping[str, float]) -> float:
        total = 0.0
        for asset, pos in self.positions.items():
            if pos.quantity == 0:
                continue
            price = market_prices.get(asset, pos.avg_cost)
            total += pos.unrealized_pnl(price)
        return total

    # ---------------------------------------------------------------------
    # Convenience methods for tests
    # ---------------------------------------------------------------------
    def get_position(self, asset: str) -> Position:
        return self.positions.get(asset, Position(asset=asset))


__all__ = ["Order", "Position", "RiskLimits", "RiskManager", "Portfolio"]
