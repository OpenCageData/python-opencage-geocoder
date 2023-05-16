# encoding: utf-8

from pathlib import Path

import os
import httpretty

from httpretty import httprettified
from opencage.geocoder import OpenCageGeocode

# reduce maximum backoff retry time from 120s to 1s
os.environ['BACKOFF_MAX_TIME'] = '1'


geocoder = OpenCageGeocode('abcde')


def _any_result_around(results, lat=None, lon=None):
    for result in results:
        if (abs(result['geometry']['lat'] - lat) < 0.05 and
            abs(result['geometry']['lng'] - lon) < 0.05):
            return True
    return False

@httprettified
def test_gb_postcode():
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body=Path('test/fixtures/uk_postcode.json').read_text(encoding="utf-8")
    )

    results = geocoder.geocode("EC1M 5RF")
    assert _any_result_around(results, lat=51.5201666, lon=-0.0985142)


@httprettified
def test_australia():
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body=Path('test/fixtures/mudgee_australia.json').read_text(encoding="utf-8")
    )

    results = geocoder.geocode("Mudgee, Australia")
    assert _any_result_around(results, lat=-32.5980702, lon=149.5886383)


@httprettified
def test_munster():
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body=Path('test/fixtures/muenster.json').read_text(encoding="utf-8")
    )

    results = geocoder.geocode("Münster")
    assert _any_result_around(results, lat=51.9625101, lon=7.6251879)

@httprettified
def test_donostia():
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body=Path('test/fixtures/donostia.json').read_text(encoding="utf-8")

    )

    results =geocoder.geocode("Donostia")
    assert _any_result_around(results, lat=43.300836, lon=-1.9809529)

    # test that the results are in unicode
    assert results[0]['formatted'] == 'San Sebastián, Autonomous Community of the Basque Country, Spain'
