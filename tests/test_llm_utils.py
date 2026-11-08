import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

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

@pytest.mark.xfail(reason="Bug: accepts bool True as 1 for max_retries instead of rejecting invalid type")
def test_call_llm_with_retry_bool_true():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message={'ok': True})])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, max_retries=True, model='m', messages=[])
    if response == expected_response:
        pytest.fail("Bug: successfully processed bool True as an integer")


@pytest.mark.xfail(reason="Bug: accepts bool False as 0 for max_retries instead of rejecting invalid type")
def test_call_llm_with_retry_bool_false():
    client = MagicMock()

    try:
        call_llm_with_retry(client, max_retries=False, model='m', messages=[])
    except ValueError as e:
        if "LLM call failed after False attempts" in str(e):
            pytest.fail("Bug: successfully processed bool False as an integer and failed gracefully on loop")
        raise
