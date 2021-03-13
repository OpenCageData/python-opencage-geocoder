# encoding: utf-8

import unittest

from pathlib import Path

import os
import sys
import httpretty

from opencage.geocoder import OpenCageGeocode
from opencage.geocoder import InvalidInputError, RateLimitExceededError, UnknownError, ForbiddenError, NotAuthorizedError
from opencage.geocoder import floatify_latlng, _query_for_reverse_geocoding

sys.path.insert(0,'.')

# reduce maximum backoff retry time from 120s to 1s
os.environ['BACKOFF_MAX_TIME'] = '1'

class OpenCageGeocodeTestCase(unittest.TestCase):
    def setUp(self):
        httpretty.enable()

        self.geocoder = OpenCageGeocode('abcde')

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    def testUKPostcode(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body=Path('test/fixtures/uk_postcode.json').read_text()
        )

        results = self.geocoder.geocode("EC1M 5RF")
        self.assertTrue(
            any((abs(result['geometry']['lat'] - 51.5201666) < 0.05 and abs(result['geometry']['lng'] - -0.0985142) < 0.05) for result in results),
            msg="Bad result"
        )

    def testAustralia(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body=Path('test/fixtures/mudgee_australia.json').read_text()
        )

        results = self.geocoder.geocode("Mudgee, Australia")
        self.assertTrue(
            any((abs(result['geometry']['lat'] - -32.5980702) < 0.05 and abs(result['geometry']['lng'] - 149.5886383) < 0.05) for result in results),
            msg="Bad result"
        )


    def testMustBeUnicodeString(self):
        # dud mock so this goes quick
        httpretty.register_uri(httpretty.GET, self.geocoder.url, body='{"results":{}}')

        # Should not give errors
        self.geocoder.geocode('xxx')    # ascii convertable
        self.geocoder.geocode('xxá')   # unicode

        # But if it isn't a unicode string, it should give error
        utf8_string = "xxá".encode("utf-8")
        latin1_string = "xxá".encode("latin1")

        self.assertRaises(InvalidInputError, self.geocoder.geocode, utf8_string)

        # check the exception
        try:
            self.geocoder.geocode(utf8_string)
        except InvalidInputError as ex:
            self.assertEqual(ex.bad_value, utf8_string)
            self.assertEqual(str(ex), "Input must be a unicode string, not {0!r}".format(utf8_string))

        self.assertRaises(InvalidInputError, self.geocoder.geocode, latin1_string)

        # check the exception
        try:
            self.geocoder.geocode(latin1_string)
        except InvalidInputError as ex:
            self.assertEqual(ex.bad_value, latin1_string)
            self.assertEqual(str(ex), "Input must be a unicode string, not {0!r}".format(latin1_string))


    def testMunster(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body=Path('test/fixtures/muenster.json').read_text()
        )

        results = self.geocoder.geocode("Münster")
        self.assertTrue(
            any((abs(result['geometry']['lat'] - 51.9625101) < 0.05 and abs(result['geometry']['lng'] - 7.6251879) < 0.05) for result in results),
            msg="Bad result"
        )

    def testDonostia(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body=Path('test/fixtures/donostia.json').read_text()

        )

        results = self.geocoder.geocode("Donostia")
        self.assertTrue(
            any((abs(result['geometry']['lat'] - 43.300836) < 0.05 and abs(result['geometry']['lng'] - -1.9809529) < 0.05) for result in results),
            msg="Bad result"
        )

        # test that the results are in unicode
        self.assertEqual(results[0]['formatted'], 'San Sebastián, Autonomous Community of the Basque Country, Spain')


class FloatifyDictTestCase(unittest.TestCase):
    def _expected_output(input_value, expected_output): # pylint: disable=no-self-argument
        def test(self):
            self.assertEqual(floatify_latlng(input_value), expected_output)
        return test

    testString = _expected_output("123", "123")
    testEmptyDict = _expected_output({}, {})
    testEmptyList = _expected_output([], [])
    testDictWithFloats = _expected_output({'geom': {'lat': 12.01, 'lng': -0.9}}, {'geom': {'lat': 12.01, 'lng': -0.9}})
    testDictWithStringifiedFloats = _expected_output({'geom': {'lat': "12.01", 'lng': "-0.9"}}, {'geom': {'lat': 12.01, 'lng': -0.9}})
    testDictWithList = _expected_output(
        {'results': [{'geom': {'lat': "12.01", 'lng': "-0.9"}}, {'geometry': {'lat': '0.1', 'lng': '10'}}]},
        {'results': [{'geom': {'lat': 12.01, 'lng': -0.9}}, {'geometry': {'lat': 0.1, 'lng': 10}}]}
    )
    testListWithThings = _expected_output([{'foo': 'bar'}], [{'foo': 'bar'}])


