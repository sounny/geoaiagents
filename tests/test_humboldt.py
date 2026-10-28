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

@pytest.mark.xfail(reason="Bug: is_package_installed is case-sensitive and does not normalize package names")
def test_is_package_installed_upper(mocker):
    from humboldt import is_package_installed
    mocker.patch("importlib.util.find_spec", side_effect=lambda n: mocker.MagicMock() if n == "openai" else None)
    assert is_package_installed("OPENAI") is True

@pytest.mark.xfail(reason="Bug: is_package_installed is case-sensitive and does not normalize package names")
def test_is_package_installed_mixed(mocker):
    from humboldt import is_package_installed
    mocker.patch("importlib.util.find_spec", side_effect=lambda n: mocker.MagicMock() if n == "openai" else None)
    assert is_package_installed("OpenAi") is True

def test_is_package_installed_lower(mocker):
    from humboldt import is_package_installed
    mocker.patch("importlib.util.find_spec", side_effect=lambda n: mocker.MagicMock() if n == "openai" else None)
    assert is_package_installed("openai") is True

def test_handle_direct_command_lower(mocker):
    from humboldt import handle_direct_command
    registry = mocker.Mock()
    result = handle_direct_command("/geocode paris", registry)
    assert result is True
    registry.invoke.assert_called_with("geocode_locations", {"locations": "paris"})

@pytest.mark.xfail(reason="Bug: handle_direct_command is case-sensitive for slash commands")
def test_handle_direct_command_upper(mocker):
    from humboldt import handle_direct_command
    registry = mocker.Mock()
    result = handle_direct_command("/GEOCODE paris", registry)
    assert result is True
    registry.invoke.assert_called_with("geocode_locations", {"locations": "paris"})

@pytest.mark.xfail(reason="Bug: handle_direct_command is case-sensitive for slash commands")
def test_handle_direct_command_mixed(mocker):
    from humboldt import handle_direct_command
    registry = mocker.Mock()
    result = handle_direct_command("/GeoCode paris", registry)
    assert result is True
    registry.invoke.assert_called_with("geocode_locations", {"locations": "paris"})
