.. OpenCage Geocoder documentation master file, created by
   sphinx-quickstart on Sat Jun  7 14:38:18 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to OpenCage Geocoder's documentation!
=============================================

.. toctree::
   :maxdepth: 2

   hacking

.. autoclass:: opencage.geocoder.OpenCageGeocode
    :members:

.. autoclass:: opencage.geocoder.InvalidInputError

.. autoclass:: opencage.geocoder.RateLimitExceededError

.. autoclass:: opencage.geocoder.UnknownError

Sample Return Format
--------------------

Results from OpenCage Geocode

    >>> geocoder = OpenCageGeocode('your-key-here')
    >>> geocoder.geocode("London")
    [{u'annotations': {},
      u'bounds': {u'northeast': {'lat': 51.6918741, 'lng': 0.3340155},
                  u'southwest': {'lat': 51.2867602, 'lng': -0.510375}},
      u'components': {u'city': u'London',
                      u'country': u'United Kingdom',
                      u'country_code': u'gb',
                      u'county': u'London',
                      u'state': u'England',
                      u'state_district': u'Greater London'},
      u'formatted': u'London, London, Greater London, England, United Kingdom, gb',
      u'geometry': {'lat': 51.5073219, 'lng': -0.1276474}},
     {u'annotations': {},
      u'bounds': {u'northeast': {'lat': 43.148097, 'lng': -81.0860295},
                  u'southwest': {'lat': 42.828097, 'lng': -81.4060295}},
      u'components': {u'city': u'London',
                      u'country': u'Canada',
                      u'country_code': u'ca',
                      u'state': u'Ontario'},
      u'formatted': u'London, Ontario, Canada, ca',
      u'geometry': {'lat': 42.988097, 'lng': -81.2460295}},
     {u'annotations': {},
      u'bounds': {u'northeast': {'lat': 37.15226, 'lng': -84.0359569},
                  u'southwest': {'lat': 37.079759, 'lng': -84.1262619}},
      u'components': {u'city': u'London',
                      u'country': u'United States of America',
                      u'country_code': u'us',
                      u'county': u'Laurel County',
                      u'state': u'Kentucky'},
      u'formatted': u'London, Laurel County, Kentucky, United States of America, us',
      u'geometry': {'lat': 37.1289771, 'lng': -84.0832646}},
     {u'annotations': {},
      u'bounds': {u'northeast': {'lat': 43.0677775, 'lng': -88.9928881},
                  u'southwest': {'lat': 43.0277775, 'lng': -89.0328881}},
      u'components': {u'country': u'United States of America',
                      u'country_code': u'us',
                      u'county': u'Dane County',
                      u'hamlet': u'London',
                      u'state': u'Wisconsin'},
      u'formatted': u'London, Dane County, Wisconsin, United States of America, us',
      u'geometry': {'lat': 43.0477775, 'lng': -89.0128881}},
     {u'annotations': {},
      u'bounds': {u'northeast': {'lat': 39.921786, 'lng': -83.3899969},
                  u'southwest': {'lat': 39.85928, 'lng': -83.4789229}},
      u'components': {u'city': u'London',
                      u'country': u'United States of America',
                      u'country_code': u'us',
                      u'county': u'Madison County',
                      u'state': u'Ohio'},
      u'formatted': u'London, Madison County, Ohio, United States of America, us',
      u'geometry': {'lat': 39.8864493, 'lng': -83.448253}},
     {u'annotations': {},
      u'bounds': {u'northeast': {'lat': 36.4884367, 'lng': -119.4385394},
                  u'southwest': {'lat': 36.4734452, 'lng': -119.4497698}},
      u'components': {u'country': u'United States of America',
                      u'country_code': u'us',
                      u'county': u'Tulare County',
                      u'state': u'California',
                      u'village': u'London'},
      u'formatted': u'London, Tulare County, California, United States of America, us',
      u'geometry': {'lat': 36.4760619, 'lng': -119.4431785}},
     {u'annotations': {},
      u'bounds': {u'northeast': {'lat': 35.33814, 'lng': -93.1873749},
                  u'southwest': {'lat': 35.315577, 'lng': -93.2726929}},
      u'components': {u'city': u'London',
                      u'country': u'United States of America',
                      u'country_code': u'us',
                      u'county': u'Pope County',
                      u'state': u'Arkansas'},
      u'formatted': u'London, Pope County, Arkansas, United States of America, us',
      u'geometry': {'lat': 35.326859, 'lng': -93.2405016007635}},
     {u'annotations': {},
      u'bounds': {u'northeast': {'lat': 38.2143567, 'lng': -81.3486944},
                  u'southwest': {'lat': 38.1743567, 'lng': -81.3886944}},
      u'components': {u'country': u'United States of America',
                      u'country_code': u'us',
                      u'county': u'Kanawha County',
                      u'hamlet': u'London',
                      u'state': u'West Virginia'},
      u'formatted': u'London, Kanawha County, West Virginia, United States of America, us',
      u'geometry': {'lat': 38.1943567, 'lng': -81.3686944}},
     {u'annotations': {},
      u'bounds': {u'northeast': {'lat': 32.2509892, 'lng': -94.9243839},
                  u'southwest': {'lat': 32.2109892, 'lng': -94.9643839}},
      u'components': {u'country': u'United States of America',
                      u'country_code': u'us',
                      u'county': u'Rusk County',
                      u'hamlet': u'London',
                      u'state': u'Texas'},
      u'formatted': u'London, Rusk County, Texas, United States of America, us',
      u'geometry': {'lat': 32.2309892, 'lng': -94.9443839}},
     {u'annotations': {},
      u'bounds': {u'northeast': {'lat': 40.9303338, 'lng': -82.6093412},
                  u'southwest': {'lat': 40.8903338, 'lng': -82.6493412}},
      u'components': {u'country': u'United States of America',
                      u'country_code': u'us',
                      u'county': u'Richland County',
                      u'hamlet': u'London',
                      u'state': u'Ohio'},
      u'formatted': u'London, Richland County, Ohio, United States of America, us',
      u'geometry': {'lat': 40.9103338, 'lng': -82.6293412}}]




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

