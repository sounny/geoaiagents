import warnings
import os
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

def test_build_parser_warnings():
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        humboldt.build_parser()

def test_chat_loop_warnings():
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        with patch('builtins.input', side_effect=['exit']):
            humboldt.chat_loop(MagicMock(), MagicMock(), [], MagicMock(), [], MagicMock())

def test_check_and_install_dependencies_warnings(tmp_path, monkeypatch):
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        monkeypatch.chdir(tmp_path)
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("pytest\n")
        with patch('humboldt.is_package_installed', return_value=True):
            humboldt.check_and_install_dependencies()

def test_execute_tool_loop_warnings():
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        client_mock = MagicMock()
        args_mock = MagicMock()
        args_mock.max_steps = 1
        messages = []
        functions = []
        with patch('humboldt.call_llm_with_retry') as call_llm_mock:
            call_llm_mock.return_value = MagicMock()
            call_llm_mock.return_value.choices[0].message.content = 'Hello'
            call_llm_mock.return_value.choices[0].message.function_call = None
            humboldt.execute_tool_loop(client_mock, args_mock, messages, functions, MagicMock())

def test_handle_direct_command_warnings():
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        registry_mock = MagicMock()
        humboldt.handle_direct_command('/geocode something', registry_mock)

def test_is_package_installed_warnings():
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        humboldt.is_package_installed('openai')

def test_main_warnings():
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        with patch.dict('sys.modules', {'openai': MagicMock(), 'tool_registry': MagicMock()}):
            with patch('sys.argv', ['humboldt.py']):
                with patch('humboldt.check_and_install_dependencies'):
                    with patch('builtins.input', side_effect=['exit']):
                        humboldt.main()
