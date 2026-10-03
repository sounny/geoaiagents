from geoai_cli import SYSTEM_PROMPT

def test_system_prompt_content():
    """
    Verify that SYSTEM_PROMPT is a non-empty string and contains the required
    substrings: 'Humboldt', 'geocode_locations', and ('GeoAI' or 'Geospatial').
    """
    # Verify it is a non-empty string
    assert isinstance(SYSTEM_PROMPT, str)
    assert len(SYSTEM_PROMPT) > 0

    # Verify required substrings
    assert "Humboldt" in SYSTEM_PROMPT
    assert "geocode_locations" in SYSTEM_PROMPT
    assert "GeoAI" in SYSTEM_PROMPT or "Geospatial" in SYSTEM_PROMPT
