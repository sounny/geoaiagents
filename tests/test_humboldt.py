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

@pytest.mark.xfail(reason="is_package_installed dictionary key lookup is case-sensitive", raises=AssertionError)
def test_is_package_installed_case_insensitivity(mocker):
    def fake_find_spec(name):
        if name == 'openai':
            return mocker.MagicMock()
        return None
    mocker.patch('importlib.util.find_spec', side_effect=fake_find_spec)

    import humboldt
    assert humboldt.is_package_installed("OPENAI") is True, "Should accept UPPER case dict key"
    assert humboldt.is_package_installed("OpenAI") is True, "Should accept Mixed case dict key"

@pytest.mark.xfail(reason="handle_direct_command command parsing is case-sensitive", raises=AssertionError)
def test_handle_direct_command_case_insensitivity(mocker):
    mock_reg = mocker.MagicMock()
    mock_reg.invoke.return_value = "Result"

    import humboldt
    assert humboldt.handle_direct_command("/GEOCODE Paris", mock_reg) is True, "Should accept UPPER case command"
    assert humboldt.handle_direct_command("/Geocode Paris", mock_reg) is True, "Should accept Mixed case command"
