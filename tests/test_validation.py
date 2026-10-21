import pytest
from validation import is_valid_lat_lon, parse_coordinate_pairs, format_invalid_notes

def test_is_valid_lat_lon():
    assert is_valid_lat_lon(0, 0) is True
    assert is_valid_lat_lon(90, 180) is True
    assert is_valid_lat_lon(-90, -180) is True
    assert is_valid_lat_lon(91, 0) is False
    assert is_valid_lat_lon(0, 181) is False
    assert is_valid_lat_lon(-91, 0) is False
    assert is_valid_lat_lon(0, -181) is False
    assert is_valid_lat_lon(90, 0) is True
    assert is_valid_lat_lon(-90, 0) is True

def test_is_valid_lat_lon_locked_boundaries():
    assert is_valid_lat_lon(90.0, 0.0) is True
    assert is_valid_lat_lon(-90.0, 180.0) is True
    assert is_valid_lat_lon(0.0, -180.0) is True
    assert is_valid_lat_lon(90.001, 0.0) is False
    assert is_valid_lat_lon(0.0, -180.0001) is False
    assert is_valid_lat_lon(12.5, -180.0001) is False

def test_is_valid_lat_lon_nan_inf():
    assert is_valid_lat_lon(float("nan"), 0) is False
    assert is_valid_lat_lon(0, float("nan")) is False
    assert is_valid_lat_lon(float("inf"), 0) is False
    assert is_valid_lat_lon(0, float("inf")) is False
    assert is_valid_lat_lon(float("-inf"), 0) is False
    assert is_valid_lat_lon(0, float("-inf")) is False

def test_parse_coordinate_pairs():
    text = "0,0\n91,0\nabc,123\n10, 20"
    pairs, invalid = parse_coordinate_pairs(text)
    assert pairs == [(0, 0), (10, 20)]
    assert len(invalid) == 2
    assert invalid[0][0] == "91,0"
    assert invalid[1][0] == "abc,123"

def test_parse_coordinate_pairs_malformed():
    pairs, invalid = parse_coordinate_pairs("10,20\ninvalid\n30,200\n40\n120, 45")

    assert pairs == [(10.0, 20.0)]
    assert len(invalid) == 4
    assert invalid[0] == ("invalid", "Missing latitude/longitude pair")
    assert invalid[1] == ("30,200", "Out of range (-90 <= lat <= 90, -180 <= lon <= 180)")
    assert invalid[2] == ("40", "Missing latitude/longitude pair")
    assert invalid[3] == ("120, 45", "Out of range (-90 <= lat <= 90, -180 <= lon <= 180)")

def test_parse_coordinate_pairs_not_a_number():
    pairs, invalid = parse_coordinate_pairs("10,foo")
    assert not pairs
    assert len(invalid) == 1
    assert invalid[0] == ("10,foo", "Not a number")

def test_format_invalid_notes():
    invalid = [("91,0", "Out of range"), ("abc,123", "Not a number")]
    result = format_invalid_notes(invalid)
    assert "Skipped invalid inputs" in result
    assert "`91,0`" in result
    assert "`abc,123`" in result

    formatted = format_invalid_notes([("invalid", "Missing latitude/longitude pair")])
    assert "_Skipped invalid inputs:_" in formatted
    assert "- `invalid` (Missing latitude/longitude pair)" in formatted

def test_parse_coordinate_pairs_space_separated_locked():
    # Test valid space-separated and semicolon-delimited coordinates
    valid_text = "35.6762 139.6503; 34.6937 135.5023"
    pairs, invalid = parse_coordinate_pairs(valid_text)
    assert pairs == [(35.6762, 139.6503), (34.6937, 135.5023)]
    assert not invalid

    # Test invalid coordinates (out of range lat)
    pairs1, invalid1 = parse_coordinate_pairs("91 0")
    assert not pairs1
    assert len(invalid1) == 1
    assert "Out of range" in invalid1[0][1]

    # Test invalid coordinates (out of range lon)
    pairs2, invalid2 = parse_coordinate_pairs("0 181")
    assert not pairs2
    assert len(invalid2) == 1
    assert "Out of range" in invalid2[0][1]

