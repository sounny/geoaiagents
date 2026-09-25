import pytest
import yaml

def test_ci_workflow_orchestration():
    with open('.github/workflows/ci.yml', 'r') as f:
        ci = yaml.safe_load(f)
    concurrency = ci.get('concurrency', {})
    assert concurrency.get('cancel-in-progress') is True, "cancel-in-progress must be true to handle stale work"

def test_geocode_shared_ratelimiter():
    import geocode
    assert hasattr(geocode, '_SHARED_GEOCODE')
    assert hasattr(geocode, '_SHARED_REVERSE')
    assert geocode._SHARED_GEOCODE.max_retries == 2
    assert geocode._SHARED_REVERSE.max_retries == 2
