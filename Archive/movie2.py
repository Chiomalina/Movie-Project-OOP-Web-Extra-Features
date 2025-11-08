"""
movies.py

Interactive CLI for a JSON-backed Movies database.
Relies on movie_storage.py for all persistence.

Enhancements vs. the original:
- Case-insensitive (non-sensitive) title handling for search, update, and delete.
- Search prints ALL matches (substring matches first; fuzzy matches as fallback).
- Disambiguation menu when multiple titles match.
"""

from __future__ import annotations

import random
import unicodedata
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
from colorama import Fore, init
from rapidfuzz import fuzz
import math

from Archive import movie_storage

# Initialize colorama for colored terminal output
init(autoreset=True)

# --------- Constants ---------

FUZZY_THRESHOLD = 60  # Minimum score to include fuzzy matches (0..100)


# --------- Title normalization & matching helpers ---------


def _normalize_title(text: str) -> str:
    """
    Normalize a title for comparison in a case-insensitive, whitespace-insensitive way.
    - Unicode normalize (NFKD)
    - casefold() (more robust than lower())
    - collapse internal whitespace to single spaces
    """
    normalized = unicodedata.normalize("NFKD", text)
    normalized = normalized.casefold()
    normalized = " ".join(normalized.split())
    return normalized


def _substring_matches(
    all_titles: Iterable[str], query: str
) -> List[str]:
    """
    Return titles whose normalized form contains the normalized query as a substring.
    """
    norm_query = _normalize_title(query)
    results = []
    for title in all_titles:
        if norm_query in _normalize_title(title):
            results.append(title)
    return results


def _fuzzy_matches(
    all_titles: Iterable[str], query: str, threshold: int = FUZZY_THRESHOLD
) -> List[Tuple[str, int]]:
    """
    Return (title, score) pairs for ALL titles whose fuzzy score >= threshold.
    Uses WRatio for robust scoring; sorts by descending score, then by title.
    """
    scored: List[Tuple[str, int]] = []
    for title in all_titles:
        score = fuzz.WRatio(query, title)
        if score >= threshold:
            scored.append((title, score))
    scored.sort(key=lambda t: (-t[1], t[0]))
    return scored


def _print_title_list(
    movies: Dict[str, Dict[str, float]], titles: Sequence[str], header: str
) -> None:
    """Pretty-print a list of titles with year and rating, numbered 1..N."""
    print(Fore.CYAN + f"\n{header}")
    for idx, title in enumerate(titles, start=1):
        rec = movies[title]
        print(
            Fore.GREEN + f"{idx}. {title} ({rec['year']}) — {rec['rating']}"
        )


def _disambiguate_choice(
    movies: Dict[str, Dict[str, float]], candidates: Sequence[str]
) -> Optional[str]:
    """
    If multiple candidates exist, ask the user to pick one by number.
    Returns the chosen title or None if user cancels.
    """
    _print_title_list(movies, candidates, "Multiple matches found:")
    choice_idx = prompt_index(len(candidates))
    if choice_idx is None:
        print(Fore.YELLOW + "Cancelled.")
        return None
    return candidates[choice_idx]


def _select_title_from_user_query(
    movies: Dict[str, Dict[str, float]], user_input: str
) -> Optional[str]:
    """
    Resolve a user-typed title to a concrete title key in the movies dict.

    Strategy:
      1) Exact case-insensitive match (single hit preferred).
      2) ALL case-insensitive substring matches → disambiguate if needed.
      3) ALL fuzzy matches over threshold → disambiguate if needed.

    Returns:
      - A single title to operate on, or
      - None if nothing acceptable was selected/found.
    """
    titles = list(movies.keys())

    # 1) Exact case-insensitive equality
    norm_input = _normalize_title(user_input)
    exact = [t for t in titles if _normalize_title(t) == norm_input]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        return _disambiguate_choice(movies, exact)

    # 2) Case-insensitive substring matches (show ALL)
    subs = _substring_matches(titles, user_input)
    if len(subs) == 1:
        return subs[0]
    if len(subs) > 1:
        return _disambiguate_choice(movies, subs)

    # 3) Fuzzy fallback (show ALL above threshold)
    fuzzy = _fuzzy_matches(titles, user_input, FUZZY_THRESHOLD)
    if not fuzzy:
        print(Fore.RED + "No matching titles found.")
        return None

    # Show fuzzy matches with scores, then disambiguate
    print(Fore.CYAN + "\nNo substring matches. Fuzzy matches:")
    for idx, (title, score) in enumerate(fuzzy, start=1):
        rec = movies[title]
        print(
            Fore.GREEN
            + f"{idx}. {title} ({rec['year']}) — {rec['rating']}  [score: {score}]"
        )
    idx_choice = prompt_index(len(fuzzy))
    if idx_choice is None:
        print(Fore.YELLOW + "Cancelled.")
        return None
    return fuzzy[idx_choice][0]


