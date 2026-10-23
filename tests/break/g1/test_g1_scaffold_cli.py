"""Tests for scaffold package CLI behavior.

The current implementation treats any unknown command as a request for the
default information output and exits with status code 0.  According to the
specification an unknown command should cause the program to terminate with
a non‑zero exit status.
"""

import subprocess
import sys


def test_unknown_command_exits_nonzero():
    """Running the module with an unknown command must fail.

    The test invokes ``python -m market_time_machine bogus`` and expects a
    non‑zero return code.  The existing implementation prints the version and
    returns ``0`` which makes this test fail.
    """
    result = subprocess.run([sys.executable, "-m", "market_time_machine", "bogus"],
                            capture_output=True, text=True)
    # The process should exit with a non‑zero status code.
    assert result.returncode != 0, (
        "CLI should exit with non‑zero status for unknown commands; "
        f"got {result.returncode}. Output: {result.stdout}\n{result.stderr}"
    )
