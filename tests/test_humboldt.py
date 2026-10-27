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

import argparse
import json
from humboldt import execute_tool_loop, chat_loop

def test_execute_tool_loop_config_object(mocker):
    client = mocker.MagicMock()
    mock_llm = mocker.patch("humboldt.call_llm_with_retry")
    mock_response = mocker.MagicMock()
    mock_response.choices = [mocker.MagicMock()]
    mock_response.choices[0].message.content = "Done"
    mock_response.choices[0].message.function_call = None
    mock_llm.return_value = mock_response

    args_obj = argparse.Namespace(max_steps=3, model="test", debug=False, extra_unknown_key="ignored")
    messages = []
    functions = []
    run_tool_call = mocker.MagicMock()

    execute_tool_loop(client, args_obj, messages, functions, run_tool_call)
    assert mock_llm.call_count == 1

def test_execute_tool_loop_dict(mocker, tmp_path):
    client = mocker.MagicMock()
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"max_steps": 3, "model": "test", "debug": False, "extra_unknown_key": "ignored"}))
    args_dict = json.loads(config_file.read_text())

    messages = []
    functions = []
    run_tool_call = mocker.MagicMock()

    try:
        execute_tool_loop(client, args_dict, messages, functions, run_tool_call)
    except AttributeError:
        pytest.xfail(reason="Bug: execute_tool_loop does not support dict config objects, expects attribute access")

def test_chat_loop_config_object(mocker):
    client = mocker.MagicMock()
    mocker.patch("builtins.input", side_effect=["exit"])

    args_obj = argparse.Namespace(max_steps=3, model="test", debug=False, extra_unknown_key="ignored")
    messages = []
    tool_registry = mocker.MagicMock()
    functions = []
    run_tool_call = mocker.MagicMock()

    chat_loop(client, args_obj, messages, tool_registry, functions, run_tool_call)
    assert True  # Exited cleanly

def test_chat_loop_dict(mocker, tmp_path):
    client = mocker.MagicMock()
    mocker.patch("builtins.input", side_effect=["test", "exit"])

    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"max_steps": 3, "model": "test", "debug": False, "extra_unknown_key": "ignored"}))
    args_dict = json.loads(config_file.read_text())

    messages = []
    tool_registry = mocker.MagicMock()
    functions = []
    run_tool_call = mocker.MagicMock()

    try:
        chat_loop(client, args_dict, messages, tool_registry, functions, run_tool_call)
    except AttributeError:
        pytest.xfail(reason="Bug: chat_loop does not support dict config objects, expects attribute access")
