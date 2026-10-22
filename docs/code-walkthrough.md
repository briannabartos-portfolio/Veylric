# Understanding Veylric: code and learning walkthrough

This guide follows the working [`main.py`](../veylric_beta/main.py), from top to bottom. It describes the early Beta 0.3 code, including natural Spotify opening without a second confirmation. Line numbers refer to the version reviewed on October 22, 2026 and will shift as development continues.


## 1. The whole program in plain language

Veylric combines two kinds of work:

- **Python instructions** choose implemented tools, manage history, and enforce file approval.
- **The language model** generates conversation and suggests a restricted intent label for some requests.

The current flow is:

```text
Start Python
    ↓
Import tools, set paths, create empty session state, print greeting
    ↓
Define functions (remember their instructions, don't run their bodies)
    ↓
Ask for input in the main loop
    ↓
Check a pending clarification and then exact commands
    ├── Exact command → call its Python function
    └── Other message → classifier
                          ├── open_spotify → opening tool
                          ├── clarify_spotify → ask a question
                          └── unknown → streamed conversation
    ↓
Ask for the next request, unless shutdown breaks the loop
```

There is no single “AI brain” doing all this. The Python program connects smaller parts. The model does not receive permission to execute arbitrary code.

**Demonstrated in discussion:** defining a function differs from calling it; `return` exits a function; an unindented summary runs after a loop.

**Revisit:** tracing the next instruction Python will execute, especially when blocks are nested.

## 2. Symbols you will keep seeing

| Syntax | Meaning in this project |
| --- | --- |
| `# explanation` | A comment for the reader; Python ignores it. |
| `name = value` | Assign a value to a name. It is not an equality question. |
| `a == b` | Compare values for equality. |
| `a != b` | Compare values for inequality. |
| `"text"` or `'text'` | A string: text between matching quotes. |
| `f"Hello {name}"` | An f-string: insert a value into text. |
| `function(...)` | Call a function with the arguments inside the parentheses. |
| `object.name` | Access an attribute; it may be data or a method. |
| `object.method()` | Call a method associated with that object. |
| `[]` | An empty list; square brackets also index or slice a collection. |
| `[a, b]` | A list of values, kept in order. |
| `(a, b)` | A tuple: a fixed group of values, used here for a filename/destination pair. |
| `{"role": "user"}` | A dictionary: a key connected to a value with `:`. |
| `if`, `elif`, `else` | Choose which instructions to run. |
| `:` after a condition or definition | Starts a block whose body is indented. |
| `True`, `False` | Boolean values, representing true and false. |
| `None` | A value used to represent the absence of a result or pending subject. |
| `not value` | Reverse the truth test of a value. Empty lists and strings are false in conditions. |
| `value in collection` | Test membership. |
| `is not None` | Check that a value is not the special `None` object. |
| `count += 1` | Add one and store the updated count. |
| `reply += piece` | Join strings and store the updated text. |
| `→` inside a string | Just a displayed arrow; it has no file-moving behavior. |

Four spaces are the convention for one indentation level. Indentation is meaningful Python structure, not decoration. Within parentheses, continuation lines have more flexible spacing, but alignment still helps the reader.

## 3. Imports: making tools available (lines 1–8)

```python
import ollama
import ctypes
import os
import subprocess
from spotify_search_test import search_spotify
from intent_test import classify_request
from pathlib import Path
```

| Import | Why Veylric needs it |
| --- | --- |
| `ollama` | Send requests to the locally running model. This is the external Python dependency in `requirements.txt`. |
| `ctypes` | Bridge Python to a macOS system function for a protected move. Advanced material, isolated in one helper. |
| `os` | Convert filesystem paths for the system function and turn error numbers into descriptions. |
| `subprocess` | Ask macOS to run commands such as `open`. |
| `Path` | Work with file and folder locations. |
| `search_spotify` | Reuse the search function written in the neighbouring file. |
| `classify_request` | Reuse the neighbouring intent classifier. |

`import module` makes the module available by name. `from module import item` brings a particular item into this file's namespace. The module filename is written without `.py`.

Imports execute a module's top-level code on its first normal import. The helper files' **main guards** prevent their standalone input prompts from running on import:

