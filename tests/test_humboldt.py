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

def test_is_package_installed_surrogate():
    from humboldt import is_package_installed
    assert is_package_installed("\ud800") is False

def test_handle_direct_command_surrogate_unmatched():
    from humboldt import handle_direct_command
    tool_registry = MagicMock()
    assert handle_direct_command("\ud800", tool_registry) is False

def test_handle_direct_command_surrogate_matched():
    from humboldt import handle_direct_command
    tool_registry = MagicMock()
    tool_registry.invoke.return_value = "mocked"
    assert handle_direct_command("/geocode \ud800", tool_registry) is True

@pytest.mark.xfail(raises=UnicodeEncodeError, reason="Bug: Printing a string with surrogates crashes with UnicodeEncodeError")
def test_handle_direct_command_surrogate_print():
    from humboldt import handle_direct_command
    tool_registry = MagicMock()
    tool_registry.invoke.return_value = "\ud800"
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='strict')
    handle_direct_command("/geocode test", tool_registry)

@pytest.mark.xfail(raises=UnicodeEncodeError, reason="Bug: Printing a string with surrogates crashes with UnicodeEncodeError")
def test_execute_tool_loop_surrogate_print():
    import argparse
    from humboldt import execute_tool_loop
    client = MagicMock()
    args = argparse.Namespace(max_steps=3, debug=False, model="test")
    messages = []
    functions = []
    run_tool_call = MagicMock()

    mock_response = MagicMock()
    mock_message = MagicMock()
    mock_message.function_call = None
    mock_message.content = "\ud800"
    mock_response.choices = [MagicMock(message=mock_message)]

    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='strict')
    with patch('humboldt.call_llm_with_retry', return_value=mock_response):
        execute_tool_loop(client, args, messages, functions, run_tool_call)