def _safe_float(s: str) -> Optional[float]:
    # accept decimal comma
    s = s.replace(",", ".")
    try:
        x = float(s)
        return x if math.isfinite(x) else None
    except ValueError:
        return None


def safe_float(s: str) -> Optional[float]:
    s = s.replace(",", ".")
    try:
        x = float(s)
        return x if math.isfinite(x) else None
    except ValueError:
        return None

def prompt_rating() -> float:
    while True:
        raw = input(Fore.MAGENTA + "Enter rating (0.0–10.0): ").strip()
        val = safe_float(raw)
        if val is not None and 0.0 <= val <= 10.0:
            return val
        print(Fore.RED + "⚠️ Rating must be a finite number between 0.0 and 10.0.")

def prompt_title(prompt_msg: str) -> str:
    while True:
        text = input(Fore.MAGENTA + prompt_msg).strip()
        if text:
            return text
        print(Fore.RED + "⚠️ Title cannot be empty.")


def prompt_title(prompt_msg: str) -> str:
    """Prompt until the user provides a non-empty movie title."""
    while True:
        text = input(Fore.MAGENTA + prompt_msg).strip()
        if text:
            return text
        print(Fore.RED + "⚠️ Title cannot be empty.")


def prompt_rating() -> float:
    """Prompt until a valid float between 0.0 and 10.0 is entered."""
    while True:
        raw = input(Fore.MAGENTA + "Enter rating (0.0–10.0): ").strip()
        val = _safe_float(raw)
        if val is not None and 0.0 <= val <= 10.0:
            return val
        print(Fore.RED + "⚠️ Rating must be a finite number between 0.0 and 10.0.")


def prompt_year() -> int:
    """Prompt until a valid four-digit year is entered."""
    while True:
        raw = input(Fore.MAGENTA + "Enter release year (YYYY): ").strip()
        if raw.isdigit() and len(raw) == 4:
            return int(raw)
        print(Fore.RED + "⚠️ Year must be a four-digit number.")


def prompt_choice() -> int:
    """Prompt until the user selects a valid menu choice (0–11)."""
    while True:
        raw = input(Fore.MAGENTA + "Enter choice (0–11): ").strip()
        try:
            choice_val = int(raw)
            if 0 <= choice_val <= 11:
                return choice_val
            print(Fore.RED + "⚠️ Choice must be between 0 and 11.")
        except ValueError:
            print(Fore.RED + "⚠️ Invalid input; please enter a number.")


def prompt_index(max_index: int) -> Optional[int]:
    """
    Ask the user to select an index from 1..max_index.
    Returns a 0-based index or None if user cancels (blank).
    """
    while True:
        raw = input(
            Fore.MAGENTA
            + "Enter number to choose (leave blank to cancel): "
        ).strip()
        if raw == "":
            return None
        if raw.isdigit():
            num = int(raw)
            if 1 <= num <= max_index:
                return num - 1
        print(Fore.RED + f"⚠️ Please enter a number between 1 and {max_index}.")




# --------- UI helpers ---------

def print_header() -> None:
    """Display the program header."""
    print(Fore.CYAN + " My Movies Database ".center(40, "*"))


def display_menu() -> None:
    """Show available menu options."""
    print(Fore.YELLOW + "\nMenu:")
    print(Fore.YELLOW + "0. Exit")
    print(Fore.YELLOW + "1. List movies")
    print(Fore.YELLOW + "2. Add movie")
    print(Fore.YELLOW + "3. Delete movie")
    print(Fore.YELLOW + "4. Update movie")
    print(Fore.YELLOW + "5. Stats")
    print(Fore.YELLOW + "6. Random movie")
    print(Fore.YELLOW + "7. Search movies")
    print(Fore.YELLOW + "8. Movies sorted by rating")
    print(Fore.YELLOW + "9. Create Rating Histogram")
    print(Fore.YELLOW + "10. Movies sorted by year")
    print(Fore.YELLOW + "11. Filter movies\n")



