import ollama

def classify_request(message):
    if message.strip().lower() in ["open it", "launch it"]:
        return "unknown"
    response = ollama.chat(
        model="ministral-3:8b",
        options={"temperature": 0},
        messages=[
            {
                "role": "system",
                "content": (
                    "Classify the user's request. "
                    "Return open_spotify for a direct request to open or launch Spotify. "
                    "Return search_spotify for a request to search for, find, or play a specific song, artist, album, or podcast on Spotify. "
                    "Return clarify_spotify for an ambiguous Spotify action request, such as 'Spotify, please'. "
                    "Return unknown for ordinary questions, negated requests, future possibilities, or unrelated messages. "
                    "Return only one label. Do not perform any action."
                )
            },
            {"role": "user", "content": message}
        ]
    )

    suggested_intent = response["message"]["content"].strip()

    allowed_intents = ["open_spotify", "search_spotify", "clarify_spotify", "unknown"]

    if suggested_intent not in allowed_intents:
        suggested_intent = "unknown"

    return suggested_intent
def extract_search_term(message):
    response = ollama.chat(
        model="ministral-3:8b",
        options={"temperature": 0, "num_predict": 30},
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract only the words to search for on Spotify from the user's request. "
                    "Remove polite words, the word Spotify, and verbs such as search, find, or play. "
                    "Use only words that appear in the request. Never add names or titles. "
                    "Return only the search words on a single line, with no quotes, notes, or explanation. "
                    "If there is nothing specific to search for, return NONE."
                )
            },
            {"role": "user", "content": message}
        ]
    )

    # Keep only the first line; the model sometimes adds notes or lists after it
    reply = response["message"]["content"].strip()
    first_line = reply.split("\n")[0]
    search_term = " ".join(first_line.split()).strip("\"'")
    if search_term.upper() == "NONE":
        return None, False

    # Drop any word the model added that the user never said
    kept_words = []
    words_removed = False
    for word in search_term.split():
        if word.lower().strip(".,!?") in message.lower():
            kept_words.append(word)
        else:
            words_removed = True
    search_term = " ".join(kept_words)

    # Python checks the model's answer before it is used
    if not search_term or len(search_term) > 100:
        return None, False

    # words_removed tells the caller the model tried to add something
    return search_term, words_removed
if __name__ == "__main__":
    message = input("Request: ").strip()
    print(f"Request received: {message}")

    suggested_intent = classify_request(message)
    print(f"Validated intent: {suggested_intent}")

    if suggested_intent == "open_spotify":
        print("Preview: I would call the Spotify-opening function.")
    elif suggested_intent == "search_spotify":
        search_term, words_removed = extract_search_term(message)
        print(f"Preview: I would search Spotify for: {search_term}")
        if words_removed:
            print("Preview: The model added words, so I would ask for SEARCH approval.")
    elif suggested_intent == "clarify_spotify":
        print("Preview: What would you like me to do with Spotify?")
    else:
        print("Preview: No tool selected. This request needs chat.")
