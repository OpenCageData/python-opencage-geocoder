""" Geocoder module. """

from decimal import Decimal
import collections

import os
import sys
import requests
import backoff
from .version import __version__

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

DEFAULT_DOMAIN = 'api.opencagedata.com'

def backoff_max_time():
    return int(os.environ.get('BACKOFF_MAX_TIME', '120'))

class OpenCageGeocodeError(Exception):

    """Base class for all errors/exceptions that can happen when geocoding."""


class InvalidInputError(OpenCageGeocodeError):

    """
    There was a problem with the input you provided.

    :var bad_value: The value that caused the problem
    """

    def __init__(self, bad_value):
        super().__init__()
        self.bad_value = bad_value

    def __unicode__(self):
        return "Input must be a unicode string, not "+repr(self.bad_value)[:100]

    __str__ = __unicode__


class UnknownError(OpenCageGeocodeError):

    """There was a problem with the OpenCage server."""


class RateLimitExceededError(OpenCageGeocodeError):

    """
    Exception raised when account has exceeded it's limit.
    """

    def __unicode__(self):
        """Convert exception to a string."""
        return ("You have used the requests available on your plan. "
                "Please purchase more if you wish to continue: https://opencagedata.com/pricing")

    __str__ = __unicode__


class NotAuthorizedError(OpenCageGeocodeError):

    """
    Exception raised when an unautorized API key is used.
    """

    def __unicode__(self):
        """Convert exception to a string."""
        return "Your API key is not authorized. You may have entered it incorrectly."

    __str__ = __unicode__


class ForbiddenError(OpenCageGeocodeError):

    """
    Exception raised when a blocked or suspended API key is used.
    """

    def __unicode__(self):
        """Convert exception to a string."""
        return "Your API key has been blocked or suspended."

    __str__ = __unicode__


class AioHttpError(OpenCageGeocodeError):

    """
    Exceptions related to async HTTP calls with aiohttp
    """


class SSLError(OpenCageGeocodeError):

    """
    Exception raised when SSL connection to OpenCage server fails.
    """

    def __unicode__(self):
        """Convert exception to a string."""
        return ("SSL Certificate error connecting to OpenCage API. This is usually due to "
               "outdated CA root certificates of the operating system. "
               )

    __str__ = __unicode__


