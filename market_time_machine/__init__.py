"""Market Time Machine package.

Provides the core entry point and version information.
"""

__all__ = ["__version__", "main"]

__version__: str = "0.1.0"

def main() -> None:
    """Entry point for the package when executed as a module.

    Supports the ``export-ui`` command to generate a demo UI snapshot.
    """
    import argparse, json, os
    parser = argparse.ArgumentParser(prog='market_time_machine')
    parser.add_argument('command', nargs='?', default='info')
    args = parser.parse_args()
    if args.command == 'export-ui':
        _export_ui()
    else:
        print("Market Time Machine CLI – version", __version__)

def _export_ui() -> None:
    """Write a demo snapshot JSON for the static UI.

    The file is written to ``app/data/demo_snapshot.json`` relative to the
    project root.  It contains a minimal but representative data structure
    expected by the UI JavaScript.
    """
    import pathlib
    data = {
        "capital": 1000000,
        "positions": ["AAPL", "TSLA"],
        "weekly_grades": [
            {"week": "2024-W01", "grade": "A"},
            {"week": "2024-W02", "grade": "B"},
        ],
        "strategies": [
            {"name": "Mean Reversion", "survival": 85},
            {"name": "Momentum", "survival": 70},
        ],
        "relationships": [
            {"type": "Correlation", "detail": "AAPL ↔ MSFT: 0.78"},
            {"type": "Causation", "detail": "Interest Rate → SPY"},
        ],
        "auditor_findings": [
            "No leakage detected",
            "Risk limits respected",
        ],
        "commands": [
            "python -m market_time_machine run --days 7",
            "python -m market_time_machine strategy list",
        ],
    }
    out_path = pathlib.Path('app/data')
    out_path.mkdir(parents=True, exist_ok=True)
    file_path = out_path / 'demo_snapshot.json'
    file_path.write_text(json.dumps(data, indent=2))
    print(f"Demo UI snapshot written to {file_path}")
