import opencage
from opencage.geocoder import OpenCageGeocode
import json

key = 'your-key-here'

geocoder = OpenCageGeocode(key)

query = '182 Clerkenwell Road, London'
ret = geocoder.geocode(query)
print(ret._content)
