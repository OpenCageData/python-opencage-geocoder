# Sample forward geocode: http://127.0.0.1:5000/forward/147%20Farm%20STreet%20Blackstone%20MA%2001504
#
# Sample reverse geocode: http://127.0.0.1:5000/reverse/42.036488/-71.519678/
import json
from flask import Flask
from flask import request
from opencage.geocoder import OpenCageGeocode

app = Flask(__name__)
_key = OPEN_CAGE_KEY = "db6a41dce5777db388d7dc348358690e"
_geocoder = OpenCageGeocode(OPEN_CAGE_KEY)

@app.route("/forward/<address>")
def forward(address):
    verbose = json.loads(request.args.get('verbose', "false").lower())
    raw_result = _geocoder.geocode(address)
    return json.dumps(raw_result if verbose else [{"confidence": r["confidence"], "geometry": r["geometry"]} for r in raw_result if r["confidence"]])

@app.route("/reverse/<lat>/<lng>/")
def reverse(lat, lng):
    verbose = json.loads(request.args.get('verbose', "false").lower())
    raw_result = _geocoder.reverse_geocode(float(lat), float(lng))
    return json.dumps(raw_result if verbose else [r["components"] for r in raw_result])

if __name__ == "__main__":
    app.run(debug=True)
