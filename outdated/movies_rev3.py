# Before Bonus oprion: Filter Movies

import random
import matplotlib.pyplot as plt
from colorama import Fore, init
from rapidfuzz import process, fuzz
from Archive import movie_storage

# Initialize colorama for colored terminal output
init(autoreset=True)


def prompt_title(prompt_msg):
    """Prompt until the user provides a non-empty movie title."""
    while True:
        s = input(Fore.MAGENTA + prompt_msg).strip()
        if s:
            return s
        print(Fore.RED + "⚠️ Title cannot be empty.")


def prompt_rating():
    """Prompt until a valid float between 0.0 and 10.0 is entered."""
    while True:
        s = input(Fore.MAGENTA + "Enter rating (0.0–10.0): ").strip()
        try:
            r = float(s)
            if 0.0 <= r <= 10.0:
                return r
            print(Fore.RED + "⚠️ Rating must be between 0.0 and 10.0.")
        except ValueError:
            print(Fore.RED + "⚠️ Invalid rating format.")


def prompt_year():
    """Prompt until a valid four-digit year is entered."""
    while True:
        s = input(Fore.MAGENTA + "Enter release year (YYYY): ").strip()
        if s.isdigit() and len(s) == 4:
            return int(s)
        print(Fore.RED + "⚠️ Year must be a four-digit number.")


def prompt_choice():
    """Prompt until the user selects a valid menu choice (0-10)."""
    while True:
        s = input(Fore.MAGENTA + "Enter choice (0-10): ").strip()
        try:
            c = int(s)
            if 0 <= c <= 10:
                return c
            print(Fore.RED + "⚠️ Choice must be between 0 and 10.")
        except ValueError:
            print(Fore.RED + "⚠️ Invalid input; please enter a number.")


def title():
    """Display the program header."""
    print(Fore.CYAN + " My Movies Database ".center(40, "*"))


def display_menu():
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
    print(Fore.YELLOW + "10. Movies sorted by year\n")


def list_movies():
    """List all movies with their year and rating."""
    movies = movie_storage.get_movies()
    print(Fore.CYAN + f"\n{len(movies)} movies in total")
    for t, info in movies.items():
        print(Fore.GREEN + f"{t} ({info['year']}): {info['rating']}")
    input(Fore.MAGENTA + "\nPress enter to continue")


def add_movie():
    """Add a new movie; ensures non-empty title, valid rating and year."""
    title_str = prompt_title("Enter new movie name: ")
    rating_val = prompt_rating()
    year_val = prompt_year()
    try:
        movie_storage.add_movie(title_str, year_val, rating_val)
        print(Fore.GREEN + f"{title_str} ({year_val}) added with rating {rating_val}!")
    except ValueError as e:
        print(Fore.RED + str(e))
    input(Fore.MAGENTA + "\nPress enter to continue")


def delete_movie():
    """Delete a movie; prompts until non-empty title is given."""
    title_str = prompt_title("Enter movie name to delete: ")
    try:
        movie_storage.delete_movie(title_str)
        print(Fore.GREEN + f"{title_str} successfully deleted.")
    except KeyError:
        print(Fore.RED + f"Movie '{title_str}' not found.")
    input(Fore.MAGENTA + "\nPress enter to continue")


def update_movie():
    """Update a movie's rating; prompts until non-empty title and valid rating."""
    title_str = prompt_title("Enter movie name to update: ")
    rating_val = prompt_rating()
    try:
        movie_storage.update_movie(title_str, rating_val)
        print(Fore.GREEN + f"{title_str} rating updated to {rating_val}.")
    except KeyError:
        print(Fore.RED + f"Movie '{title_str}' not found.")
    input(Fore.MAGENTA + "\nPress enter to continue")


