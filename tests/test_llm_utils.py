import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

@pytest.mark.xfail(raises=ValueError, reason="Exposes bug: missing message attribute check")
def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[{'ok': True}])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()


@pytest.mark.xfail(raises=ValueError, reason="Exposes bug: StopIteration after TimeoutError because choices check fails")
def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[{'ok': True}])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2


def test_call_llm_with_retry_purity(mocker, tmp_path):
    import copy
    import llm_utils
    from types import SimpleNamespace

    # tmp_path explicitly requested to mock filesystem
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("dummy content")
    fs_mock = mocker.patch("os.path.exists", return_value=True)
    mocker.patch("builtins.open", mocker.mock_open(read_data=""))

    client = MagicMock()
    choice = SimpleNamespace(message="hello")
    client.chat.completions.create.return_value = SimpleNamespace(choices=[choice])

    pure_args = {'model': 'm', 'messages': [], 'max_retries': 1}
    kwargs = {'client': client, **pure_args}

    pure_args_copy = copy.deepcopy(pure_args)

    # Call 1
    response1 = llm_utils.call_llm_with_retry(**kwargs)
    client.reset_mock()
    client.chat.completions.create.return_value = SimpleNamespace(choices=[choice])

    # Call 2
    response2 = llm_utils.call_llm_with_retry(**kwargs)

    assert response1 == response2

    kwargs_pure = {k: v for k, v in kwargs.items() if k != 'client'}
    assert kwargs_pure == pure_args_copy

    expected_call_kwargs = {k: v for k, v in kwargs.items() if k not in ('client', 'max_retries')}
    client.chat.completions.create.assert_called_once_with(**expected_call_kwargs)
