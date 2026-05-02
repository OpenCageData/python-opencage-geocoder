"""Helpers vendored from opencage.geocoder so the CLI does not depend on the
library's private API. See Changes.txt v1.0.0 entry for context."""

import collections
from decimal import Decimal


def query_for_reverse_geocoding(lat, lng):
    """Format a (lat, lng) pair as the string the API expects for reverse geocoding.

    Uses Decimal(str(...)) to preserve the precision the caller specified and to
    avoid scientific notation (e.g. 1e-5).
    """
    return f"{Decimal(str(lat)):f},{Decimal(str(lng)):f}"


def floatify_latlng(input_value):
    """Recursively convert ``{'lat': ..., 'lng': ...}`` dicts to floats.

    Walks lists and dicts; any dict that contains exactly the two keys ``lat``
    and ``lng`` is rewritten with float values. Other structures pass through
    unchanged. Works around the API occasionally returning lat/lng as strings.
    """
    if isinstance(input_value, collections.abc.Mapping):
        if len(input_value) == 2 and sorted(input_value.keys()) == ['lat', 'lng']:
            return {'lat': _float_if_float(input_value['lat']), 'lng': _float_if_float(input_value['lng'])}

        return dict((key, floatify_latlng(value)) for key, value in input_value.items())

    if isinstance(input_value, collections.abc.MutableSequence):
        return [floatify_latlng(x) for x in input_value]

    return input_value


def _float_if_float(value):
    try:
        return float(value)
    except ValueError:
        return value
