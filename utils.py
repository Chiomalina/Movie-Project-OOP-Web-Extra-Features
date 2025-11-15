"""
Normalize_title / substring_matches / fuzzy_matches
"""

import unicodedata
from http.client import responses
from typing import Iterable, List, Tuple, Optional
from rapidfuzz import fuzz

import requests

FUZZY_THRESHOLD = 60

# Extract names of all countries in the world
#URL="https://restcountries.com/v3.1/all?fields=name,cca2,cca3,region"
URL="https://api.first.org/data/v1/countries"
response = requests.get(URL)
response.raise_for_status()
countries = response.json()

print(countries["data"])
for country in countries:
    #print(f'Country: {country["name"]["common"]}, Region: {country["region"]}')
    print(data)


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
