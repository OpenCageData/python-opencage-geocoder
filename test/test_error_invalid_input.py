import pytest

import responses

from opencage.geocoder import OpenCageGeocode
from opencage.geocoder import InvalidInputError

geocoder = OpenCageGeocode('abcde')

@responses.activate
def test_must_be_unicode_string():
    responses.add(
        responses.GET,
        geocoder.url,
        body='{"results":{}}',
        status=200
    )

    # Should not give errors
    geocoder.geocode('xxx')   # ascii convertable
    geocoder.geocode('xxá')   # unicode

    # But if it isn't a unicode string, it should give error
    utf8_string = "xxá".encode("utf-8")
    latin1_string = "xxá".encode("latin1")

    with pytest.raises(InvalidInputError) as excinfo:
        geocoder.geocode(utf8_string)
    assert str(excinfo.value) == f"Input must be a unicode string, not {utf8_string!r}"
    assert excinfo.value.bad_value == utf8_string

    with pytest.raises(InvalidInputError) as excinfo:
        geocoder.geocode(latin1_string)
    assert str(excinfo.value) == f"Input must be a unicode string, not {latin1_string!r}"
    assert excinfo.value.bad_value == latin1_string
