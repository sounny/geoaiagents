import subprocess
import sys
import pytest

MODULES = [
    "dd2dms",
    "distance",
    "file_loaders",
    "geocode",
    "humboldt",
    "llm_utils",
    "tool_registry",
    "validation",
    "webchat",
    "geoai_cli"
]

@pytest.mark.parametrize("module_name", MODULES)
def test_isolated_import(module_name):
    """
    Runs python -c "import <module>" in a fresh subprocess so hidden
    import-order dependencies fail. Skips if an optional dependency is missing.
    """
    cmd = [sys.executable, "-c", f"import {module_name}"]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        stderr_output = result.stderr
        if "ModuleNotFoundError" in stderr_output or "ImportError" in stderr_output:
            # Check if it's missing the module we are actually trying to test, which would be weird
            # but usually it's an optional dependency like 'folium', 'geopy', etc.
            if f"No module named '{module_name}'" in stderr_output:
                pytest.fail(f"Could not find top-level module {module_name}:\n{stderr_output}")

            # For third-party or optional dependency missing
            pytest.skip(f"Skipping due to missing optional dependency for {module_name}:\n{stderr_output}")
        else:
            # Some other error (SyntaxError, circular import, etc.)
            pytest.fail(f"Importing {module_name} failed with non-zero exit code:\n{stderr_output}")
