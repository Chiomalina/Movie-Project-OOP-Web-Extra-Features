# main.py
"""Entrypoint that wires StorageJson/StorageCsv -> MovieApp via CLI argument."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Tuple

from movie_app import MovieApp
from storage.storage_json import StorageJson
from storage.storage_csv import StorageCsv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="My Movies Database CLI — choose a storage file (.json or .csv)."
    )
    parser.add_argument(
        "storage_file",
        nargs="?",
        default="storage/movies.csv",
        help="Path to storage file (e.g., john.json or ashley.csv). Defaults to storage/movies.csv",
    )
    return parser.parse_args()


def choose_backend(path_str: str) -> Tuple[str, str]:
    """
    Decide backend by extension.
    Returns (backend_name, normalized_path_str)
    """
    p = Path(path_str)
    # Normalize to string for constructors
    if p.suffix.lower() == ".json":
        return "json", str(p)
    elif p.suffix.lower() == ".csv":
        return "csv", str(p)
    else:
        raise ValueError(
            f"Unsupported file extension '{p.suffix or '(none)'}'. "
            "Use a .json or .csv file."
        )


def ensure_parent_dir(path_str: str) -> None:
    """Create parent directory if it doesn't exist (no error if already exists)."""
    Path(path_str).parent.mkdir(parents=True, exist_ok=True)


def main() -> None:
    args = parse_args()
    backend, storage_path = choose_backend(args.storage_file)
    ensure_parent_dir(storage_path)

    if backend == "json":
        storage = StorageJson(storage_path)
    else:  # "csv"
        storage = StorageCsv(storage_path)

    app = MovieApp(storage)
    app.run()


if __name__ == "__main__":
    main()