class RateLimitErrorTestCase(unittest.TestCase):
    def setUp(self):
        httpretty.enable()

        self.geocoder = OpenCageGeocode('abcde')

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    def testNoRateLimit(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body=Path('test/fixtures/no_ratelimit.json').read_text()
        )
        # shouldn't raise an exception
        self.geocoder.geocode("whatever")


    def testRateLimitExceeded(self):
        # 4372eff77b8343cebfc843eb4da4ddc4 will always return 402
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body=Path('test/fixtures/402_rate_limit_exceeded.json').read_text(),
            status=402,
            adding_headers={'X-RateLimit-Limit': '2500', 'X-RateLimit-Remaining': '0', 'X-RateLimit-Reset': '1402185600'},
        )

        self.assertRaises(RateLimitExceededError, self.geocoder.geocode, "whatever")

        # check the exception
        try:
            self.geocoder.geocode("whatever")
        except RateLimitExceededError as ex:
            self.assertEqual(str(ex), 'Your rate limit has expired. It will reset to 2500 on 2021-03-08T00:00:00')
            self.assertEqual(ex.reset_to, 2500)


class NotAuthorizedErrorTestCase(unittest.TestCase):
    def setUp(self):
        httpretty.enable()

        self.geocoder = OpenCageGeocode('unauthorized-key')

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    def testApiKeyForbidden(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body=Path('test/fixtures/401_not_authorized.json').read_text(),
            status=401,
        )

        self.assertRaises(NotAuthorizedError, self.geocoder.geocode, "whatever")

        # check the exception
        try:
            self.geocoder.geocode("whatever")
        except NotAuthorizedError as ex:
            self.assertEqual(str(ex), 'Your API key is not authorized. You may have entered it incorrectly.')


class ForbiddenErrorTestCase(unittest.TestCase):
    def setUp(self):
        httpretty.enable()

        self.geocoder = OpenCageGeocode('2e10e5e828262eb243ec0b54681d699a') # will always return 403

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    def testApiKeyBlocked(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body=Path('test/fixtures/403_apikey_disabled.json').read_text(),
            status=403,
        )

        self.assertRaises(ForbiddenError, self.geocoder.geocode, "whatever")

        # check the exception
        try:
            self.geocoder.geocode("whatever")
        except ForbiddenError as ex:
            self.assertEqual(str(ex), 'Your API key has been blocked or suspended.')


class ReverseGeocodingTestCase(unittest.TestCase):
    def _expected_output(input_latlng, expected_output): # pylint: disable=no-self-argument
        def test(self):
            lat, lng = input_latlng
            self.assertEqual(_query_for_reverse_geocoding(lat, lng), expected_output)
        return test

    testSimple1 = _expected_output((10, 10), "10,10")
    testSimple2 = _expected_output((10.0, 10.0), "10.0,10.0")
    testSimple3 = _expected_output((0.000002, -120), "0.000002,-120")
    testSimple4 = _expected_output((2.000002, -120), "2.000002,-120")
    testSimple5 = _expected_output((2.000002, -120.000002), "2.000002,-120.000002")
    testSimple6 = _expected_output((2.000002, -1.0000002), "2.000002,-1.0000002")
    testSimple7 = _expected_output((2.000002, 0.0000001), "2.000002,0.0000001")

    testSimple8 = _expected_output(("2.000002", "-120"), "2.000002,-120")


class UnknownProblemTestCase(unittest.TestCase):
    def setUp(self):
        httpretty.enable()
        self.geocoder = OpenCageGeocode('abcde')

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    def test500Status(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body='',
            status=500,
        )

        self.assertRaises(UnknownError, self.geocoder.geocode, "whatever")

    def testNonJson(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body='',
        )

        self.assertRaises(UnknownError, self.geocoder.geocode, "whatever")

    def testNoResultsKey(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body='{"spam": "eggs"}',
        )

        self.assertRaises(UnknownError, self.geocoder.geocode, "whatever")

if __name__ == '__main__':
    unittest.main()