# --------- Features ---------


def list_movies() -> None:
    """List all movies with their year and rating."""
    movies = movie_storage.get_movies()
    print(Fore.CYAN + f"\n{len(movies)} movies in total")
    for movie_title, record in movies.items():
        print(Fore.GREEN + f"{movie_title} ({record['year']}): {record['rating']}")
    input(Fore.MAGENTA + "\nPress enter to continue")


def add_movie() -> None:
    """Add a new movie; ensures non-empty title, valid rating and year."""
    title_str = prompt_title("Enter new movie name: ")
    rating_val = prompt_rating()
    year_val = prompt_year()
    movie_storage.add_movie(title_str, year_val, rating_val)
    print(Fore.GREEN + f"{title_str} ({year_val}) added with rating {rating_val}!")
    input(Fore.MAGENTA + "\nPress enter to continue")

def confirm_delete_exact_title(expected_title: str, record: dict) -> bool:
    """
    Ask the user to confirm deletion by typing the exact movie title.

    This is safer than a yes/no prompt: it prevents accidental deletions
    caused by auto-resolved matches (substring/fuzzy) by requiring the user
    to consciously re-type the exact title.

    Returns:
        True if the user typed the exact title (case-insensitive, normalized),
        False otherwise.
    """
    print(
        Fore.YELLOW
        + f"\nAbout to delete:\n"
          f"  • Title : {expected_title}\n"
          f"  • Year  : {record.get('year', '?')}\n"
          f"  • Rating: {record.get('rating', '?')}\n"
    )
    prompt = (
        "Type the exact title to confirm deletion, or press Enter to cancel:\n> "
    )
    typed = input(Fore.RED + prompt).strip()
    if _normalize_title(typed) == _normalize_title(expected_title):
        return True

    print(Fore.GREEN + "Deletion cancelled.")
    return False


def delete_movie() -> None:
    """
    Delete a movie using non-sensitive matching, with strong confirmation.

    Flow:
      1) Resolve the user's input to a specific title (exact/substr/fuzzy).
      2) Show the movie details and require typing the exact title to confirm.
      3) If confirmed, perform deletion; otherwise, cancel safely.
    """
    movies = movie_storage.get_movies()
    if not movies:
        print(Fore.RED + "No movies in the database.")
        input(Fore.MAGENTA + "\nPress enter to continue")
        return

    user_input = prompt_title("Enter movie name to delete: ")
    resolved_title = _select_title_from_user_query(movies, user_input)
    if not resolved_title:
        input(Fore.MAGENTA + "\nPress enter to continue")
        return

    record = movies[resolved_title]
    if not confirm_delete_exact_title(resolved_title, record):
        # User changed their mind or mistyped
        input(Fore.MAGENTA + "\nPress enter to continue")
        return

    try:
        movie_storage.delete_movie(resolved_title)
        print(Fore.GREEN + f"'{resolved_title}' successfully deleted.")
    except KeyError:
        # Should be rare now, but handle just in case
        print(Fore.RED + f"Movie '{resolved_title}' not found.")
    input(Fore.MAGENTA + "\nPress enter to continue")


def update_movie() -> None:
    """
    Update a movie's rating using non-sensitive title matching.
    - Exact (case-insensitive) match preferred.
    - Otherwise disambiguate among all substring or fuzzy matches.
    """
    movies = movie_storage.get_movies()
    if not movies:
        print(Fore.RED + "No movies in the database.")
        input(Fore.MAGENTA + "\nPress enter to continue")
        return

    user_input = prompt_title("Enter movie name to update: ")
    resolved_title = _select_title_from_user_query(movies, user_input)
    if not resolved_title:
        input(Fore.MAGENTA + "\nPress enter to continue")
        return

    rating_val = prompt_rating()
    try:
        movie_storage.update_movie(resolved_title, rating_val)
        print(Fore.GREEN + f"'{resolved_title}' rating updated to {rating_val}.")
    except KeyError:
        print(Fore.RED + f"Movie '{resolved_title}' not found.")
    input(Fore.MAGENTA + "\nPress enter to continue")


