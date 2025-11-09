""" input helpers (prompt_title/rating/year/etc"""

from typing import Optional
import math
from datetime import datetime
from colorama import Fore

def safe_float(s: str) -> Optional[float]:
    """
    Convert a string to a finite float, accepting both '.' and ',' as decimal separators.

    Behavior:
        - Replaces commas with dots to accommodate locales that use ','.
        - Returns the float if conversion succeeds and the value is finite.
        - Returns None on ValueError (non-numeric input) or if the value is not finite (NaN/Inf).

    Args:
        s: The input string, e.g., "7.5", "7,5", "NaN".

    Returns:
        A finite float value, or None if parsing/validation fails.
    """
    s = s.replace(",", ".")
    try:
        x = float(s)
        return x if math.isfinite(x) else None
    except ValueError:
        return None


def prompt_title(prompt_msg: str) -> str:
    """
    Prompt the user repeatedly until they enter a non-empty title.

    UI:
        - Uses Colorama to color the prompt (magenta) and error messages (red).

    Args:
        prompt_msg: The message shown to the user (e.g., "Enter new movie name: ").

    Returns:
        The non-empty, stripped title string entered by the user.
    """
    while True:
        text = input(Fore.MAGENTA + prompt_msg).strip()
        if text:
            return text
        print(Fore.RED + "⚠️ Title cannot be empty.")


def prompt_rating() -> float:
    """
    Prompt the user for a movie rating in the range [0.0, 10.0], retrying until valid.

    Parsing rules:
        - Accepts '.' or ',' for decimals (via `safe_float`).
        - Rejects non-numeric, NaN, ±Inf, and values outside [0.0, 10.0].

    UI:
        - Magenta prompt, red validation errors.

    Returns:
        A float rating between 0.0 and 10.0 (inclusive).
    """
    while True:
        raw = input(Fore.MAGENTA + "Enter rating (0.0–10.0): ").strip()
        val = safe_float(raw)
        if val is not None and 0.0 <= val <= 10.0:
            return val
        print(Fore.RED + "⚠️ Rating must be a finite number between 0.0 and 10.0.")


def prompt_notes() -> str:
    """
    Prompt the user for a note string (can be empty to clear).
    Returns the stripped text ('' means clear).
    """
    return input(Fore.MAGENTA + "Enter movie notes (blank to clear):").strip()


def prompt_year_required(prompt_msg: str = "Enter release year") -> int:
    """
    Prompt until a valid 4-digit release year is entered (must not be in the future).

    Validation:
        - Accepts only 4-digit numeric input.
        - Year must be ≤ the current calendar year.

    UI:
        - Shows the current year's upper bound in the prompt.
        - Uses Colorama for colored prompt and error messages.

    Args:
        prompt_msg: Base text of the prompt (the function appends " (max <year>): ").

    Returns:
        The validated 4-digit year as an int.
    """
    current_year = datetime.now().year
    while True:
        raw = input(Fore.MAGENTA + f"{prompt_msg} (max {current_year}): ").strip()
        if raw.isdigit() and len(raw) == 4:
            year = int(raw)
            if year <= current_year:
                return year
            print(Fore.RED + f"⚠️ Year cannot be in the future (max {current_year}).")
        else:
            print(Fore.RED + "⚠️ Year must be a four-digit number.")


def prompt_year_filter(prompt_msg: str = "Filter by year") -> Optional[int]:
    """
    Prompt for an optional 4-digit year to use as a filter; blank returns None.

    Validation:
        - Accepts blank input → returns None (no filter).
        - Otherwise requires 4 digits and year ≤ current year.

    UI:
        - Indicates that blank disables the filter and shows the current max year.
        - Uses Colorama for colored prompt and error messages.

    Args:
        prompt_msg: Base prompt text (the function appends " (blank for none, max <year>): ").

    Returns:
        The validated year as int, or None if the user pressed Enter without input.
    """
    current_year = datetime.now().year
    while True:
        raw = input(Fore.MAGENTA + f"{prompt_msg} (blank for none, max {current_year}): ").strip()
        if raw == "":
            return None
        if raw.isdigit() and len(raw) == 4:
            year = int(raw)
            if year <= current_year:
                return year
            print(Fore.RED + f"⚠️ Year cannot be in the future (max {current_year}).")
        else:
            print(Fore.RED + "⚠️ Year must be a four-digit number.")


def prompt_choice(max_choice: int = 11) -> int:
    """
    Prompt for a menu choice integer in the range [0, max_choice], retrying until valid.

    Validation:
        - Requires an integer input.
        - Must be within bounds inclusive: 0 ≤ choice ≤ max_choice.

    UI:
        - Shows the valid range in the prompt.
        - Uses Colorama for colored prompt and error messages.

    Args:
        max_choice: The largest allowed integer choice (default 11).

    Returns:
        The validated integer choice.
    """
    while True:
        raw = input(Fore.MAGENTA + f"Enter choice (0–{max_choice}): ").strip()
        try:
            choice_val = int(raw)
            if 0 <= choice_val <= max_choice:
                return choice_val
            print(Fore.RED + f"⚠️ Choice must be between 0 and {max_choice}.")
        except ValueError:
            print(Fore.RED + "⚠️ Invalid input; please enter a number.")


def prompt_index(max_index: int) -> Optional[int]:
    """
    Prompt the user to select an index from 1..max_index, or press Enter to cancel.

    Behavior:
        - Blank input returns None (cancel).
        - Otherwise expects an integer in [1, max_index] and returns zero-based index.

    UI:
        - Uses Colorama for colored prompt and error messages.

    Args:
        max_index: The number of available items (must be ≥ 1 for any valid selection).

    Returns:
        The selected zero-based index (int), or None if the user cancels.
    """
    while True:
        raw = input(Fore.MAGENTA + "Enter number to choose (blank to cancel): ").strip()
        if raw == "":
            return None
        if raw.isdigit():
            num = int(raw)
            if 1 <= num <= max_index:
                return num - 1
        print(Fore.RED + f"⚠️ Please enter a number between 1 and {max_index}.")
