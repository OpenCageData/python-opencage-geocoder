# encoding: utf-8


from opencage.geocoder import OpenCageGeocode

# Check if protocol can be set
geocoder = OpenCageGeocode('abcde', 'http')
assert geocoder.url == 'http://api.opencagedata.com/geocode/v1/json'
