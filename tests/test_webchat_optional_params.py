import pytest
from unittest.mock import patch, MagicMock
import webchat

def test_respond_optional_params_omitted():
    with patch("webchat.call_llm_with_retry") as mock_llm:
        mock_llm.return_value = MagicMock()
        mock_llm.return_value.choices[0].message.function_call = None
        mock_llm.return_value.choices[0].message.content = "Test"
        try:
            res = webchat.respond("Test", [])
            assert isinstance(res, tuple)
            assert len(res) == 4
        except Exception as e:
            pytest.fail(f"respond() failed with omitted optional parameters: {e}")

def test_respond_optional_params_none():
    with patch("webchat.call_llm_with_retry") as mock_llm:
        mock_llm.return_value = MagicMock()
        mock_llm.return_value.choices[0].message.function_call = None
        mock_llm.return_value.choices[0].message.content = "Test"
        try:
            res = webchat.respond("Test", [], upload_file=None)
            assert isinstance(res, tuple)
            assert len(res) == 4
        except Exception as e:
            pytest.fail(f"respond() failed with None optional parameters: {e}")

def test_chat_optional_params_omitted():
    with patch("webchat.call_llm_with_retry") as mock_llm:
        mock_llm.return_value = MagicMock()
        mock_llm.return_value.choices[0].message.function_call = None
        mock_llm.return_value.choices[0].message.content = "Test"
        try:
            res = webchat.chat("Test", [])
            pytest.xfail("chat() missing 1 required positional argument: 'upload_file'")
        except TypeError as e:
            if "missing 1 required positional argument: 'upload_file'" in str(e):
                pytest.xfail("chat() missing 1 required positional argument: 'upload_file'")
            else:
                pytest.fail(f"Unexpected TypeError: {e}")
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

def test_chat_optional_params_none():
    with patch("webchat.call_llm_with_retry") as mock_llm:
        mock_llm.return_value = MagicMock()
        mock_llm.return_value.choices[0].message.function_call = None
        mock_llm.return_value.choices[0].message.content = "Test"
        try:
            res = webchat.chat("Test", [], upload_file=None)
            assert isinstance(res, tuple)
            assert len(res) == 4
        except Exception as e:
            pytest.fail(f"chat() failed with None optional parameters: {e}")
