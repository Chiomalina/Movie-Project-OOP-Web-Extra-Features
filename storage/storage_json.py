"""JSON implementation of IStorage"""

import json
from pathlib import Path
from typing import Dict, Any
from istorage import IStorage

class StorageJson(IStorage):
    """
    JSON-based storage implementation.

    File structure:
    {
      "Movie Title": {"year": "1997", "rating": 8.5, "poster": null}
    }
    """

    def __init__(self, file_path: str | Path) -> None:
        self._path = Path(file_path)
        if not self._path.exists():
            self._write({})
        else:
            try:
                data = self._read()
                if not isinstance(data, dict):
                    # Reset if root isn't a dict
                    self._write({})
            except json.JSONDecodeError:
                self._write({})

    # --------- helpers ---------
    def _read(self) -> Dict[str, Dict[str, Any]]:
        with self._path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            # Use ValueError here: JSONDecodeError is meant for parsing failures
            raise ValueError("Root of storage JSON must be a dict")
        # Migration guard: ensure each record has the poster key
        for rec in data.values():
            if "poster" not in rec:
                rec["poster"] = None
        return data

    def _write(self, data: Dict[str, Dict[str, Any]]) -> None:
        with self._path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # --------- IStorage API ---------
    def list_movies(self) -> Dict[str, Dict[str, Any]]:
        return self._read()

    def add_movie(self, title: str, year: str | int, rating: float | None, poster: str | None) -> None:
        """
        Persist a movie record exactly as provided by the caller.
        """
        data = self._read()
        data[title] = {"year": str(year) if year is None else None, "rating": rating, "poster": poster}
        self._write(data)

    def delete_movie(self, title: str) -> None:
        """
        Remove a movie by exact title key, if present.
        """
        data = self._read()
        if title in data:
            del data[title]
            self._write(data)

    def update_movie(self, title: str, rating: float | None) -> None:
        """
        Update only the rating of an existing movie, if present.
        """
        data = self._read()
        if title in data:
            data[title]["rating"] = rating
            self._write(data)
