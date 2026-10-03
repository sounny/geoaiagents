from webchat import parse_distance_table

def test_parse_distance_table_valid_input():
    table = "| Lat1 | Lon1 | Lat2 | Lon2 | Dist |\n|---|---|---|---|---|\n| 48.8566 | 2.3522 | 51.5074 | -0.1278 | 343 |"
    result = parse_distance_table(table)
    assert result == [(48.8566, 2.3522), (51.5074, -0.1278)]
