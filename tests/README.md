# Tests

This directory contains the test suite for the project.

## How to run the tests

1. Ensure all dependencies (including testing tools like `pytest`, `pytest-cov`, `pytest-timeout`, and `pytest-mock`) are installed:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the tests by appending the current directory to `PYTHONPATH` from the repository root:
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd) && python3 -m pytest tests/
   ```

## Network Policy

**Tests must not call the network.**

By default, the test suite blocks real outbound socket connections via an autouse fixture in `tests/conftest.py`. All network-dependent features should be thoroughly mocked. Tests requiring explicit network access must opt-out by being explicitly marked with `@pytest.mark.allow_network`.

If an equivalent test already exists, extend it minimally instead of duplicating. If a test exposes a real bug, keep production code unchanged and mark the test skipped/xfail with a short note.

## Test File to Module Mapping

Here is an overview of which test file covers which module:

- `test_configuration.py` -> Covers environment configurations in `humboldt.py`, `geoai_cli.py`, `webchat.py`, and `tool_registry.py`
- `test_dd2dms.py` -> `dd2dms.py`
- `test_distance.py` -> `distance.py`
- `test_example_plugin.py` -> `plugins/example_plugin.py`
- `test_file_loaders.py` -> `file_loaders.py`
- `test_geoai_cli.py` -> `geoai_cli.py`
- `test_geocode.py` -> `geocode.py`
- `test_install_requirements.py` -> `install_requirements.py` / `requirements.txt`
- `test_orchestration_retry.py` -> `humboldt.py`, `llm_utils.py`
- `test_plugins_init.py` -> `plugins/__init__.py`
- `test_provider_edge_cases.py` -> Provider edge cases in LLM integrations
- `test_provider_selection.py` -> Provider selection in LLM integrations
- `test_tool_registry.py` -> `tool_registry.py`
- `test_validation.py` -> `validation.py`
- `test_wcag_ui.py` -> `index.html` (WCAG / UI)
- `test_webchat.py` -> `webchat.py`
- `test_webchat_config.py` -> `webchat.py` (configuration)
- `test_webchat_map.py` -> `webchat.py` (map parsing)
- `test_webchat_parsing.py` -> `webchat.py` (text parsing)
- `test_webchat_tables.py` -> `webchat.py` (table generation)
