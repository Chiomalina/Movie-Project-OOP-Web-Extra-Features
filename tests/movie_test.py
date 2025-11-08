from storage_json import StorageJson

john = StorageJson("john.json")

print("=== LIST (empty or existing) ===")
print(john.list_movies())

print("\n=== ADD ===")
john.add_movies("Inception", 2010, 9.0, poster=None)
john.add_movies("Inception", 2010, 9.0, poster=None)

print("\n=== LIST (after add) ===")
print(john.list_movies())


print("\n=== UPDATE ===")
john.update_movie("Titanic", 9.1)
print(john.list_movies())

print("\n=== DELETE ===")
john.delete_movie("Inception")
print(john.list_movies)