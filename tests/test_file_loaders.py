from file_loaders import _table

def test_table_empty_list():
    result = _table([])
    lines = result.split("\n")
    assert len(lines) == 2
    assert lines[0] == '| Latitude | Longitude |'
    assert lines[1] == '|---------:|----------:|'

def test_table_single_coordinate():
    result = _table([(48.8566, 2.3522)])
    lines = result.split("\n")
    assert len(lines) == 3
    assert lines[0] == '| Latitude | Longitude |'
    assert lines[1] == '|---------:|----------:|'
    assert '48.8566' in result
    assert '2.3522' in result
