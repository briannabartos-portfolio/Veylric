# Imports: tools this program uses
import ollama
import ctypes
import os
import subprocess
import time
from datetime import datetime
from spotify_search_test import search_spotify
from intent_test import classify_request, extract_search_term
from pathlib import Path

# Settings: folder locations and assistant name
practice_folder = Path(__file__).parent / "practice_files"
move_test_folder = Path(__file__).parent / "move_test"
assistant_name = "Veylric"
conversation_history = []
pending_clarification = None
print(f"{assistant_name}: At your service, ma'am. Ready when you are.")

# File organization: build a plan and request approval
def preview_files(files, execute=False):
    proposed_moves = []
    if not files:
        print("There are no files to preview.")
        return
    for filename in files:
        if filename.lower().endswith(".jpg"):
            print(f"{filename} → Pictures (matched .jpg extension)")
            proposed_moves.append((filename, "Pictures"))
        elif filename.lower().endswith(".txt"):
            print(f"{filename} → Documents (matched .txt extension)")
            proposed_moves.append((filename, "Documents"))
        else:
            print(f"{filename} → Needs review (no matching rule; keep unchanged)")
    if not proposed_moves:
        print("No moves to propose.")
        return

    if execute:
        print("REAL MOVE MODE — approved files will be moved.")
        prompt = "Type APPROVE to move this plan, or press Enter to cancel: "
    else:
        print("SIMULATION ONLY — no files will change.")
        prompt = "Type APPROVE to simulate this plan, or press Enter to cancel: "

    approval = input(prompt).strip()

    if approval == "APPROVE":
        moved_count = 0
        skipped_count = 0
        failed_count = 0

        for filename, destination in proposed_moves:
            source_path = practice_folder / filename
            destination_path = practice_folder / destination / filename

            if not source_path.is_file():
                print(f"Skipped: {filename} — source file is no longer available.")
                skipped_count += 1
            elif destination_path.exists():
                print(f"Skipped: {filename} — destination already exists.")
                skipped_count += 1
            else:
                if execute:
                    try:
                        destination_path.parent.mkdir(exist_ok=True)
                        move_without_overwrite(source_path, destination_path)
                    except OSError as error:
                        failed_count += 1
                        print(f"Failed: {filename} — {error}")
                    else:
                        moved_count += 1
                        print(f"Moved: {filename}")
                        print(f"  To: {destination_path}")
                else:
                    print(f"Would move: {filename}")
                    print(f"  To: {destination_path}")
        if execute:
            print(
                f"Finished: {moved_count} moved, "
                f"{skipped_count} skipped, "
                f"{failed_count} failed."
            )
        else:
            print("Simulation complete. No files were changed.")
    else:
        print("Cancelled. No files were changed.")
