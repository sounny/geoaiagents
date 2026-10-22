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

def test_humboldt_log_normal(mocker, caplog):
    import logging
    caplog.set_level(logging.DEBUG)

    mocker.patch('humboldt.check_and_install_dependencies')

    mocker.patch('builtins.input', side_effect=['hello', 'exit'])
    mocker.patch('sys.argv', ['humboldt.py', '--api-key', 'secret-api-key-42'])

    mock_create = mocker.patch('openai.resources.chat.completions.Completions.create')
    mock_response = mocker.MagicMock()
    mock_response.choices = [mocker.MagicMock()]
    mock_response.choices[0].message.content = "I am a helpful assistant."
    mock_response.choices[0].message.function_call = None
    mock_create.return_value = mock_response

    main()

    # Assert there are no warnings or errors
    assert not any(record.levelno >= logging.WARNING for record in caplog.records), "Expected no warnings/errors on normal run"

    # Assert API keys are not leaked in the logs
    assert "secret-api-key-42" not in caplog.text, "Secret API key leaked in logs"

@pytest.mark.xfail(reason="Humboldt propagates unhandled ValueError on API failure instead of logging gracefully")
def test_humboldt_log_failing(mocker, caplog):
    import logging
    caplog.set_level(logging.DEBUG)

    mocker.patch('humboldt.check_and_install_dependencies')

    mocker.patch('builtins.input', side_effect=['hello', 'exit'])
    mocker.patch('sys.argv', ['humboldt.py', '--api-key', 'secret-api-key-42'])

    mock_create = mocker.patch('openai.resources.chat.completions.Completions.create', side_effect=ValueError("API connection failed"))

    # It should not raise an unhandled exception to the top level
    main()

    # Assert warning and error level logs exist from call_llm_with_retry
    assert any(record.levelno == logging.WARNING for record in caplog.records), "Expected WARNING logs"
    assert any(record.levelno == logging.ERROR for record in caplog.records), "Expected ERROR logs"

    # Assert API keys are not leaked in the logs
    assert "secret-api-key-42" not in caplog.text, "Secret API key leaked in logs"
