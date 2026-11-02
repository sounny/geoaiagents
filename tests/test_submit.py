import pytest

pytest.skip("submit.py contains no public functions", allow_module_level=True)

@pytest.mark.skip(reason="no functions take file paths")
def test_dummy(tmp_path, mocker):
    pass
