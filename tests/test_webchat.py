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

def test_webchat_public_names_locking(mocker):
    import inspect
    import webchat

    # Mock external network/model calls if necessary
    # In this test we just inspect definitions. Since `webchat` initializes OpenAI client globally
    # in module scope and we're just checking what is exported/defined, we don't necessarily need
    # to mock network/model calls *unless* reloading the module occurs. We will patch them if needed
    # for safety so that other tests wouldn't make network calls, but actually webchat handles instantiation safely.

    public_names = [name for name in dir(webchat) if not name.startswith('_')]
    results = {}

    for name in public_names:
        obj = getattr(webchat, name)
        if inspect.ismodule(obj):
            continue

        if inspect.isclass(obj):
            results[name] = 'class'
        elif inspect.isfunction(obj):
            results[name] = 'function'
        else:
            results[name] = 'constant'

    expected = {
        'API_KEY': 'constant',
        'BASE_URL': 'constant',
        'DEBUG': 'constant',
        'DEFAULT_TOOL_COORD_PARSERS': 'constant',
        'GradioLogHandler': 'class',
        'LAST_MAP_HTML': 'constant',
        'MODEL_NAME': 'constant',
        'OpenAI': 'class',
        'build_ui': 'function',
        'call_llm_with_retry': 'function',
        'chat': 'function',
        'client': 'constant',
        'create_map_html': 'function',
        'create_registry': 'function',
        'extract_map_coords': 'function',
        'functions': 'constant',
        'infer_location': 'function',
        'log_history': 'constant',
        'main': 'function',
        'messages': 'constant',
        'parse_distance_table': 'function',
        'parse_table_coordinates': 'function',
        'parse_tool_args': 'function',
        'registry': 'constant',
        'respond': 'function',
        'run_tool': 'function',
        'system_prompt': 'constant'
    }

    assert results == expected
