import pytest

pytest.skip("skip if none take strings", allow_module_level=True)

@pytest.mark.skip(reason="skip if none take strings")
def test_dummy_skip(mocker):
    pass
