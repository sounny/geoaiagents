from webchat import infer_location

def test_infer_location_greeting_and_berlin():
    assert infer_location('hello how are you?') is None
    assert infer_location('') is None
    loc = infer_location('show map for Berlin Germany')
    assert loc is not None
    assert 'berlin' in loc.lower()