def stats():
    """Display average, median, best and worst movie statistics."""
    movies = movie_storage.get_movies()
    ratings = [info['rating'] for info in movies.values()]
    if not ratings:
        print(Fore.RED + "No movies in the database.")
    else:
        avg = sum(ratings) / len(ratings)
        median = sorted(ratings)[len(ratings)//2]
        best = max(movies, key=lambda t: movies[t]['rating'])
        worst = min(movies, key=lambda t: movies[t]['rating'])
        print(Fore.CYAN + f"\nAverage Rating: {avg:.2f}")
        print(Fore.CYAN + f"Median Rating : {median:.2f}")
        print(Fore.GREEN + f"Best Movie    : {best} ({movies[best]['year']}) — {movies[best]['rating']}")
        print(Fore.RED + f"Worst Movie   : {worst} ({movies[worst]['year']}) — {movies[worst]['rating']}")
    input(Fore.MAGENTA + "\nPress enter to continue")


def random_movie():
    """Pick and display a random movie."""
    movies = movie_storage.get_movies()
    if movies:
        t = random.choice(list(movies))
        info = movies[t]
        print(Fore.GREEN + f"Your movie for tonight: {t} ({info['year']}) — {info['rating']}")
    input(Fore.MAGENTA + "\nPress enter to continue")


def search_movie():
    """Search for movies by fuzzy matching; prompts until non-empty term."""
    term = prompt_title("Enter part of movie name: ")
    movies = movie_storage.get_movies()
    if term in movies:
        info = movies[term]
        print(Fore.GREEN + f"Found: {term} ({info['year']}) — {info['rating']}")
    else:
        matches = process.extract(term, movies.keys(), scorer=fuzz.ratio, limit=5)
        suggestions = [m for m, score in matches if score >= 50]
        if suggestions:
            print(Fore.YELLOW + "\nNo exact match. Did you mean:")
            for m in suggestions:
                info = movies[m]
                print(Fore.CYAN + f" {m} ({info['year']}) — {info['rating']}")
        else:
            print(Fore.RED + "No similar movies found.")
    input(Fore.MAGENTA + "\nPress enter to continue")


def sort_movies_by_rating():
    """Show movies sorted by descending rating."""
    movies = movie_storage.get_movies()
    sorted_list = sorted(movies.items(), key=lambda x: x[1]['rating'], reverse=True)
    print(Fore.CYAN + "\nMovies sorted by rating:")
    for t, info in sorted_list:
        print(Fore.GREEN + f"{t} ({info['year']}) — {info['rating']}")
    input(Fore.MAGENTA + "\nPress enter to continue")


def sort_movies_by_year():
    """Show movies sorted by release year, asking latest-first or oldest-first."""
    movies = movie_storage.get_movies()
    # Ask user for order
    while True:
        ans = input(Fore.MAGENTA + "Show latest movies first? (y/n): ").strip().lower()
        if ans in ('y', 'n'):
            break
        print(Fore.RED + "⚠️ Please enter 'y' or 'n'.")
    reverse = True if ans == 'y' else False
    sorted_list = sorted(movies.items(), key=lambda x: x[1]['year'], reverse=reverse)
    order_desc = "latest first" if reverse else "oldest first"
    print(Fore.CYAN + f"\nMovies sorted by year ({order_desc}):")
    for t, info in sorted_list:
        print(Fore.GREEN + f"{t} ({info['year']}) — {info['rating']}")
    input(Fore.MAGENTA + "\nPress enter to continue")


def create_rating_histogram():
    """Generate and save a histogram of movie ratings; prompts until filename provided."""
    movies = movie_storage.get_movies()
    ratings = [info['rating'] for info in movies.values()]
    filename = prompt_title("Enter filename for histogram (e.g., ratings.png): ")
    plt.figure(figsize=(10, 8))
    plt.hist(ratings, bins=20, edgecolor='black', alpha=0.7)
    plt.title("Movie Ratings Histogram")
    plt.xlabel("Rating")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.savefig(filename)
    print(Fore.GREEN + f"Histogram saved to {filename}")
    input(Fore.MAGENTA + "\nPress enter to continue")


def main():
    """Main loop handling user interaction and menu navigation."""
    while True:
        title()
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


if __name__ == "__main__":
    main()
