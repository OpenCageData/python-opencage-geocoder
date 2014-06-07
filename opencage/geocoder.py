import requests
import collections
import six


class OpenCageGeocodeException(Exception):
    pass


class OpenCageGeocodeInvalidInputException(OpenCageGeocodeException):
    pass


class OpenCageGeocode(object):
    url = 'http://prototype.opencagedata.com/geocode/v1/json'
    key = ''

    def __init__(self, key):
        self.key = key

    def geocode(self, query):
        if six.PY2:
            try:
                query = unicode(query)
            except UnicodeDecodeError:
                raise OpenCageGeocodeInvalidInputException("Input query must be unicode string")

        if not isinstance(query, six.text_type):
            raise OpenCageGeocodeInvalidInputException("Input query must be unicode string")

        data = {
            'q': query,
            'key': self.key
        }
        url = self.url
        response = requests.get(url, params=data)
        #print response.content
        # TODO check for rate limiting
        # TODO check for errors
        return floatify_latlng(response.json()['results'])

        #return response.json()


def floatify_latlng(input_value):
    """
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
