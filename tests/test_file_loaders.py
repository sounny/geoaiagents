from file_loaders import load_csv

def test_load_csv_lat_lon_basic():
    csv_text = "lat,lon\n48.8566,2.3522\n"
    result = load_csv(csv_text)
    expected = "| Latitude | Longitude |\n|---------:|----------:|\n| 48.8566 | 2.3522 |"
    assert result == expected
