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

def test_handle_direct_command_large_string():
    from humboldt import handle_direct_command
    tool_registry = MagicMock()
    tool_registry.invoke.return_value = "Success"

    # 1 million character string
    large_payload = "A" * 1000000
    user_input = f"/geocode {large_payload}"

    result = handle_direct_command(user_input, tool_registry)

    assert result is True
    tool_registry.invoke.assert_called_once_with("geocode_locations", {"locations": large_payload})

def test_execute_tool_loop_large_lists_and_dicts(mocker):
    from humboldt import execute_tool_loop
    from types import SimpleNamespace

    mock_client = MagicMock()

    # Mock LLM response
    mock_response = MagicMock()
    mock_message = SimpleNamespace(content="Finished task with large payload", function_call=None)
    mock_response.choices = [SimpleNamespace(message=mock_message)]

    mock_call_llm = mocker.patch("humboldt.call_llm_with_retry", return_value=mock_response)

    args = SimpleNamespace(max_steps=3, model="test-model", debug=False)

    # 10,000 items in the list
    large_messages = [{"role": "user", "content": f"Message {i}"} for i in range(10000)]

    # Large dictionary for functions
    large_functions = {f"function_{i}": {"description": f"Description for {i}", "parameters": {"type": "object", "properties": {}}} for i in range(1000)}
    large_functions_list = [{"name": k, "description": v["description"], "parameters": v["parameters"]} for k, v in large_functions.items()]

    def run_tool_call(tool_name, raw_args):
        return "Tool output"

    # Should not crash and should call the LLM
    execute_tool_loop(mock_client, args, large_messages, large_functions_list, run_tool_call)

    assert mock_call_llm.call_count == 1

def test_chat_loop_large_inputs(mocker):
    from humboldt import chat_loop
    from types import SimpleNamespace

    mock_client = MagicMock()
    args = SimpleNamespace(max_steps=3, model="test-model", debug=False)
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    tool_registry = MagicMock()
    functions = []

    def run_tool_call(tool_name, raw_args):
        return "Tool output"

    mock_execute = mocker.patch("humboldt.execute_tool_loop")

    # Very large input string (1 million chars) followed by 'exit'
    large_input = "B" * 1000000
    mocker.patch('builtins.input', side_effect=[large_input, "exit"])

    # The chat_loop should handle this without exceptions and call execute_tool_loop
    chat_loop(mock_client, args, messages, tool_registry, functions, run_tool_call)

    # Assert execute was called once with the large message appended
    assert mock_execute.call_count == 1
    assert len(messages) == 2
    assert messages[1]["content"] == large_input
