""" Geocoder module. """

import requests
import collections
import six
from datetime import datetime
from decimal import Decimal


class OpenCageGeocodeError(Exception):

    """Base class for all errors/exceptions that can happen when geocoding."""

    pass


class InvalidInputError(OpenCageGeocodeError):

    """There was a problem with the input you provided."""

    pass


class RateLimitExceededError(OpenCageGeocodeError):

    """Your account has exceeded it's limit. Contact OpenCage."""

    def __init__(self, reset_time, reset_to):
        """Constructor."""
        self.reset_time = reset_time
        self.reset_to = reset_to

    def __str__(self):
        """Convert exception to a string."""
        return self.__unicode__()

    def __unicode__(self):
        """Convert exception to a string."""
        return "Your rate limit has expired. It will reset to {0} on {1}".format(self.reset_to, self.reset_time.isoformat())


class OpenCageGeocode(object):

    """
    Geocoder object.

    Initialize it with your API key:

        >>> geocoder = OpenCageGeocode('your-key-here')

    Query:

        >>> geocoder.geocode("London")

    Reverse geocode a latitude & longitude into a point:

        >>> geocoder.reverse_geocode(51.5104, -0.1021)

    """

    url = 'http://prototype.opencagedata.com/geocode/v1/json'
    key = ''

    def __init__(self, key):
        """Constructor."""
        self.key = key

    def geocode(self, query):
        """
        Given a string to search for, return the results from OpenCage's Geocoder.
        """
        if six.PY2:
            # py3 doesn't have unicode() function, and instead we check the text_type later
            try:
                query = unicode(query)
            except UnicodeDecodeError:
                raise InvalidInputError("Input query must be unicode string")

        if not isinstance(query, six.text_type):
            raise InvalidInputError("Input query must be unicode string")

        data = {
            'q': query,
            'key': self.key
        }
        url = self.url
        response = requests.get(url, params=data)

        # TODO check for errors
        # check for non-json
        response_json = response.json()

        if response.status_code == 429:
            # Rate limit exceeded
            reset_time = datetime.utcfromtimestamp(response_json['rate']['reset'])
            raise RateLimitExceededError(reset_to=int(response_json['rate']['limit']), reset_time=reset_time)

        return floatify_latlng(response.json()['results'])

    def reverse_geocode(self, lat, lng):
        """
        Given a latitude & longitude, return an address for that point from OpenCage's Geocoder.
        """
        return self.geocode(query_for_reverse_geocoding(lat, lng))


def _query_for_reverse_geocoding(lat, lng):
    """
    Given a lat & lng, what's the string search query.

    If the API changes, change this function. Only for internal use.
    """
    # have to do some stupid f/Decimal/str stuff to (a) ensure we get as much
    # decimal places as the user already specified and (b) to ensure we don't
    # get e-5 stuff
    return "{0:f},{1:f}".format(Decimal(str(lat)), Decimal(str(lng)))


def floatify_latlng(input_value):
    """
    Work around a JSON dict with string, not float, lat/lngs.

    Given anything (list/dict/etc) it will return that thing again, *but* any
    dict (at any level) that has only 2 elements lat & lng, will be replaced
    with the lat & lng turned into floats.

    If the API returns the lat/lng as strings, and not numbers, then this
    function will 'clean them up' to be floats.
    """
    if isinstance(input_value, collections.Mapping):
        if len(input_value) == 2 and sorted(input_value.keys()) == ['lat', 'lng']:
            # This dict has only 2 keys 'lat' & 'lon'
            return {'lat': float(input_value['lat']), 'lng': float(input_value['lng'])}
        else:
            return dict((key, floatify_latlng(value)) for key, value in input_value.items())
    elif isinstance(input_value, collections.MutableSequence):
        return [floatify_latlng(x) for x in input_value]
    else:
        return input_value
