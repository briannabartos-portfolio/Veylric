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
                    "Return search_spotify for a request to search for, find, or play a specific song, artist, album, or podcast, "
                    "whether or not Spotify is named. "
                    "Requests to find or search for things that are not music or podcasts are unknown. "
                    "Return pause_spotify for a request to pause or stop the music, such as 'pause my music'. "
                    "Return resume_spotify for a request to resume the music, such as 'carry on playing'. "
                    "Return next_spotify for a request to skip ahead, such as 'skip this song' or 'next track'. "
                    "Return previous_spotify for a request to go back, such as 'go back to the last song' or 'previous track'. "
                    "Return whats_playing for a question about which song is playing right now. "
                    "Return clarify_spotify when the user names Spotify but no action, such as 'Spotify, please' or 'Spotify?'. "
                    "Return unknown for ordinary questions, requests telling Veylric not to do something, future possibilities, or unrelated messages. "
                    "Questions about what Veylric did earlier, such as 'did you pause the music?', are unknown. "
                    "Return only one label. Do not perform any action."
                )
            },
            {"role": "user", "content": message}
        ]
    )

    # Strip decoration such as **bold** or a full stop; the allowlist check below stays exact
    suggested_intent = response["message"]["content"].strip().strip("*`'\". ")

    allowed_intents = [
        "open_spotify", "search_spotify", "clarify_spotify",
        "pause_spotify", "resume_spotify", "next_spotify", "previous_spotify", "whats_playing",
        "unknown"
    ]

    if suggested_intent not in allowed_intents:
        suggested_intent = "unknown"

    return suggested_intent
reference_words = ["them", "they", "that", "it", "this", "those", "these", "him", "her"]
# A reference word only counts right after one of these, as in "find them" or "search for that"
reference_starters = ["search", "find", "play", "for", "up"]
filler_words = reference_words + ["for", "on", "me", "please", "search", "find", "play", "spotify"]
# Word sources from safest to riskiest
word_sources = ["request", "earlier", "veylric", "invented"]
plain_prompt = (
    "Extract only the words to search for on Spotify from the user's request. "
    "Remove polite words, the word Spotify, and verbs such as search, find, or play. "
    "Use only words that appear in the request. Never add names or titles. "
    "Return only the search words on a single line, with no quotes, notes, or explanation. "
    "If there is nothing specific to search for, return NONE."
)
context_prompt = (
    "The user's current request uses words such as them, that, or it. "
    "Return the name or title those words refer to. "
    "Look first in the current request itself, then in the recent conversation, most recent first. "
    "Never add names or titles that do not appear in the request or the conversation. "
    "Return only the search words on a single line, with no quotes, notes, or explanation. "
    "If it is unclear what they refer to, return NONE."
)
def uses_reference(message):
    words = [word.strip(".,!?") for word in message.lower().split()]
    for index in range(1, len(words)):
        if words[index] in reference_words and words[index - 1] in reference_starters:
            return True
    return False
def extract_search_term(message, history=None):
    # Only give the model the conversation when the request points back to it
    if not uses_reference(message):
        history = []
    history = history or []

    user_text = ""
    veylric_text = ""
    conversation = ""
    for entry in history:
        if entry["role"] == "user":
            user_text += " " + entry["content"].lower()
            conversation += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            # Action records (role "system") are skipped; they aren't anyone's words
            veylric_text += " " + entry["content"].lower()
            conversation += f"Veylric: {entry['content']}\n"

    # Ordinary requests keep the original prompt; references get the context prompt
    if conversation:
        system_prompt = context_prompt
        prompt = f"Recent conversation:\n{conversation}\nCurrent request: {message}"
    else:
        system_prompt = plain_prompt
        prompt = message

    response = ollama.chat(
        model="ministral-3:8b",
        options={"temperature": 0, "num_predict": 30},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    # Keep only the first line; the model sometimes adds notes or lists after it
    reply = response["message"]["content"].strip()
    first_line = reply.split("\n")[0]
    search_term = " ".join(first_line.split()).strip("\"'")
    if search_term.upper() == "NONE":
        return None, "request"

    # Check where each word came from; drop any word nobody said
    kept_words = []
    riskiest_source = "request"
    for word in search_term.split():
        clean_word = word.lower().strip(".,!?")
        if clean_word in message.lower():
            source = "request"
        elif clean_word in user_text:
            source = "earlier"
        elif clean_word in veylric_text:
            source = "veylric"
        else:
            source = "invented"

        if source != "invented":
            kept_words.append(word.strip(".,!?"))
        if word_sources.index(source) > word_sources.index(riskiest_source):
            riskiest_source = source
    search_term = " ".join(kept_words)

    # Filler on its own ("for", "them") is not a real search
    if all(word.lower().strip(".,!?") in filler_words for word in kept_words):
        search_term = ""

    # Python checks the model's answer before it is used
    if not search_term or len(search_term) > 100:
        return None, "request"

    # riskiest_source tells the caller how much to trust the words
    return search_term, riskiest_source
if __name__ == "__main__":
    message = input("Request: ").strip()
    print(f"Request received: {message}")

    suggested_intent = classify_request(message)
    print(f"Validated intent: {suggested_intent}")

    if suggested_intent == "open_spotify":
        print("Preview: I would call the Spotify-opening function.")
    elif suggested_intent == "search_spotify":
        search_term, source = extract_search_term(message)
        print(f"Preview: I would search Spotify for: {search_term}")
        print(f"Preview: Riskiest word source: {source}")
    elif suggested_intent == "clarify_spotify":
        print("Preview: What would you like me to do with Spotify?")
    else:
        print("Preview: No tool selected. This request needs chat.")
