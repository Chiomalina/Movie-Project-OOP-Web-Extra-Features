"""
movie_storage.py
Storage operations for the Movies app.

This module is responsible ONLY for persistence: reading and writing the movies JSON file.
It does not interact with users or any User Interface
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, TypedDict
from json import JSONDecodeError

# --------- Types ---------

class MovieRecord(TypedDict):
    """Single movie record."""
    rating: float
    year: int

MovieDatabase = Dict[str, MovieRecord]

# --------- Configuration ---------

# Path to the JSON file for persistent storage
DATA_FILE: Path = Path("data.json")

# --------- Internal helpers ---------

def _safe_load_json(path: Path) -> MovieDatabase:
    """
    Load JSON from 'path'. If the file is missing, empty, or invalid,
    return an empty dict instead of raising an error.
    """
    if not path.exists() or path.stat().st_size == 0:
        return {}

    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (JSONDecodeError, UnicodeDecodeError):
        # Where JSON is Corrupt/invalid, treat as empty for resilience
        return{}

    return data if isinstance(data, dict) else {}


def _atomic_write_json(path: Path, data: MovieDatabase) -> None:
    """
    Atomically write JSON by writing to a temp file and replacing the target.
    Prevents partial/corrupt files (a common cause of JSONDecodeError).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as tmp:
        json.dump(data, tmp, indent=4, ensure_ascii=False)
        tmp.flush()
        os.fsync(tmp.fileno())
        temp_name = tmp.name
    os.replace(temp_name, path)


# --------- Public API (required by the spec) ---------

def get_movies() -> MovieDatabase:
    """
    Return the full movie database as a dict:
        { "<title>": {"rating": float, "year": int}, ... }
    Assumes the file exists per the spec, but safely tolerates absence/corruption.
    """
    return _safe_load_json(DATA_FILE)

def save_movies(movies: MovieDatabase) -> None:
    """
    Persist the entire movie database to disk as JSON.
    """
    _atomic_write_json(DATA_FILE, movies)

def add_movie(title: str, year: int, rating: float) -> None:
    """
    Add (or overwrite) a movie and save.
    No input validation here—UI layer should validate.
    """
    movie_db = get_movies()
    movie_db[title] = {"year": int(year), "rating": float(rating)}
    save_movies(movie_db)

def delete_movie(title: str) -> None:
    """
    Delete a movie by title and save.
    Raises KeyError if the title does not exist (so callers can handle gracefully).
    """
    movie_db = get_movies()
    if title not in movie_db:
        raise KeyError(f"Movie '{title}' does not exist.")
    del movie_db[title]
    save_movies(movie_db)

def update_movie(title: str, rating: float) -> None:
    """
    Update a movie's rating and save.
    Raises KeyError if the title does not exist.
    """
    movie_db = get_movies()
    if title not in movie_db:
        raise KeyError(f"Movie '{title}' does not exist.")
    movie_db[title]["rating"] = float(rating)
    save_movies(movie_db)