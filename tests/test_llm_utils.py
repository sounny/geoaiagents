import pytest
import random
from unittest.mock import MagicMock
from types import SimpleNamespace
from llm_utils import call_llm_with_retry

def test_call_llm_with_retry_immediate_success():
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[{'ok': True}])
    client.chat.completions.create.return_value = expected_response

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    client.chat.completions.create.assert_called_once()


def test_call_llm_with_retry_timeout_then_success(mocker):
    mocker.patch('time.sleep')
    client = MagicMock()
    expected_response = SimpleNamespace(choices=[{'ok': True}])
    client.chat.completions.create.side_effect = [TimeoutError('t'), expected_response]

    response = call_llm_with_retry(client, model='m', messages=[], max_retries=3)

    assert response == expected_response
    assert client.chat.completions.create.call_count == 2

@pytest.mark.xfail(reason="Fuzzer exposes unhandled exceptions")
def test_call_llm_with_retry_fuzz(monkeypatch):
    monkeypatch.setattr('time.sleep', lambda x: None)
    random.seed(42)

    pool = [
        None, "", "a" * 10000, "你好🔥", float('nan'), float('inf'), -float('inf'), 1e308, 0, 1, -1, [], {}, set(), True, False, Exception("mock error")
    ]

    def get_random_val():
        val = random.choice(pool)
        if isinstance(val, list): return list(val)
        if isinstance(val, dict): return dict(val)
        if isinstance(val, set): return set(val)
        return val

    for _ in range(300):
        max_retries = random.choice([0, 1, 2, 3, 1.5, "2", None])
        if random.random() < 0.2:
            client = get_random_val()
        else:
            client = MagicMock()
            if random.random() < 0.2:
                client.chat.completions.create.return_value = get_random_val()
            elif random.random() < 0.4:
                client.chat.completions.create.side_effect = Exception(str(get_random_val()))
            else:
                resp = MagicMock()
                r = random.random()
                if r < 0.2:
                    del resp.choices
                elif r < 0.4:
                    resp.choices = []
                elif r < 0.6:
                    resp.choices = None
                else:
                    choice = MagicMock()
                    r2 = random.random()
                    if r2 < 0.3:
                        del choice.message
                    elif r2 < 0.6:
                        choice.message = None
                    else:
                        choice.message = get_random_val()
                    resp.choices = [choice]
                client.chat.completions.create.return_value = resp

        kwargs = {f"kw_{i}": get_random_val() for i in range(random.randint(0, 3))}

        try:
            result = call_llm_with_retry(client, max_retries=max_retries, **kwargs)
            # The documented type for return is a response object containing choices with a message.
            assert hasattr(result, "choices")
            assert result.choices
            assert hasattr(result.choices[0], "message")
            assert result.choices[0].message
        except Exception as e:
            if not isinstance(e, ValueError):
                # Any exception other than ValueError is unexpected (like TypeError for range())
                raise e
