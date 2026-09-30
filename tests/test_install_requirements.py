import pytest
from install_requirements import read_requirements

def test_read_requirements_missing_file():
    result = read_requirements('/tmp/definitely-missing-reqs-9f3abc.txt')
    assert result == []
