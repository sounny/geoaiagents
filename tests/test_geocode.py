from geocode import _SHARED_GEOCODE, _SHARED_REVERSE

def test_shared_rate_limiter_config():
    """Verify that the rate limiter is global and has max_retries=2."""
    assert _SHARED_GEOCODE.max_retries == 2
    assert _SHARED_REVERSE.max_retries == 2
    assert _SHARED_GEOCODE.min_delay_seconds == 1
    assert _SHARED_REVERSE.min_delay_seconds == 1
