import pytest

pytest.skip("submit.py contains no defined public functions", allow_module_level=True)

@pytest.mark.skip(reason="skip if none take file paths")
def test_dummy(tmp_path, mocker, monkeypatch):
    pass
