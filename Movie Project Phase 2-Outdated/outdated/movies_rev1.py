#Before Persistent Storage


import random
import matplotlib.pyplot as plt
from colorama import Fore, init
from rapidfuzz import process
from rapidfuzz import fuzz

# Initialize colorama
init(autoreset=True)

# Global dictionary to store movies and ratings
movies = {
	"The Shawshank Redemption": {"rating": 9.5, "year": 1994},
	"Pulp Fiction": {"rating": 8.8, "year": 1994},
	"The Room": {"rating": 3.6, "year": 2003},
	"The Godfather": {"rating": 9.2, "year": 1972},
	"The Godfather: Part II": {"rating": 9.0,"year": 1974},
	"The Dark Knight": {"rating": 9.0,"year": 2008},
	"12 Angry Men": {"rating": 8.9,"year": 1957},
	"Everything Everywhere All At Once": {"rating": 8.9,"year": 2022},
	"Forrest Gump": {"rating": 8.8,"year": 1994},
	"Star Wars: Episode V": {"rating": 8.7,"year": 1980}
}


def title():
	"""This function displays the title of the program."""
	title = " My Movies Database "
	width = 40
	introduction = title.center(width, "*")
	print(Fore.CYAN + introduction)


def display_menu():
	"""This program displays the menu of the program."""
	print(Fore.YELLOW + "\nMenu: ")
	print(Fore.YELLOW + "0.  Exit")
	print(Fore.YELLOW + "1.  List movies")
	print(Fore.YELLOW + "2.  Add movie")
	print(Fore.YELLOW + "3.  Delete movies")
	print(Fore.YELLOW + "4.  Update movies")
	print(Fore.YELLOW + "5.  Stats")
	print(Fore.YELLOW + "6.  Random movies")
	print(Fore.YELLOW + "7.  Search movies")
	print(Fore.YELLOW + "8.  Movies sorted by rating")
	print(Fore.YELLOW + "9.  Create Rating Histogram\n")


def list_movies():
	"""This function lists out the movies stored in the global variable movies."""
	global movies
	count_of_movies = len(movies)
	print(Fore.CYAN + f"\n{count_of_movies} movies in total")
	for movie_title, info in movies.items():
		print(Fore.GREEN + f"{movie_title} ({info["year"] }): {info["rating"] }")

	# Pause for user input
	input(Fore.MAGENTA + "\nPress enter to continue")


def add_movie():
    """This function adds a new movie to the movie database,
    validating rating and year."""
    global movies

    # 1. Movie title (no change)
    new_title = input(Fore.MAGENTA + "Enter new movie name: ").strip()

    # 2. Rating: must be float 0.0–10.0
    while True:
        rating_input = input(Fore.MAGENTA + "Enter new movie rating (0.0–10.0): ").strip()
        try:
            new_rating = float(rating_input)
            if 0.0 <= new_rating <= 10.0:
                break
            else:
                print(Fore.RED + "⚠️ Rating must be between 0.0 and 10.0. Please try again.")
        except ValueError:
            print(Fore.RED + "⚠️ Invalid format—enter a number like 8.5.")

    # 3. Year: must be a 4-digit integer
    while True:
        year_input = input(Fore.MAGENTA + "Enter movie release year (YYYY): ").strip()
        if year_input.isdigit() and len(year_input) == 4:
            new_year = int(year_input)
            break
        else:
            print(Fore.RED + "⚠️ Year must be a 4-digit number (e.g. 1994). Please try again.")

    # 4. Save into the nested-dict structure
    movies[new_title] = {
        "rating": new_rating,
        "year":   new_year
    }
    print(Fore.GREEN + f"{new_title} ({new_year}) added with rating {new_rating}!")

    # Pause before returning to menu
    input(Fore.MAGENTA + "\nPress enter to continue")



def delete_movie():
	"""This function deletes a movie."""

	global movies

	movie_to_delete = input("Enter movie name to delete: ").strip().lower()

	# Performing a case-insensitive search for the movie.
	found_movie = None
	for movie in movies.keys():
		if movie.lower() == movie_to_delete:
			found_movie = movie
			break

	if found_movie:
		# Remove the movie using the original casing
		movies.pop(found_movie)
		print(f"{found_movie} successfully deleted")
	else:
		print(f"{movie_to_delete} doesn't exist")

	# Pause for user input
	input("\nPress enter to continue")


def update_movie():
	"""This function updates movies in the dictionary ."""
	global movies

	updated_movie_name = input("Enter movie name to update: ").strip().lower()

	found_movie = None
	for movie in movies.keys():
		if movie.lower() == updated_movie_name:
			found_movie = movie
			break

	if found_movie:
		# Update the movie
		updated_movie_rating = float(input("Enter movie rating: "))
		movies[updated_movie_name] = updated_movie_rating
		print(f"{updated_movie_name} successfully updated")
	else:
		print(f"{updated_movie_name} doesn't exist!")

	# Pause for user input
	input("\nPress enter to continue")


