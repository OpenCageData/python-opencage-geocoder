# encoding: utf-8
from datetime import datetime
from pathlib import Path
import os
import httpretty
from httpretty import httprettified
from opencage.geocoder import OpenCageGeocode

# reduce maximum backoff retry time from 120s to 1s
os.environ['BACKOFF_MAX_TIME'] = '1'

geocoder = OpenCageGeocode('abcde')


@httprettified
def test_rate_limit_properties_no_headers():
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body=Path('test/fixtures/uk_postcode.json').read_text(encoding="utf-8")
    )
    _ = geocoder.geocode("EC1M 5RF")

    assert geocoder.ratelimit_limit is None
    assert geocoder.ratelimit_remaining is None
    assert geocoder.ratelimit_reset is None


@httprettified
def test_rate_limit_properties():
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body=Path('test/fixtures/uk_postcode.json').read_text(encoding="utf-8"),
        adding_headers={
            'X-RateLimit-Limit': '2500',
            'X-RateLimit-Remaining': '2487',
            'X-RateLimit-Reset': '1402185600'
        }
    )
    _ = geocoder.geocode("EC1M 5RF")

    assert geocoder.ratelimit_limit == 2500
    assert geocoder.ratelimit_remaining == 2487
    assert geocoder.ratelimit_reset == datetime.fromtimestamp(1402185600)
