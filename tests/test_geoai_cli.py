import pytest
from geoai_cli import _tool_args_for, TEXT_FIELD_BY_TOOL

def test_text_field_by_tool_membership():
    assert TEXT_FIELD_BY_TOOL == {
        "load_geojson": "geojson",
        "load_kml": "kml",
        "load_csv": "csv",
    }

def test_tool_args_for_text_fields():
    assert _tool_args_for('load_geojson', '{ }') == {'geojson': '{ }'}
    assert _tool_args_for('load_kml', '<k/>') == {'kml': '<k/>'}
    assert _tool_args_for('load_csv', 'lat,lon') == {'csv': 'lat,lon'}
    assert _tool_args_for('not_a_builtin_tool', 'x') == {'input': 'x'}

def test_tool_args_for_geocode_locations():
    assert _tool_args_for('geocode_locations', 'Paris\nLondon') == {'locations': 'Paris\nLondon'}

def test_tool_args_for_fetch_geo_boundaries_adm0():
    assert _tool_args_for('fetch_geo_boundaries', 'USA', adm='ADM0') == {'iso': 'USA', 'adm': 'ADM0'}
    assert _tool_args_for('fetch_geo_boundaries', 'usa', adm='ADM0') == {'iso': 'usa', 'adm': 'ADM0'}
    assert _tool_args_for('fetch_geo_boundaries', 'USA') == {'iso': 'USA', 'adm': 'ADM0'}

def test_tool_args_for_fetch_geo_boundaries_adm2():
    assert _tool_args_for('fetch_geo_boundaries', 'FRA', adm='ADM2') == {'iso': 'FRA', 'adm': 'ADM2'}

def test_tool_args_for_coordinates_tools():
    assert _tool_args_for('calculate_distance', '48.8,2.3,51.5,-0.1') == {'coordinates': '48.8,2.3,51.5,-0.1'}
    assert _tool_args_for('reverse_geocode_coordinates', '48.8,2.3,51.5,-0.1') == {'coordinates': '48.8,2.3,51.5,-0.1'}
    assert _tool_args_for('convert_dd_to_dms', '48.8,2.3,51.5,-0.1') == {'coordinates': '48.8,2.3,51.5,-0.1'}
