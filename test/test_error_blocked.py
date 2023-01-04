from pathlib import Path

import pytest
import httpretty

from httpretty import httprettified
from opencage.geocoder import OpenCageGeocode
from opencage.geocoder import ForbiddenError


geocoder = OpenCageGeocode('2e10e5e828262eb243ec0b54681d699a') # will always return 403

@httprettified
def test_api_key_blocked():
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body=Path('test/fixtures/403_apikey_disabled.json').read_text(encoding="utf-8"),
        status=403,
    )

    with pytest.raises(ForbiddenError) as excinfo:
        geocoder.geocode("whatever")
    assert str(excinfo.value) == 'Your API key has been blocked or suspended.'