```python
if __name__ == "__main__":
    # Run the standalone test only when this file is executed directly.
    ...
```

`main.py` itself does not yet have a main guard: importing it would print the greeting and enter the input loop. That is one reason our checks avoid simply importing `main.py`.

**Practised:** importing tested helpers instead of copying them, adding main guards, and fixing imports that accidentally pointed into the backup folder.

**Revisit:** what happens when a file is run directly versus imported, and how Python finds neighbouring modules.

## 4. Settings and session state (lines 10–16)

```python
practice_folder = Path(__file__).parent / "practice_files"
move_test_folder = Path(__file__).parent / "move_test"
assistant_name = "Veylric"
conversation_history = []
pending_clarification = None
print(f"{assistant_name}: At your service, ma'am. Ready when you are.")
```

### Finding folders beside the script

- `__file__` supplies this script's location.
- `Path(__file__)` represents that location as a path object.
- `.parent` selects the containing folder, `veylric_beta`.
- `/ "practice_files"` joins a child name to the path. Here `/` is path joining, not numeric division.

A path object describes an address. Creating one does not create or move a file. Keeping these paths relative to the script lets the program find its practice folders even when it is launched from the project root.

### Remembering values

`assistant_name` refers to text. The f-string uses it in the greeting. Double quotes around the string allow the apostrophe in `ma'am` without ending the string.

`conversation_history` starts as an empty list. `pending_clarification` starts as `None`, meaning no unfinished clarification is recorded. These initializations run once at startup, not once per turn.

These variables live at module level. Functions can read them. The chat function changes the existing history list with `.append()` and `del`; it does not assign a new list to that name, so it does not need a `global` declaration for these operations.

**Practised:** variables, f-strings, path construction, and session state.

**Revisit:** Python variables are names referring to objects, rather than literal containers. Mutating a list and rebinding a variable are different operations.

## 5. Building the organization plan (lines 19–35)

```python
def preview_files(files, execute=False):
    proposed_moves = []
```

`def` defines a function. `files` and `execute` are **parameters**: names used inside it. A value supplied in a call is an **argument**.

```python
preview_files(practice_files)                 # execute defaults to False
preview_files(practice_files, execute=True)   # keyword argument selects real mode
```

The name `preview_files` predates real moves; it now handles both modes. We should remember this when reading it, and may rename it in a later cleanup.

```python
if not files:
    print("There are no files to preview.")
    return
```

An empty list is false in a condition. `not files` is therefore true when there are no filenames. `return` exits this call and returns `None` implicitly. A printed message alone would not stop execution.

```python
for filename in files:
    if filename.lower().endswith(".jpg"):
        print(f"{filename} → Pictures (matched .jpg extension)")
        proposed_moves.append((filename, "Pictures"))
```

For each filename:

1. `.lower()` produces lowercase text for the check; it does not rename the file or replace the original string.
2. `.endswith(".jpg")` returns a Boolean.
3. The matching branch displays a suggestion.
4. `.append()` adds one tuple to the proposed-moves list.

The `.txt` branch applies the same pattern for Documents. The final `else` prints “Needs review” and does not add a proposed move. These are extension rules, not an inspection of a file's contents. A filename ending in `.jpg` does not prove it is a valid image.

After the loop, `if not proposed_moves` handles a folder containing only unknown types. That differs from an empty input list: files were found, but none matched the rules.

**Practised:** loops, case-insensitive extension checks, tuple pairs, `.append()`, and keeping unknown types outside the plan.

**Revisit:** following the nesting of function → loop → condition, and explaining what each variable contains on a particular pass.

## 6. Approval and selecting a mode (lines 37–49)

`if execute` chooses the real-move heading and prompt. Its `else` chooses simulation wording. `prompt` is just text stored in a variable.

```python
approval = input(prompt).strip()
```

`input()` prints the question and waits for Return. `.strip()` removes surrounding whitespace. Pressing Return without text produces `""`, an empty string.

```python
if approval == "APPROVE":
    moved_count = 0
    skipped_count = 0
    failed_count = 0
```

Only this exact uppercase word, after trimming, selects the approved branch. `yes` and an empty string cancel. Approval applies to the stored `proposed_moves` list for this call; the function does not rescan the folder after approval.

Counters start once, before processing the plan. If they were initialized inside the loop, they would reset for each file.

