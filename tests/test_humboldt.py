import humboldt
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

def test_is_package_installed_str():
    assert isinstance(humboldt.is_package_installed("openai"), bool)

@pytest.mark.xfail(raises=TypeError, reason="is_package_installed throws TypeError on bytes")
def test_is_package_installed_bytes():
    humboldt.is_package_installed(b"openai")

def test_handle_direct_command_str():
    tool_registry = MagicMock()
    tool_registry.invoke.return_value = "mock_output"
    assert humboldt.handle_direct_command("/geocode test", tool_registry) is True

@pytest.mark.xfail(raises=TypeError, reason="handle_direct_command throws TypeError on bytes")
def test_handle_direct_command_bytes():
    tool_registry = MagicMock()
    humboldt.handle_direct_command(b"/geocode test", tool_registry)
