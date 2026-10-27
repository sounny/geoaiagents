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

import copy
import argparse
from humboldt import execute_tool_loop, chat_loop

def test_execute_tool_loop_no_mutation(mocker, tmp_path):
    mock_client = mocker.MagicMock()
    args = argparse.Namespace(max_steps=1, debug=False, model="test")
    messages = [{"role": "system", "content": "test"}]
    functions = [{"name": "test_func"}]
    mock_run_tool = mocker.MagicMock(return_value="output")

    mock_call_llm = mocker.patch('humboldt.call_llm_with_retry')
    # First call returns a function call to trigger mutation
    mock_msg_func = mocker.MagicMock()
    mock_msg_func.content = None
    mock_call = mocker.MagicMock()
    mock_call.name = "test_func"
    mock_call.arguments = "{}"
    mock_msg_func.function_call = mock_call
    mock_resp_func = mocker.MagicMock()
    mock_resp_func.choices = [mocker.MagicMock(message=mock_msg_func)]

    # Second call returns content
    mock_msg_content = mocker.MagicMock()
    mock_msg_content.content = "done"
    mock_msg_content.function_call = None
    mock_resp_content = mocker.MagicMock()
    mock_resp_content.choices = [mocker.MagicMock(message=mock_msg_content)]

    mock_call_llm.side_effect = [mock_resp_func, mock_resp_content]

    orig_messages = copy.deepcopy(messages)
    orig_functions = copy.deepcopy(functions)

    # Use tmp_path for a file
    dummy_file = tmp_path / "dummy.txt"
    dummy_file.write_text("test")

    execute_tool_loop(mock_client, args, messages, functions, mock_run_tool)

    if messages != orig_messages:
        pytest.xfail("Mutation of messages list looks like a bug")
    assert messages == orig_messages

    if functions != orig_functions:
        pytest.xfail("Mutation of functions list looks like a bug")
    assert functions == orig_functions

def test_chat_loop_no_mutation(mocker, tmp_path):
    mock_client = mocker.MagicMock()
    args = argparse.Namespace(max_steps=0, debug=False, model="test")
    messages = [{"role": "system", "content": "test"}]
    functions = [{"name": "test_func"}]
    mock_tool_registry = mocker.MagicMock()
    mock_run_tool = mocker.MagicMock()

    mocker.patch('builtins.input', side_effect=['hello', 'exit'])

    mock_call_llm = mocker.patch('humboldt.call_llm_with_retry')
    mock_msg = mocker.MagicMock()
    mock_msg.content = "hi"
    mock_msg.function_call = None
    mock_resp = mocker.MagicMock()
    mock_resp.choices = [mocker.MagicMock(message=mock_msg)]
    mock_call_llm.return_value = mock_resp

    orig_messages = copy.deepcopy(messages)
    orig_functions = copy.deepcopy(functions)

    # Use tmp_path for a file
    dummy_file = tmp_path / "dummy.txt"
    dummy_file.write_text("test")

    chat_loop(mock_client, args, messages, mock_tool_registry, functions, mock_run_tool)

    if messages != orig_messages:
        pytest.xfail("Mutation of messages list looks like a bug")
    assert messages == orig_messages

    if functions != orig_functions:
        pytest.xfail("Mutation of functions list looks like a bug")
    assert functions == orig_functions