**Practised:** explicit confirmation, exact comparisons, empty input, and counter initialization.

**Revisit:** words such as “Cancelled” do not enforce behavior. The branch structure and `return` determine what actually happens.

## 7. Checking and processing proposed moves (lines 51–75)

```python
for filename, destination in proposed_moves:
    source_path = practice_folder / filename
    destination_path = practice_folder / destination / filename
```

`filename, destination` **unpacks** each tuple into two names. A pair like `("notes.txt", "Documents")` supplies those values in order.

Both paths are built under the practice folder. The suggested Documents folder is not the Mac's personal Documents folder.

### Skip checks

`not source_path.is_file()` detects a missing source or a path that is not a file. `destination_path.exists()` checks whether something occupies the target. Their branches print a skip reason and increment `skipped_count`.

```python
skipped_count += 1
```

means `skipped_count = skipped_count + 1`. Unknown file types are not counted here: they never became proposed moves.

### Real move branch

```python
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
```

- `.parent` selects the destination's containing folder.
- `.mkdir(exist_ok=True)` creates it, or accepts an existing directory. It does not mean “overwrite any existing item.”
- The helper attempts the protected move.
- `except OSError as error` catches this category of failure and names the exception `error`.
- The `else` aligned with `except` runs only if the `try` finishes without an exception.

No `return` or `break` is used after an individual failed move here: the loop continues to other files. If creating the folder succeeds but the move fails, the empty folder may remain. A failed plan is not automatically rolled back.

### Simulation branch

The other `else`, aligned with `if execute`, only prints `Would move` and the path. It does not call `.mkdir()` or the move helper.

**Practised:** source and destination checks, success/failure branches, counting outcomes, and distinguishing preview from action.

**Revisit:** recognizing which `if` or `try` an `else` belongs to. These safeguards are not a hardened sandbox: symlinks and changes to files between checks need further work before real-data access.

## 8. Printing the summary once (lines 76–85)

```python
if execute:
    print(
        f"Finished: {moved_count} moved, "
        f"{skipped_count} skipped, "
        f"{failed_count} failed."
    )
else:
    print("Simulation complete. No files were changed.")
```

Inside the function, this block is after the file loop and inside the approved branch. Adjacent f-strings join into one string. Parentheses let the call span several lines.

The outer approval `else` prints cancellation. It is separate from this mode-selecting `else`.

The key lesson we worked through was:

```python
for filename in files:
    print(filename)      # Once for each filename

print("Finished")        # Once after the loop
```

With three files, the loop makes three passes, then `Finished` prints once. If that final print were indented into the loop, it would print three times.

**Demonstrated in discussion:** the loop processes its items, then Python proceeds to the summary.

**Testing evidence:** isolated examples used a pretend move function to exercise one success, two skips, and one failure. Those counter tests did not move the practice files.

## 9. App tools (lines 86–113)

Spotify, Chrome, and Messages opening share this pattern:

```python
subprocess.run(["open", "-a", "Spotify"], check=True)
```

- `subprocess.run()` starts an external command and waits for that command to finish.
- The list supplies separate command arguments; it is not a string evaluated by a shell.
- `open` is the macOS command.
- `-a` is an option belonging to `open`, selecting an application.
- `check=True` raises `CalledProcessError` if the command exits unsuccessfully.

The matching `except subprocess.CalledProcessError` prints a failure message. The success `else` reports that the request was sent. This does not verify Spotify's screen or music playback. Missing command executables are a different error category that these handlers do not currently catch.

Chrome quitting uses:

```python
subprocess.run(
    ["osascript", "-e", 'tell application "Google Chrome" to quit'],
    check=True
)
```

`osascript` runs AppleScript. `-e` identifies the following argument as script text. Single Python quotes allow the inner double quotes around Google Chrome. This is a normal application quit request, rather than terminating matching processes with `pkill`.

**Practised:** a function as an ability, command arguments, basic error handling, and truthful launch-request messages.

**Revisit:** command options are command-specific. The same `-a` does not mean the same thing in every command.

## 10. Reading the practice folder (lines 114–123)

```python
if not practice_folder.is_dir():
    print(f"{assistant_name}: I couldn't find the practice folder.")
    return None
```

