from webchat import parse_distance_table

def test_parse_distance_table_malformed():
    malformed_str = "This is\nnot\na\ntable"
    result = parse_distance_table(malformed_str)
    assert result == []
