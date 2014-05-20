import requests, json

class OpenCageGeocode:
	url = 'http://prototype.opencagedata.com/geocode/v1/json'
	key = ''

	def __init__(self, key):
		self.key = key

	def geocode(self, query):
		return self.getJSON(query)

	def getJSON(self, query):
		data = {
			'q': query,
			'key': self.key
		}
		url = self.url
		return requests.get(url, params=data)
