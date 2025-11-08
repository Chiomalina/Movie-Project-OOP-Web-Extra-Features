import json
import os

# Path to the JSON file for persistent storage
DATA_FILE = "data.json"


def get_movies():
    """
    Returns a dictionary of dictionaries that
    contains the movies information in the database.

    The function loads the information from the JSON
    file and returns the data.

    For example, the function may return:
    {
      "Titanic": {
        "rating": 9,
        "year": 1999
      },
      "...": {
        ...
      },
    }
    """
    if not os.path.exists(DATA_FILE):
        # Initialize an empty database if none exists
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_movies(movies):
    """
    Gets all your movies as an argument and saves them to the JSON file.
    """
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(movies, f, indent=4, ensure_ascii=False)


def add_movie(title, year, rating):
    """
    Adds a movie to the movies database.
    Loads the information from the JSON file, adds the movie,
    and saves it. The function doesn't need to validate the input.
    """
    movies = get_movies()
    movies[title] = {
        "rating": rating,
        "year": year
    }
    save_movies(movies)


def delete_movie(title):
    """
    Deletes a movie from the movies database.
    Loads the information from the JSON file, deletes the movie,
    and saves it. The function doesn't need to validate the input.
    """
    movies = get_movies()
    if title not in movies:
        raise KeyError(f"Movie '{title}' does not exist.")
    del movies[title]
    save_movies(movies)


def update_movie(title, rating):
    """
    Updates a movie from the movies database.
    Loads the information from the JSON file, updates the movie,
    and saves it. The function doesn't need to validate the input.
    """
    movies = get_movies()
    if title in movies:
        movies[title]["rating"] = rating
        save_movies(movies)
