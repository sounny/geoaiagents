import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message='ok')])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()


def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message='ok')])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2

import unicodedata

@pytest.mark.xfail(raises=AssertionError, strict=True, reason="Bug: Unicode NFC and NFD strings are treated differently")
def test_call_llm_with_retry_nfc_nfd_equivalence():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message='ok')])
    client.chat.completions.create.return_value = expected_response

    s_nfc = unicodedata.normalize('NFC', 'café')
    s_nfd = unicodedata.normalize('NFD', 'café')

    call_llm_with_retry(client, model='m', messages=[{'role': 'user', 'content': s_nfc}], max_retries=1)
    call_args_nfc = client.chat.completions.create.call_args

    client.chat.completions.create.reset_mock()

    call_llm_with_retry(client, model='m', messages=[{'role': 'user', 'content': s_nfd}], max_retries=1)
    call_args_nfd = client.chat.completions.create.call_args

    assert call_args_nfc == call_args_nfd
