from __future__ import annotations

import html
import os
from pathlib import Path
from typing import Dict, Any, Iterable


def build_movie_grid(movies: Iterable[Dict[str, Any]]) -> str:
	"""
	Accepts an iterable of movie dicts that look like:
	  {"title": str, "year": str|int|None, "poster": str|None, "notes: str"}
	and returns the <li>...</li> HTML for all movies.
	"""
	parts = []
	for movie in movies:
		title = html.escape(str(movie.get("title", "")).strip())
		year = html.escape(str(movie.get("year", "")).strip()) if movie.get("year") is not None else ""
		poster = str(movie.get("poster") or "").strip()
		notes_raw = str(movie.get("notes") or "").strip()
		notes = html.escape(notes_raw)

		raw_r = movie.get("rating")
		rating_val = None
		if isinstance(raw_r, (int, float)):
			rating_val = float(raw_r)
		else:
			try:
				s = str(raw_r).strip()
				if s and s.upper() != "N/A":
					rating_val = float(s)
			except (TypeError, ValueError):
				rating_val = None

		rating_num = f"{rating_val:.1f}" if rating_val is not None else "N/A"
		rating_pct = int(max(0.0, min((rating_val or 0) / 10.0 * 100.0, 100.0)))

		poster_html = (
			f'<img class="movie-poster" src="{html.escape(poster)}" title="{notes}" alt="Poster for {title}"/>'
			if poster else
			f'<div class="movie-poster" title="{notes}"></div>'
		)

		rating_html = f"""
				<div class="movie-rating" data-rating="{html.escape(str(raw_r or ''))}" aria-label="Rating {rating_num} out of 10">
				  <span class="rating-number">Rating: {rating_num}</span>
				  <span class="stars" role="img" aria-hidden="true">
					<span class="stars-bg">★★★★★</span>
					<span class="stars-fg" style="width:{rating_pct}%">★★★★★</span>
				  </span>
				</div>
				""".strip()

		parts.append(
			f"""
					<li>
					  <div class="movie">
						<div class="poster-wrap" data-note="{notes}" title="{notes}">
						  {poster_html}
						</div>
						<div class="movie-title">Movie Title: {title}</div>
						<div class="movie-year">Release Year: {year}</div>
						{rating_html}
					  </div>
					</li>
					""".strip()
		)
	return "\n\n".join(parts)


def _parse_rating(raw) -> float | None:
	"""Accept floats/ints or numeric strings like '7.9'/'7,9'; else None."""
	if isinstance(raw, (int, float)):
		return float(raw)
	if raw is None:
		return None
	s = str(raw).strip().replace(",", ".")
	if not s or s.upper() == "N/A":
		return None
	try:
		return float(s)
	except ValueError:
		return None


def generate_website_from_storage(
	storage,
	template_path: str | None = None,
	output_path: str | None = None,
	title: str = "Chioma's Movie App",
) -> None:
	base_dir = Path(__file__).resolve().parent
	static_dir = base_dir / "static"
	tpl_path = Path(template_path) if template_path else static_dir / "index_template.html"
	out_path = Path(output_path) if output_path else static_dir / "index.html"
	out_path.parent.mkdir(parents=True, exist_ok=True)

	if not tpl_path.exists():
		raise FileNotFoundError(f"Template not found: {tpl_path}")

	# 2) Get movies from storage
	movie_data: Dict[str, Dict[str, Any]] = storage.list_movies()

	# 3) Flatten + NORMALIZE rating here (critical fix)
	movies = []
	for movie_title, movie in movie_data.items():
		movies.append({
			"title": movie_title,
			"year": movie.get("year"),
			"poster": movie.get("poster"),
			"notes": movie.get("notes"),
			"rating": _parse_rating(movie.get("rating")),   # <-- normalize
		})

	# (optional) quick debug so you can see values in the console:
	try:
		sample = next((m for m in movies if m["title"].casefold() == "titanic".casefold()), None)
		print("DEBUG Titanic ->", sample)
	except Exception:
		pass

	template_html = tpl_path.read_text(encoding="utf-8")
	movie_grid_html = build_movie_grid(movies)

	html_output = (
		template_html
		.replace("__TEMPLATE_TITLE__", html.escape(title))
		.replace("__TEMPLATE_MOVIE_GRID__", movie_grid_html)
	)
	out_path.write_text(html_output, encoding="utf-8")
	print(f"Template: {tpl_path}")
	print(f"Output:   {out_path}")