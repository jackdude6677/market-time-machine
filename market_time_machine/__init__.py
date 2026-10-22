"""Market Time Machine package.

Provides the core entry point and version information.
"""

__all__ = ["__version__", "main"]

__version__: str = "0.1.0"

def main() -> None:
    """Entry point for the package when executed as a module.

    Currently prints a simple greeting.
    """
    print("Market Time Machine CLI – version", __version__)
