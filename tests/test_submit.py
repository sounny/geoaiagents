import pytest

@pytest.mark.skip(reason="No public functions in submit.py take dates or times")
def test_dummy(mocker):
    pass
