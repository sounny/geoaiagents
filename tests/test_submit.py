import pytest

@pytest.mark.skipif(
    True,
    reason="skip if none read files: submit.py contains no public functions that read files"
)
def test_dummy(tmp_path, mocker):
    pass
