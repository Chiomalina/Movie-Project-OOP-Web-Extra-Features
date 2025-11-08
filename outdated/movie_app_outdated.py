"""
movie_app.py
The CLI app class (menu + commands), no main() here

"""

from __future__ import annotations

from colorama import Fore, Style
import random
import matplotlib.pyplot as plt

from storage import IStorage
from validators import (
    prompt_title,
    prompt_rating,
    prompt_year_filter,
    prompt_choice,
    safe_float,
    prompt_year_required,
)
from utils import normalize_title
from movies import select_title_from_user_query


class MovieApp:
    """ CLI application that manages movies using a pluggable storage backend """

    MENU_TEXT = f"""
    {Fore.CYAN}=== Movie App ==={Style.RESET_ALL}
    0.  Exit
    1.  List movies
    2.  Add movie
    3.  Delete movie
    4.  Update movie rating
    5.  Stats
    6.  Random movie
    7.  Create rating histogram
    8.  Search by name
    9.  Sort by rating
    10. Sort by year
    11. Filter by rating/year
    """


    def __init__(self, storage: IStorage) -> None:
        """
        Args:
            storage: An implementation of IStorage (e.g., StorageJson).
        """
        self._storage = storage


    # ----------------- Commands (private) -----------------
    def _command_list_movies(self) -> None:
        """
        Print all movies currently stored.

        Side effects:
            - Reads the full database from `movie_storage`.
            - Prints one line per movie in the format: "<title> (<year>): <rating>".

        Returns:
            None
        """
        movies = self._storage.list_movies()
        if not movies:
            print("No movies in database.")
            return
        for title, rec in movies.items():
            print(f"{title} ({rec.get('year', '?')}): {rec.get('rating', '?')}")

    def _command_add_movie(self) -> None:
        """
        Add a movie by fetching real data from OMDb using only the title from the user.
        Stores: Title, Year, Rating (IMDb), Poster URL.
        """

        title = prompt_title("Enter new movie name: ")
        rating = prompt_rating()
        year = prompt_year_required()
        # poster optional-keep None for now
        self._storage.add_movie(title, year, rating, poster=None)
        print(f"{title} ({year}) added with rating {rating}")



    def _command_delete_movie(self) -> None:
        """
        Delete a movie using a safe, user-confirmed flow.

        Flow:
            1) Load all movies; abort if empty.
            2) Ask for a movie name; resolve against database titles using:
               - exact match (case/space-insensitive via `normalize_title`),
               - substring matches,
               - fuzzy matches (RapidFuzz).
            3) Show the resolved record's details.
            4) Require the user to re-type the exact title to confirm deletion.
            5) Delete from storage (handles missing key gracefully).

        Side effects:
            - Reads input from stdin; writes messages to stdout.
            - May remove an entry from persistent storage.

        Returns:
            None
        """
        movies = self._storage.list_movies()
        if not movies:
            print("No movies in database.")
            return

        user_input = prompt_title("Enter movie name to delete: ")
        resolved_title = select_title_from_user_query(movies, user_input)
        if not resolved_title:
            return

        record = movies[resolved_title]

        # Show details for confirmation
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

        # Perform deletion
        self._storage.delete_movie(resolved_title)
        print(f"'{resolved_title}' successfully deleted.")


    def _command_update_movie(self) -> None:
        """
        Update the rating of an existing movie.

        Flow:
            1) Load movies; abort if empty.
            2) Ask for a movie name and resolve it (exact/substring/fuzzy).
            3) Prompt for a new rating (float in [0.0, 10.0]).
            4) Save the updated rating.

        Side effects:
            - Reads user input.
            - Writes the updated record to storage.
            - Prints a confirmation line.

        Returns:
            None
        """
        movies = self._storage.list_movies()
        if not movies:
            print("No movies in database.")
            return
        user_input = prompt_title("Enter movie name to update: ")
        resolved_title = select_title_from_user_query(movies, user_input)
        if not resolved_title:
            return
        new_rating = prompt_rating()
        self._storage.update_movie(resolved_title, new_rating)
        print(f"'{resolved_title}' updated with rating {new_rating}")


    def _command_stats(self) -> None:
        """
        Compute and display simple statistics for stored movies.

        Statistics:
            - Average rating (mean, 1 decimal place).
            - Median rating (simple middle element; for even counts this uses the
              upper-middle after sorting).
            - Best movie title by rating (first max).
            - Worst movie title by rating (first min).

        Side effects:
            - Reads from storage and prints results.

        Returns:
            None
        """
        movies = self._storage.list_movies()
        ratings = [rec["rating"] for rec in movies.values()]
        if not ratings:
            print("No movies in database.")
            return
        avg = sum(ratings) / len(ratings)
        sorted_ratings = sorted(ratings)
        median = sorted_ratings[len(sorted_ratings) // 2]
        best = max(movies, key=lambda t: movies[t]["rating"])
        worst = min(movies, key=lambda t: movies[t]["rating"])
        print(f"Average: {avg:.1f}, Median: {median}, Best: {best}, Worst: {worst}")


    def _command_random_movie(self) -> None:
        """
        Pick and display a random movie from the database.

        Side effects:
            - Reads movies from storage.
            - Prints the randomly chosen title with year and rating.

        Returns:
            None
        """
        movies = self._storage.list_movies()
        if not movies:
            print("No movies in database.")
            return
        chosen = random.choice(list(movies))
        rec = movies[chosen]
        year = rec.get("year", "Unknown")
        rating = rec.get("rating", "N/A")
        print(f"Your random Movie for tonight is: {chosen} ({year}): {rating}")


    def _command_create_rating_histogram(self) -> None:
        """
        Create and save a histogram of all movie ratings.

        Flow:
            1) Load ratings from storage; abort if none.
            2) Ask the user for an output filename (e.g., 'ratings.png').
            3) Plot a histogram with 20 bins and save the figure to disk.

        Side effects:
            - Prompts for a filename.
            - Writes an image file via matplotlib.
            - Prints where the histogram was saved.

        Returns:
            None
        """
        movies = self._storage.list_movies()
        ratings = [rec["rating"] for rec in movies.values()]
        if not ratings:
            print("No movies in database.")
            return
        filename = input("Enter filename for histogram (ratings.png): ").strip() or "ratings.png"
        plt.hist(ratings, bins=20, edgecolor="black")
        plt.title("Movie Ratings Histogram")
        plt.xlabel("Rating")
        plt.ylabel("Frequency")
        plt.savefig(filename)
        print(f"Histogram saved to {filename}")


    # ----------------- Search & Selection -----------------
    def _command_search_movies(self) -> None:
        """
        Search for a movie by (part of) its name and print the best match.

        Flow:
            1) Load movies; abort if empty.
            2) Prompt the user for a search string.
            3) Resolve a title via `select_title_from_user_query`.
            4) Print the resolved movie's year and rating.

        Side effects:
            - Reads user input; prints results.

        Returns:
            None
        """
        movies = self._storage.list_movies()
        if not movies:
            print("No movies in database.")
            return
        term = prompt_title("Enter part of movie name to search: ")
        resolved = select_title_from_user_query(movies, term)
        if resolved:
            rec = movies[resolved]
            print(f"{resolved} ({rec['year']}): {rec['rating']}")


    def _command_sort_movies_by_rating(self) -> None:
        """
        Display movies sorted by rating (highest first).

        Side effects:
            - Reads from storage.
            - Prints one line per movie in sorted order.

        Returns:
            None
        """
        movies = self._storage.list_movies()
        sorted_items = sorted(movies.items(), key=lambda kv: kv[1]["rating"], reverse=True)
        for title, rec in sorted_items:
            print(f"{title} ({rec['year']}): {rec['rating']}")


    def _command_sort_movies_by_year(self) -> None:
        """
        Display movies sorted by release year.

        Flow:
            - Prompt whether to show latest movies first.
            - Sort ascending (oldest→newest) unless the user chooses 'y' for latest first.

        Side effects:
            - Reads user input.
            - Prints sorted movie lines.

        Returns:
            None
        """
        movies = self._storage.list_movies()
        if not movies:
            print("No movies in database.")
            return
        reverse = input("Show latest movies first? (y/n): ").strip().lower() == "y"
        sorted_items = sorted(movies.items(), key=lambda kv: kv[1]["year"], reverse=reverse)
        for title, rec in sorted_items:
            print(f"{title} ({rec['year']}): {rec['rating']}")


    def _command_filter_movies(self) -> None:
        """
        Filter movies by minimum rating and/or a year range, then display matches.

        Prompts:
            - Minimum rating (blank = no minimum). Accepts '.' or ',' decimals.
            - Start year (blank = no lower bound). Must be ≤ current year.
            - End year (blank = no upper bound). Must be ≤ current year.

        Filter logic:
            - Exclude any movie with rating < min_rating (if provided).
            - Exclude movies with year < start_year (if provided).
            - Exclude movies with year > end_year (if provided).

        Side effects:
            - Reads user input and prints the filtered list, or a message if none.

        Returns:
            None
        """
        movies = self._storage.list_movies()

        # Minimum rating
        raw = input("Enter minimum rating (blank=none): ").strip()
        min_rating = safe_float(raw) if raw else None

        # Start year (cannot be future)
        start_year = prompt_year_filter("Enter start year")

        # End year (cannot be future)
        end_year = prompt_year_filter("Enter end year")

        filtered = []
        for title, rec in movies.items():
            if min_rating is not None and rec["rating"] < min_rating:
                continue
            if start_year is not None and rec["year"] < start_year:
                continue
            if end_year is not None and rec["year"] > end_year:
                continue
            filtered.append((title, rec["year"], rec["rating"]))

        if not filtered:
            print("No movies match criteria.")
            return

        for title, year, rating in filtered:
            print(f"{title} ({year}): {rating}")


    # -------- Main loop --------
    def run(self) -> None:
        """
		Menu loop: prints options, gets a command, executes it until user exits.
		"""
        actions = {
            1: self._command_list_movies,
            2: self._command_add_movie,
            3: self._command_delete_movie,
            4: self._command_update_movie,
            5: self._command_stats,
            6: self._command_random_movie,
            7: self._command_create_rating_histogram,
            8: self._command_search_movies,
            9: self._command_sort_movies_by_rating,
            10: self._command_sort_movies_by_year,
            11: self._command_filter_movies,
        }

        while True:
            print(self.MENU_TEXT)
            choice = prompt_choice(max_choice=11)
            if choice == 0:
                print("Goodbye!")
                return
            action = actions.get(kind := choice)
            if action:
                action()
            else:
                print(f"Unknown choice: {kind}")
