"""Auditor module for Market Time Machine.

The Auditor probes the system for information‑firewall violations.  It is a
light‑weight utility used only in the test suite – it does not interfere with
the normal operation of the Oracle or the TradingEngine.

Current checks:

* **Future price leak** – the Oracle should not allow the Trader to query a
  price for a date later than the current simulation date.  The Oracle in the
  current code base does not enforce this rule, so the Auditor records a
  violation when the call succeeds.

Additional checks can be added later (timestamps, grading leaks, etc.).
"""

from __future__ import annotations

import datetime
from typing import List

from .oracle import Oracle


class Auditor:
    """Simple adversarial auditor.

    The auditor runs a series of sanity checks against an ``Oracle`` instance.
    Detected problems are stored in :attr:`violations` as human‑readable
    strings.
    """

    def __init__(self) -> None:
        self.violations: List[str] = []

    # ---------------------------------------------------------------------
    # Helper utilities
    # ---------------------------------------------------------------------
    @staticmethod
    def _next_trading_day(date: datetime.date, oracle: Oracle) -> datetime.date:
        """Return the next trading day after *date* using the Oracle's calendar.

        The Oracle provides :meth:`is_trading_day`.  We simply step forward one
        calendar day until a trading day is found.
        """
        nxt = date + datetime.timedelta(days=1)
        while not oracle.is_trading_day(nxt):
            nxt += datetime.timedelta(days=1)
        return nxt

    # ---------------------------------------------------------------------
    # Checks
    # ---------------------------------------------------------------------
    def check_future_price_leak(self, oracle: Oracle) -> None:
        """Detect if the Oracle leaks future price information.

        The test obtains the next trading day after ``oracle.current_date`` and
        attempts to call ``oracle.get_price``.  If the call does **not** raise a
        ``PermissionError`` the auditor records a violation.
        """
        future_date = self._next_trading_day(oracle.current_date, oracle)
        try:
            oracle.get_price("FAKE", future_date)
        except PermissionError:
            # Correct behaviour – no leak.
            return
        except Exception as exc:
            # Record the actual exception type name.
            self.violations.append(
                f"Future price leak detected: unexpected exception {type(exc).__name__}"
            )
            return
        else:
            self.violations.append(
                f"Future price leak detected: price for {future_date} was accessible"
            )

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def run_all(self, oracle: Oracle) -> List[str]:
        """Execute all checks against *oracle* and return the list of violations.
        """
        self.violations.clear()
        self.check_future_price_leak(oracle)
        # Future checks can be added here.
        return list(self.violations)

    def has_violations(self) -> bool:
        """Return ``True`` if any violations have been recorded."""
        return bool(self.violations)

    def __repr__(self) -> str:  # pragma: no cover – debugging helper
        return f"Auditor(violations={self.violations!r})"
