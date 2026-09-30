from webchat import infer_location

def test_infer_location_positive():
    assert infer_location('please show a map for Tokyo') == 'Tokyo'
    assert infer_location('FOR Berlin Center') == 'Berlin Center'
