import pytest
from unittest.mock import MagicMock
from llm_utils import call_llm_with_retry

def test_original_exception_preserved():
    client = MagicMock()
    class CustomAPIError(Exception):
        pass

    client.chat.completions.create.side_effect = CustomAPIError("Rate limit exceeded")

    with pytest.raises(CustomAPIError, match="Rate limit exceeded"):
        call_llm_with_retry(client, max_retries=1)
