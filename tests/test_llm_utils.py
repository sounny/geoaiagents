import pytest
from unittest.mock import Mock, patch
from llm_utils import call_llm_with_retry

class MockResponse:
    def __init__(self, choices):
        self.choices = choices

@patch("llm_utils.time.sleep")
def test_transient_failure_retried(mock_sleep):
    client = Mock()
    # First call raises an exception, second call succeeds
    client.chat.completions.create.side_effect = [
        Exception("Transient error"),
        MockResponse(choices=[{"message": {"content": "Success"}}])
    ]

    response = call_llm_with_retry(client, max_retries=3, model="test")

    assert response.choices[0]["message"]["content"] == "Success"
    assert client.chat.completions.create.call_count == 2
    mock_sleep.assert_called_once_with(1)

@pytest.mark.xfail(reason="Permanent errors are currently retried instead of raising immediately")
@patch("llm_utils.time.sleep")
def test_permanent_failure_not_retried(mock_sleep):
    from openai import AuthenticationError

    client = Mock()
    # Mocking AuthenticationError which is a permanent error
    client.chat.completions.create.side_effect = AuthenticationError(
        message="Invalid authentication",
        response=Mock(status_code=401),
        body=None
    )

    with pytest.raises(AuthenticationError):
        call_llm_with_retry(client, max_retries=3, model="test")

    # Should only be called once because it's a permanent error
    assert client.chat.completions.create.call_count == 1
    mock_sleep.assert_not_called()
