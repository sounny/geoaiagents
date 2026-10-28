import pytest
import sys
from unittest.mock import patch, MagicMock
import humboldt
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

def test_execute_tool_loop_keeps_repeated_messages(mocker):
    mock_call_llm = mocker.patch('humboldt.call_llm_with_retry')
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.function_call = None
    mock_response.choices[0].message.content = "mock response"
    mock_call_llm.return_value = mock_response

    client = MagicMock()
    args = MagicMock()
    args.max_steps = 0
    args.debug = False

    messages = [
        {"role": "user", "content": "hello"},
        {"role": "user", "content": "hello"}
    ]
    functions = [{"name": "func1"}]

    run_tool_call = MagicMock()

    humboldt.execute_tool_loop(client, args, messages, functions, run_tool_call)

    called_messages = mock_call_llm.call_args[1]["messages"]
    assert called_messages == messages

@pytest.mark.xfail(raises=AssertionError, reason="Humboldt keeps duplicate tool definitions, which looks like a bug")
def test_execute_tool_loop_repeated_functions_bug(mocker):
    mock_call_llm = mocker.patch('humboldt.call_llm_with_retry')
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.function_call = None
    mock_response.choices[0].message.content = "mock response"
    mock_call_llm.return_value = mock_response

    client = MagicMock()
    args = MagicMock()
    args.max_steps = 0
    args.debug = False

    messages = [{"role": "user", "content": "hello"}]
    functions = [
        {"name": "func1"},
        {"name": "func1"}
    ]

    run_tool_call = MagicMock()

    humboldt.execute_tool_loop(client, args, messages, functions, run_tool_call)

    called_functions = mock_call_llm.call_args[1]["functions"]
    assert len(called_functions) == 1

def test_chat_loop_keeps_repeated_messages(mocker):
    mocker.patch('builtins.input', side_effect=['hello', 'hello', 'exit'])
    mock_execute = mocker.patch('humboldt.execute_tool_loop')

    client = MagicMock()
    args = MagicMock()
    args.debug = False

    messages = []
    tool_registry = MagicMock()
    functions = []
    run_tool_call = MagicMock()

    humboldt.chat_loop(client, args, messages, tool_registry, functions, run_tool_call)

    assert len(messages) == 2
    assert messages[0] == {"role": "user", "content": "hello"}
    assert messages[1] == {"role": "user", "content": "hello"}
