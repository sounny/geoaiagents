import pytest

def test_skip():
    pass

pytest.skip('no public function is numeric', allow_module_level=True)
