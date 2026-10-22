import subprocess
from urllib.parse import quote

def search_spotify(search_term=None):
    if search_term is None:
        search_term = input("Search Spotify for: ")

    search_term = search_term.strip()
    if not search_term:
        print("No search entered.")
        return

    encoded_term = quote(search_term, safe="")

    search_uri = f"spotify:search:{encoded_term}"
    print(f'Search preview: "{search_term}"')
    approval = input("Type SEARCH to open these results, or press Enter to cancel: ").strip()

    if approval == "SEARCH":
        try:
            subprocess.run(["open", search_uri], check=True)
        except subprocess.CalledProcessError:
            print("Couldn't open the Spotify search.")
        else:
            print(f"Sent Spotify a search request for: {search_term}")
    else:
        print("Cancelled. Spotify was not opened.")

if __name__ == "__main__":
    search_spotify()
