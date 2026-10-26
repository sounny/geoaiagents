from unittest.mock import MagicMock
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

def test_execute_tool_loop_iter_vs_list(monkeypatch):
    from humboldt import execute_tool_loop
    client = MagicMock()
    args = MagicMock(max_steps=1, debug=False)

    mock_msg = MagicMock()
    mock_msg.function_call = MagicMock()
    mock_msg.function_call.name = "test_func"
    mock_msg.function_call.arguments = "{}"
    mock_msg.content = None

    mock_msg2 = MagicMock()
    mock_msg2.function_call = None
    mock_msg2.content = "Done"

    mock_choice = MagicMock()
    mock_choice.message = mock_msg
    mock_choice2 = MagicMock()
    mock_choice2.message = mock_msg2

    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]
    mock_resp2 = MagicMock()
    mock_resp2.choices = [mock_choice2]

    client.chat.completions.create.side_effect = [mock_resp, mock_resp2]

    messages_list = [{"role": "system", "content": "hi"}]
    functions_list = [{"name": "test_func"}]

    execute_tool_loop(client, args, messages_list, functions_list, lambda x, y: "result")

    assert len(messages_list) == 3
    assert messages_list[-1]["role"] == "function"

@pytest.mark.xfail(raises=AttributeError, reason="execute_tool_loop uses append which fails for iterables")
def test_execute_tool_loop_iter_vs_list_iterable(monkeypatch):
    from humboldt import execute_tool_loop
    client = MagicMock()
    args = MagicMock(max_steps=1, debug=False)

    mock_msg = MagicMock()
    mock_msg.function_call = MagicMock()
    mock_msg.function_call.name = "test_func"
    mock_msg.function_call.arguments = "{}"
    mock_msg.content = None

    mock_choice = MagicMock()
    mock_choice.message = mock_msg

    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]

    client.chat.completions.create.return_value = mock_resp

    messages_iter = iter([{"role": "system", "content": "hi"}])
    functions_iter = iter([{"name": "test_func"}])

    execute_tool_loop(client, args, messages_iter, functions_iter, lambda x, y: "result")

def test_chat_loop_iter_vs_list(monkeypatch):
    from humboldt import chat_loop
    client = MagicMock()
    args = MagicMock(max_steps=0, debug=False)
    registry = MagicMock()
    registry.invoke.return_value = False

    inputs = ["hello", "exit"]
    monkeypatch.setattr('builtins.input', lambda _: inputs.pop(0))

    mock_msg = MagicMock()
    mock_msg.function_call = None
    mock_msg.content = "Done"
    mock_choice = MagicMock()
    mock_choice.message = mock_msg
    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]
    client.chat.completions.create.return_value = mock_resp

    messages = [{"role": "system", "content": "hi"}]
    functions = [{"name": "test"}]

    chat_loop(client, args, messages, registry, functions, lambda x, y: None)

@pytest.mark.xfail(raises=AttributeError, reason="chat_loop uses append and len which fails for iterables")
def test_chat_loop_iter_vs_list_iterable(monkeypatch):
    from humboldt import chat_loop
    client = MagicMock()
    args = MagicMock(max_steps=0, debug=False)
    registry = MagicMock()
    registry.invoke.return_value = False

    inputs = ["hello", "exit"]
    monkeypatch.setattr('builtins.input', lambda _: inputs.pop(0))

    mock_msg = MagicMock()
    mock_msg.function_call = None
    mock_msg.content = "Done"
    mock_choice = MagicMock()
    mock_choice.message = mock_msg
    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]
    client.chat.completions.create.return_value = mock_resp

    messages = iter([{"role": "system", "content": "hi"}])
    functions = iter([{"name": "test"}])

    chat_loop(client, args, messages, registry, functions, lambda x, y: None)
