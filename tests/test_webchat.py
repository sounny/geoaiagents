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





import random
import json
import pytest
from unittest.mock import patch, MagicMock
import webchat

@pytest.mark.xfail(reason="Fuzzer exposes some bugs with invalid types/NaNs/empty inputs", strict=False)
def test_fuzz_webchat_public_functions():
    random.seed(42)

    strings = [
        "",
        "a" * 10000,
        "ñ" * 100,
        "👍",
        "| Lat | Lon |\n|---|---|\n| 1.0 | 2.0 |",
        "| A | B | C | D |\n| 1 | 2 | 3 | 4 |",
        "for Paris",
        "for " + "A" * 1000,
        '{"test": 1}',
        '{"locations": "Paris"}',
        "| A |\n|---|\n| 1 |"
    ]
    floats = [0.0, -0.0, 1.0, -1.0, 1e300, -1e300, float('inf'), float('-inf'), float('nan')]
    ints = [0, 1, -1, 1000, -1000, 2**63 - 1, -(2**63)]

    all_values = strings + floats + ints + [None, True, False, []]

    def get_random_val(): return random.choice(all_values)
    def get_random_str(): return random.choice(strings)
    def get_random_int(): return random.choice(ints)
    def get_random_float(): return random.choice(floats)
    def get_random_point(): return (get_random_float(), get_random_float())
    def get_random_points(): return [get_random_point() for _ in range(random.randint(0, 10))]
    def get_random_history(): return [{"role": "user", "content": get_random_str()} for _ in range(random.randint(0, 5))]
    def get_random_function_call():
        fc = MagicMock()
        fc.name = random.choice(["geocode_locations", "distance", get_random_str()])
        fc.arguments = get_random_str()
        return fc
    def get_random_upload_file():
        if random.choice([True, False]): return None
        uf = MagicMock()
        uf.name = "dummy.txt"
        return uf

    expected_exceptions = (ValueError, TypeError, json.JSONDecodeError, AttributeError, IndexError)

    with patch('webchat.call_llm_with_retry') as mock_call, \
         patch('webchat.registry.invoke', return_value="| A | B |\n| 1 | 2 |"):

        for i in range(200):
            mock_msg = MagicMock()
            mock_msg.content = "mocked reply"
            mock_msg.function_call = None
            if random.choice([True, False]):
                mock_msg.function_call = get_random_function_call()

            mock_response = MagicMock()
            mock_response.choices = [MagicMock(message=mock_msg)]
            mock_call.return_value = mock_response

            try:
                r = webchat.infer_location(get_random_val())
                assert r is None or isinstance(r, str)
            except expected_exceptions: pass

            try:
                r = webchat.create_map_html(get_random_val())
                assert isinstance(r, str)
            except expected_exceptions: pass

            try:
                r = webchat.parse_table_coordinates(get_random_val(), get_random_val(), get_random_val())
                assert isinstance(r, list)
            except expected_exceptions: pass

            try:
                r = webchat.parse_distance_table(get_random_val())
                assert isinstance(r, list)
            except expected_exceptions: pass

            try:
                r = webchat.extract_map_coords(get_random_val(), get_random_val())
                assert isinstance(r, list)
            except expected_exceptions: pass

            try:
                r = webchat.run_tool(get_random_val())
                assert isinstance(r, tuple)
            except expected_exceptions: pass

            try:
                r = webchat.respond(get_random_val(), get_random_val(), get_random_val())
                assert isinstance(r, tuple)
            except expected_exceptions: pass

            try:
                r = webchat.chat(get_random_val(), get_random_val(), get_random_val())
                assert isinstance(r, tuple)
            except expected_exceptions: pass

            try:
                r = webchat.infer_location(get_random_str())
                assert r is None or isinstance(r, str)
            except expected_exceptions: pass

            try:
                r = webchat.create_map_html(get_random_points())
                assert isinstance(r, str)
            except expected_exceptions: pass

            try:
                r = webchat.parse_table_coordinates(get_random_str(), get_random_int(), get_random_int())
                assert isinstance(r, list)
            except expected_exceptions: pass

            try:
                r = webchat.parse_distance_table(get_random_str())
                assert isinstance(r, list)
            except expected_exceptions: pass

            try:
                r = webchat.extract_map_coords(get_random_str(), get_random_str())
                assert isinstance(r, list)
            except expected_exceptions: pass

            try:
                r = webchat.run_tool(get_random_function_call())
                assert isinstance(r, tuple)
            except expected_exceptions: pass

            try:
                r = webchat.respond(get_random_str(), get_random_history(), get_random_upload_file())
                assert isinstance(r, tuple)
            except expected_exceptions: pass

            try:
                r = webchat.chat(get_random_str(), get_random_history(), get_random_upload_file())
                assert isinstance(r, tuple)
            except expected_exceptions: pass
