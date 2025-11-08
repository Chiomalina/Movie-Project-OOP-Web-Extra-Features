from __future__ import annotations

import html
import os
from pathlib import Path
from typing import Dict, Any, Iterable


def build_movie_grid(movies: Iterable[Dict[str, Any]]) -> str:
	"""
	Accepts an iterable of movie dicts that look like:
	  {"title": str, "year": str|int|None, "poster": str|None}
	and returns the <li>...</li> HTML for all movies.
	"""
	parts = []
	for movie in movies:
		title = html.escape(str(movie.get("title", "")).strip())
		year = html.escape(str(movie.get("year", "")).strip()) if movie.get("year") is not None else ""
		poster = str(movie.get("poster") or "").strip()

		poster_attr = html.escape(poster) if poster else ""
		img_tag = (
			f'<img class="movie-poster" src="{poster_attr}" title="" alt="Poster for {title}"/>'
			if poster_attr else
			'<div class="movie-poster" title=""></div>'
		)

		parts.append(
			f"""
			<li>
			  <div class="movie">
				{img_tag}
				<div class="movie-title">{title}</div>
				<div class="movie-year">{year}</div>
			  </div>
			</li>
			""".strip()
		)
	return "\n\n".join(parts)


def generate_website_from_storage(
	storage,
	template_path: str | None = None,
	output_path: str | None = None,
	title: str = "Chioma's Movie App",
) -> None:
	# Resolve base dir next to this source file, not the CWD
	base_dir = Path(__file__).resolve().parent
	static_dir = base_dir / "static"

	# Defaults if not provided
	tpl_path = Path(template_path) if template_path else static_dir / "index_template.html"
	out_path = Path(output_path) if output_path else static_dir / "index.html"

	# Ensure output directory exists
	out_path.parent.mkdir(parents=True, exist_ok=True)

	# 1) Validate template
	if not tpl_path.exists():
		raise FileNotFoundError(f"Template not found: {tpl_path}")

	# 2) Get movies
	movie_data: Dict[str, Dict[str, Any]] = storage.list_movies()

	# 3) Flatten for rendering
	movies = [
		{"title": movie_title, "year": movie.get("year"), "poster": movie.get("poster")}
		for movie_title, movie in movie_data.items()
	]

	# 4) Read template
	template_html = tpl_path.read_text(encoding="utf-8")

	# 5) Build grid
	movie_grid_html = build_movie_grid(movies)

	# 6) Fill placeholders
	html_output = (
		template_html
		.replace("__TEMPLATE_TITLE__", html.escape(title))
		.replace("__TEMPLATE_MOVIE_GRID__", movie_grid_html)
	)

	# 7) Write output
	out_path.write_text(html_output, encoding="utf-8")

	# Optional: quick breadcrumb for debugging
	print(f"Template: {tpl_path}")
	print(f"Output:   {out_path}")
