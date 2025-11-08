from colorama import Fore

def print_header() -> None:
    """Display the program header."""
    print(Fore.CYAN + " My Movies Database ".center(40, "*"))


def display_menu() -> None:
    """Show available menu options."""
    print(Fore.YELLOW + "\nMenu:")
    print(Fore.YELLOW + "0. Exit")
    print(Fore.YELLOW + "1. List movies")
    print(Fore.YELLOW + "2. Add movie")
    print(Fore.YELLOW + "3. Delete movie")
    print(Fore.YELLOW + "4. Update movie")
    print(Fore.YELLOW + "5. Stats")
    print(Fore.YELLOW + "6. Random movie")
    print(Fore.YELLOW + "7. Search movies")
    print(Fore.YELLOW + "8. Movies sorted by rating")
    print(Fore.YELLOW + "9. Create Rating Histogram")
    print(Fore.YELLOW + "10. Movies sorted by year")
    print(Fore.YELLOW + "11. Filter movies\n")
