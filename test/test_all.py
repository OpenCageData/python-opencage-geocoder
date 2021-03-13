# encoding: utf-8

from pathlib import Path

import os
import httpretty

from httpretty import httprettified
from opencage.geocoder import OpenCageGeocode

# reduce maximum backoff retry time from 120s to 1s
os.environ['BACKOFF_MAX_TIME'] = '1'


geocoder = OpenCageGeocode('abcde')

@httprettified
def test_gb_postcode():
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body=Path('test/fixtures/uk_postcode.json').read_text()
    )

    results = geocoder.geocode("EC1M 5RF")
    assert any((abs(result['geometry']['lat'] - 51.5201666) < 0.05 and abs(result['geometry']['lng'] - -0.0985142) < 0.05) for result in results)


@httprettified
def test_australia():
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body=Path('test/fixtures/mudgee_australia.json').read_text()
    )

    results = geocoder.geocode("Mudgee, Australia")
    assert any((abs(result['geometry']['lat'] - -32.5980702) < 0.05 and abs(result['geometry']['lng'] - 149.5886383) < 0.05) for result in results)


@httprettified
def testMunster():
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body=Path('test/fixtures/muenster.json').read_text()
    )

    results = geocoder.geocode("Münster")
    assert any((abs(result['geometry']['lat'] - 51.9625101) < 0.05 and abs(result['geometry']['lng'] - 7.6251879) < 0.05) for result in results)

@httprettified
def testDonostia():
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body=Path('test/fixtures/donostia.json').read_text()

    )

    results =geocoder.geocode("Donostia")
    assert any((abs(result['geometry']['lat'] - 43.300836) < 0.05 and abs(result['geometry']['lng'] - -1.9809529) < 0.05) for result in results)

    # test that the results are in unicode
    assert results[0]['formatted'] == 'San Sebastián, Autonomous Community of the Basque Country, Spain'
