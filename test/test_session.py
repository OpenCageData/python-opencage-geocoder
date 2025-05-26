# encoding: utf-8

from pathlib import Path

import pytest
import responses

from opencage.geocoder import OpenCageGeocode
from opencage.geocoder import NotAuthorizedError


def _any_result_around(results, lat=None, lon=None):
    for result in results:
        if (abs(result['geometry']['lat'] - lat) < 0.05
                and abs(result['geometry']['lng'] - lon) < 0.05):
            return True
    return False


@responses.activate
def test_success():
    with OpenCageGeocode('abcde') as geocoder:
        responses.add(
            responses.GET,
            geocoder.url,
            body=Path('test/fixtures/uk_postcode.json').read_text(encoding="utf-8"),
            status=200
        )

        results = geocoder.geocode("EC1M 5RF")
        assert _any_result_around(results, lat=51.5201666, lon=-0.0985142)


@responses.activate
def test_failure():
    with OpenCageGeocode('unauthorized-key') as geocoder:
        responses.add(
            responses.GET,
            geocoder.url,
            body=Path('test/fixtures/401_not_authorized.json').read_text(encoding="utf-8"),
            status=401,
        )

        with pytest.raises(NotAuthorizedError) as excinfo:
            geocoder.geocode("whatever")
        assert str(excinfo.value) == 'Your API key is not authorized. You may have entered it incorrectly.'
