import pytest
import time
import geocode

def test_shared_ratelimiter_idempotency():
    # If the rate limiter is shared, two consecutive calls should take >= 1 second
    start = time.time()
    geocode.get_coordinates("London")
    geocode.get_coordinates("Paris")
    end = time.time()
    # It might be exactly 1 second, allow some epsilon
    assert (end - start) >= 0.9, f"Elapsed time {end - start} is too short, rate limiter is not shared"

def test_max_retries_configured():
    assert geocode._shared_geocode.max_retries == 2
    assert geocode._shared_reverse.max_retries == 2
