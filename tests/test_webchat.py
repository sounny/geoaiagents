import pytest
from webchat import parse_distance_table

def test_parse_distance_table_locking_header_only_empty():
    assert parse_distance_table('| A | B | C | D |\n|---|---|---|---|') == []

    table = '| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 48.8 | 2.3 | 51.5 | -0.1 |'
    assert parse_distance_table(table) == [(48.8, 2.3), (51.5, -0.1)]

from webchat import parse_table_coordinates, create_map_html
import re

def test_create_map_html_markers_and_skips_invalid_locking_markers():
    table = """| Location | Latitude | Longitude |
|---|---|---|
| Valid 1 | 51.5074 | -0.1278 |
| Invalid 1 | ABC | DEF |
| Valid 2 | 48.8566 | 2.3522 |
| Invalid 2 | 10.0 |"""
    points = parse_table_coordinates(table, 1, 2)
    assert len(points) == 2
    html = create_map_html(points)
    assert len(re.findall(r"L\.marker", html)) == 2

def test_parse_table_coordinates_with_fences():
    table_with_nested = """```markdown
Some text
```json
{ "foo": "bar" }
```
| Lat1 | Lon1 |
|---|---|
| 48.8 | 2.3 |
```"""
    assert parse_table_coordinates(table_with_nested, 0, 1) == [(48.8, 2.3)]

    table_with_unclosed = """```markdown
| Lat1 | Lon1 |
|---|---|
| 48.8 | 2.3 |"""
    assert parse_table_coordinates(table_with_unclosed, 0, 1) == [(48.8, 2.3)]

def test_parse_distance_table_with_fences():
    table_with_nested = """```markdown
Some text
```json
{ "foo": "bar" }
```
| Lat1 | Lon1 | Lat2 | Lon2 |
|---|---|---|---|
| 48.8 | 2.3 | 51.5 | -0.1 |
```"""
    assert parse_distance_table(table_with_nested) == [(48.8, 2.3), (51.5, -0.1)]

    table_with_unclosed = """```markdown
| Lat1 | Lon1 | Lat2 | Lon2 |
|---|---|---|---|
| 48.8 | 2.3 | 51.5 | -0.1 |"""
    assert parse_distance_table(table_with_unclosed) == [(48.8, 2.3), (51.5, -0.1)]