def test_swap_axis_order():
    try:
        from validation import swap_axis_order
    except ImportError:
        pytest.xfail("swap_axis_order helper is missing")

    # Assert (lat, lon) to (lon, lat) swaps coordinates
    assert swap_axis_order((10.0, 20.0)) == (20.0, 10.0)

    # Assert extra dimensions are preserved
    assert swap_axis_order((10.0, 20.0, 30.0)) == (20.0, 10.0, 30.0)
    assert swap_axis_order((10.0, 20.0, 30.0, 40.0)) == (20.0, 10.0, 30.0, 40.0)

import random
import string

def test_validation_fuzz():
    random.seed(42)

    def rand_input():
        # Choices covering wrong types, strings, numbers, NaN, None, etc.
        choices = [
            random.uniform(-1000, 1000),
            random.uniform(-180, 180),
            random.uniform(-90, 90),
            0.0,
            float('inf'),
            float('-inf'),
            float('nan'),
            None,
            [],
            {},
            True,
            False,
        ]

        # Add random strings
        length = random.choice([0, 10, 100, 1000])
        chars = string.ascii_letters + string.digits + string.punctuation + ' \\n\\t\\r;' + 'ñçéœ∑œ®†¥¨ˆøπ'
        random_str = ''.join(random.choice(chars) for _ in range(length))
        choices.append(random_str)

        return random.choice(choices)

    # Allowed exception types the module uses or python uses for wrong types implicitly
    allowed_exceptions = (ValueError, TypeError, AttributeError)

    for _ in range(500):
        lat = rand_input()
        lon = rand_input()
        try:
            res = is_valid_lat_lon(lat, lon)
            assert isinstance(res, bool)
        except allowed_exceptions:
            pass
        except AssertionError:
            raise
        except Exception as e:
            pytest.fail(f"Unexpected exception for is_valid_lat_lon({repr(lat)}, {repr(lon)}): {e}")

    for _ in range(500):
        text = rand_input()
        try:
            res = parse_coordinate_pairs(text)
            assert isinstance(res, tuple) and len(res) == 2
            assert isinstance(res[0], list) and isinstance(res[1], list)
        except allowed_exceptions:
            pass
        except AssertionError:
            raise
        except Exception as e:
            pytest.fail(f"Unexpected exception for parse_coordinate_pairs({repr(text)}): {type(e)} {e}")

    for _ in range(500):
        # Generate some valid lists of tuples, and some completely wrong inputs
        if random.random() < 0.5:
            invalid_entries = rand_input()
        else:
            invalid_entries = []
            for _ in range(random.randint(0, 10)):
                invalid_entries.append((rand_input(), rand_input()))

        try:
            res = format_invalid_notes(invalid_entries)
            assert isinstance(res, str)
        except allowed_exceptions:
            pass
        except AssertionError:
            raise
        except Exception as e:
            pytest.fail(f"Unexpected exception for format_invalid_notes(): {type(e)} {e}")

    try:
        from validation import swap_axis_order
    except ImportError:
        pass

    if 'swap_axis_order' in locals():
        for _ in range(500):
            if random.random() < 0.5:
                axis_input = rand_input()
            else:
                axis_input = (rand_input(), rand_input())
                if random.random() < 0.5:
                    axis_input += (rand_input(),)
            try:
                res = swap_axis_order(axis_input)
                assert isinstance(res, tuple) or isinstance(res, list)
            except allowed_exceptions:
                pass
            except AssertionError:
                raise
            except Exception as e:
                pytest.fail(f"Unexpected exception for swap_axis_order(): {type(e)} {e}")
