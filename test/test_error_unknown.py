import pytest

import httpretty

from httpretty import httprettified
from opencage.geocoder import OpenCageGeocode
from opencage.geocoder import UnknownError

geocoder = OpenCageGeocode('abcde')

@httprettified
def test_http_500_status():
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body='',
        status=500,
    )

    with pytest.raises(UnknownError):
        geocoder.geocode('whatever')

@httprettified
def test_non_json():
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body='',
    )

    with pytest.raises(UnknownError):
        geocoder.geocode('whatever')

@httprettified
def test_no_results_key():
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body='{"spam": "eggs"}',
    )

    with pytest.raises(UnknownError):
        geocoder.geocode('whatever')
