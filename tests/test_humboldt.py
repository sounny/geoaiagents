import pytest
import sys
from unittest.mock import patch, MagicMock
from humboldt import main, call_llm_with_retry

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

def test_call_llm_with_retry_true(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = "test"
    client.chat.completions.create.return_value = mock_response

    result = call_llm_with_retry(client, max_retries=True)
    assert result == mock_response
    assert client.chat.completions.create.call_count == 1

@pytest.mark.xfail(raises=ValueError, strict=True, reason="max_retries=False evaluated as 0 in range(False), raising ValueError before retrying")
def test_call_llm_with_retry_false(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = "test"
    client.chat.completions.create.return_value = mock_response

    call_llm_with_retry(client, max_retries=False)

@pytest.mark.xfail(raises=TypeError, strict=True, reason="max_retries=-0.0 fails because range() does not accept floats")
def test_call_llm_with_retry_negative_zero(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = "test"
    client.chat.completions.create.return_value = mock_response

    call_llm_with_retry(client, max_retries=-0.0)
