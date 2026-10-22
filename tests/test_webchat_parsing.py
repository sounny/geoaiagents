import pytest
from webchat import parse_table_coordinates

def test_parse_table_coordinates_valid():
    table = """| Location | Latitude | Longitude |
|---|---|---|
| Point A | 34.0522 | -118.2437 |
| Point B | 40.7128 | -74.0060 |"""
    coords = parse_table_coordinates(table, 1, 2)
    assert coords == [(34.0522, -118.2437), (40.7128, -74.0060)]

def test_parse_table_coordinates_invalid_float():
    table = """| Location | Latitude | Longitude |
|---|---|---|
| Point A | 34.0522 | -118.2437 |
| Point B | Invalid | -74.0060 |
| Point C | 51.5074 | 0.1278 |"""
    coords = parse_table_coordinates(table, 1, 2)
    assert coords == [(34.0522, -118.2437), (51.5074, 0.1278)]

def test_parse_table_coordinates_insufficient_columns():
    table = """| Location | Latitude |
|---|---|
| Point A | 34.0522 |
| Point B | 40.7128 |"""
    # Asking for index 2, which doesn't exist
    coords = parse_table_coordinates(table, 1, 2)
    assert coords == []

def test_parse_table_coordinates_different_indices():
    table = """| Latitude | Location | Longitude |
|---|---|---|
| 34.0522 | Point A | -118.2437 |
| 40.7128 | Point B | -74.0060 |"""
    coords = parse_table_coordinates(table, 0, 2)
    assert coords == [(34.0522, -118.2437), (40.7128, -74.0060)]

def test_parse_table_coordinates_empty_or_headers_only():
    table = """| Location | Latitude | Longitude |
|---|---|---|"""
    coords = parse_table_coordinates(table, 1, 2)
    assert coords == []

    empty_table = ""
    coords = parse_table_coordinates(empty_table, 1, 2)
    assert coords == []

def test_parse_table_coordinates_no_pipes():
    # What happens if a line has no pipes?
    # .split("|") gives 1 element.
    # if len(cells) <= max(lat_index, lon_index) handles this.
    table = """| Location | Latitude | Longitude |
|---|---|---|
Just a string without pipes
| Point A | 34.0522 | -118.2437 |"""
    coords = parse_table_coordinates(table, 1, 2)
    assert coords == [(34.0522, -118.2437)]

def test_parse_table_coordinates_none_raises_attributeerror():
    with pytest.raises(AttributeError):
        parse_table_coordinates(None, 1, 2)

def test_parse_table_coordinates_int_raises_attributeerror():
    with pytest.raises(AttributeError):
        parse_table_coordinates(123, 1, 2)

def test_parse_table_coordinates_string_index_raises_typeerror():
    table = "| Location | Latitude | Longitude |\n|---|---|---|\n| Point A | 34.0522 | -118.2437 |"
    with pytest.raises(TypeError):
        parse_table_coordinates(table, "a", 2)
    with pytest.raises(TypeError):
        parse_table_coordinates(table, 1, "b")
