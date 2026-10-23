import pytest
import sys
from unittest.mock import patch, MagicMock
import copy
import types
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


def test_execute_tool_loop_mutability(mocker):
    client = MagicMock()
    args = types.SimpleNamespace(max_steps=1, debug=False, model="test")
    messages = [{"role": "system", "content": "prompt"}]
    orig_messages = copy.deepcopy(messages)
    functions = [{"name": "func1"}]
    orig_functions = copy.deepcopy(functions)
    run_tool_call = MagicMock(return_value="tool_result")

    mock_response1 = types.SimpleNamespace()
    mock_message1 = types.SimpleNamespace(content=None, function_call=types.SimpleNamespace(name="func1", arguments="{}"))
    mock_response1.choices = [types.SimpleNamespace(message=mock_message1)]

    mock_response2 = types.SimpleNamespace()
    mock_message2 = types.SimpleNamespace(content="hello", function_call=None)
    mock_response2.choices = [types.SimpleNamespace(message=mock_message2)]

    mocker.patch('humboldt.call_llm_with_retry', side_effect=[mock_response1, mock_response2])
    mocker.patch('builtins.print')

    from humboldt import execute_tool_loop
    execute_tool_loop(client, args, messages, functions, run_tool_call)

    assert messages != orig_messages
    assert functions == orig_functions

def test_chat_loop_mutability(mocker):
    client = MagicMock()
    args = types.SimpleNamespace(max_steps=1, debug=False, model="test")
    messages = [{"role": "system", "content": "prompt"}]
    orig_messages = copy.deepcopy(messages)
    functions = [{"name": "func1"}]
    orig_functions = copy.deepcopy(functions)
    tool_registry = MagicMock()
    run_tool_call = MagicMock()

    mocker.patch('humboldt.handle_direct_command', return_value=False)
    mocker.patch('humboldt.execute_tool_loop')
    mocker.patch('builtins.input', side_effect=['hello', 'exit'])
    mocker.patch('builtins.print')

    from humboldt import chat_loop
    chat_loop(client, args, messages, tool_registry, functions, run_tool_call)

    assert messages != orig_messages
    assert functions == orig_functions
