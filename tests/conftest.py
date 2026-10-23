import pathlib

def pytest_ignore_collect(collection_path, config):
    # Ignore any test files under the 'tests/break' directory
    break_dir = pathlib.Path(__file__).parent / "break"
    try:
        return break_dir in collection_path.parents
    except Exception:
        return False
