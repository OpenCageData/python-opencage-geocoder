# encoding: utf-8

from pathlib import Path

import httpretty
import pytest

from httpretty import httprettified
from opencage.geocoder import OpenCageGeocode
from opencage.geocoder import NotAuthorizedError


@httprettified
def test_success():
    with OpenCageGeocode('abcde') as geocoder:
        httpretty.register_uri(
            httpretty.GET,
            geocoder.url,
            body=Path('test/fixtures/uk_postcode.json').read_text()
        )

        results = geocoder.geocode("EC1M 5RF")
        assert any((abs(result['geometry']['lat'] - 51.5201666) < 0.05 and abs(result['geometry']['lng'] - -0.0985142) < 0.05) for result in results)

@httprettified
def test_failure():
    with OpenCageGeocode('unauthorized-key') as geocoder:
        httpretty.register_uri(
            httpretty.GET,
            geocoder.url,
            body=Path('test/fixtures/401_not_authorized.json').read_text(),
            status=401,
        )

        with pytest.raises(NotAuthorizedError) as excinfo:
            geocoder.geocode("whatever")
        assert str(excinfo.value) == 'Your API key is not authorized. You may have entered it incorrectly.'