def _median(values: List[float]) -> float:
    """
    Return the median of a non-empty list of floats (handles even/odd length).
    """
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    mid = n // 2
    if n % 2 == 1:
        return float(sorted_vals[mid])
    return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0


def stats() -> None:
    """Display average, median, best and worst movie statistics."""
    movies = movie_storage.get_movies()
    ratings = [record["rating"] for record in movies.values()]
    if not ratings:
        print(Fore.RED + "No movies in the database.")
    else:
        average_rating = sum(ratings) / len(ratings)
        median_rating = _median(ratings)
        best_title = max(movies, key=lambda t: movies[t]["rating"])
        worst_title = min(movies, key=lambda t: movies[t]["rating"])
        print(Fore.CYAN + f"\nAverage Rating: {average_rating:.1f}")
        print(Fore.CYAN + f"Median Rating : {median_rating:.1f}")
        print(
            Fore.GREEN
            + f"Best Movie    : {best_title} ({movies[best_title]['year']}) — {movies[best_title]['rating']}"
        )
        print(
            Fore.RED
            + f"Worst Movie   : {worst_title} ({movies[worst_title]['year']}) — {movies[worst_title]['rating']}"
        )
    input(Fore.MAGENTA + "\nPress enter to continue")


def random_movie() -> None:
    """Pick and display a random movie."""
    movies = movie_storage.get_movies()
    if not movies:
        print(Fore.RED + "No movies in the database.")
    else:
        chosen_title = random.choice(list(movies.keys()))
        record = movies[chosen_title]
        print(
            Fore.GREEN
            + f"Your movie for tonight: {chosen_title} ({record['year']}) — {record['rating']}"
        )
    input(Fore.MAGENTA + "\nPress enter to continue")


def search_movie() -> None:
    """
    Search for movies non-sensitively and print ALL matches.

    Order of attempts:
      1) ALL case-insensitive substring matches (primary result).
      2) If none, ALL fuzzy matches with score >= FUZZY_THRESHOLD.
    """
    term = prompt_title("Enter part of movie name to search: ")
    movies = movie_storage.get_movies()

    if not movies:
        print(Fore.RED + "No movies in the database.")
        input(Fore.MAGENTA + "\nPress enter to continue")
        return

    titles = list(movies.keys())

    # 1) Case-insensitive substring matches (ALL)
    subs = _substring_matches(titles, term)
    if subs:
        _print_title_list(movies, subs, "Substring matches:")
        input(Fore.MAGENTA + "\nPress enter to continue")
        return

    # 2) Fuzzy fallback (ALL with score >= threshold)
    fuzzy = _fuzzy_matches(titles, term, FUZZY_THRESHOLD)
    if fuzzy:
        print(Fore.CYAN + "\nNo substring matches. Fuzzy matches:")
        for idx, (title, score) in enumerate(fuzzy, start=1):
            rec = movies[title]
            print(
                Fore.GREEN
                + f"{idx}. {title} ({rec['year']}) — {rec['rating']}  [score: {score}]"
            )
    else:
        print(Fore.RED + "No similar movies found.")
    input(Fore.MAGENTA + "\nPress enter to continue")


def sort_movies_by_rating() -> None:
    """Show movies sorted by descending rating."""
    movies = movie_storage.get_movies()
    sorted_items = sorted(
        movies.items(), key=lambda kv: kv[1]["rating"], reverse=True
    )
    print(Fore.CYAN + "\nMovies sorted by rating:")
    for movie_title, record in sorted_items:
        print(Fore.GREEN + f"{movie_title} ({record['year']}) — {record['rating']}")
    input(Fore.MAGENTA + "\nPress enter to continue")


