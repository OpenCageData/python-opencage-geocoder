from pathlib import Path

import httpretty
import pytest

from httpretty import httprettified
from opencage.geocoder import OpenCageGeocode
from opencage.geocoder import NotAuthorizedError

geocoder = OpenCageGeocode('unauthorized-key')

@httprettified
def test_api_key_not_authorized():
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body=Path('test/fixtures/401_not_authorized.json').read_text(encoding="utf-8"),
        status=401,
    )

    with pytest.raises(NotAuthorizedError) as excinfo:
        geocoder.geocode("whatever")
    assert str(excinfo.value) == 'Your API key is not authorized. You may have entered it incorrectly.'
