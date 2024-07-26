from pathlib import Path

import httpretty
import pytest

from httpretty import httprettified
from opencage.geocoder import OpenCageGeocode
from opencage.geocoder import RateLimitExceededError

geocoder = OpenCageGeocode('abcde')

@httprettified
def test_no_rate_limit():
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body=Path('test/fixtures/no_ratelimit.json').read_text(encoding="utf-8")
    )
    # shouldn't raise an exception
    geocoder.geocode("whatever")


@httprettified
def test_rate_limit_exceeded():
    # 4372eff77b8343cebfc843eb4da4ddc4 will always return 402
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body=Path('test/fixtures/402_rate_limit_exceeded.json').read_text(encoding="utf-8"),
        status=402,
        adding_headers={
            'X-RateLimit-Limit': '2500',
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': '1402185600'
        }
    )

    with pytest.raises(RateLimitExceededError) as excinfo:
        geocoder.geocode("whatever")
    assert 'You have used the requests available on your plan.' in str(excinfo.value)