`.is_dir()` checks for a directory. `None` signals that the expected folder could not be found as a directory.

Otherwise, the function creates `files = []`, iterates over `practice_folder.iterdir()`, checks `item.is_file()`, and appends `item.name`.

- `.iterdir()` provides entries directly in the folder; it does not recursively scan subfolders.
- `item` is a path, while `item.name` is its final filename component.
- Subfolders are skipped. This keeps already-organized subfolders outside the top-level scan.
- `return files` sends the completed list back.

The distinction matters:

| Result | Meaning |
| --- | --- |
| `None` | The expected folder wasn't found as a directory. |
| `[]` | The folder was read, but no files were collected. |
| A nonempty list | Filenames are available for the preview. |

The caller uses `is not None` so that an empty-but-valid list can still get an empty-folder explanation. Reading on each command gets fresh names rather than the startup snapshot we originally tested.

**Practised:** fresh reads, missing versus empty folders, and returning data from a function.

**Revisit:** this function does not catch every directory-reading error, and `.is_file()` normally follows symlinks.

## 11. The macOS no-overwrite helper (lines 124–139)

This was the most advanced section introduced. It connects Python to a C system function. It is reasonable to revisit it separately from everyday Python and not memorize it.

```python
def move_without_overwrite(source, destination):
```

The two parameters are the file's current location and intended location. The learner identified `destination` as where the file should end up.

```python
macos = ctypes.CDLL("/usr/lib/libSystem.B.dylib", use_errno=True)
```

This loads access to a macOS system library. The starting `/` makes it an absolute path. `use_errno=True` enables access to the error number associated with a failing call.

```python
rename_file = macos.renamex_np
```

This selects the function without calling it. No parentheses means we are referring to the callable, not invoking it. `renameatx_np` is a different function with a different input signature; we corrected that typing mix-up during review.

```python
rename_file.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
rename_file.restype = ctypes.c_int
```

These describe the C interface:

- Two pointers to byte strings for the paths.
- An unsigned integer for flags.
- An integer return value.

This is necessary setup for a foreign-function interface, not a pattern required for ordinary Python functions.

```python
rename_exclusive = 4
```

`4` is the macOS `RENAME_EXCL` flag value, not a number invented by the project. Naming it makes its purpose clearer: refuse a destination that already exists.

```python
result = rename_file(
    os.fsencode(source),
    os.fsencode(destination),
    rename_exclusive
)
```

This is the actual move attempt when the helper is called. `os.fsencode()` converts Python paths to filesystem-encoded bytes. The three arguments are source, destination, and protection setting. `result` receives zero for success or minus one for failure.

```python
if result != 0:
    error_number = ctypes.get_errno()
    raise OSError(error_number, os.strerror(error_number))
```

On failure, get the system error number, translate it into a description, and `raise` a Python exception. This helper does not print a friendly message itself; its caller catches the exception and decides how to report it.

The operation is macOS-specific and intended for moves on the same filesystem. Unsupported operations fail rather than falling back to an overwrite-capable move. It protects an occupied destination, not every aspect of access control or file identity.

**Testing evidence:** isolated temporary files verified that an existing destination was rejected with both contents unchanged, and an available destination allowed a move with content preserved.

**Revisit:** byte strings, C types, system libraries, flags, and `raise` versus `except`. These remain advanced topics introduced with substantial guidance, not claimed independent mastery.

## 12. The one-file move exercise (lines 140–166)

`test_file_move()` limits the experiment to `move_test/move_me.txt` and its proposed `Documents/move_me.txt` destination. It prints the plan and asks for approval.

```python
if approval != "APPROVE":
    print("Cancelled. No files were changed.")
    return
```

This is an **early return**: end the function before action if permission is absent. Subsequent early returns handle an unavailable source and an occupied destination. A `try` prepares the folder and calls the protected helper. An `except OSError` prints the problem and returns before the success messages.

`source_path.name` can still display the original filename after the move. A `Path` is a description of a location, not a live object that relocates itself when the file moves.

**Practised:** approval-first ordering, early returns, and checking the resulting location in Explorer rather than trusting displayed text alone.

**Debugging lesson:** removing a cancellation `return` allowed execution to continue after printing “Cancelled.” Reinstating it restored the intended control flow. We caught this before connecting the real move.

