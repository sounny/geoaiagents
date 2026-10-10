import pytest
from unittest.mock import MagicMock
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_happy_path_single_call_success():
    client = MagicMock()

    fake_response = MagicMock()
    fake_response.choices = ["some_choice"]

    client.chat.completions.create.return_value = fake_response

    result = call_llm_with_retry(client, max_retries=3, model="test-model", messages=[])

    assert result == fake_response
    client.chat.completions.create.assert_called_once()
