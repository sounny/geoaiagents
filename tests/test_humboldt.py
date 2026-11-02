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

@pytest.mark.parametrize("char", ['\t', '\r', '\x07', '\x1b'])
def test_is_package_installed_control_chars(char):
    from humboldt import is_package_installed
    assert is_package_installed(f"geopy{char}") is False

@pytest.mark.parametrize("char", ['\t', '\r', '\x07', '\x1b'])
def test_handle_direct_command_control_chars(char, capsys):
    from humboldt import handle_direct_command
    from unittest.mock import MagicMock
    mock_registry = MagicMock()
    mock_registry.invoke.return_value = "mock_output"
    result = handle_direct_command(f"/geocode test{char}test", mock_registry)
    assert result is True
    mock_registry.invoke.assert_called_once_with("geocode_locations", {"locations": f"test{char}test"})
    out, err = capsys.readouterr()
    assert out == "mock_output\n"
