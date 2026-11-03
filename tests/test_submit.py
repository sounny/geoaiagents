import pytest

@pytest.mark.skip(reason="No public functions take strings in submit.py")
def test_submit_very_long_strings(monkeypatch):
    pass
