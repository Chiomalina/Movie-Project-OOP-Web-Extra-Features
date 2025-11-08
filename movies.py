"""
movies.py -- minimal module exporting only
    select_title_from_user_query
    (the resolver) used by movie_app.py
"""

from typing import Dict
from validators import (
    prompt_index,
)
from utils import normalize_title, substring_matches, fuzzy_matches


# ----------------- Search & Selection -----------------

def select_title_from_user_query(movies: Dict[str, dict], user_input: str) -> str | None:
    """
    Resolve a user-entered movie title against existing records.

    Matching strategy:
        1) Exact match using normalized titles (`normalize_title`).
        2) Substring matches (case/space-insensitive). If multiple, show a
           numbered menu and let the user pick.
        3) Fuzzy matches using RapidFuzz. If multiple, show a numbered list
           with scores, then let the user pick.

    Args:
        movies: A mapping from title to record dict (must contain 'year'/'rating').
        user_input: The raw string typed by the user.

    Side effects:
        - May print match lists and prompt for an index if multiple options exist.

    Returns:
        The resolved canonical title string if a selection is made; otherwise None.
    """
    titles = list(movies.keys())
    norm_input = normalize_title(user_input)

    # Exact match
    exact = [t for t in titles if normalize_title(t) == norm_input]
    if exact:
        return exact[0]

    # Substring match
    subs = substring_matches(titles, user_input)
    if subs:
        if len(subs) == 1:
            return subs[0]
        print("Multiple matches:")
        for idx, t in enumerate(subs, 1):
            print(f"{idx}. {t}")
        idx_choice = prompt_index(len(subs))
        if idx_choice is not None:
            return subs[idx_choice]
        return None

    # Fuzzy match
    fuzzy = fuzzy_matches(titles, user_input)
    if fuzzy:
        print("Fuzzy matches:")
        for idx, (t, score) in enumerate(fuzzy, 1):
            print(f"{idx}. {t} [score: {score}]")
        idx_choice = prompt_index(len(fuzzy))
        if idx_choice is not None:
            return fuzzy[idx_choice][0]

    print("No matching titles found.")
    return None