import humboldt
import argparse
from _pytest.outcomes import Failed
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

@pytest.mark.parametrize("invalid_retries", [
    pytest.param(float("nan"), marks=pytest.mark.xfail(raises=TypeError, reason="Fails with internal TypeError from range() instead of explicitly validating type")),
    pytest.param(float("inf"), marks=pytest.mark.xfail(raises=TypeError, reason="Fails with internal TypeError from range() instead of explicitly validating type")),
    pytest.param(float("-inf"), marks=pytest.mark.xfail(raises=TypeError, reason="Fails with internal TypeError from range() instead of explicitly validating type")),
    pytest.param(-0.0, marks=pytest.mark.xfail(raises=TypeError, reason="Fails with internal TypeError from range() instead of explicitly validating type")),
])
def test_call_llm_with_retry_float_args(invalid_retries, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    client = MagicMock()
    with pytest.raises(ValueError):
        humboldt.call_llm_with_retry(client, max_retries=invalid_retries)

@pytest.mark.parametrize("invalid_max_steps", [
    pytest.param(float("nan"), marks=pytest.mark.xfail(raises=Failed, reason="Silently breaks instead of raising error for invalid max_steps type")),
    pytest.param(float("inf"), marks=pytest.mark.xfail(raises=Failed, reason="Silently breaks instead of raising error for invalid max_steps type")),
    pytest.param(float("-inf"), marks=pytest.mark.xfail(raises=Failed, reason="Silently breaks instead of raising error for invalid max_steps type")),
    pytest.param(-0.0, marks=pytest.mark.xfail(raises=Failed, reason="Silently breaks instead of raising error for invalid max_steps type")),
])
def test_execute_tool_loop_float_args(invalid_max_steps, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "test"
    mock_response.choices[0].message.function_call = None
    client.chat.completions.create.return_value = mock_response

    args = argparse.Namespace(max_steps=invalid_max_steps, debug=False, model='test')
    messages = []
    functions = []
    def run_tool_call(name, args): return ""

    with pytest.raises(TypeError):
        humboldt.execute_tool_loop(client, args, messages, functions, run_tool_call)
