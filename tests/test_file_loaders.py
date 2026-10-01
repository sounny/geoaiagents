import pytest
from file_loaders import load_csv

def test_load_csv_locking_blank_line_rows():
    """Distinct from missing-Latitude and y/x-alias titles by locking blank-line rows. Pure parse."""
    res = load_csv('Latitude,Longitude\n\n48.8,2.3\n\n')
    assert '48.8' in res
    assert '2.3' in res

    empty_res = load_csv('')
    assert empty_res.startswith('| Latitude | Longitude |')
    assert len(empty_res.strip().split('\n')) == 2
