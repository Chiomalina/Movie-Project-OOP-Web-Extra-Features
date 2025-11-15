"""
movie_app.py
CLI application class (menu + commands)
"""
from __future__ import annotations

from migrations import migrate_csv_ensure_columns
from storage.storage_csv import StorageCsv


import random
from typing import Dict, Optional, Tuple

import matplotlib.pyplot as plt
from colorama import Fore, Style

from istorage import IStorage
from movies import select_title_from_user_query
from utils import normalize_title
from validators import (
    prompt_choice,
    prompt_rating,
    prompt_notes,
    prompt_title,
    prompt_year_filter,
    safe_float,
)

# If this file lives in src/, prefer absolute intra-package imports:
# from omdb_client import (...). Using relative imports is also fine if you make src a package.
from src.omdb_client import (
    OmdbAuthError,
    OmdbError,
    OmdbNetworkError,
    OmdbNotFound,
    OmdbRateLimit,
    extract_core_fields,
    fetch_by_title,
)


def _year_to_int(value) -> Optional[int]:
    """
    Convert various OMDb/CSV year strings to an int year when possible.

    Examples:
        "1997" -> 1997
        "2015–2019" -> 2015
        "1997/II" -> 1997
        None, "", invalid -> None
    """
    s = str(value or "").strip()
    return int(s[:4]) if len(s) >= 4 and s[:4].isdigit() else None


