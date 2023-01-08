from pprint import pprint
from opencage.geocoder import OpenCageGeocode

APIKEY = 'your-key-here'

geocoder = OpenCageGeocode(APIKEY)

results = geocoder.reverse_geocode(44.8303087, -0.5761911)
pprint(results)
# [{'components': {'city': 'Bordeaux',
#                  'country': 'France',
#                  'country_code': 'fr',
#                  'county': 'Bordeaux',
#                  'house_number': '11',
#                  'political_union': 'European Union',
#                  'postcode': '33800',
#                  'road': 'Rue Sauteyron',
#                  'state': 'New Aquitaine',
#                  'suburb': 'Bordeaux Sud'},
#   'formatted': '11 Rue Sauteyron, 33800 Bordeaux, France',
#   'geometry': {'lat': 44.8303087, 'lng': -0.5761911}}]