## 13. Chat requests and message dictionaries (lines 169–190)

```python
user_message = {"role": "user", "content": message}
```

This dictionary labels the speaker and holds the text. The unquoted `message` is a variable; `"message"` would be literal text.

```python
stream = ollama.chat(
    model="ministral-3:8b",
    stream=True,
    messages=[ ... ] + conversation_history + [user_message]
)
```

`model=` and `stream=` are keyword arguments. `stream=True` requests incremental responses. The assembled message list has this order:

```text
System instructions → earlier exchanges → current user message
```

`+` joins lists here. `[user_message]` makes a one-item list so it can be joined to the others. This expression does not itself append to the stored history.

The system dictionary supplies personality and honesty instructions. Adjacent strings inside parentheses join automatically; spaces at the ends prevent sentences sticking together. These instructions guide generated text but do not enforce permissions or guarantee accuracy. The prompt currently asks for neutral greetings because no real clock value has been supplied yet.

**Practised:** dictionaries, list concatenation, separating system instructions from user input, and correcting a nested-dictionary mistake where `user_message` was incorrectly placed inside `content`.

**Revisit:** a model only receives the information the program includes. A confident answer is not evidence that a fact is true or an action happened.

## 14. Streaming, collecting text, and temporary history (lines 191–204)

```python
reply = ""
print(f"{assistant_name}: ", end="", flush=True)

for chunk in stream:
    piece = chunk["message"]["content"]
    print(piece, end="", flush=True)
    reply += piece

print()
```

- `reply` starts as an empty string.
- `end=""` prevents a newline after each print.
- `flush=True` asks Python to send the text to output immediately.
- Each `chunk` contains a piece of the response, not necessarily a full word.
- Nested indexing retrieves the piece's text.
- `reply += piece` collects the same text into a complete answer.
- The final `print()` adds a newline after streaming ends.

This is actual incremental output, not an artificial typing delay. The prefix is printed before the response arrives, which can leave an empty `Veylric:` line when a request fails.

```python
conversation_history.append(user_message)
conversation_history.append({"role": "assistant", "content": reply})
del conversation_history[:-10]
return reply
```

Only after the stream completes normally are both messages stored. An interrupted stream may display a partial answer without storing that exchange.

`[:-10]` means everything before the last ten entries. `del` removes that older portion in place. Ten entries means five complete user/assistant exchanges. The next request includes those stored exchanges plus the new user message. This is a message-count limit, not a limit on tokens or characters.

The function returns the complete reply, but the current caller does not need that value for display: the function has already printed it. Printing it again in the caller would duplicate the answer.

**Practised:** streamed output, string accumulation, no duplicate printing, session recall, trimming history, and explicitly clearing it.

**Revisit:** history is context supplied again, not model retraining. Clearing the Python list does not erase terminal text or guarantee deletion from every layer outside this application's history management.

## 15. The main loop and original versus normalized text (lines 207–215)

```python
while True:
    message = input("You: ").strip()
    request = message.lower()
```

`while True` keeps looping until something exits it. `message` preserves capitalization after trimming; `request` is a lowercase copy used for command comparisons. This lets `OPEN SPOTIFY` work without lowercasing ordinary conversation sent to the model.

```python
previous_clarification = pending_clarification
pending_clarification = None
```

Copy the old subject for this turn, then clear the pending slot. If it was `"spotify"` and the input is exactly `open it` or `launch it`, rewrite `message` to `Please open Spotify.`. Leave `request` unchanged, so the expanded request goes through classification rather than the exact-command branch.

This is deliberately narrow, one-turn context. Other wordings or punctuation do not match this exact Python list. Chat history is a separate source of context and may still influence conversational replies after pending state expires.

**Practised:** state that lasts between turns, consuming it once, and preventing unresolved pronouns from selecting Spotify through the classifier's explicit guard.

**Revisit:** why chat history and pending clarification have separate jobs; normalizing text for comparison versus changing the message sent onward.

## 16. Exact command routing (lines 217–246)

Only the first matching branch in this `if`/`elif` chain runs.

