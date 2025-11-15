"""
Normalize_title / substring_matches / fuzzy_matches
"""

import unicodedata
from http.client import responses
from typing import Iterable, List, Tuple, Optional
from rapidfuzz import fuzz
from src.data.country_map import COUNTRY_NAME_TO_CODE

import requests

FUZZY_THRESHOLD = 60

# Extra manual aliases for non-standard or shortened names that OMDb might use
COUNTRY_NAME_ALIASES = {
    "usa": "US",
    "u.s.a.": "US",
    "united states": "US",
    "uk": "GB",
    "u.k.": "GB",
    "england": "GB",
    "scotland": "GB",
    "wales": "GB",
    "russia": "RU",
    "south korea": "KR",
    "north korea": "KP",
}

def normalize_country_name(raw_country: Optional[str]) -> str:
    """
    Takes the raw 'Country' string from OMDb (e.g. 'USA, UK')
    and returns a single 'main' country name (e.g. 'USA').

    Strategy:
      - If the string contains commas, assume the first part
        is the primary production country.
      - Strip whitespace.
    """
    if not raw_country:
        return ""

    first = raw_country.split(",")[0].strip()
    return first

def country_name_to_iso2(raw_country: Optional[str]) -> Optional[str]:
    """
    Convert a country name from OMDb into a 2-letter ISO code.

    Steps:
      1. Normalize (take first country if comma-separated).
      2. Lowercase and look up in our generated COUNTRY_NAME_TO_CODE.
      3. Fall back to alias mapping for abbreviations like 'USA', 'UK'.

    Returns:
      - 'US' for 'USA' / 'United States' / 'United States of America'
      - 'GB' for 'UK' / 'England' etc.
      - None if no match found.
    """
    if not raw_country:
        return None

    main_name = normalize_country_name(raw_country)
    normalized = main_name.strip().lower()

    # 1) Try exact match from FIRST.org data
    iso_from_main = COUNTRY_NAME_TO_CODE.get(normalized)
    if iso_from_main:
        return iso_from_main

    # 2) Try alias mapping (for abbreviations or alternative names)
    iso_from_alias = COUNTRY_NAME_ALIASES.get(normalized)
    if iso_from_alias:
        return iso_from_alias

    # 3) Nothing found?
    return None

def country_to_flag_image_url(raw_country: Optional[str], size: str = "40x30") -> str:
    """
    High-level helper:
      'USA, UK'   → 'https://flagcdn.com/40x30/us.png'
      'Nigeria'   → 'https://flagcdn.com/40x30/ng.png'
      None/unknown → '' (empty string, meaning: no flag)

    Uses FlagCDN-style URLs:
      https://flagcdn.com/{width}x{height}/{iso2_lowercase}.png
    """
    iso2 = country_name_to_iso2(raw_country)
    if not iso2:
        return ""

    iso2_lower = iso2.lower()
    return f"https://flagcdn.com/{size}/{iso2_lower}.png"


def normalize_title(text: str) -> str:
    """
    Normalize a movie title for robust, case/spacing-insensitive comparison.

    Steps:
        1) Unicode normalize to NFKD (compatibility decomposition).
        2) Case-fold (stronger than lowercasing; handles ß, Turkish dotted i, etc.).
        3) Collapse any internal whitespace to single spaces and strip ends.

    Args:
        text: Raw title text as entered/stored.

    Returns:
        A normalized string suitable for equality and containment checks.
    """
    text = unicodedata.normalize("NFKD", text)
    text = text.casefold()
    return " ".join(text.split())


def substring_matches(all_titles: Iterable[str], query: str) -> List[str]:
    """
    Find titles that contain the query as a substring (case/space-insensitive).

    The comparison is performed on normalized strings (see `normalize_title`),
    but the returned results preserve the original, unnormalized titles.

    Args:
        all_titles: An iterable of available movie titles.
        query: The user-provided search text.

    Returns:
        A list of titles from `all_titles` whose normalized form contains the
        normalized query. Order matches the input iteration order.
    """
    norm_query = normalize_title(query)
    return [t for t in all_titles if norm_query in normalize_title(t)]


def fuzzy_matches(
    all_titles: Iterable[str],
    query: str,
    threshold: int = FUZZY_THRESHOLD,
) -> List[Tuple[str, int]]:
    """
    Rank titles by fuzzy similarity to the query and return those above a threshold.

    Uses RapidFuzz's `WRatio` scorer (hybrid token/ratio heuristic) to compute a
    similarity score in [0, 100] between the raw `query` and each title.

    Args:
        all_titles: An iterable of movie titles to score.
        query: The user-provided search text (un-normalized; WRatio handles this).
        threshold: Minimum score a title must reach to be included (default 60).

    Returns:
        A list of (title, score) tuples filtered to scores >= `threshold`,
        sorted by:
            1) score descending, then
            2) title ascending (as a deterministic tie-breaker).
    """
    scored = [(t, fuzz.WRatio(query, t)) for t in all_titles]
    scored = [(t, s) for t, s in scored if s >= threshold]
    scored.sort(key=lambda t: (-t[1], t[0]))
    return scored
