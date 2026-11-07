"""Fetch the current outdoor temperature (Open-Meteo, no API key) and append it
to data/<slug>/YYYY-MM.csv.

usage: capture_outdoor.py <slug> <latitude> <longitude>
e.g.   capture_outdoor.py austin-78705 30.298 -97.742
"""
import json
import sys
import urllib.parse
import urllib.request

from datalog import append_reading

URL = "https://api.open-meteo.com/v1/forecast"


def fetch_temp_f(lat, lon):
    query = urllib.parse.urlencode({
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m",
        "temperature_unit": "fahrenheit",
    })
    with urllib.request.urlopen(URL + "?" + query, timeout=20) as resp:
        return float(json.load(resp)["current"]["temperature_2m"])


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    append_reading(sys.argv[1], fetch_temp_f(sys.argv[2], sys.argv[3]))