| Command branch | What it does |
| --- | --- |
| `shutdown` | Prints a message and `break`s out of the main loop. |
| `organise my files` / `organize my files` | Gets fresh filenames; previews only if the result isn't `None`. |
| `open spotify` | Calls the app-opening function immediately. |
| `search spotify` / `search spotify for` | Calls search without an argument, prompting for the words. |
| Starts with `search spotify for ` | Extracts the remaining text and supplies it to search. |
| `open chrome` | Calls Chrome opening. |
| `close chrome` | Calls the normal Chrome quit request. |
| `open messages` | Opens the Messages application; it does not send a message. |
| `test file move` | Runs the approved one-file experiment. |
| `move practice files` | Gets fresh filenames and selects `execute=True`; approval is still required inside the function. |
| `clear conversation` | Empties the history list without closing the program. |

### The search slice

```python
search_term = message[len("search spotify for "):].strip()
```

`len()` counts the prefix characters. `[number:]` takes the rest of the string from that position onward. Using `message` preserves the search's case. The separate missing-term branch is needed because `.strip()` removes the trailing space from `search spotify for `.

### `break` versus `return`

- `break` exits the nearest loop. Here, it ends the assistant session.
- `return` exits the current function. A tool returning leaves the main loop available for more input.

**Practised:** alternate spellings, case-insensitive commands, prefix matching, string slicing, loop continuation, and shutdown.

**Revisit:** exact matching doesn't understand arbitrary phrasing or internal extra spaces. The app and file functions themselves are not running the model.

## 17. Model-selected tools, clarification, and errors (lines 247–264)

If no exact command matched, the program calls `classify_request(message)` inside a `try`.

The classifier is in [`intent_test.py`](../veylric_beta/intent_test.py). Its tested labels are:

- `open_spotify`
- `clarify_spotify`
- `unknown`

It replaces unexpected labels with `unknown` and explicitly rejects unresolved `open it` / `launch it` before asking the model. This allowlist validates the output label, not whether the interpretation is correct. A permitted label can still be a model mistake.

### Current Beta 0.3 opening behavior

```python
if intent == "open_spotify":
    print(f"{assistant_name}: Certainly, ma'am. Opening Spotify.")
    open_spotify()
```

The learner chose to remove the extra `OPEN` confirmation for this low-impact action in Beta 0.3. The explicit natural request now authorizes the opening attempt. File moves still require `APPROVE`; search still requires `SEARCH`. The acknowledgement announces an attempt; the tool reports its command result.

`clarify_spotify` sets the pending subject and asks a fixed question. `unknown` goes to the chat function. The classifier does not receive the chat history; the chat model does. For ordinary conversation, this path makes two model calls: classification, then generation.

### Error handling

- `except ConnectionError` reports that Ollama could not be reached.
- `except ollama.ResponseError as error` reports a problem returned by Ollama, such as a missing model.
- `error.error` accesses the explanation provided by the exception.
- A blank `print()` separates the error from any streaming prefix already displayed.

After a handled error, execution reaches the next main-loop iteration. These handlers are specific, not a guarantee against every possible crash. Most exact tool branches are outside this final `try` and rely on their own handlers.

**Practised:** natural-request classification, an allowlist, ambiguity and negation examples, temporary confirmation before Beta 0.3, and deliberate connection/missing-model failure tests followed by restoration.

**Revisit:** deterministic Python controls versus probabilistic model choices; accurate action reporting; the difference between asking a clarification and resolving its answer.

## 18. The imported Spotify search function

Although its body is outside `main.py`, this helper is part of the working application. See [`spotify_search_test.py`](../veylric_beta/spotify_search_test.py).

```python
def search_spotify(search_term=None):
```

The optional parameter supports both interactive input and a supplied string. `None` triggers the question; an explicit empty string reaches the empty-input check rather than prompting again.

The function:

1. Obtains and trims the search words.
2. Returns early if they are empty.
3. Uses `quote(search_term, safe="")` from Python's standard library to encode spaces and special characters for the URI.
4. Builds `spotify:search:...` with an f-string.
5. Shows the original words, not the encoded address, for approval.
6. Requires exact `SEARCH` after trimming.
7. Calls `subprocess.run(["open", search_uri], check=True)` or reports cancellation.

