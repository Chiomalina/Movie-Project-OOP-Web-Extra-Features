"""
Interface CRUD
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class IStorage(ABC):
	""" Abstract storage interface exposing CRUD operations for movies."""

	@abstractmethod
	def list_movies(self) -> Dict[str, Dict[str, Any]]:
		"""
		return ll movies keyed by title.
		"""
		raise NotImplementedError

	@abstractmethod
	def add_movie(self, title: str, year: str, rating: float | None, poster: str | None) -> None:
		"""
        Persist a movie record. No input validation or user interaction here.
        """
		raise NotImplementedError

	@abstractmethod
	def delete_movie(self, title: str) -> None:
		"""
	    Remove a movie by its exact title key.
	    """
		raise NotImplementedError

	@abstractmethod
	def update_movie(self, title: str, rating: float | None) -> None:
		"""
	    Update only the rating for an existing movie.
	    """
		raise NotImplementedError