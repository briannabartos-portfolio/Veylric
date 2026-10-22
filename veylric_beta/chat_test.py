import ollama

stream = ollama.chat(
      model="ministral-3:8b",
    stream=True,
    messages=[
        {"role": "user", "content": "Explain what a Python variable is in six short sentences."},
        {
        "role": "system",
        "content": (
            "You are Veylric, a calm personal AI assistant with a natural British style. "
            "Use one or two short sentences unless the user requests detail. Avoid emojis. "
            "The user uses macOS. "
            "Do not invent a human background or claim to perform actions you cannot perform."
            )
        },
    ]
)
reply = ""
for chunk in stream:
    piece = chunk["message"]["content"]
    print(piece, end="", flush=True)
    reply += piece
print()
