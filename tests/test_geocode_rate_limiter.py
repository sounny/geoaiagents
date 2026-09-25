import pytest
from geocode import _geocode_rate_limited, _reverse_rate_limited
from geopy.extra.rate_limiter import RateLimiter

def test_rate_limiter_global():
    # Verify that RateLimiters have max_retries set to 2 and min_delay_seconds to 1
    assert isinstance(_geocode_rate_limited, RateLimiter)
    assert getattr(_geocode_rate_limited, "min_delay_seconds", None) == 1
    assert getattr(_geocode_rate_limited, "max_retries", None) == 2

    assert isinstance(_reverse_rate_limited, RateLimiter)
    assert getattr(_reverse_rate_limited, "min_delay_seconds", None) == 1
    assert getattr(_reverse_rate_limited, "max_retries", None) == 2
