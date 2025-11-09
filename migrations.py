# migrations.py
from __future__ import annotations
import csv
from pathlib import Path
from typing import List

def migrate_csv_add_notes(file_path: str | Path) -> bool:
    """
    Ensure the CSV has a trailing 'notes' column.
    - Makes a single backup <file>.bak the first time it changes the file.
    - Idempotent: returns False if already OK, True if modified.
    """
    p = Path(file_path)
    if not p.exists() or not p.is_file() or p.suffix.lower() != ".csv":
        raise FileNotFoundError(f"CSV not found or not a file: {p}")

    with p.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames: List[str] = list(reader.fieldnames or [])
        rows = [dict(row) for row in reader]

    if not fieldnames:
        # minimal default header if file was empty or headerless
        fieldnames = ["title", "rating", "year", "poster"]

    if "notes" in fieldnames:
        return False  # already migrated

    fieldnames = fieldnames + ["notes"]
    for r in rows:
        r.setdefault("notes", "")

    # one-time backup
    backup = p.with_suffix(p.suffix + ".bak")
    if not backup.exists():
        p.replace(backup)
        # re-open backup to read rows we already have

    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return True
