"""
Fetches country data from FIRST.org Countries API  and generates
a Python module with country mappings for use in the Movie App.

Output: src/data/country_map.py (auto-generated)
"""

import json
import os
from pathlib import Path

import requests

API_URL = "https://api.first.org/data/v1/countries"

# Where to write the generated module
OUTPUT_PATH = Path("src/data/country_map.py")


def fetch_countries() -> dict:
	"""
	Fetch country data from FIRST.org API.
    Returns the 'data' dict where keys are ISO codes like 'DE', 'NG'.
	"""
	print(f"Fetching countries from {API_URL}...")
	response = requests.get(API_URL, timeout=10)
	response.raise_for_status()

	payload = response.json()
	data = payload.get("data", {})
	if not data:
		raise RuntimeError("No 'data' fields in First.org response")

	print(f"Received {len(data)} countries")
	return data

def build_mappings(data: dict ) -> tuple[dict, dict]:
	"""
	Build two mappings:
      - code_to_name: 'DE' -> 'Germany'
      - name_to_code: 'germany' -> 'DE'
	"""

	code_to_name: dict[str, str] = {}
	name_to_code: dict[str, str] = {}

	for iso_code, info in data.items():
		country_name = info.get("country")

data = fetch_countries()
build_mappings(data)