class MovieApp:
    """CLI application that manages movies using a pluggable storage backend."""

    MENU_TEXT = f"""
    {Fore.CYAN}=== Movie App ==={Style.RESET_ALL}
    0.  Exit
    1.  List movies
    2.  Add movie
    3.  Delete movie
    4.  Update movie notes
    5.  Stats
    6.  Random movie
    7.  Create rating histogram
    8.  Search by name
    9.  Generate website
    10. Sort by rating
    11. Sort by year
    12. Filter by rating/year
    13. Migrate CSV: add "notes" column
    """

    def __init__(self, storage: IStorage) -> None:
        """
        Args:
            storage: An implementation of IStorage (e.g., StorageJson or StorageCsv).
        """
        self._storage = storage

    # ----------------- Commands (private) -----------------
    def _command_list_movies(self) -> None:
        """Print all movies currently stored."""
        movies_dict = self._storage.list_movies()
        if not movies_dict:
            print("No movies in database.")
            return

        for title, record in movies_dict.items():
            print(f"{title} ({record.get('year', '?')}): {record.get('rating', '?')}")

    def _command_add_movie(self) -> None:
        """
        Add a movie by fetching real data from OMDb using only the title.
        Stores: Title, Year, Rating (IMDb), Poster URL.
        """
        title_input = prompt_title("Enter movie title: ")

        try:
            payload = fetch_by_title(title_input)
            core = extract_core_fields(payload)

            # Parse rating as float when possible
            rating_value = safe_float(core["Rating"]) if core["Rating"] is not None else None

            # defensively extract imdbID"
            imdb_id = core.get("imdb_id") or core.get("ImdbID") or core.get("imdbID")

            self._storage.add_movie(
                title=core["Title"],
                year=core["Year"],
                rating=rating_value,
                poster=core["Poster"],
                imdb_id=imdb_id,
            )

            print(
                f'{Fore.GREEN}Added: {core["Title"]} ({core["Year"]})'
                f' | Rating: {core["Rating"] or "N/A"}'
                f' | Poster: {core["Poster"] or "N/A"}{Style.RESET_ALL}'
            )

        except OmdbNotFound:
            print(f'{Fore.YELLOW}Movie not found on OMDb. Try a different title or exact name.{Style.RESET_ALL}')
        except OmdbRateLimit:
            print(f'{Fore.YELLOW}OMDb free-tier rate limit reached. Please wait and try again.{Style.RESET_ALL}')
        except OmdbAuthError as exc:
            print(f'{Fore.RED}{exc} Set OMDB_API_KEY and retry.{Style.RESET_ALL}')
        except OmdbNetworkError as exc:
            print(f'{Fore.RED}Network problem: {exc}. Check your internet connection and retry.{Style.RESET_ALL}')
        except OmdbError as exc:
            print(f'{Fore.RED}OMDb error: {exc}{Style.RESET_ALL}')
        except Exception as exc:  # safeguard
            print(f'{Fore.RED}Unexpected error: {exc}{Style.RESET_ALL}')

    def _command_delete_movie(self) -> None:
        """Delete a movie using a safe, user-confirmed flow."""
        movies_dict = self._storage.list_movies()
        if not movies_dict:
            print("No movies in database.")
            return

        user_input = prompt_title("Enter movie name to delete: ")
        resolved_title = select_title_from_user_query(movies_dict, user_input)
        if not resolved_title:
            return

        record = movies_dict[resolved_title]
        print(
            f"\nAbout to delete:\n"
            f"  • Title : {resolved_title}\n"
            f"  • Year  : {record.get('year', '?')}\n"
            f"  • Rating: {record.get('rating', '?')}\n"
        )

        typed = input("Type the exact title to confirm deletion (or press Enter to cancel): ").strip()
        if normalize_title(typed) != normalize_title(resolved_title):
            print("Deletion cancelled.")
            return

        self._storage.delete_movie(resolved_title)
        print(f"'{resolved_title}' successfully deleted.")

    def _command_update_movie(self) -> None:
        """Add/update a note for an existing movie (blank clears it)."""
        movies_dict = self._storage.list_movies()
        if not movies_dict:
            print("No movies in database.")
            return

        user_input = prompt_title("Enter movie name to update: ")
        resolved_title = select_title_from_user_query(movies_dict, user_input)
        if not resolved_title:
            return

        note_text = prompt_notes()
        try:
            self._storage.update_movie_notes(resolved_title, note_text or None)
            if note_text:
                print(f"Movie '{resolved_title}' successfully updated with note.")
            else:
                print(f"Note cleared for '{resolved_title}'.")
        except KeyError as exc:
            print(f"{Fore.RED}{exc}{Style.RESET_ALL}")

    def _command_stats(self) -> None:
        """
        Compute and display simple statistics for stored movies:
        average, median, best title, worst title (by rating).
        """
        movies_dict = self._storage.list_movies()
        numeric_ratings = [
            record.get("rating")
            for record in movies_dict.values()
            if isinstance(record.get("rating"), (int, float))
        ]
        if not numeric_ratings:
            print("No rated movies in database.")
            return

        average = sum(numeric_ratings) / len(numeric_ratings)
        sorted_ratings = sorted(numeric_ratings)
        median = sorted_ratings[len(sorted_ratings) // 2]

        def rating_or_default(title: str, default: float) -> float:
            value = movies_dict[title].get("rating")
            return value if isinstance(value, (int, float)) else default

        best_title = max(movies_dict, key=lambda t: rating_or_default(t, float("-inf")))
        worst_title = min(movies_dict, key=lambda t: rating_or_default(t, float("inf")))

        print(f"Average: {average:.1f}, Median: {median}, Best: {best_title}, Worst: {worst_title}")

    def _command_random_movie(self) -> None:
        """Pick and display a random movie from the database."""
        movies_dict = self._storage.list_movies()
        if not movies_dict:
            print("No movies in database.")
            return
        chosen_title = random.choice(list(movies_dict.keys()))
        record = movies_dict[chosen_title]
        year_text = record.get("year", "Unknown")
        rating_text = record.get("rating", "N/A")
        print(f"Your random movie for tonight is: {chosen_title} ({year_text}): {rating_text}")

    def _command_create_rating_histogram(self) -> None:
        """Create and save a histogram of all numeric movie ratings."""
        movies_dict = self._storage.list_movies()
        numeric_ratings = [
            record.get("rating")
            for record in movies_dict.values()
            if isinstance(record.get("rating"), (int, float))
        ]
        if not numeric_ratings:
            print("No movies in database.")
            return

        filename = input("Enter filename for histogram (ratings.png): ").strip() or "ratings.png"
        plt.hist(numeric_ratings, bins=20, edgecolor="black")
        plt.title("Movie Ratings Histogram")
        plt.xlabel("Rating")
        plt.ylabel("Frequency")
        plt.savefig(filename)
        print(f"Histogram saved to {filename}")

    # ----------------- Search & Selection -----------------
    def _command_search_movies(self) -> None:
        """Search for a movie by (part of) its name and print the best match."""
        movies_dict = self._storage.list_movies()
        if not movies_dict:
            print("No movies in database.")
            return
        term = prompt_title("Enter part of movie name to search: ")
        resolved = select_title_from_user_query(movies_dict, term)
        if resolved:
            record = movies_dict[resolved]
            print(f"{resolved} ({record.get('year', '?')}): {record.get('rating', '?')}")

    def _command_generate_website(self) -> None:
        """Generate static website into static/index.html."""
        try:
            from website import generate_website_from_storage

            generate_website_from_storage(
                storage=self._storage,
                template_path="static/index_template.html",
                output_path="static/index.html",
                title="🍿LinaFlix",
            )
            print("Website was generated successfully.")
        except Exception as exc:
            print(f"{Fore.RED}Failed to generate website: {exc}{Style.RESET_ALL}")

    def _command_sort_movies_by_rating(self) -> None:
        """Display movies sorted by rating (highest first)."""
        movies_dict = self._storage.list_movies()
        if not movies_dict:
            print("No movies in database.")
            return

        def key_fn(item: Tuple[str, Dict]) -> float:
            rating = item[1].get("rating")
            return rating if isinstance(rating, (int, float)) else float("-inf")

        for title, record in sorted(movies_dict.items(), key=key_fn, reverse=True):
            print(f"{title} ({record.get('year', '?')}): {record.get('rating', '?')}")

    def _command_sort_movies_by_year(self) -> None:
        """Display movies sorted by release year."""
        movies_dict = self._storage.list_movies()
        if not movies_dict:
            print("No movies in database.")
            return

        latest_first = input("Show latest movies first? (y/n): ").strip().lower() == "y"

        def key_fn(item: Tuple[str, Dict]) -> Tuple[bool, int]:
            year_int = _year_to_int(item[1].get("year"))
            # Sort None years to the end: (True/False, year)
            return (year_int is None, year_int or 0)

        for title, record in sorted(movies_dict.items(), key=key_fn, reverse=latest_first):
            print(f"{title} ({record.get('year', '?')}): {record.get('rating', '?')}")

    def _command_filter_movies(self) -> None:
        """Filter movies by minimum rating and/or a year range, then display matches."""
        movies_dict = self._storage.list_movies()
        if not movies_dict:
            print("No movies in database.")
            return

        raw = input("Enter minimum rating (blank=none): ").strip()
        min_rating = safe_float(raw) if raw else None
        start_year = prompt_year_filter("Enter start year")
        end_year = prompt_year_filter("Enter end year")

        filtered: list[tuple[str, str | int | None, float | None]] = []
        for title, record in movies_dict.items():
            year_int = _year_to_int(record.get("year"))
            rating_val = record.get("rating")

            if min_rating is not None and (not isinstance(rating_val, (int, float)) or rating_val < min_rating):
                continue
            if start_year is not None and (year_int is None or year_int < start_year):
                continue
            if end_year is not None and (year_int is None or year_int > end_year):
                continue

            filtered.append((title, record.get("year"), rating_val))

        if not filtered:
            print("No movies match criteria.")
            return

        for title, year_text, rating_text in filtered:
            print(f"{title} ({year_text if year_text is not None else '?'}): {rating_text if rating_text is not None else '?'}")

    def _command_migrate_csv_ensure_columns(self) -> None:
        if not isinstance(self._storage, StorageCsv):
            print(f"{Fore.YELLOW}Current backend is not CSV; nothing to migrate.{Style.RESET_ALL}")
            return
        csv_path = getattr(self._storage, "filepath", None)
        if not csv_path:
            print(f"{Fore.RED}Could not determine CSV path from storage.{Style.RESET_ALL}")
            return
        try:
            changed = migrate_csv_ensure_columns(csv_path, ["notes", "imdb_id"])
            if changed:
                print(f"{Fore.GREEN}Migrated: ensured columns 'notes' and 'imdb_id' in {csv_path}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}No change: columns already present in {csv_path}{Style.RESET_ALL}")
        except Exception as exc:
            print(f"{Fore.RED}Migration failed: {exc}{Style.RESET_ALL}")

    # -------- Main loop --------
    def run(self) -> None:
        """Menu loop: prints options, gets a command, executes until user exits."""
        actions = {
            1: self._command_list_movies,
            2: self._command_add_movie,
            3: self._command_delete_movie,
            4: self._command_update_movie,
            5: self._command_stats,
            6: self._command_random_movie,
            7: self._command_create_rating_histogram,
            8: self._command_search_movies,
            9: self._command_generate_website,
            10: self._command_sort_movies_by_rating,
            11: self._command_sort_movies_by_year,
            12: self._command_filter_movies,
            13: self._command_migrate_csv_ensure_columns,
        }

        while True:
            print(self.MENU_TEXT)
            choice = prompt_choice(max_choice=13)
            if choice == 0:
                print("Goodbye!")
                return
            action = actions.get(choice)
            if action:
                action()
            else:
                print(f"Unknown choice: {choice}")