class OpenCageGeocode:

    """
    Geocoder object.

    Initialize it with your API key:

        >>> geocoder = OpenCageGeocode('your-key-here')

    Query:

        >>> geocoder.geocode("London")

    Reverse geocode a latitude & longitude into a place:

        >>> geocoder.reverse_geocode(51.5104, -0.1021)

    """

    session = None

    def __init__(self, key, protocol='https', domain=DEFAULT_DOMAIN, sslcontext=None, user_agent_comment=None):
        """Constructor."""
        self.key = key

        if protocol and protocol not in ('http', 'https'):
            protocol = 'https'
        self.url = protocol + '://' + domain + '/geocode/v1/json'

        # https://docs.aiohttp.org/en/stable/client_advanced.html#ssl-control-for-tcp-sockets
        self.sslcontext = sslcontext

        self.user_agent_comment = user_agent_comment

    def __enter__(self):
        self.session = requests.Session()
        return self

    def __exit__(self, *args):
        self.session.close()
        self.session = None
        return False

    async def __aenter__(self):
        if not AIOHTTP_AVAILABLE:
            raise AioHttpError("You must install `aiohttp` to use async methods")

        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args):
        await self.session.close()
        self.session = None
        return False

    def geocode(self, query, **kwargs):
        """
        Given a string to search for, return the list (array) of results from OpenCage's Geocoder.

        :param string query: String to search for

        :returns: Dict results
        :raises InvalidInputError: if the query string is not a unicode string
        :raises RateLimitExceededError: if you have exceeded the number of queries you can make.
        :                                  Exception says when you can try again
        :raises UnknownError: if something goes wrong with the OpenCage API

        """

        if self.session and isinstance(self.session, aiohttp.client.ClientSession):
            raise AioHttpError("Cannot use `geocode` in an async context, use `geocode_async`.")

        raw_response = kwargs.pop('raw_response', False)
        request = self._parse_request(query, kwargs)
        response = self._opencage_request(request)

        if raw_response:
            return response

        return floatify_latlng(response['results'])

    async def geocode_async(self, query, **kwargs):
        """
        Aync version of `geocode`.

        Given a string to search for, return the list (array) of results from OpenCage's Geocoder.

        :param string query: String to search for

        :returns: Dict results
        :raises InvalidInputError: if the query string is not a unicode string
        :raises RateLimitExceededError: if exceeded number of queries you can make. You can try again
        :raises UnknownError: if something goes wrong with the OpenCage API

        """

        if not AIOHTTP_AVAILABLE:
            raise AioHttpError("You must install `aiohttp` to use async methods.")

        if not self.session:
            raise AioHttpError("Async methods must be used inside an async context.")

        if not isinstance(self.session, aiohttp.client.ClientSession):
            raise AioHttpError("You must use `geocode_async` in an async context.")

        raw_response = kwargs.pop('raw_response', False)
        request = self._parse_request(query, kwargs)
        response = await self._opencage_async_request(request)

        if raw_response:
            return response

        return floatify_latlng(response['results'])

    def reverse_geocode(self, lat, lng, **kwargs):
        """
        Given a latitude & longitude, return an address for that point from OpenCage's Geocoder.

        :param lat: Latitude
        :param lng: Longitude
        :return: Results from OpenCageData
        :rtype: dict
        :raises RateLimitExceededError: if you have exceeded the number of queries you can make.
        :                                  Exception says when you can try again
        :raises UnknownError: if something goes wrong with the OpenCage API
        """
        return self.geocode(_query_for_reverse_geocoding(lat, lng), **kwargs)

    async def reverse_geocode_async(self, lat, lng, **kwargs):
        """
        Aync version of `reverse_geocode`.

        Given a latitude & longitude, return an address for that point from OpenCage's Geocoder.

        :param lat: Latitude
        :param lng: Longitude
        :return: Results from OpenCageData
        :rtype: dict
        :raises RateLimitExceededError: if exceeded number of queries you can make. You can try again
        :raises UnknownError: if something goes wrong with the OpenCage API
        """
        return await self.geocode_async(_query_for_reverse_geocoding(lat, lng), **kwargs)

    @backoff.on_exception(
        backoff.expo,
        (UnknownError, requests.exceptions.RequestException),
        max_tries=5, max_time=backoff_max_time)
    def _opencage_request(self, params):

        if self.session:
            response = self.session.get(self.url, params=params, headers=self._opencage_headers('aiohttp'))
        else:
            response = requests.get(self.url, params=params, headers=self._opencage_headers('requests')) # pylint: disable=missing-timeout

        try:
            response_json = response.json()
        except ValueError as excinfo:
            raise UnknownError("Non-JSON result from server") from excinfo

        if response.status_code == 401:
            raise NotAuthorizedError()

        if response.status_code == 403:
            raise ForbiddenError()

        if response.status_code in (402, 429):
            raise RateLimitExceededError()

        if response.status_code == 500:
            raise UnknownError("500 status code from API")

        if 'results' not in response_json:
            raise UnknownError("JSON from API doesn't have a 'results' key")

        return response_json

    def _opencage_headers(self, client):
        client_version = requests.__version__
        if client == 'aiohttp':
            client_version = aiohttp.__version__

        py_version = '.'.join(str(x) for x in sys.version_info[0:3])

        comment = ''
        if self.user_agent_comment:
            comment = f" ({self.user_agent_comment})"

        return {
            'User-Agent': f"opencage-python/{__version__} Python/{py_version} {client}/{client_version}{comment}"
        }

    async def _opencage_async_request(self, params):
        try:
            async with self.session.get(self.url, params=params, ssl=self.sslcontext) as response:
                try:
                    response_json = await response.json()
                except ValueError as excinfo:
                    raise UnknownError("Non-JSON result from server") from excinfo

                if response.status == 401:
                    raise NotAuthorizedError()

                if response.status == 403:
                    raise ForbiddenError()

                if response.status in (402, 429):
                    raise RateLimitExceededError()

                if response.status == 500:
                    raise UnknownError("500 status code from API")

                if 'results' not in response_json:
                    raise UnknownError("JSON from API doesn't have a 'results' key")

                return response_json
        except aiohttp.ClientSSLError as exp:
            raise SSLError() from exp
        except aiohttp.client_exceptions.ClientConnectorCertificateError as exp:
            raise SSLError() from exp

    def _parse_request(self, query, params):
        if not isinstance(query, str):
            raise InvalidInputError(bad_value=query)

        data = { 'q': query, 'key': self.key }
        data.update(params) # Add user parameters
        return data


def _query_for_reverse_geocoding(lat, lng):
    """
    Given a lat & lng, what's the string search query.

    If the API changes, change this function. Only for internal use.
    """
    # have to do some stupid f/Decimal/str stuff to (a) ensure we get as much
    # decimal places as the user already specified and (b) to ensure we don't
    # get e-5 stuff
    return f"{Decimal(str(lat)):f},{Decimal(str(lng)):f}"


def float_if_float(float_string):
    """
    Given a float string, returns the float value.
    On value error returns the original string.
    """
    try:
        float_val = float(float_string)
        return float_val
    except ValueError:
        return float_string


def floatify_latlng(input_value):
    """
    Work around a JSON dict with string, not float, lat/lngs.

    Given anything (list/dict/etc) it will return that thing again, *but* any
    dict (at any level) that has only 2 elements lat & lng, will be replaced
    with the lat & lng turned into floats.

    If the API returns the lat/lng as strings, and not numbers, then this
    function will 'clean them up' to be floats.
    """
    if isinstance(input_value, collections.abc.Mapping):
        if len(input_value) == 2 and sorted(input_value.keys()) == ['lat', 'lng']:
            # This dict has only 2 keys 'lat' & 'lon'
            return {'lat': float_if_float(input_value["lat"]), 'lng': float_if_float(input_value["lng"])}

        return dict((key, floatify_latlng(value)) for key, value in input_value.items())

    if isinstance(input_value, collections.abc.MutableSequence):
        return [floatify_latlng(x) for x in input_value]

    return input_value
