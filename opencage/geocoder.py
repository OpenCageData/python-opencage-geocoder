"""Geocoder module for the OpenCage API."""

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


def _validate_domain(domain):
    """Validate that the API domain is an allowed hostname.

    Only subdomains of opencagedata.com, localhost, and 0.0.0.0 are
    permitted. An optional port suffix (e.g. ``localhost:8080``) is allowed.

    Args:
        domain: Hostname string, optionally with a port.

    Returns:
        The validated domain string.

    Raises:
        ValueError: If the domain is not in the allow-list.
    """
    # Strip optional port
    host = domain.rsplit(':', 1)[0] if ':' in domain else domain

    if host in ('localhost', '0.0.0.0'):
        return domain

    if host.endswith('.opencagedata.com'):
        return domain

    raise ValueError(
        f"Invalid API domain '{domain}'. "
        f"Must be a subdomain of opencagedata.com, localhost, or 0.0.0.0."
    )


def backoff_max_time():
    """Return the maximum backoff time in seconds for retrying API requests.

    Returns:
        Maximum time in seconds, from the BACKOFF_MAX_TIME environment
        variable or 120 by default.
    """
    return int(os.environ.get('BACKOFF_MAX_TIME', '120'))


class OpenCageGeocodeError(Exception):
    """Base class for all errors/exceptions that can happen when geocoding."""


class InvalidInputError(OpenCageGeocodeError):
    """There was a problem with the input you provided.

    Attributes:
        message: Error message describing the bad input.
        bad_value: The value that caused the problem.
    """

    def __init__(self, message, bad_value=None):
        super().__init__()
        self.message = message
        self.bad_value = bad_value

    def __unicode__(self):
        return self.message

    __str__ = __unicode__


class UnknownError(OpenCageGeocodeError):
    """There was a problem with the OpenCage server."""


class RateLimitExceededError(OpenCageGeocodeError):
    """Exception raised when account has exceeded its limit."""

    def __unicode__(self):
        """Convert exception to a string."""
        return ("You have used the requests available on your plan. "
                "Please purchase more if you wish to continue: https://opencagedata.com/pricing")

    __str__ = __unicode__


class NotAuthorizedError(OpenCageGeocodeError):
    """Exception raised when an unauthorized API key is used."""

    def __unicode__(self):
        """Convert exception to a string."""
        return "Your API key is not authorized. You may have entered it incorrectly."

    __str__ = __unicode__


class ForbiddenError(OpenCageGeocodeError):
    """Exception raised when a blocked or suspended API key is used."""

    def __unicode__(self):
        """Convert exception to a string."""
        return "Your API key has been blocked or suspended."

    __str__ = __unicode__


class AioHttpError(OpenCageGeocodeError):
    """Exception raised for errors related to async HTTP calls with aiohttp."""


class SSLError(OpenCageGeocodeError):
    """Exception raised when SSL connection to OpenCage server fails."""

    def __unicode__(self):
        """Convert exception to a string."""
        return ("SSL Certificate error connecting to OpenCage API. This is usually due to "
                "outdated CA root certificates of the operating system. "
                )

    __str__ = __unicode__


