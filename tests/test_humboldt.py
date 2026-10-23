import logging
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


def test_humboldt_logging_normal(caplog, mocker):
    mocker.patch('humboldt.check_and_install_dependencies')
    mocker.patch('openai.OpenAI')

    mock_input = mocker.patch('builtins.input', side_effect=['Hello', 'exit'])
    mock_call_llm = mocker.patch('humboldt.call_llm_with_retry')

    mock_msg = mocker.MagicMock()
    mock_msg.content = "I am a helpful agent."
    mock_msg.function_call = None
    mock_choice = mocker.MagicMock()
    mock_choice.message = mock_msg
    mock_response = mocker.MagicMock()
    mock_response.choices = [mock_choice]

    mock_call_llm.return_value = mock_response

    mocker.patch.object(sys, 'argv', ['humboldt.py', '--debug'])

    with caplog.at_level(logging.DEBUG):
        main()

    records = [(r.name, r.levelname) for r in caplog.records if r.name == "root"]
    assert records == []

def test_humboldt_logging_error(caplog, mocker):
    mocker.patch('humboldt.check_and_install_dependencies')

    mock_client = mocker.MagicMock()
    mock_client.chat.completions.create.side_effect = ValueError("Network Error")

    mocker.patch('openai.OpenAI', return_value=mock_client)
    mock_input = mocker.patch('builtins.input', side_effect=['Hello', 'exit'])
    mocker.patch('time.sleep')
    mocker.patch.object(sys, 'argv', ['humboldt.py', '--debug'])

    with caplog.at_level(logging.DEBUG):
        try:
            main()
        except ValueError:
            pass

    records = [(r.name, r.levelname) for r in caplog.records if r.name == "root"]
    assert records == [('root', 'WARNING'), ('root', 'WARNING'), ('root', 'ERROR')]
