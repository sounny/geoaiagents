import pytest
import sys
from unittest.mock import patch, MagicMock
from humboldt import main, handle_direct_command, is_package_installed

@pytest.mark.xfail(reason="Humboldt calls LLM for empty or whitespace-only input instead of a no-op")
def test_humboldt_empty_input(mocker, capsys):
    mocker.patch('humboldt.check_and_install_dependencies')
    mocker.patch('openai.OpenAI')

    mock_input = mocker.patch('builtins.input', side_effect=['', '   ', '\t\n', 'exit'])

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

def test_handle_direct_command_empty_input():
    mock_registry = MagicMock()
    for input_str in ["", "   ", "\t\n"]:
        assert handle_direct_command(input_str, mock_registry) is False

def test_handle_direct_command_padded_input():
    mock_registry = MagicMock()
    # It should not recognize the command because it expects exactly "/geocode " at start
    assert handle_direct_command("\t\n/geocode \n\t", mock_registry) is False

    # But if padded after the command, it should extract the payload
    # Mocking tool_registry.invoke to avoid actual invocation
    mock_registry.invoke.return_value = "Result"
    assert handle_direct_command("/geocode \t\nParis\n\t", mock_registry) is True
    mock_registry.invoke.assert_called_with("geocode_locations", {"locations": "\t\nParis\n\t"})

def test_is_package_installed_empty_input():
    for input_str in ["", "   ", "\t\n"]:
        assert is_package_installed(input_str) is False

def test_is_package_installed_padded_input():
    # is_package_installed strips nothing and just tries to find the module.
    # An invalid module name padded with whitespace will just fail to import.
    assert is_package_installed("\t\nrequests\n\t") is False
