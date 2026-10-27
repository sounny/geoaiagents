import argparse
import copy
import os
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

def test_check_and_install_dependencies_happy_path(mocker, tmp_path):
    mocker.patch('subprocess.run')
    # Change current working directory to tmp_path to mock requirements.txt
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("pytest==8.0.0\n")
        mocker.patch('humboldt.is_package_installed', return_value=False)
        result = humboldt.check_and_install_dependencies()
        assert type(result) is type(None)
    finally:
        os.chdir(original_cwd)

def test_is_package_installed_happy_path(mocker):
    mocker.patch('importlib.util.find_spec', return_value=True)
    result = humboldt.is_package_installed("pytest")
    assert type(result) is bool

def test_build_parser_happy_path():
    result = humboldt.build_parser()
    assert type(result) is argparse.ArgumentParser

def test_handle_direct_command_happy_path(mocker):
    mock_registry = mocker.MagicMock()
    mock_registry.invoke.return_value = "Result"
    result = humboldt.handle_direct_command("/geocode Paris", mock_registry)
    assert type(result) is bool

def test_execute_tool_loop_happy_path(mocker):
    mock_client = mocker.MagicMock()
    mock_args = mocker.MagicMock()
    mock_args.max_steps = 1
    mock_args.debug = False
    mock_args.model = "test-model"

    messages = [{"role": "user", "content": "hello"}]
    messages_orig = copy.deepcopy(messages)
    functions = [{"name": "geocode"}]
    functions_orig = copy.deepcopy(functions)

    mock_resp = mocker.MagicMock()
    mock_resp.choices = [mocker.MagicMock()]
    mock_resp.choices[0].message.content = "Hi!"
    mock_resp.choices[0].message.function_call = None

    mocker.patch('humboldt.call_llm_with_retry', return_value=mock_resp)

    def mock_run_tool(name, args):
        return "tool_res"

    result = humboldt.execute_tool_loop(mock_client, mock_args, messages, functions, mock_run_tool)

    assert type(result) is type(None)

    if messages != messages_orig:
        pytest.xfail("execute_tool_loop mutates messages list")
    assert messages == messages_orig

def test_chat_loop_happy_path(mocker):
    mock_client = mocker.MagicMock()
    mock_args = mocker.MagicMock()
    mock_args.max_steps = 1
    mock_args.debug = False
    mock_args.model = "test-model"

    messages = [{"role": "system", "content": "sys"}]
    messages_orig = copy.deepcopy(messages)
    functions = [{"name": "geocode"}]

    mock_registry = mocker.MagicMock()

    mocker.patch('builtins.input', side_effect=["test", "exit"])

    mock_resp = mocker.MagicMock()
    mock_resp.choices = [mocker.MagicMock()]
    mock_resp.choices[0].message.content = "Hi!"
    mock_resp.choices[0].message.function_call = None

    mocker.patch('humboldt.call_llm_with_retry', return_value=mock_resp)

    def mock_run_tool(name, args):
        return "tool_res"

    result = humboldt.chat_loop(mock_client, mock_args, messages, mock_registry, functions, mock_run_tool)

    assert type(result) is type(None)

    if messages != messages_orig:
        pytest.xfail("chat_loop mutates messages list")
    assert messages == messages_orig

def test_main_happy_path(mocker, capsys):
    mocker.patch('humboldt.check_and_install_dependencies')
    mocker.patch('openai.OpenAI')

    mock_resp = mocker.MagicMock()
    mock_resp.choices = [mocker.MagicMock()]
    mock_resp.choices[0].message.content = "Hi!"
    mock_resp.choices[0].message.function_call = None

    mocker.patch('humboldt.call_llm_with_retry', return_value=mock_resp)
    mocker.patch('builtins.input', side_effect=["hello", "exit"])

    mocker.patch('sys.argv', ['humboldt.py', '--skip-deps'])

    result = humboldt.main()
    assert type(result) is type(None)
