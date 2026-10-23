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
                    "Return clarify_spotify for an ambiguous Spotify action request, such as 'Spotify, please'. "
                    "Return unknown for ordinary questions, negated requests, future possibilities, or unrelated messages. "
                    "Return only one label. Do not perform any action."
                )
            },
            {"role": "user", "content": message}
        ]
    )

    suggested_intent = response["message"]["content"].strip()

    allowed_intents = ["open_spotify", "clarify_spotify", "unknown"]

    if suggested_intent not in allowed_intents:
        suggested_intent = "unknown"

    return suggested_intent
if __name__ == "__main__":
    message = input("Request: ").strip()
    print(f"Request received: {message}")

    suggested_intent = classify_request(message)
    print(f"Validated intent: {suggested_intent}")

    if suggested_intent == "open_spotify":
        print("Preview: I would call the Spotify-opening function.")
    elif suggested_intent == "clarify_spotify":
        print("Preview: What would you like me to do with Spotify?")
    else:
        print("Preview: No tool selected. This request needs chat.")
