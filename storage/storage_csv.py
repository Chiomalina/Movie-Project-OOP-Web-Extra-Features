# storage_csv.py
from __future__ import annotations

import csv
import os
from typing import Dict, Any, List, Optional

from istorage import IStorage


class StorageCsv(IStorage):
    """
    CSV-based storage for movies.

    CSV schema (always with header):
        title,rating,year,poster

    - title:  str (unique, case-insensitive)
    - rating: float | None  (stored as string; empty cell means None)
    - year:   str           (can be "1997", "2021–2025", "1997/II", etc.)
    - poster: str | None    (empty cell means None)

    All public methods satisfy IStorage.
    """

    FIELDNAMES = ["title", "rating", "year", "poster", "notes", "imdb_id"]

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self._ensure_file()

    # ------------- IStorage API -------------

    def list_movies(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns a dictionary-of-dictionaries keyed by title.
        Example:
            {
              "Titanic": {"rating": 9.2, "year": "1997", "poster": "..."},
              ...
            }
        """
        result: Dict[str, Dict[str, Any]] = {}
        for row in self._read_all():
            title = (row.get("title") or "").strip()
            if not title:
                continue
            result[title] = {
                "rating": self._to_float(row.get("rating")),
                "year": (row.get("year") or "").strip() or None,
                "poster": self._none_if_blank(row.get("poster")),
                "notes": self._none_if_blank(row.get("notes")),
                "imdb_id": self._none_if_blank(row.get("imdb_id")),
            }
        return result

    def add_movie(
            self,
            title: str,
            year: str,
            rating: float | None,
            poster: str | None,
            imdb_id: str | None = None,
    ) -> None:
        """
        Add a new movie; raise ValueError if movie title already exists (case-insensitive).
        """
        rows = self._read_all()
        if self._find_index_by_title(rows, title) is not None:
            raise ValueError(f'Movie "{title}" already exists.')

        rows.append({
            "title": title,
            # store empty string for None to keep CSV clean
            "rating": "" if rating is None else f"{float(rating)}",
            # keep year as-is (string) to support ranges/suffixes
            "year": "" if year is None else str(year),
            "poster": poster or "",
            "notes": "",
            "imdb_id": imdb_id or "",
        })
        self._write_all(rows)

    def delete_movie(self, title: str) -> None:
        """
        Delete a movie by title; raise KeyError if not found.
        """
        rows = self._read_all()
        idx = self._find_index_by_title(rows, title)
        if idx is None:
            raise KeyError(f'Movie "{title}" not found.')
        del rows[idx]
        self._write_all(rows)

    def update_movie(self, title: str, rating: float | None) -> None:
        """
        Update rating of a movie by title; raise KeyError if not found.
        """
        rows = self._read_all()
        idx = self._find_index_by_title(rows, title)
        if idx is None:
            raise KeyError(f'Movie "{title}" not found.')
        rows[idx]["rating"] = "" if rating is None else f"{float(rating)}"
        self._write_all(rows)

    def update_movie_notes(self, title: str, notes: Optional[str]) -> None:
        """
        Update notes given to a movie by user; raise KeyError if not found.
        """
        rows = self._read_all()
        idx = self._find_index_by_title(rows, title)
        if idx is None:
            raise KeyError(f'Movie "{title}" not found.')
        rows[idx]["notes"] = (notes or "").strip()
        self._write_all(rows)

    # ------------- Internals -------------

    def _ensure_file(self) -> None:
        """
        Make sure the CSV exists and has the correct header.
        If header is missing/incorrect, rewrite a header (rows preserved or next write).
        """
        needs_header = False
        if not os.path.exists(self.filepath):
            needs_header = True
        else:
            try:
                with open(self.filepath, "r", encoding="utf-8", newline="") as f:
                    sample = f.read(1024);
                    f.seek(0)
                    if not sample.strip():
                        needs_header = True
                    else:
                        reader = csv.DictReader(f)
                        if reader.fieldnames is None or any(
                                fn not in (reader.fieldnames or []) for fn in self.FIELDNAMES
                        ):
                            needs_header = True
            except Exception:
                needs_header = True

        if needs_header:
            with open(self.filepath, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(
                    f, fieldnames=self.FIELDNAMES, extrasaction="ignore"
                )
                writer.writeheader()

    def _read_all(self) -> List[Dict[str, str]]:
        with open(self.filepath, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = [dict(row) for row in reader]

            # Backfill for older files that had no notes column
            for row in rows:
                row.setdefault("notes", "")
                row.setdefault("imdb_id", "")
            return rows

    def _write_all(self, rows: List[Dict[str, str]]) -> None:
        with open(self.filepath, "w", encoding="utf-8", newline="") as f:
            # extraAction="ignore" avoids crashing if any row has stray keys
            writer = csv.DictWriter(
                f, fieldnames=self.FIELDNAMES, extrasaction="ignore"
            )
            writer.writeheader()
            for row in rows:
                row.setdefault("title", "")
                row.setdefault("rating", "")
                row.setdefault("year", "")
                row.setdefault("poster", "")
                row.setdefault("notes", "")
                row.setdefault("imdb_id", "")
                writer.writerow(row)

    @staticmethod
    def _find_index_by_title(rows: List[Dict[str, str]], title: str) -> Optional[int]:
        target = title.casefold()
        for i, row in enumerate(rows):
            if (row.get("title") or "").casefold() == target:
                return i
        return None

    @staticmethod
    def _to_int(value: Optional[str]) -> Optional[int]:
        try:
            return int(value) if value not in (None, "") else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _none_if_blank(value: Optional[str]) -> Optional[str]:
        v = (value or "").strip()
        return v if v else None

    @staticmethod
    def _to_float(value: Optional[str]) -> Optional[float]:
        if value is None:
            return None
        s = str(value).strip()
        if not s or s.upper() == "N/A":
            return None
        try:
            return float(s)
        except ValueError:
            return None


