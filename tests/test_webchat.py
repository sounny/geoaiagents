from webchat import parse_distance_table

def test_parse_distance_table_malformed():
    result = parse_distance_table("just some random text\nwith newlines\nbut no pipes")
    assert result == []
