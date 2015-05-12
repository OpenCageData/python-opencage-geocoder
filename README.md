# OpenCage Data Geocoding Module for Python

A Python module that uses [OpenCage Data's](http://www.opencagedata.com/)
geocoder.

## Usage

Install the module:

```bash
pip install opencage
```

Load the module:

```python
from opencage.geocoder import OpenCageGeocode
```

Create an instance of the geocoder module, passing a valid OpenCage Data Geocoder API key
as a parameter to the geocoder modules's constructor:

```python
key = 'your-api-key-here'
geocoder = OpenCageGeocode(key)
```

Pass a string containing the query or address to be geocoded to the modules's `geocode` method:

```python
query = "82 Clerkenwell Road, London";
result = geocoder.geocode(query)
```

### Reverse geocoding

Turn a lat/long into an address with the ``reverse_geocode`` method:

    results = geocoder.reverse_geocode(51.51024, -0.10303)


### Exceptions

If anything goes wrong, then an exception will be raised: ``InvalidInputError`` for non-unicode query strings, ``UnknownError`` if there's some problem with the API (bad results, 500 status code, etc). ``RateLimitExceededError`` if you go past your rate limit.
