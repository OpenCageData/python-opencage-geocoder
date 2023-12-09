# encoding: utf-8

from pathlib import Path

import os
import re
import httpretty

from httpretty import httprettified
from opencage.geocoder import OpenCageGeocode

# reduce maximum backoff retry time from 120s to 1s
os.environ['BACKOFF_MAX_TIME'] = '1'

geocoder = OpenCageGeocode('abcde')

user_agent_format = re.compile(r'^opencage-python/[\d\.]+ Python/[\d\.]+ (requests|aiohttp)/[\d\.]+$')

@httprettified
def test_sync():
    httpretty.register_uri(
        httpretty.GET,
        geocoder.url,
        body=Path('test/fixtures/uk_postcode.json').read_text(encoding="utf-8")
    )

    geocoder.geocode("EC1M 5RF")
    user_agent = httpretty.last_request().headers['User-Agent']

    assert user_agent_format.match(user_agent) is not None
