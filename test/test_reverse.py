from opencage.geocoder import _query_for_reverse_geocoding

def _expected_output(input_latlng, expected_output): # pylint: disable=no-self-argument
    def test():
        lat, lng = input_latlng
        assert _query_for_reverse_geocoding(lat, lng) == expected_output
    return test

def test_reverse():
    _expected_output((10, 10), "10,10")
    _expected_output((10.0, 10.0), "10.0,10.0")
    _expected_output((0.000002, -120), "0.000002,-120")
    _expected_output((2.000002, -120), "2.000002,-120")
    _expected_output((2.000002, -120.000002), "2.000002,-120.000002")
    _expected_output((2.000002, -1.0000002), "2.000002,-1.0000002")
    _expected_output((2.000002, 0.0000001), "2.000002,0.0000001")

    _expected_output(("2.000002", "-120"), "2.000002,-120")
