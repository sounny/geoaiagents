from webchat import extract_map_coords

def test_extract_map_coords_calculate_distance():
    table = "| a | b | c | d | e |\n|---|---|---|---|---|\n| 1.0 | 2.0 | 3.0 | 4.0 | 0 |"
    assert extract_map_coords('calculate_distance', table) == [(1.0, 2.0), (3.0, 4.0)]

def test_extract_map_coords_unknown_tool():
    assert extract_map_coords('unknown_tool', 'x') == []
