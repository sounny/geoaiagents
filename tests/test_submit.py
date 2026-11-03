import pytest
from unittest.mock import patch

@pytest.mark.skip(reason="submit.py has no public functions that take paths")
def test_submit_paths(tmp_path, monkeypatch):
    pass
