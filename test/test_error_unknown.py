import pytest

import responses

from opencage.geocoder import OpenCageGeocode
from opencage.geocoder import UnknownError

geocoder = OpenCageGeocode('abcde')


@responses.activate
def test_http_500_status():
    responses.add(
        responses.GET,
        geocoder.url,
        body='{}',
        status=500,
    )

    with pytest.raises(UnknownError) as excinfo:
        geocoder.geocode('whatever')

    assert str(excinfo.value) == '500 status code from API'


@responses.activate
def test_non_json():
    "These kinds of errors come from webserver and may not be JSON"
    responses.add(
        responses.GET,
        geocoder.url,
        body='<html><body><h1>503 Service Unavailable</h1></body></html>',
        headers={
            'Content-Type': 'text/html',
        },
        status=503
    )

    with pytest.raises(UnknownError) as excinfo:
        geocoder.geocode('whatever')

    assert str(excinfo.value) == 'Non-JSON result from server'


@responses.activate
def test_no_results_key():
    responses.add(
        responses.GET,
        geocoder.url,
        body='{"spam": "eggs"}',
        status=200,  # Need to specify status code with responses
    )

    with pytest.raises(UnknownError) as excinfo:
        geocoder.geocode('whatever')

    assert str(excinfo.value) == "JSON from API doesn't have a 'results' key"
