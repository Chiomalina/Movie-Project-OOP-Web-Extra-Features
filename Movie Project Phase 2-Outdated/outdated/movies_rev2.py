# Before Application Robustness

import random
import matplotlib.pyplot as plt
from colorama import Fore, init
from rapidfuzz import process, fuzz
from Archive import movie_storage

# Initialize colorama
init(autoreset=True)


def title():
    """Display the program header."""
    # Inline header centering
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
    print(Fore.YELLOW + "9. Create Rating Histogram\n")


def prompt_rating():
    """Prompt user until a valid float rating between 0.0 and 10.0 is entered."""
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
    """Prompt user until a valid four-digit year is entered."""
    while True:
        s = input(Fore.MAGENTA + "Enter release year (YYYY): ").strip()
        if s.isdigit() and len(s) == 4:
            return int(s)
        print(Fore.RED + "⚠️ Year must be a four-digit number.")


def list_movies():
    """List all movies with year and rating."""
    movies = movie_storage.get_movies()
    print(Fore.CYAN + f"\n{len(movies)} movies in total")
    for title, info in movies.items():
        print(Fore.GREEN + f"{title} ({info['year']}): {info['rating']}")
    input(Fore.MAGENTA + "\nPress enter to continue")


def add_movie():
    """Add a new movie after validating rating and year."""
    title = input(Fore.MAGENTA + "Enter new movie name: ").strip()
    rating = prompt_rating()
    year = prompt_year()
    try:
        movie_storage.add_movie(title, year, rating)
        print(Fore.GREEN + f"{title} ({year}) added with rating {rating}!")
    except ValueError as e:
        print(Fore.RED + str(e))
    input(Fore.MAGENTA + "\nPress enter to continue")


def delete_movie():
    """Delete a movie by title."""
    title = input(Fore.MAGENTA + "Enter movie name to delete: ").strip()
    try:
        movie_storage.delete_movie(title)
        print(Fore.GREEN + f"{title} successfully deleted.")
    except KeyError:
        print(Fore.RED + f"Movie '{title}' not found.")
    input(Fore.MAGENTA + "\nPress enter to continue")


def update_movie():
    """Update an existing movie's rating."""
    title = input(Fore.MAGENTA + "Enter movie name to update: ").strip()
    rating = prompt_rating()
    try:
        movie_storage.update_movie(title, rating)
        print(Fore.GREEN + f"{title} rating updated to {rating}.")
    except KeyError:
        print(Fore.RED + f"Movie '{title}' not found.")
    input(Fore.MAGENTA + "\nPress enter to continue")


def stats():
    """Display average, median, best and worst movie stats."""
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
        print(Fore.GREEN + f"Best: {best} ({movies[best]['year']}) — {movies[best]['rating']}")
        print(Fore.RED + f"Worst: {worst} ({movies[worst]['year']}) — {movies[worst]['rating']}")
    input(Fore.MAGENTA + "\nPress enter to continue")


def random_movie():
    """Pick and show a random movie."""
    movies = movie_storage.get_movies()
    if movies:
        title = random.choice(list(movies))
        info = movies[title]
        print(Fore.GREEN + f"Your movie for tonight: {title} ({info['year']}) — {info['rating']}")
    input(Fore.MAGENTA + "\nPress enter to continue")


def search_movie():
    """Search for movies by fuzzy matching."""
    movies = movie_storage.get_movies()
    term = input(Fore.MAGENTA + "Enter part of movie name: ").strip()
    if term in movies:
        info = movies[term]
        print(Fore.GREEN + f"Found: {term} ({info['year']}) — {info['rating']}")
    else:
        matches = process.extract(term, movies.keys(), scorer=fuzz.ratio, limit=5)
        suggested = [m for m, score in matches if score >= 50]
        if suggested:
            print(Fore.YELLOW + "\nNo exact match. Did you mean:")
            for m in suggested:
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
    for title, info in sorted_list:
        print(Fore.GREEN + f"{title} ({info['year']}) — {info['rating']}")
    input(Fore.MAGENTA + "\nPress enter to continue")


def create_rating_histogram():
    """Generate and save a histogram of movie ratings."""
    movies = movie_storage.get_movies()
    ratings = [info['rating'] for info in movies.values()]
    filename = input(Fore.MAGENTA + "Enter filename for histogram: ").strip()
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
    """Main loop for user interaction."""
    while True:
        title()
        display_menu()
        try:
            choice = int(input(Fore.MAGENTA + "Enter choice (0-9): ").strip())
        except ValueError:
            print(Fore.RED + "Invalid input; please enter a number.")
            continue
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
        else:
            print(Fore.RED + "Invalid choice! Please select 0-9.")


if __name__ == "__main__":
    main()
