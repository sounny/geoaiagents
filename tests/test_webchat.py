from webchat import parse_table_coordinates

def test_parse_table_coordinates_too_few_cells_skip():
    table = '| Latitude | Longitude | Extra |\n|---|---|---|\n| 48.8 |\n| 48.85 | 2.35 | x |'
    assert parse_table_coordinates(table, 0, 1) == [(48.85, 2.35)]
