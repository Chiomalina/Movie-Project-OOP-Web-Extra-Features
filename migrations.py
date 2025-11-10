# migrations.py
from __future__ import annotations
import csv
from pathlib import Path
from typing import List

def migrate_csv_ensure_columns(file_path: str | Path, required: list[str]) -> bool:
    p = Path(file_path)
    if not p.exists() or not p.is_file() or p.suffix.lower() != ".csv":
        raise FileNotFoundError(f"CSV not found or not a file: {p}")

    with p.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = [dict(row) for row in reader]

    if not fieldnames:
        fieldnames = ["title", "rating", "year", "poster"]

    changed = False
    for col in required:
        if col not in fieldnames:
            fieldnames.append(col)
            changed = True
            for r in rows:
                r.setdefault(col, "")

    if not changed:
        return False

    backup = p.with_suffix(p.suffix + ".bak")
    if not backup.exists():
        p.replace(backup)

    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return True
