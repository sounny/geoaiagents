import pytest
from unittest.mock import MagicMock
from llm_utils import call_llm_with_retry
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
import json
import logging

def test_call_llm_with_retry_immediate_success(tmp_path):
    client = MagicMock()
    # Construct a more realistic mock that mimics the actual expected class
    expected_response = ChatCompletion(
        id="test-id",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content="ok",
                    role="assistant"
                )
            )
        ],
        created=1234567890,
        model="gpt-4",
        object="chat.completion"
    )
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='gpt-4', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()
    assert type(response) is ChatCompletion

    # Asserting type to ensure test verifies the return type
    assert isinstance(response, ChatCompletion)
    # The return object doesn't strictly yield a dict directly, but we can verify its attributes
    assert hasattr(response, 'choices')

def test_call_llm_with_retry_timeout_then_success(mocker, tmp_path):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = ChatCompletion(
        id="test-id",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content="ok",
                    role="assistant"
                )
            )
        ],
        created=1234567890,
        model="gpt-4",
        object="chat.completion"
    )
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='gpt-4', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2
    assert type(response) is ChatCompletion
    assert isinstance(response, ChatCompletion)
