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
        status=500,
    )

    with pytest.raises(UnknownError) as excinfo:
        geocoder.geocode('whatever')

    assert str(excinfo.value) == '500 status code from API'

@httprettified
def test_non_json():
    "These kinds of errors come from webserver and may not be JSON"
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body='<html><body><h1>503 Service Unavailable</h1></body></html>',
        forcing_headers={
            'Content-Type': 'text/html',
        },
        status=503
    )

    with pytest.raises(UnknownError) as excinfo:
        geocoder.geocode('whatever')

    assert str(excinfo.value) == 'Non-JSON result from server'

@httprettified
def test_no_results_key():
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body='{"spam": "eggs"}',
    )

    with pytest.raises(UnknownError) as excinfo:
        geocoder.geocode('whatever')

    assert str(excinfo.value) == "JSON from API doesn't have a 'results' key"
