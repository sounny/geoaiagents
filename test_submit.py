import pytest

pytest.skip("no public functions write files", allow_module_level=True)

def test_dummy(tmp_path, mocker):
    pass