# App checks: ask macOS whether an app is running
def is_app_running(app_name):
    result = subprocess.run(
        ["osascript", "-e", f'application "{app_name}" is running'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip() == "true"
def wait_for_app(app_name, timeout=5):
    # Check every half second until the app is running or time runs out
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_app_running(app_name):
            return True
        time.sleep(0.5)
    return False
def open_spotify():
    already_running = is_app_running("Spotify")
    try:
        subprocess.run(["open", "-a", "Spotify"], check=True)
    except subprocess.CalledProcessError:
        print(f"{assistant_name}: I couldn't open Spotify.")
        return

    # Attempt sent; now verify the outcome
    if already_running:
        print(f"{assistant_name}: Spotify was already open, ma'am. I've brought it to the front.")
    elif wait_for_app("Spotify"):
        print(f"{assistant_name}: Spotify is open, ma'am.")
    else:
        print(f"{assistant_name}: I asked macOS to open Spotify, but I can't confirm it started.")
def open_chrome():
    try:
        subprocess.run(["open", "-a", "Google Chrome"], check=True)
    except subprocess.CalledProcessError:
        print(f"{assistant_name}: I couldn't open Google Chrome.")
    else:
        print(f"{assistant_name}: I've sent the request to open Google Chrome.")
def close_chrome():
    try:
        subprocess.run(
            ["osascript", "-e", 'if application "Google Chrome" is running then tell application "Google Chrome" to quit'],
            check=True
        )
    except subprocess.CalledProcessError:
        print(f"{assistant_name}: I couldn't close Google Chrome.")
    else:
        print(f"{assistant_name}: I've sent the request to close Google Chrome.")
def open_messages():
    try:
        subprocess.run(["open", "-a", "Messages"], check=True)
    except subprocess.CalledProcessError:
        print(f"{assistant_name}: I couldn't open Messages.")
    else:
        print(f"{assistant_name}: I've sent the request to open Messages.")
def get_practice_files():
    if not practice_folder.is_dir():
        print(f"{assistant_name}: I couldn't find the practice folder.")
        return None
    files = []
    for item in practice_folder.iterdir():
        if item.is_file():
            files.append(item.name)

    return files
def move_without_overwrite(source, destination):
    macos = ctypes.CDLL("/usr/lib/libSystem.B.dylib", use_errno=True)

    rename_file = macos.renamex_np
    rename_file.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
    rename_file.restype = ctypes.c_int

    rename_exclusive = 4
    result = rename_file(
        os.fsencode(source),
        os.fsencode(destination),
        rename_exclusive
    )
    if result != 0:
        error_number = ctypes.get_errno()
        raise OSError(error_number, os.strerror(error_number))
def test_file_move():
    source_path = move_test_folder / "move_me.txt"
    destination_path = move_test_folder / "Documents" / "move_me.txt"

    print("ONE-FILE MOVE TEST — this will move the test file if approved.")
    print(f"From: {source_path}")
    print(f"To:   {destination_path}")
    approval = input("Type APPROVE to move this file, or press Enter to cancel: ").strip()
    if approval != "APPROVE":
        print("Cancelled. No files were changed.")
        return
    if not source_path.is_file():
        print("Skipped: the source file is missing or isn't a file.")
        return

    if destination_path.exists():
        print("Skipped: the destination already exists.")
        return
    try:
        destination_path.parent.mkdir(exist_ok=True)
        move_without_overwrite(source_path, destination_path)
    except OSError as error:
        print(f"Move failed: {error}")
        return

    print(f"Moved: {source_path.name}")
    print(f"To: {destination_path}")

# Date and time: Python reads the Mac's clock so the model never guesses
time_phrases = ["what time is it", "what's the time", "what is the time", "current time"]
date_phrases = ["what's the date", "what is the date", "today's date", "what day is it", "what's today", "what is today"]
def is_time_question(request):
    request = request.replace("’", "'")
    return any(phrase in request for phrase in time_phrases)
def is_date_question(request):
    request = request.replace("’", "'")
    return any(phrase in request for phrase in date_phrases)
def tell_time():
    now = datetime.now()
    print(f"{assistant_name}: It's {now.strftime('%-I:%M %p')}, ma'am.")
def tell_date():
    now = datetime.now()
    print(f"{assistant_name}: Today is {now.strftime('%A, %-d %B %Y')}, ma'am.")

# AI conversation: send a message to Ministral
def chat_with_veylric(message):
    user_message = {"role": "user", "content": message}
    current_time = datetime.now().strftime("%A, %-d %B %Y, %-I:%M %p")
    stream = ollama.chat(
        model="ministral-3:8b",
        stream=True,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Veylric, a calm personal AI assistant with a natural British style. "
                    "Use one or two short sentences unless the user requests detail. Avoid emojis. "
                    "The user uses macOS. "
                    "Veylric has app-opening tools handled separately by Python. "
                    "Your conversational reply does not execute tools. "
                    "Never claim an action succeeded without a tool result. "
                    "If asked to open something without a clear target, ask what to open. "
                    "If a question depends on information the user has not provided in this conversation, say you don't know and ask for it. Do not invent personal facts or imply you remember them. "
                    f"The current date and time is {current_time}. "
                )
            },
        ] + conversation_history + [user_message]
    )
    reply = ""

    print(f"{assistant_name}: ", end="", flush=True)

    for chunk in stream:
        piece = chunk["message"]["content"]
        print(piece, end="", flush=True)
        reply += piece

    print()
    conversation_history.append(user_message)
    conversation_history.append({"role": "assistant", "content": reply})
    del conversation_history[:-10]
    return reply

# Main loop: read requests and choose an ability
while True:
    message = input("You: ").strip()
    request = message.lower()
    previous_clarification = pending_clarification
    pending_clarification = None

    if previous_clarification == "spotify":
        if request in ["open it", "launch it"]:
            message = "Please open Spotify."

    if request == "shutdown":
        print(f"{assistant_name}: Shutting down, ma'am.")
        break
    elif request in ["organise my files", "organize my files"]:
        print(f"{assistant_name}: Of course, ma'am. I'll prepare an organisation preview.")
        practice_files = get_practice_files()
        if practice_files is not None:
            preview_files(practice_files)
    elif request == "open spotify":
        open_spotify()
    elif request in ["search spotify", "search spotify for"]:
        search_spotify()
    elif request.startswith("search spotify for "):
        search_term = message[len("search spotify for "):].strip()
        search_spotify(search_term)
    elif request == "open chrome":
        open_chrome()
    elif request == "close chrome":
        close_chrome()
    elif request == "open messages":
        open_messages()
    elif request == "test file move":
        test_file_move()
    elif request == "move practice files":
        practice_files = get_practice_files()
        if practice_files is not None:
            preview_files(practice_files, execute=True)
    elif request == "clear conversation":
        conversation_history.clear()
        print(f"{assistant_name}: This session's conversation history has been cleared.")
    elif is_time_question(request):
        tell_time()
    elif is_date_question(request):
        tell_date()
    else:
        try:
            # Only ask the classifier when Spotify is mentioned
            if "spotify" in message.lower():
                intent = classify_request(message)
            else:
                intent = "unknown"

            if intent == "open_spotify":
                print(f"{assistant_name}: Certainly, ma'am. Opening Spotify.")
                open_spotify()
            elif intent == "search_spotify":
                if "play" in request.split():
                    print(f"{assistant_name}: I can't start playback yet, ma'am, but I can search for it.")
                search_term = extract_search_term(message)
                if search_term is None:
                    print(f"{assistant_name}: What would you like me to search for?")
                search_spotify(search_term)
            elif intent == "clarify_spotify":
                pending_clarification = "spotify"
                print(f"{assistant_name}: What would you like me to do with Spotify?")
            else:
                chat_with_veylric(message)
        except ConnectionError:
            print()
            print(f"{assistant_name}: I couldn't connect to Ollama. Please check that it's running.")
        except ollama.ResponseError as error:
            print()
            print(f"{assistant_name}: Ollama couldn't complete the request: {error.error}")