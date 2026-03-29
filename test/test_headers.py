# encoding: utf-8

from pathlib import Path

import os
import re
import responses

from opencage.geocoder import OpenCageGeocode

# reduce maximum backoff retry time from 120s to 1s
os.environ['BACKOFF_MAX_TIME'] = '1'

geocoder = OpenCageGeocode('abcde', user_agent_comment='OpenCage Test')

user_agent_format = re.compile(
    r'^opencage-python/[\d\.]+ Python/[\d\.]+ (requests|aiohttp)/[\d\.]+ \(OpenCage Test\)$')


@responses.activate
def test_sync():
    responses.add(
        responses.GET,
        geocoder.url,
        body=Path('test/fixtures/uk_postcode.json').read_text(encoding="utf-8"),
        status=200
    )

    geocoder.geocode("EC1M 5RF")

    # Check the User-Agent header in the most recent request
    request = responses.calls[-1].request
    user_agent = request.headers['User-Agent']

    assert user_agent_format.match(user_agent) is not None


@responses.activate
def test_user_agent_comment_crlf_stripped():
    """Test that CR/LF characters are stripped from user_agent_comment to prevent header injection."""
    geocoder_crlf = OpenCageGeocode('abcde', user_agent_comment="bad\r\nInjected-Header: value")

    responses.add(
        responses.GET,
        geocoder_crlf.url,
        body=Path('test/fixtures/uk_postcode.json').read_text(encoding="utf-8"),
        status=200
    )

    geocoder_crlf.geocode("EC1M 5RF")

    request = responses.calls[-1].request
    user_agent = request.headers['User-Agent']

    assert '\r' not in user_agent
    assert '\n' not in user_agent
    assert 'Injected-Header' in user_agent  # still present, just on the same line
