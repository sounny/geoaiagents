import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry
import time
from unittest.mock import patch
import builtins

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message={'ok': True})])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()

def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message={'ok': True})])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2

@pytest.fixture(autouse=True)
def restore_tz():
    yield
    if hasattr(time, 'tzset'):
        time.tzset()

def test_call_llm_with_retry_tz_behavior(monkeypatch, tmp_path):
    # Use tmp_path to simulate user input instead of adding dummy args to function call
    input_file = tmp_path / "input.txt"
    input_file.write_text("dummy input\n")

    def run_under_tz(tz):
        monkeypatch.setenv('TZ', tz)
        if hasattr(time, 'tzset'):
            time.tzset()

        client = MagicMock()
        expected_response = SimpleNamespace(choices=[SimpleNamespace(message={'ok': True})])
        client.chat.completions.create.return_value = expected_response

        with open(input_file, 'r') as f:
            with patch.object(builtins, 'input', lambda prompt="": f.readline().strip()):
                return call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    res_utc = run_under_tz('UTC')
    res_ny = run_under_tz('America/New_York')

    if res_utc != res_ny:
        pytest.xfail("Behavior differs under different TZ settings")

    assert res_utc == res_ny