def stats():
	"""This function displays movie statistics."""
	global movies

	#movie_ratings = list(movies.values())
	movie_ratings = [info["rating"] for info in movies.values()]

	if movie_ratings:
		avg_rating = sum(movie_ratings) / len(movie_ratings)
		median_rating = sorted(movie_ratings)[len(movie_ratings) // 2]

		# Titles of the best and worst movies
		best_title = max(movies, key=lambda t: movies[t]["rating"])
		worst_title = min(movies, key=lambda t: movies[t]["rating"])

		# Ratings of the best and worst movies
		best_rating = movies[best_title]["rating"]
		worst_rating = movies[worst_title]["rating"]

		print(Fore.CYAN + f"\nAverage Rating: {avg_rating:.1f}")
		print(Fore.CYAN + f"Median Rating: {median_rating:.1f}")
		print(Fore.GREEN + f"Best Movie: {best_title} {best_rating}")
		print(Fore.RED + f"Worst Movie: {worst_title} {worst_rating}")
	else:
		print(Fore.RED + "No movies in the database.")

	# Pause for user input
	input(Fore.MAGENTA + "\nPress enter to continue")


def random_movie():
	"""This function selects a random movie."""
	global movies

	if movies:
		chosen_movie = random.choice(list(movies.keys()))
		print(Fore.GREEN + f"Your movie for tonight: {chosen_movie}, rated {movies[chosen_movie]}")

	# Pause for user input
	input(Fore.MAGENTA + "\nPress enter to continue")


def search_movie():
	"""This function searches for movies using fuzzy matching."""
	global movies

	# Step 1: Ask the user for a search term
	search_term = input(Fore.MAGENTA + "Enter part of movie name: ").strip()

	# Step 2: Check for an exact match
	if search_term in movies:
		print(Fore.GREEN + f"The movie \"{search_term}\" exists with a rating of {movies[search_term]}.")
	else:
		# Step 3: Use rapidfuzz to find close matches
		close_matches = process.extract(
			# The term the user is searching for
			query=search_term,
			# The movie titles in the dictionary
			choices=movies.keys(),
			# Scoring function (similarity based on Levenshtein distance)
			scorer=fuzz.ratio,
			# Max number of matches to return
			limit=5
		)

		# Filter matches with a similarity score above a threshold
		# Set a similarity threshold (0-100)
		threshold = 50
		filtered_matches = [match[0] for match in close_matches if match[1] >= threshold]

		# Step 4: Display results
		if filtered_matches:
			print(Fore.YELLOW + f"\nThe movie \"{search_term}\" does not exist. Did you mean:")
			for match in filtered_matches:
				print(Fore.CYAN + f" {match}")
		else:
			print(Fore.RED + f"\nThe movie \"{search_term}\" does not exist, and no similar movies were found.")

	# Pause for user input
	input(Fore.MAGENTA + "\nPress enter to continue")


def sort_movies_by_rating():
	"""This function sorts movies by rating."""
	global movies

	sorted_movies = sorted(
		movies.items(),
		key=lambda item: item[1]["rating"],
		reverse=True
	)
	print(Fore.CYAN + "\nMovies sorted by rating (descending):")
	for movie_title, info in sorted_movies:
		print(Fore.GREEN + f"{movie_title} ({info['year']}: {info['rating']}")

	# Pause for user input
	input(Fore.MAGENTA + "\nPress enter to continue")


def create_rating_histogram():
	"""This function creates a histogram of movie ratings."""
	global movies
	ratings = [info["rating"] for info in movies.values()]
	filename = input(Fore.MAGENTA + "Enter the filename to save the histogram (e.g., ratings_histogram.png): ").strip()
	plt.figure(figsize=(10, 8))
	plt.hist(ratings, bins=20, color='blue', edgecolor='black', alpha=0.7)
	plt.title("Movie Ratings Histogram")
	plt.xlabel("Movie Ratings")
	plt.ylabel("Frequency")
	plt.grid(True)
	plt.savefig(filename)
	print(Fore.GREEN + f"Histogram saved to {filename}")

	# Pause for user input
	input(Fore.MAGENTA + "\nPress enter to continue")


def main():
	"""Main function to run the program."""
	while True:
		title()
		display_menu()
		try:
			choice = int(input(Fore.MAGENTA + "Enter choice (0-9): "))
			if choice == 0:
				print(Fore.CYAN + "Bye")
				break
			if choice == 1:
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
				print(Fore.RED + "Invalid choice! Please select a number between 1 and 9.")
		except ValueError:
			print(Fore.RED + "Invalid input! Please enter a number.")


main()

