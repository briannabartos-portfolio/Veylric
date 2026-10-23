import subprocess
from urllib.parse import quote

def search_spotify(search_term=None, needs_approval=False):
    if search_term is None:
        search_term = input("Search Spotify for: ")

    search_term = search_term.strip()
    if not search_term:
        print("No search entered.")
        return None

    encoded_term = quote(search_term, safe="")

    search_uri = f"spotify:search:{encoded_term}"

    # Approval is only required when something looked off
    if needs_approval:
        print(f'Search preview: "{search_term}"')
        approval = input("Type SEARCH to open these results, or press Enter to cancel: ").strip()
        if approval != "SEARCH":
            print("Cancelled. Spotify was not opened.")
            return None
    else:
        print(f'Searching Spotify for "{search_term}".')

    try:
        subprocess.run(["open", search_uri], check=True)
    except subprocess.CalledProcessError:
        print("Couldn't open the Spotify search.")
        return None

    # Return the words searched so the caller can verify and remember them
    return search_term

if __name__ == "__main__":
    if search_spotify():
        print("Search request sent.")
