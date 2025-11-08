# /Users/linachiomaanaso/CODIO_PROJECTS/MOVIE Project/Movie Project-OOP + Web + Extra Features/src/omdb_client.py

from __future__ import annotations

import os
from typing import Dict, Optional

import requests
from dotenv import load_dotenv

# loads variables from .env if present
load_dotenv()

OMDB_BASE_URL = "http://www.omdbapi.com"

class OmdbError(Exception):
	"""Base error for OMDB client"""

class OmdbNotFound(OmdbError):
	"""Raised when a movie is not found."""

class OmdbAuthError(OmdbError):
	"""Raised when API key is missing/invalid."""

class OmdbRateLimit(OmdbError):
	"""Raised when OMDb rate limit is hit."""

class OmdbNetworkError(OmdbError):
	"""Raised for network/connection issues."""

def get_api_key() -> str:
	key = os.getenv("OMDB_API_KEY", "").strip()
	if not key:
		raise OmdbAuthError(
			"OMDB_API_KEY is not set. Export it or add to your .env file."
		)
	return key

def fetch_by_title(title: str, *, timeout: float = 8.0) -> Dict[str, str]:
	"""
    Fetch a single movie by exact title using the 't' parameter.
    Returns a dict with Title, Year, imdbRating, Poster, etc. (raw OMDb payload).

    Raises:
        OmdbNotFound, OmdbAuthError, OmdbRateLimit, OmdbNetworkError
    """
	params = {
		"apikey": get_api_key(),
		"t": title,
		"r": "json",
	}
	try:
		response = requests.get(OMDB_BASE_URL, params=params, timeout=timeout)
	except requests.exceptions.RequestException as e:
		raise OmdbNetworkError(f"Network error: {e}") from e

	# Some OMDb errors are returned as 200 with an "Error" field.
	if response.status_code == 401:
		raise OmdbAuthError("Invalid or missing API key (HTTP 401).")
	if response.status_code == 403:
		raise OmdbAuthError("Access forbidden (HTTP 403).")
	if response.status_code >= 500:
		raise OmdbNetworkError(f"OMDb server error (HTTP {response.status_code}).")

	try:
		data: Dict[str, str] = response.json()
	except ValueError as e:
		raise OmdbNetworkError("Invalid JSON response from OMBD.") from e

	# OMDb signals problems in JSON:
	# {"Response":"False","Error":"Movie not found!"}
	if str(data.get("Response")).lower() == "false":
		err_msg = (data.get("Error") or "").lower()
		if "limit" in err_msg:
			raise OmdbRateLimit("OMDb free tier rate limit reached.")
		if "apikey" in err_msg or "api key" in err_msg:
			raise OmdbAuthError(data.get("Error", "Authentication error."))
		if "not found" in err_msg:
			raise OmdbNotFound("Movie not found.")
		# Generic fallback:
		raise OmdbError(data.get("Error", "Unknown OMDb error."))

	return data


def extract_core_fields(payload: Dict[str, str]) -> Dict[str, Optional[str]]:
	"""
	Normalize the raw OMDb payload to the 4 fields my app needs.
    - Title (str)
    - Year (str)
    - Rating (str or None) — we use 'imdbRating'
    - Poster (str or None)
	"""
	title = payload.get("Title")
	year = payload.get("Year")
	rating = payload.get("imdbRating")
	poster = payload.get("Poster")

	# Prevent OMDB from crashing incase it  returns "N/A"
	rating = None if not rating or rating == "N/A" else rating
	poster = None if not poster or poster == "N/A" else poster

	return {
		"Title": title,
		"Year": year,
		"Rating": rating,
		"Poster": poster,
	}



