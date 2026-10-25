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

def test_build_parser_wrong_type():
    with pytest.raises(TypeError):
        humboldt.build_parser(123)

def test_check_and_install_dependencies_wrong_type(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(TypeError):
        humboldt.check_and_install_dependencies(123)

@pytest.mark.xfail(reason="raises AttributeError instead of TypeError for invalid type")
def test_is_package_installed_wrong_type():
    with pytest.raises(TypeError):
        humboldt.is_package_installed(123)

@pytest.mark.xfail(reason="raises AttributeError instead of TypeError when user_input is not a string")
def test_handle_direct_command_wrong_type():
    with pytest.raises(TypeError):
        humboldt.handle_direct_command(123, MagicMock())

@pytest.mark.xfail(reason="raises AttributeError instead of TypeError for invalid args")
def test_execute_tool_loop_wrong_type_args():
    with pytest.raises(TypeError):
        humboldt.execute_tool_loop(MagicMock(), 123, [], [], MagicMock())

@pytest.mark.xfail(reason="raises AttributeError instead of TypeError for invalid messages")
def test_execute_tool_loop_wrong_type_messages():
    args = MagicMock()
    args.max_steps = 0
    with pytest.raises(TypeError):
        humboldt.execute_tool_loop(MagicMock(), args, 123, [], MagicMock())

@pytest.mark.xfail(reason="raises ValueError from retries or AttributeError instead of TypeError for invalid client")
def test_execute_tool_loop_wrong_type_client():
    args = MagicMock()
    args.max_steps = 0
    with pytest.raises(TypeError):
        humboldt.execute_tool_loop(123, args, [], [], MagicMock())

@pytest.mark.xfail(reason="raises AttributeError instead of TypeError for invalid messages type")
def test_chat_loop_wrong_type_messages(mocker):
    mocker.patch('builtins.input', side_effect=['hello', 'exit'])
    mocker.patch('humboldt.call_llm_with_retry')
    args = MagicMock()
    args.debug = False
    with pytest.raises(TypeError):
        humboldt.chat_loop(MagicMock(), args, 123, MagicMock(), [], MagicMock())

def test_main_wrong_type(mocker):
    mocker.patch('humboldt.check_and_install_dependencies')
    with pytest.raises(TypeError):
        humboldt.main(123)

@pytest.mark.xfail(reason="raises TypeError with generic message or fails inside for wrong arg type in mock")
def test_call_llm_with_retry_wrong_type(mocker):
    with pytest.raises(TypeError):
        from llm_utils import call_llm_with_retry
        call_llm_with_retry(123)
