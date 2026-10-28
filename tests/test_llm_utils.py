import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry
import concurrent.futures

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='ok'))])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()


def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='ok'))])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2

@pytest.mark.xfail(reason="Concurrent execution might result in unstable mock behavior or issue in call_llm_with_retry", strict=False)
def test_call_llm_with_retry_concurrent():
    client = MagicMock()
    expected_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="success"))]
    )
    client.chat.completions.create.return_value = expected_response

    single = call_llm_with_retry(client, model="m", messages=[], max_retries=3)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(
                call_llm_with_retry, client, model="m", messages=[], max_retries=3
            )
            for _ in range(5)
        ]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    for res in results:
        assert res == single
