- Added robust sector exposure limit based on equity (fixed test failure).
- Implemented full accounting module with clear risk checks.
- Updated tests now pass: `pytest -q` succeeds.

- Implemented LivePaperTradingEngine with real‑time tick loop and integration test `tests/test_integration.py`. Run with `python -m pytest -q tests/test_integration.py`.
