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
from unittest.mock import MagicMock, patch
from humboldt import (
    build_parser,
    chat_loop,
    check_and_install_dependencies,
    execute_tool_loop,
    handle_direct_command,
    is_package_installed,
    main,
)

@pytest.mark.xfail(reason="argparse.ArgumentParser objects do not compare equal to their deepcopies")
def test_build_parser_deepcopy():
    res = build_parser()
    assert res == copy.deepcopy(res)

def test_check_and_install_dependencies_deepcopy(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    res = check_and_install_dependencies()
    assert res == copy.deepcopy(res)

@patch('importlib.util.find_spec', return_value=None)
def test_is_package_installed_deepcopy(mock_find_spec):
    res = is_package_installed('openai')
    assert res == copy.deepcopy(res)

def test_handle_direct_command_deepcopy():
    registry = MagicMock()
    res = handle_direct_command('/geocode Paris', registry)
    assert res == copy.deepcopy(res)

@patch('humboldt.call_llm_with_retry')
def test_execute_tool_loop_deepcopy(mock_call_llm_with_retry):
    client = MagicMock()
    args = MagicMock()
    args.max_steps = 0
    messages = []
    functions = []

    mock_response = MagicMock()
    mock_message = MagicMock()
    mock_message.function_call = None
    mock_message.content = "Hello"
    mock_response.choices = [MagicMock(message=mock_message)]
    mock_call_llm_with_retry.return_value = mock_response

    res = execute_tool_loop(client, args, messages, functions, lambda x, y: None)
    assert res == copy.deepcopy(res)

@patch('builtins.input', side_effect=['exit'])
def test_chat_loop_deepcopy(mock_input):
    client = MagicMock()
    args = MagicMock()
    messages = []
    registry = MagicMock()
    functions = []

    res = chat_loop(client, args, messages, registry, functions, lambda x, y: None)
    assert res == copy.deepcopy(res)

@patch('sys.argv', ['humboldt.py', '--skip-deps'])
@patch.dict('sys.modules', {'openai': MagicMock(), 'tool_registry': MagicMock()})
@patch('humboldt.chat_loop')
def test_main_deepcopy(mock_chat_loop, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    res = main()
    assert res == copy.deepcopy(res)
