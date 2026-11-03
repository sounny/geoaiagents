import pytest
from llm_utils import call_llm_with_retry

@pytest.mark.skip(reason="No public functions take paths")
def test_path_traversal(tmp_path, mocker):
    pass
