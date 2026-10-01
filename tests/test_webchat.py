from webchat import infer_location

def test_infer_location_tokyo_paris_positive_path():
    assert infer_location('Show a map for Paris France') == 'Paris France'

def test_infer_location_greeting_negative_plus_berlin_scenario():
    assert infer_location('hello how are you?') is None
    assert infer_location('hello there') is None
    assert infer_location('') is None
    result = infer_location('show map FOR Berlin Germany')
    assert result is not None
    assert 'Berlin' in result