class OpenCageGeocode:
    """Client for the OpenCage Geocoding API.

    Supports both synchronous and asynchronous geocoding. Can be used as
    a context manager for connection pooling.

    Example:
        >>> geocoder = OpenCageGeocode('your-key-here')
        >>> geocoder.geocode("London")
        >>> geocoder.reverse_geocode(51.5104, -0.1021)
    """

    session = None

    def __init__(
            self,
            key=None,
            protocol='https',
            domain=DEFAULT_DOMAIN,
            sslcontext=None,
            user_agent_comment=None):
        """Initialize the geocoder.

        Args:
            key: OpenCage API key. If not provided, reads from the
                OPENCAGE_API_KEY environment variable.
            protocol: HTTP protocol to use, either 'http' or 'https'.
            domain: API domain to connect to.
            sslcontext: SSL context for async (aiohttp) connections.
            user_agent_comment: Optional comment appended to the User-Agent header.

        Raises:
            ValueError: If no API key is provided or found in the environment.
        """
        self.key = key if key is not None else os.environ.get('OPENCAGE_API_KEY')

        if self.key is None:
            raise ValueError(
                "API key not provided. "
                "Either pass a 'key' parameter or set the OPENCAGE_API_KEY environment variable."
            )

        if protocol and protocol not in ('http', 'https'):
            protocol = 'https'
        _validate_domain(domain)
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
        """Geocode an address string.

        Args:
            query: Address or place name to geocode.
            **kwargs: Additional API parameters (e.g. language, countrycode).
                Pass raw_response=True to get the full API response dict
                instead of just the results list.

        Returns:
            List of geocoding results with lat/lng and components, or the
            full API response dict if raw_response=True.

        Raises:
            InvalidInputError: If query is not a unicode string.
            RateLimitExceededError: If API quota is exceeded.
            UnknownError: If something goes wrong with the OpenCage API.
            AioHttpError: If called inside an async context manager.
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
        """Async version of geocode.

        Must be used inside an async context manager (``async with``).

        Args:
            query: Address or place name to geocode.
            **kwargs: Additional API parameters (e.g. language, countrycode).
                Pass raw_response=True to get the full API response dict
                instead of just the results list.

        Returns:
            List of geocoding results with lat/lng and components, or the
            full API response dict if raw_response=True.

        Raises:
            InvalidInputError: If query is not a unicode string.
            RateLimitExceededError: If API quota is exceeded.
            UnknownError: If something goes wrong with the OpenCage API.
            AioHttpError: If aiohttp is not installed or no async session is active.
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
        """Reverse geocode a latitude/longitude pair into an address.

        Args:
            lat: Latitude (-90 to 90).
            lng: Longitude (-180 to 180).
            **kwargs: Additional API parameters (e.g. language, countrycode).

        Returns:
            List of geocoding results with address components.

        Raises:
            InvalidInputError: If latitude or longitude is out of bounds.
            RateLimitExceededError: If API quota is exceeded.
            UnknownError: If something goes wrong with the OpenCage API.
        """

        self._validate_lat_lng(lat, lng)

        return self.geocode(_query_for_reverse_geocoding(lat, lng), **kwargs)

    async def reverse_geocode_async(self, lat, lng, **kwargs):
        """Async version of reverse_geocode.

        Must be used inside an async context manager (``async with``).

        Args:
            lat: Latitude (-90 to 90).
            lng: Longitude (-180 to 180).
            **kwargs: Additional API parameters (e.g. language, countrycode).

        Returns:
            List of geocoding results with address components.

        Raises:
            InvalidInputError: If latitude or longitude is out of bounds.
            RateLimitExceededError: If API quota is exceeded.
            UnknownError: If something goes wrong with the OpenCage API.
        """

        self._validate_lat_lng(lat, lng)

        return await self.geocode_async(_query_for_reverse_geocoding(lat, lng), **kwargs)

    @backoff.on_exception(
        backoff.expo,
        (UnknownError, requests.exceptions.RequestException),
        max_tries=5, max_time=backoff_max_time)
    def _opencage_request(self, params):
        """Send a synchronous geocoding request to the OpenCage API.

        Args:
            params: Dict of query parameters for the API request.

        Returns:
            Parsed JSON response dict from the API.

        Raises:
            NotAuthorizedError: If the API key is invalid.
            ForbiddenError: If the API key is blocked or suspended.
            RateLimitExceededError: If the rate limit is exceeded.
            UnknownError: If the server returns an error or invalid JSON.
        """
        if self.session:
            response = self.session.get(self.url, params=params, headers=self._opencage_headers('aiohttp'), timeout=30)
        else:
            response = requests.get(self.url, params=params, headers=self._opencage_headers('requests'), timeout=30)

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
        """Build the HTTP headers for an API request.

        Args:
            client: HTTP client name ('requests' or 'aiohttp').

        Returns:
            Dict with User-Agent header.
        """
        client_version = requests.__version__
        if client == 'aiohttp':
            client_version = aiohttp.__version__

        py_version = '.'.join(str(x) for x in sys.version_info[0:3])

        comment = ''
        if self.user_agent_comment:
            clean = self.user_agent_comment.replace('\r', '').replace('\n', '')
            comment = f" ({clean})"

        return {
            'User-Agent': f"opencage-python/{__version__} Python/{py_version} {client}/{client_version}{comment}"
        }

    async def _opencage_async_request(self, params):
        """Send an async geocoding request to the OpenCage API.

        Args:
            params: Dict of query parameters for the API request.

        Returns:
            Parsed JSON response dict from the API.

        Raises:
            NotAuthorizedError: If the API key is invalid.
            ForbiddenError: If the API key is blocked or suspended.
            RateLimitExceededError: If the rate limit is exceeded.
            UnknownError: If the server returns an error or invalid JSON.
            SSLError: If the SSL connection fails.
        """
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with self.session.get(self.url, params=params, ssl=self.sslcontext, timeout=timeout) as response:
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
        """Build the request parameters dict for an API call.

        Args:
            query: The geocoding query string.
            params: Additional API parameters from the caller.

        Returns:
            Dict of parameters ready to send to the API.

        Raises:
            InvalidInputError: If query is not a unicode string.
        """
        if not isinstance(query, str):
            error_message = "Input must be a unicode string, not " + repr(query)[:100]
            raise InvalidInputError(error_message, bad_value=query)

        data = {'q': query, 'key': self.key}
        data.update(params)  # Add user parameters
        return data

    def _validate_lat_lng(self, lat, lng):
        """Validate latitude and longitude values.

        Args:
            lat: Latitude value to validate.
            lng: Longitude value to validate.

        Raises:
            InvalidInputError: If latitude is not in [-90, 90] or longitude
                is not in [-180, 180].
        """
        try:
            lat_float = float(lat)
            if not -90 <= lat_float <= 90:
                raise InvalidInputError(f"Latitude must be a number between -90 and 90, not {lat}", bad_value=lat)
        except ValueError:
            raise InvalidInputError(f"Latitude must be a number between -90 and 90, not {lat}", bad_value=lat)

        try:
            lng_float = float(lng)
            if not -180 <= lng_float <= 180:
                raise InvalidInputError(f"Longitude must be a number between -180 and 180, not {lng}", bad_value=lng)
        except ValueError:
            raise InvalidInputError(f"Longitude must be a number between -180 and 180, not {lng}", bad_value=lng)