def sort_movies_by_year() -> None:
    """Show movies sorted by release year, asking latest-first or oldest-first."""
    movies = movie_storage.get_movies()
    while True:
        answer = input(
            Fore.MAGENTA + "Show latest movies first? (y/n): "
        ).strip().lower()
        if answer in ("y", "n"):
            break
        print(Fore.RED + "⚠️ Please enter 'y' or 'n'.")
    reverse = answer == "y"
    order_desc = "latest first" if reverse else "oldest first"

    sorted_items = sorted(
        movies.items(), key=lambda kv: kv[1]["year"], reverse=reverse
    )
    print(Fore.CYAN + f"\nMovies sorted by year ({order_desc}):")
    for movie_title, record in sorted_items:
        print(Fore.GREEN + f"{movie_title} ({record['year']}) — {record['rating']}")
    input(Fore.MAGENTA + "\nPress enter to continue")


def filter_movies() -> None:
    """Filter movies by minimum rating, start year and end year."""
    movies = movie_storage.get_movies()

    # Minimum rating
    while True:
        raw = input(
            Fore.MAGENTA + "Enter minimum rating (leave blank for no minimum rating): "
        ).strip()
        if not raw:
            min_rating = None
            break
        try:
            val = float(raw)
            if 0.0 <= val <= 10.0:
                min_rating = val
                break
            print(Fore.RED + "⚠️ Rating must be between 0.0 and 10.0.")
        except ValueError:
            print(Fore.RED + "⚠️ Invalid rating format.")

    # Start year
    while True:
        raw = input(
            Fore.MAGENTA + "Enter start year (leave blank for no start year): "
        ).strip()
        if not raw:
            start_year = None
            break
        if raw.isdigit() and len(raw) == 4:
            start_year = int(raw)
            break
        print(Fore.RED + "⚠️ Year must be a four-digit number.")

    # End year
    while True:
        raw = input(
            Fore.MAGENTA + "Enter end year (leave blank for no end year): "
        ).strip()
        if not raw:
            end_year = None
            break
        if raw.isdigit() and len(raw) == 4:
            end_year = int(raw)
            break
        print(Fore.RED + "⚠️ Year must be a four-digit number.")

    # Filtering
    filtered: List[Tuple[str, int, float]] = []
    for movie_title, record in movies.items():
        movie_rating = record["rating"]
        movie_year = record["year"]
        if min_rating is not None and movie_rating < min_rating:
            continue
        if start_year is not None and movie_year < start_year:
            continue
        if end_year is not None and movie_year > end_year:
            continue
        filtered.append((movie_title, movie_year, movie_rating))

    # Output
    print(Fore.CYAN + "\nFiltered Movies:")
    if filtered:
        for movie_title, movie_year, movie_rating in filtered:
            print(Fore.GREEN + f"{movie_title} ({movie_year}): {movie_rating}")
    else:
        print(Fore.YELLOW + "No movies match the criteria.")
    input(Fore.MAGENTA + "\nPress enter to continue")


def create_rating_histogram() -> None:
    """Generate and save a histogram of movie ratings."""
    movies = movie_storage.get_movies()
    ratings = [record["rating"] for record in movies.values()]
    if not ratings:
        print(Fore.RED + "No movies in the database.")
        input(Fore.MAGENTA + "\nPress enter to continue")
        return

    filename = prompt_title("Enter filename for histogram (e.g., ratings.png): ")
    plt.figure(figsize=(10, 8))
    plt.hist(ratings, bins=20, edgecolor="black", alpha=0.7)
    plt.title("Movie Ratings Histogram")
    plt.xlabel("Rating")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.savefig(filename)
    print(Fore.GREEN + f"Histogram saved to {filename}")
    input(Fore.MAGENTA + "\nPress enter to continue")


# --------- Main loop ---------


def main() -> None:
    """Main loop handling user interaction and menu navigation."""
    while True:
        print_header()
        display_menu()
        choice = prompt_choice()

        if choice == 0:
            print(Fore.CYAN + "Bye!")
            break
        elif choice == 1:
            list_movies()
        elif choice == 2:
            add_movie()
        elif choice == 3:
            delete_movie()
        elif choice == 4:
            update_movie()
        elif choice == 5:
            stats()
        elif choice == 6:
            random_movie()
        elif choice == 7:
            search_movie()
        elif choice == 8:
            sort_movies_by_rating()
        elif choice == 9:
            create_rating_histogram()
        elif choice == 10:
            sort_movies_by_year()
        elif choice == 11:
            filter_movies()


if __name__ == "__main__":
    main()
