import asyncio
import os
import socket
import threading
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import quote_plus, urlencode

import aiohttp
import pytest
import requests
import responses

from opencage.geocoder import OpenCageGeocode, NetworkError, NetworkTimeoutError, UnknownError

os.environ['BACKOFF_MAX_TIME'] = '1'

KEY = 'oc_gc_0123456789abcdef0123456789abcdef'


def assert_key_not_exposed(exc, key=KEY):
    formatted = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    for text in (str(exc), repr(exc), formatted):
        assert key not in text
        assert quote_plus(key) not in text


def closed_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


class HtmlErrorPageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(502)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<html><body><h1>502 Bad Gateway</h1></body></html>')

    def log_message(self, *args):
        pass


@pytest.fixture(scope='module')
def html_server_port():
    server = HTTPServer(('127.0.0.1', 0), HtmlErrorPageHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server.server_address[1]
    server.shutdown()
    server.server_close()


def test_connection_refused():
    geocoder = OpenCageGeocode(KEY, protocol='http', domain=f'localhost:{closed_port()}')

    with pytest.raises(NetworkError) as excinfo:
        geocoder.geocode('whatever')

    assert not isinstance(excinfo.value, NetworkTimeoutError)
    assert str(excinfo.value).startswith('ConnectionError: ')
    assert 'key=[REDACTED]' in str(excinfo.value)
    assert_key_not_exposed(excinfo.value)


def test_connection_refused_url_encoded_key():
    key = 'not a valid key+&'
    geocoder = OpenCageGeocode(key, protocol='http', domain=f'localhost:{closed_port()}')

    with pytest.raises(NetworkError) as excinfo:
        geocoder.geocode('whatever')

    assert 'key=[REDACTED]' in str(excinfo.value)
    assert_key_not_exposed(excinfo.value, key)


def test_tls_failure(html_server_port):
    geocoder = OpenCageGeocode(KEY, protocol='https', domain=f'localhost:{html_server_port}')

    with pytest.raises(NetworkError) as excinfo:
        geocoder.geocode('whatever')

    assert str(excinfo.value).startswith('SSLError: ')
    assert_key_not_exposed(excinfo.value)


@responses.activate
def test_timeout():
    geocoder = OpenCageGeocode(KEY)
    responses.add(
        responses.GET,
        geocoder.url,
        body=requests.exceptions.ConnectTimeout(
            "HTTPSConnectionPool(host='api.opencagedata.com', port=443): Max retries exceeded "
            f"with url: /geocode/v1/json?q=whatever&key={KEY} (Caused by ConnectTimeoutError())"
        ),
    )

    with pytest.raises(NetworkTimeoutError) as excinfo:
        geocoder.geocode('whatever')

    assert isinstance(excinfo.value, asyncio.TimeoutError)
    assert_key_not_exposed(excinfo.value)


@pytest.mark.asyncio
async def test_async_html_error_page(html_server_port):
    async with OpenCageGeocode(KEY, protocol='http', domain=f'localhost:{html_server_port}') as geocoder:
        with pytest.raises(UnknownError) as excinfo:
            await geocoder.geocode_async('whatever')

    assert str(excinfo.value) == 'Non-JSON result from server'
    assert_key_not_exposed(excinfo.value)


@pytest.mark.asyncio
async def test_async_connection_refused():
    async with OpenCageGeocode(KEY, protocol='http', domain=f'localhost:{closed_port()}') as geocoder:
        with pytest.raises(NetworkError) as excinfo:
            await geocoder.geocode_async('whatever')

    assert not isinstance(excinfo.value, NetworkTimeoutError)
    assert_key_not_exposed(excinfo.value)


@pytest.mark.asyncio
async def test_async_connection_timeout(monkeypatch):
    def get_that_times_out(self, url, params=None, **kwargs):
        raise aiohttp.ServerTimeoutError(f"Connection timeout to host {url}?{urlencode(params)}")

    monkeypatch.setattr(aiohttp.ClientSession, 'get', get_that_times_out)

    async with OpenCageGeocode(KEY) as geocoder:
        with pytest.raises(NetworkTimeoutError) as excinfo:
            await geocoder.geocode_async('whatever')

    assert isinstance(excinfo.value, asyncio.TimeoutError)
    assert 'key=[REDACTED]' in str(excinfo.value)
    assert_key_not_exposed(excinfo.value)
