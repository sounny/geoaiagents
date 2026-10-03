import pytest
from file_loaders import load_csv, _table

def test_load_csv_empty_lines():
    result = load_csv('Latitude,Longitude\n\n')
    lines = result.strip().split('\n')
    assert len(lines) == 2
    assert lines[0] == '| Latitude | Longitude |'
    assert lines[1] == '|---------:|----------:|'

def test_load_csv_empty_string():
    result = load_csv('')
    lines = result.strip().split('\n')
    assert len(lines) == 2
    assert lines[0] == '| Latitude | Longitude |'
    assert lines[1] == '|---------:|----------:|'