def _query_for_reverse_geocoding(lat, lng):
    """Build the query string for a reverse geocoding request.

    Args:
        lat: Latitude value.
        lng: Longitude value.

    Returns:
        Comma-separated string of lat and lng with full decimal precision.
    """
    # have to do some stupid f/Decimal/str stuff to (a) ensure we get as much
    # decimal places as the user already specified and (b) to ensure we don't
    # get e-5 stuff
    return f"{Decimal(str(lat)):f},{Decimal(str(lng)):f}"


def float_if_float(float_string):
    """Convert a string to float if possible.

    Args:
        float_string: String to attempt to convert.

    Returns:
        The float value if conversion succeeds, or the original string.
    """
    try:
        float_val = float(float_string)
        return float_val
    except ValueError:
        return float_string


def floatify_latlng(input_value):
    """Recursively convert string lat/lng values to floats in API results.

    Any dict at any nesting level that has exactly two keys 'lat' and 'lng'
    will have its values converted to floats.

    Args:
        input_value: A dict, list, or scalar from the API response.

    Returns:
        The same structure with lat/lng string values converted to floats.
    """
    if isinstance(input_value, collections.abc.Mapping):
        if len(input_value) == 2 and sorted(input_value.keys()) == ['lat', 'lng']:
            # This dict has only 2 keys 'lat' & 'lon'
            return {'lat': float_if_float(input_value["lat"]), 'lng': float_if_float(input_value["lng"])}

        return dict((key, floatify_latlng(value)) for key, value in input_value.items())

    if isinstance(input_value, collections.abc.MutableSequence):
        return [floatify_latlng(x) for x in input_value]

    return input_value
