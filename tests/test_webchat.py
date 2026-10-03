import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from webchat import parse_table_coordinates

def test_parse_table_coordinates_skips_non_numeric():
    table = '| Lat | Lon |\n| --- | --- |\n| 48.8 | 2.3 |\n| abc | def |\n| -33.9 | 151.2 |'
    result = parse_table_coordinates(table, 0, 1)
    assert result == [(48.8, 2.3), (-33.9, 151.2)]
