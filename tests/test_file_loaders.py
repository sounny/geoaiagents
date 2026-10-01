from file_loaders import _table

def test_table_empty():
    result = _table([])
    lines = result.split('\n')
    assert len(lines) == 2
    assert lines[0] == '| Latitude | Longitude |'
    assert lines[1] == '|---------:|----------:|'

def test_table_with_data():
    result = _table([(1.0, 2.0)])
    lines = result.split('\n')
    assert len(lines) == 3
    assert lines[0] == '| Latitude | Longitude |'
    assert lines[1] == '|---------:|----------:|'
    assert '1.0' in lines[2]
    assert '2.0' in lines[2]