Its main guard permits standalone tests without prompting when imported. Search results opened successfully for Fleetwood Mac and Here Comes the Sun. The client's displayed plus signs and special-character behavior need further investigation. A sent search request is not proof of playback, and the function does not request playback.

**Practised:** optional arguments, URL encoding, preview and confirmation, helper imports, and preserving a main loop after a helper returns.

## 19. What the tests taught 

| Test or mistake | What it revealed |
| --- | --- |
| Missing quote in a filename list | Strings need matching delimiters; valid-looking words can still form invalid syntax. |
| `.JPG` and `.TXT` examples | Case-sensitive comparisons need intentional normalization. |
| New file created while running | Read the folder on demand rather than reuse a startup list. |
| Missing versus empty folder | `None` and `[]` can communicate different outcomes. |
| Summary inside a loop | Correct syntax can still have incorrect placement and repeated output. |
| Cancellation without `return` | Printed words don't stop execution. |
| `Documets` versus `Documents` | A valid path expression can still point to the wrong name. |
| Existing destination | Check the conflict and test the helper's deeper no-overwrite protection separately. |
| Incorrect system-function name | Passing syntax checks doesn't prove an external call has the right signature. |
| Made-up spaceship name | Model confidence is not evidence; explicitly test missing context. |
| Clearing conversation | Session context can be erased without shutting down the program. |
| Repeated unresolved `open it` | An allowlisted tool label can still be a mistaken guess; add narrow Python rules. |
| Copied files imported from a checkpoint | A backup should preserve code, not become a dependency of the working application. |
| GitHub upload | A commit saves a local version; push publishes commits. Ignored files stay local. |

Not every behavior has an automated test. Some were observed manually; others used isolated temporary files or replacement functions. Successful examples support a claim about those examples, not a promise that every input is handled.

## 20. Learning record: evidence and next practice

| Topic | Evidence from the learning sessions | Useful next practice |
| --- | --- | --- |
| Functions | Correctly distinguished calling from defining. | Write a small greeting function without a template. |
| Parameters | Identified destination as the intended location. | Explain what two arguments become inside a function. |
| `return` | Identified it as the instruction that stops the current function. | Predict which later lines become unreachable. |
| Loops | Explained that the loop processes all files, then prints the summary. | Predict output with zero, one, and three items. |
| Indentation | Corrected nested summary placement through guided checks. | Mark which block owns each `else` before editing it. |
| Data structures | Used lists, tuples, dictionaries, and history trimming with guidance. | Construct one message dictionary and unpack one move pair independently. |
| Errors | Tested deliberate failures and restored the working configuration. | Explain the difference between `raise` and `except`. |
| AI integration | Tested prompts, streaming, recall, hallucination, and classification. | Trace what each model call receives and what Python controls. |
| Advanced macOS helper | Walked through each part after it was introduced too quickly. | Review separately; don't treat native-interface knowledge as a prerequisite for basic Python. |
| Git | Created a checkpoint workflow and distinguished commit from push. | Review and commit one small tested change independently. |

### Personal reflections to fill in

These prompts are intentionally unanswered. They should capture the learner's own voice rather than invented first-person claims.

- A section I can now explain without looking at this guide:
- A section I can follow but cannot yet write from scratch:
- The part that currently feels most confusing:
- A bug I fixed and why the fix worked:
- One small piece I want to write independently next:

## 21. Short exercises without real file actions

Work through these before running anything; the goal is to predict the result.

1. In a three-item loop, what changes if the summary moves one indentation level right?
2. If `execute` is omitted in `preview_files(files)`, which mode is selected?
3. Why does `get_practice_files()` return a list, while the app tools mostly print and return `None` implicitly?
4. If the input is `OPEN SPOTIFY`, what do `message` and `request` contain?
5. What happens if `return` is removed from a cancellation guard?
6. Why can `main.py` call a function defined earlier without running that function at startup?
7. Why doesn't clearing history guarantee the next model response is factually correct?
8. Why does an allowlist not prove that a Spotify-opening label matches the user's intention?
9. What is different between an `else` paired with `if`, one paired with `try`, and the `for…else` we accidentally formed during editing?
10. Why should code and documentation be committed together when behavior changes?

The next learning goal is not memorizing this whole file. It is being able to trace one request through the program, explain why each step exists, and make a small tested change with increasing independence.
