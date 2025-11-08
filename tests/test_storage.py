"""
test_storage.py -- Quick sanity check for StorageJson (dev-only)
"""
import os
from storage.storage_json import StorageJson

TEST_FILE = "../outdated/john.json"

def reset(path: str) -> None:
    if os.path.exists(path):
        os.remove(path)

def main() -> None:
    reset(TEST_FILE)
    s = StorageJson(TEST_FILE)

    print("1) LIST on new file -> {} expected")
    print(s.list_movies())

    print("\n2) ADD two movies")
    s.add_movie("Inception", 2010, 9.0, poster=None)
    s.add_movie("Titanic", 1997, 8.5, poster=None)
    print(s.list_movies())

    print("\n3) UPDATE Titanic -> 9.1")
    s.update_movie("Titanic", 9.1)
    print(s.list_movies())

    print("\n4) DELETE Inception")
    s.delete_movie("Inception")
    print(s.list_movies())

if __name__ == "__main__":
    main()
