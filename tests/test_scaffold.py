import subprocess
import sys

import market_time_machine

def test_version_format():
    # Version should be a string with three numeric parts
    parts = market_time_machine.__version__.split('.')
    assert len(parts) == 3
    assert all(p.isdigit() for p in parts)

def test_cli_output():
    # Run the module as a script and capture output
    result = subprocess.run([sys.executable, '-m', 'market_time_machine'],
                            capture_output=True, text=True, check=True)
    assert "Market Time Machine CLI" in result.stdout
    assert market_time_machine.__version__ in result.stdout
