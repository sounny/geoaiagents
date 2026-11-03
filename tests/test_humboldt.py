import pytest
import sys
from unittest.mock import patch, MagicMock
from humboldt import main

@pytest.mark.xfail(reason="Humboldt calls LLM for empty or whitespace-only input instead of a no-op")
def test_humboldt_empty_input(mocker, capsys):
    mocker.patch('humboldt.check_and_install_dependencies')
    mocker.patch('openai.OpenAI')

    mock_input = mocker.patch('builtins.input', side_effect=['', '   ', 'exit'])

    mock_call_llm = mocker.patch('humboldt.call_llm_with_retry')

    # We also need to mock sys.argv
    mocker.patch('sys.argv', ['humboldt.py'])

    main()

    # Check what happens
    # It should NOT call the LLM for empty/whitespace input
    # Currently it does, so we expect this to fail.

    # Assert LLM was not called
    assert mock_call_llm.call_count == 0, "LLM was called for empty or whitespace-only input"

    out, err = capsys.readouterr()
    # It should print some informative message or no-op. If it calls the LLM, mock_call_llm.call_count is non-zero.

import time
import humboldt

@pytest.mark.xfail(raises=RecursionError, reason="importlib.util.find_spec crashes with RecursionError for deeply nested module paths")
def test_is_package_installed_long_string():
    long_str = "a." * 1000000
    start_time = time.time()
    humboldt.is_package_installed(long_str)
    assert time.time() - start_time < 5.0

def test_handle_direct_command_long_string():
    long_str = "a" * 1000000
    tool_registry = MagicMock()
    start_time = time.time()
    result = humboldt.handle_direct_command("/geocode " + long_str, tool_registry)
    assert time.time() - start_time < 5.0
    assert result is True
    tool_registry.invoke.assert_called_once_with("geocode_locations", {"locations": long_str})
